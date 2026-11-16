<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/mvr_core_kickoff_and_action_bus_sandbox_bridge_protocol.md"
purpose: "MVR Core Implementation Kickoff Protocol: Bridging FastAPI Headless Runtime, Agent Action Bus & Plugin Sandbox Runner"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-12"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🚀 MVR Core Kickoff & Action Bus Sandbox Bridge Protocol (IMPLEMENTATION-001)

## 1. Executive Context & Architectural Shift
Transitioning from frozen specifications (`PHASE-001`) to the first code-modifying implementation slice (`IMPLEMENTATION-001`) requires a strict, fail-safe bridging mechanism.
In DNK OS, the core objective of the first implementation slice is to bring up a headless **FastAPI service**, connect the asynchronous in-memory **Agent Action Bus (AAB)**, and execute the first live action through the isolated **Plugin Sandbox Runner** (`PluginSandboxRunner`).

```text
[Client / Swarm Request]
           │
           ▼ (HTTP POST /api/v1/mvr/tasks/dispatch)
┌────────────────────────────────────────────────────────┐
│ FastAPI Headless Layer (mvr_core_router.py)            │
│  - Request validation via Pydantic v2 ActionTask       │
├────────────────────────────────────────────────────────┤
│ Agent Action Bus Core (core/action_bus/bus.py)         │
│  - In-memory event publish (TASK_QUEUED)               │
│  - Policy check via validate_sandbox_policy            │
├────────────────────────────────────────────────────────┤
│ Plugin Sandbox Runner (core/plugins/sandbox_runner.py) │
│  - Isolated temp workspace execution                   │
│  - Captures stdout, stderr, exit_code, timing          │
├────────────────────────────────────────────────────────┤
│ Audit & Event History (AuditLog / EventStore)          │
│  - TASK_COMPLETED / TASK_FAILED event published        │
│  - Returns deterministic ActionExecutionResponse       │
└────────────────────────────────────────────────────────┘
```

---

## 2. The 4 Golden Rules of the Implementation Kickoff

### Rule 1: Zero Direct Execution (Sandboxed Execution Only)
Any code dispatched via the Agent Action Bus that runs plugin or worker actions MUST execute through `PluginSandboxRunner` inside a designated temporary workspace. No uncontained `subprocess.run` or `eval()` outside the sandbox.

### Rule 2: Strict Headless Separation (Zero UI Leaks)
Phase 1 focuses entirely on the backend engine and headless API contracts. Spatial UI and Canvas frontend components (`visual_shell/`, React components) are strictly quarantined until Phase 2.

### Rule 3: Dual-Optics Verification (CLI & Pytest TestClient)
Every implementation slice must provide two symmetrical interfaces for verification:
1. **Machine/Automated**: Pytest suite using Starlette/FastAPI `TestClient` (`tests/mvr/test_mvr_core_kickoff.py`).
2. **Human Founder**: Deterministic CLI runner (`scripts/system/mvr_core_runner.py`) supporting `--health`, `--dispatch-sample`, and `--json`.

### Rule 4: Canonical Task Spec Storage (`docs/tasks/`)
Task formulations authored by the Mentor/Architect are committed to `docs/tasks/TASK-DNK-MVR-<DATE>-<NUM>_<slug>.md` with machine-readable headers (MRH), explicit target file whitelists, and 4 sequential MASE slices ($\le 25$ tool calls per turn).

---

## 3. Mandatory MASE Slicing Pattern for MVR Core
To prevent context saturation and 90/90 tool budget exhaustion, implementation is partitioned into 4 atomic phases:
1. **Slice 1: Data Models & Action Bus Engine** (`core/action_bus/models.py`, `core/action_bus/bus.py`).
2. **Slice 2: FastAPI Router & Main App Mounting** (`apps/api/routers/mvr_core_router.py`, `apps/api/main.py`).
3. **Slice 3: CLI Runner & TestClient Integration Suite** (`scripts/system/mvr_core_runner.py`, `tests/mvr/test_mvr_core_kickoff.py`).
4. **Slice 4: Adversarial Audit, Evidence & Obsidian Knowledge Harvesting** (`docs/notes/122_...`, `docs/audit/..._evidence.json`).

---

## 4. Cross-References
- Canonical Task Spec: `docs/tasks/TASK-DNK-MVR-20260912-001_mvr_core_kickoff.md`
- Bulletproof Task Standard: `references/bulletproof_task_formulation_and_v3_spec_protocol.md`
- Phase Kickoff Handoff: `references/mvr_phase_handoff_and_zero_mutation_kickoff_protocol.md`
