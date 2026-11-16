# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/neural_mesh_topology_and_pgid_process_isolation.md"
# purpose: "Neural Mesh Declarative Swarm Topology, Fallback Rings, and PGID Subagent Process Isolation Protocol"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-13"
# author: "Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🧠 Neural Mesh Topology & PGID Process Group Isolation Protocol

Assimilated from high-leverage architectural patterns in `imMamdouhaboammar/delegate-team` (MIT License), OpenTelemetry, and Celery for hardening DNK OS Multi-Agent Swarm execution.

---

## 1. Declarative Swarm Topology (Neural Mesh Pattern)

### 1.1 The Problem
Hardcoded routing tables and ad-hoc dispatcher fallbacks create hidden coupling, brittle error handling when model quotas are exhausted, and opacity in cross-agent handoffs.

### 1.2 The Mesh Invariant
Represent swarm topology as a single, auditable declarative graph (`core/orchestrator/swarm_mesh.json`) managed by runtime engine `core/orchestrator/swarm_mesh.py`:
- **Neurons**: 14 Swarm components (`gerych_prime`, `gerych_builder`, `gerych_auditor`, `dnk_dev_fullstack`, `dnk_shopify`, `dnk_scones_memory`, etc.).
- **Synapses**: Typed, directed edges:
  - `ROUTES_TO`: Normal routing slice dispatch (e.g. `backend` -> `dnk_dev_fullstack`, `liquid` -> `dnk_shopify`).
  - `FALLBACKS_TO`: Dynamic failover ring on API quota exhaustion or runtime crash (e.g. `dnk_dev_fullstack` -> `gerych_builder`).
  - `GATE_BEFORE`: Strict quality or adversarial gate before mutation/commit (e.g. `pre_commit` -> `gerych_auditor`).
  - `MEMORY_OF`: Cognitive memory sink (e.g. `task_finish` -> `dnk_scones_memory`).
  - `EMITS_TO`: Audit event broadcast (e.g. `all` -> `unified_trace_bus`).

### 1.3 Schema Example
```json
{
  "version": "1.0.0",
  "neurons": {
    "gerych_prime": { "role": "orchestrator", "description": "Chief Swarm Manager" },
    "dnk_dev_fullstack": { "role": "worker", "domain": "backend" },
    "gerych_auditor": { "role": "gate", "domain": "security_audit" },
    "dnk_scones_memory": { "role": "memory", "domain": "knowledge_retrieval" }
  },
  "synapses": [
    { "from": "gerych_prime", "to": "dnk_dev_fullstack", "type": "ROUTES_TO", "domain": "backend" },
    { "from": "dnk_dev_fullstack", "to": "gerych_builder", "type": "FALLBACKS_TO", "reason": "worker_timeout" },
    { "from": "dnk_dev_fullstack", "to": "gerych_auditor", "type": "GATE_BEFORE", "action": "pre_commit" },
    { "from": "dnk_dev_fullstack", "to": "dnk_scones_memory", "type": "MEMORY_OF", "action": "persist_lesson" }
  ]
}
```

### 1.4 Runtime Engine API (`SwarmNeuralMesh`)
```python
from core.orchestrator.swarm_mesh import swarm_neural_mesh

# Validate mesh integrity
is_valid, errors = swarm_neural_mesh.validate()

# Route a task based on domain
assigned_agent = swarm_neural_mesh.route_task(domain="backend", complexity=2)

# Retrieve fallbacks if assigned agent is unavailable
fallbacks = swarm_neural_mesh.get_fallbacks(agent_id="dnk_dev_fullstack")

# Retrieve required quality gates before an action
gates = swarm_neural_mesh.get_gates(agent_id="dnk_dev_fullstack", action="pre_commit")
```

---

## 2. Process-Group Isolation & Watchdog Cleanup (PGID Hygiene)

### 2.1 The Zombie Process Hazard
When background subagents, test runners, or compilation tools spawn child processes (e.g. Node dev servers, Python daemons, Vite builders) and are terminated via standard `proc.terminate()` or `proc.kill()`, only the root PID is killed. The child processes become orphaned zombies, holding open TCP ports, locks, and GPU/RAM memory.

### 2.2 The PGID Isolation Invariant
Every autonomous worker or subprocess runner MUST be isolated into its own session process group via `start_new_session=True` (POSIX `setsid()`).

### 2.3 Implementation Contract (`ProcessGroupManager`)
Located at `core/orchestrator/process_group_manager.py`:
- **Method Signature**:
  ```python
  ProcessGroupManager.run_in_group(
      cmd: list[str],
      cwd: Optional[Path | str] = None,
      env: Optional[dict[str, str]] = None,
      timeout: Optional[float] = None,
      task_id: Optional[str] = None,
      state_file_path: Optional[Path | str] = None,
      max_output_chars: int = 2_000_000,
  ) -> ProcessRunResult
  ```
- **State File Tracking (`boulder` pattern)**:
  When `state_file_path` is passed, the manager writes atomic JSON tracking:
  ```json
  {
    "task_id": "task_123",
    "pid": 45120,
    "pgid": 45120,
    "status": "running",
    "start_time": 1773400000.0,
    "command": ["pytest", "tests/"]
  }
  ```
- **Guaranteed Termination Protocol**:
  1. `SIGTERM` broadcast to entire process group (`-pgid` on POSIX).
  2. Non-blocking polling with grace window (default 3.0s - 5.0s).
  3. Escalation to `SIGKILL` on `-pgid` if processes linger.
  4. On Windows: fall back to `taskkill /F /T /PID <pid>`.

---

## 3. Unified Trace Bus & Event Observer (`SynapseEvent`)

