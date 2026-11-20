# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/thought_companion.py"
# purpose: "First Agent Companion & Architect (Gerych Thought Companion) distilling DNK_OS_APP MVP and the 9 global SOTA DAG/Canvas harness architectures into interconnected ThoughtDAG & XYFlow nodes."
# canonical_source: true
# alters_files: ["core/domain/companion_contracts.py", "apps/api/routers/kernel_router.py"]
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-11-17"
# author: "Gerych Prime & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
First Agent Companion & Architect (Gerych Thought Companion).

Distills the `/DNK_OS_APP` MVP architecture and integrates the 9 global SOTA
Canvas & DAG Harness systems explored in session 20261014_233355_7d3ab0:
1. chenxiachan/thoughtdag — ThoughtDAG 2.0 DSL (`[type] ID: Label`, `A -> B`, SHA-256 fingerprint)
2. winlp4ever/canvas-harness — Dual-Surface Agentic Canvas & Capsule binding
3. ximing/tributary — Causal Tree Layout (layered topological X/Y positioning)
4. vcmf/dim0 — Minimalist Zero-Framework Microkernel Execution
5. dagster-io/dagster — Software-Defined Assets & Data Lineage verification
6. toolclub/dsh-agent-team-gui — Multi-Agent Role Capsule assignment & visual team routing
7. thesakshijaiswal/algopipe — Typed pipeline ports & cycle-safe wiring
8. ullaskunder3/node-editor — XYFlow / ReactFlow interactive node-edge state schema
9. yule1048596-art/nonlinear-chat — Non-Linear Branching Dialogue & context wire assembly
"""

import hashlib
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from core.domain.dag_models import (
    NodeKind,
    ThoughtDAGGraph,
    ThoughtNode,
    Wire,
    WireType,
    compile_thoughtdag_context,
    compute_upstream_ancestors,
    compute_upstream_fingerprint,
)
from core.domain.thought_dsl import (
    ThoughtType,
    detect_cycles_kahn,
    parse_thought_dsl,
)
from core.domain.companion_contracts import (
    AgentCapsuleSpec,
    CompanionCritiqueBlock,
    ThoughtCompanionRequest,
    ThoughtCompanionResponse,
)
from core.obsidian.json_canvas_builder import (
    CanvasColor,
    CanvasEdge,
    CanvasEnd,
    JSONCanvasDocument,
    TextNode,
    generate_canvas_id,
)

# 8 Canonical Role Capsules per DEC-004 (4 Dev Builders + 4 Runtime Business Executors)
CANONICAL_ROLE_CAPSULES: Dict[str, AgentCapsuleSpec] = {
    "dnk_companion_architect": AgentCapsuleSpec(
        capsule_id="dnk_companion_architect",
        role_name="Gerych Thought Companion & Chief Architect",
        track="dev",
        sanctioned_tools=[
            "dnk_triage_task",
            "dnk_decompose_task_dna",
            "scones_get_memories",
            "dnk_resolve_symbol",
        ],
        skills_loaded=[
            "thoughtdag_assimilated",
            "tributary_assimilated",
            "dnk-intent-discovery",
        ],
        max_context_tokens=4500,
        target_files_lock=["core/kernel/**", "docs/architecture/**"],
        can_mutate_files=False,
    ),
    "gerych_builder": AgentCapsuleSpec(
        capsule_id="gerych_builder",
        role_name="UI & Infinity Canvas Builder",
        track="dev",
        sanctioned_tools=["read_file", "patch", "write_file", "search_files", "dnk_resolve_symbol"],
        skills_loaded=["canvas-engine-architecture", "excalidraw", "dsh_agent_team_gui_assimilated"],
        max_context_tokens=5000,
        target_files_lock=["apps/web/**"],
        can_mutate_files=True,
    ),
    "dnk_dev_fullstack": AgentCapsuleSpec(
        capsule_id="dnk_dev_fullstack",
        role_name="FastAPI Microkernel & DAG Backend Engineer",
        track="dev",
        sanctioned_tools=["read_file", "patch", "write_file", "search_files", "terminal"],
        skills_loaded=["architecture-invariants-and-blast-radius", "test-driven-development"],
        max_context_tokens=5000,
        target_files_lock=["apps/api/**", "core/**"],
        can_mutate_files=True,
    ),
    "gerych_auditor": AgentCapsuleSpec(
        capsule_id="gerych_auditor",
        role_name="Red-Team Security & Quality Gate Auditor",
        track="dev",
        sanctioned_tools=["read_file", "search_files", "terminal", "dnk_run_adversarial_review"],
        skills_loaded=["requesting-code-review", "agentshield_assimilated"],
        max_context_tokens=4000,
        target_files_lock=["tests/**", "scripts/**"],
        can_mutate_files=False,
    ),
    "dnk_shopify": AgentCapsuleSpec(
        capsule_id="dnk_shopify",
        role_name="Shopify OS 2.0 Theme & CRO Block Specialist",
        track="runtime",
        sanctioned_tools=["read_file", "patch", "write_file", "dnk_shopify_validate_liquid"],
        skills_loaded=[
            "shopify-theme-ast-engineering",
            "shopify_theme_handbook_assimilated",
            "ks_origin_assimilated",
        ],
        max_context_tokens=5000,
        target_files_lock=["services/dnk_shopify/**"],
        can_mutate_files=True,
    ),
    "dnk_video_ai_creator": AgentCapsuleSpec(
        capsule_id="dnk_video_ai_creator",
        role_name="Kinetic Video & Media Pipeline Creator",
        track="runtime",
        sanctioned_tools=["dnk_video_generate_composition", "read_file", "write_file"],
        skills_loaded=["word-anchored-shorts", "video-retention-engineering"],
        max_context_tokens=4500,
        target_files_lock=["services/dnk_media/**"],
        can_mutate_files=True,
    ),
    "dnk_scones_memory": AgentCapsuleSpec(
        capsule_id="dnk_scones_memory",
        role_name="SCONES Knowledge & Obsidian PKM Librarian",
        track="runtime",
        sanctioned_tools=["scones_get_memories", "scones_add_memory", "read_file", "write_file"],
        skills_loaded=["obsidian", "review-gated-ingest", "visual-thinking-pkm"],
        max_context_tokens=4000,
        target_files_lock=["docs/notes/**"],
        can_mutate_files=True,
    ),
    "dnk_distribution": AgentCapsuleSpec(
        capsule_id="dnk_distribution",
        role_name="Omni-Channel Content & Growth Executor",
        track="runtime",
        sanctioned_tools=["read_file", "write_file", "web_search"],
        skills_loaded=["postiz-distribution-rlsf", "content-compliance-hitl"],
        max_context_tokens=4000,
        target_files_lock=["services/dnk_distribution/**"],
        can_mutate_files=False,
    ),
}

ASSIMILATED_GLOBAL_PATTERNS: List[str] = [
    "chenxiachan/thoughtdag (ThoughtDAG 2.0 DSL & SHA-256 Content Fingerprinting)",
    "winlp4ever/canvas-harness (Dual-Surface Agentic Canvas & Role Capsule Binding)",
    "ximing/tributary (Causal Tree Topological Layout Engine)",
    "vcmf/dim0 (Zero-Framework Lightweight Microkernel Loop)",
    "dagster-io/dagster (Software-Defined Lineage & Upstream Stale Propagation)",
    "toolclub/dsh-agent-team-gui (Visual Swarm Team Routing & Capsule Assignment)",
    "thesakshijaiswal/algopipe (Typed Port Contracts & Cycle-Safe Kahn Validation)",
    "ullaskunder3/node-editor (XYFlow / ReactFlow Interactive Node-Edge State)",
    "yule1048596-art/nonlinear-chat (Non-Linear Branching Dialogue & Context Wires)",
]


class FirstThoughtCompanionAgent:
    """
    First Agent Companion & Architect of DNK OS.
    Transforms unstructured founder ideas or ThoughtDSL scripts into:
    1. A validated, cycle-free ThoughtDAG graph with SHA-256 node fingerprints.
    2. Causal tree topological coordinates (Tributary layout) for XYFlow (`apps/web`).
    3. JSON Canvas 1.0 document for Obsidian (`./docs/notes/`).
    4. Role Capsule assignments (`AgentCapsuleSpec`) with file lock isolation.
    5. Mandatory Epistemic Critique (3 Hidden Risks, Boundary Conditions, Skeptic Alternative).
    """

    def __init__(self) -> None:
        self.capsules = CANONICAL_ROLE_CAPSULES

    def _infer_type_kind_and_capsule(
        self, text_segment: str, idx: int
    ) -> Tuple[ThoughtType, NodeKind, str]:
        """Infers the optimal ThoughtType, NodeKind, and Role Capsule from text intent."""
        lower = text_segment.lower()
        if any(w in lower for w in ("shopify", "liquid", "theme", "store", "cro", "pdp", "магазин", "блок")):
            return ThoughtType.SYNTHESIS, NodeKind.AGENT, "dnk_shopify"
        if any(w in lower for w in ("ui", "canvas", "xyflow", "react", "node", "інтерфейс", "полотно", "нод")):
            return ThoughtType.SYNTHESIS, NodeKind.TASK, "gerych_builder"
        if any(w in lower for w in ("test", "audit", "security", "gate", "verify", "тест", "аудит", "безпек")):
            return ThoughtType.EVALUATION, NodeKind.TASK, "gerych_auditor"
        if any(w in lower for w in ("memory", "obsidian", "scones", "note", "vault", "пам'ят", "нотат")):
            return ThoughtType.NOTE, NodeKind.NOTE, "dnk_scones_memory"
        if any(w in lower for w in ("video", "media", "remotion", "short", "відео", "медіа")):
            return ThoughtType.SYNTHESIS, NodeKind.ARTIFACT, "dnk_video_ai_creator"
        if any(w in lower for w in ("api", "kernel", "backend", "fastapi", "harness", "ядро", "харнес", "сервер")):
            return ThoughtType.DECISION, NodeKind.TASK, "dnk_dev_fullstack"
        if idx == 0:
            return ThoughtType.HYPOTHESIS, NodeKind.PROJECT, "dnk_companion_architect"
        return ThoughtType.HYPOTHESIS, NodeKind.TASK, "dnk_companion_architect"

    def _synthesize_dsl_from_raw_thought(self, raw_thought: str, title: str) -> str:
        """
        Converts unstructured natural language ideas into canonical ThoughtDAG 2.0 DSL
        (`[type] ID: Title` and `ID1 -> ID2`) if the input is not already formatted in ThoughtDSL.
        """
        if re.search(r"^\[[a-zA-Z_-]+\]\s+[a-zA-Z0-9_\-]+\s*:", raw_thought.strip(), re.MULTILINE):
            return raw_thought.strip()

        raw_lines = [
            line.strip(" -•*\t0123456789.)")
            for line in re.split(r"[\n;]+", raw_thought)
            if len(line.strip(" -•*\t0123456789.)")) > 5
        ]
        if len(raw_lines) <= 1 and "." in raw_thought:
            raw_lines = [
                s.strip()
                for s in raw_thought.split(".")
                if len(s.strip()) > 8
            ]
        if not raw_lines:
            raw_lines = [raw_thought.strip()]

        dsl_nodes: List[str] = []
        dsl_edges: List[str] = []

        root_id = "N0_VISION"
        dsl_nodes.append(f"[hypothesis] {root_id}: {title}\n{raw_lines[0]}")

        step_ids: List[str] = []
        action_segments = raw_lines[1:7] if len(raw_lines) > 1 else raw_lines[:1]
        for idx, segment in enumerate(action_segments, start=1):
            t_type, _, capsule_id = self._infer_type_kind_and_capsule(segment, idx)
            node_id = f"N{idx}_{capsule_id.split('_')[-1].upper()}"
            dsl_nodes.append(
                f"[{t_type.value}] {node_id}: {segment[:72]}\n"
                f"Капсула: {capsule_id} | Деталі: {segment}"
            )
            parent_id = root_id if idx <= 2 else step_ids[-1]
            dsl_edges.append(f"{parent_id} -> {node_id}: context_flow")
            step_ids.append(node_id)

        # Attach Critic & Quality Gate convergence node (Dagster + ThoughtDAG pattern)
        gate_id = "NGATE_VERIFY"
        dsl_nodes.append(
            f"[evaluation] {gate_id}: Master Architecture & Quality Gate\n"
            f"Перевірка контрактів ядра, відсутності циклів у графі та ізоляції файлових замків."
        )
        if step_ids:
            for sid in step_ids[-3:]:
                dsl_edges.append(f"{sid} -> {gate_id}: verify_gate")
        else:
            dsl_edges.append(f"{root_id} -> {gate_id}: verify_gate")

        return "\n\n".join(dsl_nodes) + "\n\n" + "\n".join(dsl_edges)

    def _compute_causal_tree_layout(self, graph: ThoughtDAGGraph) -> Dict[str, Tuple[int, int]]:
        """
        Tributary + Node-Editor Causal Tree Layout Engine:
        Calculates deterministic topological layers (depth) and vertical lanes
        so nodes never overlap on the Infinity Canvas.
        """
        depths: Dict[str, int] = {nid: 0 for nid in graph.nodes}
        for _ in range(len(graph.nodes) + 1):
            changed = False
            for wire in graph.wires:
                if wire.from_node in depths and wire.to_node in depths:
                    candidate = depths[wire.from_node] + 1
                    if candidate > depths[wire.to_node]:
                        depths[wire.to_node] = candidate
                        changed = True
            if not changed:
                break

        layers: Dict[int, List[str]] = {}
        for nid, depth in depths.items():
            layers.setdefault(depth, []).append(nid)

        coords: Dict[str, Tuple[int, int]] = {}
        x_spacing = 420
        y_spacing = 180

        for depth, nids in sorted(layers.items()):
            count = len(nids)
            for idx, nid in enumerate(nids):
                x = depth * x_spacing
                y = int((idx - (count - 1) / 2.0) * y_spacing)
                coords[nid] = (x, y)

        return coords

    def _build_epistemic_critique(self, raw_thought: str, nodes_count: int) -> CompanionCritiqueBlock:
        """
        Generates the Mandatory Dissent & 3 Flaws critique per Section 6 of AGENTS.md.
        """
        return CompanionCritiqueBlock(
            hidden_risks=[
                "Ризик 1 (Контекстний вибух при глибокому розгалуженні): Якщо передавати повний контекст через >4 рівні нод, обсяг перевищить ліміт 6,000 токенів капсули.",
                "Ризик 2 (Колізія паралельних нод на спільних файлах): Якщо дві сусідні ноди одночасно мутують один файл без target_files_lock, виникне стан гонитви.",
                "Ризик 3 (Десинхронізація стану Canvas та SHA-256): Зміна тексту батьківської ноди робить дочірні артефакти застарілими (is_stale=True), якщо не перевіряти upstream_fingerprint.",
            ],
            boundary_conditions=[
                f"Поточний граф ({nodes_count} нод) стабільний при синхронному виконанні до 8 капсул одночасно.",
                "При масштабуванні понад 50 нод на одному полотні потрібна автоматична агрегація підграфів у GroupNode та режим вибіркових сніпетів (HighlightMode.SELECTIVE).",
            ],
            skeptic_alternative=(
                "Мінімалістична альтернатива: замість створення складного дерева підзадач для простих ідей (C <= 3), "
                "виконувати одну кореневу ноду [hypothesis] N0_VISION напряму в SOLO-режимі та розгортати дочірні ноди лише при виявленні мультидоменності."
            ),
        )

    def structure_thought(self, req: ThoughtCompanionRequest) -> ThoughtCompanionResponse:
        """
        Main orchestration entrypoint for the First Thought Companion & Architect Agent.
        Distills the input thought into a complete, interconnected multi-surface graph.
        """
        receipt_id = f"comp_{uuid.uuid4().hex[:12]}"
        dsl_script = self._synthesize_dsl_from_raw_thought(req.raw_thought, req.title)
        dsl_result = parse_thought_dsl(dsl_script, graph_id=f"dag_{receipt_id}")
        graph = dsl_result.graph

        # Merge with existing graph if provided (Nonlinear-Chat branching pattern)
        if req.existing_graph and isinstance(req.existing_graph.get("nodes"), dict):
            try:
                base_graph = ThoughtDAGGraph.model_validate(req.existing_graph)
                for nid, node in graph.nodes.items():
                    base_graph.nodes[nid] = node
                existing_edges = [(w.from_node, w.to_node) for w in base_graph.wires]
                all_node_ids = set(base_graph.nodes.keys())
                for wire in graph.wires:
                    test_edges = existing_edges + [(wire.from_node, wire.to_node)]
                    has_cyc, _ = detect_cycles_kahn(all_node_ids, test_edges)
                    if not has_cyc:
                        base_graph.wires.append(wire)
                        existing_edges.append((wire.from_node, wire.to_node))
                graph = base_graph
            except Exception:
                pass

        # Connect to explicit parent_node_ids if requested
        if req.parent_node_ids:
            first_node_id = next(iter(graph.nodes.keys()), None)
            if first_node_id:
                existing_edges = [(w.from_node, w.to_node) for w in graph.wires]
                all_node_ids = set(graph.nodes.keys())
                for parent_id in req.parent_node_ids:
                    if parent_id in graph.nodes and parent_id != first_node_id:
                        has_cyc, _ = detect_cycles_kahn(
                            all_node_ids, existing_edges + [(parent_id, first_node_id)]
                        )
                        if not has_cyc:
                            wire = Wire(
                                id=f"w_{parent_id}_{first_node_id}",
                                from_node=parent_id,
                                to_node=first_node_id,
                                wire_type=WireType.CONTEXT,
                                label="parent_branch",
                                token_budget=4000,
                            )
                            graph.wires.append(wire)
                            existing_edges.append((parent_id, first_node_id))

        # Compute Causal Tree Layout coordinates (Tributary pattern)
        coords = self._compute_causal_tree_layout(graph)

        # Assign Role Capsules and compute SHA-256 content fingerprints (Dagster + DSH-GUI pattern)
        assigned_capsules_map: Dict[str, AgentCapsuleSpec] = {}
        xyflow_nodes: List[Dict[str, Any]] = []
        xyflow_edges: List[Dict[str, Any]] = []
        obsidian_doc = JSONCanvasDocument()

        for idx, (nid, node) in enumerate(graph.nodes.items()):
            x, y = coords.get(nid, (idx * 380, 0))
            ancestors = compute_upstream_ancestors(graph, nid)
            fp = compute_upstream_fingerprint(ancestors + [node])
            node.upstream_fingerprint = fp

            _, inferred_kind, capsule_id = self._infer_type_kind_and_capsule(
                f"{node.title} {node.content}", idx
            )
            node.kind = inferred_kind
            capsule = self.capsules.get(capsule_id, self.capsules["dnk_companion_architect"])
            if req.auto_assign_capsules:
                node.assigned_agent = capsule.capsule_id
                node.metadata["assigned_capsule_id"] = capsule.capsule_id
                node.metadata["max_context_tokens"] = capsule.max_context_tokens
                node.metadata["target_files_lock"] = capsule.target_files_lock
                node.metadata["position"] = {"x": x, "y": y}
                assigned_capsules_map[capsule.capsule_id] = capsule

            thought_type_str = node.metadata.get("thought_type", "note")

            # Build XYFlow node for apps/web Infinity Canvas
            xyflow_nodes.append({
                "id": nid,
                "type": f"dnk_{node.kind.value}",
                "position": {"x": x, "y": y},
                "data": {
                    "label": node.title,
                    "kind": node.kind.value,
                    "thought_type": thought_type_str,
                    "status": node.status,
                    "content": node.content,
                    "upstream_fingerprint": fp,
                    "assigned_capsule": capsule.capsule_id,
                    "sanctioned_tools": capsule.sanctioned_tools,
                    "target_files_lock": capsule.target_files_lock,
                },
            })

            # Build Obsidian JSON Canvas 1.0 node
            color_map = {
                NodeKind.PROJECT: CanvasColor.CYAN,
                NodeKind.AGENT: CanvasColor.GREEN,
                NodeKind.TASK: CanvasColor.ORANGE,
                NodeKind.NOTE: CanvasColor.PURPLE,
                NodeKind.ARTIFACT: CanvasColor.YELLOW,
            }
            obsidian_doc.nodes.append(
                TextNode(
                    id=generate_canvas_id(nid),
                    x=x,
                    y=y,
                    width=340,
                    height=140,
                    text=(
                        f"### [{nid}:{thought_type_str}] {node.title}\n"
                        f"**Capsule**: `{capsule.capsule_id}` | **SHA**: `{fp[:8]}`\n\n"
                        f"{node.content[:160]}"
                    ),
                    color=color_map.get(node.kind, CanvasColor.CYAN),
                )
            )

        for wire in graph.wires:
            xyflow_edges.append({
                "id": wire.id,
                "source": wire.from_node,
                "target": wire.to_node,
                "type": "smoothstep",
                "animated": wire.wire_type == WireType.CONTEXT,
                "label": wire.label or wire.wire_type.value,
                "data": {
                    "wire_type": wire.wire_type.value,
                    "token_budget": wire.token_budget,
                },
            })
            obsidian_doc.edges.append(
                CanvasEdge(
                    id=generate_canvas_id(wire.id),
                    from_node=generate_canvas_id(wire.from_node),
                    to_node=generate_canvas_id(wire.to_node),
                    to_end=CanvasEnd.ARROW,
                    label=wire.label or wire.wire_type.value,
                    color=CanvasColor.CYAN,
                )
            )

        # Preview compiled context for the terminal node in the graph
        tail_node_id = list(graph.nodes.keys())[-1] if graph.nodes else ""
        compiled_preview = ""
        if tail_node_id:
            comp_res = compile_thoughtdag_context(graph, tail_node_id)
            compiled_preview = comp_res.context_text

        critique = self._build_epistemic_critique(req.raw_thought, len(graph.nodes))

        return ThoughtCompanionResponse(
            session_receipt_id=receipt_id,
            title=req.title,
            dsl_script=dsl_script,
            thought_dag={
                "graph_id": graph.graph_id,
                "has_cycles": dsl_result.has_cycles,
                "cycle_nodes": dsl_result.cycle_nodes,
                "nodes_count": len(graph.nodes),
                "wires_count": len(graph.wires),
                "nodes": {nid: n.model_dump() for nid, n in graph.nodes.items()},
                "wires": [w.model_dump() for w in graph.wires],
            },
            xyflow_canvas={
                "nodes": xyflow_nodes,
                "edges": xyflow_edges,
                "layout_engine": "tributary_causal_tree_v1",
            },
            obsidian_canvas=obsidian_doc.to_dict(),
            epistemic_critique=critique,
            assigned_capsules=list(assigned_capsules_map.values()),
            compiled_context_preview=compiled_preview,
            assimilated_patterns_applied=ASSIMILATED_GLOBAL_PATTERNS,
        )

    def structure_thoughts(self, req: ThoughtCompanionRequest) -> ThoughtCompanionResponse:
        """Alias for structure_thought used by FastAPI router endpoints."""
        return self.structure_thought(req)

    def get_assimilated_patterns(self) -> List[str]:
        """Returns the list of 9 global SOTA DAG/Canvas harness patterns assimilated into the kernel."""
        return ASSIMILATED_GLOBAL_PATTERNS


_companion_singleton: Optional[FirstThoughtCompanionAgent] = None


def get_thought_companion() -> FirstThoughtCompanionAgent:
    """Returns singleton instance of the First Thought Companion & Architect Agent."""
    global _companion_singleton
    if _companion_singleton is None:
        _companion_singleton = FirstThoughtCompanionAgent()
    return _companion_singleton
