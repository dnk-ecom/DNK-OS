# Excalidraw & Mermaid Interactive Embed Controls (Obsidian Plugin v2.0)

## Overview & UX Architecture
Obsidian embedded diagrams (`.excalidraw`, `.excalidraw.md`, `.mermaid`) in preview/reading view by default have static dimensions and capture drag events. 
The unified `mermaid-interactive-zoom` v2.0 plugin enhances embedded diagram containers with a floating glassmorphic toolbar, responsive fullscreen mode, smooth pan/drag, and wheel zoom.

## Supported Embed Types
1. **Mermaid**: `.block-language-mermaid`, `.mermaid`, `div.mermaid`
2. **Excalidraw**:
   - `span.internal-embed[src*=".excalidraw"]`
   - `div.internal-embed[src*=".excalidraw"]`
   - `.media-embed[src*=".excalidraw"]`
   - `.image-embed[src*=".excalidraw"]`
   - `.excalidraw-svg`

## Core Interactive Controls
1. **Toolbar Actions**:
   - **`⛶ На все вікно` / `⛶ Компактно`**: Toggles viewport height (`calc(100vh - 120px)`) with backdrop dimming and smooth focus scroll. `Escape` key exits fullscreen.
   - **`⟲ Fit`**: Centers the drawing and resets scale to 100% / auto-fit with smooth easing.
   - **`+` / `−`**: Incremental step zoom (+15% / -15%) clamped between 15% and 600%.
   - **`Badge (% / Fit)`**: Displays current zoom level in real time; clicking toggles between Fit and 100%.
   - **`↗ Редактор`** (Excalidraw only): Opens the drawing file directly in Obsidian's native Excalidraw canvas editor.

2. **Pan & Drag Hygiene ("Ладошка")**:
   - Left-click drag pans the diagram smoothly (`cursor: grab` -> `cursor: grabbing`).
   - Movement threshold (>3px): If the pointer has moved during drag, subsequent click and pointerup events are swallowed in the capture phase. This prevents Excalidraw from opening the `.excalidraw` file in a new tab when the user was only panning.

3. **Wheel / Pinch Zoom**:
   - `Ctrl` / `Cmd` + Wheel anywhere on the canvas zooms smoothly.
   - In fullscreen/expanded mode, wheel scrolling zooms directly without requiring modifier keys.

4. **Double Click**:
   - Double-clicking on empty canvas area immediately triggers Auto-Fit.
