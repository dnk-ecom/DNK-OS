<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "references/canvas_occ_3way_merge_mvp.md"
# purpose: "Reference guide for Canvas OCC 3-Way Merge MVP v0.1 (CANVAS-002)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym / Gerych Prime"
# --- END DNK-MRH-HEADER ---
-->

# Canvas OCC 3-Way Merge MVP (Slice CANVAS-002)

## Overview & Architecture

When multiple swarm workers or clients concurrently manipulate `CanvasState`, optimistic concurrency control (OCC) requires a deterministic 3-way merge engine to reconcile changes between `base_state`, `local_state`, and `remote_state` without losing graph topology or corrupting coordinate spaces.

### Core Module & CLI
- **Engine**: `core/canvas/occ_merge.py` (`CanvasOCCMergeEngine`, `canvas_3way_merge`, `MergeResult`, `Conflict`)
- **CLI**: `scripts/system/canvas_occ.py` (`merge`, `show-conflicts`)
- **Templates**: `templates/canvas/occ/{base,local,remote,merged}_state.json`

## Pydantic Data Contracts

```python
from typing import Any, List
from pydantic import BaseModel, Field

class Conflict(BaseModel):
    path: str
    base_value: Any = None
    local_value: Any = None
    remote_value: Any = None
    resolution: str = "manual"  # manual | local | remote | base

class MergeResult(BaseModel):
    success: bool
    conflicts: List[Conflict] = Field(default_factory=list)
    merged_state: dict = Field(default_factory=dict)
    version: str = "v0.1"
```

## Merge & Conflict Detection Rules

1. **Equal Mutations**: If `local == remote`, no conflict occurs. The mutated value is adopted.
2. **Orthogonal Mutations**: If `local != remote` and they modify disjoint fields or disjoint graph nodes, both changes are cleanly merged into `merged_state`. `success = True`, `conflicts = []`.
3. **Overlapping Contradictory Mutations**: If `local != remote` and both modify the same field with different values:
   - A `Conflict` is appended with `path`, `base_value`, `local_value`, `remote_value`, and `resolution="manual"`.
   - `success` is set to `False`.
   - The conflict retains the local mutation by default in `merged_state` pending resolution.
4. **Semantic Graph Identity Alignment**:
   - `nodes`: Keyed by `node_id`. Nodes existing in both branches are recursively merged by attribute (`position`, `title`, `metadata`). New nodes in either branch are appended.
   - `edges`: Keyed by `edge_id`. Edges modified in disjoint fields (`label`, `metadata`) are merged; distinct added edges are preserved.

## Critical Testing Pitfall & Workaround

### Pitfall: macOS `tmp_path` Breaks Relative Path Invariants
- **Symptom**: `ValueError: '/private/var/folders/...' is not in the subpath of '/Users/...'`
- **Cause**: Pytest's standard fixture `tmp_path` creates directories under `/private/var/folders/...` on macOS, which is outside the repository workspace root (`Path.cwd()`). When testing strict relative path validators (`validate_relative_path`), converting `tmp_path.relative_to(Path.cwd())` fails.
- **Solution**: Use in-tree test scratch files relative to the test directory (e.g. `Path("tests/canvas/_tmp_test.json")`), cleaned up deterministically in a `try...finally` block:

```python
out_file = Path("tests/canvas/_tmp_test_output.json")
try:
    result = run_cli(["merge", "--output", str(out_file), ...])
    assert result.exit_code == 0
    assert out_file.exists()
finally:
    if out_file.exists():
        out_file.unlink()
```
