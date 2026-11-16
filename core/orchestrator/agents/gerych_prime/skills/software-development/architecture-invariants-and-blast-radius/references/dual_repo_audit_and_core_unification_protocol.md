# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/dual_repo_audit_and_core_unification_protocol.md"
# purpose: "Canonical protocol for dual-repo audit (DNK_OS_APP Product v1 vs DNK_HUB R&D Factory), Self-Awareness Engine, and Zero-Hub-Leak invariants."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Dual-Repo Audit, Product v1 Architecture & Self-Awareness Protocol (`DNK_OS_APP` vs `DNK_HUB`)

## 1. Architectural Topology: Dual-Tier Roles

In the DNK OS ecosystem, development spans two coordinated repositories with strict role separation:

| Dimension | `DNK_OS_APP` (Clean Product v1 & Self-Aware Flagship) | `DNK_HUB` (R&D Swarm Factory & Assimilation Monorepo) |
|---|---|---|
| **Primary Role** | Clean, modular, standalone **First Product Version (Product v1)** of DNK OS with built-in self-awareness, plus canonical specs (`specs/01`–`07`) | Heavy R&D monorepo, 1997-repo catalog, 195 SOTA research digests, 55 skills, and multi-worker Swarm Factory |
| **External Coupling** | **Zero External References Invariant**: Strictly 0 references to `DNK_HUB` or absolute `/Users/...` paths (`verify_all.sh` Gate 1/5 fails closed if violated) | Can inspect `../DNK_OS_APP` via relative paths and export verified capabilities |
| **Self-Awareness** | **`core/self_awareness.py` (`SelfAwarenessEngine`)**: Live AST atlas, module contracts (`agent_owner`, `when_to_edit`), `recommend_edit_targets(goal)`, and SCONES learning loop | Uses `dnk_resolve_symbol`, `repo_map.py`, and Graphify across 7,000+ files |
| **First Agent** | **`core/orchestrator/thought_companion.py` (`FirstThoughtCompanionAgent`)**: Structures raw ideas into `ThoughtDAGGraph` + Role Capsules (`<=8` tools, `<=6000` tokens) + `xyflow` & Obsidian Canvas + `recommended_code_targets` | Full 14-worker Swarm (`dnk_swarm_parallel`, `dnk_triage_task`) |
| **Microkernel & API** | **6-Layer Modular Architecture**: `core/kernel.py` (FastMCP + CLI `status`, `thought`, `companion`, `atlas`, `locate`, `learn`) + `apps/api/main.py` REST Gateway | Production multi-router FastAPI gateway + 3 Core Workhorses (`dnk_shopify`, `dnk_media`, `dnk_distribution`) |

---

## 2. The 6-Layer Modular Architecture of `DNK_OS_APP` (Product v1)

`DNK_OS_APP` is NOT a passive staging folder from which files are merely drained into `DNK_HUB`. It is the **clean, standalone Product v1** engineered so any developer agent immediately understands the codebase, knows which exact files and lines to edit, and records architectural lessons back into cognitive memory:

1. **Layer 0 — Microkernel & FastMCP Host (`core/kernel.py`)**:
   - `FastMCPKernel`: unified entrypoint, Action Bus with HITL approval gates (`core/action_bus/approval.py`), MCP tools (`structure_thought_companion`, `locate_developer_targets`), and CLI (`status`, `thought`, `companion`, `atlas`, `locate`, `learn`, `codemap`, `prune`).
