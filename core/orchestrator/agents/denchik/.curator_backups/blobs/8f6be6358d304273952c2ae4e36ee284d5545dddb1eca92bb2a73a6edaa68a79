# SQLite WAL Artifact Persistence & SSE Heartbeat Protocol

## Purpose
Establishes the enterprise-grade persistence and keep-alive standards for ActionBus artifact catalogs and SSE event streaming in MVR Core and DNK OS swarms.

## 1. Dual-Layer Artifact Catalog (In-Memory + SQLite WAL)
- **Problem**: When storing large payloads (>1KB) as artifacts to protect the ActionBus event stream from backpressure degradation, storing metadata exclusively in memory (`ArtifactStore._index`) causes total artifact catalog loss on hard process restarts (`SIGKILL`, container reboot).
- **Architecture**:
  - The SQLite database maintains an `action_artifacts` table storing:
    `artifact_id`, `uri`, `filename`, `content_type`, `size_bytes`, `created_by_agent`, `task_id`, `checksum_sha256`, `created_at`, `storage_path`.
  - Indexes: `CREATE INDEX IF NOT EXISTS idx_artifacts_task ON action_artifacts(task_id)` and `CREATE INDEX IF NOT EXISTS idx_artifacts_uri ON action_artifacts(uri)`.
  - Dual-layer access:
    - Writes: Write payload to disk -> Write metadata to SQLite WAL -> Update in-memory `_index`.
    - Reads: Query `_index` first; if missed or during initialization, load from SQLite WAL.
  - **Ordering Invariant**: SQLite queries listing artifacts MUST use `ORDER BY rowid ASC` to preserve chronological insertion order identical to Python `dict` iteration order.

## 2. Thread-Safe DB Initialization & Synchronous Fallback
- `ArtifactStore` is frequently invoked from synchronous execution contexts (e.g. plugins, stage executors).
- When calling synchronous persistence methods like `_sync_save_artifact` or `_sync_get_artifact`:
  ```python
  with self._sync_lock:
      if not self._initialized:
          self._sync_init_db()
  ```
  Ensure database tables and WAL PRAGMAs (`journal_mode=WAL`, `synchronous=NORMAL`) are initialized before write operations proceed.

## 3. SSE Keep-Alive Heartbeat Protocol
- **Problem**: Long-lived Server-Sent Events (SSE) connections (`GET /api/v1/mvr/events/sse`) are terminated prematurely by aggressive corporate proxies, firewalls, and mobile gateways if no messages are sent within 30-60 seconds.
- **Heartbeat Pattern**:
  - Default heartbeat timeout: `25.0` seconds.
  - Implement via `asyncio.wait_for(queue.get(), timeout=heartbeat_interval)`:
  ```python
  try:
      event = await asyncio.wait_for(sub.queue.get(), timeout=clean_interval)
      yield f"data: {event.model_dump_json()}\n\n"
  except asyncio.TimeoutError:
      yield ": keep-alive\n\n"
  ```
  - The leading colon `:` marks a standard W3C SSE comment, preventing client-side `onmessage` handlers from triggering while resetting gateway idle timers.

## 4. FastAPI Direct Function Execution Pitfall in Tests
- In async tests calling the endpoint function directly (e.g., `await sse_events_stream_endpoint(heartbeat_interval=0.05)`):
  - Parameters declared with default `fastapi.params.Query(...)` (e.g., `task_id: Optional[str] = Query(None)`) remain instances of `fastapi.params.Query` rather than `None` or string values.
  - Direct type validation prevents crashes:
  ```python
  clean_task_id = task_id if isinstance(task_id, str) else None
  clean_types = [t for t in filter_types if isinstance(t, str)] if isinstance(filter_types, (list, tuple)) else None
  ```
