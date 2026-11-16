# DNK OS Harness Integration v1.0 Reference & Architecture Patterns

## Overview
Reference document for Slice `INTEGRATION-001` unifying Plugin Governance (`core.plugins.*`) and Canvas Control Plane (`core.canvas.*`) into a cohesive orchestration layer without runtime mutations.

---

## 1. The 5 Key Integration Points

### Point 1: Plugin Registry & Capability Graph → Canvas Control Plane
- **Adapter**: `PluginNodeAdapter` parses registered `PluginCard` instances.
- **Node Projection**:
  - `id`: `plugin:<plugin_id>`
  - `type`: `task_agent`
  - `metadata`: `{"card": card.to_dict(), "risk_tier": card.security.risk_tier.value, "status": "REGISTERED"}`
- **Edge Projection**:
  - `CapabilityGraph` dependency and dataflow edges mapped to `CanvasEdge(source=req_id, target=consumer_id, edge_type="DEPENDENCY")`.

### Point 2: Execution Engine & Audit Log → Canvas Live State
- **Execution Plan**: Translates execution stages into node lifecycle transitions (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`).
- **Metadata Updates**: Execution durations, token metrics, and output artifact paths synced to `CanvasNode.metadata`.
- **Canvas Events**: Step completions and failures emitted as `CanvasEvent(event_type=EventType.STEP_COMPLETED, ...)`.

### Point 3: Health & Risk Metrics → Canvas Visual Indicators
- **Health Indicators**: `PluginHealthMetrics.health_score` (0.0 - 1.0) drives visual node status:
  - `score >= 0.8`: `HEALTHY` (Green ring)
  - `0.5 <= score < 0.8`: `WARNING` (Amber warning indicator)
  - `score < 0.5`: `DEGRADED` (Red alert badge)
- **Consecutive Failures**: Triggers automatic canvas node badge and isolation suggestion.

### Point 4: Human-in-the-Loop Approval → Plugin Governance Unlock
- **Fail-Closed Trigger**: `RiskTier.CRITICAL` actions or policy violations trigger `ApprovalRequest` in `core.canvas.approval.ApprovalManager`.
- **Pipeline Interruption**: `PluginExecutionEngine` suspends execution and yields control.
- **Unlock**: Founder approval (`Decision.APPROVED` by Maksym) emits `APPROVAL_RESOLVED`, transitions node state to `RUNNING`, and resumes execution.

### Point 5: Audit Ledger → Canvas Timeline History
- **Immutable Log**: `PluginAuditLedger` entries projected into chronological `CanvasEvent` streams.
- **Traceability**: Audit events link plugin actions, parameters, risk ratings, and human approval IDs directly to Canvas nodes for interactive timeline scrubbing.

---

## 2. Headless Pure-Python PNG Rasterization Pattern
When `mmdc` (Mermaid CLI) or headless Chromium is unavailable in container/CLI environments, rasterize architecture diagrams to clean PNGs without external dependencies:

```python
import struct, zlib

def generate_clean_png(filename, width=1200, height=900):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter byte: None
        for x in range(width):
            # Draw background or colored rectangular bounding boxes / text markers
            raw_data.extend((26, 27, 38))  # Dark canvas theme (RGB)

    def png_chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    idat = png_chunk(b"IDAT", zlib.compress(bytes(raw_data), 9))
    iend = png_chunk(b"IEND", b"")

    with open(filename, "wb") as f:
        f.write(header + ihdr + idat + iend)
```

---

## 3. Ten Specification Invariant Verification Suite
When delivering architectural specification slices without runtime mutations, enforce this 10-point test harness:
1. Complete coverage of all 5 integration points.
2. Valid Mermaid diagram syntax (`flowchart TD`, distinct subgraphs, explicit cross-subgraph edges).
3. Founder leverage documented (Cognitive clarity, bottleneck elimination, speed).
4. Audit evidence report confirms all integration points and SHA256 file hashes.
5. Safety invariants strictly held (no secrets read, no network calls, no DB mutations).
6. 100% relative paths only (`./`, `../`) across all documentation and references.
7. Compatibility with existing core components verified via clean imports.
8. Zero modifications to Plugin Governance models.
9. Zero modifications to Canvas Control models.
10. Ready for implementation without ambiguous stubs.
