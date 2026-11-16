# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/living_swarm_simulation_and_async_hitl_suspension_protocol.md"
# purpose: "Canonical Protocol for Living Swarm Interactive Simulation, Async HITL Suspension and ASGI E2E Testing"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Living Swarm Simulation, Async HITL Gate Suspension & ASGI E2E Testing Protocol

## 1. Context & Architectural Challenge
In multi-agent interactive simulations (e.g. Living Swarm Playgrounds):
1. Background agent workflows run asynchronously (`asyncio.create_task`).
2. High-risk actions require human-in-the-loop (HITL) approval before proceeding (e.g. production deploy, financial transfer, schema migration).
3. The background workflow must suspend without blocking the worker thread or event loop, awaiting an asynchronous approval decision from a web client.
4. E2E tests must be able to launch the simulation, listen to SSE stream events, and submit approval decisions via REST without deadlocking.

## 2. Asynchronous HITL Gate Suspension Pattern
Inside `HitlApprovalBridge`:
- Maintain an internal event dictionary:
  ```python
  self._decision_events: Dict[str, asyncio.Event] = {}
  self._decision_results: Dict[str, ApprovalHistoryEntry] = {}
  ```
- When a decision is required:
  ```python
  async def wait_for_decision(self, request_id: str, timeout_seconds: float = 60.0) -> Optional[ApprovalHistoryEntry]:
      event = self._decision_events.setdefault(request_id, asyncio.Event())
      try:
          await asyncio.wait_for(event.wait(), timeout=timeout_seconds)
          return self._decision_results.get(request_id)
      except asyncio.TimeoutError:
          return None
      finally:
          self._decision_events.pop(request_id, None)
  ```
- When `resolve_request` is invoked (via REST endpoint `POST /api/v1/mvr/hitl/decide`):
  ```python
  self._decision_results[request_id] = history_entry
  if request_id in self._decision_events:
      self._decision_events[request_id].set()
  ```

## 3. ASGI Asynchronous Testing Invariant
- **Never** use synchronous Starlette `TestClient` for testing background async simulation tasks or SSE streaming with interactive gates:
  - `TestClient` manages its own private loop in a thread, causing background `asyncio.create_task` tasks to stall or desync from the test's event loop.
- **Always** use `httpx.AsyncClient` with `ASGITransport`:
  ```python
  from httpx import ASGITransport, AsyncClient

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
      response = await client.post("/api/v1/mvr/simulation/launch", json=payload)
      assert response.status_code == 200
      # Wait or poll for events, then resolve approval:
      approve_resp = await client.post("/api/v1/mvr/hitl/decide", json={"request_id": req_id, "decision": "APPROVED"})
      assert approve_resp.status_code == 200
  ```

## 4. Frontend Reactive Integration (Next.js / ReactFlow)
- Frontend client subscribes to `/api/v1/mvr/events/stream`.
- Action envelopes parse event types:
  - `TASK_STARTED` / `TASK_COMPLETED`: Update node progress and status.
  - `APPROVAL_REQUESTED`: Open `HitlApprovalDrawer` immediately, displaying risk assessment, proposed action, and diff.
  - `APPROVAL_RESOLVED`: Update node status to active/failed and close drawer.
  - `SIMULATION_COMPLETED`: Display completion notification and summary.
