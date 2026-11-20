---
title: "Dnk Canvas Occ 3Way Merge V0.1"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_CANVAS_OCC_3WAY_MERGE_v0.1.md"
> purpose: "Document: Dnk Canvas Occ 3Way Merge V0.1"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/DNK_CANVAS_OCC_3WAY_MERGE_v0.1.md"
> # purpose: "Specification for DNK OS Canvas OCC 3-Way Merge MVP v0.1 (CANVAS-002)"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "0.1.0"
> # updated_at: "2026-09-09"
> # author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# DNK OS Spatial Canvas Architecture: OCC 3-Way Merge MVP v0.1

## 1. Overview & Objective

The **Canvas OCC 3-Way Merge MVP** (`CANVAS-002`) provides a deterministic, optimistic concurrency control (OCC) 3-way merge engine for asynchronous updates to `CanvasState`. When multiple swarm agents, users, or background synchronizers update the visual canvas topology concurrently, the 3-way merge engine reconciles concurrent modifications against a common baseline (`base_state.json`), detecting conflicts when identical fields diverge, and cleanly merging non-conflicting disjoint updates.

### Scope & Role
- **Non-Invasive Synchronization**: Compares three states — `base_state`, `local_state`, and `remote_state` — and generates a unified `merged_state` alongside explicit conflict descriptions.
- **Pure Compute & Offline**: No UI, no WebSocket/SSE transport, no background daemon, and no runtime mutation.
- **Zero Secrets / Network / DB**: Does not access secrets, vault, network endpoints, or databases. Operates exclusively on memory dicts and relative JSON files.
- **Deterministic Field & Array Merging**: Reconciles nodes and edges by unique identifiers (`node_id`, `edge_id`) while preserving JSONPath-style indexing (`nodes.0.position.x`).

---

## 2. OCC 3-Way Merge Data Models

### 2.1 Conflict Model

Represents a field-level collision where both local and remote states modified the same field to conflicting values relative to the base state.

```yaml
Conflict:
  path: "nodes.0.position.x"
  base_value: 0
  local_value: 100
  remote_value: 200
  resolution: "manual"
  # Allowed resolutions: "manual" | "local" | "remote" | "base"
```

#### Fields
- `path` (`str`): JSON dot-separated path to the conflicted field (e.g., `nodes.0.position.x`, `metadata.title`).
- `base_value` (`Any`): The original value in the shared baseline state.
- `local_value` (`Any`): The value in the local state modification.
- `remote_value` (`Any`): The value in the remote state modification.
- `resolution` (`str`): Current resolution strategy (`"manual"`, `"local"`, `"remote"`, or `"base"`). Default: `"manual"`.

---

### 2.2 MergeResult Model

Represents the complete result of a 3-way merge operation.

```yaml
MergeResult:
  success: true
  conflicts: list[Conflict]
  merged_state: {}
  version: "v0.1"
```

#### Fields
- `success` (`bool`): `True` if no conflicts were detected; `False` if one or more conflicts occurred.
- `conflicts` (`list[Conflict]`): List of detected conflicts. Empty when `success` is `True`.
- `merged_state` (`dict`): The reconciled canvas state dictionary.
- `version` (`str`): Canvas state version, preserving `"v0.1"`.

---

## 3. Merge Logic & Resolution Rules

Given `base`, `local`, and `remote`:

1. **Identical State / No-Op**:
   - If `local == remote`: No conflict. Merged value equals `local`.
   - If `local == base` and `remote == base`: Base state is returned unchanged.
2. **Disjoint Unilateral Changes**:
   - If `local != base` and `remote == base`: Local modification is applied cleanly.
   - If `remote != base` and `local == base`: Remote modification is applied cleanly.
   - If `local != remote` but changes affect disjoint fields (e.g. local changed `position.x`, remote changed `position.y`): Both modifications are applied into the merged state. `success: true`, `conflicts: []`.
3. **Overlapping Concurrent Mutations (Conflict)**:
   - If `local != base` and `remote != base` and `local != remote` for the exact same scalar path:
     - A `Conflict` record is created with `resolution: "manual"`.
     - `success` is set to `False`.
     - Local value is retained in `merged_state` as tentative placeholder awaiting resolution.
4. **Collection Alignment (`nodes` and `edges`)**:
   - Array elements with identity keys (`node_id` for nodes, `edge_id` for edges) are matched across states regardless of list order.
   - New items added only in local or only in remote are incorporated into the merged list.
   - Deletions are respected when the other branch did not modify the item.
   - Field paths use canonical 0-based array indices matching base ordering (e.g. `nodes.0.position.x`).
5. **Version & Timestamp Invariants**:
   - Canvas state `version: "v0.1"` is preserved across all merges.
   - Audit timestamp `last_updated_at` takes the latest update timestamp and does not produce spurious conflicts.

---

## 4. CLI Interface

The CLI utility is located at `scripts/system/canvas_occ.py`.

### 4.1 Merge Command

```bash
./.venv/bin/python3 scripts/system/canvas_occ.py merge \
  --base templates/canvas/occ/base_state.json \
  --local templates/canvas/occ/local_state.json \
  --remote templates/canvas/occ/remote_state.json \
  --output templates/canvas/occ/merged_state.json
```

- Reads base, local, and remote JSON states.
- Executes 3-way merge algorithm.
- Outputs serialized `MergeResult` JSON to the specified relative file path.
- Exit code 0 on clean merge.

### 4.2 Show Conflicts Command

```bash
./.venv/bin/python3 scripts/system/canvas_occ.py show-conflicts \
  templates/canvas/occ/merged_state.json
```

- Parses target JSON file for conflict records.
- Outputs human-readable summary of all conflicts with path, base, local, remote, and resolution values.
- If no conflicts are present, prints `No conflicts found.`.

---

## 5. Security & Safety Invariants

1. **Relative Paths Only**: All inputs and outputs must resolve to relative paths inside the project repository. Absolute paths and directory traversal (`..`) are strictly rejected with `ValueError`.
2. **Offline Isolation**: No external network requests, no database queries, and no git commands are executed.
3. **Non-Invasive**: No runtime processes, agents, or plugins are started or modified.
