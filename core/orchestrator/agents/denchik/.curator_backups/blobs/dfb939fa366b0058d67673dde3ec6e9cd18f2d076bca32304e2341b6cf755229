# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/thoughtdag_smart_context_and_dag_reevaluation.md"
# purpose: "Technical reference for Smart Context Gathering, Token Budgeting, SCONES Injection & DAG Re-evaluation Engine (Slice 3)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# ThoughtDAG: Smart Context Gathering & DAG Re-evaluation Engine

## 1. Architectural Overview

ThoughtDAG Slice 3 provides the execution and context compilation layer that translates spatial wires into LLM prompt contexts and coordinates multi-level DAG re-evaluations when upstream notes are modified:

1. **Topological Level Planner (`getReevaluationPlan`)**:
   - Computes in-degrees and uses Kahn's algorithm to partition the DAG into ordered levels (`levels: string[][]`).
   - Nodes in the same level can execute in parallel without dependency hazards.
   - Selective re-evaluation via `onlyStale: true` filters the execution set to only nodes that are stale (`isStale: true`) or downstream of modified nodes.
   - Scoped execution via `targetNodeId` limits execution to a target node and its required upstream/downstream subgraph.

2. **Smart Context Gathering (`gatherSmartContext`)**:
   - Walks upstream wires connected to a target node (`target-top` or `target-left`).
   - Resolves block-level handles (`handle-block-${id}`) or active text selections to extract targeted paragraphs rather than entire notes.
   - Enforces a strict token budget (`maxTokens`, default: 4,000 tokens) using character heuristics (~4 chars/token).
   - Pruning strategies:
     - `prioritize_near`: Truncates distant ancestors first, preserving direct parent nodes.
     - `prioritize_blocks`: Preserves fine-grained block selections, truncating full document bodies.
     - `truncate_tail`: Retains top of assembled context and appends `\n[... Truncated to fit token budget ...]`.

3. **SCONES Memory Injection**:
   - Injects long-term episodic and semantic memory retrieved from SCONES into the compiled context:
     ```markdown
     ### Long-Term Episodic Memory (SCONES)
     > **[Topic]** (Relevance: 0.95)
     Content of memory...
     ```
   - Formats memories cleanly before node context sections so LLM models ground actions in canonical invariants.

4. **Async DAG Execution Engine (`executeDAGReevaluation`)**:
   - Executes nodes level-by-level using `Promise.all`.
   - Before evaluating each node, compiles fresh smart context (`gatherSmartContext`).
   - Calls the user-supplied `evaluateNodeFn(node, context, signal)`.
   - On completion of each node:
     - Updates `node.data.response` and `node.data.lastExecutedAt`.
     - Recomputes `node.data.upstreamFingerprint = context.fingerprint`.
     - Sets `node.data.isStale = false`.
     - Clears incoming edge staleness: `edge.data.isStale = false`.
   - Fires `onProgress` callbacks with current phase (`planning`, `gathering`, `evaluating`, `complete`, `cancelled`, `error`).
   - Respects `AbortSignal` for user cancellation.

## 2. Zustand Store Integration Patterns

```typescript
// Triggering DAG Re-evaluation from a component:
const runDAGReevaluation = useCanvasStore((state) => state.runDAGReevaluation);
const isReevaluating = useCanvasStore((state) => state.isReevaluating);
const progress = useCanvasStore((state) => state.reevaluationProgress);

// In button handler:
await runDAGReevaluation({
  targetNodeId: node.id, // optional: target specific node subtree
  onlyStale: true,       // only re-run stale nodes
  sconesMemories: activeSconesMemories,
});
```

## 3. Test & Import Invariants

- **`@xyflow/react` vs `reactflow`**:
  In modern Next.js / TypeScript setups with `@xyflow/react`, headless tests in `tsx` must import types directly from `@xyflow/react`:
  ```typescript
  import type { Node, Edge } from '@xyflow/react';
  ```
- **Cycle Detection**:
  Kahn's algorithm detects cycles if `visitedCount < nodes.length`. When a cycle is detected, fallback to remaining nodes ensures no infinite loop or crash occurs during execution.
- **Atomic State Updates**:
  Always update nodes and edges simultaneously in the store (`set({ nodes: updatedNodes, edges: updatedEdges })`) to prevent tearing between wire visual states and node badges.
