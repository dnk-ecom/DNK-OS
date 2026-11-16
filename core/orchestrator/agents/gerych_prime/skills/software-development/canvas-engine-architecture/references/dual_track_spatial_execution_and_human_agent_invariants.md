# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/dual_track_spatial_execution_and_human_agent_invariants.md"
# purpose: "Dual-Track Spatial Execution & Human-Idea Agent-Executor Invariants (LOD 0/1 Fast-Path vs LOD 2/3 Heavy-Path)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🌐 Dual-Track Spatial Execution & Human-Idea Agent-Executor Invariants

## 1. Problem Statement: Latency Stacking & The Full-Cycle Cascade Trap
In an agentic spatial canvas where "Human = Ideas, Agents = Executors", executing every idea through the monolithic pipeline:
```
[ Canvas Note ] ➔ [ ThoughtDAG Compiler ] ➔ [ Gerych Harness ] ➔ [ Subagent FastMCP ] ➔ [ Adversarial Auditor Gate ] ➔ [ Generative UI ]
```
creates an unacceptable latency penalty:
- 3–4 sequential LLM inference hops (15–45s minimum wall-clock latency).
- High token burn on micro-iterations (e.g. tweaking a button style, editing single parameter).
- Risk of OCC 3-way merge race conditions if the human continues editing the graph while a subagent operates asynchronously.

## 2. The Dual-Track Execution Invariant

### Track 1: Fast-Path (LOD 0 / LOD 1 — Direct Micro-Execution)
- **Trigger**: Single-node edits, property alterations, direct tool calls, single asset generation, text refinement.
- **Workflow**:
  1. Human mutates node / inputs inline prompt.
  2. Bypasses ThoughtDAG DAG compilation and Adversarial Gate.
  3. Direct dispatch to specialized FastMCP tool via `core/framework/fastmcp_dispatcher.py` or direct action adapter.
  4. Latency ceiling: < 2.0s.
  5. UI state updates immediately with optimistic visual state.

### Track 2: Heavy-Path (LOD 2 / LOD 3 — Full Evolutionary Swarm Pipeline)
- **Trigger**: Multi-node canvas branches, multi-file code synthesis, store-wide theme refactors, full marketing campaigns.
- **Workflow**:
  1. Human tags node/group as Epic or triggers multi-step swarm execution.
  2. ThoughtDAG Compiler extracts upstream context wires and formalizes explicit `Negative Scope`.
  3. Gerych Harness partitions into TaskDNA DAG slices (<= 25 tool calls/slice).
  4. Swarm domain workers execute isolated slices.
  5. Adversarial Auditor Gate validates deterministic quality gates (100% green tests, lint, AST check).
  6. OCC 3-Way Merge applies structural mutation to canvas graph with Human-in-the-Loop "Accept / Refine" modal.

## 3. OCC Merge Race Condition & Branch Locking Guard
When Heavy-Path agents run asynchronously in the background:
- The sub-graph branch originating from the source node must enter an `executing_lock` status.
- UI displays subtle neon pulsing edge and disables destructive restructuring of the locked branch.
- Upstream and non-dependent sibling nodes remain fully editable by the human.
- Upon completion, changes are applied through an atomic OCC 3-way structural merge with visual diff overlay before releasing lock.

## 4. Lean Frontend Bridge Invariant (Anti-CopilotKit Bloat)
- Avoid heavy intermediate Node.js server runtimes (CopilotRuntime) for desktop/local architectures.
- Use direct native W3C Server-Sent Events (SSE) or WebSocket streaming from FastAPI (`apps/api`) directly into `@xyflow/react` and Zustand store.
- Every node carries explicit state machine status: `draft` ➔ `executing` ➔ `pending_review` ➔ `approved`.
