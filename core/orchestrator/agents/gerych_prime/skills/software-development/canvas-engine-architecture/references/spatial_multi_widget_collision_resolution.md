# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/canvas-engine-architecture/references/spatial_multi_widget_collision_resolution.md"
# purpose: "Reference specification for spatial multi-widget quadrant partitioning, collision prevention, and UI harmonization on infinite agentic canvases."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-16"
# author: "Gerych Prime & Maxim"
# --- END DNK-MRH-HEADER ---

# Spatial Multi-Widget Collision Resolution & Studio Layout Harmonization

## 1. Problem Statement: Infinite Canvas Widget Collision & Stacking Disorder
When scaling an agentic canvas (React Flow / XYFlow) to include multiple floating widgets (creative toolbars, viewport controls, revision rails, status monitors, and an AI chat drawer), uncoordinated positioning causes severe visual collisions:
- Floating toolbars (`right-4`) hidden behind or colliding with the AI chat drawer (`w-[380px]` right panel).
- Viewport controls (`bottom-6 right-6`) overlapping the chat input box and submit button.
- Bottom prompt docks (`StitchPromptDock`) colliding with bottom-center timeline scrubbers (`TimeTravelRail`), presenting duplicate prompt inputs.
- Uncollapsed AI reasoning accordions and multi-card artifact lists consuming vertical space and obscuring chat context.
- **Top Bar Dual-Layer Collision**: Inner canvas components (`CanvasEngine.tsx`) mounting floating toolbars at `absolute top-4 left-1/2 -translate-x-1/2` that clash with the parent workspace header (`StitchTopNav.tsx` at `top-4 left-4 right-4`), causing clipped elements (`Spatial HQ`, `Notes`, `Edges`) to peek out from under the navigation pills.

---

## 2. The Four-Quadrant Spatial Allocation Model

```
+-----------------------------------------------------------------------------------------+
| Top Bar (SSOT Header: StitchTopNav):                                                    |
|  - Left: Hub Back, Project Title, [ObsidianSyncBar: Nodes/Edges status & sync]         |
|  - Center: Mode Pills (🪶 Swarm / ⚡ Timeline / 🛍️ Shopify / 📊 Analytics)              |
|  - Right: [SwarmHealthWidget: 🟢 Ready / Telemetry], Preview / Export / Share actions   |
+-----------------------------------------------------------------------------------------+
|                                              |                                          |
| [Left Rail: StitchSpatialToolbar]            |                                          |
|  - Select / Drag                             |                                          |
|  - Shape / Note tools                        |                                          |
|  - Drawing tools                             |                                          |
|  Position: left-6 top-1/2 -translate-y-1/2   |                                          |
|  Tooltips: left-full ml-2.5 (inward-facing)  |                                          |
|                                              |   [Right Drawer: OrchestratorChatPanel]  |
|                                              |    - Hero Welcome State                  |
|                                              |    - Swarm Skill Pills                   |
|                                              |    - Message Stream                      |
|                                              |    - Collapsed Thought Micro-Chips       |
|                                              |    - Compact Artifact Badges             |
|                                              |    - Floating Studio Input Cockpit       |
|                                              |    Position: fixed top-0 right-0 w-96    |
| [Bottom-Left Cluster]                        |                                          |
|  - StitchAgentLog (left-6 bottom-6)          |                                          |
|  - StitchCanvasControls (left-48 bottom-6)   |                                          |
|    Zoom / Undo / Redo / Minimap              |                                          |
|                                              |                                          |
|                 [Bottom-Center: TimeTravelRail]                                         |
|                  - Minimized Pill by Default                                            |
|                  - Asymmetric Offset: left-[calc(50%-180px)]                            |
|                  - z-30 to avoid occlusion                                              |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Implementation Rules

### Rule 1: Dedicated Right Zone for Orchestrator Cockpit
No floating canvas widgets, inspection palettes, or quick-action bars may be anchored to `right-*` CSS positions unless explicitly scoped within or nested under `OrchestratorChatPanel`. All creative tools belong on the left vertical rail.

### Rule 2: Single SSOT Input Surface
Never present two active natural-language prompt input boxes simultaneously on an infinite canvas view. If `OrchestratorChatPanel` is active, disable or hide secondary floating docks (`StitchPromptDock`).

### Rule 3: Collapsible Secondary Overlays (Time Travel & Timeline Rails)
Large horizontal inspection bars (such as `TimeTravelRail` at 680px width) must initialize in `isMinimized = true` state. They render as a discrete badge `[ ⏱️ Task Forest Rail • LIVE HEAD ⌄ ]` that expands only on user click.

### Rule 4: Progressive Disclosure of AI Execution Streams
- **Thoughts & Reasoning**: Do not auto-expand `expandedAccordions` on every SSE message chunk. Default to collapsed micro-chips (`💭 N міркувань • ⚡ N інструментів`) to preserve conversation readability.
- **Generated Canvas Artifacts**: Render newly created nodes/notes as inline horizontal badges (`[ 📦 gerych_builder ✓ ]`) with flex-wrap rather than multi-line full-width card lists.

### Rule 5: Single SSOT Top Header & Elimination of Floating Canvas Bars
- Never mount floating horizontal toolbars inside child canvas components (e.g., `CanvasEngine.tsx` at `absolute top-4 left-1/2`) when the parent workspace view already mounts a global navigation bar (`StitchTopNav.tsx` at `top-4`).
- Child floating toolbars at the top edge inevitably clash with parent headers across viewport sizes, creating clipped text artifacts and overlapping hitboxes.
- System-wide status indicators (`ObsidianSyncBar`, `SwarmHealthWidget`) must be hoisted into the parent `StitchTopNav` header as first-class citizens.

### Rule 6: Bidirectional Tooltip Inversion on Edge Rails
When a floating toolbar is relocated from a right edge to a left edge (e.g., `left-6`), all hover tooltips and flyout popups must be flipped from `right-full mr-2.5` to `left-full ml-2.5`. This ensures tooltips project inward toward the canvas workspace rather than clipping against or disappearing off the browser window boundary.

### Rule 7: Header Title Truncation & Compact Multi-Widget Spacing
When placing status indicators (such as `ObsidianSyncBar`) inside a top navigation bar next to project metadata, the project title (`<h1>`) MUST have `whitespace-nowrap truncate max-w-[220px]` and `shrink-0`. Secondary badge collections must collapse into compact pills or popovers on viewports < 1440px to prevent title text splitting across multiple vertical lines.

### Rule 8: Dynamic Viewport & History Wire-up Invariant
Bottom-left canvas controls (`StitchCanvasControls`) must dynamically read from `useViewport().zoom` (displaying `Math.round(zoom * 100)%`) rather than static text placeholders. All Undo / Redo buttons must directly invoke `useCanvasStore.getState().undo() / redo()`; never leave stubbed `console.log` handlers.

### Rule 9: Node-to-Drawer Contextual Event Bus (SOTA Paradigm)
In Google Stitch / CapCut workspaces, floating drawers (`StitchSmartInspector`, `StitchTaskForestDrawer`, `StitchShopifyPreviewDrawer`) must not be purely manual toggles. Wire `onNodeClick` in `CanvasEngine.tsx` to automatically route the selected node type to its corresponding contextual drawer.

### Rule 10: Native Browser Tooltip Elimination in Action Bars
In compact icon docks and drawer headers, avoid native HTML `title="..."` attributes when custom Tailwind/CSS hover states or event handlers are attached. Stale native tooltips can linger on canvas repaints and render as orphaned text strings underneath action buttons.