All cross-agent transitions emit structured, replayable trace events:
```json
{
  "timestamp": "2026-09-13T14:30:00.123456+00:00",
  "event_id": "syn_1773400000123_00000a_4f1b",
  "synapse_type": "ROUTES_TO",
  "source": "gerych_prime",
  "target": "dnk_dev_fullstack",
  "action": "dispatch",
  "status": "dispatched",
  "payload": { "task_description": "Generate FastAPI schema" },
  "correlation_id": "corr_abc123"
}
```

### 3.1 High-Concurrency Monotonic ID Invariant
Under high-velocity parallelism (e.g., 50 concurrent subagent dispatches), millisecond timestamps collide.
Use a triple-composite ID generator:
```python
event_id = f"syn_{int(time.time() * 1000)}_{next(self._event_counter):06x}_{uuid.uuid4().hex[:4]}"
```
This guarantees chronological sortability, $O(1)$ atomicity, and zero collision risk across threads.

### 3.2 Bounded Ring Buffer & Thread Safety
`trace_bus` is backed by `collections.deque(maxlen=1000)` synchronized with `threading.RLock()`.
- Thread-safe emission and queries.
- Bounded memory footprint (no memory leaks during long orchestrator lifecycles).

### 3.3 Reactive Observer Subscriptions
External observers (Visual Canvas, Prometheus/OpenTelemetry bridges, Live UI) register callbacks via:
```python
mesh.subscribe(callback_fn)
mesh.unsubscribe(callback_fn)
```
Callbacks are isolated in safe execution blocks (`try...except`) so subscriber errors never fail the core swarm routing.

---

## 4. Common Pitfalls & Operational Traps

### 4.1 Parameter Name Mismatch in `run_in_group`
- **Pitfall**: Calling `ProcessGroupManager.run_in_group(cmd, state_file=path)` raises `TypeError: unexpected keyword argument 'state_file'`.
- **Rule**: The canonical argument name is `state_file_path`. Always verify method signatures in `core/orchestrator/process_group_manager.py`.

### 4.2 Test Suite Directory-Wide Pytest Timeout (Exit 124)
- **Pitfall**: Running `pytest tests/core/` without filtering executes hundreds of integration tests, hitting the execution timeout limit.
- **Rule**: Always run targeted pytest suites during atomic slice verification:
  `pytest tests/core/test_process_group_manager.py tests/core/test_swarm_mesh.py -v`.

### 4.3 macOS Darwin `PermissionError: [Errno 1] Operation not permitted` on PGID Kill
- **Pitfall**: On macOS Darwin, sending `SIGKILL` or signal 0 via `os.killpg(pgid, ...)` to a process group whose leader has already exited or been reaped by the kernel can raise `PermissionError: [Errno 1] Operation not permitted` instead of `ProcessLookupError`.
- **Rule**: In POSIX process group cleanup loops, always handle both `(ProcessLookupError, PermissionError)` when checking process liveness (`os.killpg(pgid, 0)`) or issuing escalation signals (`SIGKILL`), treating them as successful process termination.

### 4.4 Mandatory `cwd` Argument in `ProcessGroupManager.run_in_group`
- **Pitfall**: Omitting `cwd` raises `TypeError: run_in_group() missing 1 required positional argument: 'cwd'`.
- **Rule**: Always pass explicit `cwd` (e.g. `cwd="."` or target repo/subagent directory) when invoking `ProcessGroupManager.run_in_group(...)`.

### 4.5 Non-Existent Executable Crashing Subprocess Runner (POSIX 127)
- **Pitfall**: Spawning `subprocess.Popen` without trapping `FileNotFoundError` or `PermissionError` causes the entire parent orchestrator to throw an uncaught exception when a tool or binary is missing.
- **Rule**: `run_in_group` catches `(FileNotFoundError, PermissionError, OSError)` and returns a structured `ProcessRunResult(pid=-1, returncode=127, stop_reason="file_not_found")` or `returncode=126`, ensuring the orchestrator gracefully handles missing dependencies.

### 4.6 Unbounded Memory Exhaustion on Runaway Subprocesses (OOM Deadlock)
- **Pitfall**: A rogue subagent in an infinite loop printing logging output can produce gigabytes of text into `proc.communicate()`, causing host OS OOM kills.
- **Rule**: Always enforce `max_output_chars` truncation (default 2,000,000 chars) on both stdout and stderr in `ProcessGroupManager`.

### 4.7 Multi-Worker Dispatch ID Collision Trap (`SwarmCoordinator`)
- **Pitfall**: Generating dispatch IDs using integer second timestamps (e.g. `f"disp_{to_agent}_{int(timestamp())}"`) causes duplicate IDs and state overwrites when parallel workers (`dnk_swarm_parallel`) dispatch multiple tasks within the same second.
- **Rule**: Always include millisecond precision and UUID entropy tail: `f"disp_{to_agent}_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:4]}"`.

### 4.8 Subprocess Grace Period Polling vs Instant SIGKILL Escalation (`ProcessGroupManager`)
- **Pitfall**: Abruptly sending `SIGKILL` without giving subprocesses a chance to flush buffers or release locks causes corrupt WAL files and incomplete socket shutdowns; conversely, blocking `proc.wait(timeout)` without polling process group liveness risks hanging the orchestrator.
- **Rule**: Send `SIGTERM` to `-pgid`, execute a non-blocking polling loop (`proc.poll()` with small sleeps like 0.1s up to the grace period), verify group liveness via `os.killpg(pgid, 0)` catching `(ProcessLookupError, PermissionError)`, and only escalate to `SIGKILL` on `-pgid` if processes remain alive after the grace period.
