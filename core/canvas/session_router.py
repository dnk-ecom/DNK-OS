# --- DNK-MRH-HEADER ---
# mrh_id: "core/canvas/session_router.py"
# purpose: "Spatial Canvas Per-Node Session Router & Dual-State Context Compiler for Vibe-Coding (session_id = node:{canvas_id}:{node_id})."
# canonical_source: true
# alters_files: ["~/.dnk_runtime/agents_state/spatial_canvas_sessions.db", "docs/canvas/*.canvas"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
Spatial Canvas Per-Node Session Router & Dual-State Context Compiler.

Implements the Dual-State Storage & Context Surgery Architecture (ADR-092):
- Layer 1: Open JSON Canvas 1.0 file (Obsidian & Git SSOT).
- Layer 2: SQLite WAL Thread Store (~/.dnk_runtime/agents_state/spatial_canvas_sessions.db).

Guarantees 100% conversational isolation between canvas nodes:
    session_id = f"node:{canvas_id}:{node_id}"

When an agent enters a node, the compiler traverses upstream DAG wires
and injects ONLY the crystallized output contracts of parent nodes,
completely eliminating chat bloat and amnesia.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("dnk.canvas.session_router")

# Default database location in 4-zone APFS runtime with fallback
DEFAULT_DB_PATH = Path(os.path.expanduser("~/.dnk_runtime/agents_state/spatial_canvas_sessions.db"))
FALLBACK_DB_PATH = Path(".data/spatial_canvas_sessions.db")


class NodeSession(BaseModel):
    """Metadata and state of an isolated node chat session."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    canvas_id: str
    node_id: str
    agent_role: str
    status: str = "active"  # "active", "crystallized", "archived"
    crystallized_summary: Optional[str] = None
    artifact_refs: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ChatMessage(BaseModel):
    """Single message within a node-isolated conversation thread."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    session_id: str
    role: str  # "user", "assistant", "system"
    content: str
    meta_json: Optional[str] = None
    created_at: str


class UpstreamContract(BaseModel):
    """Crystallized output contract from a parent node in the DAG."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str
    title: str
    summary: str
    artifacts: List[str] = Field(default_factory=list)


class NodeContextPrompt(BaseModel):
    """Compiled context delivered to the agent driving a canvas node."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    canvas_id: str
    node_id: str
    node_title: str
    node_task: str
    agent_role: str
    upstream_contracts: List[UpstreamContract]
    system_prompt: str
    project_dna: Optional[Dict[str, Any]] = None
    account_spec: Optional[Dict[str, Any]] = None


