# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/dag_models.py"
# purpose: "CONTRACT-002 Pydantic v2 schemas and context compiler for ThoughtDAG & Context Wire Protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-06"
# author: "DNK Swarm (dnk_dev_fullstack)"
# --- END DNK-MRH-HEADER ---

"""
ThoughtDAG & Context Wire Protocol Models (CONTRACT-002).
Provides Pydantic v2 schemas for DAG nodes, context wires, upstream fingerprinting,
and context compilation for autonomous swarm agents.
"""

from collections import deque
from enum import Enum
import hashlib
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class NodeKind(str, Enum):
    PROJECT = "project"         # Brand, store, or organizational context
    TASK = "task"               # Forest node / subtask
    ENTITY = "entity"           # Physical / digital entity (product, file, CAD, photo)
    AGENT = "agent"             # Swarm agent executor (Shopify dev, Video AI, etc.)
    SKILL = "skill"             # Skill or instruction (from skills/ catalog)
    SAAP_TOOL = "saap_tool"     # External tool (ComfyUI, FFmpeg, Shopify API)
    ARTIFACT = "artifact"       # Deliverable result (video, product listing, image)
    NOTE = "note"               # Spatial thought/canvas note node
    IDEA = "idea"               # v2: raw idea not yet shaped into a task
    GATE = "gate"               # v2: HITL / quality gate (approval point)


class Scale(str, Enum):
    """Task Forest vocabulary (canonical): field > sector > tree > bush > flower.
    Legacy aliases (epic/task/slice) are accepted only via SCALE_ALIASES for import."""
    FIELD = "field"
    SECTOR = "sector"
    TREE = "tree"
    BUSH = "bush"
    FLOWER = "flower"


SCALE_ALIASES: Dict[str, "Scale"] = {
    "epic": Scale.TREE,
    "task": Scale.BUSH,
    "slice": Scale.FLOWER,
}


class NodeStatus(str, Enum):
    DRAFT = "draft"
    BACKLOG = "backlog"
    BLOCKED = "blocked"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Legacy values (ThoughtNode v1 'status', Task Forest 'stage', NodeTaskGraph) -> NodeStatus.
STATUS_ALIASES: Dict[str, "NodeStatus"] = {
    "active": NodeStatus.READY,
    "pending": NodeStatus.BACKLOG,
    "planned": NodeStatus.READY,
    "todo": NodeStatus.BACKLOG,
    "running": NodeStatus.IN_PROGRESS,
    "completed": NodeStatus.DONE,
    "error": NodeStatus.FAILED,
    "verifying": NodeStatus.REVIEW,
    "verification": NodeStatus.REVIEW,
    "ideation": NodeStatus.DRAFT,
    "architecture": NodeStatus.DRAFT,
}


def normalize_status(value: Any) -> NodeStatus:
    """Maps any legacy status/stage string onto NodeStatus. Unknown -> DRAFT."""
    raw = str(getattr(value, "value", value) or "").strip().lower()
    try:
        return NodeStatus(raw)
    except ValueError:
        return STATUS_ALIASES.get(raw, NodeStatus.DRAFT)


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskSpec(BaseModel):
    goal: str = ""
    acceptance_criteria: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    estimate_minutes: Optional[int] = None


class RunState(BaseModel):
    run_id: Optional[str] = None
    agent: Optional[str] = None
    state: str = Field("idle", description="idle | running | completed | failed")
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0


class WireType(str, Enum):
    CONTEXT = "context"
    DATA_STREAM = "data_stream"
    DEPENDENCY = "dependency"


class HighlightMode(str, Enum):
    ALL = "all"
    SELECTIVE = "selective"


