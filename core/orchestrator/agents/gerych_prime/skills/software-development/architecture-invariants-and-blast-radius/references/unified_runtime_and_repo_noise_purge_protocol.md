# Unified Runtime Environment & Repository Noise Purge Protocol

## 🎯 1. Overview & Architectural Invariants

This protocol operationalizes the **Unified Runtime Environment Invariant** (DEC-033 / Rule 10 AGENTS.md) and provides deterministic guidelines for monorepo noise auditing and zero-bloat maintenance in `DNK_HUB`.

### Core Invariants:
1. **Centralized Runtime SSOT**: Strictly forbidden to create or download isolated virtualenvs or heavy physical `.pnpm` virtual stores inside repository subdirectories.
   - **Python**: Unified runtime lives at `~/.dnk_runtime/venv`. Root `.venv` and agent `.venv` directories are strictly symlinks to this path (`.venv -> /Users/.../.dnk_runtime/venv`).
   - **Node.js**: Global virtual store must be directed to `~/.dnk_runtime/pnpm_virtual_store`. Configure via:
     ```bash
     pnpm config set virtual-store-dir ~/.dnk_runtime/pnpm_virtual_store --global
     ```
     This ensures all monorepo `node_modules` contain ONLY lightweight symlinks (~150 KB total per app instead of 750 MB+), keeping repository footprint strictly Zero-Bloat (< 500 KB total).
2. **APFS CoW & Hardlink SSOT**: When `pnpm install` is executed in frontend apps (`apps/web`), pnpm symlinks into the global virtual store (0 duplicate disk bytes). Never let unlinked trees break `tsc --noEmit` type checks.
3. **8-Root Directory Invariant**: Top-level directory structure is frozen to: `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`. Transient directories (`data/`, `artifacts/`, `cache/`) must either be in gitignore or placed in designated scratch directories.

---

## 🧹 2. Monorepo Noise Categories & Purge Taxonomy

| Category | Common Locations | Purge Method | Safety / Impact |
| :--- | :--- | :--- | :--- |
| **Finder Noise** | `**/.DS_Store` | `find . -name '.DS_Store' -delete` | 100% safe. Eliminates git status pollution. |
| **Python Bytecode** | `**/__pycache__`, `**/*.pyc` | `find . -type d -name '__pycache__' -exec rm -rf {} +` | 100% safe. Regenerated on demand by interpreter. |
| **Unlinked node_modules** | `apps/*/node_modules` (physical copies) | Purge physical dirs, re-link via `pnpm --dir apps/<app> install` | Safe. Re-establishes hardlinks from `~/.pnpm-store`. |
| **Build & Dist Artifacts** | `apps/web/.next`, `apps/canvas/dist` | `rm -rf apps/web/.next apps/canvas/dist` | Safe. Auto-rebuilt during test/build passes. |
| **Stale High-Volume Logs** | `infra/logs/*.log`, `core/orchestrator/agents/*/logs/*.log` | Truncate files > 10MB to 0 bytes (`: > file.log`) | Safe. Prevents context stall and disk bloat. |
| **Stale Worktrees & Cache** | `.kilo/worktrees/*`, `.data/graphify-out/` | Prune dead worktrees (`git worktree prune -v`), purge stale caches | Safe. Recover disk space (>100MB). |

---

## ⚙️ 3. Deterministic Purge & Verification Workflow

### Step 1: Scan & Inventory Noise (In-RAM)
Execute an in-memory scan via `execute_code`:
```python
from pathlib import Path

# Identify untracked bloat without dumping thousands of lines to context
ds_stores = list(Path(".").rglob(".DS_Store"))
pycaches = list(Path(".").rglob("__pycache__"))
large_logs = [p for p in Path(".").rglob("*.log") if p.is_file() and p.stat().st_size > 10 * 1024 * 1024]
```

