# Runtime Migration Mapping, MVR Formulation & Core Extraction Protocol

## Overview

This reference provides the canonical protocol for auditing, classifying, and migrating the autonomous agent core runtime from a legacy or monolithic workspace into a clean standalone repository (e.g. `DNK_HUB`), ensuring zero disruption, zero data loss, and zero-waste phased execution.

---

## 1. Strict Read-Only Audit Invariants

During migration audit and mapping:
- **Zero-Mutation Enforcement**: The audit phase must run in strict read-only mode. No code, configuration, or structural renaming may take place until the migration map is signed off.
- **Evidence-First Classification**:
  - `PROVEN`: Component has direct, passing automated tests (`pytest`) or validated executable CLI runs in the repository.
  - `PARTIAL`: Component is partially functional or tested, but carries unmitigated risks (e.g. hardcoded paths, unverified edge cases, or external infrastructure coupling).
  - `DOCUMENTED_ONLY`: Specification, markdown, or interface exists, but automated verification suites are missing.
  - `UNKNOWN`: Execution status or testability cannot be confirmed from repository artifacts.
- **Migration Decision Taxonomy**:
  - `ADOPT`: Component is verified, decoupled, and ready to move verbatim into the target runtime.
  - `ADAPT`: Component must be refactored before/during transfer (e.g. removing absolute paths `/Users/...`, removing cloud-specific coupling, or abstracting provider tokens).
  - `REFERENCE`: Component remains in the host repository as an external service or legacy client; only its public schema/contract is imported.
  - `QUARANTINE`: Component is tightly coupled to experimental code or heavyweight external infrastructure (e.g. live database clusters); do not move until decoupling prerequisites are met.

---

## 2. Minimum Viable Runtime (MVR) Formulation

The Minimum Viable Runtime defines the smallest self-contained subset of modules required for the agent to boot, triage tasks, execute tools safely, and generate verified proof of completion.

### Mandatory MVR Modules
1. **Task Contract & Specification**:
   - Canonical task template (`docs/templates/GERYCH_TASK_TEMPLATE.md`)
   - Complexity classifier & triage (`core/orchestrator/task_triage.py`)
   - Mandatory Atomic Slice Execution (`core/orchestrator/zero_waste_slicer.py`, `scripts/system/zero_waste_runner.py`)
2. **Process Guard & Runtime Hooks**:
   - Launcher entrypoint (`scripts/system/gerych.sh`)
   - CLI harness abstraction (`core/hermes_runtime.py`)
   - Pre-tool & Post-tool security hooks (`scripts/system/hermes_pre_tool_hook.py`, `scripts/system/hermes_post_tool_hook.py`)
   - Process watchdog (`scripts/system/process_guard.py`)
3. **Primary Agent Definition**:
   - Declarative agent card & soul (`agent_card.yaml`, `SOUL.md`)
   - Profile configuration (`config.yaml`)
   - Long-term memory anchor (`memories/MEMORY.md`)
   - Dynamic prompt synthesizer (`core/orchestrator/adaptive_prompt.py`)
4. **Tool Security & Execution Pipeline**:
   - Central tool registry (`core/orchestrator/tool_registry.py`)
   - MCP Slim Guard token filter (`core/orchestrator/mcp_slim_guard.py`)
   - 5-stage tool guard pipeline (`core/security/tool_guard_pipeline.py`)
   - Tool executor & alias normalizer (`core/orchestrator/tool_executor.py`, `core/orchestrator/tool_aliases.py`)
5. **Quality & Completion Verification**:
   - Master quality gate script (`scripts/verify_all.sh`)
   - Architecture & cycle guard (`scripts/system/architecture_and_cycle_guard.py`)
   - Deterministic blast radius analyzer (`scripts/system/blast_radius_analyzer.py`)
   - Git commit physical guard (`core/guards/completion_gate.py`)
   - Evidence generator (`scripts/system/generate_evidence.py`, `core/orchestrator/evidence_planner.py`)

