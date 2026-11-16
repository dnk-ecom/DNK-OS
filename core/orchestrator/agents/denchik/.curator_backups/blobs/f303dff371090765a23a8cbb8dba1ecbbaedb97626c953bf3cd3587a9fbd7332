# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/ephemeral_docker_sandbox_and_cgroups_v2_isolation_protocol.md"
# purpose: "Canonical Ephemeral Docker Sandbox Execution, Cgroups v2 Resource Governance, and Dual-Mode Fallback Protocol for Swarm Agent Isolation (SWARM-008)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Ephemeral Docker Sandbox Runner & Cgroups v2 Governance Protocol (SWARM-008)

This protocol defines the production invariants and implementation mechanics for running untrusted agent-generated code (Python, Bash, Node.js) inside locked-down, ephemeral Docker containers with cgroups v2 resource governance and zero-trust containment.

---

## 1. Security & Containment Invariants

| Security Dimension | Parameter / Flag | Invariant Behavior |
| :--- | :--- | :--- |
| **Network Isolation** | `--network none` | Complete default-deny. Outbound/inbound network blocked. |
| **User Privileges** | `--user 10001:10001` | Non-root execution (`dnkrunner`). Never run as root. |
| **Filesystem Safety** | `--read-only` | Root filesystem mounted strictly immutable. |
| **Capabilities** | `--cap-drop ALL` | Drops all Linux capabilities (prevents raw sockets, chroot, ptrace). |
| **Privilege Escalation**| `--security-opt no-new-privileges:true` | Prevents setuid/setgid privilege acquisition. |
| **Memory Isolation** | `tmpfs /tmp`, `tmpfs /app/workspace` | Writable scratch space in RAM only; `noexec,nosuid,nodev` on `/tmp`. |

---

## 2. Cgroups v2 Resource Governance

- **Memory Cap**: `--memory 512m --memory-swap 512m` (prevents swap thrashing and OOM impact on host).
- **CPU Quota**: `--cpus 1.0` or `--cpu-period 100000 --cpu-quota 100000` (caps compute to 1 vCPU equivalent).
- **Process Limit**: `--pids-limit 64` (instantly neutralizes fork-bomb vectors).
- **Disk Scratchpad**: `tmpfs` mounts capped at 128MB (`/tmp`) and 256MB (`/app/workspace`).

---

## 3. Ephemeral Lifecycle & Timeout Watchdog

1. **Unique Ephemeral Naming**:
   - Container name formatted as `dnk-sbx-<uuid4().hex[:10]>`.
   - Never reuse container names across runs.
2. **Supervisor Watchdog**:
   - Monitored asynchronously via `asyncio.wait_for(coro, timeout=config.timeout_seconds)`.
   - On timeout (`TimeoutError`): supervisor immediately schedules `docker rm -f <container_name>` via a detached subprocess to ensure zero container leaks.
   - Result mapped to status `TIMEOUT` with exit code `124`.

---

## 4. Dual-Mode Fallback & Daemon Hang Protection

When Docker is unavailable (daemon not running, socket missing, or in constrained test environments):
1. **Non-Blocking Daemon Probing (Critical Pitfall)**:
   - **Never** use synchronous `os.system("docker info")` or raw untimeouted checks — an unresponsive Docker socket or sleeping desktop daemon will permanently freeze the worker process.
   - **Always** bound daemon checks with a hard timeout:
     ```python
     try:
         res = subprocess.run([self.docker_bin, "info"], capture_output=True, timeout=2.0)
         return res.returncode == 0
     except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
         return False
     ```
2. **Graceful Subprocess Fallback**:
   - Executes code in isolated temporary directory (`tempfile.TemporaryDirectory`).
   - Cleanses environment variables (strips secrets, tokens, credentials).
   - Enforces asynchronous timeout watchdog and terminates child process tree with `terminate()` and `kill()` after grace period.
   - Sets result `container_id` to `local-subprocess-fallback`.

---

## 5. Async Testing & ASGITransport Invariant

When running integration tests against FastAPI routers that launch background simulations or long-running ActionBus tasks:
- **Never use** synchronous `starlette.testclient.TestClient` inside `async def` tests with background loops — it blocks the main thread and starves background workers.
- **Always use** `httpx.AsyncClient` with `ASGITransport`:
  ```python
  from httpx import ASGITransport, AsyncClient

  async with AsyncClient(
      transport=ASGITransport(app=app), base_url="http://test"
  ) as client:
      resp = await client.post("/api/v1/mvr/simulation/launch", json=payload)
      assert resp.status_code == 200
  ```

---

## 6. Event-Driven HITL Bridge & SSE Routing Invariants

1. **Zero-CPU HITL Waiters**:
   - Never implement human approval polling with `while True: await asyncio.sleep(...)`.
   - Use `asyncio.Event` registered per pending `action_id`. Resolving the approval (`APPROVED`/`REJECTED`) sets the event, instantly awakening the waiting agent task.
2. **Dual-Route SSE Streaming**:
   - Fast-path web UIs and background clients may request `/api/v1/mvr/events/sse` or `/api/v1/mvr/events/stream`. Always register both routes pointing to the same event generator.
