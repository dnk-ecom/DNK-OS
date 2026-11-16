# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/archify_obsidian_iframe_embed_and_autofit.md"
# purpose: "Autonomous mathematical auto-fit, ResizeObserver layout detection, double-downscaling prevention, and cache-busting for Archify diagrams embedded in Obsidian notes & Canvas."
# canonical_source: true
# status: "Active"
# version: "1.1.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Archify Obsidian & Iframe Embed Integration Guide

## 1. Context & Pitfall: The "Broken Fit" Symptom

When embedding Archify diagrams (`docs/diagrams/*.html`) inside an Obsidian note iframe or Obsidian Canvas card:
- Standard container sizes are constrained (e.g. `800x540` px or `720x480` px).
- Typical Archify diagrams render an SVG viewBox of `1173x676` px or larger.
- **Native Archify `reset()` behavior**: The default `Archify.view.reset()` sets `scale = 1.0` and `x = 0, y = 0`. If the diagram is already at scale 1.0 and overflowing, clicking `Fit` appears completely inert to the user because returning to 1.0 does not scale the diagram down to fit the smaller viewport.
- Additionally, the native zoom-out limit in Archify template code may clamp `scale >= 1.0`, disabling zoom-out altogether.

## 2. Critical Pitfall: The Double-Downscaling Trap in SVG Embeds

If `<svg>` only has a `viewBox="0 0 W H"` attribute without explicit CSS `width`/`height`:
1. The browser's default CSS auto-shrinks `<svg>` to fit the container width ($cW < W$).
2. When the pan-zoom script applies `transform: scale(s)` where $s = \min((cW-32)/W, (cH-32)/H)$, the CSS transform scales **an already shrunken element**.
3. **Compound scale consequence**:
   $$\text{effective\_scale} = s \times \frac{cW}{W} \approx 0.58 \times 0.61 \approx 0.35$$
   The diagram shrinks into a tiny upper-left corner, leaving huge dead space on the right and bottom, rendering it unreadable.

### Fix: Lock Natural Dimensions on SVG Element
```css
svg.diagram-canvas,
svg[viewBox] {
  width: 1173px !important;  /* Match exact natural viewBox width */
  height: 676px !important;  /* Match exact natural viewBox height */
  max-width: none !important;
  max-height: none !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
}
```

## 3. Container Hierarchy Height Collapse

Archify's default `template.html` has `.container` without explicit 100% height, causing it to collapse to a smaller intrinsic height (~419px) regardless of iframe height (e.g. 480px or 520px).
Force 100% height across the complete DOM chain:
```css
html, body, .container, .diagram-container {
  height: 100% !important;
  min-height: 100% !important;
  max-height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  box-sizing: border-box !important;
  overflow: hidden !important;
}
.container {
  display: flex !important;
  flex-direction: column !important;
  background: #0f141c !important;
}
.diagram-container {
  flex: 1 1 100% !important;
  position: relative !important;
  overflow: hidden !important;
  background: #0f141c !important;
}
```

## 4. Solution: Autonomous Mathematical Fit (`fitDiagram`)

Implement an explicit viewBox-to-container fitting routine:

```javascript
function fitDiagram(padding = 32, maxScale = 1.0) {
  const dc = document.querySelector('.diagram-container') || document.body;
  const svg = dc.querySelector('svg.diagram-canvas') || dc.querySelector('svg');
  if (!dc || !svg) return;

  const cW = dc.clientWidth || window.innerWidth;
  const cH = dc.clientHeight || window.innerHeight;

  // Resolve SVG dimensions from viewBox
  let vW = 1173, vH = 676;
  if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width > 0) {
    vW = svg.viewBox.baseVal.width;
    vH = svg.viewBox.baseVal.height;
  }

  // Calculate uniform scaling factor
  const scale = Math.min((cW - padding) / vW, (cH - padding) / vH, maxScale);

  // Center diagram in container
  const x = Math.round(((cW - vW * scale) / 2) * 100) / 100;
  const y = Math.round(((cH - vH * scale) / 2) * 100) / 100;

  // Apply transform
  svg.style.transformOrigin = '0 0';
  svg.style.transition = 'transform 0.22s cubic-bezier(0.16, 1, 0.3, 1)';
  const transform = `translate(${x}px, ${y}px) scale(${scale})`;
  svg.style.transform = transform;

  // Update zoom badge
  const badge = document.getElementById('archify-badge');
  if (badge) badge.textContent = `${Math.round(scale * 100)}%`;

  return { x, y, scale, transform };
}
```

## 5. Guarding Against Native Archify Transform Reset

Native Archify `template.html` contains `window.addEventListener('load', ...)` and resize handlers that attempt to reset transform to `scale(1), translate(0, 0)`.
To prevent the native script from wiping out the auto-fitted state before the user actually interacts:
1. Track `let userInteracted = false;` on `pointerdown`, `wheel`, or button clicks.
2. Store `let expectedTransform = '';` upon `fitDiagram()`.
3. Use a `MutationObserver` on `svg.style.transform`: if `!userInteracted` and the transform differs from `expectedTransform`, restore `expectedTransform`.

## 6. Obsidian Tab Rendering & ResizeObserver

Obsidian Webviews often initialize iframes before geometry settles (dimensions reported as 0x0):
- Using simple `window.addEventListener('resize')` misses the initial frame layout.
- Use `ResizeObserver` to catch the exact moment layout dimensions become non-zero:

```javascript
let initialFitted = false;
const ro = new ResizeObserver((entries) => {
  for (let entry of entries) {
    if (entry.contentRect.width > 100 && entry.contentRect.height > 100) {
      if (!initialFitted) {
        initialFitted = true;
        fitDiagram();
      }
    }
  }
});
ro.observe(document.querySelector('.diagram-container') || document.body);
```

## 7. Cache-Busting for Obsidian Webviews

Obsidian's Chromium webview aggressively caches local `http://127.0.0.1` iframes. When updating diagram HTML or script logic:
- Always append/increment a version query parameter in the markdown note or canvas node:
  ```markdown
  <iframe src="http://127.0.0.1:8765/dnk_swarm_workflow.html?embed=1&v=3.0" width="100%" height="480"></iframe>
  ```
- This forces an immediate reload of updated JS/CSS without requiring an Obsidian application restart.