### Invariant: Zero External Database Coupling
The MVR must operate 100% offline and standalone:
- Primary cognitive and operational memory must rely on local SQLite (`UnifiedMemoryBroker`), local JSON files (SCONES L1-L2), and markdown notes (Obsidian).
- External database engines (e.g. PostgreSQL, `pgvector`, Redis) must remain optional adapters or placed in quarantine until offline mock fallbacks are available.

---

## 3. Phased Sliced Extraction Sequencing (8 Slices)

To avoid big-bang refactoring failures, core runtime extraction follows an 8-stage topological sequence. Each slice is an atomic unit verified by targeted tests:

```
[Slice 1: Quality Foundation] ───► [Slice 2: Tool Security Pipeline]
               │                                   │
               ▼                                   ▼
    [Slice 3: TaskDNA & MASE] ───────► [Slice 4: Runtime & Hooks]
               │                                   │
               ▼                                   ▼
    [Slice 5: Agent & Prompts] ──────► [Slice 6: Memory Core]
               │                                   │
               ▼                                   ▼
    [Slice 7: Swarm Control] ────────► [Slice 8: Audit & Evidence]
```

1. **SLICE-01: Quality & Pre-Flight Foundation**:
   - *Target*: `verify_all.sh`, `completion_gate.py`, `architecture_and_cycle_guard.py`, `blast_radius_analyzer.py`.
   - *Verification*: `pytest tests/guards/test_completion_gate.py && pytest tests/test_architecture_guard_and_blast_radius.py`.
   - *Rollback*: Reset target directory; quality scripts are stateless.
2. **SLICE-02: Capability & Tool Security Pipeline**:
   - *Target*: `tool_registry.py`, `tool_guard_pipeline.py`, `mcp_slim_guard.py`, `tool_executor.py`.
   - *Verification*: `pytest tests/harness/test_tool_guard_pipeline.py tests/core/test_mcp_slim_guard.py tests/core/test_lazy_tool_loader.py`.
   - *Rollback*: Revert tool registry; fall back to static tool manifest.
3. **SLICE-03: TaskDNA & MASE Engine**:
   - *Target*: `core/task_forest/`, `task_triage.py`, `zero_waste_slicer.py`, `zero_waste_runner.py`.
   - *Verification*: `pytest tests/core/test_task_triage.py tests/core/test_zero_waste_slicer.py tests/core/test_task_forest.py`.
   - *Rollback*: Revert TaskForest tree changes.
4. **SLICE-04: Gerych Runtime & Process Guard**:
   - *Target*: `gerych.sh`, `hermes_runtime.py`, `hermes_pre_tool_hook.py`, `hermes_post_tool_hook.py`, `process_guard.py`.
   - *Verification*: `pytest tests/staging/test_hermes_v0210_compatibility.py tests/verification/test_sentinel_circuit_breaker.py`.
   - *Rollback*: Restore shell launcher and hook symlinks.
5. **SLICE-05: Primary Agent & Prompt System**:
   - *Target*: `gerych_prime` specs (`agent_card.yaml`, `SOUL.md`, `config.yaml`, `MEMORY.md`), `adaptive_prompt.py`, `prompt_ship_gate.py`, `skills/`.
   - *Verification*: `pytest tests/core/test_adaptive_prompt.py && hermes-agent config validate`.
   - *Rollback*: Revert prompt template files.
6. **SLICE-06: Multi-Tier Memory Core**:
   - *Target*: `unified_memory_broker.py`, `scones_*.py`, `memory_manager.py`, `obsidian_vault_sync.py`.
   - *Verification*: `pytest tests/core/test_unified_memory_broker.py tests/core/test_scones_expect.py tests/core/test_obsidian_vault_sync.py`.
   - *Rollback*: Remove migrated sqlite/json databases.
