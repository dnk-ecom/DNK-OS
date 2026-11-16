# --- DNK-MRH-HEADER ---
# mrh_id: "references/mvr_event_streaming_websocket_and_artifact_storage_protocol.md"
# purpose: "Real-Time Event Streaming (WebSockets/SSE), Non-blocking Backpressure, and Artifact URI Passing Protocol"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Real-Time Event Streaming (WebSockets / SSE) & Artifact Store Protocol

## 1. Context & Architecture (Phase 3 MVR Core)
When swarms execute complex multi-agent pipelines (`SwarmPipeline`, `SwarmParallel`), passing massive payloads (codebases, binary media, full AST dumps) between agents creates context rot, serialisation overhead, and memory spikes.
Furthermore, Visual Canvas UI requires millisecond-latency streaming of atomic swarm milestones (`SWARM_PARALLEL_STARTED`, `TASK_ROUTED`, `ARTIFACT_CREATED`) without blocking agent execution loops.

## 2. Invariants & Patterns

### A. Non-Blocking Event Broadcaster (`EventBroadcaster`)
- **Queue Architecture**: Per-subscriber bounded `asyncio.Queue(maxsize=N)` (default 200).
- **Backpressure & Drop Policy**: Fast producers must never be held back by slow network consumers or disconnected tabs.
  ```python
  try:
      queue.put_nowait(event)
  except asyncio.QueueFull:
      try:
          queue.get_nowait()  # Drop oldest
      except asyncio.QueueEmpty:
          pass
      queue.put_nowait(event)
  ```
- **Cold-Start History**: Maintain an in-memory `collections.deque(maxlen=100)` so new UI clients immediately receive recent swarm pulse on connection.

### B. Artifact URI Passing Over Payload Bloat
- **Threshold Rule**: Any pipeline stage output exceeding 1,024 bytes (or marked `store_artifact=True`) must be written to disk (`artifacts/mvr/<category>/<id>_<name>`).
- **Deterministic URI**: Format `artifact://mvr/<category>/<id>_<name>` is passed in `payload["artifact_uri"]` and `prior_stage_output`.
- **Integrity**: Store SHA-256 hash and metadata (`ArtifactMetadata`) alongside files.

### C. FastAPI WebSocket & SSE Test Isolation
- **Dependency Injection**: Always declare `Depends(get_action_bus)` on both HTTP (`/events/sse`) and WebSocket (`/events/ws`) endpoints.
  Never rely on module-level `_GLOBAL_BUS` singletons; Starlette `TestClient` tests must override `get_action_bus` via `app.dependency_overrides`.
- **Clean Task Cancellation in WebSockets**:
  When managing dual send/receive loops in a WebSocket endpoint, catch `WebSocketDisconnect` and explicitly cancel background tasks:
  ```python
  send_task = asyncio.create_task(...)
  recv_task = asyncio.create_task(...)
  try:
      await asyncio.wait([send_task, recv_task], return_when=asyncio.FIRST_COMPLETED)
  finally:
      send_task.cancel()
      recv_task.cancel()
      await asyncio.gather(send_task, recv_task, return_exceptions=True)
  ```
  Failing to await cancelled tasks causes `TestClient` or ASGI server cleanup to hang indefinitely.
