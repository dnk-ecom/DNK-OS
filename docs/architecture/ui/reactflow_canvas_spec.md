---
title: "ReactFlow Canvas Technical Specification"
description: "Technical Component & State Architecture for ReactFlow Spatial Canvas in DNK OS"
mrh_id: "docs/architecture/ui/reactflow_canvas_spec.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/ui/reactflow_canvas_spec.md"
> purpose: "Technical Component & State Architecture for ReactFlow Spatial Canvas in DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧩 ReactFlow Canvas Technical Specification

> **Parent Spec:** `docs/ui/DNK_OS_SPATIAL_UI_SPEC_v1.0.md`  
> **Engine:** ReactFlow v11+ (@xyflow/react)  
> **Scope:** Spatial Canvas Container, Custom Nodes, Custom Edges, Store Architecture & Viewport Sync  

---

## 1. Architectural Overview

The Spatial Canvas is built on **ReactFlow v11+**, providing a GPU-accelerated, virtualized 2D plane for orchestrating DNK OS entities. It interfaces directly with a dedicated **Zustand store** (`useCanvasStore`), separating high-frequency rendering logic from backend communication.

```
+--------------------------------------------------------------------------------+
|                             ReactFlow Viewport                                 |
|                                                                                |
|   +-----------------------+                    +---------------------------+   |
|   | PluginNode: Shopify   |                    | AgentNode: Gerych Prime   |   |
|   | • Kind: E-commerce    |--[DataflowEdge]--> | • Role: Swarm Manager     |   |
|   | • Health: 99% (Active)|                    | • Status: Orchestrating   |   |
|   +-----------------------+                    +---------------------------+   |
|              |                                               |                 |
|              +-----------------[DependencyEdge]--------------+                 |
|                                                                                |
+--------------------------------------------------------------------------------+
                                       |
                   [State Actions: onNodesChange / onEdgesChange]
                                       v
+--------------------------------------------------------------------------------+
|                         Zustand Store (useCanvasStore)                         |
|  • nodes: CanvasNodeData[]                                                     |
|  • edges: CanvasEdgeData[]                                                     |
|  • selectedNodeId: string | null                                               |
|  • optimisticQueue: Map<string, MutationEvent>                                 |
|  • serverVersion: number                                                       |
+--------------------------------------------------------------------------------+
                                       ^
                                       | [Full-Duplex WS Streaming]
                                       v
+--------------------------------------------------------------------------------+
|                   Backend Canvas Control Plane (/ws/canvas)                    |
+--------------------------------------------------------------------------------+
```

---

## 2. Component Hierarchy & Layout

```
apps/web/src/components/canvas/
├── CanvasContainer.tsx       # Root wrapper with ReactFlowProvider & event dispatchers
├── CanvasViewport.tsx        # Inner ReactFlow renderer with Controls & MiniMap
├── Toolbar.tsx               # Floating command toolbar (Zoom, Fit, Layout, Add Node)
├── nodes/
│   ├── BaseNode.tsx          # Shared container, handles, status pill, context trigger
│   ├── PluginNode.tsx        # Specialized node for Plugin Registry components
│   ├── AgentNode.tsx         # Specialized node for autonomous Swarm agents
│   └── ServiceNode.tsx       # Specialized node for core OS microservices
├── edges/
│   ├── DependencyEdge.tsx    # Solid bezier line for structural prerequisites
│   ├── DataflowEdge.tsx      # Animated marching-ants stroke for live messages
│   └── CapabilityEdge.tsx    # Dotted line for capability graph bindings
└── overlays/
    ├── ContextMenu.tsx       # Right-click contextual actions
    └── NodeInspector.tsx     # Quick flyout preview on node hover
```

---

## 3. Custom Node Types Specification

Every custom node implements standard handles using `@xyflow/react` `<Handle />` components.

### 3.1 `PluginNode`
Represents an assimilated or custom DNK OS Plugin:
- **Visual Design**:
  - Border: 1.5px solid Zinc-800 with subtle rounded corners (`rounded-xl`).
  - Dark mode background: Slate-900 / Zinc-950 with 85% opacity (`backdrop-blur-md`).
  - Header: 18px Lucide icon (e.g. `ShoppingBag` for Shopify, `Database` for Storage).
  - Version & License: Small typography badge (`v1.2.0 • MIT`).
  - Health Gauge: Micro radial progress indicator displaying current health score (0–100%).
- **Handles**:
  - `Target` (Input): Position Top (`Position.Top`), accepts input capabilities.
  - `Source` (Output): Position Bottom (`Position.Bottom`), emits output capabilities.

