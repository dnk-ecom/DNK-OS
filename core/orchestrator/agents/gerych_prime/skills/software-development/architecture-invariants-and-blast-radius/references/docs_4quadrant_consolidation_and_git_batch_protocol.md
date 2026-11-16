# Documentation 4-Quadrant Consolidation & In-RAM Git Batch Protocol (DEC-055)

## Overview
When consolidating thousands of scattered documentation files across legacy directories into canonical quadrants (`docs/architecture/`, `docs/tasks/`, `docs/audit/`, `docs/vault/`), naive shell execution (`git mv` in bash loops) triggers stream stalls, terminal buffer truncation, and `.git/index.lock` contention. 

This protocol establishes a zero-loss, deterministic procedure for high-velocity documentation refactoring.

---

## 1. Canonical 4-Quadrant Topology (DEC-055)

All repository documentation in `docs/` must strictly reside in one of four operational quadrants or sanctioned system folders:

| Quadrant / Area | Target Path | Scope & Contents |
| :--- | :--- | :--- |
| **Q1: Architecture** | `docs/architecture/` | System specs (`specs/`), ADRs (`adr/`), schemas (`schemas/`), SCONES rules (`scones/`), API contracts, diagrams, and UX architecture. |
| **Q2: Tasks** | `docs/tasks/` | Task specifications, sprint plans, active implementation roadmaps, and DAGs. |
| **Q3: Audit** | `docs/audit/` | Audit reports, verification receipts (`RECEIPT-*.json`), benchmark results, research teardowns, and handoff summaries. |
| **Q4: Vault** | `docs/vault/` | Knowledge base, Obsidian notes, research archives, conceptual drafts, guides, and templates (`notes/`, `tech/`, `canvas/`). |
| **Root Docs** | `docs/` | Strictly top-level navigation: `CHANGELOG.md`, `DIRECTORY_MAP.yaml`, `DOMAIN_RULES.md`, `README.md`. |

---

## 2. In-RAM Batch Execution vs Naive Shell Moving

### Problem with Shell Loops
- Executing `git mv <source> <target>` in shell loops on 3,000+ files spawns thousands of sub-processes, causes index lock contention (`fatal: Unable to create '.git/index.lock': File exists`), and floods tool output streams.
- Moving files on disk without updating git index causes git to see thousands of deletes and untracked additions rather than clean renames.

### Recommended Pattern: Python In-RAM Batch Operations
1. **Pre-Flight In-RAM Collision Detection**:
   Scan all target destinations in memory. If a file exists at both source and target, verify their SHA256 hashes:
   - If identical: deduplicate by unlinking the redundant copy.
   - If divergent: rename the incoming copy with a distinct suffix or timestamp.
2. **Deterministic Move via `shutil.move` / `os.replace`**:
   Execute file moves directly via Python standard library in RAM (<0.5s for thousands of files).
3. **Prune Stale Source Directories**:
   Walk source trees bottom-up and remove empty directories (`os.rmdir`).
4. **Synchronize Git Index in One Atomic Call**:
   ```python
   subprocess.run(["git", "add", "-A", "docs/"], check=True)
   ```
   Git automatically detects renames (similarity > 50%) across the entire tree in seconds without lock thrashing.

---

## 3. Post-Move Contract & Gate Synchronization

Moving documentation frequently breaks downstream static path expectations. Always run the following verification pipeline:

### A. Contract Schema Path Fallback
Contract tests validating YAML schemas (e.g. `tests/contracts/test_service_card_contract.py`) typically define a `SCHEMA_PATH`.
Update them to support both canonical quadrant paths and backward-compatibility fallbacks:
```python
candidate_paths = [
    Path(__file__).resolve().parents[2] / "docs/architecture/schemas/service_card.schema.yaml",
    Path(__file__).resolve().parents[2] / "docs/schemas/service_card.schema.yaml",
]
SCHEMA_PATH = next((p for p in candidate_paths if p.exists()), candidate_paths[0])
```

### B. Machine-Readable Header (MRH) Normalization
Execute the automated header fixer across `docs/`:
```bash
python3 scripts/system/check_mrh_headers.py --fix docs/
```
Verify that all `mrh_id` values match their new relative file paths and no absolute local paths (`/Users/...`) are exposed.

### C. Anti-Tautology & Pre-Commit Verification Gate
Run pre-commit checks to catch tautological assertions and contract breaks:
```bash
python3 scripts/system/anti_tautology_guard.py --affected
python3 scripts/system/auto_precommit_guard.py
```
Ensure 8/8 checks return `PASS` (Exit Code 0).