7. **SLICE-07: Swarm Control Plane & Core Swarm**:
   - *Target*: `control_plane.py`, `swarm_engine.py`, `swarm_director.py`, `subagent_sandbox.py`, builder/researcher/auditor cards.
   - *Verification*: `pytest tests/test_swarm_control_plane.py tests/verification/test_subagent_sandbox_handshake.py`.
   - *Rollback*: Fall back to single-agent execution mode.
8. **SLICE-08: Audit, Sentinel & Evidence Generation**:
   - *Target*: `adversarial_review.py`, `session_sentinel.py`, `generate_evidence.py`, `evidence_planner.py`.
   - *Verification*: `pytest tests/verification/test_adversarial_review.py tests/verification/test_session_sentinel.py`.
   - *Rollback*: Disable pre-commit adversarial gate check.

---

## 4. Quarantine List ("Do Not Move Yet")

Identify components that pose high blast-radius risks during extraction:
- **Presentation & Web Coupling**:
  - `core/orchestrator/visual_canvas_control.py` (coupled to `CanvasEngine` and WebSocket state).
  - `apps/api/routers/task_forest_router.py` (FastAPI HTTP routing).
- **External Heavyweight Stores**:
  - `core/memory/pgvector_store.py` (requires active PostgreSQL server; failed tests without pgvector).
  - `core/memory/tencent_memory_provider.py` (untested cloud infrastructure).
- **Ephemeral State & Blobs**:
  - `core/orchestrator/agents/gerych_prime/state.db` (ephemeral SQLite database blob; re-created at runtime).
  - `core/orchestrator/agents/*/auth.json` (sensitive tokens; never commit).
  - Runtime cache and audio folders (`cache/`, `audio_cache/`, `logs/`).
- **Reverse Dependency Leaks**:
  - `core/orchestrator/swarm_coordinator.py` importing `apps.api.logging.structured_logger` (must be decoupled to standard library logging before migration).

---

## 5. Compatibility Risk Gates

| Risk Category | Hazard Description | Mitigation Gate |
|---|---|---|
| **Python Toolchain** | Host OS mismatch (e.g. system Python 3.14 vs `.venv` Python 3.12, PEP 668 restrictions). | Enforce execution via explicit `./.venv/bin/python3` and virtual environment SSOT in `verify_all.sh`. |
| **Provider Auth** | Google Cloud / Vertex AI OAuth token expiration causing silent LLM failures. | Background token refresh daemon (`scripts/system/gcp_token_daemon.py`) and pre-flight token check. |
| **Path Hygiene** | Hardcoded `/Users/...` or `/home/...` absolute paths break portability across machines. | Pre-tool hook circuit breaker (`hermes_pre_tool_hook.py`) and AST static sanitizer in pre-commit. |
| **Database Lock-in** | Core services failing to boot without external DB connectivity. | SQLite/JSON local fallback default in `UnifiedMemoryBroker`. |
| **Secret Leakage** | Credentials accidentally copied with agent home directories. | Strict `.gitignore` blocking `auth.json`, `.env`, and secret scanning pre-commit hooks. |
| **Reverse Imports** | Core importing presentation or application layers (`apps/`). | Architecture cycle guard (`scripts/system/architecture_and_cycle_guard.py`) blocking upper-tier imports. |

---

## 6. Multi-Format Output Contract

Whenever performing an architectural migration audit, generate the following 3 complementary artifacts:
1. `docs/audit/<NAME>_v<VERSION>.md`: Human-readable engineering specification with 11-column component tables, risk analysis, and migration steps.
2. `docs/audit/<NAME>_v<VERSION>.yaml`: Canonical machine-readable SSOT containing complete component metadata, dependencies, test assertions, and slice definitions.
3. `docs/notes/<ID>_<name>.md`: Permanent Obsidian Vault knowledge note containing MRH headers, YAML frontmatter, executive summary, and bidirectional `[[wikilinks]]`.
