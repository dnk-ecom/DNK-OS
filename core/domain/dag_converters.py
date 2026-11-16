# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/dag_converters.py"
# purpose: "Lossless-as-possible converters from legacy graph models (Task Forest TaskNode, NodeTaskGraph) into canon ThoughtDAG v2."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Converters into ThoughtDAG v2 (S3). Inputs are plain dicts or objects exposing
``to_dict()`` / ``model_dump()``; no import of the legacy packages is needed.
Anything without a v2 home is preserved in ``metadata`` (``legacy_*`` keys).
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.domain.dag_models import (
    NodeKind,
    NodeStatus,
    PriorityLevel,
    RunState,
    SCALE_ALIASES,
    Scale,
    TaskSpec,
    ThoughtDAGGraph,
    ThoughtNode,
    Wire,
    WireType,
    normalize_status,
)


def _as_dict(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    for attr in ("to_dict", "model_dump"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            return fn()
    raise TypeError(f"Cannot convert {type(obj).__name__} to dict")


def _priority(value: Any) -> PriorityLevel:
    try:
        return PriorityLevel(str(getattr(value, "value", value) or "medium").lower())
    except ValueError:
        return PriorityLevel.MEDIUM


# --- Task Forest (core/task_forest/models.py: TaskNode) ---

_TF_KIND = {
    "task": NodeKind.TASK,
    "goal": NodeKind.TASK,
    "bug": NodeKind.TASK,
    "idea": NodeKind.IDEA,
    "documentation": NodeKind.NOTE,
}


def task_forest_node_to_thought_node(raw: Any) -> ThoughtNode:
    d = _as_dict(raw)
    tf_type = str(d.get("type", "task"))
    meta = dict(d.get("metadata") or {})
    meta["legacy_tf_type"] = tf_type
    meta["legacy_stage"] = str(d.get("stage", "backlog"))
    if d.get("agent_status"):
        meta["legacy_agent_status"] = d["agent_status"]
    if d.get("completed_at"):
        meta["legacy_completed_at"] = str(d["completed_at"])

    progress = meta.get("progress")
    status = normalize_status(d.get("stage", "backlog"))
    if not isinstance(progress, (int, float)):
        progress = 1.0 if status is NodeStatus.DONE else 0.0

    run: Optional[RunState] = None
    if d.get("agent_run_id") or d.get("agent_status"):
        run = RunState(
            run_id=d.get("agent_run_id"),
            agent=d.get("assigned_agent"),
            state=str(d.get("agent_status") or "idle"),
        )

    return ThoughtNode(
        id=d["id"],
        kind=_TF_KIND.get(tf_type, NodeKind.TASK),
        title=d.get("title", "") or "Untitled",
        content=d.get("description", ""),
        status=status.value,
        metadata=meta,
        assigned_agent=d.get("assigned_agent"),
        tags=list(d.get("tags") or []),
        progress=max(0.0, min(1.0, float(progress))),
        priority=_priority(d.get("priority")),
        run=run,
        position=dict(d["position"]) if d.get("position") else None,
        size=dict(d["size"]) if d.get("size") else None,
        created_at=str(d["created_at"]) if d.get("created_at") else None,
        updated_at=str(d["updated_at"]) if d.get("updated_at") else None,
    )


def task_forest_to_thoughtdag(
    nodes: Iterable[Any], graph_id: str = "task_forest", project_id: str = "default"
) -> ThoughtDAGGraph:
    converted = [task_forest_node_to_thought_node(n) for n in nodes]
    by_id = {n.id: n for n in converted}
    wires: List[Wire] = []
    for raw in nodes:
        d = _as_dict(raw)
        for dep in d.get("dependencies") or []:
            if dep in by_id:
                wires.append(Wire(id=f"dep_{dep}_{d['id']}", from_node=dep, to_node=d["id"],
                                  wire_type=WireType.DEPENDENCY))
    return ThoughtDAGGraph(graph_id=graph_id, project_id=project_id, nodes=by_id, wires=wires)


# --- Node Tasks (services/dnk_node_tasks/models.py: NodeTaskGraph) ---

_NT_KIND_SCALE = {
    "idea": (NodeKind.IDEA, None),
    "epic": (NodeKind.TASK, SCALE_ALIASES["epic"]),
    "task": (NodeKind.TASK, SCALE_ALIASES["task"]),
    "slice": (NodeKind.TASK, SCALE_ALIASES["slice"]),
    "gate": (NodeKind.GATE, None),
}


def node_item_to_thought_node(raw: Any) -> ThoughtNode:
    d = _as_dict(raw)
    node_type = str(getattr(d.get("node_type"), "value", d.get("node_type", "task")))
    kind, scale = _NT_KIND_SCALE.get(node_type, (NodeKind.TASK, None))
    status = normalize_status(d.get("status", "ready"))
    pos = d.get("position")
    pos = _as_dict(pos) if pos is not None else None
    meta = {
        "legacy_node_type": node_type,
        "legacy_stage": str(getattr(d.get("stage"), "value", d.get("stage", ""))),
        "legacy_status": str(getattr(d.get("status"), "value", d.get("status", "ready"))),
        "target_module": d.get("target_module"),
        "target_files": list(d.get("target_files") or []),
    }
    return ThoughtNode(
        id=d["id"],
        kind=kind,
        title=d.get("title", "") or "Untitled",
        content=d.get("description", ""),
        project_id=d.get("project_id"),
        status=status.value,
        metadata=meta,
        assigned_agent=d.get("assigned_agent"),
        tags=list(d.get("tags") or []),
        scale=scale,
        progress=max(0.0, min(1.0, float(d.get("progress", 0.0)) / 100.0)),
        priority=_priority(d.get("priority")),
        spec=TaskSpec(goal=d.get("description", ""), acceptance_criteria=list(d.get("acceptance_criteria") or [])),
        position=pos,
        created_at=d.get("created_at") or None,
        updated_at=d.get("updated_at") or None,
    )


def kind_scale_for_type(type_name: Any) -> Tuple[NodeKind, Optional[Scale]]:
    """Single mapping from any legacy node `type` word (Task Forest or Node Tasks vocabulary)
    to (NodeKind, Scale): epic/slice/gate/idea from Node Tasks; goal/bug/documentation from Task Forest."""
    t = str(getattr(type_name, "value", type_name) or "task").strip().lower()
    if t in _NT_KIND_SCALE:
        return _NT_KIND_SCALE[t]
    if t in _TF_KIND:
        return _TF_KIND[t], None
    try:  # canon Task Forest scale words: field / sector / tree / bush / flower
        return NodeKind.TASK, Scale(t)
    except ValueError:
        return NodeKind.TASK, None


def node_task_graph_to_thoughtdag(raw: Any, graph_id: str = "node_tasks", project_id: str = "default") -> ThoughtDAGGraph:
    g = _as_dict(raw)
    nodes = {nid: node_item_to_thought_node(n) for nid, n in (g.get("nodes") or {}).items()}
    wires: List[Wire] = []
    for e in g.get("edges") or []:
        e = _as_dict(e)
        src, dst = e.get("source"), e.get("target")
        if src not in nodes or dst not in nodes:
            continue
        rel = str(getattr(e.get("relation"), "value", e.get("relation", "depends_on")))
        if rel == "parent_of":
            nodes[dst].parent_id = src
            if e.get("id"):
                nodes[dst].metadata["legacy_parent_edge_id"] = e["id"]
                nodes[dst].metadata["legacy_parent_edge_desc"] = e.get("description") or ""
            continue
        wire_type = WireType.CONTEXT if rel == "spawns_from" else WireType.DEPENDENCY
        wires.append(Wire(
            id=e.get("id") or f"{rel}_{src}_{dst}",
            from_node=src,
            to_node=dst,
            wire_type=wire_type,
            label=e.get("description") or None,
            validates=(rel == "validates"),
            metadata={"legacy_relation": rel},
        ))
    return ThoughtDAGGraph(graph_id=graph_id, project_id=project_id, nodes=nodes, wires=wires)


# --- Reverse: canon -> Node Tasks legacy dict shape (NodeItem / NodeTaskGraph), for API projections ---

_CANON_TO_NT_STATUS = {"done": "completed", "failed": "cancelled"}
_NT_STATUS_TO_STAGE = {
    "draft": "ideation", "backlog": "ideation", "blocked": "ready", "ready": "ready",
    "in_progress": "in_progress", "review": "verification", "completed": "completed", "cancelled": "completed",
}
_NT_STAGES = {"ideation", "architecture", "ready", "in_progress", "verification", "completed"}
_NT_STATUSES = {"draft", "backlog", "blocked", "ready", "in_progress", "review", "completed", "cancelled"}


def thought_node_to_node_item(node: ThoughtNode) -> Dict[str, Any]:
    """Inverse of `node_item_to_thought_node`: a dict accepted by `NodeItem(**d)`.
    Prefers the `legacy_*` metadata kept by the forward conversion; falls back to canon fields."""
    meta = node.metadata or {}
    canon_status = str(getattr(node.status, "value", node.status))
    status = meta.get("legacy_status")
    consistent = status in _NT_STATUSES and normalize_status(status).value == canon_status
    if not consistent:  # another writer changed the canon status: legacy_* hints are stale
        status = None
    if status not in _NT_STATUSES:
        status = _CANON_TO_NT_STATUS.get(canon_status, canon_status)
        if status not in _NT_STATUSES:
            status = "ready"
    stage = meta.get("legacy_stage") if consistent else None
    if stage not in _NT_STAGES:
        stage = _NT_STATUS_TO_STAGE[status]
    node_type = meta.get("legacy_node_type")
    if node_type not in {"idea", "epic", "task", "slice", "gate"}:
        if node.kind is NodeKind.IDEA:
            node_type = "idea"
        elif node.kind is NodeKind.GATE:
            node_type = "gate"
        else:
            node_type = {Scale.FIELD: "epic", Scale.SECTOR: "epic", Scale.TREE: "epic",
                         Scale.BUSH: "task", Scale.FLOWER: "slice"}.get(node.scale, "task")
    pos = node.position or {}
    out: Dict[str, Any] = {
        "id": node.id,
        "title": node.title,
        "description": node.content or "",
        "node_type": node_type,
        "stage": stage,
        "status": status,
        "progress": round(max(0.0, min(1.0, float(node.progress))) * 100.0, 4),
        "assigned_agent": node.assigned_agent,
        "target_files": list(meta.get("target_files") or []),
        "acceptance_criteria": list(node.spec.acceptance_criteria) if node.spec else [],
        "tags": list(node.tags or []),
        "priority": str(getattr(node.priority, "value", node.priority)),
        "position": {"x": float(pos.get("x", 0.0)), "y": float(pos.get("y", 0.0))},
        "created_at": node.created_at or "",
        "updated_at": node.updated_at or "",
    }
    if node.project_id:
        out["project_id"] = node.project_id
    if meta.get("target_module") is not None:
        out["target_module"] = meta["target_module"]
    return out


def thoughtdag_to_node_task_graph(graph: ThoughtDAGGraph) -> Dict[str, Any]:
    """Inverse of `node_task_graph_to_thoughtdag`: {"nodes": {id: NodeItem dict}, "edges": [DependencyEdge dict]}.
    `is_blocked`/`blocked_by` are left to the persistence layer, which recomputes them."""
    nodes = {nid: thought_node_to_node_item(n) for nid, n in graph.nodes.items()}
    edges: List[Dict[str, Any]] = []
    for w in graph.wires:
        rel = (w.metadata or {}).get("legacy_relation")
        if rel not in {"depends_on", "spawns_from", "blocks", "validates", "parent_of"}:
            rel = "validates" if w.validates else ("spawns_from" if w.wire_type is WireType.CONTEXT else "depends_on")
        edges.append({"id": w.id, "source": w.from_node, "target": w.to_node, "relation": rel,
                      "description": w.label or ""})
    for nid, n in graph.nodes.items():
        if n.parent_id and n.parent_id in graph.nodes:
            m = n.metadata or {}
            edges.append({"id": m.get("legacy_parent_edge_id") or f"parent_of_{n.parent_id}_{nid}",
                          "source": n.parent_id, "target": nid, "relation": "parent_of",
                          "description": m.get("legacy_parent_edge_desc") or ""})
    return {"nodes": nodes, "edges": edges}


# --- Reverse + merge: canon -> core.task_forest TaskNode dict shape (untangle D1.4c) ---

_TF_STAGE_FROM_STATUS = {
    "draft": "backlog", "backlog": "backlog", "blocked": "backlog", "ready": "planned",
    "in_progress": "in_progress", "review": "review", "done": "done", "failed": "backlog", "cancelled": "backlog",
}
_TF_STAGES = {"backlog", "planned", "in_progress", "review", "done"}
_TF_TYPES = {"task", "idea", "goal", "bug", "documentation"}


def thought_node_to_task_node_dict(node: ThoughtNode, dependencies: Iterable[str] = ()) -> Dict[str, Any]:
    """Inverse of `task_forest_node_to_thought_node`: a dict accepted by `TaskNode.from_dict`."""
    meta = dict(node.metadata or {})
    canon_status = str(getattr(node.status, "value", node.status))
    stage = meta.get("legacy_stage")
    if stage not in _TF_STAGES or normalize_status(stage).value != canon_status:
        stage = _TF_STAGE_FROM_STATUS.get(canon_status, "backlog")
    tf_type = meta.get("legacy_tf_type")
    if tf_type not in _TF_TYPES and meta.get("legacy_node_type") in _TF_TYPES:
        tf_type = meta["legacy_node_type"]  # e.g. a note imported from the vault
    if tf_type not in _TF_TYPES:
        tf_type = "idea" if node.kind is NodeKind.IDEA else ("documentation" if node.kind is NodeKind.NOTE else "task")
    completed_at = meta.get("legacy_completed_at")
    agent_status = None
    if node.run is not None and (node.run.state != "idle" or meta.get("legacy_agent_status")):
        agent_status = node.run.state
    plain = {k: v for k, v in meta.items() if not str(k).startswith("legacy_")}
    if abs(float(node.progress) - (1.0 if canon_status == "done" else 0.0)) > 1e-9:
        plain["progress"] = float(node.progress)  # keep canon-side progress; forward conversion reads it back
    return {
        "id": node.id,
        "type": tf_type,
        "title": node.title,
        "description": node.content or "",
        "stage": stage,
        "priority": str(getattr(node.priority, "value", node.priority)),
        "dependencies": list(dependencies),
        "tags": list(node.tags or []),
        "created_at": node.created_at,
        "updated_at": node.updated_at,
        "completed_at": completed_at,
        "assigned_agent": node.assigned_agent,
        "agent_status": agent_status,
        "agent_run_id": node.run.run_id if node.run else None,
        "metadata": plain,
        "position": dict(node.position) if node.position else {"x": 0.0, "y": 0.0},
        "size": dict(node.size) if node.size else {"width": 260.0, "height": 140.0},
    }


def _is_dep_wire(w: Wire) -> bool:
    return w.wire_type is WireType.DEPENDENCY and not w.validates


def thoughtdag_to_task_forest_dicts(graph: ThoughtDAGGraph) -> List[Dict[str, Any]]:
    deps: Dict[str, List[str]] = {nid: [] for nid in graph.nodes}
    for w in graph.wires:
        if _is_dep_wire(w) and w.from_node in graph.nodes and w.to_node in graph.nodes:
            if w.from_node not in deps[w.to_node]:
                deps[w.to_node].append(w.from_node)
    return [thought_node_to_task_node_dict(n, deps[nid]) for nid, n in graph.nodes.items()]


def merge_task_forest_into_graph(graph: ThoughtDAGGraph, tf_dicts: Iterable[Dict[str, Any]]) -> ThoughtDAGGraph:
    """Apply TaskNode dicts onto `graph` in place without discarding canon-only data: kind/scale/spec/
    parent_id of known nodes and every non-dependency wire (context, data stream, validates) survive."""
    tf_dicts = list(tf_dicts)
    incoming = {d["id"]: d for d in tf_dicts}
    for nid in [n for n in graph.nodes if n not in incoming]:
        del graph.nodes[nid]
    graph.wires = [w for w in graph.wires if w.from_node in graph.nodes and w.to_node in graph.nodes]

    for d in tf_dicts:
        new = task_forest_node_to_thought_node(d)
        old = graph.nodes.get(d["id"])
        if old is None:
            graph.nodes[new.id] = new
            continue
        changed_type = (old.metadata or {}).get("legacy_tf_type") != new.metadata.get("legacy_tf_type")
        update: Dict[str, Any] = {
            "title": new.title, "content": new.content, "status": new.status, "metadata": new.metadata,
            "assigned_agent": new.assigned_agent, "tags": new.tags, "progress": new.progress,
            "priority": new.priority, "run": new.run, "position": new.position, "size": new.size,
            "created_at": new.created_at, "updated_at": new.updated_at,
        }
        if changed_type:
            update["kind"] = new.kind
        graph.nodes[new.id] = old.model_copy(update=update)

    wanted = {(dep, d["id"]) for d in tf_dicts for dep in (d.get("dependencies") or []) if dep in graph.nodes}
    kept: List[Wire] = []
    present = set()
    for w in graph.wires:
        if _is_dep_wire(w):
            if (w.from_node, w.to_node) not in wanted or (w.from_node, w.to_node) in present:
                continue
            present.add((w.from_node, w.to_node))
        kept.append(w)
    for d in tf_dicts:
        for dep in d.get("dependencies") or []:
            if (dep, d["id"]) in wanted and (dep, d["id"]) not in present:
                present.add((dep, d["id"]))
                kept.append(Wire(id=f"dep_{dep}_{d['id']}", from_node=dep, to_node=d["id"], wire_type=WireType.DEPENDENCY))
    graph.wires = kept
    return graph


# --- Task Forest router store (apps/api/routers/tasks/forest.py: TaskForestNode + TaskDependencyWire) ---

def forest_node_to_thought_node(raw: Any) -> ThoughtNode:
    d = _as_dict(raw)
    scale_raw = str(d.get("plant_scale", "")).lower()
    scale = Scale(scale_raw) if scale_raw in {s.value for s in Scale} else SCALE_ALIASES.get(scale_raw)
    status = normalize_status(d.get("status", "todo"))
    meta = {
        "legacy_status": str(d.get("status", "")),
        "author": d.get("author"),
        "verification_status": d.get("verification_status"),
        "git_diff": d.get("git_diff"),
        "dto_contract": d.get("dto_contract"),
    }
    return ThoughtNode(
        id=d["id"],
        kind=NodeKind.PROJECT if scale is Scale.FIELD else NodeKind.TASK,
        title=d.get("title", "") or "Untitled",
        status=status.value,
        metadata={k: v for k, v in meta.items() if v is not None},
        assigned_agent=d.get("assigned_agent"),
        scale=scale,
        parent_id=d.get("parent_id"),
        progress=max(0.0, min(1.0, float(d.get("progress", 0.0)) / 100.0)),
        weight=float(d.get("weight", 1.0)),
        updated_at=d.get("updated_at"),
    )


_CANON_TO_FOREST_STATUS = {
    "draft": "todo", "backlog": "todo", "ready": "ready", "blocked": "blocked", "in_progress": "in_progress",
    "review": "verifying", "done": "done", "failed": "failed", "cancelled": "cancelled",
}


def thought_node_to_forest_node_dict(node: ThoughtNode) -> Dict[str, Any]:
    """Inverse of `forest_node_to_thought_node`: kwargs for the router's `TaskForestNode`."""
    meta = node.metadata or {}
    canon_status = str(getattr(node.status, "value", node.status))
    status = meta.get("legacy_status")
    if not status or normalize_status(status).value != canon_status:
        status = _CANON_TO_FOREST_STATUS.get(canon_status, "todo")
    scale = node.scale.value if node.scale else ("field" if node.kind is NodeKind.PROJECT else "flower")
    return {
        "id": node.id,
        "title": node.title,
        "plant_scale": scale,
        "status": status,
        "progress": round(max(0.0, min(1.0, float(node.progress))) * 100.0, 4),
        "parent_id": node.parent_id,
        "assigned_agent": node.assigned_agent,
        "author": meta.get("author"),
        "weight": float(node.weight),
        "git_diff": meta.get("git_diff"),
        "dto_contract": meta.get("dto_contract"),
        "verification_status": meta.get("verification_status"),
        "updated_at": node.updated_at or "",
    }


def thoughtdag_to_forest_dicts(graph: ThoughtDAGGraph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """(node dicts, wire dicts) in the router's `TaskForestNode` / `TaskDependencyWire` shape."""
    nodes = [thought_node_to_forest_node_dict(n) for n in graph.nodes.values()]
    wires = [
        {"source_id": w.from_node, "target_id": w.to_node,
         "wire_kind": (w.metadata or {}).get("legacy_wire_kind", "data_dependency")}
        for w in graph.wires if w.wire_type is WireType.DEPENDENCY and not w.validates
    ]
    return nodes, wires


def forest_to_thoughtdag(
    nodes: Iterable[Any], wires: Iterable[Any] = (), graph_id: str = "task_forest", project_id: str = "default"
) -> ThoughtDAGGraph:
    by_id = {n.id: n for n in (forest_node_to_thought_node(r) for r in nodes)}
    out: List[Wire] = []
    for raw in wires:
        w = _as_dict(raw)
        src, dst = w.get("source_id"), w.get("target_id")
        if src in by_id and dst in by_id:
            out.append(Wire(id=f"wire_{src}_{dst}", from_node=src, to_node=dst, wire_type=WireType.DEPENDENCY,
                            metadata={"legacy_wire_kind": w.get("wire_kind", "data_dependency")}))
    return ThoughtDAGGraph(graph_id=graph_id, project_id=project_id, nodes=by_id, wires=out)


def dag_view(graph: ThoughtDAGGraph) -> Dict[str, Any]:
    """Canon read-model returned by the facades: graph + stats + critical path + ready set."""
    from core.domain import dag_algorithms as algo

    algo.recompute_blocked(graph)
    return {
        "graph": graph.model_dump(mode="json"),
        "stats": algo.statistics(graph),
        "critical_path": algo.critical_path(graph),
        "ready": algo.ready_nodes(graph),
        "topological_order": algo.topological_order(graph),
    }
