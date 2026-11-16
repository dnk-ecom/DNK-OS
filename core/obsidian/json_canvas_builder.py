# --- DNK-MRH-HEADER ---
# mrh_id: "core/obsidian/json_canvas_builder.py"
# purpose: "Official JSON Canvas 1.0 (jsoncanvas.org / Kepano) specification builder, layout engine, domain visualizers, and XYFlow bi-directional bridge for Obsidian PKM."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym / Gerych Prime"
# --- END DNK-MRH-HEADER ---

import collections
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    cast,
)

from .export_canvas import (
    DEFAULT_VAULT_ROOT,
    DEFAULT_TASK_FOREST_DIR,
    get_canonical_vault_root,
    validate_vault_path,
    _sanitize_filename,
)


class CanvasNodeType(str, Enum):
    TEXT = "text"
    FILE = "file"
    LINK = "link"
    GROUP = "group"


class CanvasColor(str, Enum):
    RED = "1"
    ORANGE = "2"
    YELLOW = "3"
    GREEN = "4"
    CYAN = "5"
    PURPLE = "6"


class CanvasSide(str, Enum):
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"


class CanvasEnd(str, Enum):
    NONE = "none"
    ARROW = "arrow"


class CanvasBackgroundStyle(str, Enum):
    COVER = "cover"
    RATIO = "ratio"
    REPEAT = "repeat"


def generate_canvas_id(seed: Optional[str] = None) -> str:
    """Generate a 16-character hexadecimal identifier compliant with JSON Canvas 1.0."""
    if seed:
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return uuid.uuid4().hex[:16]


@dataclass
class CanvasNode:
    id: str
    x: int
    y: int
    width: int
    height: int
    type: CanvasNodeType
    color: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, CanvasNodeType) else str(self.type),
            "x": int(self.x),
            "y": int(self.y),
            "width": int(self.width),
            "height": int(self.height),
        }
        if self.color is not None:
            d["color"] = self.color.value if isinstance(self.color, CanvasColor) else str(self.color)
        return d


@dataclass
class TextNode(CanvasNode):
    text: str = ""
    type: CanvasNodeType = CanvasNodeType.TEXT

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["text"] = self.text
        return d


@dataclass
class FileNode(CanvasNode):
    file: str = ""
    subpath: Optional[str] = None
    type: CanvasNodeType = CanvasNodeType.FILE

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["file"] = self.file
        if self.subpath:
            d["subpath"] = self.subpath
        return d


@dataclass
class LinkNode(CanvasNode):
    url: str = ""
    type: CanvasNodeType = CanvasNodeType.LINK

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["url"] = self.url
        return d


@dataclass
class GroupNode(CanvasNode):
    label: Optional[str] = None
    background: Optional[str] = None
    background_style: Optional[CanvasBackgroundStyle] = None
    type: CanvasNodeType = CanvasNodeType.GROUP

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        if self.label:
            d["label"] = self.label
        if self.background:
            d["background"] = self.background
        if self.background_style:
            val = (
                self.background_style.value
                if isinstance(self.background_style, CanvasBackgroundStyle)
                else str(self.background_style)
            )
            d["backgroundStyle"] = val
        return d


@dataclass
class CanvasEdge:
    id: str
    from_node: str
    to_node: str
    from_side: Optional[CanvasSide] = None
    from_end: Optional[CanvasEnd] = None
    to_side: Optional[CanvasSide] = None
    to_end: Optional[CanvasEnd] = CanvasEnd.ARROW
    label: Optional[str] = None
    color: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "fromNode": self.from_node,
            "toNode": self.to_node,
        }
        if self.from_side:
            d["fromSide"] = (
                self.from_side.value
                if isinstance(self.from_side, CanvasSide)
                else str(self.from_side)
            )
        if self.from_end:
            d["fromEnd"] = (
                self.from_end.value
                if isinstance(self.from_end, CanvasEnd)
                else str(self.from_end)
            )
        if self.to_side:
            d["toSide"] = (
                self.to_side.value
                if isinstance(self.to_side, CanvasSide)
                else str(self.to_side)
            )
        if self.to_end:
            d["toEnd"] = (
                self.to_end.value
                if isinstance(self.to_end, CanvasEnd)
                else str(self.to_end)
            )
        if self.label:
            d["label"] = self.label
        if self.color is not None:
            d["color"] = self.color.value if isinstance(self.color, CanvasColor) else str(self.color)
        return d


def _node_to_dict(node: Any) -> Dict[str, Any]:
    if hasattr(node, "to_dict") and callable(getattr(node, "to_dict")):
        res = getattr(node, "to_dict")()
        return cast(Dict[str, Any], res)
    if isinstance(node, dict):
        return cast(Dict[str, Any], dict(node))
    raise TypeError(f"Unsupported node type: {type(node)}")


def _edge_to_dict(edge: Any) -> Dict[str, Any]:
    if hasattr(edge, "to_dict") and callable(getattr(edge, "to_dict")):
        res = getattr(edge, "to_dict")()
        return cast(Dict[str, Any], res)
    if isinstance(edge, dict):
        return cast(Dict[str, Any], dict(edge))
    raise TypeError(f"Unsupported edge type: {type(edge)}")


