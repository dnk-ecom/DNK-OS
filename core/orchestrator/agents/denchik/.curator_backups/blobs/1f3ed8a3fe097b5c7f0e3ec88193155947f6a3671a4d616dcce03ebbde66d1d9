# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/spatial_ui_mvr_reactflow_and_approval_patterns.md"
# purpose: "Technical Architecture & Operational Patterns for MVR Spatial UI (ReactFlow + Next.js + HITL Approval Gate)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-10"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Spatial UI MVR: ReactFlow v11+, Zustand Store & HITL Approval Modal Architecture

## 1. Executive Pattern
The DNK OS MVR Spatial UI provides an interactive 2D spatial canvas that maps plugins, swarm agents, and system services into an interconnected topological graph with real-time bidirectional synchronization and a fail-closed Human-in-the-Loop (HITL) approval gate.

## 2. Component Topology (Next.js 14/15 App Router + ReactFlow v11+)
- **CanvasContainer (`apps/web/components/canvas/CanvasContainer.tsx`)**:
  - Encapsulates `<ReactFlowProvider>` with `<ReactFlow>` viewport.
  - Native integration of `<Background variant={BackgroundVariant.Dots}>`, `<Controls>`, and `<MiniMap>`.
  - Floating toolbar for spatial actions (Auto-Layout, OCC Resync, Filter, Reset Viewport).
- **Custom Node Hierarchy**:
  - `PluginNode`: Displays plugin lifecycle status (`Active`, `Sandbox`, `Deprecated`), health radial gauge, and capability socket badges.
  - `AgentNode`: Displays autonomous swarm agent identity (`gerych_builder`, `dnk_shopify`, etc.), status beacon, and active TaskDNA subtask.
  - `ServiceNode`: Core infrastructure services (`TaskDNA`, `SCONES Memory`, `Audit Engine`).
- **Custom Edge Hierarchy**:
  - `DependencyEdge`: Static architectural dependency (solid bezier line).
  - `DataflowEdge`: Active telemetry or event streaming (animated pulsing dash array).
  - `CapabilityEdge`: Semantic matching between plugin demands and service supplies.

## 3. Zustand Reactive Store Pattern (`useCanvasStore`)
- Decouples ReactFlow presentation from WebSocket event dispatching.
- **Optimistic Concurrency Control (OCC)**:
  - Client performs instant UI state mutation (node drag, property edit).
  - Generates client-side version token and dispatches over WebSocket (`/ws/canvas`).
  - If backend reports `OCC_VERSION_MISMATCH`, UI triggers a non-destructive toast notification and rolls back to server SSOT.
- **Performance Budget**:
  - Node rendering wrapped in `React.memo` with custom shallow props comparison.
  - Viewport culling (`onlyRenderVisibleElements={true}`) to maintain 60 FPS up to 250+ concurrent nodes.

## 4. Human-in-the-Loop (HITL) Approval Modal Pattern
- **Fail-Closed Security Invariant**: Any operation classified as `HIGH` or `CRITICAL` risk (e.g. destructive node deletion, live production config modification, billing/payment actions) is intercepted before execution.
- **ApprovalRequest Lifecycle**:
  - `PENDING` -> `APPROVED` | `REJECTED` | `TIMEOUT` | `ESCALATED`.
  - Default action on network loss, disconnection, or countdown expiry is `TIMEOUT` (treated as `REJECTED`).
- **UX & Ergonomics**:
  - Side-by-side JSON/AST diff viewer highlighting exact delta.
  - Keyboard shortcuts: `Enter` to approve, `Escape` to reject with mandatory feedback rationale.
  - Cryptographic signature / token generated upon approval for tamper-evident audit logging.
