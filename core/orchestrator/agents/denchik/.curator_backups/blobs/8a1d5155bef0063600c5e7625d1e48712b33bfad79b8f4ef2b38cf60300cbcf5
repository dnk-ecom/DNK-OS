<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/canvas-engine-architecture/references/thoughtdag_context_wires_and_graph_of_operations_architecture.md"
purpose: "Architecture guide for ThoughtDAG 2.0 Context Wires, Graph of Operations, and Obsidian Canvas bidirectional sync."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-28"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 ThoughtDAG 2.0: Context Wires & Graph of Operations (GoO) Architecture

## 1. Architectural Pipeline & Transpiler Flow
```
[ Obsidian Canvas / Web UI (.canvas) ]
                │
                ▼ (transpile_obsidian_canvas_to_thoughtdag)
      [ ThoughtDAG Graph ] ──(Kahn Cycle Gate)──► [ Validated DAG ]
                │
        ┌───────┴────────────────────────┐
        ▼                                ▼
[ Context Wires Compiler ]      [ Swarm Graph of Operations ]
(Topological Ancestor Slicing    (Generate ➔ Audit ➔ Merge ➔ Act)
 + SHA-256 Staleness Fingerprint)        │
        │                                ▼
        └──────────────────────► [ Swarm Workers Execution ]
                                 (Builder, Fullstack, Auditor)
```

## 2. Core Pillars & Invariants

### A. Context Wires Engine (Topological Ancestor Slicing)
- **Token Diet Invariant**: Monolithic session histories (>40k tokens) degrade agent reasoning.
- **Mechanism**: Dynamic context extraction via `canvas_compile_thought_context(dag, target_node_id)`.
- **Behavior**: An agent executing a node only receives the prompt context of its upstream topological ancestors (`compute_upstream_ancestors`). Unconnected branches are completely pruned from the prompt.

### B. Graph of Operations (GoO) for Swarm Orchestration
Derived from SOTA Graph-of-Thoughts / Tree-of-Thoughts:
- **Branch/Explore**: Parallel exploration forks for competing architectural implementations.
- **Evaluate/Audit**: Adversarial gate where `gerych_auditor` scores and filters candidate branches before commit.
- **Multi-Parent Merge**: `canvas_merge_thought_context` combines verified branches, synthesizing a single consensus artifact.

### C. Staleness Fingerprinting & Merkle Invalidation
- **Merkle Hash**: Every node computes a SHA-256 fingerprint:
  `fingerprint = sha256(node.content + sum(parent.fingerprint for parent in node.parents))`
- **Cascading Invalidation**: Modifying an upstream specification or architecture doc flips all downstream child nodes to `stale=True`, requiring re-evaluation before execution.

### D. Bidirectional Obsidian Canvas Synchronization
- Visual thought engineering inside `./docs/notes/` via Obsidian JSON Canvas (`.canvas`).
- `transpile_obsidian_canvas_to_thoughtdag` maps cards, notes, and directional connectors to TaskDNA nodes and dependency edges, validated against Kahn's algorithm cycle gate.

### E. Local Branching & Self-Healing Backtracking
- If a worker encounters test or lint failures, the engine spawns an isolated sub-branch `Fix-Attempt-1` invoking `dnk_query_error_solutions`.
- Once verified with exit code 0, the patch merges into the parent branch without polluting global execution state.
