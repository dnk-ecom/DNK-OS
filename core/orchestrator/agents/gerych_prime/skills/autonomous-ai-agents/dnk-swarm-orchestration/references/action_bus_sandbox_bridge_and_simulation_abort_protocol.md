<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/action_bus_sandbox_bridge_and_simulation_abort_protocol.md"
purpose: "Phase 9 Protocol: ActionBus DockerSandbox Integration, Cancellation Lifecycle, and EventBroadcaster Verification"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-13"
author: "Antigravity (Mentor) & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🚀 ActionBus DockerSandbox Bridge & Simulation Abort Protocol (PHASE-009)

## 1. Architectural Scope & Lifecycle
In DNK OS Phase 9, code dispatched across the swarm moves through an isolated DockerSandbox container pool while exposing real-time cancellation (Abort) and telemetry (RAM/Duration) down to the Canvas UI.

```text
[Frontend Canvas / Operator]
       │
       ├── (POST /api/v1/mvr/simulation/{id}/launch) ──► Background asyncio.Task
       │                                                         │
       │                                                         ▼
       │                                              [AgentActionBus]
       │                                                         │
       │                                      execute_sandbox(code, lang, timeout)
       │                                                         ▼
       │                                              [DockerSandboxRunner]
       │                                                         │
       │                                                         ▼
       │                                            SANDBOX_EXECUTION_COMPLETED
       │                                            (ram_bytes, duration_ms)
       │
       └── (POST /api/v1/mvr/simulation/{id}/abort)
               │
               ▼
       [Active Task Registry] ──► task.cancel()
                                        │
                                        ▼
                             asyncio.CancelledError
                                        │
                                        ▼
                               SIMULATION_ABORTED
                         (sets node status -> ABORTED)
```

---

## 2. Mandatory Invariants

### 1. ActionBus Sandbox Bridge
- `AgentActionBus.execute_sandbox(code, language, timeout, task_id)` must encapsulate the container execution lifecycle.
- When `docker_sandbox_runner` is configured, it runs `runner.run(code, language=language, timeout_seconds=timeout)`.
- On completion, it broadcasts `BusEventType.SANDBOX_EXECUTION_COMPLETED` with payload containing:
  - `status`: execution status string (`completed`, `timeout`, `oom_killed`, `failed`).
  - `exit_code`: container process exit code.
  - `ram_bytes`: memory consumption in bytes.
  - `duration_ms`: execution time in milliseconds.

### 2. Simulation Abort Endpoint & Task Tracking
- The router (`apps/api/routers/mvr_core_router.py`) maintains two in-memory registries guarded during simulation runs:
  - `_ACTIVE_SIMULATION_TASKS: Dict[str, asyncio.Task]`
  - `_ACTIVE_SIMULATION_NODES: Dict[str, str]` (maps simulation ID to current active node ID)
- `POST /api/v1/mvr/simulation/{simulation_id}/abort`:
  1. Checks if `simulation_id` exists in `_ACTIVE_SIMULATION_TASKS` and not `done()`.
  2. Calls `task.cancel()`.
  3. Broadcasts SSE event `SIMULATION_ABORTED` targeting the currently active node with status `ABORTED`.
  4. Always returns HTTP 200 with `{ "status": "aborted", "simulation_id": simulation_id }`.

### 3. EventBroadcaster Verification in Unit Tests
- `EventBroadcaster` uses a non-blocking bounded ring buffer (`collections.deque(maxlen=buffer_size)`).
- **Pitfall**: `broadcaster` does NOT expose `add_subscriber` or callback hooks.
- **Pattern**: Query `broadcaster.get_recent_envelopes(limit=N)` to inspect broadcast history deterministically in unit and integration tests:
  ```python
  recent = [env.event_type for env in test_bus.broadcaster.get_recent_envelopes(limit=50)]
  assert BusEventType.SIMULATION_ABORTED.value in recent
  ```

### 4. ReactFlow Custom Node ReactNode Typing
- When rendering custom node data with dynamic keys (`MvrTaskNodeData`), avoid directly inserting possibly `unknown` fields in JSX.
- Type telemetry fields explicitly (`memoryMb?: number`, `durationMs?: number`) or wrap them (`{nodeData.memoryMb ?? 0}`) with explicit typing in the node component props to satisfy `tsc` / LSP diagnostics.
