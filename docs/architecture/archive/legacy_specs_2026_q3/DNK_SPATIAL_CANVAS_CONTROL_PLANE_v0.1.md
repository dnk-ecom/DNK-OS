---
title: "Dnk Spatial Canvas Control Plane V0.1"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_SPATIAL_CANVAS_CONTROL_PLANE_v0.1.md"
> purpose: "Document: Dnk Spatial Canvas Control Plane V0.1"
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
> # mrh_id: "docs/architecture/specs/DNK_SPATIAL_CANVAS_CONTROL_PLANE_v0.1.md"
> # purpose: "Specification for DNK OS Spatial Canvas Control Plane MVP v0.1 (CANVAS-001)"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "0.1.0"
> # updated_at: "2026-09-09"
> # author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# DNK OS Spatial Canvas Architecture: Spatial Canvas Control Plane MVP v0.1

## 1. Overview & Objective

The **Spatial Canvas Control Plane MVP** (`CANVAS-001`) establishes a deterministic, non-invasive spatial state management and topology control plane for DNK OS. It provides the initial foundation for visual representation and spatial coordination of plugins, agents, services, and memories across visual canvases.

### Scope & Role
- **Non-Invasive Observer & Transformer**: Reads from the plugin registry (`plugins_index.json`) and capability graph (`capability_graph.json`) to construct an immutable spatial state (`CanvasState`).
- **No UI or Frontend**: Does not introduce frontend UI code, HTML, CSS, or browser-side canvas engines.
- **No WebSocket / SSE**: Operates purely offline via CLI and standard Python models.
- **No Runtime Mutation**: Does not alter plugin lifecycles, execution plans, runtime engines, or activate plugins.
- **Zero Secrets / Network**: No external services, HTTP calls, secret files (`.env`), or database connections.
- **Strict Relative Path Invariant**: Enforces safe workspace-relative paths; rejects absolute and path traversal attempts.

---

## 2. Canvas Control Plane Data Models

### 2.1 CanvasNode

Represents an individual spatial node on the canvas representing an entity (plugin, agent, service, or memory).

```yaml
CanvasNode:
  node_id: "node-github-plugin-001"
  type: "plugin" # plugin | agent | service | memory
  plugin_id: "github-plugin-001"
  agent_id: null
  service_id: null
  memory_id: null
  position:
    x: 0.0
    y: 0.0
  size:
    width: 200.0
    height: 100.0
  metadata: {}
```

#### Field Specifications
- `node_id: str`: Unique identifier of the node on the canvas (e.g. `node-{plugin_id}`).
- `type: str`: Entity classification, constrained to `{"plugin", "agent", "service", "memory"}`. Default: `"plugin"`.
- `plugin_id: Optional[str]`: Associated plugin identifier when `type == "plugin"`.
- `agent_id: Optional[str]`: Associated swarm agent identifier when `type == "agent"`.
- `service_id: Optional[str]`: Associated service identifier when `type == "service"`.
- `memory_id: Optional[str]`: Associated memory bank identifier when `type == "memory"`.
- `position: NodePosition`: Cartesian coordinates `(x, y)` on the canvas. Supports both dot access (`.x`, `.y`) and dictionary access (`["x"]`, `["y"]`).
- `size: NodeSize`: Dimensions `(width, height)`. Default: `200x100`.
- `metadata: Dict[str, Any]`: Arbitrary key-value metadata preserved from the source registry.

### 2.2 CanvasEdge

Represents a directed topological connection between two nodes on the canvas.

```yaml
CanvasEdge:
  edge_id: "edge-node-p1->node-p2:read->process"
  source_node_id: "node-p1"
  target_node_id: "node-p2"
  type: "capability" # capability | dependency | workflow
  metadata: {}
```

#### Field Specifications
- `edge_id: str`: Unique edge identifier.
- `source_node_id: str`: Source node reference.
- `target_node_id: str`: Target node reference.
- `type: str`: Relationship type, constrained to `{"capability", "dependency", "workflow"}`. Default: `"capability"`.
- `metadata: Dict[str, Any]`: Edge attributes, such as source/target capabilities or routing parameters.

### 2.3 CanvasState

Aggregates the entire spatial topology snapshot of the canvas.

```yaml
CanvasState:
  version: "v0.1"
  nodes: list[CanvasNode]
  edges: list[CanvasEdge]
  last_updated_at: "2026-09-09T23:00:00Z"
```

#### Field Specifications
- `version: str`: Schema version string (default `"v0.1"`).
- `nodes: List[CanvasNode]`: Array of spatial nodes.
- `edges: List[CanvasEdge]`: Array of topological edges.
- `last_updated_at: str`: ISO 8601 UTC timestamp of state compilation or export.

---

## 3. Control Plane Logic & Deterministic Layout

### 3.1 Registry & Capability Graph Loading
1. **Registry Ingestion**: Reads `templates/plugin/plugins_index.json` containing registered plugins.
2. **Capability Graph Ingestion**: Reads `templates/plugin/capability_graph.json` containing capability dependencies and edges.

### 3.2 Deterministic Positioning Engine
To guarantee zero visual jitter and reproducible graph builds across runs:
- Plugins are sorted strictly alphabetically by `plugin_id`.
- Grid layout is computed deterministically:
  ```python
  col = index % 3
  row = index // 3
  x = float(col * 250)
  y = float(row * 150)
  ```
- Nodes are assigned fixed dimensions `width: 200.0, height: 100.0`.

### 3.3 Topological Edge Mapping
- Each capability edge in the capability graph is translated to a `CanvasEdge` with `type="capability"`.
- `source_node_id` is resolved to `node-{from_plugin}`.
- `target_node_id` is resolved to `node-{to_plugin}`.
- Capability metadata (`from_capability`, `to_capability`) is preserved in `metadata`.

---

## 4. CLI Interface (`scripts/system/canvas_control.py`)

### 4.1 Build Command
Compiles state from Registry and Capability Graph and saves to output:
```bash
./.venv/bin/python3 scripts/system/canvas_control.py build
```
Flags:
- `--registry`, `-r`: Path to plugins index (default `templates/plugin/plugins_index.json`).
- `--capability-graph`, `-g`: Path to capability graph (default `templates/plugin/capability_graph.json`).
- `--output`, `-o`: Path to target output JSON (default `templates/canvas/canvas_state.json`).

### 4.2 Show Command
Inspects and pretty-prints current canvas state:
```bash
./.venv/bin/python3 scripts/system/canvas_control.py show
```
Flags:
- `--state`, `-s`: Path to canvas state JSON (default `templates/canvas/canvas_state.json`).

### 4.3 Export Command
Exports CanvasState to a specified output file:
```bash
./.venv/bin/python3 scripts/system/canvas_control.py export --output templates/canvas/canvas_state.json
```

---

## 5. Security & Isolation Guarantees

1. **Read-Only Ingestion**: Reads registry and capability graph; does not modify them.
2. **No Network Access**: Zero socket connections or HTTP traffic.
3. **No Secret Access**: Never reads `.env` or credential files.
4. **No Subprocess / DB Calls**: Fully self-contained Python execution.
5. **Path Traversal Protection**: Enforces relative paths; forbids `..` or absolute prefixes.
