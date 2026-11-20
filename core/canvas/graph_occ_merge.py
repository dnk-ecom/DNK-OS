# --- DNK-MRH-HEADER ---
# mrh_id: "core/canvas/graph_occ_merge.py"
# purpose: "OCC 3-Way Structural Graph Mutation Resolver for Multi-User & Multi-Agent Canvas"
# canonical_source: true
# alters_files: []
# triggers_tasks: ["task-occ-merge", "task-node-system"]
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-05"
# author: "Antigravity (Mentor) & DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import difflib
import json
from copy import deepcopy
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.domain.thought_dsl import detect_cycles_kahn


class ConflictType(str, Enum):
    CYCLE_DETECTED = "CYCLE_DETECTED"
    POSITION_CONFLICT = "POSITION_CONFLICT"
    DATA_CONFLICT = "DATA_CONFLICT"
    DELETED_MODIFIED = "DELETED_MODIFIED"
    ORPHAN_EDGE = "ORPHAN_EDGE"

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return super().__eq__(other)


class PositionConflictStrategy(str, Enum):
    SHIFT = "shift"                      # Deterministic vector shift (+20px, +20px)
    LAST_WRITE_WINS = "last_write_wins"  # Local/incoming mutation overrides
    MINE = "mine"                        # Explicitly keep Mine position
    THEIRS = "theirs"                    # Explicitly keep Theirs position


class MergeConflict:
    """Represents a conflict discovered during 3-way structural graph merge."""

    def __init__(
        self,
        conflict_type: Union[ConflictType, str],
        entity_type: str,
        entity_id: str,
        message: str,
        resolvable: bool = True,
        resolution: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if isinstance(conflict_type, ConflictType):
            self.conflict_type = conflict_type
        elif isinstance(conflict_type, str):
            try:
                self.conflict_type = ConflictType(conflict_type.upper())
            except ValueError:
                self.conflict_type = ConflictType(conflict_type) if conflict_type in ConflictType._value2member_map_ else conflict_type
        else:
            self.conflict_type = conflict_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.message = message
        self.resolvable = resolvable
        self.resolution = resolution
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_type": getattr(self.conflict_type, "value", str(self.conflict_type)),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "message": self.message,
            "resolvable": self.resolvable,
            "resolution": self.resolution,
            "details": self.details,
        }


class OCCMergeResult:
    """Encapsulates the complete result of an OCC 3-way merge operation."""

    def __init__(
        self,
        status: str,
        merged_graph: Dict[str, Any],
        conflicts: List[MergeConflict],
        applied_mutations: List[str],
        has_unresolved_conflicts: bool = False,
        version: str = "1.0.0",
    ):
        self.status = status
        self.merged_graph = merged_graph
        self.conflicts = conflicts
        self.applied_mutations = applied_mutations
        self.has_unresolved_conflicts = has_unresolved_conflicts
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "has_unresolved_conflicts": self.has_unresolved_conflicts,
            "version": self.version,
            "applied_mutations": self.applied_mutations,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "merged_graph": self.merged_graph,
        }