class Wire(BaseModel):
    id: str = Field(..., description="Unique wire ID")
    from_node: str = Field(..., description="Source node ID")
    to_node: str = Field(..., description="Target node ID")
    wire_type: WireType = Field(WireType.CONTEXT, description="Wire semantics")
    label: Optional[str] = Field(None, description="Optional wire label or descriptor")
    token_budget: Optional[int] = Field(None, description="Max token limit passed along this wire")
    derived: bool = Field(False, description="v2: wire is computed (e.g. from parent_id), not user-drawn")
    validates: bool = Field(False, description="v2: source node validates/reviews the target")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ThoughtNode(BaseModel):
    id: str = Field(..., description="Unique node ID")
    kind: NodeKind = Field(NodeKind.NOTE, description="Node category")
    title: str = Field(..., description="Human-readable title or label")
    content: str = Field("", description="Markdown payload, note body, prompt, or structured data")
    project_id: Optional[str] = Field(None, description="Associated project or workspace ID")
    status: str = Field("active", description="'pending' | 'active' | 'in_progress' | 'done' | 'failed'")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    assigned_agent: Optional[str] = Field(None, description="Designated swarm agent if applicable")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    highlight_mode: HighlightMode = Field(HighlightMode.ALL, description="Context extraction mode")
    selected_snippet: Optional[str] = Field(None, description="Explicit highlight snippet if in selective mode")
    upstream_fingerprint: Optional[str] = Field(None, description="SHA256 fingerprint of upstream ancestors")
    is_stale: bool = Field(False, description="Flag indicating if upstream context mutated")
    # --- v2 additive fields (Task Forest / Task DAG unification) ---
    scale: Optional[Scale] = Field(None, description="Task Forest level: field/sector/tree/bush/flower")
    parent_id: Optional[str] = Field(None, description="Hierarchy parent (containment), distinct from wires")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="0..1 completion")
    weight: float = Field(1.0, ge=0.0, description="Weight for rolling progress up to the parent")
    priority: PriorityLevel = Field(PriorityLevel.MEDIUM)
    spec: Optional[TaskSpec] = None
    run: Optional[RunState] = None
    position: Optional[Dict[str, float]] = Field(None, description="Canvas position {x, y}")
    size: Optional[Dict[str, float]] = Field(None, description="Canvas size {width, height}")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ThoughtDAGGraph(BaseModel):
    graph_id: str = Field(..., description="Unique graph identifier")
    project_id: str = Field("default", description="Associated project identifier")
    root_nodes: List[str] = Field(default_factory=list, description="Explicit entry root node IDs")
    nodes: Dict[str, ThoughtNode] = Field(default_factory=dict, description="Dictionary of nodes by node ID")
    wires: List[Wire] = Field(default_factory=list, description="List of directional context wires")


class CompiledContextNode(BaseModel):
    node_id: str
    title: str
    kind: NodeKind
    text: str
    snippet_only: bool = False


class ContextCompileRequest(BaseModel):
    graph: ThoughtDAGGraph
    target_node_id: str
    max_tokens: Optional[int] = Field(None, description="Optional upper bound on compiled tokens")
    include_kinds: Optional[List[NodeKind]] = Field(None, description="Filter ancestor nodes by kind")


class ContextCompileResponse(BaseModel):
    target_node_id: str
    context_text: str
    upstream_fingerprint: str
    included_nodes: List[CompiledContextNode]
    is_stale: bool = False
    estimated_tokens: int = 0


class StalenessCheckRequest(BaseModel):
    graph: ThoughtDAGGraph
    target_node_id: str
    current_fingerprint: Optional[str] = None


class StalenessCheckResponse(BaseModel):
    target_node_id: str
    is_stale: bool
    computed_fingerprint: str
    current_fingerprint: Optional[str] = None


# --- v2: cycle detection (the single cycle check for the canon graph) ---

_ACYCLIC_WIRE_TYPES = (WireType.CONTEXT, WireType.DEPENDENCY)


def cycle_edges(wires) -> List[Tuple[str, str]]:
    """(from, to) pairs that count for cycle detection: CONTEXT/DEPENDENCY wires, never `validates`
    (a gate may point back at the task it verifies) and never DATA_STREAM/derived loops.
    Single definition used by `find_cycle` and by `NodeCanvasCore`."""
    return [
        (w.from_node, w.to_node)
        for w in wires
        if not w.validates and w.wire_type in _ACYCLIC_WIRE_TYPES
    ]