### Step 2: Atomic Cleanup
```bash
# 1. Clean OS and compiler noise
find . -name '.DS_Store' -delete
find . -type d -name '__pycache__' -exec rm -rf {} +

# 2. Truncate heavy log files (>10MB)
for log in infra/logs/*.log core/orchestrator/agents/*/logs/*.log; do
  [ -f "$log" ] && [ $(stat -f%z "$log" 2>/dev/null || echo 0) -gt 10485760 ] && : > "$log"
done

# 3. Clean temporary build caches
rm -rf apps/web/.next apps/canvas/dist
```

### Step 3: Re-link Node Dependencies (PNPM Workspace & Global Virtual Store SSOT)
Ensure `pnpm` points to the centralized virtual store, configure the root workspace, and link all packages:
```bash
# Set global virtual store SSOT
pnpm config set virtual-store-dir ~/.dnk_runtime/pnpm_virtual_store --global

# Configure root pnpm-workspace.yaml (apps/*, packages/*)
# and ensure packages use "workspace:*" instead of fragile "file:../" links.

# Run workspace install from root to link all packages with 0 duplicate storage
pnpm install

# Validate type checks across frontend apps
pnpm --dir apps/web type-check
```

### Step 4: Run Pre-Commit Adversarial Gates
Ensure zero breakage after noise cleanup:
```bash
python3 scripts/system/anti_tautology_guard.py --affected
python3 scripts/system/auto_precommit_guard.py
```

---

## ⚠️ 4. Critical Pitfalls

- **Root PNPM Workspace & Root Hygiene Guard**: Adding `pnpm-workspace.yaml` causes pnpm to create a root `node_modules` directory for binary hoists. `scripts/system/root_hygiene_guard.py` must explicitly whitelist `pnpm-workspace.yaml`, `pnpm-lock.yaml`, and `node_modules` in `ALLOWED_ROOT_FILES` and `ALLOWED_ROOT_DIRS` to avoid fail-closed pre-commit rejections.
- **Local Package Linking (`workspace:*` over `file:../`)**: Relative `"file:../package_name"` references in `package.json` break easily on folder renames and fail during root installs. Monorepo packages MUST use `"workspace:*"` within `pnpm-workspace.yaml`.
- **Pre-Existing Template/Fixture Directory Deletion Trap**: Never delete or move root template directories (e.g. `templates/plugin`) without first auditing all hardcoded string references across `core/` and running the corresponding test suite (`uv run pytest tests/plugins/`). Blind deletion can cause dozens of `FileNotFoundError` test failures across certification, registry, and sandbox modules.
- **Git Submodule Dirty Worktree Protection**: When auditing root `git status` that shows modified submodule pointers (e.g. `services/dnk_shopify/DNK-e.com`), always run `git -C <submodule_path> status` first. Submodules may contain uncommitted branch work (e.g. active redesign branches like `story`). Discarding or committing changes blindly will destroy in-flight developer work.
- **Recharts JSX vs `@types/react` Incompatibilities**: In isolated apps, Recharts may require `@ts-expect-error`. However, once root workspace types are unified, unused `@ts-expect-error` directives trigger TS2578 errors. Always run `pnpm --dir apps/web type-check` to verify directive necessity.
- **Blind node_modules Wipe Without Re-linking**: Completely wiping `apps/web/node_modules` without running `pnpm install` causes `auto_precommit_guard.py` frontend type-check (`tsc --noEmit`) to fail-closed because `node_modules/.bin/tsc` is absent.
- **Untracked Test Staging Requirement**: If new test files or router files were generated before or during audit, `auto_precommit_guard.py` git hygiene check blocks pre-commit. All test files must be staged (`git add tests/...`).
- **Log File Deletion vs Truncation**: Deleting active log files while daemon processes (watchdogs, background runners) hold open file descriptors can cause orphaned file handles or uncollected errors. Always truncate active logs (`: > file.log`) instead of unlinking them.
