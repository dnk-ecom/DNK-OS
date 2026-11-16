# Standalone Export Whitelist, Zero-Torch Invariant & Root Hygiene Protocol

## Context
When packaging Tier 2 standalone distributions (e.g. `DNK_OS_APP` via `scripts/system/export_standalone_app.py`) and maintaining workspace cleanliness for CI/Master Quality Gate (`bash scripts/verify_all.sh`):

### 1. Zero-Torch & Pure-Python Invariant for Standalone Export
- Modules exported to Tier 2 (`core/system_one/`, `core/bricks/`, etc.) must remain strictly pure Python / standard library / lightweight Pydantic where possible.
- They must NEVER import PyTorch, torchvision, or CUDA runtimes at module import time, preserving the Zero-Torch Invariant for sub-second lightweight distributions.
- When updating standalone export scripts, ensure `dirs_exist_ok=True` is passed to `shutil.copytree` when merging directories, and register new core modules in `STANDALONE_CORE_MODULES`.

### 2. Root Hygiene Guard Invariant
- The canonical 8-root directory layout (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`) is enforced by `scripts/system/root_hygiene_guard.py`.
- Recognized developer workspace files (e.g. `.kilo`, `.vscode`, `DNK_HUB.code-workspace`) and temporary test run roots must be properly whitelisted in `ALLOWED_TOP_LEVEL_DIRS` and `ALLOWED_TOP_LEVEL_FILES` to prevent precommit / CI false-positives.
- Transient logs and transcripts generated during swarm execution must be placed in `.data/transcripts/` or `artifacts/`, never dumped into repository root.

### 3. Markdown Schema & MRH Invariants
- All documentation and note files must maintain valid DNK-MRH headers (`mrh_id`, `purpose`, `canonical_source`, `status`, `version`, `updated_at`, `author`).
- SOTA assimilation digests require a `## 🎭 Mandatory Dissent` section to satisfy the anti-sycophancy and architectural critique gates (`scripts/system/markdown_schema_gate.py`).

### 4. Clean Room Secret Isolation & In-Target Quality Gate
- **Strict Excludes (`clean_room_ignore`)**: Standalone export must deterministically ignore all `.env*` files (except `.env.example`), `.pem`, `.key`, `.secret`, `.token`, `.git`, `__pycache__`, `node_modules`, `.venv`, and `*.db`.
- **Post-Copy Secret Leak Audit**: The export engine scans `target_dir` post-copy. If any unauthorized `.env*` or secret file is detected, it raises `RuntimeError` and deletes `target_dir` to prevent leaky client distributions.
- **Fail-Closed In-Target Test Gate**: During export, tests run directly inside the target app with `TESTING=1` and isolated `PYTHONPATH`. If `proc.returncode != 0`, export is aborted and the target directory is purged.

### 5. Pre-Export Gate & Composable Bricks DAG Invariant
- **Deterministic Pre-Export Check**: Integrated as Step [2.8/4] in `scripts/system/verify_all.sh`:
  `python3 -m pytest tests/bricks/test_brick_registry.py --quiet --tb=short`
- **Integrity Guarantee**: Confirms that all `brick.manifest.yaml` files are syntactically sound, internal DAG dependencies have zero cycles, and declared target paths physically exist on disk before any export is attempted.
- **RFC Requirement**: Any new or updated composable brick must provide an approved RFC based on `docs/templates/RFC_BRICK_TEMPLATE.md` with explicit `Target File Whitelist`, `Negative Scope`, and `DoD`.