class OCCConcurrencyEngine:
    """
    Optimistic Concurrency Control (OCC) 3-Way Structural Graph Mutation Resolver.
    
    Resolves concurrent edits between:
    - Base (common ancestor snapshot)
    - Mine (incoming client/agent mutation)
    - Theirs (canonical server/remote state)
    
    Guarantees:
    - 0% data loss across disjoint edits.
    - Set union for node tags and smart concatenation for descriptions.
    - Deterministic vector shift (+20px) or LWW for position clashes.
    - Cycle detection gate (canon Kahn, core.domain.thought_dsl) returning unresolvable conflict on loops.
    """

    @classmethod
    def merge_graph_state(
        cls,
        base_state: Union[Dict[str, Any], str, Any],
        current_state: Union[Dict[str, Any], str, Any],
        incoming_state: Union[Dict[str, Any], str, Any],
        position_strategy: Union[PositionConflictStrategy, str] = PositionConflictStrategy.SHIFT,
    ) -> OCCMergeResult:
        """
        Merge base, current (Theirs), and incoming (Mine) graph states.
        
        Args:
            base_state: Ancestor state.
            current_state: Current canonical state on server (Theirs).
            incoming_state: Incoming client/agent patch (Mine).
            position_strategy: Strategy for handling concurrent position changes.
        """
        strat_str = str(position_strategy).lower()
        if "last_write" in strat_str or "lww" in strat_str:
            pos_strat = PositionConflictStrategy.LAST_WRITE_WINS
        elif "mine" in strat_str:
            pos_strat = PositionConflictStrategy.MINE
        elif "theirs" in strat_str:
            pos_strat = PositionConflictStrategy.THEIRS
        else:
            pos_strat = PositionConflictStrategy.SHIFT

        base = cls._normalize_graph(base_state)
        theirs = cls._normalize_graph(current_state)
        mine = cls._normalize_graph(incoming_state)

        conflicts: List[MergeConflict] = []
        applied_mutations: List[str] = []

        # 1. Merge Nodes
        merged_nodes, node_conflicts, node_mutations = cls._merge_nodes(
            base_nodes=base.get("nodes", {}),
            theirs_nodes=theirs.get("nodes", {}),
            mine_nodes=mine.get("nodes", {}),
            position_strategy=pos_strat,
        )
        conflicts.extend(node_conflicts)
        applied_mutations.extend(node_mutations)

        # 2. Merge Edges
        merged_edges, edge_conflicts, edge_mutations, has_cycle = cls._merge_edges(
            base_edges=base.get("edges", []),
            theirs_edges=theirs.get("edges", []),
            mine_edges=mine.get("edges", []),
            valid_node_ids=set(merged_nodes.keys()),
        )
        conflicts.extend(edge_conflicts)
        applied_mutations.extend(edge_mutations)

        has_unresolved = has_cycle or any(not c.resolvable for c in conflicts)
        status = "conflict" if has_unresolved else "success"

        now_iso = datetime.now(timezone.utc).isoformat()
        current_ver = theirs.get("version", "1.0.0")
        try:
            ver_parts = str(current_ver).split(".")
            ver_parts[-1] = str(int(ver_parts[-1]) + 1)
            new_version = ".".join(ver_parts)
        except Exception:
            new_version = f"{current_ver}-merged"

        merged_graph: Dict[str, Any] = {
            "nodes": merged_nodes,
            "edges": merged_edges,
            "stages": theirs.get("stages", base.get("stages", mine.get("stages", []))),
            "version": new_version,
            "updated_at": now_iso,
        }

        # Preserve top-level canvas elements/app_state if present
        if "app_state" in theirs or "app_state" in mine:
            app_state = deepcopy(theirs.get("app_state", {}))
            app_state.update(mine.get("app_state", {}))
            merged_graph["app_state"] = app_state

        if "name" in theirs or "name" in mine:
            merged_graph["name"] = mine.get("name") if mine.get("name") != base.get("name") else theirs.get("name", "Canvas")

        return OCCMergeResult(
            status=status,
            merged_graph=merged_graph,
            conflicts=conflicts,
            applied_mutations=applied_mutations,
            has_unresolved_conflicts=has_unresolved,
            version=new_version,
        )

    @classmethod
    def _merge_nodes(
        cls,
        base_nodes: Dict[str, Dict[str, Any]],
        theirs_nodes: Dict[str, Dict[str, Any]],
        mine_nodes: Dict[str, Dict[str, Any]],
        position_strategy: PositionConflictStrategy,
    ) -> Tuple[Dict[str, Dict[str, Any]], List[MergeConflict], List[str]]:
        merged_nodes: Dict[str, Dict[str, Any]] = {}
        conflicts: List[MergeConflict] = []
        mutations: List[str] = []

        all_node_ids = set(base_nodes.keys()) | set(theirs_nodes.keys()) | set(mine_nodes.keys())

        for node_id in sorted(all_node_ids):
            in_base = node_id in base_nodes
            in_theirs = node_id in theirs_nodes
            in_mine = node_id in mine_nodes

            # Case 1: Added only by Mine
            if in_mine and not in_base and not in_theirs:
                merged_nodes[node_id] = deepcopy(mine_nodes[node_id])
                mutations.append(f"node:added_by_mine:{node_id}")
                continue

            # Case 2: Added only by Theirs
            if in_theirs and not in_base and not in_mine:
                merged_nodes[node_id] = deepcopy(theirs_nodes[node_id])
                mutations.append(f"node:added_by_theirs:{node_id}")
                continue

            # Case 3: Added by both independently
            if in_mine and in_theirs and not in_base:
                # Merge both
                merged_node, c_list, m_list = cls._merge_single_node(
                    base_node={},
                    theirs_node=theirs_nodes[node_id],
                    mine_node=mine_nodes[node_id],
                    position_strategy=position_strategy,
                )
                merged_nodes[node_id] = merged_node
                conflicts.extend(c_list)
                mutations.extend(m_list)
                mutations.append(f"node:concurrent_add_resolved:{node_id}")
                continue

            # Case 4: Deleted by Mine
            if in_base and not in_mine and in_theirs:
                if cls._is_node_equal(base_nodes[node_id], theirs_nodes[node_id]):
                    # Theirs didn't touch it -> safe delete
                    mutations.append(f"node:deleted_by_mine:{node_id}")
                    continue
                else:
                    # Conflict: Deleted by Mine, but modified by Theirs -> Keep Theirs with warning
                    merged_nodes[node_id] = deepcopy(theirs_nodes[node_id])
                    conflicts.append(
                        MergeConflict(
                            conflict_type=ConflictType.DELETED_MODIFIED,
                            entity_type="node",
                            entity_id=node_id,
                            message=f"Node '{node_id}' deleted by Mine but modified by Theirs. Retaining Theirs modification.",
                            resolvable=True,
                            resolution="retained_theirs",
                        )
                    )
                    mutations.append(f"node:retained_modified_theirs:{node_id}")
                    continue

            # Case 5: Deleted by Theirs
            if in_base and in_mine and not in_theirs:
                if cls._is_node_equal(base_nodes[node_id], mine_nodes[node_id]):
                    # Mine didn't touch it -> safe delete
                    mutations.append(f"node:deleted_by_theirs:{node_id}")
                    continue
                else:
                    # Conflict: Deleted by Theirs, but modified by Mine -> Keep Mine
                    merged_nodes[node_id] = deepcopy(mine_nodes[node_id])
                    conflicts.append(
                        MergeConflict(
                            conflict_type=ConflictType.DELETED_MODIFIED,
                            entity_type="node",
                            entity_id=node_id,
                            message=f"Node '{node_id}' deleted by Theirs but modified by Mine. Retaining Mine modification.",
                            resolvable=True,
                            resolution="retained_mine",
                        )
                    )
                    mutations.append(f"node:retained_modified_mine:{node_id}")
                    continue

            # Case 6: Deleted by both
            if in_base and not in_mine and not in_theirs:
                mutations.append(f"node:deleted_by_both:{node_id}")
                continue

            # Case 7: Exists in all three (or both)
            b_node = base_nodes.get(node_id, {})
            t_node = theirs_nodes.get(node_id, {})
            m_node = mine_nodes.get(node_id, {})

            merged_node, c_list, m_list = cls._merge_single_node(
                base_node=b_node,
                theirs_node=t_node,
                mine_node=m_node,
                position_strategy=position_strategy,
            )
            merged_nodes[node_id] = merged_node
            conflicts.extend(c_list)
            mutations.extend(m_list)

        return merged_nodes, conflicts, mutations

    @classmethod
    def _merge_single_node(
        cls,
        base_node: Dict[str, Any],
        theirs_node: Dict[str, Any],
        mine_node: Dict[str, Any],
        position_strategy: PositionConflictStrategy,
    ) -> Tuple[Dict[str, Any], List[MergeConflict], List[str]]:
        merged = deepcopy(theirs_node)
        conflicts: List[MergeConflict] = []
        mutations: List[str] = []
        node_id = mine_node.get("id") or theirs_node.get("id") or base_node.get("id", "unknown")

        # 1. Position Resolution
        b_pos = cls._extract_position(base_node)
        t_pos = cls._extract_position(theirs_node)
        m_pos = cls._extract_position(mine_node)

        t_pos_changed = (t_pos != b_pos)
        m_pos_changed = (m_pos != b_pos)

        final_pos = t_pos
        if m_pos_changed and not t_pos_changed:
            final_pos = m_pos
            mutations.append(f"node:position_updated_mine:{node_id}")
        elif t_pos_changed and not m_pos_changed:
            final_pos = t_pos
            mutations.append(f"node:position_updated_theirs:{node_id}")
        elif m_pos_changed and t_pos_changed:
            if m_pos == t_pos:
                final_pos = m_pos
            else:
                # Concurrent position conflict!
                if position_strategy == PositionConflictStrategy.SHIFT:
                    # Deterministic vector shift (+20px, +20px) on the incoming mine position
                    final_pos = {"x": round(m_pos["x"] + 20.0, 2), "y": round(m_pos["y"] + 20.0, 2)}
                    conflicts.append(
                        MergeConflict(
                            conflict_type=ConflictType.POSITION_CONFLICT,
                            entity_type="node",
                            entity_id=node_id,
                            message=f"Concurrent position change on node '{node_id}'. Applied vector shift (+20px).",
                            resolvable=True,
                            resolution=f"shifted_vector(+20px):({final_pos['x']},{final_pos['y']})",
                            details={"base": b_pos, "theirs": t_pos, "mine": m_pos, "resolved": final_pos},
                        )
                    )
                    mutations.append(f"node:position_shifted:{node_id}")
                elif position_strategy == PositionConflictStrategy.LAST_WRITE_WINS or position_strategy == PositionConflictStrategy.MINE:
                    final_pos = m_pos
                    conflicts.append(
                        MergeConflict(
                            conflict_type=ConflictType.POSITION_CONFLICT,
                            entity_type="node",
                            entity_id=node_id,
                            message=f"Concurrent position change on node '{node_id}'. Last-write-wins (Mine) applied.",
                            resolvable=True,
                            resolution="mine_wins",
                            details={"base": b_pos, "theirs": t_pos, "mine": m_pos},
                        )
                    )
                    mutations.append(f"node:position_mine_wins:{node_id}")
                else:
                    final_pos = t_pos
                    conflicts.append(
                        MergeConflict(
                            conflict_type=ConflictType.POSITION_CONFLICT,
                            entity_type="node",
                            entity_id=node_id,
                            message=f"Concurrent position change on node '{node_id}'. Theirs retained.",
                            resolvable=True,
                            resolution="theirs_wins",
                            details={"base": b_pos, "theirs": t_pos, "mine": m_pos},
                        )
                    )

        cls._apply_position(merged, final_pos)

        # 2. Tag Merge (Set Union per spec)
        b_tags = set(base_node.get("tags") or [])
        t_tags = set(theirs_node.get("tags") or [])
        m_tags = set(mine_node.get("tags") or [])
        merged_tags = sorted(list(t_tags | m_tags))
        merged["tags"] = merged_tags
        if set(merged_tags) != t_tags:
            mutations.append(f"node:tags_union_merged:{node_id}")

        # 3. Description Concatenation & Diff Merge
        b_desc = str(base_node.get("description") or "").strip()
        t_desc = str(theirs_node.get("description") or "").strip()
        m_desc = str(mine_node.get("description") or "").strip()

        if m_desc != b_desc and t_desc != b_desc and m_desc != t_desc:
            # Both changed description: concatenate with markdown divider
            if m_desc in t_desc:
                merged["description"] = t_desc
            elif t_desc in m_desc:
                merged["description"] = m_desc
            else:
                merged["description"] = f"{t_desc}\n\n---\n{m_desc}".strip()
                conflicts.append(
                    MergeConflict(
                        conflict_type=ConflictType.DATA_CONFLICT,
                        entity_type="node",
                        entity_id=node_id,
                        message=f"Concurrent description edit on '{node_id}'. Merged via concatenation.",
                        resolvable=True,
                        resolution="concatenated",
                    )
                )
                mutations.append(f"node:description_concatenated:{node_id}")
        elif m_desc != b_desc:
            merged["description"] = m_desc
            mutations.append(f"node:description_updated_mine:{node_id}")
        else:
            merged["description"] = t_desc

        # 4. Target Files & Acceptance Criteria (Union)
        t_files = set(theirs_node.get("target_files") or [])
        m_files = set(mine_node.get("target_files") or [])
        merged["target_files"] = sorted(list(t_files | m_files))

        t_crit = list(theirs_node.get("acceptance_criteria") or [])
        m_crit = list(mine_node.get("acceptance_criteria") or [])
        seen_crit = set(t_crit)
        combined_crit = list(t_crit)
        for c in m_crit:
            if c not in seen_crit:
                combined_crit.append(c)
                seen_crit.add(c)
        merged["acceptance_criteria"] = combined_crit

        # 5. Scalar attributes: Title, Progress, Stage, Status, Priority
        # Progress: take highest progress achieved
        b_prog = float(base_node.get("progress") or 0.0)
        t_prog = float(theirs_node.get("progress") or 0.0)
        m_prog = float(mine_node.get("progress") or 0.0)
        merged["progress"] = max(t_prog, m_prog)

        # Title: Mine takes precedence if modified
        if mine_node.get("title") and mine_node.get("title") != base_node.get("title"):
            merged["title"] = mine_node["title"]

        # Stage & Status: advance if mine is further along
        if mine_node.get("stage") and mine_node.get("stage") != base_node.get("stage"):
            merged["stage"] = mine_node["stage"]
        if mine_node.get("status") and mine_node.get("status") != base_node.get("status"):
            merged["status"] = mine_node["status"]

        # Priority & Assigned Agent: Mine takes precedence if explicitly edited
        if mine_node.get("priority") and mine_node.get("priority") != base_node.get("priority"):
            merged["priority"] = mine_node["priority"]
        if mine_node.get("assigned_agent") and mine_node.get("assigned_agent") != base_node.get("assigned_agent"):
            merged["assigned_agent"] = mine_node["assigned_agent"]

        return merged, conflicts, mutations

    @classmethod
    def _merge_edges(
        cls,
        base_edges: List[Dict[str, Any]],
        theirs_edges: List[Dict[str, Any]],
        mine_edges: List[Dict[str, Any]],
        valid_node_ids: Set[str],
    ) -> Tuple[List[Dict[str, Any]], List[MergeConflict], List[str], bool]:
        conflicts: List[MergeConflict] = []
        mutations: List[str] = []
        has_cycle = False

        base_map = {cls._edge_key(e): e for e in base_edges}
        theirs_map = {cls._edge_key(e): e for e in theirs_edges}
        mine_map = {cls._edge_key(e): e for e in mine_edges}

        all_keys = set(base_map.keys()) | set(theirs_map.keys()) | set(mine_map.keys())
        candidate_edges: List[Dict[str, Any]] = []

        for key in sorted(all_keys):
            in_b = key in base_map
            in_t = key in theirs_map
            in_m = key in mine_map

            # Added by Mine
            if in_m and not in_b and not in_t:
                candidate_edges.append(deepcopy(mine_map[key]))
                mutations.append(f"edge:added_by_mine:{key}")
                continue

            # Added by Theirs
            if in_t and not in_b and not in_m:
                candidate_edges.append(deepcopy(theirs_map[key]))
                mutations.append(f"edge:added_by_theirs:{key}")
                continue

            # Added by both
            if in_m and in_t and not in_b:
                candidate_edges.append(deepcopy(mine_map[key]))
                mutations.append(f"edge:added_by_both:{key}")
                continue

            # Deleted by Mine
            if in_b and not in_m and in_t:
                edge_id = base_map[key].get("id") or f"{key[0]}->{key[1]}"
                mutations.append(f"edge:deleted:{edge_id}")
                mutations.append(f"edge:deleted_by_mine:{edge_id}")
                continue

            # Deleted by Theirs
            if in_b and in_m and not in_t:
                edge_id = base_map[key].get("id") or f"{key[0]}->{key[1]}"
                mutations.append(f"edge:deleted:{edge_id}")
                mutations.append(f"edge:deleted_by_theirs:{edge_id}")
                continue

            # Deleted by both
            if in_b and not in_m and not in_t:
                edge_id = base_map[key].get("id") or f"{key[0]}->{key[1]}"
                mutations.append(f"edge:deleted:{edge_id}")
                mutations.append(f"edge:deleted_by_both:{edge_id}")
                continue

            # In both (or all three)
            edge_data = deepcopy(mine_map[key]) if in_m else deepcopy(theirs_map[key])
            candidate_edges.append(edge_data)

        # Filter out orphan edges whose source or target nodes were deleted
        final_edges: List[Dict[str, Any]] = []
        for e in candidate_edges:
            s = str(e.get("source", ""))
            t = str(e.get("target", ""))
            if s not in valid_node_ids or t not in valid_node_ids:
                conflicts.append(
                    MergeConflict(
                        conflict_type=ConflictType.ORPHAN_EDGE,
                        entity_type="edge",
                        entity_id=str(e.get("id") or f"{s}->{t}"),
                        message=f"Edge '{s}->{t}' pruned: incident node does not exist in merged graph.",
                        resolvable=True,
                        resolution="pruned_orphan",
                        details={"edge": e},
                    )
                )
                mutations.append(f"edge:pruned_orphan:{s}->{t}")
            else:
                final_edges.append(e)

        # Cycle check (canon Kahn algorithm): target depends on source
        cycle_edges: List[Tuple[str, str]] = []
        for e in final_edges:
            s = str(e.get("source", ""))
            t = str(e.get("target", ""))
            rel = str(e.get("relation", "depends_on")).lower()
            if rel in ("depends_on", "blocks", "parent_of"):
                cycle_edges.append((s, t))
        cycle_node_ids = {n for edge in cycle_edges for n in edge}
        cyclic, _ = detect_cycles_kahn(cycle_node_ids, cycle_edges)

        if cyclic:
            has_cycle = True
            conflicts.append(
                MergeConflict(
                    conflict_type=ConflictType.CYCLE_DETECTED,
                    entity_type="edge",
                    entity_id="graph_cycle",
                    message="Irresolvable dependency cycle detected after merging edges.",
                    resolvable=False,
                    resolution=None,
                    details={"edges_count": len(final_edges)},
                )
            )

        return final_edges, conflicts, mutations, has_cycle

    @staticmethod
    def _normalize_graph(graph_input: Any) -> Dict[str, Any]:
        """Ensures graph representation is a standard dictionary."""
        if graph_input is None:
            return {"nodes": {}, "edges": [], "stages": []}

        if isinstance(graph_input, str):
            try:
                data = json.loads(graph_input)
            except Exception:
                return {"nodes": {}, "edges": [], "stages": []}
        elif hasattr(graph_input, "model_dump"):
            data = graph_input.model_dump()
        elif hasattr(graph_input, "dict"):
            data = graph_input.dict()
        elif isinstance(graph_input, dict):
            data = deepcopy(graph_input)
        else:
            return {"nodes": {}, "edges": [], "stages": []}

        # Normalize nodes: could be in data["nodes"] or data["elements"]["nodes"]
        raw_nodes = data.get("nodes")
        if raw_nodes is None and "elements" in data and isinstance(data["elements"], dict):
            raw_nodes = data["elements"].get("nodes")

        normalized_nodes: Dict[str, Dict[str, Any]] = {}
        if isinstance(raw_nodes, dict):
            for k, v in raw_nodes.items():
                if hasattr(v, "model_dump"):
                    normalized_nodes[k] = v.model_dump()
                elif isinstance(v, dict):
                    normalized_nodes[k] = deepcopy(v)
        elif isinstance(raw_nodes, list):
            for item in raw_nodes:
                if isinstance(item, dict) and "id" in item:
                    normalized_nodes[str(item["id"])] = deepcopy(item)
                elif hasattr(item, "id"):
                    n_id = getattr(item, "id")
                    dumped = getattr(item, "model_dump")() if hasattr(item, "model_dump") else dict(item)  # type: ignore
                    normalized_nodes[str(n_id)] = dumped

        data["nodes"] = normalized_nodes

        # Normalize edges
        raw_edges = data.get("edges")
        if raw_edges is None and "elements" in data and isinstance(data["elements"], dict):
            raw_edges = data["elements"].get("edges")

        normalized_edges: List[Dict[str, Any]] = []
        if isinstance(raw_edges, list):
            for item in raw_edges:
                if hasattr(item, "model_dump"):
                    normalized_edges.append(item.model_dump())
                elif isinstance(item, dict):
                    normalized_edges.append(deepcopy(item))

        data["edges"] = normalized_edges
        return data

    @staticmethod
    def _extract_position(node: Dict[str, Any]) -> Dict[str, float]:
        pos = node.get("position")
        if isinstance(pos, dict):
            return {"x": float(pos.get("x", 0.0)), "y": float(pos.get("y", 0.0))}
        elif pos is not None and hasattr(pos, "x") and hasattr(pos, "y"):
            return {"x": float(getattr(pos, "x")), "y": float(getattr(pos, "y"))}
        elif "x" in node and "y" in node:
            return {"x": float(node.get("x", 0.0)), "y": float(node.get("y", 0.0))}
        return {"x": 0.0, "y": 0.0}

    @staticmethod
    def _apply_position(node: Dict[str, Any], pos: Dict[str, float]) -> None:
        if "position" in node and isinstance(node["position"], dict):
            node["position"]["x"] = pos["x"]
            node["position"]["y"] = pos["y"]
        elif "position" in node and hasattr(node["position"], "x"):
            node["position"] = {"x": pos["x"], "y": pos["y"]}
        else:
            node["position"] = {"x": pos["x"], "y": pos["y"]}
        # Also keep root x, y if present
        if "x" in node:
            node["x"] = pos["x"]
        if "y" in node:
            node["y"] = pos["y"]

    @staticmethod
    def _edge_key(edge: Dict[str, Any]) -> str:
        if "id" in edge and edge["id"]:
            return str(edge["id"])
        s = edge.get("source", "")
        t = edge.get("target", "")
        rel = edge.get("relation", "depends_on")
        return f"{s}->{t}:{rel}"

    @staticmethod
    def _is_node_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
        # Compare key invariant attributes
        keys_to_compare = ["title", "description", "progress", "stage", "status", "tags", "priority"]
        for k in keys_to_compare:
            if a.get(k) != b.get(k):
                return False
        # Compare position
        pos_a = OCCConcurrencyEngine._extract_position(a)
        pos_b = OCCConcurrencyEngine._extract_position(b)
        return pos_a == pos_b