def find_cycle(graph: ThoughtDAGGraph) -> Optional[List[str]]:
    """Returns one cycle as a node-id path (first == last) over CONTEXT/DEPENDENCY wires
    and parent_id containment, or None if the graph is acyclic."""
    adj: Dict[str, List[str]] = {nid: [] for nid in graph.nodes}
    for w in graph.wires:
        if w.validates:
            continue  # validation gates may point back at the task they verify
        if w.wire_type in _ACYCLIC_WIRE_TYPES and w.from_node in adj and w.to_node in adj:
            adj[w.from_node].append(w.to_node)
    for nid, node in graph.nodes.items():
        if node.parent_id and node.parent_id in adj:
            adj[node.parent_id].append(nid)

    WHITE, GREY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in adj}
    for start in adj:
        if color[start] != WHITE:
            continue
        stack = [(start, iter(adj[start]))]
        path = [start]
        color[start] = GREY
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = BLACK
                stack.pop()
                path.pop()
            elif color[nxt] == GREY:
                return path[path.index(nxt):] + [nxt]
            elif color[nxt] == WHITE:
                color[nxt] = GREY
                path.append(nxt)
                stack.append((nxt, iter(adj[nxt])))
    return None


def validate_acyclic(graph: ThoughtDAGGraph) -> None:
    cycle = find_cycle(graph)
    if cycle:
        raise ValueError("Cycle detected: " + " -> ".join(cycle))


# --- Context Compilation & Fingerprinting Core Algorithms ---

def compute_upstream_ancestors(graph: ThoughtDAGGraph, target_node_id: str) -> List[ThoughtNode]:
    """
    Traverse incoming context wires in reverse to collect all unique upstream ancestor nodes
    in topological/top-down order (roots first, nearest ancestors last).
    """
    if target_node_id not in graph.nodes:
        return []

    # Build incoming adjacency list for CONTEXT wires
    incoming: Dict[str, List[str]] = {node_id: [] for node_id in graph.nodes}
    for wire in graph.wires:
        if wire.wire_type == WireType.CONTEXT:
            if wire.to_node in incoming and wire.from_node in graph.nodes:
                incoming[wire.to_node].append(wire.from_node)

    # Collect all reachable ancestors using BFS/queue
    ancestor_ids: Set[str] = set()
    queue = deque(incoming.get(target_node_id, []))
    
    while queue:
        curr = queue.popleft()
        if curr not in ancestor_ids:
            ancestor_ids.add(curr)
            for parent in incoming.get(curr, []):
                if parent not in ancestor_ids:
                    queue.append(parent)

    if not ancestor_ids:
        return []

    # Compute topological sort of the ancestor subgraph
    in_degree = {nid: 0 for nid in ancestor_ids}
    for wire in graph.wires:
        if wire.wire_type == WireType.CONTEXT and wire.from_node in ancestor_ids and wire.to_node in ancestor_ids:
            in_degree[wire.to_node] += 1

    zero_in = deque([nid for nid in ancestor_ids if in_degree[nid] == 0])
    ordered_ids: List[str] = []

    while zero_in:
        nid = zero_in.popleft()
        ordered_ids.append(nid)
        for wire in graph.wires:
            if wire.wire_type == WireType.CONTEXT and wire.from_node == nid and wire.to_node in ancestor_ids:
                in_degree[wire.to_node] -= 1
                if in_degree[wire.to_node] == 0:
                    zero_in.append(wire.to_node)

    # Any remaining due to cycles
    for nid in ancestor_ids:
        if nid not in ordered_ids:
            ordered_ids.append(nid)

    return [graph.nodes[nid] for nid in ordered_ids if nid in graph.nodes]


def compute_upstream_fingerprint(ancestors: List[ThoughtNode]) -> str:
    """
    Compute a deterministic SHA-256 fingerprint across all upstream ancestors.
    Includes node ID, kind, content/snippet, and tags.
    """
    hasher = hashlib.sha256()
    for node in ancestors:
        text = node.selected_snippet if (node.highlight_mode == HighlightMode.SELECTIVE and node.selected_snippet) else node.content
        payload = f"{node.id}:{node.kind.value}:{node.highlight_mode.value}:{text.strip()}:{','.join(sorted(node.tags))}"
        hasher.update(payload.encode("utf-8"))
    return hasher.hexdigest()


