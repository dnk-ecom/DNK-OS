# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/canvas-engine-architecture/references/thoughtdag_infinite_canvas_context_engineering_patterns.md"
# purpose: "Assimilation reference for ThoughtDAG: Wires as Context, Note Requirement Nodes, and Staleness Fingerprints on Infinite Canvas."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🌐 ThoughtDAG Context Engineering & Infinite Palette Patterns

## 1. Core Principle: "Wires are the Context"
In traditional chat interfaces, conversation context is a rigid chronological transcript. On the ThoughtDAG infinite palette:
- **Edges control prompt composition**: What an agent receives on its turn is strictly determined by its incoming DAG edges.
- **Layered Partition Order**:
  1. `materials`: Content nodes (`note`, `file`, `link`) wired via outgoing edges.
  2. `reference blocks`: Dashed edges to other branches/conversations (`[Reference: Title]`).
  3. `live chain`: Solid edges representing topological ancestor conversation turns.
  4. `current query / directive`: Leaf node prompt.

## 2. Requirement Notes (`ContentNode: note` / `ThoughtDagNoteNode`)
- Human operators write requirements, target audience constraints, and brand guidelines as markdown cards.
- Content nodes do not generate on their own; they supply context via outgoing edges.
- **Invariant 1: First-Class ReactFlow Node (NOT WhiteboardElement)**:
  Living notes MUST be registered as first-class ReactFlow nodes (`ThoughtDagNoteNode`, type `thoughtDagNote`) and stored in `CanvasState.nodes`. They must NEVER be relegated to `whiteboardElements`, ensuring they participate fully in the DAG connection graph, selection state, history stack, and delta queueing.
- **Invariant 2: Wire Directionality (Source = Note, Target = Agent)**:
  Wires MUST originate from the Note and connect to downstream Swarm Agents (`source: noteId`, `target: agentId`). The Note provides source handles (`source-bottom`, `source-right`) and upstream target handles (`target-top`, `target-left`). Downstream agents collect active context (`selectedText` or full content) along their incoming edges.
- **Data Model Schema (`ThoughtDagNoteData`)**:
  - `title: string`
  - `content: string`
  - `selectedText?: string` (active context snippet for downstream agent)
  - `highlightMode: 'filter' | 'tag' | 'off'`
  - `tag?: string`
  - `upstreamFingerprint?: string` (SHA-256 hash of upstream contents)
  - `isStale?: boolean`
  - `author: string`
  - `updatedAt: number`
- **Store Actions (`useCanvasStore`)**:
  - `addThoughtDagNote(x, y, initialContent?, initialData?)`: Spawns living note node, selects it, updates history, and queues delta.
  - `setNoteHighlightMode(nodeId, mode)`: Toggles between `'filter' | 'tag' | 'off'`.
- **Highlight Filtering (`highlightMode: 'filter' | 'tag' | 'off'`)**:
  - `filter`: Extracts only highlighted sentences from a requirement note into the agent prompt, eliminating prompt bloat.
  - `tag`: Wraps highlighted text in `[Important] ... [/Important]` tags.
  - `off`: Standard markdown card.
- **Headless Unit Verification**: Test note creation, edge connectivity, and highlight mode mutations with `npx tsx --test apps/web/src/canvas/nodes/__tests__/thoughtdag-node.test.ts`.

## 3. Staleness Fingerprinting & Context Builder Engine
- Deterministic FNV-1a hash algorithm (`deterministicHash(str)`) works identically across Node.js and browser runtimes without requiring external crypto dependencies:
  ```typescript
  export function deterministicHash(input: string): string {
    let hash = 0x811c9dc5;
    for (let i = 0; i < input.length; i++) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193);
    }
    return (hash >>> 0).toString(16).padStart(8, '0');
  }
  ```
- **Context Builder Engine (`apps/web/src/canvas/context/context-builder.ts`)**:
  - `extractEffectiveNoteContent(noteData, edgeScope)`: respects `highlightMode` (`filter`: strictly `selectedText`, `tag`: wraps with `[Important: tag]...[/Important]`, `off`: full content).
  - `getUpstreamAncestors(targetNodeId, nodes, edges)`: walks incoming wires against the flow (`edge.target === targetId`), prevents infinite cycles via visited set, and returns nodes topologically ordered from root materials to direct parents.
  - `partitionContext(...)`: organizes context into `materials` (`thoughtDagNote`), `references` (cross-chain citations), and `mainline` (sequential conversation history).
  - `buildContextFromWires(targetNodeId, nodes, edges, options)`: returns `BuildContextResult` containing structured `messages`, `sources`, and unified `assembledPrompt`.
  - `computeUpstreamFingerprint(targetNodeId, nodes, edges)`: computes compound hash of ancestor IDs, contents, and update timestamps.
  - `isNodeStale(targetNode, nodes, edges)`: flags true if current fingerprint diverges from `node.data.upstreamFingerprint`.