@dataclass
class JSONCanvasDocument:
    nodes: List[Any] = field(default_factory=list)
    edges: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        raw_nodes = [_node_to_dict(n) for n in self.nodes]
        raw_edges = [_edge_to_dict(e) for e in self.edges]
        return {
            "nodes": raw_nodes,
            "edges": raw_edges,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Sizing and Geometry Utilities
# ---------------------------------------------------------------------------

def calculate_node_dimensions(
    text: str,
    base_width: int = 280,
    min_height: int = 120,
    max_height: int = 600,
) -> Tuple[int, int]:
    """Dynamically estimates optimal node width and height based on text content density."""
    if not text:
        return base_width, min_height

    lines = text.strip().split("\n")
    line_count = len(lines)
    max_line_len = max(len(l) for l in lines) if lines else 0

    width = max(base_width, min(480, max_line_len * 9 + 40))
    # Each line consumes roughly 22px vertical space + padding
    calculated_height = max(min_height, min(max_height, line_count * 24 + 60))
    return int(width), int(calculated_height)


def compute_group_bounds(
    child_nodes: List[Union[CanvasNode, Dict[str, Any]]],
    padding: int = 40,
    label: Optional[str] = None,
    color: Optional[str] = None,
    group_id: Optional[str] = None,
) -> GroupNode:
    """Calculates a tight bounding box enclosing child nodes with surrounding padding."""
    if not child_nodes:
        return GroupNode(
            id=group_id or generate_canvas_id(label or "group"),
            x=0,
            y=0,
            width=200,
            height=140,
            label=label,
            color=color,
        )

    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for node in child_nodes:
        if isinstance(node, dict):
            nx = float(node.get("x", 0))
            ny = float(node.get("y", 0))
            nw = float(node.get("width", 250))
            nh = float(node.get("height", 160))
        elif hasattr(node, "x") and hasattr(node, "y"):
            nx = float(getattr(node, "x", 0))
            ny = float(getattr(node, "y", 0))
            nw = float(getattr(node, "width", 250))
            nh = float(getattr(node, "height", 160))
        else:
            continue

        min_x = min(min_x, nx)
        min_y = min(min_y, ny)
        max_x = max(max_x, nx + nw)
        max_y = max(max_y, ny + nh)

    # Extra top space for the group header label
    top_extra = 35 if label else 0

    gx = int(min_x - padding)
    gy = int(min_y - padding - top_extra)
    gw = int(max_x - min_x + (padding * 2))
    gh = int(max_y - min_y + (padding * 2) + top_extra)

    return GroupNode(
        id=group_id or generate_canvas_id(f"group_{label}_{min_x}_{min_y}"),
        x=gx,
        y=gy,
        width=max(gw, 160),
        height=max(gh, 100),
        label=label,
        color=color,
    )


# ---------------------------------------------------------------------------
# Status and Agent Semantics Color Mapping
# ---------------------------------------------------------------------------

STATUS_COLOR_MAP: Dict[str, CanvasColor] = {
    "completed": CanvasColor.GREEN,
    "done": CanvasColor.GREEN,
    "success": CanvasColor.GREEN,
    "passed": CanvasColor.GREEN,
    "in_progress": CanvasColor.ORANGE,
    "running": CanvasColor.ORANGE,
    "review": CanvasColor.ORANGE,
    "pending": CanvasColor.YELLOW,
    "queued": CanvasColor.YELLOW,
    "todo": CanvasColor.YELLOW,
    "failed": CanvasColor.RED,
    "blocked": CanvasColor.RED,
    "error": CanvasColor.RED,
    "rejected": CanvasColor.RED,
    "meta": CanvasColor.PURPLE,
    "architecture": CanvasColor.PURPLE,
    "orchestrator": CanvasColor.CYAN,
    "active": CanvasColor.CYAN,
}

AGENT_COLOR_MAP: Dict[str, CanvasColor] = {
    "gerych_prime": CanvasColor.CYAN,
    "orchestrator": CanvasColor.CYAN,
    "gerych_builder": CanvasColor.ORANGE,
    "builder": CanvasColor.ORANGE,
    "dnk_shopify": CanvasColor.GREEN,
    "shopify": CanvasColor.GREEN,
    "gerych_auditor": CanvasColor.RED,
    "auditor": CanvasColor.RED,
    "dnk_dev_fullstack": CanvasColor.CYAN,
    "fullstack": CanvasColor.CYAN,
    "herich_librarian": CanvasColor.PURPLE,
    "librarian": CanvasColor.PURPLE,
    "dnk_video_ai_creator": CanvasColor.YELLOW,
    "video": CanvasColor.YELLOW,
    "dnk_scones_memory": CanvasColor.PURPLE,
    "memory": CanvasColor.PURPLE,
}


def status_to_color(status: str) -> str:
    """Maps operational status to canonical Obsidian Canvas color code (1-6)."""
    normalized = str(status).strip().lower()
    return STATUS_COLOR_MAP.get(normalized, CanvasColor.YELLOW).value


def agent_to_color(agent_name: str) -> str:
    """Maps swarm agent identity to distinctive visual color code."""
    normalized = str(agent_name).strip().lower()
    return AGENT_COLOR_MAP.get(normalized, CanvasColor.CYAN).value


# ---------------------------------------------------------------------------
# Auto-Layout Engine
# ---------------------------------------------------------------------------

def layout_dag(
    nodes: Sequence[Any],
    edges: Sequence[Any],
    direction: str = "LR",
    rank_spacing: int = 320,
    node_spacing: int = 180,
    start_x: int = 100,
    start_y: int = 100,
    as_document: bool = False,
) -> Any:
    """Computes deterministic DAG layout coordinates using longest-path topological ranking.

    Args:
        nodes: List of CanvasNode or dict objects.
        edges: List of CanvasEdge or dict objects.
        direction: 'LR' (Left-to-Right) or 'TB' (Top-to-Bottom).
        rank_spacing: Distance between hierarchy levels.
        node_spacing: Distance between nodes on the same rank.
        start_x: Root canvas X offset.
        start_y: Root canvas Y offset.
        as_document: If True, returns a JSONCanvasDocument instead of (nodes, edges) tuple.

    Returns:
        JSONCanvasDocument if as_document=True, else Tuple[nodes, edges].
    """
    node_dict: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        d = _node_to_dict(n)
        node_dict[d["id"]] = d

    edge_list: List[Dict[str, Any]] = []
    adj: Dict[str, List[str]] = collections.defaultdict(list)
    in_degree: Dict[str, int] = {nid: 0 for nid in node_dict}

    for e in edges:
        ed = _edge_to_dict(e)
        from_node = ed.get("fromNode") or ed.get("source")
        to_node = ed.get("toNode") or ed.get("target")
        if from_node and to_node and from_node in node_dict and to_node in node_dict:
            adj[from_node].append(to_node)
            in_degree[to_node] = in_degree.get(to_node, 0) + 1
            edge_list.append(ed)

    # Topological sorting with longest-path level calculation
    levels: Dict[str, int] = {nid: 0 for nid in node_dict}
    queue: collections.deque = collections.deque(
        [nid for nid, deg in in_degree.items() if deg == 0]
    )

    visited_count = 0
    while queue:
        curr = queue.popleft()
        visited_count += 1
        curr_lvl = levels[curr]
        for neighbor in adj[curr]:
            levels[neighbor] = max(levels[neighbor], curr_lvl + 1)
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # In case of cycles, ensure all nodes have an assigned level
    for nid in node_dict:
        if nid not in levels:
            levels[nid] = 0

    # Group nodes by rank level
    rank_groups: Dict[int, List[str]] = collections.defaultdict(list)
    for nid, lvl in levels.items():
        rank_groups[lvl].append(nid)

    # Assign positions
    positioned_nodes: List[Dict[str, Any]] = []
    is_lr = direction.upper() == "LR"

    for lvl in sorted(rank_groups.keys()):
        group_nids = rank_groups[lvl]
        total_group_span = len(group_nids) * node_spacing

        for idx, nid in enumerate(group_nids):
            node = node_dict[nid]
            w = int(node.get("width", 260))
            h = int(node.get("height", 140))

            if is_lr:
                x = start_x + (lvl * rank_spacing)
                y = start_y + (idx * node_spacing)
            else:
                x = start_x + (idx * node_spacing)
                y = start_y + (lvl * rank_spacing)

            node["x"] = x
            node["y"] = y
            node["width"] = w
            node["height"] = h
            positioned_nodes.append(node)

    # Update edge routing handles
    routed_edges: List[Dict[str, Any]] = []
    for ed in edge_list:
        if is_lr:
            ed.setdefault("fromSide", CanvasSide.RIGHT.value)
            ed.setdefault("toSide", CanvasSide.LEFT.value)
        else:
            ed.setdefault("fromSide", CanvasSide.BOTTOM.value)
            ed.setdefault("toSide", CanvasSide.TOP.value)
        ed.setdefault("toEnd", CanvasEnd.ARROW.value)
        routed_edges.append(ed)

    if as_document:
        return JSONCanvasDocument(nodes=positioned_nodes, edges=routed_edges)
    return positioned_nodes, routed_edges


def layout_pipeline(
    stages: Sequence[Dict[str, Any]],
    stage_spacing: int = 400,
    task_spacing: int = 160,
    start_x: int = 100,
    start_y: int = 100,
    wrap_in_groups: bool = True,
    create_stage_groups: Optional[bool] = None,
    as_document: bool = False,
) -> Any:
    """Arranges stages in columns left-to-right, with parallel subtasks stacked vertically."""
    if create_stage_groups is not None:
        wrap_in_groups = create_stage_groups
    all_nodes: List[Dict[str, Any]] = []
    all_edges: List[Dict[str, Any]] = []
    stage_prev_node_ids: List[str] = []

    for stage_idx, stage in enumerate(stages):
        stage_name = stage.get("name") or f"Stage {stage_idx + 1}"
        tasks = stage.get("tasks", [])
        stage_x = start_x + (stage_idx * stage_spacing)

        stage_nodes: List[Dict[str, Any]] = []
        current_node_ids: List[str] = []

        for task_idx, task in enumerate(tasks):
            t_id = task.get("id") or generate_canvas_id(f"{stage_name}_task_{task_idx}")
            t_title = task.get("title", f"Task {task_idx + 1}")
            t_status = task.get("status", "pending")
            t_agent = task.get("agent")
            t_desc = task.get("description", "")

            status_badge = f"**[{t_status.upper()}]**"
            agent_badge = f"`🤖 @{t_agent}`\n\n" if t_agent else ""
            desc_md = f"\n\n{t_desc}" if t_desc else ""
            text_body = f"### {t_title}\n{status_badge} {agent_badge}{desc_md}"

            width, height = calculate_node_dimensions(text_body, base_width=280)
            t_y = start_y + (task_idx * task_spacing)

            color = task.get("color") or status_to_color(t_status)

            node_dict = {
                "id": t_id,
                "type": CanvasNodeType.TEXT.value,
                "x": stage_x,
                "y": t_y,
                "width": width,
                "height": height,
                "text": text_body,
                "color": color,
            }
            stage_nodes.append(node_dict)
            all_nodes.append(node_dict)
            current_node_ids.append(t_id)

        # Connect previous stage to this stage with forward arrows
        if stage_prev_node_ids:
            for prev_id in stage_prev_node_ids:
                for curr_id in current_node_ids:
                    all_edges.append({
                        "id": generate_canvas_id(f"edge_{prev_id}_{curr_id}"),
                        "fromNode": prev_id,
                        "fromSide": CanvasSide.RIGHT.value,
                        "toNode": curr_id,
                        "toSide": CanvasSide.LEFT.value,
                        "toEnd": CanvasEnd.ARROW.value,
                    })

        # Wrap stage in visual group if requested
        if wrap_in_groups and stage_nodes:
            group = compute_group_bounds(
                stage_nodes,
                padding=30,
                label=f"Stage {stage_idx + 1}: {stage_name}",
                color=CanvasColor.PURPLE.value,
            )
            all_nodes.append(group.to_dict())

        stage_prev_node_ids = current_node_ids

    if as_document:
        return JSONCanvasDocument(nodes=all_nodes, edges=all_edges)
    return all_nodes, all_edges


def layout_grid(
    nodes: Sequence[Any],
    cols: int = 3,
    col_spacing: int = 320,
    row_spacing: int = 220,
    start_x: int = 100,
    start_y: int = 100,
    as_document: bool = False,
) -> Any:
    """Arranges nodes in a tidy grid matrix."""
    positioned: List[Dict[str, Any]] = []
    for idx, node in enumerate(nodes):
        d = _node_to_dict(node)
        col = idx % cols
        row = idx // cols
        d["x"] = start_x + (col * col_spacing)
        d["y"] = start_y + (row * row_spacing)
        positioned.append(d)
    if as_document:
        return JSONCanvasDocument(nodes=positioned, edges=[])
    return positioned


# ---------------------------------------------------------------------------
# High-Level Domain Builders
# ---------------------------------------------------------------------------

def build_swarm_task_dag_canvas(
    tasks: List[Dict[str, Any]],
    dependencies: Optional[List[Tuple[str, str]]] = None,
    title: str = "DNK Swarm Task Execution DAG",
    group_by: Optional[str] = "stage",
) -> JSONCanvasDocument:
    """Constructs a production-grade Obsidian Canvas visual graph for Swarm TaskDNA DAGs.

    Args:
        tasks: List of task specifications (id, title, status, agent, stage, description).
        dependencies: Optional list of (from_id, to_id) edge pairs.
        title: Main diagram header.
        group_by: Optional attribute name to partition into visual swimlanes/groups ('stage', 'domain', 'agent').

    Returns:
        Fully configured, validated JSONCanvasDocument.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Title node
    title_id = generate_canvas_id("title_node")
    nodes.append({
        "id": title_id,
        "type": CanvasNodeType.TEXT.value,
        "x": 60,
        "y": 40,
        "width": 360,
        "height": 90,
        "text": f"# 👑 {title}\n*Generated by Gerych Prime Swarm Orchestrator*",
        "color": CanvasColor.CYAN.value,
    })

    task_nodes_map: Dict[str, Dict[str, Any]] = {}
    for t in tasks:
        tid = t.get("id") or generate_canvas_id(t.get("title", "task"))
        status = t.get("status", "pending")
        agent = t.get("agent", "gerych_prime")
        task_title = t.get("title", f"Task {tid}")
        desc = t.get("description", "")

        status_emoji = {
            "completed": "✅",
            "done": "✅",
            "in_progress": "⚡",
            "running": "⚡",
            "failed": "❌",
            "blocked": "⛔",
            "pending": "⏳",
        }.get(status.lower(), "📌")

        body_lines = [
            f"### {status_emoji} {task_title}",
            f"**Status**: `{status.upper()}` | **Agent**: `@{agent}`",
        ]
        if desc:
            body_lines.append(f"\n> {desc}")
        if t.get("target_files"):
            files_str = ", ".join(f"`{f}`" for f in t["target_files"][:3])
            body_lines.append(f"\n📂 **Files**: {files_str}")

        text = "\n".join(body_lines)
        w, h = calculate_node_dimensions(text, base_width=290)

        nd = {
            "id": tid,
            "type": CanvasNodeType.TEXT.value,
            "x": 0,
            "y": 0,
            "width": w,
            "height": h,
            "text": text,
            "color": status_to_color(status),
            "_stage": t.get("stage", "main"),
            "_domain": t.get("domain", "core"),
            "_agent": agent,
        }
        nodes.append(nd)
        task_nodes_map[tid] = nd

    # Explicit edge construction
    if dependencies:
        for from_id, to_id in dependencies:
            if from_id in task_nodes_map and to_id in task_nodes_map:
                edges.append({
                    "id": generate_canvas_id(f"dag_edge_{from_id}_{to_id}"),
                    "fromNode": from_id,
                    "toNode": to_id,
                    "toEnd": CanvasEnd.ARROW.value,
                })

    # Task-level declared dependencies
    for t in tasks:
        tid = str(t.get("id") or generate_canvas_id(t.get("title", "task")))
        for dep_id in t.get("dependencies", []):
            if dep_id in task_nodes_map and tid in task_nodes_map:
                edge_id = generate_canvas_id(f"dag_edge_{dep_id}_{tid}")
                if not any(e.get("id") == edge_id for e in edges):
                    edges.append({
                        "id": edge_id,
                        "fromNode": dep_id,
                        "toNode": tid,
                        "toEnd": CanvasEnd.ARROW.value,
                    })

    # Run DAG layout on task nodes
    task_nodes = [n for n in nodes if n["id"] != title_id]
    pos_task_nodes, routed_edges = layout_dag(
        nodes=task_nodes,
        edges=edges,
        direction="LR",
        rank_spacing=340,
        node_spacing=180,
        start_x=100,
        start_y=160,
    )

    final_nodes: List[Dict[str, Any]] = [nodes[0]] + pos_task_nodes

    # Grouping by attribute (e.g. stage or agent)
    if group_by:
        groups_dict: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        for tn in pos_task_nodes:
            key = str(tn.get(f"_{group_by}", "default"))
            groups_dict[key].append(tn)

        for g_key, g_nodes in groups_dict.items():
            if len(g_nodes) > 1:
                grp = compute_group_bounds(
                    g_nodes,
                    padding=35,
                    label=f"{group_by.capitalize()}: {g_key}",
                    color=CanvasColor.PURPLE.value,
                )
                final_nodes.append(grp.to_dict())

    # Clean internal underscore keys
    for n in final_nodes:
        for k in list(n.keys()):
            if k.startswith("_"):
                del n[k]

    return JSONCanvasDocument(nodes=final_nodes, edges=routed_edges)


def build_architecture_canvas(
    architecture_map: Dict[str, Any],
    title: str = "DNK OS System Architecture Map",
) -> JSONCanvasDocument:
    """Builds a multi-tier spatial architecture diagram with categorized subsystem groups."""
    all_nodes: List[Dict[str, Any]] = []
    all_edges: List[Dict[str, Any]] = []

    # Title Banner
    title_id = generate_canvas_id("arch_title")
    all_nodes.append({
        "id": title_id,
        "type": CanvasNodeType.TEXT.value,
        "x": 60,
        "y": 40,
        "width": 420,
        "height": 90,
        "text": f"# 🏗️ {title}\n*SSOT Architectural Boundaries & Dataflow*",
        "color": CanvasColor.PURPLE.value,
    })

    # Tier columns or sections: Apps, Core Engines, Services, Infrastructure
    categories = [
        ("Apps & Presentation", architecture_map.get("apps", {}), 80, CanvasColor.CYAN),
        ("Core Engines & Orchestrator", architecture_map.get("core", {}), 460, CanvasColor.PURPLE),
        ("Microservices & Workers", architecture_map.get("services", {}), 840, CanvasColor.GREEN),
        ("Storage & Infrastructure", architecture_map.get("infra", {}), 1220, CanvasColor.ORANGE),
    ]

    for cat_name, cat_items, cat_x, cat_color in categories:
        if not cat_items:
            continue

        cat_nodes: List[Dict[str, Any]] = []
        start_y = 180

        items_iter = (
            cat_items.items() if isinstance(cat_items, dict) else enumerate(cat_items)
        )
        for idx, item in enumerate(items_iter):
            if isinstance(cat_items, dict):
                comp_key, comp_val = item
                name = str(comp_key)
                desc = (
                    comp_val.get("description", "")
                    if isinstance(comp_val, dict)
                    else str(comp_val)
                )
            else:
                _, comp_val = item
                name = str(comp_val)
                desc = ""

            cid = generate_canvas_id(f"arch_{cat_name}_{name}")
            text_body = f"### 📦 {name}\n\n{desc}" if desc else f"### 📦 {name}"
            w, h = calculate_node_dimensions(text_body, base_width=260)
            y = start_y + (idx * 160)

            node_dict = {
                "id": cid,
                "type": CanvasNodeType.TEXT.value,
                "x": cat_x,
                "y": y,
                "width": w,
                "height": h,
                "text": text_body,
                "color": cat_color.value,
            }
            cat_nodes.append(node_dict)
            all_nodes.append(node_dict)

        if cat_nodes:
            grp = compute_group_bounds(
                cat_nodes,
                padding=30,
                label=cat_name,
                color=cat_color.value,
            )
            all_nodes.append(grp.to_dict())

    # Process explicit inter-subsystem connections
    connections = architecture_map.get("connections", [])
    for conn in connections:
        from_name = conn.get("from")
        to_name = conn.get("to")
        label = conn.get("label", "")
        # Find matching node IDs
        from_id = next(
            (n["id"] for n in all_nodes if n.get("type") == "text" and from_name in n.get("text", "")),
            None,
        )
        to_id = next(
            (n["id"] for n in all_nodes if n.get("type") == "text" and to_name in n.get("text", "")),
            None,
        )
        if from_id and to_id:
            all_edges.append({
                "id": generate_canvas_id(f"arch_edge_{from_id}_{to_id}"),
                "fromNode": from_id,
                "fromSide": CanvasSide.RIGHT.value,
                "toNode": to_id,
                "toSide": CanvasSide.LEFT.value,
                "toEnd": CanvasEnd.ARROW.value,
                "label": label,
            })

    return JSONCanvasDocument(nodes=all_nodes, edges=all_edges)


def build_pkm_mindmap_canvas(
    root_title: str,
    branches: Dict[str, Any],
    root_file: Optional[str] = None,
    color_map: Optional[Dict[str, Union[str, CanvasColor]]] = None,
    center_x: int = 0,
    center_y: int = 0,
) -> JSONCanvasDocument:
    """Creates a radiating or hierarchical Visual PKM mindmap canvas document.

    Args:
        root_title: Main topic / hub label.
        branches: Mapping of branch titles to sub-items, lists of notes, or sub-dictionaries.
        root_file: Optional vault file path for the root node.
        color_map: Optional branch color overrides.
        center_x: Canvas X offset.
        center_y: Canvas Y offset.

    Returns:
        JSONCanvasDocument ready for Obsidian Canvas.
    """
    all_nodes: List[Dict[str, Any]] = []
    all_edges: List[Dict[str, Any]] = []

    root_id = generate_canvas_id(f"pkm_root_{root_title}")
    root_color = CanvasColor.PURPLE.value

    if root_file:
        all_nodes.append(
            FileNode(
                id=root_id,
                file=root_file,
                x=center_x,
                y=center_y,
                width=320,
                height=160,
                color=root_color,
            ).to_dict()
        )
    else:
        all_nodes.append(
            TextNode(
                id=root_id,
                text=f"# 🧠 {root_title}\n\n*PKM Knowledge Hub*",
                x=center_x,
                y=center_y,
                width=300,
                height=140,
                color=root_color,
            ).to_dict()
        )

    branch_keys = list(branches.keys())
    num_branches = len(branch_keys)
    if num_branches == 0:
        return JSONCanvasDocument(nodes=all_nodes, edges=all_edges)

    # Distribute branches: left vs right or vertical tiers
    # For a balanced 2-column or radiating layout:
    # Right branches (first half), Left branches (second half)
    half = (num_branches + 1) // 2
    right_branches = branch_keys[:half]
    left_branches = branch_keys[half:]

    branch_palette = [
        CanvasColor.CYAN.value,
        CanvasColor.GREEN.value,
        CanvasColor.YELLOW.value,
        CanvasColor.ORANGE.value,
        CanvasColor.PURPLE.value,
        CanvasColor.RED.value,
    ]

    def _render_side(side_keys: List[str], is_right: bool):
        base_x = center_x + 420 if is_right else center_x - 420
        total_items = len(side_keys)
        start_y = center_y - ((total_items - 1) * 200 // 2)

        for b_idx, b_name in enumerate(side_keys):
            b_val = branches[b_name]
            b_id = generate_canvas_id(f"pkm_b_{b_name}")
            b_color = (
                str(color_map.get(b_name, branch_palette[b_idx % len(branch_palette)]))
                if color_map
                else branch_palette[b_idx % len(branch_palette)]
            )
            b_y = start_y + (b_idx * 220)
            node_x = base_x if is_right else (base_x - 260)

            # Check if branch value has sub items
            items_text = ""
            sub_list: List[str] = []
            if isinstance(b_val, list):
                sub_list = [str(item) for item in b_val]
            elif isinstance(b_val, dict):
                sub_list = [f"**{k}**: {v}" for k, v in b_val.items()]
            elif isinstance(b_val, str) and b_val:
                items_text = f"\n\n{b_val}"

            if sub_list:
                items_text = "\n\n" + "\n".join(f"- [[{item}]]" if not item.startswith("**") else f"- {item}" for item in sub_list)

            w, h = calculate_node_dimensions(f"### {b_name}{items_text}", base_width=280, min_height=120)

            all_nodes.append(
                TextNode(
                    id=b_id,
                    text=f"### 📌 {b_name}{items_text}",
                    x=node_x,
                    y=b_y,
                    width=w,
                    height=h,
                    color=b_color,
                ).to_dict()
            )

            # Edge from root to branch
            if is_right:
                all_edges.append(
                    CanvasEdge(
                        id=generate_canvas_id(f"pkm_edge_{root_id}_{b_id}"),
                        from_node=root_id,
                        from_side=CanvasSide.RIGHT,
                        to_node=b_id,
                        to_side=CanvasSide.LEFT,
                        to_end=CanvasEnd.ARROW,
                        color=b_color,
                    ).to_dict()
                )
            else:
                all_edges.append(
                    CanvasEdge(
                        id=generate_canvas_id(f"pkm_edge_{root_id}_{b_id}"),
                        from_node=root_id,
                        from_side=CanvasSide.LEFT,
                        to_node=b_id,
                        to_side=CanvasSide.RIGHT,
                        to_end=CanvasEnd.ARROW,
                        color=b_color,
                    ).to_dict()
                )

    _render_side(right_branches, is_right=True)
    _render_side(left_branches, is_right=False)

    return JSONCanvasDocument(nodes=all_nodes, edges=all_edges)


# ---------------------------------------------------------------------------
# Bidirectional XYFlow (React Flow) ⇄ JSON Canvas 1.0 Bridge
# ---------------------------------------------------------------------------

def xyflow_to_json_canvas(xyflow_doc: Dict[str, Any]) -> JSONCanvasDocument:
    """Converts a React Flow / XYFlow graph representation into JSON Canvas 1.0 format."""
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    raw_nodes = xyflow_doc.get("nodes", [])
    for rn in raw_nodes:
        nid = str(rn.get("id") or generate_canvas_id())
        pos = rn.get("position", {})
        x = int(float(rn.get("x", pos.get("x", 0))))
        y = int(float(rn.get("y", pos.get("y", 0))))
        width = int(float(rn.get("width", 260)))
        height = int(float(rn.get("height", 140)))

        data = rn.get("data", {})
        node_type_raw = str(rn.get("type", "default")).lower()

        # Handle groups
        if node_type_raw == "group":
            label = data.get("label") or rn.get("label") or "Group"
            nodes.append({
                "id": nid,
                "type": CanvasNodeType.GROUP.value,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "label": label,
                "color": rn.get("color") or data.get("color"),
            })
            continue

        # Content resolution
        text = str(
            data.get("content")
            or data.get("text")
            or data.get("label")
            or rn.get("label")
            or ""
        )
        title = data.get("title")
        if title and text and not text.startswith(f"# {title}"):
            full_text = f"### {title}\n\n{text}"
        else:
            full_text = text or title or f"Node {nid}"

        color = rn.get("color") or data.get("color")

        # Check for file or link types
        if "file" in data or rn.get("type") == "file":
            nodes.append({
                "id": nid,
                "type": CanvasNodeType.FILE.value,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "file": data.get("file") or rn.get("file", ""),
                "subpath": data.get("subpath"),
                "color": color,
            })
        elif "url" in data or rn.get("type") == "link":
            nodes.append({
                "id": nid,
                "type": CanvasNodeType.LINK.value,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "url": data.get("url") or rn.get("url", ""),
                "color": color,
            })
        else:
            nodes.append({
                "id": nid,
                "type": CanvasNodeType.TEXT.value,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "text": full_text,
                "color": color,
            })

    # Clean None values in nodes
    for n in nodes:
        for k in list(n.keys()):
            if n[k] is None:
                del n[k]

    raw_edges = xyflow_doc.get("edges", [])
    for idx, re_edge in enumerate(raw_edges):
        eid = str(re_edge.get("id") or f"edge_{idx}")
        from_node = str(re_edge.get("source") or re_edge.get("fromNode") or "")
        to_node = str(re_edge.get("target") or re_edge.get("toNode") or "")

        c_edge: Dict[str, Any] = {
            "id": eid,
            "fromNode": from_node,
            "toNode": to_node,
        }

        # Port mapping
        source_handle = re_edge.get("sourceHandle") or re_edge.get("fromSide")
        if source_handle in ("top", "right", "bottom", "left"):
            c_edge["fromSide"] = source_handle

        target_handle = re_edge.get("targetHandle") or re_edge.get("toSide")
        if target_handle in ("top", "right", "bottom", "left"):
            c_edge["toSide"] = target_handle

        if re_edge.get("label"):
            c_edge["label"] = str(re_edge["label"])
        if re_edge.get("color"):
            c_edge["color"] = str(re_edge["color"])

        marker_end = re_edge.get("markerEnd") or re_edge.get("toEnd")
        if marker_end:
            c_edge["toEnd"] = CanvasEnd.ARROW.value

        edges.append(c_edge)

    return JSONCanvasDocument(nodes=nodes, edges=edges)


def json_canvas_to_xyflow(canvas_doc: Union[JSONCanvasDocument, Dict[str, Any]]) -> Dict[str, Any]:
    """Converts a JSON Canvas 1.0 document into React Flow / XYFlow compatible format."""
    if isinstance(canvas_doc, JSONCanvasDocument):
        cdict = canvas_doc.to_dict()
    elif isinstance(canvas_doc, dict):
        cdict = canvas_doc
    else:
        raise TypeError(f"Expected JSONCanvasDocument or dict, got {type(canvas_doc)}")
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    for n in cdict.get("nodes", []):
        nid = str(n.get("id", ""))
        ntype = str(n.get("type", "text"))
        x = float(n.get("x", 0))
        y = float(n.get("y", 0))
        width = float(n.get("width", 260))
        height = float(n.get("height", 140))
        color = n.get("color")

        if ntype == "group":
            nodes.append({
                "id": nid,
                "type": "group",
                "position": {"x": x, "y": y},
                "width": width,
                "height": height,
                "data": {"label": n.get("label", "Group")},
                "style": {"backgroundColor": "rgba(240, 240, 240, 0.2)"},
            })
        elif ntype == "file":
            nodes.append({
                "id": nid,
                "type": "fileNode",
                "position": {"x": x, "y": y},
                "width": width,
                "height": height,
                "data": {
                    "file": n.get("file", ""),
                    "subpath": n.get("subpath"),
                    "label": Path(n.get("file", "")).name,
                },
            })
        elif ntype == "link":
            nodes.append({
                "id": nid,
                "type": "linkNode",
                "position": {"x": x, "y": y},
                "width": width,
                "height": height,
                "data": {
                    "url": n.get("url", ""),
                    "label": n.get("url", ""),
                },
            })
        else:
            text = n.get("text", "")
            title = text.split("\n")[0].lstrip("#").strip() if text else "Card"
            nodes.append({
                "id": nid,
                "type": "default",
                "position": {"x": x, "y": y},
                "width": width,
                "height": height,
                "data": {
                    "text": text,
                    "title": title,
                    "label": title,
                },
            })

    for e in cdict.get("edges", []):
        edges.append({
            "id": str(e.get("id", "")),
            "source": str(e.get("fromNode", "")),
            "target": str(e.get("toNode", "")),
            "sourceHandle": e.get("fromSide"),
            "targetHandle": e.get("toSide"),
            "label": e.get("label"),
            "markerEnd": {"type": "arrowclosed"} if e.get("toEnd") == "arrow" else None,
        })

    return {"nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Strict Validation Engine
# ---------------------------------------------------------------------------

VALID_COLORS = {"1", "2", "3", "4", "5", "6"}
VALID_SIDES = {"top", "right", "bottom", "left"}
VALID_ENDS = {"none", "arrow"}


def validate_json_canvas(canvas_doc: Union[JSONCanvasDocument, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validates a canvas document strictly against the jsoncanvas.org v1.0 specification.

    Returns:
        Tuple of (is_valid: bool, errors: List[str]).
    """
    errors: List[str] = []
    if isinstance(canvas_doc, JSONCanvasDocument):
        data = canvas_doc.to_dict()
    elif isinstance(canvas_doc, dict):
        data = canvas_doc
    else:
        return False, [f"Expected JSONCanvasDocument or dict, got {type(canvas_doc)}"]

    if not isinstance(data, dict):
        return False, ["Canvas root must be a JSON object dictionary."]

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        errors.append("Canvas root must contain a 'nodes' array.")
        nodes = []

    edges = data.get("edges")
    if not isinstance(edges, list):
        errors.append("Canvas root must contain an 'edges' array.")
        edges = []

    node_ids: Set[str] = set()
    for idx, n in enumerate(nodes):
        if not isinstance(n, dict):
            errors.append(f"Node at index {idx} is not a valid dictionary object.")
            continue

        nid = n.get("id")
        if not nid or not isinstance(nid, str):
            errors.append(f"Node at index {idx} has missing or non-string 'id'.")
        elif nid in node_ids:
            errors.append(f"Duplicate node ID '{nid}' detected at index {idx}.")
        else:
            node_ids.add(nid)

        ntype = n.get("type")
        if ntype not in [t.value for t in CanvasNodeType]:
            errors.append(f"Node '{nid}' has invalid type '{ntype}'. Allowed: {[t.value for t in CanvasNodeType]}")

        for coord in ("x", "y", "width", "height"):
            val = n.get(coord)
            if val is None or not isinstance(val, (int, float)):
                errors.append(f"Node '{nid}' has invalid or missing coordinate '{coord}': {val}")

        # Type-specific invariants
        if ntype == CanvasNodeType.TEXT.value and "text" not in n:
            errors.append(f"Text node '{nid}' missing required 'text' string attribute.")
        elif ntype == CanvasNodeType.FILE.value and "file" not in n:
            errors.append(f"File node '{nid}' missing required 'file' path attribute.")
        elif ntype == CanvasNodeType.LINK.value and "url" not in n:
            errors.append(f"Link node '{nid}' missing required 'url' attribute.")

        # Color invariant
        color = n.get("color")
        if color:
            c_str = str(color).strip()
            if c_str not in VALID_COLORS and not (c_str.startswith("#") and len(c_str) in (4, 7)):
                errors.append(f"Node '{nid}' has non-standard color '{color}'. Must be 1-6 or hex #RRGGBB.")

    # Edge validation
    edge_ids: Set[str] = set()
    for idx, e in enumerate(edges):
        if not isinstance(e, dict):
            errors.append(f"Edge at index {idx} is not a valid dictionary object.")
            continue

        eid = e.get("id")
        if not eid or not isinstance(eid, str):
            errors.append(f"Edge at index {idx} has missing or non-string 'id'.")
        elif eid in edge_ids:
            errors.append(f"Duplicate edge ID '{eid}' detected at index {idx}.")
        else:
            edge_ids.add(eid)

        from_node = e.get("fromNode")
        to_node = e.get("toNode")

        if not from_node or from_node not in node_ids:
            errors.append(f"Edge '{eid}' references non-existent or invalid fromNode '{from_node}'.")
        if not to_node or to_node not in node_ids:
            errors.append(f"Edge '{eid}' references non-existent or invalid toNode '{to_node}'.")

        from_side = e.get("fromSide")
        if from_side and from_side not in VALID_SIDES:
            errors.append(f"Edge '{eid}' has invalid fromSide '{from_side}'.")

        to_side = e.get("toSide")
        if to_side and to_side not in VALID_SIDES:
            errors.append(f"Edge '{eid}' has invalid toSide '{to_side}'.")

        from_end = e.get("fromEnd")
        if from_end and from_end not in VALID_ENDS:
            errors.append(f"Edge '{eid}' has invalid fromEnd '{from_end}'.")

        to_end = e.get("toEnd")
        if to_end and to_end not in VALID_ENDS:
            errors.append(f"Edge '{eid}' has invalid toEnd '{to_end}'.")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Vault Exporter
# ---------------------------------------------------------------------------

def export_canvas_to_vault(
    canvas_doc: Union[JSONCanvasDocument, Dict[str, Any]],
    relative_path: Union[str, Path] = "Canvas/swarm_tasks.canvas",
    vault_root: Optional[Union[str, Path]] = None,
    enforce_vault_root: bool = True,
    validate_schema: bool = True,
) -> Path:
    """Exports a validated JSON Canvas document into the Obsidian Vault.

    Args:
        canvas_doc: JSONCanvasDocument or dict.
        relative_path: Path relative to vault root (e.g. 'Canvas/architecture.canvas').
        vault_root: Vault root override.
        enforce_vault_root: Strict validation against canonical vault root.
        validate_schema: If True, validates against jsoncanvas.org before writing.

    Returns:
        Resolved destination Path.
    """
    if validate_schema:
        is_valid, errs = validate_json_canvas(canvas_doc)
        if not is_valid:
            raise ValueError(f"Cannot export invalid JSON Canvas: {'; '.join(errs)}")

    canonical_root = (
        Path(os.path.expanduser(str(vault_root))).resolve()
        if vault_root is not None
        else get_canonical_vault_root()
    )

    str_path = str(relative_path).strip()
    if str_path.startswith("vault:"):
        str_path = str_path[6:].lstrip("/\\")

    dest_path = (canonical_root / str_path).resolve()
    resolved_root = canonical_root.resolve()

    if enforce_vault_root:
        try:
            dest_path.relative_to(resolved_root)
        except ValueError:
            raise ValueError(f"Path traversal detected: {relative_path} escapes vault root {canonical_root}")
        dest_path = validate_vault_path(dest_path, vault_root=canonical_root)

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    json_str = (
        canvas_doc.to_json(indent=2)
        if hasattr(canvas_doc, "to_json")
        else json.dumps(canvas_doc, indent=2, ensure_ascii=False)
    )
    dest_path.write_text(json_str, encoding="utf-8")
    return dest_path
