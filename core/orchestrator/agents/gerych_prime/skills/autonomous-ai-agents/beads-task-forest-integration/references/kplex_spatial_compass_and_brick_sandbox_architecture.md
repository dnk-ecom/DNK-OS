# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/beads-task-forest-integration/references/kplex_spatial_compass_and_brick_sandbox_architecture.md"
# purpose: "K-Plex 5-zone spatial compass layout, graph lenses, relation evidence provenance, and isolated branch-to-brick sandbox execution for DNK OS."
# canonical_source: true
# alters_files: ["core/task_forest/models.py", "core/task_forest/forest.py", "core/bricks/registry.py", "core/orchestrator/subagent_sandbox.py"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-14"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# K-Plex Spatial Compass, Graph Lenses & Brick-Sandbox Execution Blueprint

This reference encodes the Track 2 Clean-Room architectural synthesis of **`zsviczian/kplex`** (AGPL-3.0 spatial knowledge navigator) combined with DNK OS's native **`core/task_forest/`**, **`core/bricks/registry.py`**, **`core/orchestrator/subagent_sandbox.py`**, and **`services/dnk_shopify/DNK_Horizon_Tinker/`** (Shopify Horizon — Tinker 4.3.0).

---

## 1. Deterministic 5-Zone Ego-Centric Compass Layout (Anti-Force-Graph Chaos)

Unlike force-directed graphs where nodes jump unpredictably, the active `TaskNode` (or Idea/Brick) sits at the **Focal Center**, surrounded by 5 deterministic spatial zones:

1. **⬆️ North (Parents / Epics / Architecture Contracts)**:
   - High-level goal, ADR, or parent `TaskNode` (e.g., `Epic: DNK-Ecom Theme on Horizon Tinker 4.3.0`).
2. **⬇️ South (Children / Step-by-Step Execution Branches)**:
   - Concrete atomic subtasks (`Slice <= 25 tool calls`) to be executed sequentially or in parallel branches.
3. **⬅️ West (Friends / Prerequisites / Reusable Bricks)**:
   - Existing verified `BrickSpec` modules from `core/bricks/registry.py`, SCONES memories, and upstream completed nodes that feed inputs/contracts into the focal task.
4. **➡️ East (Challengers / Alternatives / Adversarial Audit)**:
   - Competing hypotheses, `gerych_auditor` critique gates, A/B variations, or downstream dependent consumers.
5. **↗️ Periphery (Siblings)**:
   - Adjacent tasks sharing the same parent epic for peripheral situational awareness without visual clutter.

---

## 2. Graph Lenses & Dark Teal Status Color Coding

Adapted from K-Plex's declarative `GraphLens` pipeline (`Scope: Note | Relationship | Evidence -> Conditions -> Effect: Show | Hide | Style`), every branch node in `TaskForest` is styled deterministically:

| Visual Badge | `ExecutionStage` | Dark Teal Hex | Canvas Color ID | Sandbox & Swarm State |
| :--- | :--- | :--- | :--- | :--- |
| ⚪ **Seed / Idea** | `DRAFT` / `PENDING` | `#64748b` | `"0"` (Slate) | Raw thought, hypothesis, or backlog item persisted in SCONES + Obsidian. |
| 🔵 **Ready Slice** | `READY` | `#35d5d5` | `"5"` (Cyan) | All North (`Parents`) and West (`Bricks`) dependencies satisfied; ready to claim. |
| 🟡 **Sandbox Active** | `IN_PROGRESS` | `#f59e0b` | `"2"` (Amber) | Isolated `SubagentSandbox` active with strict `Target File Whitelist`. |
| 🟣 **Auditor Gate** | `VERIFYING` | `#a855f7` | `"6"` (Purple) | Code written in sandbox; `gerych_auditor` running AST/Schema/Unit verification. |
| 🟢 **Sealed Brick** | `COMPLETED` | `#22c55e` | `"4"` (Green) | Verified 100% Green, merged to mainline, and registered/upgraded in `BrickRegistry`. |
| 🔴 **Blocked / Failed** | `BLOCKED` / `FAILED` | `#ef4444` | `"1"` (Red) | Verification failed or dependency blocked; triggers `dnk_query_error_solutions`. |

---

## 3. RelationEvidenceStore (Edge Provenance Contract)

Every directed edge `(source_id -> target_id)` in the task/brick graph carries machine-verifiable provenance (`RelationEvidence`) rather than an untyped arrow:
- `dependency_type`: `"task_prerequisite" | "brick_import" | "liquid_render_snippet" | "css_token_consumer" | "mrh_alters_file"`
- `evidence_locator`: File path, AST line range, or schema key proving why the connection exists (e.g., `sections/main-product.liquid:L42 -> snippets/buy-buttons.liquid`).
- `impact_weight`: Blast-radius weight computed by `core/task_forest/diff_impact_analyzer.py`.

---

## 4. 4-Tier Modular "Brick -> Plugin -> Service -> Swarm" Hierarchy

To prevent agents from regenerating boilerplate from scratch and exhausting token budgets, all outputs must register into `core/bricks/registry.py`:

1. **Level 1 — Atomic Brick (`BrickSpec`)**:
   - Single self-contained unit with explicit inputs, CSS tokens, `target_files`, and `test_command` (e.g., `blocks/tinker-dnk-quantity-breaks.liquid` or `blocks/swatches.liquid` in `DNK_Horizon_Tinker`).
2. **Level 2 — Composite Plugin (`BlueprintGraph` Bundle)**:
   - Wired assembly of 2–5 bricks (e.g., `High-CRO Product Card Plugin` = `_product-card-gallery` + `swatches` + `review` + `buy-buttons`).
3. **Level 3 — Domain Service (`services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`)**:
   - Orchestrates plugins into complete deliverables (e.g., full OS 2.0 theme templates `index.json`, `product.json`).
4. **Level 4 — Pre-Flight Brick Lookup Gate (Anti-Duplication Rule)**:
   - Before dispatching a builder agent on any branch node, the orchestrator queries `BrickRegistry.list_bricks(layer=..., tags=...)`.
   - If an existing brick matches $\ge 70\%$ of the capability contract, the branch node MUST run in **`UPGRADE_EXISTING_BRICK (v1.x -> v1.y)`** mode inside its `SubagentSandbox` rather than creating a duplicate module.
