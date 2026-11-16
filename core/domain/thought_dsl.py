# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/thought_dsl.py"
# purpose: "ThoughtDAG 2.0 DSL Parser, Cycle Detection (Kahn's Algorithm), and Multi-Parent Context Merging for Swarm Agents."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
ThoughtDAG 2.0 DSL & Multi-Parent Context Aggregation Engine.
Allows agents and human operators to declare thought trees via lightweight DSL:
    [hypothesis] H1: Monolith Migration
    [hypothesis] H2: Micro-frontend Isolation
    [critique] C1: Team overhead risk
    [synthesis] S1: Hybrid Core with Islands
    H1 -> C1
    H2 -> C1
    C1 -> S1
"""

from collections import deque
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from core.domain.dag_models import (
    HighlightMode,
    NodeKind,
    ThoughtDAGGraph,
    ThoughtNode,
    Wire,
    WireType,
    compute_upstream_ancestors,
    compute_upstream_fingerprint,
)


class ThoughtType(str, Enum):
    HYPOTHESIS = "hypothesis"
    CRITIQUE = "critique"
    SYNTHESIS = "synthesis"
    DECISION = "decision"
    QUESTION = "question"
    EVALUATION = "evaluation"
    NOTE = "note"


class DSLNodeDef(BaseModel):
    id: str
    thought_type: ThoughtType
    label: str
    content: str = ""


class DSLWireDef(BaseModel):
    from_node: str
    to_node: str
    label: Optional[str] = None


class DSLParseResult(BaseModel):
    graph: ThoughtDAGGraph
    errors: List[str] = Field(default_factory=list)
    has_cycles: bool = False
    cycle_nodes: List[str] = Field(default_factory=list)


class MultiParentMergeRequest(BaseModel):
    graph: ThoughtDAGGraph
    parent_node_ids: List[str]
    target_node_id: Optional[str] = None
    target_title: Optional[str] = "Synthesis"


class MultiParentMergeResult(BaseModel):
    target_node_id: str
    target_title: str
    synthesized_prompt: str
    source_parents: List[Dict[str, Any]]
    ancestors_deduped_count: int
    upstream_fingerprint: str


def detect_cycles_kahn(node_ids: Set[str], edges: List[Tuple[str, str]]) -> Tuple[bool, List[str]]:
    """
    Detects directed cycles using Kahn's algorithm (topological sort via indegrees).
    Returns (has_cycle: bool, cycle_node_ids: List[str]).
    """
    if not node_ids:
        return False, []

    in_degree: Dict[str, int] = {nid: 0 for nid in node_ids}
    adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}

    for u, v in edges:
        if u in node_ids and v in node_ids:
            adj[u].append(v)
            in_degree[v] += 1

    zero_in = deque([nid for nid in node_ids if in_degree[nid] == 0])
    visited_count = 0

    while zero_in:
        u = zero_in.popleft()
        visited_count += 1
        for v in adj.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                zero_in.append(v)

    if visited_count == len(node_ids):
        return False, []

    # Nodes with in_degree > 0 participate in or descend from a cycle
    cycle_nodes = [nid for nid, deg in in_degree.items() if deg > 0]
    return True, cycle_nodes


def parse_thought_dsl(dsl_text: str, graph_id: str = "thought_dsl_graph") -> DSLParseResult:
    """
    Parses DSL declarations into a ThoughtDAGGraph with validation and Kahn cycle detection.
    Syntax:
        [<type>] <ID>: <Title/Summary>
        <ID> -> <ID> [: <Optional wire label>]
    """
    errors: List[str] = []
    nodes: Dict[str, ThoughtNode] = {}
    wires: List[Wire] = []
    edge_tuples: List[Tuple[str, str]] = []

    node_pattern = re.compile(r"^\[(?P<type>[a-zA-Z_-]+)\]\s*(?P<id>[a-zA-Z0-9_\-]+)\s*:\s*(?P<label>.*)$")
    edge_pattern = re.compile(r"^(?P<from>[a-zA-Z0-9_\-]+)\s*->\s*(?P<to>[a-zA-Z0-9_\-]+)(?:\s*:\s*(?P<label>.*))?$")

    lines = dsl_text.strip().splitlines()
    current_node_id: Optional[str] = None
    accumulated_content: List[str] = []

    def flush_content():
        nonlocal current_node_id, accumulated_content
        if current_node_id and current_node_id in nodes:
            extra_content = "\n".join(accumulated_content).strip()
            if extra_content:
                existing = nodes[current_node_id].content
                nodes[current_node_id].content = f"{existing}\n\n{extra_content}".strip()
        accumulated_content = []

    for line_idx, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue

        # Check for node definition
        node_match = node_pattern.match(line)
        if node_match:
            flush_content()
            raw_type = node_match.group("type").lower()
            node_id = node_match.group("id")
            label = node_match.group("label").strip()

            try:
                thought_type = ThoughtType(raw_type)
            except ValueError:
                thought_type = ThoughtType.NOTE

            node = ThoughtNode(
                id=node_id,
                kind=NodeKind.NOTE,
                title=label or node_id,
                content=label,
                metadata={
                    "thought_type": thought_type.value,
                    "dsl_source": True,
                },
                tags=[thought_type.value],
            )
            nodes[node_id] = node
            current_node_id = node_id
            continue

        # Check for edge definition
        edge_match = edge_pattern.match(line)
        if edge_match:
            flush_content()
            current_node_id = None
            from_node = edge_match.group("from")
            to_node = edge_match.group("to")
            edge_label = edge_match.group("label")
            wire_id = f"wire_{from_node}_to_{to_node}_{len(wires)}"

            wire = Wire(
                id=wire_id,
                from_node=from_node,
                to_node=to_node,
                wire_type=WireType.CONTEXT,
                label=edge_label.strip() if edge_label else None,
                metadata={"dsl_wire": True},
            )
            wires.append(wire)
            edge_tuples.append((from_node, to_node))
            continue

        # Otherwise treat as multi-line content for current node
        if current_node_id:
            accumulated_content.append(raw_line)
        else:
            errors.append(f"Line {line_idx}: Unrecognized DSL token outside node: '{line}'")

    flush_content()

    # Validate edge endpoints
    node_keys = set(nodes.keys())
    for from_n, to_n in edge_tuples:
        if from_n not in node_keys:
            errors.append(f"Wire references undefined source node '{from_n}'")
        if to_n not in node_keys:
            errors.append(f"Wire references undefined target node '{to_n}'")

    # Detect cycles via Kahn's algorithm
    has_cycles, cycle_nodes = detect_cycles_kahn(node_keys, edge_tuples)
    if has_cycles:
        errors.append(f"Cycle detected in Thought DAG among nodes: {', '.join(cycle_nodes)}")

    graph = ThoughtDAGGraph(
        graph_id=graph_id,
        project_id="thought_dag_core",
        root_nodes=[nid for nid in nodes if not any(t == nid for _, t in edge_tuples)],
        nodes=nodes,
        wires=wires,
    )

    return DSLParseResult(
        graph=graph,
        errors=errors,
        has_cycles=has_cycles,
        cycle_nodes=cycle_nodes,
    )


def export_thought_dsl(graph: ThoughtDAGGraph) -> str:
    """
    Exports a ThoughtDAGGraph into human-readable Thought DSL.
    """
    lines: List[str] = []

    # Output node declarations
    for node in graph.nodes.values():
        thought_type = node.metadata.get("thought_type", "note")
        lines.append(f"[{thought_type}] {node.id}: {node.title}")
        if node.content and node.content != node.title:
            # Indent multi-line content
            for sub_line in node.content.splitlines():
                if sub_line.strip() and sub_line.strip() != node.title:
                    lines.append(f"  {sub_line}")

    if lines:
        lines.append("")

    # Output wire declarations
    for wire in graph.wires:
        if wire.label:
            lines.append(f"{wire.from_node} -> {wire.to_node} : {wire.label}")
        else:
            lines.append(f"{wire.from_node} -> {wire.to_node}")

    return "\n".join(lines).strip()


def merge_multi_parent_context(
    graph: ThoughtDAGGraph,
    parent_node_ids: List[str],
    target_title: str = "Synthesis",
    target_node_id: Optional[str] = None,
) -> MultiParentMergeResult:
    """
    Merges context from multiple upstream research branches into a single synthesized context.
    Ensures shared ancestor deduplication and preserves topological causal ordering.
    """
    target_id = target_node_id or f"synthesis_{'_'.join(parent_node_ids)}"
    all_ancestors_ordered: List[ThoughtNode] = []
    seen_ancestor_ids: Set[str] = set()
    parent_summaries: List[Dict[str, Any]] = []

    for parent_id in parent_node_ids:
        if parent_id not in graph.nodes:
            continue

        parent_node = graph.nodes[parent_id]
        parent_ancestors = compute_upstream_ancestors(graph, parent_id)

        # Include parent's own ancestors (deduplicated)
        for anc in parent_ancestors:
            if anc.id not in seen_ancestor_ids:
                seen_ancestor_ids.add(anc.id)
                all_ancestors_ordered.append(anc)

        # Include parent node itself
        if parent_node.id not in seen_ancestor_ids:
            seen_ancestor_ids.add(parent_node.id)
            all_ancestors_ordered.append(parent_node)

        parent_summaries.append({
            "parent_id": parent_node.id,
            "title": parent_node.title,
            "kind": parent_node.kind.value,
            "content": parent_node.content,
        })

    # Compute deduplicated upstream fingerprint
    upstream_fingerprint = compute_upstream_fingerprint(all_ancestors_ordered)

    # Build prompt synthesis
    prompt_lines: List[str] = [
        f"# Multi-Branch Context Synthesis for [{target_title}]",
        f"Aggregated upstream inputs from {len(parent_summaries)} distinct branches with topological ancestor deduplication.\n",
        "## Upstream Context Ancestry (Topological Order):",
    ]

    for anc in all_ancestors_ordered:
        prompt_lines.append(f"- **[{anc.title}]** ({anc.kind.value}): {anc.content.strip()[:300]}")

    prompt_lines.append("\n## Direct Converging Branches:")
    for p in parent_summaries:
        prompt_lines.append(f"### Branch: {p['title']} (`{p['parent_id']}`)\n{p['content'].strip()}\n")

    prompt_lines.append("## Directive:\nSynthesize the above converging perspectives into a unified architectural resolution.")

    synthesized_prompt = "\n".join(prompt_lines)

    return MultiParentMergeResult(
        target_node_id=target_id,
        target_title=target_title,
        synthesized_prompt=synthesized_prompt,
        source_parents=parent_summaries,
        ancestors_deduped_count=len(all_ancestors_ordered),
        upstream_fingerprint=upstream_fingerprint,
    )
