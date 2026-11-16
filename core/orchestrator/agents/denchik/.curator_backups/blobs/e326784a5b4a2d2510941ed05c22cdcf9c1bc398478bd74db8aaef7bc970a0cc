# ThoughtDAG Slice 2: Staleness Visual Indicators & Branch Propagation Engine

## 1. Overview & Architecture
In the ThoughtDAG context-as-wires architecture, downstream agents and nodes rely on upstream note content for prompt construction. When any upstream note, paragraph, or selection changes, downstream dependencies immediately become desynchronized.

Slice 2 introduces an autonomous graph-staleness detection and visualization engine that:
1. Detects upstream mutations using deterministic cryptographic fingerprints (`upstreamFingerprint`).
2. Propagates staleness recursively across multi-level downstream DAG branches (e.g. Note A -> Agent B -> Agent C).
3. Visually highlights stale wires (edges) and downstream nodes with amber warnings, pulsing glows, and dashed vectors.
4. Provides a 1-click resynchronization mechanism directly on the edge or node (`syncNodeContext`).

---

## 2. Core Staleness Evaluation Algorithm (`evaluateGraphStaleness`)
Location: `apps/web/src/canvas/context/context-builder.ts`

```typescript
export interface GraphStalenessReport {
  staleNodeIds: string[];
  staleEdgeIds: string[];
  nodeStalenessMap: Record<string, boolean>;
  staleBranchCount: number;
}

export function evaluateGraphStaleness(
  nodes: Node[],
  edges: Edge[],
  targetNodeId?: string
): GraphStalenessReport
```

### Invariant Rules:
1. **Upstream Fingerprint Drift**: For every downstream node with incoming wires, compute the current upstream fingerprint via `computeUpstreamFingerprint(node, nodes, edges)`.
2. **Staleness Condition**: A node is stale if `storedFingerprint !== currentFingerprint`.
3. **Wire Staleness**: Any edge terminating at a stale node receives `edge.data.isStale = true`. Furthermore, if an edge originates from an upstream node that is itself stale, the outgoing edge is marked stale to propagate branch staleness down the DAG.
4. **Target Scoping**: If `targetNodeId` is provided, evaluation is optimized to only walk the subgraph rooted at or targeting that node.

---

## 3. UI & Visual Indicators

### A. Context Wires (`apps/web/components/canvas/edges/ContextWireEdge.tsx`)
When `data.isStale === true`:
- **Stroke Color**: Amber `#f59e0b` / `stroke-amber-500` (overrides default purple/blue gradient).
- **Line Style**: Dashed `strokeDasharray: '5 5'` or `'6 4'` indicating broken/outdated synchronization.
- **Filter/Glow**: `filter: drop-shadow(0 0 5px rgba(245, 158, 11, 0.7))` with CSS animation `animate-pulse`.
- **Center Marker Badge**: Amber alert badge with `AlertCircle` / `RefreshCw` icon.
- **1-Click Quick Resync**: Clicking the center badge invokes `syncNodeContext(targetNodeId)`, instantly pulling fresh context without opening menus.

### B. Downstream Nodes (`AgentTaskNode.tsx`, `TextNode.tsx`, `ThoughtDagNoteNode.tsx`)
When `node.data.isStale === true`:
- **Outer Border**: `border-amber-500/80 ring-2 ring-amber-500/40 shadow-[0_0_20px_rgba(245,158,11,0.25)]`.
- **Status Badge**: "Context Stale" / "Context Outdated" amber pill badge.
- **Action Banner**: Prominent banner informing the user that upstream sources were modified, with a direct "Resync" / "Sync & Re-run" trigger button.

---

## 4. Zustand Store Reactive Dispatch & Critical Pitfall

### The Store Action:
In `apps/web/store/canvasStore.ts`:
- `refreshNodeStaleness(nodeId?)`: runs `evaluateGraphStaleness`, updating both `nodes` and `edges` state atomically, returning `{ staleCount, updatedNodeIds, staleEdgeIds }`.
- `syncNodeContext(nodeId)`: compiles fresh prompt context, computes new `upstreamFingerprint`, sets `isStale: false` on the target node, and clears `isStale` on all incoming edges.

### ⚠️ CRITICAL PITFALL: Auto-Staleness Override during `updateNodeData`
When attaching an automatic staleness check to node content edits in `updateNodeData`:

```typescript
// ❌ WRONG: Overwrites explicit isStale flags
const hasContentChange = Boolean(
  patch.content !== undefined ||
  patch.title !== undefined ||
  patch.selectedText !== undefined
);
if (hasContentChange) {
  get().refreshNodeStaleness(); // Root notes have 0 incoming edges, so isNodeStale evaluates to false!
}

// ✅ CORRECT: Guard against explicit isStale overrides
const hasContentChange = Boolean(
  (patch.content !== undefined ||
  patch.title !== undefined ||
  patch.selectedText !== undefined ||
  patch.highlightMode !== undefined ||
  patch.blocks !== undefined) &&
  patch.isStale === undefined // Preserves caller's explicit staleness intent!
);
if (hasContentChange) {
  get().refreshNodeStaleness();
}
```

Without the `patch.isStale === undefined` guard, any unit test or external controller attempting to set `store.updateNodeData(rootNodeId, { selectedText: '...', isStale: true })` will immediately have its `isStale: true` overwritten back to `false` because root nodes with zero incoming edges evaluate to non-stale in graph algorithms.

---

## 5. Verification Command
```bash
npx tsx --test apps/web/src/canvas/nodes/__tests__/staleness-indicators.test.ts
npm --prefix apps/web run type-check
```

---

## 6. Live Interactive Canvas Invariants & Reactive Staleness Pitfalls

### A. Interactive Input Debounce vs onBlur Flush Invariant
- **The Pitfall**: In living canvas nodes (e.g. `ThoughtDagNoteNode`), synchronizing text changes exclusively via `onBlur` breaks real-time reactivity. While a user is typing, the textarea retains focus, so `onBlur` never fires, leaving downstream staleness detection and amber glow indicators inert.
- **The Pattern**: Implement a debounced auto-sync (e.g. 200ms `useEffect` with cleanup) that calls `updateNodeData(id, { content, updatedAt })` on the fly, complemented by `onBlur` as an immediate flush for instant transitions.

### B. Initial Upstream Baseline Fingerprint Invariant
- **The Pitfall**: In DAG staleness engines where `isNodeStale` checks `storedFingerprint !== currentFingerprint`, if downstream agent nodes in the initial state or template are spawned without an `upstreamFingerprint` (`undefined`), downstream staleness checks fail to trigger on subsequent upstream edits because there is no baseline to compare against.
- **The Pattern**: Ensure initial mock nodes or workspace templates compute and store the baseline `upstreamFingerprint` via `computeUpstreamFingerprint(nodeId, nodes, edges)`. During workspace hydration, scan downstream nodes lacking fingerprints and initialize them.

### C. Edge Lifecycle Staleness Refresh Invariant (`onConnect` / `connectContextWire`)
- **The Pitfall**: When a user connects a wire between an upstream note and a downstream agent, the edge list updates, but staleness flags are not re-evaluated until a subsequent node mutation occurs.
- **The Pattern**: In `onConnect` and `connectContextWire` store actions, immediately invoke `get().refreshNodeStaleness()` following `set({ edges: nextEdges })` so newly wired dependencies reflect their true synchronization state instantly.