### 3.2 `AgentNode`
Represents an autonomous Swarm worker (`gerych_builder`, `gerych_auditor`, etc.):
- **Visual Design**:
  - Border: Accent purple/indigo outline with subtle pulse effect when executing.
  - Avatar / Icon: `Bot` or `Cpu` with role indicator pill (`Auditor`, `Builder`, `Prime`).
  - Active Task Indicator: Real-time ticker showing current slice or subtask description.
- **Handles**:
  - Multiple connection points for parallel collaboration channels.

### 3.3 `ServiceNode`
Represents system-level infrastructure (`TaskDNA Engine`, `SCONES Memory`, `Audit Engine`):
- **Visual Design**:
  - Monochromatic slate styling with gear/network icon.
  - Uptime and memory footprint ticker (`99.9% • 34MB`).

---

## 4. Custom Edge Types Specification

Edges represent semantic relationships between entities:

| Edge Type | SVG Stroke Style | Color Token | Animation | Semantic Meaning |
|---|---|---|---|---|
| **DependencyEdge** | Solid (stroke-width: 2) | `#71717a` (Zinc-500) | None | Node A requires Node B before initialization. |
| **DataflowEdge** | Dashed (stroke-dasharray: 5,5) | `#10b981` (Emerald-500) | Marching Ants (CSS keyframes) | Active payload streaming between nodes. |
| **CapabilityEdge** | Dotted (stroke-dasharray: 2,4) | `#6366f1` (Indigo-500) | Pulse on invocation | Dynamic capability binding resolved by graph. |

---

## 5. Zustand Store Architecture (`useCanvasStore`)

The canvas state is managed decoupled from UI rendering cycles to guarantee sub-100ms updates.

### TypeScript Contract:

```typescript
export type NodeKind = 'plugin' | 'agent' | 'service';
export type NodeStatus = 'active' | 'sandbox' | 'deprecated' | 'error';

export interface CanvasNodePayload {
  id: string;
  name: string;
  kind: NodeKind;
  version: string;
  license: string;
  healthScore: number;
  status: NodeStatus;
  capabilities: {
    inputs: string[];
    outputs: string[];
  };
  metrics?: {
    latencyP95Ms: number;
    errorRate: number;
    invocations: number;
  };
}

export interface CanvasEdgePayload {
  id: string;
  source: string;
  target: string;
  kind: 'dependency' | 'dataflow' | 'capability';
  label?: string;
  throughputMsgSec?: number;
}

export interface CanvasStoreState {
  canvasId: string;
  serverVersion: number;
  nodes: Node<CanvasNodePayload>[];
  edges: Edge<CanvasEdgePayload>[];
  selectedNodeId: string | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting';
  
  // Actions
  setNodes: (nodes: Node<CanvasNodePayload>[]) => void;
  setEdges: (edges: Edge<CanvasEdgePayload>[]) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  selectNode: (nodeId: string | null) => void;
  updateNodePositionOptimistic: (nodeId: string, position: { x: number; y: number }) => void;
  applyServerSnapshot: (snapshot: { version: number; nodes: Node[]; edges: Edge[] }) => void;
  reconcileConflict: (resolvedState: { version: number; nodes: Node[]; edges: Edge[] }) => void;
}
```

---

## 6. Auto-Layout Integration (Dagre / ELK)

To maintain clarity in complex multi-agent graphs:
- **Hierarchical Layout (Dagre)**:
  - Directed Acyclic Graph (DAG) auto-ordering from left-to-right (`rankdir: 'LR'`) or top-to-bottom (`rankdir: 'TB'`).
  - Node separation: `nodeSep: 50`, Rank separation: `rankSep: 80`.
  - Triggered via Toolbar action: *"Auto-Arrange Graph"*.
- **Physics / Force-Directed (ELK)**:
  - Applied for exploratory clusters where loose capability rings are preferred over strict hierarchy.

---

## 7. Performance & Rendering Budgets

1. **60 FPS Pan & Zoom**: Achieved through CSS transforms (`will-change: transform`) and GPU composite layers.
2. **Viewport Frustum Culling**:
   - `onlyRenderVisibleElements={true}` enabled on `<ReactFlow />`. Nodes outside visible bounding box are detached from DOM tree.
3. **Memoized Components**:
   - Every custom node component is wrapped in `React.memo` with strict shallow property comparison.
   - Event callbacks are memoized via `useCallback` to prevent unnecessary node re-renders during panning.
