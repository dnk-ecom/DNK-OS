<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "references/canvas_websocket_sse_protocol_design.md"
# purpose: "Reference guide for Canvas WebSocket/SSE Protocol Design v0.1 (CANVAS-003)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym / Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Canvas WebSocket/SSE Protocol Design (Slice CANVAS-003)

## Overview & Architecture

When coordinating spatial canvas state between distributed swarm workers, agents, and client interfaces, `CANVAS-003` defines a strict dual-transport messaging protocol:
- **Server-Sent Events (SSE)**: Unidirectional broadcast of `canvas.state.update`, `canvas.node.*`, `canvas.edge.*`, and `canvas.conflict` events from server to clients.
- **WebSocket (WS)**: Full-duplex interactive channel for client mutations, intent dispatches, and acknowledgments (`canvas.ack`).

### Core Modules, Schemas & CLI
- **Protocol Models**: `core/canvas/protocol.py` (`CanvasMessage`, `CanvasStateUpdate`, `CanvasNodeOperation`, `CanvasEdgeOperation`, `CanvasConflict`, `CanvasAck`)
- **Schema**: `docs/schemas/dnk_canvas_message.schema.yaml`
- **CLI Simulator**: `scripts/system/canvas_protocol.py` (`generate-message`, `validate`)
- **Sample Payload**: `templates/canvas/messages/sample_message.json`
- **Audit Evidence**: `docs/audit/DNK_CANVAS_WEBSOCKET_SSE_PROTOCOL_v0.1_evidence.json`

## Pydantic Protocol Contracts

```python
from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field

class MessageType(str, Enum):
    STATE_UPDATE = "canvas.state.update"
    NODE_ADD = "canvas.node.add"
    NODE_REMOVE = "canvas.node.remove"
    NODE_MOVE = "canvas.node.move"
    NODE_UPDATE = "canvas.node.update"
    EDGE_ADD = "canvas.edge.add"
    EDGE_REMOVE = "canvas.edge.remove"
    EDGE_UPDATE = "canvas.edge.update"
    CONFLICT = "canvas.conflict"
    ACK = "canvas.ack"

class CanvasMessage(BaseModel):
    message_id: str
    timestamp: str
    message_type: MessageType
    sender_id: str
    payload: Union[
        CanvasStateUpdate,
        CanvasNodeOperation,
        CanvasEdgeOperation,
        CanvasConflict,
        CanvasAck,
        Dict[str, Any]
    ]
```

## SSE Event Formatting Convention

SSE event serialization must conform to standard text stream specifications:
```text
event: canvas.state.update
id: msg-20260909-001
data: {"message_id":"msg-20260909-001","timestamp":"2026-09-09T23:00:00Z","message_type":"canvas.state.update","sender_id":"system","payload":{...}}

```

## Critical Testing Pitfalls & Workarounds

### 1. Absolute Path Validation in Unit Tests
- **Pitfall**: Attempting to test relative path enforcement by passing `str(tmp_path)` in pytest. On macOS/Linux, `tmp_path` creates paths like `/tmp/...` or `/private/var/folders/...`, which may trigger different validation errors or behave inconsistently across CI containers.
- **Solution**: Pass an explicit virtual absolute path string (e.g. `"/absolute/virtual/test_msg.json"`) to verify `pytest.raises(ValueError, match="Absolute path.*forbidden")`.

### 2. Subprocess CLI Exit Code Testing
- **Pitfall**: Using `subprocess.check_output` on invalid CLI inputs raises `subprocess.CalledProcessError` rather than returning a structured inspection result.
- **Solution**: Use `subprocess.run(..., capture_output=True, text=True)` and assert on `result.returncode != 0` and `result.stderr` (or `result.stdout`) content.