2. **Layer 1 — Self-Awareness & First Companion (`core/self_awareness.py`, `core/orchestrator/thought_companion.py`)**:
   - `SelfAwarenessEngine.build_live_atlas()`: dynamically parses live Python AST (`core/code_map.py`) and merges it with canonical module metadata (`layer`, `responsibility`, `agent_owner`, `when_to_edit`, `invariants`).
   - `SelfAwarenessEngine.recommend_edit_targets(developer_goal)`: accepts a natural-language developer task and returns a deterministic `target_file_whitelist` (top 4 modules) plus exact AST symbol names and line numbers.
   - `SelfAwarenessEngine.record_learning()` / `recall_learnings()`: persists refactoring and debugging lessons directly into `SconesMemoryStore` (`scones_observations` + `scones_episodic_logs`).
   - `FirstThoughtCompanionAgent`: converts raw user intent into an acyclic `ThoughtDAGGraph` (validated via Kahn's algorithm and SHA-256 context fingerprints), assigns bounded Role Capsules (`MAX_TOOLS_PER_CAPSULE = 8`, `MAX_STARTUP_TOKENS = 6000`), computes Tributary Causal Tree layout coordinates, exports dual canvases (`xyflow_canvas` + `obsidian_canvas`), and attaches `recommended_code_targets` to every node.
3. **Layer 2 — Thought Domain Core (`core/domain/dag_models.py`, `core/domain/thought_dsl.py`)**:
   - `ThoughtNode`, `Wire`, `ThoughtDAGGraph`, `detect_cycles_kahn`, `compute_upstream_fingerprint`.
4. **Layer 3 — Cognitive Memory SCONES (`core/memory/scones_store.py`)**:
   - 3-tier SQLite WAL persistence (`working_memory`, `scones_episodic_logs`, `scones_observations`).
5. **Layer 4 — Spatial Projection (`core/obsidian/json_canvas_builder.py`)**:
   - Bidirectional Obsidian JSON Canvas 1.0 (`.canvas`) serializer.
6. **Layer 5 — Product API Gateway (`apps/api/main.py`)**:
   - `GET /health`, `POST /api/v1/companion/structure`, `GET /api/v1/companion/capsules`, `GET /api/v1/system/atlas`, `POST /api/v1/system/locate`, `POST /api/v1/system/learn`.

---

## 3. Strict Verification & Hygiene Gates in `DNK_OS_APP` (`scripts/verify_all.sh`)

Before declaring any work in `../DNK_OS_APP` complete, run `bash ../DNK_OS_APP/scripts/verify_all.sh` and ensure all 5 gates pass (`Exit Code: 0`):

1. **Gate 1/5 — Zero Absolute Paths & Zero External Hub Leaks**:
   - Scans `core`, `apps`, `packages`, `services`, `scripts`, `tests`, `docs`, and `specs`.
   - Fails closed if any file contains `/Users/` or references the R&D repository name (`DNK_` + `HUB`).
2. **Gate 2/5 — Canonical 8-Root Directory Invariant**:
   - Only `apps`, `core`, `docs`, `packages`, `scripts`, `services`, `specs`, `tests` are permitted at top level. Never leave scratch folders (`task_forest/`, `artifacts/`) or unignored `.coverage` files in the root.
3. **Gate 3/5 — Documentation Standard Guardian (`scripts/system/doc_standard_guardian.py`)**:
   - Validates YAML frontmatter, MRH headers, Mandatory Dissent sections in ADRs (`## Mandatory Dissent`, `### 3 Flaws`, `### Boundary Conditions`, `### Skeptic Alternative`), zero secret patterns (`api_key = "..."`), and zero broken relative Markdown links.
4. **Gate 4/5 — Markdown Schema Gate (`scripts/verification/markdown_schema_gate.py`)**:
   - Validates all `.md` files across `docs/` and `specs/`.
5. **Gate 5/5 — Unit & Contract Test Suite (`pytest`)**:
   - Always check `import pytest` when using `@pytest.mark.asyncio` in async CLI/kernel tests (`tests/unit/test_self_aware_product_v1.py`).

---

## 4. Current State Drift & Operational Pitfalls in `DNK_OS_APP`

During physical repository audits of `../DNK_OS_APP`, be alert to three critical structural gaps:

1. **Git State Rot & Untracked Codebase Risk**:
   - `DNK_OS_APP` git history may be frozen (e.g. branch `dnk-mvp/feature/task-forest-obsidian` at Sep 2026 commit `e5b3f7a`).
   - Core directories (`apps/`, `core/`, `tests/`, `specs/01-07`, `scripts/`) may exist as untracked files without remote tracking.
   - **Critical Warning**: Never run `git clean -fd` or destructive branch checkouts in `DNK_OS_APP` without first checking `git status`, or untracked product modules will be lost permanently.
2. **Hollow Frontend Shell (`apps/web`)**:
   - While `WorldSotaThoughtCanvas.tsx` is present, `apps/web/` lacks `package.json`, `tsconfig.json`, Next.js 15 scaffolding, and `pnpm-lock.yaml`.
   - Before attempting `pnpm dev`, bootstrap the Next.js runtime per ADR-009.
3. **Absence of Local Dependency Manifests**:
   - `DNK_OS_APP` root lacks `pyproject.toml`, `requirements.txt`, or Dockerfiles. Runtimes depend on the fallback interpreter (`~/.dnk_runtime/venv`).
4. **Terminal CWD Persistence Pitfall**:
   - When inspecting `../DNK_OS_APP` via `cd ../DNK_OS_APP`, the shell working directory persists. Always explicitly reset `cd` back to repo root (`DNK_HUB`) before running relative path diffs or verify scripts, otherwise comparative commands compare the directory against itself.

---

## 5. Split-Brain Anti-Pattern & One-Way Two-Tier Export Guard (DEC-022)

### 5.1 The Split-Brain Anti-Pattern
When an engineering team attempts to maintain two active codebases (`DNK_HUB` for R&D and `DNK_OS_APP` for production) via manual code transfers, the following systemic failure inevitably occurs:
1. **Time-Freeze Drift**: The client repository freezes at an earlier milestone (e.g. v2.4.0 with early specs and ADR-001..012), while daily development, tests, and FastMCP servers continue evolving in the R&D hub (v2.8.0 with DEC-001..022, microkernel ADR-091, Canvas ADR-093).
2. **Reverse SSOT Illusion ("The Tail Wags the Dog")**: Because `DNK_OS_APP` was envisioned as the "clean target architecture", developers mistakenly assume its files are newer and consider refactoring the active Hub to match the App. Doing so would regress active architectural contracts (e.g. re-introducing deprecated patterns like `skeleton-theme` from ADR-011 over live Horizon v4.3+).

### 5.2 Mandatory Resolution & Consolidation Protocol (DEC-022)
1. **Presupposition Inversion & Date Audit**: Before altering either repo, execute a deterministic timestamp and commit audit across both trees (`git log -1`, `AGENTS.md` version comparison). Confirm which repo holds the true evolutionary frontline.
2. **One-Way Ingestion (App -> Hub Salvage)**: Extract any unique architectural assets authored directly in the App and assimilate them into canonical Hub paths:
   - Standalone specs (`specs/01`–`07`) ➔ `./docs/specs/`
   - Foundational ADRs (`docs/adr/ADR-001`..`012`) ➔ `./docs/adr/` (restoring broken Obsidian wikilinks)
   - Master templates (`Do not Delete - Example.md`, `Draft.md`) ➔ `./docs/templates/`
   - Task trees (`task_forest/*`) ➔ `./docs/notes/task_forest/`
   - Executable mind agents & AST atlas:
     - `core/orchestrator/thought_companion.py` ➔ `./core/orchestrator/thought_companion.py` (FirstThoughtCompanion & Kahn DAG)
     - `core/self_awareness.py` ➔ `./core/self_awareness.py` (SelfAwarenessEngine AST locator)
     - `core/obsidian/smart_linker.py` ➔ `./core/obsidian/smart_linker.py` (Obsidian wiki-linker)
     - `core/code_map.py` & `core/pruner.py` ➔ `./core/`
     - `core/ui/tokens.css` & `theme.ts` ➔ `./core/ui/`
   - Spatial Canvas & Whiteboards:
     - `apps/web/src/components/canvas/WorldSotaThoughtCanvas.tsx` ➔ `./apps/web/components/canvas/WorldSotaThoughtCanvas.tsx`
     - Visual thought boards (`my Notes.excalidraw.md`, `whiteboards/*`) ➔ `./docs/diagrams/whiteboards/`
   - Post-Ingestion Verification Gate:
     - Compile all ingested Python files: `python3 -m py_compile core/*.py core/*/*.py`
     - Run regression tests: `pytest tests/core/`
     - Confirm 3-Tier Chassis integrity: Backend (`apps/api` :8000), Frontend (`apps/web` :3000), Services (`services/dnk_*`)
3. **Strict One-Way Export Packaging**:
   - Never write or edit production code manually inside `../DNK_OS_APP`.
   - `DNK_HUB` is the sole Single Source of Truth (SSOT).
   - `DNK_OS_APP` is strictly a generated distribution artifact compiled via automated export:
     ```bash
     python3 scripts/export_standalone_app.py ../DNK_OS_APP
     ```
   - Run verification in `DNK_HUB` (`pytest`, `verify_all.sh`) before releasing any standalone package.

