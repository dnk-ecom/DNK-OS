# Clean-Room Live DOM Canvas & Semantic Drop Patterns (`morluto/rea` vs `dnk-web-design`)

## 1. License & Track-2 Boundary
- `morluto/rea` has **no open-source license** (`license: None` on GitHub — All Rights Reserved).
- Direct code copying (Track 1) is strictly prohibited. Only **Track 2 (Clean-Room Reverse Engineering of architectural concepts)** is permitted inside `DNK_HUB`.
- **Zero Unsanctioned Microservices Invariant**: Do not create a standalone `services/dnk_web_design` directory. Implement frontend visual canvas primitives inside `apps/web/src/components/studio/` (or `apps/web/src/modules/web-design/`) and backend AST/Liquid transpilation in `core/` + `services/dnk_shopify/shopify_liquid/canvas_to_liquid_transpiler.py`.

## 2. Core Architectural Comparison

| Layer | `Open Design Local` | `morluto/rea` | `dnk-web-design` (DNK Studio Clean-Room) |
| :--- | :--- | :--- | :--- |
| **Artboard Isolation** | Heavy multi-package sandbox / iframe | Raw live React DOM (`transform: matrix(...)`) | Scoped Shadow DOM / Artboard container + CSS `matrix()` zoom/pan |
| **Element Picking** | Complex frame bridge | `data-rea-id` + `document.elementFromPoint(x, y)` | `data-dnk-node-id` + `elementFromPoint(x, y)` with `getBoundingClientRect()` overlay |
| **Drag-and-Drop Layout** | None (regeneration only) | `computeDropPlacement` (converts drag delta into semantic flex/margin CSS) | Semantic Flex/Grid drop solver (`flex-direction`, `justify-content`, `gap`, `margin`) |
| **Code Write-Back** | Full file overwrite via `opencode run` | Spawns `claude -p` via Vite `/__rea/SaveToCode` (slow, token-heavy) | Two-tier: (1) Deterministic AST mutation (<20ms) for style/text/order; (2) Vertex AI (`gemini-2.5-flash` / `gemini-4-argon`) for new component synthesis |
| **E-Commerce Target** | Static HTML/React only | Local React SPA only | Dual target: React/Tailwind + Shopify OS 2.0 `.liquid` & `{% schema %}` via `canvas_to_liquid_transpiler.py` |

## 3. Semantic Drop Solver (`computeDropPlacement` Clean-Room Pattern)
Instead of applying brittle `position: absolute; left: Xpx; top: Ypx` when a user drags an element on the canvas:
1. Measure the target parent container's computed display (`flex`, `grid`, `block`) and children bounding boxes (`getBoundingClientRect()`).
2. Determine the insertion index among siblings based on cursor `(clientX, clientY)` relative to sibling midpoints.
3. Compute residual offset (`deltaX`, `deltaY`) from the natural flow position and quantize to Tailwind spacing tokens (`gap-*`, `mt-*`, `ml-*`, `justify-*`, `items-*`).
4. Apply the update immediately to the in-memory `CanvasStatePayload` store (optimistic 60fps preview) and commit via deterministic AST/Liquid transpiler without invoking an LLM.
