# Archify HTML Diagrams & Interactive Web Visuals in Obsidian

## Problem Context
Obsidian uses the `app://` Electron custom scheme. As a result, embedding interactive HTML/JS visuals with `<iframe src="./relative/path.html">` directly from local disk fails or behaves inconsistently across platforms due to CORS/security restrictions.

## Proven Integration Patterns

### 1. Loopback Server Pattern
Serve compiled standalone HTML artifacts (such as Archify diagrams, Remotion web players, or interactive Three.js/D3 canvases) via a lightweight local daemon:
```bash
python3 -m http.server 8765 --directory docs/diagrams
```

### 2. Embed Query Parameter (`?embed=1`)
Archify HTML outputs support `embed=1` in `location.search` (`dnk_swarm_workflow.html?embed=1`). This cleanly removes outer toolbars, page borders, and full-screen margins, providing a clean canvas.

### 3. Responsive Obsidian Markdown Iframe
Embed directly into any `.md` note:
```html
<iframe 
  src="http://127.0.0.1:8765/dnk_swarm_workflow.html?embed=1" 
  width="100%" 
  height="750px" 
  style="border: 1px solid #1e293b; border-radius: 12px; background: #0b0f19; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
</iframe>
```

### 4. Obsidian Native Canvas (`.canvas`) Web Node
Obsidian Canvas natively supports web URLs as interactive cards:
```json
{
  "id": "archify_interactive_view",
  "type": "link",
  "url": "http://127.0.0.1:8765/dnk_swarm_workflow.html?embed=1",
  "x": 0,
  "y": 0,
  "width": 1280,
  "height": 820
}
```
This allows placing an interactive animated HTML diagram alongside markdown note cards with bidirectional edges.

## Archify Workflow Layout & Validation Rules
- **Lane & Column Slotting**: In workflow mode, at most 1 node should occupy a `(lane, col)` slot. Overlapping nodes closer than 8px fail validation.
- **MainPath Continuity**: `mainPath` node IDs must strictly match existing directional edges.
- **Quality Profile**: Use `quality_profile: "standard"` for multi-lane or cyclic workflows to prevent ambiguous corridor errors; reserve `"showcase"` for strict acyclic pipelines.
