# SaaP FastMCP Tool Protocol & Canvas Live HUD WebSocket Event Stream

## 1. Architectural Invariants
1. **Strict Monorepo Service Boundaries**:
   - SaaP (Service as a Plugin) microservices reside EXCLUSIVELY under `services/dnk_*` or `packages/plugins/`.
   - `core/` contains reusable orchestration, graph engines, and base schemas.
   - `apps/` contains user-facing API gateways (`apps/api`) and frontends (`apps/web`).
   - `ServiceRegistry` is strictly prohibited from scanning `apps/` or `core/` for business service discovery.

2. **FastMCP Integration Model & ServicePluginNode**:
   - Every SaaP service exposes tools via Model Context Protocol (FastMCP) over stdio, SSE, or stream transports.
   - Tool capabilities are accompanied by a `widget_descriptor` declaring how the tool/service renders as a living node on the Spatial Canvas (color, icon, input/output sockets, inspector controls).
   - Canvas engine represents these via `ServicePluginNode` in `core/canvas/canvas_engine.py`:
     * Inherits `CanvasNode` with node_type `"ServicePlugin"`.
     * Fields: `service_id` (str), `endpoints` (list[str]), `input_slots` (list[str]), `output_slots` (list[str]), `health_status` ("HEALTHY" | "DEGRADED" | "UNHEALTHY"), `widget_descriptor` (dict).
     * Polymorphic `.clone()`: Overrides `CanvasNode.clone()` to perform deep cloning of all slot arrays, descriptors, and endpoints.
     * State updates via `update_health(status)` with validation.
     * ReactFlow mapping via `CanvasEngine.to_reactflow_graph()` with glassmorphism styles and typed handles.

3. **Critical Pitfall: Snapshot Downgrade & Polymorphic Node Preservation**:
   - In graph engines supporting undo/redo (such as `core/canvas/canvas_engine.py`), `take_snapshot()` and `_apply_snapshot()` must NEVER instantiate hardcoded base classes (e.g. `CanvasNode(...)`).
   - Hardcoded instantiation downgrades specialized nodes (`ServicePluginNode`, `MindMapNode`, etc.) to base `CanvasNode`, irreversibly destroying domain attributes (`service_id`, `endpoints`, `input_slots`, `output_slots`, `widget_descriptor`).
   - **Remedy**: Base `CanvasNode` must implement `.clone()`, and every derived subclass must override `.clone()` to preserve specialized attributes. Snapshots must strictly use `nodes_snapshot[nid] = node.clone()`.
   - **Testing Invariant**: Always write snapshot-undo-redo roundtrip tests (`add_service_plugin_node()` ➔ `take_snapshot()` ➔ mutate/add node ➔ `undo()`) asserting `isinstance(restored, ServicePluginNode)` and verifying all custom fields remain intact.

4. **Harness ↔ Canvas Real-Time Event Stream (`apps/api/routers/canvas_stream.py`)**:
   - Connection established via WebSocket endpoint `/api/v1/canvas/events/stream` (with HTTP POST fallback `/broadcast`).
   - Managed via `CanvasStreamManager` with granular session-based subscription:
     * Handshake / Ping: Accepts raw string (`"ping"`, `"heartbeat"`) and JSON payload (`{"type": "ping"}` / `{"action": "ping"}`) ➔ replies with `{"type": "pong", "timestamp": ...}`.
     * Graceful Disconnect: Catches `WebSocketDisconnect` cleanly, removing the connection from active pools without logging uncaught server exceptions.
     * Session subscription: `{"action": "subscribe", "session_id": "session-xyz"}`.
     * Session unsubscription: `{"action": "unsubscribe", "session_id": "session-xyz"}`.
   - **Fallback Polling & SSE Endpoints**:
     * `/api/v1/canvas/events/poll`: Supports HTTP clients via cursor pagination (`since_seq`, `since_ts`, `session_id`) backed by a bounded ring buffer (`deque(maxlen=200)`).
     * `/api/v1/canvas/events/sse`: Streams events as Server-Sent Events (`text/event-stream`) via FastAPI `StreamingResponse`.
   - **Event Normalization Invariant**:
     * `format_hud_payload` must accept both Pydantic v2 `HarnessEvent` instances and raw `dict` objects (`getattr(event, "event_type", None) or event.get("event_type")`).
   - Event translation mapping from `HarnessEvent` to Canvas Live HUD:
     * `REASONING_DELTA` ➔ `HUD_TELEMETRY_STREAM` with `stream_type: "reasoning"`, payload `{delta: str}`.
     * `TOOL_CALL` ➔ `HUD_TELEMETRY_STREAM` with `stream_type: "tool_call"`, payload `{tool_name, tool_call_id, arguments}`.
     * `TOOL_RESULT` ➔ `HUD_TELEMETRY_STREAM` with `stream_type: "tool_result"`, payload `{tool_name, tool_call_id, result}`.
     * `CIRCUIT_TRIP` ➔ `HUD_TELEMETRY_STREAM` with `stream_type: "circuit_trip"`, payload `{tool_name, failures, cooldown_s}`.
     * `STATE_CHANGE` / `SESSION_COMPLETE` ➔ `NODE_STATE_TRANSITION` with `from_state`, `to_state`, `node_id`.

