# Obsidian Mermaid & Vector DOM Containment Architecture

## CodeMirror 6 Containment Trap (`contain: layout paint`)

In Obsidian Live Preview (CodeMirror 6), markdown embeds (codeblocks, Mermaid charts, math blocks) are wrapped in `.cm-embed-block`.
CodeMirror attaches layout isolation styles to these containers:
```css
contain: layout paint;
overflow: hidden;
```

### The Pitfall
- Applying `position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;` to an element inside `.cm-embed-block` fails.
- In CSS containment specifications (`contain: paint` or `layout`), the containing block for `fixed` positioned descendants becomes the containment container itself, NOT the viewport.
- As a result, the diagram collapses, gets clipped to 0px, or disappears off-screen.

### Proven Solutions
1. **Inline Window-Height Expansion (Preferred for in-canvas zooming)**:
   - Keep `position: relative !important;`.
   - Set height to window viewport bounds: `height: calc(100vh - 120px) !important; max-height: calc(100vh - 120px) !important;`.
   - Scroll the container into view: `container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });`.
2. **Body Portal (Modal / Fullscreen Overlays)**:
   - If true absolute viewport fullscreen is required, detach the element from `.cm-embed-block` and mount directly to `activeDocument.body.appendChild(modalContainer)`.

---

## Bounded Initial Viewport (≤ 500px) & 100% Auto-Fit Recipe

When opening notes with large or tall Mermaid diagrams, diagrams must fit completely within a bounded window (≤ 500px) without vertical clipping or horizontal truncation, allowing users to zoom in manually when needed.

### SVG & Container Invariants
```css
/* Container */
.mermaid-canvas-container {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  max-height: 500px !important;
  width: 100% !important;
  overflow: hidden !important;
  position: relative !important;
}

/* Vector SVG */
.mermaid-canvas-svg {
  display: block !important;
  margin: 0 auto !important;
  max-width: 100% !important;
  max-height: 100% !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
  transform-origin: center center !important;
}
```

### SVG Preserve Aspect Ratio
Ensure the SVG attribute is explicitly configured:
```javascript
svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
```

### Dynamic Height Clamping
Compute natural height from SVG `viewBox` or `getBBox()`:
```javascript
const cWidth = container.clientWidth || 800;
let svgW = svg.viewBox?.baseVal?.width || 0;
let svgH = svg.viewBox?.baseVal?.height || 0;

if (svgW > 0 && svgH > 0 && cWidth > 0) {
    const naturalH = (svgH / svgW) * cWidth;
    const targetH = Math.min(Math.max(Math.round(naturalH), 160), 500);
    container.style.height = `${targetH}px`;
    container.style.maxHeight = '500px';
} else {
    container.style.height = '500px';
    container.style.maxHeight = '500px';
}
```

### Zoom & Pan Geometry
- At initial load (`Fit` state):
  `transform: translate(0px, 0px) scale(1)`
- Manual zooming:
  - Button step: `±15%` (`scale *= 1.15` / `scale /= 1.15`)
  - Mousewheel / Trackpad step: `3%` (`scaleFactor = 1.03` / `0.97`)
  - Bounds: `25%` to `600%`
- Toolbar ergonomics:
  - Ghost Mode default opacity: `0.18`, hover `1.0`
  - Floating badge displaying current percentage or `Fit`.
