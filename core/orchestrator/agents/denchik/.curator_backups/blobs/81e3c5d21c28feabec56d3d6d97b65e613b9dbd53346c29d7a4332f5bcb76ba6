# --- DNK-MRH-HEADER ---
# mrh_id: "skills_canvas_engine_references_tributary_causal_tree"
# purpose: "Tributary (支流) Causal Tree Algebra, Dynamic 2D Layout & Reactive Stream Bus Patterns"
# author: "DNK-e.com Maksym & Gerych Prime"
# status: "Active"
# version: "1.0.0"
# --- END DNK-MRH-HEADER ---

# Tributary Causal Tree Algebra, Dynamic 2D Layout & Reactive Stream Bus

Assimilated from `ximing/tributary` (支流) monorepo (`packages/domain`, `apps/server`, `apps/desktop`).

## 1. Causal Lineage Isolation (`messagesForNode`)

In non-linear branching conversation and multi-agent DAGs, flat linear context causes context pollution and hallucination across parallel sibling branches.

### Pattern Implementation
```typescript
export function messagesForNode(
  tree: TreeNode[],
  targetNodeId: string
): Message[] {
  const nodeMap = new Map(tree.map(n => [n.id, n]));
  const lineage: TreeNode[] = [];
  let curr = nodeMap.get(targetNodeId);

  // Ascend strictly along parentId links to root
  while (curr) {
    lineage.unshift(curr);
    curr = curr.parentId ? nodeMap.get(curr.parentId) : undefined;
  }

  // Linear clean causal history (Zero Crosstalk from sibling branches)
  return lineage.flatMap(node => node.messages);
}
```

**Key Invariant**: Sibling nodes and competing agent branches are never passed into the active node prompt.

---

## 2. Dynamic 2D Tree Layout Algorithm (`layout.ts`)

Pure functional positioning algorithm for branching mind-maps and node graphs without edge collision.

### Key Rules
1. **Directional Flexibility**: Supports both Horizontal (`LR` - left-to-right) and Vertical (`TB` - top-to-bottom).
2. **Subtree Extent Measurement**: Each branch computes its recursive bounding box (sum of child extents + margins).
3. **Parent Centering**: Parent node coordinate along the transversal axis is placed at the arithmetic mean of its first and last child's center coordinates:
   $$Y_{parent} = \frac{Y_{child\_first} + Y_{child\_last}}{2}$$
4. **Column Alignment**: Depth determines the primary coordinate ($X = depth \times (nodeWidth + horizontalGap)$), while sibling spacing prevents overlap.

---

## 3. Dual-Layer Event Stream Bus (`stream-bus.ts`)

Decoupled execution streaming for multi-agent canvases:
- **In-Process Fan-Out**: `StreamHub` with registered `Set<(event) => void>` listeners for low-latency (<5ms) subagent event propagation.
- **Inter-Process / Cluster Notification**: PostgreSQL `pg_notify('tributary_node', nodeId)` triggers worker notifications across backend processes without polling.
- **Client Transport**: SSE (Server-Sent Events) push reactive execution tokens and lifecycle updates to the canvas frontend (`apps/web` or Tauri desktop).

---

## 4. Tauri v2 Desktop Bridge

- Monorepo package `apps/desktop` wraps Vite/React Flow via Tauri v2 (`src-tauri`).
- Background worker processes run locally or connect to the server via SSE/WebSocket, keeping memory footprint low.