5. **Root Hygiene & Storage Guard (Fail-Closed Pitfall)**:
   - NEVER configure default storage paths targeting repo-root folders like `templates/` (e.g., `templates/canvas/approvals/`).
   - Repository root strictly enforces the 8-root directory invariant (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`). Creating `templates/` in root triggers an immediate hard failure in `scripts/system/root_hygiene_guard.py`.
   - Ephemeral or runtime state must always point to `.data/canvas/`, designated service caches, or pytest `tmp_path`.

6. **ServicePluginCard Manifest Specification (v1alpha2) & Progressive ToolRAG**:
   - SaaP manifests declare `apiVersion: dnk.os/v1alpha2` and `kind: ServicePluginCard`.
   - Structure includes:
     * `fastmcp_tools`: List of tool capability objects (`name`, `description`, `input_schema`).
     * `canvas_widgets`: List of HUD widget descriptors (`widget_id`, `name`, `component_path`, `inputs`, `outputs`).
     * `governance`: Operational constraints including `spend_guard` (`max_cost_per_invocation_usd`, `monthly_budget_usd`, `max_tokens_per_task`) and `circuit_breaker` (`failure_threshold`, `timeout_seconds`).
   - Progressive Disclosure (`ProgressiveToolCatalog`): In `core/framework/canonical_harness_engine.py`, dynamic ToolRAG queries `ServiceRegistry.get_fastmcp_tools_catalog()` to match relevant tools dynamically based on user prompt/goal keywords (e.g. "shopify", "theme", "liquid"), injecting only matched tools into agent turn context rather than dumping hundreds of tools.
   - ReactFlow Node Serialization: `CanvasEngine.to_reactflow_graph()` exports `ServicePluginNode` as `type: "custom"` containing `data` with `widget_type`, `service_id`, `input_slots`, `output_slots`, and `widget_descriptor`. Upstream task edges are linked using `engine.add_edge(from_id, to_id)`.

7. **Contract Testing & Migration Backward Compatibility**:
   - When modernizing existing services to `ServicePluginCard`, test suites validating service manifests (e.g., `tests/contracts/test_service_card_contract.py`) must inspect `manifest.get("kind")`:
     * If `ServicePluginCard`: Validate via Pydantic model `ServicePluginCard.model_validate(raw)`.
     * If legacy `ServiceCard`: Validate against legacy JSONSchema / Pydantic v1 schemas.
   - `ServiceRegistry` provides backward-compatible loader alias `load_manifest = register_service_from_file`.

8. **Headless & Asynchronous Testing Pattern**:
   - Test `ServicePluginNode` graph mutations via `tests/core/test_canvas_service_node.py`.
   - Test WebSocket stream subscriptions and telemetry broadcast via Starlette/FastAPI `TestClient` in `tests/api/test_canvas_stream.py`.
   - Test full pilot migration and ToolRAG resolution via `tests/core/test_saap_e2e_pilot_migration.py`.
