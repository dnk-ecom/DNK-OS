# Spatial Canvas Control Plane MVP Pattern & Invariants

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/spatial_canvas_control_plane_mvp.md"
# purpose: "Reference architecture, Pydantic topology models, deterministic grid layout, and safety invariants for Spatial Canvas Control Plane."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---
-->

## Overview

The **Spatial Canvas Control Plane** (`core/canvas/control_plane.py` + `scripts/system/canvas_control.py`) acts as the deterministic, non-invasive spatial transformation layer between static declarative registries (plugin manifest index, capability graphs) and dynamic visual canvas representations.

## Key Principles & Invariants

1. **Non-Invasive Observer (Zero Side-Effects)**:
   - Does NOT activate, execute, or mutate plugins.
   - Does NOT touch runtime engines, swarm workers, or service registries.
   - Strictly forbids reading secrets (`.env`), making network calls, or connecting to databases.
2. **Strict Relative Path Invariant**:
   - Every input and output file path must be verified relative (`validate_relative_path`).
   - Forbids absolute paths (`/Users/...`, `/tmp`), home directories (`~`), and path traversal (`..`).
3. **Deterministic Spatial Layout (Zero Jitter)**:
   - Plugin nodes are sorted strictly alphabetically by `plugin_id`.
   - Grid layout coordinates are computed via fixed step math:
     - `col = idx % 3`, `row = idx // 3`
     - `x = float(col * 250)`, `y = float(row * 150)`
     - Standard dimensions: `width: 200.0, height: 100.0`.
4. **Topological Edge Mapping**:
   - Translates capability graph edges directly to `CanvasEdge(type="capability")`.
   - Resolves source and target node IDs to `node-{plugin_id}`.

## Pydantic Data Models

```python
class NodePosition(BaseModel):
    x: float = 0.0
    y: float = 0.0

class NodeSize(BaseModel):
    width: float = 200.0
    height: float = 100.0

class CanvasNode(BaseModel):
    node_id: str = ""
    type: str = "plugin"  # plugin | agent | service | memory
    plugin_id: Optional[str] = None
    agent_id: Optional[str] = None
    service_id: Optional[str] = None
    memory_id: Optional[str] = None
    position: NodePosition = Field(default_factory=NodePosition)
    size: NodeSize = Field(default_factory=NodeSize)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CanvasEdge(BaseModel):
    edge_id: str = ""
    source_node_id: str = ""
    target_node_id: str = ""
    type: str = "capability"  # capability | dependency | workflow
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CanvasState(BaseModel):
    version: str = "v0.1"
    nodes: List[CanvasNode] = Field(default_factory=list)
    edges: List[CanvasEdge] = Field(default_factory=list)
    last_updated_at: str = Field(...)
```

## CLI Operations

```bash
# Build state from registry + capability graph
./.venv/bin/python3 scripts/system/canvas_control.py build

# Inspect state in terminal
./.venv/bin/python3 scripts/system/canvas_control.py show

# Export to target state JSON
./.venv/bin/python3 scripts/system/canvas_control.py export --output templates/canvas/canvas_state.json
```