def compile_thoughtdag_context(
    graph: ThoughtDAGGraph,
    target_node_id: str,
    max_tokens: Optional[int] = None,
    include_kinds: Optional[List[NodeKind]] = None
) -> ContextCompileResponse:
    """
    Compiles the full upstream prompt context for a target node according to CONTRACT-002.
    """
    ancestors = compute_upstream_ancestors(graph, target_node_id)
    if include_kinds:
        ancestors = [n for n in ancestors if n.kind in include_kinds]

    fingerprint = compute_upstream_fingerprint(ancestors)
    target_node = graph.nodes.get(target_node_id)
    is_stale = False
    if target_node and target_node.upstream_fingerprint:
        is_stale = target_node.upstream_fingerprint != fingerprint

    sections: List[str] = []
    included: List[CompiledContextNode] = []

    for node in ancestors:
        is_snippet = False
        if node.highlight_mode == HighlightMode.SELECTIVE and node.selected_snippet:
            node_text = node.selected_snippet.strip()
            is_snippet = True
        else:
            node_text = node.content.strip()

        if not node_text:
            continue

        prefix = f"### [Context Node: {node.title}] (Kind: {node.kind.value})"
        if is_snippet:
            prefix += " [Selective Excerpt]"
        if node.tags:
            prefix += f" [Tags: {', '.join(node.tags)}]"

        section = f"{prefix}\n{node_text}\n"
        sections.append(section)

        included.append(
            CompiledContextNode(
                node_id=node.id,
                title=node.title,
                kind=node.kind,
                text=node_text,
                snippet_only=is_snippet
            )
        )

    full_context_text = "\n".join(sections).strip()
    # Rough token count estimate (4 chars/token)
    estimated_tokens = max(1, len(full_context_text) // 4) if full_context_text else 0

    return ContextCompileResponse(
        target_node_id=target_node_id,
        context_text=full_context_text,
        upstream_fingerprint=fingerprint,
        included_nodes=included,
        is_stale=is_stale,
        estimated_tokens=estimated_tokens
    )


def transpile_obsidian_canvas_to_thoughtdag(canvas_data: Dict[str, Any]) -> ThoughtDAGGraph:
    """
    Transpiles an Obsidian JSON Canvas (.canvas) structure into a ThoughtDAGGraph.
    - 'text' nodes -> ThoughtNode(kind=NOTE)
    - 'file' nodes -> ThoughtNode(kind=ENTITY)
    - edges -> Wire(wire_type=CONTEXT)
    """
    graph_id = canvas_data.get("id", "obsidian_canvas_transpiled")
    nodes_dict: Dict[str, ThoughtNode] = {}
    wires_list: List[Wire] = []

    for raw_node in canvas_data.get("nodes", []):
        nid = raw_node.get("id", "")
        ntype = raw_node.get("type", "text")
        
        kind = NodeKind.NOTE
        title = "Note"
        content = ""

        if ntype == "text":
            kind = NodeKind.NOTE
            content = raw_node.get("text", "")
            lines = content.strip().split("\n")
            title = lines[0].replace("#", "").strip() if lines and lines[0] else "Note"
        elif ntype == "file":
            kind = NodeKind.ENTITY
            content = raw_node.get("file", "")
            title = content.split("/")[-1]
        elif ntype == "link":
            kind = NodeKind.SAAP_TOOL
            content = raw_node.get("url", "")
            title = content

        node = ThoughtNode(
            id=nid,
            kind=kind,
            title=title or "Untitled Node",
            content=content,
            metadata={
                "x": raw_node.get("x", 0),
                "y": raw_node.get("y", 0),
                "width": raw_node.get("width", 250),
                "height": raw_node.get("height", 140),
                "color": raw_node.get("color")
            }
        )
        nodes_dict[nid] = node

    for raw_edge in canvas_data.get("edges", []):
        eid = raw_edge.get("id", f"wire_{raw_edge.get('fromNode')}_{raw_edge.get('toNode')}")
        from_id = raw_edge.get("fromNode", "")
        to_id = raw_edge.get("toNode", "")
        wire = Wire(
            id=eid,
            from_node=from_id,
            to_node=to_id,
            wire_type=WireType.CONTEXT,
            label=raw_edge.get("label")
        )
        wires_list.append(wire)

    return ThoughtDAGGraph(
        graph_id=graph_id,
        project_id="obsidian",
        nodes=nodes_dict,
        wires=wires_list
    )