# Canonical aliases
OCCGraphMergeResolver = OCCConcurrencyEngine


class FileMergeStatus(str, Enum):
    CLEAN_MERGE = "CLEAN_MERGE"
    STRUCTURAL_MERGE = "STRUCTURAL_MERGE"
    CONFLICT = "CONFLICT"
    NO_MUTATION = "NO_MUTATION"

    def __str__(self) -> str:
        return self.value


class OCCFileMergeResult:
    """Outcome of an OCC file mutation merge across multiple workers."""

    def __init__(
        self,
        status: Union[FileMergeStatus, str],
        merged_content: Optional[str] = None,
        merged_data: Optional[Dict[str, Any]] = None,
        conflicts: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status = str(status)
        self.merged_content = merged_content
        self.merged_data = merged_data
        self.conflicts = conflicts or []
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "merged_content": self.merged_content,
            "merged_data": self.merged_data,
            "conflicts": self.conflicts,
            "details": self.details,
        }


class OCCFileMergeResolver:
    """
    3-Way Semantic & Structural OCC File Mutation Resolver.
    Resolves concurrent file edits from multiple swarm workers:
    1. Structural Graph / JSON state merge via OCCConcurrencyEngine
    2. Disjoint hunk 3-way text merge for code and config files
    3. Dictionary merge for generic JSON configurations
    """

    @classmethod
    def merge_text_mutations(
        cls, base_text: str, mutations: List[Dict[str, Any]]
    ) -> OCCFileMergeResult:
        """
        Merges concurrent text mutations from N workers against base_text.
        Each mutation dict: {'agent': str, 'new_text': str} (or 'content' / 'text')
        """
        if not mutations:
            return OCCFileMergeResult(
                status=FileMergeStatus.NO_MUTATION,
                merged_content=base_text,
                details={"reason": "No mutations provided"},
            )

        if len(mutations) == 1:
            mut = mutations[0]
            new_text = mut.get("new_text") or mut.get("content") or mut.get("text") or base_text
            return OCCFileMergeResult(
                status=FileMergeStatus.CLEAN_MERGE,
                merged_content=new_text,
                details={"agent": mut.get("agent"), "strategy": "single_worker_passthrough"},
            )

        base_lines = base_text.splitlines(keepends=True)
        all_edits = []

        for mut in mutations:
            agent = mut.get("agent", "worker")
            new_text = mut.get("new_text") or mut.get("content") or mut.get("text")
            if new_text is None:
                continue

            mut_lines = new_text.splitlines(keepends=True)
            sm = difflib.SequenceMatcher(None, base_lines, mut_lines)
            ops = [op for op in sm.get_opcodes() if op[0] != "equal"]

            for tag, i1, i2, j1, j2 in ops:
                all_edits.append({
                    "start": i1,
                    "end": i2,
                    "replacement": mut_lines[j1:j2],
                    "agent": agent,
                    "tag": tag,
                })

        if not all_edits:
            return OCCFileMergeResult(
                status=FileMergeStatus.NO_MUTATION,
                merged_content=base_text,
                details={"reason": "Workers produced identical content to base"},
            )

        # Sort edits by start line index, then end line index
        all_edits.sort(key=lambda x: (x["start"], x["end"]))

        # Check for overlapping edits (conflicts)
        conflicts = []
        for idx in range(len(all_edits) - 1):
            e1 = all_edits[idx]
            e2 = all_edits[idx + 1]

            has_overlap = not (e1["end"] <= e2["start"] or e2["end"] <= e1["start"])
            is_same_insert = (e1["start"] == e1["end"] == e2["start"] == e2["end"])

            if has_overlap or is_same_insert:
                if e1["replacement"] != e2["replacement"]:
                    conflicts.append({
                        "agents": [e1["agent"], e2["agent"]],
                        "span": (min(e1["start"], e2["start"]), max(e1["end"], e2["end"])),
                        "hunk_a": "".join(e1["replacement"]),
                        "hunk_b": "".join(e2["replacement"]),
                    })

        if conflicts:
            return OCCFileMergeResult(
                status=FileMergeStatus.CONFLICT,
                conflicts=conflicts,
                details={"conflicting_edits_count": len(conflicts)},
            )

        # Deduplicate identical edits (e.g. multiple workers made the same change)
        unique_edits = []
        for e in all_edits:
            if unique_edits:
                prev = unique_edits[-1]
                if (
                    prev["start"] == e["start"]
                    and prev["end"] == e["end"]
                    and prev["replacement"] == e["replacement"]
                ):
                    continue
            unique_edits.append(e)

        # Construct merged text
        merged_lines = []
        cursor = 0
        for edit in unique_edits:
            merged_lines.extend(base_lines[cursor:edit["start"]])
            merged_lines.extend(edit["replacement"])
            cursor = edit["end"]
        merged_lines.extend(base_lines[cursor:])

        return OCCFileMergeResult(
            status=FileMergeStatus.CLEAN_MERGE,
            merged_content="".join(merged_lines),
            details={
                "strategy": "3way_disjoint_merge",
                "total_edits": len(unique_edits),
                "participating_agents": list({e["agent"] for e in all_edits}),
            },
        )

    @classmethod
    def merge_json_mutations(
        cls, base_data: Dict[str, Any], mutations: List[Dict[str, Any]]
    ) -> OCCFileMergeResult:
        """
        Merges concurrent JSON/graph mutations. If nodes/edges exist, delegates to OCCConcurrencyEngine.
        Otherwise performs 3-way key-level dictionary reconciliation.
        """
        if not mutations:
            return OCCFileMergeResult(
                status=FileMergeStatus.NO_MUTATION,
                merged_data=base_data,
                merged_content=json.dumps(base_data, indent=2),
            )

        if len(mutations) == 1:
            mut_data = mutations[0].get("data") or mutations[0].get("new_data") or base_data
            return OCCFileMergeResult(
                status=FileMergeStatus.STRUCTURAL_MERGE,
                merged_data=mut_data,
                merged_content=json.dumps(mut_data, indent=2),
                details={"strategy": "single_worker_json_passthrough"},
            )

        # Check if graph structure (nodes + edges)
        is_graph = (
            ("nodes" in base_data and "edges" in base_data)
            or any("nodes" in m.get("data", {}) for m in mutations)
        )

        if is_graph and len(mutations) == 2:
            # Delegate to OCCConcurrencyEngine 3-way merge
            state_a = mutations[0].get("data", {})
            state_b = mutations[1].get("data", {})
            report = OCCConcurrencyEngine.merge_graph_state(
                base_state=base_data,
                current_state=state_a,
                incoming_state=state_b,
                position_strategy=PositionConflictStrategy.LAST_WRITE_WINS,
            )
            if report.has_unresolved_conflicts:
                return OCCFileMergeResult(
                    status=FileMergeStatus.CONFLICT,
                    conflicts=[c.to_dict() for c in report.conflicts],
                    details={"error": "Graph state contains unresolved conflicts", "status": report.status},
                )
            return OCCFileMergeResult(
                status=FileMergeStatus.STRUCTURAL_MERGE,
                merged_data=report.merged_graph,
                merged_content=json.dumps(report.merged_graph, indent=2),
                details={
                    "strategy": "occ_graph_3way_engine",
                    "status": report.status,
                    "applied_mutations": report.applied_mutations,
                },
            )

        # Generic dictionary reconciliation
        merged = deepcopy(base_data)
        conflicts = []

        # Collect keys changed by each mutation relative to base_data
        for mut in mutations:
            agent = mut.get("agent", "worker")
            data = mut.get("data") or mut.get("new_data") or {}
            for k, v in data.items():
                if k not in base_data or base_data[k] != v:
                    # Key changed or added
                    if k in merged and merged[k] != v and merged[k] != base_data.get(k):
                        conflicts.append({
                            "key": k,
                            "agent": agent,
                            "current_val": merged[k],
                            "incoming_val": v,
                        })
                    else:
                        merged[k] = v

        if conflicts:
            return OCCFileMergeResult(
                status=FileMergeStatus.CONFLICT,
                conflicts=conflicts,
                details={"dict_conflicts_count": len(conflicts)},
            )

        return OCCFileMergeResult(
            status=FileMergeStatus.STRUCTURAL_MERGE,
            merged_data=merged,
            merged_content=json.dumps(merged, indent=2),
            details={"strategy": "3way_dict_reconciliation"},
        )

    @classmethod
    def resolve_file(
        cls,
        file_path: str,
        base_content: Optional[str],
        worker_mutations: List[Dict[str, Any]],
    ) -> OCCFileMergeResult:
        """
        High-level dispatcher for arbitrary file mutations across workers.
        """
        # If base_content is missing, check if file exists on disk
        if base_content is None:
            p = Path(file_path) if "Path" in globals() else None
            if p and p.exists() and p.is_file():
                try:
                    base_content = p.read_text(encoding="utf-8")
                except Exception:
                    base_content = ""
            else:
                base_content = ""

        # Check if file is JSON
        is_json_file = file_path.endswith(".json") or file_path.endswith(".canvas")
        if is_json_file and base_content:
            try:
                base_json = json.loads(base_content)
                # Parse mutation data if string
                parsed_mutations = []
                for m in worker_mutations:
                    m_copy = deepcopy(m)
                    if "data" not in m_copy and "new_text" in m_copy:
                        try:
                            m_copy["data"] = json.loads(m_copy["new_text"])
                        except Exception:
                            pass
                    parsed_mutations.append(m_copy)
                return cls.merge_json_mutations(base_json, parsed_mutations)
            except Exception:
                pass

        return cls.merge_text_mutations(base_text=base_content or "", mutations=worker_mutations)