class SpatialCanvasSessionRouter:
    """
    Coordinates per-node session lifecycle, SQLite persistence, and context surgery.
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is not None:
            self.db_path = db_path
        elif DEFAULT_DB_PATH.parent.exists():
            self.db_path = DEFAULT_DB_PATH
        else:
            self.db_path = FALLBACK_DB_PATH

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS node_chat_sessions (
                    id TEXT PRIMARY KEY,
                    canvas_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    crystallized_summary TEXT,
                    artifact_refs TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS node_chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    meta_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES node_chat_sessions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session ON node_chat_messages(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_canvas_node ON node_chat_sessions(canvas_id, node_id);
            """)

    @staticmethod
    def format_session_id(canvas_id: str, node_id: str) -> str:
        """Deterministic 1:1 mapping from canvas node to session."""
        clean_canvas = canvas_id.removesuffix(".canvas")
        return f"node:{clean_canvas}:{node_id}"

    def get_or_create_session(
        self, canvas_id: str, node_id: str, agent_role: str = "general_agent"
    ) -> NodeSession:
        """Retrieve existing session or instantiate a new isolated thread."""
        session_id = self.format_session_id(canvas_id, node_id)
        clean_canvas = canvas_id.removesuffix(".canvas")

        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM node_chat_sessions WHERE id = ?", (session_id,)
            ).fetchone()

            if row:
                artifacts = json.loads(row["artifact_refs"]) if row["artifact_refs"] else []
                return NodeSession(
                    id=row["id"],
                    canvas_id=row["canvas_id"],
                    node_id=row["node_id"],
                    agent_role=row["agent_role"],
                    status=row["status"],
                    crystallized_summary=row["crystallized_summary"],
                    artifact_refs=artifacts,
                    created_at=str(row["created_at"]),
                    updated_at=str(row["updated_at"]),
                )

            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """
                INSERT INTO node_chat_sessions
                (id, canvas_id, node_id, agent_role, status, artifact_refs, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'active', '[]', ?, ?)
                """,
                (session_id, clean_canvas, node_id, agent_role, now_str, now_str),
            )

            return NodeSession(
                id=session_id,
                canvas_id=clean_canvas,
                node_id=node_id,
                agent_role=agent_role,
                status="active",
                crystallized_summary=None,
                artifact_refs=[],
                created_at=now_str,
                updated_at=now_str,
            )

    def post_message(
        self,
        session_id: str,
        role: str,
        content: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Append a message to the isolated node thread."""
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        meta_json = json.dumps(meta) if meta else None
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO node_chat_messages (id, session_id, role, content, meta_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (msg_id, session_id, role, content, meta_json, now_str),
            )
            conn.execute(
                "UPDATE node_chat_sessions SET updated_at = ? WHERE id = ?",
                (now_str, session_id),
            )

        return ChatMessage(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            meta_json=meta_json,
            created_at=now_str,
        )

    def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Fetch chronological message history for a node."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, meta_json, created_at
                FROM node_chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

            return [
                ChatMessage(
                    id=r["id"],
                    session_id=r["session_id"],
                    role=r["role"],
                    content=r["content"],
                    meta_json=r["meta_json"],
                    created_at=str(r["created_at"]),
                )
                for r in rows
            ]

    def crystallize_node(
        self,
        canvas_path: Path,
        node_id: str,
        summary: str,
        artifact_refs: Optional[List[str]] = None,
    ) -> NodeSession:
        """
        Crystallize node outcome:
        1. Store summary contract & artifact links in SQLite (guaranteeing session exists).
        2. Set session status to 'crystallized'.
        3. Atomically sync the contract directly into the JSON Canvas 1.0 file.
        """
        canvas_id = canvas_path.stem
        # Ensure session exists in DB before updating
        self.get_or_create_session(canvas_id, node_id)
        session_id = self.format_session_id(canvas_id, node_id)
        artifacts = artifact_refs or []
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Update SQLite Layer
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE node_chat_sessions
                SET status = 'crystallized',
                    crystallized_summary = ?,
                    artifact_refs = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (summary, json.dumps(artifacts), now_str, session_id),
            )

        # 2. Synchronize to .canvas file (Git & Obsidian Layer)
        if canvas_path.exists():
            self._sync_crystallization_to_canvas(canvas_path, node_id, summary, artifacts)

        return self.get_or_create_session(canvas_id, node_id)

    def _sync_crystallization_to_canvas(
        self, canvas_path: Path, node_id: str, summary: str, artifacts: List[str]
    ) -> None:
        """Atomically update node text in the .canvas file with pinned contract."""
        try:
            with open(canvas_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("Failed to read canvas file %s: %s", canvas_path, e)
            return

        nodes = data.get("nodes", [])
        updated = False

        for node in nodes:
            if node.get("id") == node_id:
                old_text = node.get("text", "")
                title_line = old_text.splitlines()[0] if old_text else f"Node {node_id}"
                if not title_line.startswith("#"):
                    title_line = f"### {title_line}"

                agent_line = ""
                import re
                for l in old_text.splitlines():
                    if re.search(r"[*_]*agent[*_]*\s*:\s*", l, re.IGNORECASE):
                        agent_line = f"\n{l.strip()}"
                        break

                artifact_block = ""
                if artifacts:
                    artifact_block = "\n**Artifacts**:\n" + "\n".join(f"- `{a}`" for a in artifacts)

                new_text = (
                    f"{title_line}\n"
                    f"{agent_line}\n"
                    f"**Status**: 📌 CRYSTALLIZED\n"
                    f"**Output Contract**:\n{summary}\n"
                    f"{artifact_block}"
                )
                node["text"] = new_text
                node["color"] = "4"  # Green in JSON Canvas / Obsidian
                updated = True
                break

        if updated:
            with tempfile.NamedTemporaryFile("w", dir=canvas_path.parent, delete=False) as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name
            os.replace(temp_name, canvas_path)

    def find_project_dna(self, canvas_path: Path) -> Optional[Any]:
        """
        Locate and load L2 ProjectDNA for the canvas.
        Discovery order:
        1. Check if canvas content references a brand_dna.json or project.manifest.yaml.
        2. Check for brand_dna.json in matching docs/projects/<project_name>/ folder.
        3. Fallback to default project if exists.
        """
        try:
            from core.domain.vibe_core_contracts import ProjectDNA
        except ImportError:
            return None

        # 1. Check canvas content for explicit path
        try:
            if canvas_path.exists():
                with open(canvas_path, "r", encoding="utf-8") as f:
                    content = f.read()
                import re
                if "brand_dna.json" in content or "project.manifest.yaml" in content:
                    for candidate in [
                        Path("docs/projects/dnk_ecom/brand_dna.json"),
                        canvas_path.parent / "brand_dna.json",
                        canvas_path.parent.parent / "brand_dna.json",
                    ]:
                        if candidate.exists():
                            with open(candidate, "r", encoding="utf-8") as df:
                                return ProjectDNA.model_validate(json.load(df))
        except Exception as e:
            logger.debug("Failed parsing canvas for DNA: %s", e)

        # 2. Derive project folder from canvas_path (e.g. docs/canvas/projects/<proj>/...)
        parts = canvas_path.parts
        if "projects" in parts:
            idx = parts.index("projects")
            if idx + 1 < len(parts):
                proj_name = parts[idx + 1]
                candidate = Path(f"docs/projects/{proj_name}/brand_dna.json")
                if candidate.exists():
                    try:
                        with open(candidate, "r", encoding="utf-8") as df:
                            return ProjectDNA.model_validate(json.load(df))
                    except Exception as e:
                        logger.warning("Failed loading ProjectDNA from %s: %s", candidate, e)

        # 3. Fallback to default project if exists
        default_candidate = Path("docs/projects/dnk_ecom/brand_dna.json")
        if default_candidate.exists() and ("dnk_ecom" in str(canvas_path) or "shopify" in str(canvas_path)):
            try:
                with open(default_candidate, "r", encoding="utf-8") as df:
                    return ProjectDNA.model_validate(json.load(df))
            except Exception:
                pass

        return None

    def find_account_spec(self, config_path: Optional[Path] = None) -> Optional[Any]:
        """
        Locate and load L1 AccountSpec (Sovereign Vibe-Coder Workstation Profile).
        Discovery order:
        1. Explicit config_path if provided.
        2. core/config/vibe_coder_account.json
        3. config/vibe_coder_account.json
        4. .data/vibe_coder_account.json
        """
        try:
            from core.domain.vibe_core_contracts import AccountSpec
        except ImportError:
            return None

        candidates: List[Path] = []
        if config_path:
            candidates.append(config_path)
        candidates.extend([
            Path("core/config/vibe_coder_account.json"),
            Path("config/vibe_coder_account.json"),
            Path(".data/vibe_coder_account.json"),
        ])

        for candidate in candidates:
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        return AccountSpec.model_validate(json.load(f))
                except Exception as e:
                    logger.warning("Failed loading AccountSpec from %s: %s", candidate, e)

        return None

    def decompose_node_to_subtasks(
        self,
        canvas_path: Path,
        parent_node_id: str,
        subtasks: List[Any],
    ) -> List[str]:
        """
        Chat-to-DAG Tree Spawner (ThoughtDAG + BuilderIO visual-plans):
        Decomposes a parent node into a tree of child subtask nodes on the canvas,
        wires directed edges from parent to children, updates parent status,
        and initializes isolated SQLite sessions for all subtasks.
        """
        if not canvas_path.exists():
            raise FileNotFoundError(f"Canvas not found at: {canvas_path}")

        with open(canvas_path, "r", encoding="utf-8") as f:
            canvas_data = json.load(f)

        nodes = canvas_data.get("nodes", [])
        edges = canvas_data.setdefault("edges", [])

        parent_node = next((n for n in nodes if n.get("id") == parent_node_id), None)
        if not parent_node:
            raise KeyError(f"Parent node '{parent_node_id}' not found in canvas '{canvas_path.name}'")

        parent_x = parent_node.get("x", 0)
        parent_y = parent_node.get("y", 0)
        parent_w = parent_node.get("width", 380)
        parent_h = parent_node.get("height", 240)

        child_w = 380
        child_h = 240
        gap_x = 40
        child_y = parent_y + parent_h + 120
        total_width = len(subtasks) * child_w + max(0, len(subtasks) - 1) * gap_x
        start_x = parent_x + (parent_w // 2) - (total_width // 2)

        created_ids: List[str] = []
        existing_edge_ids = {e["id"] for e in edges if "id" in e}
        canvas_id = canvas_path.stem

        for i, subtask in enumerate(subtasks):
            child_x = start_x + i * (child_w + gap_x)

            node_id = getattr(subtask, "node_id", None) or (subtask.get("node_id") if isinstance(subtask, dict) else f"subtask_{i+1}")
            title = getattr(subtask, "title", None) or (subtask.get("title") if isinstance(subtask, dict) else f"Subtask {i+1}")
            goal = getattr(subtask, "goal", None) or (subtask.get("goal") if isinstance(subtask, dict) else "")
            
            agent_role = getattr(subtask, "assigned_agent", None)
            if hasattr(agent_role, "value"):
                agent_role = agent_role.value
            elif not agent_role:
                agent_role = subtask.get("assigned_agent", "general_agent") if isinstance(subtask, dict) else "general_agent"

            verification = getattr(subtask, "verification", None)
            v_cmd = getattr(verification, "command", None) if verification else (subtask.get("verification", {}).get("command") if isinstance(subtask, dict) else "exit 0")

            actions = getattr(subtask, "actions", []) or (subtask.get("actions", []) if isinstance(subtask, dict) else [])
            action_lines = ""
            if actions:
                action_strs = []
                for a in actions:
                    act_id = getattr(a, "action_id", None) or (a.get("action_id") if isinstance(a, dict) else str(a))
                    label = getattr(a, "label_uk", None) or (a.get("label_uk") if isinstance(a, dict) else "")
                    action_strs.append(f"- `{act_id}`: {label}")
                action_lines = "\n**Actions**:\n" + "\n".join(action_strs)

            child_text = (
                f"### {title}\n\n"
                f"**Goal**: {goal}\n"
                f"**Agent**: `{agent_role}`\n"
                f"**Status**: `decomposed`\n"
                f"**Verification**: `{v_cmd}`\n"
                f"{action_lines}"
            )

            new_node = {
                "id": node_id,
                "type": "text",
                "text": child_text,
                "x": child_x,
                "y": child_y,
                "width": child_w,
                "height": child_h,
                "color": "1",
            }
            nodes.append(new_node)
            created_ids.append(node_id)

            edge_id = f"edge_{parent_node_id}_to_{node_id}"
            if edge_id not in existing_edge_ids:
                edges.append({
                    "id": edge_id,
                    "fromNode": parent_node_id,
                    "fromSide": "bottom",
                    "toNode": node_id,
                    "toSide": "top",
                    "label": f"Subtask: {title[:20]}",
                })
                existing_edge_ids.add(edge_id)

            # Initialize isolated SQLite WAL session
            self.get_or_create_session(canvas_id, node_id, agent_role=str(agent_role))

        # Update parent node status
        parent_text = parent_node.get("text", "")
        if "**Status**:" not in parent_text:
            parent_node["text"] = parent_text + "\n\n**Status**: 🌿 DECOMPOSED"
        parent_node["color"] = "3"  # Yellow/Orange

        # Atomically write to canvas file
        with tempfile.NamedTemporaryFile("w", dir=canvas_path.parent, delete=False) as tf:
            json.dump(canvas_data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, canvas_path)

        return created_ids

    @staticmethod
    def topological_sort_subdag(
        nodes_map: Dict[str, Any],
        edges: List[Dict[str, Any]],
        target_node_id: str,
        filter_nodes: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Chain-preserving Kahn's topological sort for Canvas SubDAGs (assimilated from ZM-BAD/DAG-chat).
        Gathers ancestors leading to target_node_id and returns them in topological order,
        preserving causal sequence chains without interleaving unrelated branches.
        If filter_nodes is provided, restricts output to only those nodes, sorted in topological order.
        """
        from collections import defaultdict, deque

        parent_map = defaultdict(list)
        child_map = defaultdict(list)
        for e in edges:
            fn = e.get("fromNode")
            tn = e.get("toNode")
            if fn and tn:
                parent_map[tn].append(fn)
                child_map[fn].append(tn)

        # Collect ancestors
        ancestors = set()
        queue = deque(parent_map.get(target_node_id, []))
        while queue:
            curr = queue.popleft()
            if curr not in ancestors and curr in nodes_map:
                ancestors.add(curr)
                queue.extend(parent_map.get(curr, []))

        if not ancestors:
            return []

        subdag_nodes = set(ancestors)
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        subdag_edges = defaultdict(list)

        for n in subdag_nodes:
            for p in parent_map.get(n, []):
                if p in subdag_nodes:
                    in_degree[n] += 1
            for c in child_map.get(n, []):
                if c in subdag_nodes:
                    out_degree[n] += 1
                    subdag_edges[n].append(c)

        available = {n for n in subdag_nodes if in_degree[n] == 0}
        in_deg_dyn = defaultdict(int, in_degree)
        result: List[str] = []

        while available:
            selected = None
            if result:
                last = result[-1]
                # Strategy 1: Continue existing chain
                for child in subdag_edges.get(last, []):
                    if child in available and in_degree[child] == 1:
                        selected = child
                        break
                # Strategy 2: Node that starts a linear chain
                if selected is None:
                    for n in sorted(available):
                        if in_degree[n] == 1 and out_degree.get(n, 0) == 1:
                            selected = n
                            break
                # Strategy 3: Deterministic fallback
                if selected is None:
                    selected = min(available)
            else:
                selected = min(available)

            result.append(selected)
            available.remove(selected)

            for child in subdag_edges.get(selected, []):
                in_deg_dyn[child] -= 1
                if in_deg_dyn[child] == 0:
                    available.add(child)

        if filter_nodes is not None:
            return [n for n in result if n in filter_nodes]

        return result

    def compile_node_context(
        self, canvas_path: Path, node_id: str
    ) -> NodeContextPrompt:
        """
        Compile context for a node using Graph Context Surgery:
        1. Parse .canvas graph structure.
        2. Find all direct upstream parent nodes.
        3. Collect their crystallized contracts (0 raw tokens, only clean facts).
        4. Auto-discover L2 ProjectDNA (Zero Context Re-typing).
        5. Synthesize zero-waste system prompt for the node agent.
        """
        if not canvas_path.exists():
            raise FileNotFoundError(f"Canvas not found at: {canvas_path}")

        with open(canvas_path, "r", encoding="utf-8") as f:
            canvas_data = json.load(f)

        nodes_map = {n["id"]: n for n in canvas_data.get("nodes", [])}
        edges = canvas_data.get("edges", [])

        target_node = nodes_map.get(node_id)
        if not target_node:
            raise KeyError(f"Node '{node_id}' not found in canvas '{canvas_path.name}'")

        # Find direct upstream ancestors (where toNode == node_id)
        upstream_node_ids = [e["fromNode"] for e in edges if e.get("toNode") == node_id]
        if len(upstream_node_ids) > 1:
            # Sort multiple parents topologically preserving causal chains (DAG-chat Kahn algorithm)
            sorted_parents = self.topological_sort_subdag(nodes_map, edges, node_id, filter_nodes=set(upstream_node_ids))
            if sorted_parents:
                upstream_node_ids = sorted_parents

        canvas_id = canvas_path.stem
        upstream_contracts: List[UpstreamContract] = []

        with self._get_connection() as conn:
            for up_id in upstream_node_ids:
                up_node = nodes_map.get(up_id, {})
                up_text = up_node.get("text", f"Node {up_id}")
                up_title = up_text.splitlines()[0].lstrip("#").strip()

                up_session_id = self.format_session_id(canvas_id, up_id)
                row = conn.execute(
                    "SELECT crystallized_summary, artifact_refs FROM node_chat_sessions WHERE id = ?",
                    (up_session_id,),
                ).fetchone()

                if row and row["crystallized_summary"]:
                    artifacts = json.loads(row["artifact_refs"]) if row["artifact_refs"] else []
                    upstream_contracts.append(
                        UpstreamContract(
                            node_id=up_id,
                            title=up_title,
                            summary=row["crystallized_summary"],
                            artifacts=artifacts,
                        )
                    )
                else:
                    # Fallback to parsing text inside the node if not yet in SQLite
                    upstream_contracts.append(
                        UpstreamContract(
                            node_id=up_id,
                            title=up_title,
                            summary=up_text,
                            artifacts=[],
                        )
                    )

        # Parse target node details
        target_text = target_node.get("text", "")
        lines = target_text.splitlines()
        title = lines[0].lstrip("#").strip() if lines else node_id
        task = "\n".join(lines[1:]).strip() if len(lines) > 1 else target_text

        # Detect assigned agent role from node text or metadata
        agent_role = "general_agent"
        import re
        for line in lines:
            match = re.search(r"[*_]*agent[*_]*\s*:\s*[`*_]*([a-zA-Z0-9_\-]+)[`*_]*", line, re.IGNORECASE)
            if match:
                agent_role = match.group(1).strip()
                break

        if agent_role == "general_agent":
            with self._get_connection() as conn:
                session_id = self.format_session_id(canvas_id, node_id)
                s_row = conn.execute("SELECT agent_role FROM node_chat_sessions WHERE id = ?", (session_id,)).fetchone()
                if s_row and s_row["agent_role"] and s_row["agent_role"] != "general_agent":
                    agent_role = s_row["agent_role"]

        # Auto-discover L1 AccountSpec
        account_spec = self.find_account_spec()
        account_spec_dict = account_spec.model_dump() if account_spec and hasattr(account_spec, "model_dump") else None

        # Auto-discover L2 ProjectDNA
        project_dna = self.find_project_dna(canvas_path)
        project_dna_dict = project_dna.model_dump() if project_dna and hasattr(project_dna, "model_dump") else None

        # Generate zero-waste system prompt with auto-injected DNA & Account
        system_prompt = self._build_prompt_string(
            title, task, agent_role, upstream_contracts, project_dna=project_dna, account_spec=account_spec
        )

        return NodeContextPrompt(
            canvas_id=canvas_id,
            node_id=node_id,
            node_title=title,
            node_task=task,
            agent_role=agent_role,
            upstream_contracts=upstream_contracts,
            system_prompt=system_prompt,
            project_dna=project_dna_dict,
            account_spec=account_spec_dict,
        )

    @staticmethod
    def _build_prompt_string(
        title: str,
        task: str,
        role: str,
        contracts: List[UpstreamContract],
        project_dna: Optional[Any] = None,
        account_spec: Optional[Any] = None,
    ) -> str:
        prompt_parts = [
            f"# Role: Sovereign Specialist ({role})",
            f"You are operating within Canvas Node: **{title}**.",
            f"\n## 🎯 Node Mission & Task:\n{task}",
        ]

        if account_spec is not None:
            prompt_parts.extend([
                f"\n## 👑 L1 Vibe-Coder Account: {account_spec.owner_name} (`{account_spec.account_id}`)",
                f"**Tone of Voice**: {account_spec.tone_of_voice}",
                f"**System Invariants**: {'; '.join(account_spec.system_invariants[:4])}",
            ])

        if project_dna is not None:
            prompt_parts.extend([
                f"\n## 🧬 L2 Project DNA: {project_dna.project_name} (`{project_dna.project_id}`)",
                f"**Domain**: `{project_dna.domain_type}` | **ICP Target**: {project_dna.icp.segment_name}",
                f"**Value Proposition**: {project_dna.icp.value_proposition}",
                f"**Brand Voice Principles**: {', '.join(project_dna.icp.brand_voice_rules[:3])}",
                f"**Forbidden Clichés**: {', '.join(project_dna.icp.forbidden_cliches[:5])}",
                f"**Design Tokens**: Spacing={project_dna.design_system.spacing_unit_px}px, Radius={project_dna.design_system.border_radius_px}px, Colors={project_dna.design_system.primary_colors}",
                f"**Technical Constraints**: {'; '.join(project_dna.technical_constraints[:4])}",
            ])

        if contracts:
            prompt_parts.append("\n## 📥 Upstream Output Contracts (Parent Nodes):")
            for c in contracts:
                prompt_parts.append(f"### Parent [{c.node_id}] {c.title}:")
                prompt_parts.append(f"{c.summary}")
                if c.artifacts:
                    prompt_parts.append("Artifacts: " + ", ".join(f"`{a}`" for a in c.artifacts))
        else:
            prompt_parts.append("\n## 📥 Upstream Output Contracts:\n*No parent nodes — this is a root inception node.*")

        prompt_parts.append(
            "\n## 🛡️ Spatial Node Execution Invariants:\n"
            "1. Focus strictly on this node's mission. Do not attempt unrequested work outside this node.\n"
            "2. When your work is complete, produce a concise crystallized output contract for downstream nodes.\n"
            "3. Keep conversational tokens minimal; facts and code artifacts over verbal filler."
        )

        return "\n".join(prompt_parts)
