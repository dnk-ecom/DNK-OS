# --- DNK-MRH-HEADER ---
# mrh_id: "references/swarm_join_barrier_and_token_diet_engine.md"
# purpose: "Reference architecture and runtime contract for Swarm Join Barrier and Progressive Tool Catalog (Token Diet)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Swarm Join Barrier & Progressive Tool Catalog (Token Diet)

## 1. Context & Operational Need
When orchestrating multi-agent swarms (`dnk_swarm_parallel`), two major failure modes occur at scale:
1. **Context Window Tax & Tool Bloat**: Registering 50+ tool schemas upfront consumes 15,000–25,000 tokens on every turn before conversation starts.
2. **Concurrent Mutation Races (Write Collisions)**: Independent parallel workers mutating the same files (`target_files` intersection) lead to lost edits, git merge conflicts, and corrupted states.

## 2. Progressive Tool Catalog (Token Diet Engine)
Implemented in `core/orchestrator/lazy_tool_loader.py`:
- **L0 (Minimal Core)**: Core routing & classification tools (~1,500 tokens).
- **L1 (Domain Suites)**: Domain-specific tools loaded on-demand via aliases (e.g. `fastapi`, `shopify`, `video`, `qa`).
- **L2 (Full Hydration)**: Deep MCP/API specs hydrated only when explicitly called.
- Result: **60–70% token economy** on initialization, avoiding 90/90 tool budget exhaustion and context compaction churn.

## 3. Swarm Join Barrier Contract & OCC 3-Way Auto-Resolver (Vector A)
Implemented in `core/orchestrator/swarm_coordinator.py` & `core/occ_merge.py`:
- **Collision Detection**: Evaluates pairwise intersections of `target_files` declared by parallel workers:
  ```python
  all_target_files = [f for r in results for f in r.target_files]
  has_intersection = len(all_target_files) != len(set(all_target_files))
  ```
- **Harness Validation**: Verifies that every completed worker produced a valid `HarnessResult` (clean exit code, passing assertions).
- **OCC 3-Way Auto-Merge Path (`auto_resolve_occ=True`)**:
  When two workers touch the same file, `SwarmJoinBarrier` delegates to `OCCFileMergeResolver`:
  - **Disjoint Code Lines**: Uses `difflib.SequenceMatcher` to verify that worker edits occupy strictly disjoint line ranges relative to base state. Merges cleanly without data loss.
  - **Structured JSON/Configs**: Performs dictionary key-level 3-way merge.
  - **Graph/Canvas Nodes**: Integrates with `OCCConcurrencyEngine` for node/edge union merges.
  - **Resolution Verdict**:
    - Clean merge -> `join_status = "AUTO_RESOLVED_VIA_OCC"`, `safe_to_commit = True`, and auto-merged files recorded in `resolved_files`.
    - Overlapping / conflicting lines -> `join_status = "COLLISION_DETECTED"`, `safe_to_commit = False`.

## 4. Canonical Verification Recipe
```bash
./.venv/bin/pytest tests/core/test_swarm_join_barrier.py tests/framework/test_canonical_harness.py tests/framework/test_eval_harness.py
```
Expected: 17+ passing unit & integration tests verifying zero collision leakage and verified OCC 3-way auto-resolution.
