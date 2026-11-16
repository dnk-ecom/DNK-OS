# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/thought_companion_agent_and_9_harness_synthesis.md"
# purpose: "Architecture, contracts, and implementation patterns for FirstThoughtCompanionAgent (Gerych Thought Companion) distilling DNK_OS_APP and 9 SOTA DAG/Canvas harnesses."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-15"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🧠 First Thought Companion Agent & 9-Harness DAG Synthesis

This reference documents the canonical architecture implemented in `core/kernel/thought_companion.py`, `core/kernel/contracts.py`, and `apps/api/routers/kernel_router.py`. It distills the historical `DNK_OS_APP` MVP donor with 9 global open-source DAG/Canvas harness architectures.

## 1. The 9 Assimilated Global Harnesses (`ASSIMILATED_GLOBAL_PATTERNS`)

1. **`chenxiachan/thoughtdag`**: Typed reasoning nodes (`hypothesis`, `evidence`, `critique`, `conclusion`, `question`, `evaluation`), ThoughtDSL `[type] ID: Title`, and immediate parent-only context compilation (`compile_thoughtdag_context`) with `token_budget=4000`.
2. **`winlp4ever/canvas-harness`**: Spatial Role Capsule binding — every canvas node binds to an isolated `AgentCapsuleSpec` enforcing `MAX_TOOLS_PER_CAPSULE <= 8` and `max_context_tokens <= 6000`.
3. **`ximing/tributary`**: Causal Tree Layout (`_compute_causal_tree_layout`) — non-overlapping horizontal rank (`depth * 360px`) and vertical sibling spacing (`220px`) for deterministic canvas placement.
4. **`vcmf/dim0`**: Strict input/output port typing and contextual wire routing (`WireType.CONTEXT`, `WireType.TRIGGER`, `WireType.DEPENDENCY`, `WireType.MERGE`).
5. **`dagster-io/dagster`**: Upstream SHA-256 content fingerprinting (`compute_upstream_fingerprint`) and automatic downstream staleness propagation (`is_stale`) + Kahn's topological cycle detection (`detect_cycles_kahn`).
6. **`toolclub/dsh-agent-team-gui`**: Visual multi-agent role badge routing across the 5 canonical capsules (`dnk_companion_architect`, `dnk_shopify`, `gerych_builder`, `dnk_dev_fullstack`, `gerych_auditor`).
7. **`thesakshijaiswal/algopipe`**: Topological stage execution ordering and convergence onto a terminal verification gate (`[evaluation] NGATE_VERIFY`).
8. **`ullaskunder3/node-editor`**: Dual-surface serialization outputting both ReactFlow/XYFlow JSON (`xyflow_canvas`) and Obsidian JSON Canvas 1.0 (`obsidian_canvas`).
9. **`yule1048596-art/nonlinear-chat`**: Non-linear thought branching via `parent_node_ids`, allowing any new brainstorm to attach to existing nodes without flattening history.

## 2. Canonical Domain & Contract Rules

- **Wire Schema (`core/domain/dag_models.py`)**: Always instantiate `Wire(id=..., from_node=..., to_node=..., wire_type=...)` using `from_node` and `to_node` (never `source`/`target`, which belong only to the downstream `xyflow_canvas` edge projection).
- **Single-Line vs Multi-Line Decomposition**: In `FirstThoughtCompanionAgent.structure_thoughts`, when `raw_lines` has only 1 line (`len(raw_lines) == 1`), `action_segments` must fall back to `raw_lines[:1]` so a single-sentence brainstorm still produces at least `N0_VISION -> N1_ACTION -> NGATE_VERIFY` (minimum 3 nodes).
- **Mandatory Dissent (`CompanionCritiqueBlock`)**: Every structured thought response includes `three_flaws`, `boundary_conditions`, and `skeptic_alternative`.

## 3. FastAPI Endpoints (`apps/api/routers/kernel_router.py`)

- `GET /api/v1/kernel/companion/capsules`: Returns `CANONICAL_ROLE_CAPSULES` and `ASSIMILATED_GLOBAL_PATTERNS`.
- `POST /api/v1/kernel/companion/structure`: Accepts `ThoughtCompanionRequest` and returns `ThoughtCompanionResponse` containing `dsl_script`, `thought_dag`, `xyflow_canvas`, `obsidian_canvas`, `critique`, and `recommended_capsules`.
