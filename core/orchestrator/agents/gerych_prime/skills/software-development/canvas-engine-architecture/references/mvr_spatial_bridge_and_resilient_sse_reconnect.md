# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/mvr_spatial_bridge_and_resilient_sse_reconnect.md"
# purpose: "Technical Architecture & Operational Patterns for MVR Spatial Bridge, Resilient W3C SSE Reconnect & HITL Gateway"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# MVR Spatial Bridge, Resilient W3C SSE Reconnect & HITL Gateway

## 1. Executive Summary
This reference captures the production patterns for connecting the high-velocity MVR Action Bus backend to the Visual Working Canvas (XYFlow/ReactFlow) via resilient W3C Server-Sent Events (SSE), Human-in-the-Loop (HITL) approval gates, and spatial node mutation streaming.

## 2. Resilient W3C SSE Reconnection (`Last-Event-ID`)
- **W3C Standard Compliance**: Each emitted SSE event payload includes an `id: <event_id>` line alongside `event: <type>` and `data: <json>\n\n`.
- **Catch-up Architecture**:
  - The `ActionBroadcaster` maintains a fixed-size ring buffer (`deque(maxlen=500)`).
  - When the browser or canvas client disconnects due to network flapping, the browser's native `EventSource` automatically transmits the HTTP header `Last-Event-ID: <id>` (with fallback to query parameter `?last_event_id=<id>`).
  - Upon reconnection, `broadcaster.get_events_since(last_event_id)` yields all missed historical events in FIFO order before transitioning the subscriber to live event streaming.
  - If the requested ID has expired from the ring buffer, the broadcaster safely falls back to returning the most recent events, preventing reconnection stalls.

## 3. Spatial Canvas Streaming & Worker Routing
- **Fine-Grained Spatial Updates**:
  - `CANVAS_NODE_MOVED`: Carries `(node_id, x, y, delta_x, delta_y)` for real-time kinematic drag tracking without serializing the full graph tree.
  - `CANVAS_BATCH_MUTATION`: Encapsulates atomic arrays of added/updated/deleted nodes and edges in a single bus transaction.
- **Worker Routing Invariant**:
  - Both `CANVAS_NODE_MOVED` and `CANVAS_BATCH_MUTATION` events route to `target_agent="gerych_builder"`, ensuring the UI builder agent maintains active supervision of spatial topology.

## 4. Human-in-the-Loop (HITL) Approval Gateway
- **Approval Lifecycle Integration**:
  - `HitlApprovalBridge` sits between `AgentActionBus` and `ApprovalManager` (`core/canvas/approval.py`).
  - High-risk operations request approval via `bridge.request_approval(task_id, action_type, description, details)`.
  - The action task transitions to `ActionTaskStatus.WAITING_APPROVAL`, and an `APPROVAL_REQUESTED` event is broadcast to the canvas HUD.
  - Upon operator review (`POST /api/v1/mvr/approvals/{request_id}/decision`), the bridge records the verdict (`approved` / `rejected`), transitions the task, and emits `APPROVAL_RESOLVED`.
- **Path Hygiene & Security Invariant**:
  - `ApprovalManager` enforces `not os.path.isabs(p)`. Absolute paths (`/Users/...`, `/private/...`) are rejected with `ValueError`.
  - Test suites and production callers must supply relative paths (e.g. `.test_pending_<uuid>.json` or `config/approval_pending.json`).

## 5. Artifact Retention & Dual-Layer TTL Garbage Collection
- **Pruning Strategy**:
  - `ArtifactStore.prune_expired_artifacts(max_age_seconds=14 * 86400)` cleans up artifacts exceeding the retention period.
  - Dual-layer purge:
    1. Unlinks binary/text payload files from the filesystem.
    2. Purges the in-memory lookup cache (`_index`).
    3. Deletes metadata rows from the SQLite WAL database (`DELETE FROM action_artifacts WHERE artifact_id IN (...)`).
  - Exposed via REST: `POST /api/v1/mvr/artifacts/prune?max_age_seconds=...`.

## 6. Testing Invariant: FastAPI SSE Async Streaming in Pytest
- **Starlette TestClient Deadlock Pitfall**:
  - Calling `client.stream("GET", "/api/v1/mvr/events/sse")` against an infinite async generator (`while True: await asyncio.sleep(...)`) in synchronous `TestClient` freezes the test runner event loop, causing 180s command timeouts.
- **Canonical Non-Blocking Verification Pattern**:
  - Call the FastAPI router function directly as an async generator fixture:
  ```python
  response = await sse_events_stream_endpoint(
      request=Request(...),
      heartbeat_interval=0.05,
      last_event_id=e1.event_id,
      bus=bus,
  )
  gen: Any = response.body_iterator
  connected_banner = await gen.__anext__()
  replay_event = await gen.__anext__()
  assert f"id: {e1.event_id}" in replay_event
  await gen.aclose()
  ```
