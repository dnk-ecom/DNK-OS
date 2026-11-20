---
title: "Dnk Canvas Websocket Sse Protocol V0.1"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_CANVAS_WEBSOCKET_SSE_PROTOCOL_v0.1.md"
> purpose: "Document: Dnk Canvas Websocket Sse Protocol V0.1"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/DNK_CANVAS_WEBSOCKET_SSE_PROTOCOL_v0.1.md"
> # purpose: "Formal Specification for DNK OS Canvas WebSocket/SSE Message Protocol v0.1 (CANVAS-003)"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "0.1.0"
> # updated_at: "2026-09-09"
> # author: "DNK-e.com Maksym / Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# DNK OS Spatial Canvas Architecture: WebSocket/SSE Protocol Design v0.1

## 1. Overview & Objective

The **Canvas WebSocket/SSE Protocol Design** (`CANVAS-003`) establishes a formal, declarative event-driven wire protocol for synchronizing `CanvasState` changes across distributed agents, users, and backend microservices.

### Scope & Invariants
- **Formal Protocol Models**: Defines strict schema contracts for event envelopes (`CanvasMessage`) and operational payloads (`CanvasStateUpdate`, `CanvasNodeOperation`, `CanvasEdgeOperation`, `CanvasConflict`, `CanvasAck`).
- **Transport Independence**: Models are decoupled from network transport, supporting both Server-Sent Events (SSE) for unidirectional delta broadcasts and WebSockets for duplex command channels.
- **Pure Schema & Simulation**: This slice creates no active runtime server, opens no external sockets, and requires no database. It focuses entirely on data contracts, validation, and CLI simulation tools.
- **Zero Secrets / Network / DB**: Operates strictly on in-memory representations and relative file paths (`./`, `../`).

---

## 2. Protocol Models & Wire Schemas

### 2.1 CanvasMessage (Envelope)

The universal message envelope for all canvas communication:

```yaml
CanvasMessage:
  message_id: "c6626b36-05e6-44de-8e3c-28c6220abd7d"
  timestamp: "2026-09-09T23:00:00Z"
  message_type: "canvas.state.update"
  # Allowed message types:
  # canvas.state.update | canvas.node.add | canvas.node.remove
  # canvas.node.move | canvas.node.update | canvas.edge.add
  # canvas.edge.remove | canvas.edge.update | canvas.conflict | canvas.ack
  sender_id: "gerych_prime"
  # Allowed senders: gerych_prime | maksym | system | <agent_id> | <client_id>
  payload: {}
  # Structured payload corresponding to message_type
```

### 2.2 CanvasStateUpdate (Full/Partial Snapshot)

Encapsulates complete or checkpointed canvas state synchronizations:

```yaml
CanvasStateUpdate:
  canvas_id: "canvas-main"
  version: "v0.1"
  state:
    nodes: [...]
    edges: [...]
```

### 2.3 CanvasNodeOperation (Delta Mutation)

Represents fine-grained node manipulations on the visual canvas:

```yaml
CanvasNodeOperation:
  operation: "add" # add | remove | move | update
  node:
    node_id: "plugin-001"
    type: "plugin"
    position:
      x: 100
      y: 200
    data:
      title: "Shopify Core Engine"
```

### 2.4 CanvasEdgeOperation (Topology Connector Mutation)

Represents topological connection events between canvas nodes:

```yaml
CanvasEdgeOperation:
  operation: "add" # add | remove | update
  edge:
    edge_id: "edge-001"
    source: "plugin-001"
    target: "plugin-002"
    label: "depends_on"
```

### 2.5 CanvasConflict (OCC Collision Signal)

Dispatched when concurrent mutations on the same entity or field collision are detected:

```yaml
CanvasConflict:
  conflict_id: "conf-789"
  path: "nodes.0.position.x"
  base_value: 0
  local_value: 100
  remote_value: 200
  resolution: "manual" # manual | local | remote | base
```

### 2.6 CanvasAck (Receipt & Status Confirmation)

Acknowledges receipt and admission of an operation:

```yaml
CanvasAck:
  message_id: "msg-001"
  status: "accepted" # accepted | rejected | conflict
  reason: null
```

---

## 3. Message Flow Architecture

```text
Client A                         Server                         Client B
   |                               |                               |
   |--- canvas.node.add ---------->|                               |
   |                               |--- canvas.node.add --------->|
   |<-- canvas.ack (accepted) -----|                               |
   |                               |                               |
   |                               |<-- canvas.node.move ---------|
   |<-- canvas.node.move ----------|                               |
   |                               |                               |
   |--- canvas.node.move --------->|                               |
   |                               |<-- canvas.conflict ----------|
   |<-- canvas.conflict -----------|                               |
```

### Flow Lifecycle
1. **Node Insertion**: Client A transmits `canvas.node.add`. Server validates schema, applies optimistic update, returns `canvas.ack (accepted)` to Client A, and broadcasts `canvas.node.add` to Client B.
2. **Node Movement**: Client B moves the node, emitting `canvas.node.move`. Server broadcasts the spatial update to Client A.
3. **Concurrent Mutation & Conflict**: Client A attempts a conflicting move while Client B's change is in-flight. Server runs OCC reconciliation; upon detecting divergent updates to the same path, server dispatches `canvas.conflict` to participating actors.

---

## 4. WebSocket vs. SSE Architecture Trade-offs

| Criterion | Server-Sent Events (SSE) | WebSocket |
|:---|:---|:---|
| **Directionality** | Unidirectional (Server → Client) | Bi-directional (Full Duplex) |
| **Protocol Overhead** | HTTP/1.1 or HTTP/2 standard streams | Stateful TCP handshake upgrade |
| **Proxy / Ingress Compatibility** | High (natively supported by CDNs, Cloudflare, Nginx) | Moderate (requires persistent sticky connections) |
| **Automatic Reconnection** | Built-in browser reconnect with `Last-Event-ID` | Requires manual application-level reconnection |
| **Designation in DNK OS** | **Primary for CanvasState updates & delta streams** | **Command-oriented interactions & collaborative cursor duplexing** |

---

## 5. CLI Simulator & Verification

### Generate Message
```bash
./.venv/bin/python3 scripts/system/canvas_protocol.py generate-message \
  --type canvas.node.add \
  --sender gerych_prime \
  --node '{"node_id":"plugin-001","type":"plugin","position":{"x":0,"y":0}}'
```

### Validate Message File
```bash
./.venv/bin/python3 scripts/system/canvas_protocol.py validate \
  templates/canvas/messages/sample_message.json
```

---

## 6. Integration Roadmap
- **CANVAS-004**: Human-in-the-Loop (HITL) approval protocols (`canvas.approval.request`, `canvas.approval.response`) building directly on this envelope schema.
- **CANVAS-005**: Live FastAPI SSE router mounting the streaming endpoint for web clients.
