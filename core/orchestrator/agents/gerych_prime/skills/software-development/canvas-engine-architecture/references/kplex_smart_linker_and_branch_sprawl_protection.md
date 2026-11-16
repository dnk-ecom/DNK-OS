---
title: "zsviczian/kplex Obsidian Smart Linker & Branch Sprawl Protection Pattern"
description: "Production implementation blueprint for zsviczian/kplex + Obsidian Smart Linker: 5 core patterns, Ego-Centric Plex subgraphs, Graph Lenses, Evidence Store triples, and Branch Sprawl Lifecycle."
---

# 🌐 zsviczian/kplex Obsidian Smart Linker & Branch Sprawl Protection

This reference documents the production architecture and concrete implementation patterns in `DNK_OS_APP` (`core/obsidian/smart_linker.py`, `core/kernel.py`, and `apps/web/src/components/canvas/WorldSotaThoughtCanvas.tsx`) unifying `zsviczian/kplex` graph traversal, Dataview semantic triples, and Obsidian bidirectional link graphs.

---

## 💎 1. The 5 Core KPlex Patterns

1. **Ego-Centric Plex Subgraph (`get_k_hop_context_subgraph`)**:
   - Rather than loading the entire global graph into the LLM context, focuses strictly on a focal seed node ($k \in [1, 3]$ hops).
   - Traverses outward via BFS, tracking node distance from the seed.
   - Prevents context window explosion while retaining relevant local dependencies.

2. **Graph Lenses (`apply_lens` / `GraphLensType`)**:
   - Dynamic projection filters based on the active agent role:
     - `architectural`: focuses on hierarchy and implementation (`parent`, `child`, `implements`, `depends_on`).
     - `evidence`: focuses on proofs, verification, and counter-evidence (`verifies`, `supports`, `refutes`, `implements`).
     - `causal`: focuses on cause-and-effect and mutations (`depends_on`, `alters`, `verifies`, `child`).
     - `dependency`: focuses strictly on code and library imports (`depends_on`, `implements`, `alters`, `references`).
     - `all`: unconstrained view.

3. **Evidence Store & Semantic Triples (`predicate::[[target|alias]]`)**:
   - Inline Dataview/kplex typed triples:
     - `supports:: [[EvidenceNode]]` (corroborates design or hypothesis).
     - `refutes:: [[CounterEvidence]]` (disproves hypothesis or flags critical defect).
     - `verifies:: [[TestFile]]` (deterministic verification gate link).
     - `implements:: [[DecisionID]]` (code artifact link to architectural decision).

4. **Bidirectional Wikilinks & Unlinked Mentions (`discover_unlinked_mentions`)**:
   - Parses explicit `[[target#section|alias]]` and resolves backlinks.
   - Scans natural text against vault entity aliases and titles (alias length $\ge 4$ characters to prevent false positives).
   - Computes confidence scores based on term specificity and length.

5. **Branch Sprawl Protection & Status Lifecycle (`BranchStatus` & `prune_stale_branches`)**:
   - Multi-agent branch exploration runs the risk of combinatorial graph expansion and context rot.
   - Governed by an explicit branch state machine:
     - `PROPOSED` (`#35d5d5`, Teal): Initial hypothesis / seed node.
     - `IN_PROGRESS` (`#3b82f6`, Blue): Worker agent assigned.
     - `VERIFIED` (`#22c55e`, Green): Passes test gate / verified proof.
     - `STALE` (`#f59e0b`, Amber): Upstream contract changed; pending re-check.
     - `REFUTED` (`#ef4444`, Red): Fails tests or counter-evidence found.
     - `PRUNED` (`#64748b`, Slate): Truncated from traversal to protect LLM context.
     - `ARCHIVED` (`#475569`, Dark Slate): Historical locked node.

---

## ⚡ 2. Branch Lifecycle Transitions & Pruning Invariants

```
        ┌─────────────┐
        │  PROPOSED   │
        └──────┬──────┘
               │ (dispatch to domain worker)
               ▼
        ┌─────────────┐       (upstream contract mutation)     ┌───────────┐
        │ IN_PROGRESS ├────────────────────────────────────────►│   STALE   │
        └──────┬──────┘                                        └─────┬─────┘
               │                                                     │
      ┌────────┴────────┐                                            │
(pass)│                 │ (fail / refutes::)                         │
      ▼                 ▼                                            │
┌───────────┐     ┌───────────┐                                      │
│ VERIFIED  │     │  REFUTED  ├────────────────────────┐             │
└─────┬─────┘     └─────┬─────┘                        │             │
      │                 │                              │             │
      │ (commit / lock) ▼ (prune dead branch)          ▼             ▼
      │           ┌───────────┐                  ┌───────────┐
      └──────────►│ ARCHIVED  │◄─────────────────┤  PRUNED   │
                  └───────────┘                  └───────────┘
```

### Pruning Rule (Strict Deep Module Invariant):
- Any branch remaining in `REFUTED` or unreviewed `STALE` for $>2$ ticks is pruned (`status = PRUNED`).
- Nodes marked `PRUNED` are physically skipped during `get_k_hop_context_subgraph` BFS traversal, reducing context token consumption by 70–85%.

---

## 📐 3. Boundary Conditions & Limits

| Boundary Parameter | Safe Bound | Failure Mode if Violated |
|---|---|---|
| **Max $k$-Hop Depth** | $k \le 3$ (Default $k=2$) | Attention entropy and irrelevant distant nodes in LLM prompt |
| **Max Subgraph Nodes** | $N \le 25$ | Exceeds atomic slice bound (MASE $\le 25$ tools/nodes per turn) |
| **Min Alias Length** | $\ge 4$ characters | False-positive unlinked mentions of common words ("test", "code", "node") |
| **Branch Fan-Out** | $\le 4$ child nodes | Exponential branch explosion across parallel subagents |
