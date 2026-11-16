# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/spatial_canvas_controls_and_node_drawer_event_bus.md"
# purpose: "Architecture patterns for dynamic zoom, history gating, node-to-drawer event bus routing, and sticky tooltip prevention."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# Spatial Canvas Controls & Node-to-Drawer Event Bus

## 1. Dynamic Zoom Viewport vs Static Mock Scale
- **Anti-Pattern**: Hardcoded zoom scale indicators (e.g. fixed `23%`) in canvas HUD controls.
- **Implementation**:
  - Connect directly to ReactFlow's reactive hook `const { zoom } = useViewport()`.
  - Format the scale dynamically: `const zoomPct = Math.round((zoom || 1) * 100)`.
  - Wire the percentage badge click to `fitView({ padding: 0.2, duration: 400 })` to center and bound the active scene.

## 2. Undo / Redo Zustand Integration & Defensive Gating
- Connect canvas history actions directly to the store:
  ```tsx
  const { undo, redo, canUndo, canRedo } = useCanvasStore();
  ```
- Guard buttons with `disabled={!canUndo}` and apply conditional styling (`opacity-30 cursor-not-allowed`) to prevent invalid history dispatch.

## 3. Node-to-Drawer Event Bus Invariant
In spatial multi-modal canvases, clicking heterogeneous nodes (`onNodeClick` in `ReactFlow`) must programmatically route to corresponding contextual drawers rather than leaving them disconnected:
- **Shopify / Ecom nodes** (`shopifySpecNote`, `dnk_shopify`) -> Open `StitchShopifyPreviewDrawer`
- **Task Forest / Agent task nodes** (`agentTaskNode`, `taskForestNode`) -> Open `StitchTaskForestDrawer`
- **Video Storyboard nodes** (`videoStoryboardNote`) -> Expand `StitchKineticTimeline`
- **Swarm / Cluster nodes** (`swarmHubNode`) -> Open `StitchSwarmCommandCenter`
- **Artboard / Design frames** (`StitchArtboardNode`) -> Focus `StitchSmartInspector`

## 4. Interactive Tool Spawning (Zero Dead-Clicks)
Spatial toolbars (`StitchSpatialToolbar`) must not terminate on local tool selection state alone:
- Tool activation (`Frame`, `Image`, `Templates`) should trigger `addNode(nodeType, position, initialData)`.
- Apply a small jitter offset (`offset = Math.floor(Math.random() * 60) - 30`) to prevent newly added nodes from perfectly stacking over existing items.

## 5. Sticky OS Tooltip Elimination
- Avoid native HTML `title="..."` attributes on buttons inside dense floating canvas widgets (such as chat panels or action docks). Native desktop window managers often leave `title` tooltips stuck on screen across canvas drags and focus transitions.
- Use `aria-label` or managed React popover tooltips instead.

## 6. Top Bar Spatial Collision & Layout Pill Consolidation
- Floating navigation bars (`StitchTopNav`) must enforce `whitespace-nowrap truncate max-w-[200px] shrink-0` on project title blocks.
- Secondary integration widgets (such as Obsidian 2-way sync bars) must collapse into compact status pills with on-click popovers rather than consuming wide horizontal strips (400px+) that squash board titles.