- **Zustand Store Actions (`useCanvasStore`)**:
  - `compileNodeContext(nodeId, options)`: compiles full prompt and message bundle for target agent node.
  - `refreshNodeStaleness(nodeId?)`: recomputes fingerprint and updates `isStale` flag across canvas nodes.
- **Headless Unit Verification**:
  - Slice 1 (Node & Store): `npx tsx --test apps/web/src/canvas/nodes/__tests__/thoughtdag-node.test.ts`
  - Slice 2 (Context Builder & Staleness): `npx tsx --test apps/web/src/canvas/context/__tests__/context-builder.test.ts`
  - Slice 3 (UI Components, Wires & Stale Sync): `npx tsx --test apps/web/src/canvas/ui/__tests__/thoughtdag-slice3-ui.test.ts`
  - Slice 4 (Backend CONTRACT-002 Models & Compilation API): `.venv/bin/pytest tests/api/test_thoughtdag_api.py -v`

## 4. Slice 3 UI Components, Context Wires & Stale Syncing
- **`ContextWireEdge` (`apps/web/components/canvas/edges/ContextWireEdge.tsx`)**:
  - Custom SVG path with gradient stroke `#8b5cf6` to `#3b82f6` representing context transmission.
  - Interactive pill badge displaying wire scope (`ALL` or `SELECTION`). Clicking toggles between `all` (full markdown card) and `selection` (only highlighted text).
  - Shows animated pulse along the wire when downstream agent is compiling or executing.
- **`AgentTaskNode` Stale Alert & Sync Action (`apps/web/components/canvas/AgentTaskNode.tsx`)**:
  - Detects `data.isStale === true` and renders an amber warning pill badge: `"Stale Context"`.
  - Provides a one-click `"Sync & Re-run"` button triggering `compileNodeContext(node.id)` and `dispatchSwarmTask()` to re-execute agent with fresh upstream context.
- **`ThoughtDagNoteNode` Selection Capture (`apps/web/components/canvas/nodes/ThoughtDagNoteNode.tsx`)**:
  - Captures operator text selections via `document.getSelection()` and updates `selectedText` in store.
  - Quick action toolbar to switch `highlightMode` (`filter` vs `tag` vs `off`) and edit tags inline.
- **Headless Test Invariant (Store Background Sync Timer Guard)**:
  - In Zustand store background sync methods (`flushDeltaSync`, network sync, interval polling), ALWAYS check:
    ```typescript
    if (process.env.NODE_ENV === 'test' || typeof window === 'undefined') {
      return;
    }
    ```
  - Without this guard, unresolved asynchronous `setTimeout` or `fetch` operations keep Node.js event loop active, causing `tsx --test` or `node:test` to hang indefinitely (exit code 124 timeout).

## 5. Slice 4 Backend Models & Compilation API (CONTRACT-002)
- **Domain Models (`core/domain/dag_models.py`)**:
  - `NodeKind` (`agent`, `thoughtDagNote`, `prompt`, `artifact`), `ContextStatus` (`fresh`, `stale`, `unknown`), `Wire` (`from_node`/`to_node` with JSON aliases `from`/`to`, `scope: 'all' | 'selection'`).
  - Strict Pydantic v2 validation.
  - Kahn's algorithm implementation for topological sort and cycle detection: raises `ValueError("Cycle detected in ThoughtDAG: ...")` if cycle exists.
  - Compound SHA256 upstream fingerprinting across all ancestors.
  - Bidirectional Obsidian JSON Canvas transpiler (`to_obsidian_canvas()`).
- **FastAPI Endpoints (`apps/api/routers/thoughtdag_router.py`)**:
  - `POST /api/v1/thoughtdag/compile`: Validates DAG, performs topological sort, partitions context (`materials`, `references`, `mainline`), and returns compiled prompt bundle.
  - `POST /api/v1/thoughtdag/staleness-check`: Recomputes fingerprints and flags stale nodes across graph.
  - `POST /api/v1/thoughtdag/transpile/obsidian`: Converts ThoughtDAG into `.canvas` JSON.
  - `GET /api/v1/thoughtdag/health`: Read-only healthcheck.

## 6. Multi-Agent Session Atlas & Inline Approvals
- Bridges external CLI and background agent runs (Claude Code, Codex, DeepSeek Harness, DNK Swarm workers) onto visual canvas turns.
- Inline `ApprovalRequest` / `ApprovalRecord` cards render human-in-the-loop decisions directly on living nodes before tool execution proceeds.

## 5. Spatial Wayfinding Frames (`FrameNode`)
- Background regions (`stepKind: 'frame'`) organize ideation phases (e.g. `[Hooks]`, `[Scripts]`, `[Ecom Assets]`).
- `frameCarry: true` ensures dragging the frame moves all contained requirement and agent nodes cohesively.
