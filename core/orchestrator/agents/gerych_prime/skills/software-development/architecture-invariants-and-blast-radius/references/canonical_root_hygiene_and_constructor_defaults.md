# Canonical Root Hygiene & Constructor Path Anchoring Protocol

## 1. Context & Invariants

In the DNK OS monorepo, strict root directory hygiene is enforced by `scripts/system/root_hygiene_guard.py` and `scripts/system/git_hygiene_guard.py` during pre-commit checks and CI.
The repository root permits exactly **8 canonical domains**:
1. `apps/` — Web frontend, FastAPI micro-framework backend gateway (`apps/api`), Visual Shell.
2. `core/` — Swarm orchestrator, telemetry, security, SCONES memory, task engines, action bus, contracts.
3. `services/` — Standalone agentic microservices (`dnk_node_tasks`, `dnk_video_ai_creator`, `dnk_shopify_builder`). All services MUST be subdirectories prefixed with `dnk_`; loose files in `services/` are forbidden.
4. `packages/` — Shared libraries, tools, and plugins (`packages/plugins/`).
5. `infra/` — Docker configurations (`infra/docker/`), Docker Compose (`infra/compose/`), logs (`infra/logs/`), monitoring.
6. `docs/` — Technical specs, schemas, notes (Obsidian vault link), plans, SOTA research assimilation.
7. `tests/` — Unit, integration, and E2E test suites.
8. `scripts/` — System verification, preflight checks, pre-commit watchdogs, hygiene guards.

All non-canonical root folders (e.g. `artifacts/`, `cache/`, `logs/`, `telemetry/`, `skills/`, `.worktrees/`, `plugins/`) are strictly disallowed.

---

## 2. Source-Tree Immutability & Runtime Cache Isolation (The "Stop the Bleed" Invariant)

### The Anti-Pattern
Source directories (`core/`, `apps/`, `services/`, `packages/`, `tests/`) must remain **100% read-only** during runtime and test execution.
A common regression is classes or service engines hardcoding cache/temp paths pointing into source folders:
```python
# ANTI-PATTERN: Pollutes source repository, creating uncommitted churn and hygiene failures!
class CacheManager:
    def __init__(self, cache_dir: str = "./core/cache/media_renders"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)  # RECREATES core/cache/ ON IMPORT!

class YouTubeMediaCacher:
    DEFAULT_CACHE_DIR = "core/cache/youtube_media"  # POLLUTION!

class SconesProvider:
    def __init__(self, storage_path: str = "tests/scones_storage.json"):  # POLLUTES tests/!
        ...
```
When workers, tests, or subagents run, these defaults silently regenerate `core/cache/`, `core/artifacts/`, or `tests/scones_storage.json`. This causes git untracked file clutter, dirty branches, and breaks automated CI hygiene guards.

### The Canonical Fix
Always resolve runtime caches, renders, and transient scratchpads to the isolated runtime directory (`~/.dnk_runtime/cache` or `$DNK_CACHE_DIR`), or use pytest `tmp_path` in test suites:
```python
# CORRECT: Isolated runtime cache, decoupled from repository source tree
import os
from pathlib import Path

def get_default_cache_dir(subfolder: str) -> Path:
    base = os.getenv("DNK_CACHE_DIR")
    if base:
        p = Path(base) / subfolder
    else:
        p = Path.home() / ".dnk_runtime" / "cache" / subfolder
    p.mkdir(parents=True, exist_ok=True)
    return p

class CacheManager:
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else get_default_cache_dir("media_renders")

class YouTubeMediaCacher:
    @classmethod
    def get_default_cache(cls) -> Path:
        return get_default_cache_dir("youtube_media")
```

For test suites and fixtures, never write mock storage files to `tests/` or `core/tests/`. Always pass `tmp_path` or use in-memory SQLite (`:memory:`):
```python
@pytest.fixture
def isolated_scones(tmp_path):
    storage_file = tmp_path / "scones_storage.json"
    return SconesProvider(storage_path=str(storage_file))
```

---

## 3. Autonomous Service Directory Isolation (`services/dnk_*`)

In accordance with Domain-Driven Design (DDD) and `services/DOMAIN_RULES.md`:
1. Every service in `services/` must be an encapsulated package directory prefixed with `dnk_` (e.g., `services/dnk_alerting/`, `services/dnk_video_ai_creator/`).
2. Loose scripts (e.g. `services/alerting_service.py`) directly under `services/` are strictly forbidden.
3. If legacy imports exist, maintain a backward-compatibility shim:
   ```python
   # services/alerting_service.py (Backward Compatibility Shim)
   """Deprecated: import from services.dnk_alerting.alerting_service instead."""
   from services.dnk_alerting.alerting_service import *
   ```

---

## 4. Constructor Default Path Anchoring (Root Leakage Prevention)

### The Anti-Pattern
Service or utility classes defining constructor arguments with relative paths in root:
```python
# ANTI-PATTERN: Creates stray folders in cwd (repository root) when instantiated without args!
class LocalTelemetryEngine:
    def __init__(self, telemetry_dir: str = "telemetry", logs_dir: str = "logs"):
        ...
```
When tests or agents run from repo root, this creates uncanonical directories (`telemetry/`, `logs/`, `artifacts/`, `cache/`) tripping fail-closed `root_hygiene_guard.py`.

### The Fix
Anchor constructor defaults to either:
- The isolated runtime directory (`Path.home() / ".dnk_runtime" / ...`)
- Canonical infrastructure subdirectories (`infra/logs/`)
- Or enforce explicit required arguments in constructors rather than dangerous cwd defaults.

---

## 5. Fast Verification & Audit

To verify that the working copy adheres to canonical root and git hygiene:
```bash
python3 scripts/system/root_hygiene_guard.py
python3 scripts/system/git_hygiene_guard.py
```
If violations are reported:
1. Identify the caller creating the folder using `search_files(pattern='folder_name')`.
2. Inspect constructor defaults, module constants, and pytest fixtures.
3. Patch the class to use `$DNK_CACHE_DIR` / `~/.dnk_runtime/cache` or pytest `tmp_path`.
4. Re-run `scripts/system/root_hygiene_guard.py` until 100% Green.

---

## 6. Automated Remediation via Workspace Janitor

When `root_hygiene_guard.py` fails due to transient/ephemeral directories (such as `.worktrees/`, `.extracted_assets/`, `output/`, `temp/`, root `skills/`) or orphan locks (`core/orchestrator/agents/*/*.lock`), run the workspace janitor before manually inspecting:
```bash
python3 scripts/system/workspace_janitor.py
```
The janitor executes a 4-phase automated remediation:
1. **Prunes Stale Worktrees**: Runs `git worktree prune -v` to cleanly unmount and clear dangling `.worktrees/`.
2. **Reaps Dead Locks**: Inspects `/tmp/dnk_agent_locks` and agent-specific lockfiles; safely unlinks locks whose owner PID is no longer alive.
3. **Purges Ephemeral Directories**: Recursively removes unauthorized root scratchpads (`artifacts/`, `cache/`, `logs/`, `telemetry/`, root `skills/`).
4. **Verifies 8-Root Compliance**: Concludes with an automated call to `root_hygiene_guard.py` ensuring 100% Green status.

---

## 7. Ephemeral Test Fixture Cleanliness & Zero-Symlink Invariant

### The Anti-Pattern: Dynamic Bridge Symlinks in Test Fixtures
In legacy setups, `tests/conftest.py` utilized an autouse session fixture (`ensure_canonical_bridges`) that dynamically generated symlinks at repo root (`templates`, `data`, `Dockerfile*`, `docker-compose*`, `monitoring`, etc.) to bridge paths for tests.
When test suites or CI scripts timed out, failed unexpectedly, or were aborted via `SIGTERM`/`SIGINT`, the pytest fixture teardown was bypassed, leaving loose symlinks in the repository root. This immediately broke `root_hygiene_guard.py` and `git_hygiene_guard.py` with `UNAUTHORIZED ROOT FILE / DIRECTORY`.

### The Canonical Resolution
1. **Eliminate Dynamic Root Symlinks**: Pytest fixtures must NEVER create loose files or symlinks at the repository root. Tests needing access to Docker, Compose, templates, or monitoring configurations must reference their canonical locations directly (`infra/docker/`, `infra/compose/`, `core/templates/`, `core/data/`).
2. **Explicit Teardown Sanitation**: Fixtures that clean ephemeral test bridge artifacts must use `try ... finally` or session-scoped cleanup that guarantees unlinking of any stray bridges without polluting the repository root.
3. **Fail-Closed Symlink Detection in `root_hygiene_guard.py`**:
   The guard inspects every directory entry at root via `entry.is_symlink()`:
   ```python
   # Detect unauthorized symlinks (only .venv is allowed if symlinked)
   if entry.is_symlink() and entry.name != ".venv":
       target = os.readlink(entry.path)
       violations.append(f"UNAUTHORIZED ROOT SYMLINK: {entry.name} -> {target} (move to canonical domain)")
   ```
4. **13 Canonical Core Subsystems Validation**:
   `root_hygiene_guard.py` programmatically verifies the 13 canonical core domains (`core/manifests`, `core/registry`, `core/data`, `core/stores`, `core/orchestrator`, `core/action_bus`, `core/hermes_runtime`, `core/skills`, `core/local_telemetry`, `core/canvas`, `core/guards`, `core/auditor`, `core/security`) and prohibits unauthorized scratch folders (`core/artifacts/`, `core/cache/`).
5. **Continuous Contract Validation in `auto_precommit_guard.py`**:
   Guard #4 (Fast Test Suites) permanently includes `tests/contracts/test_service_card_contract.py` to validate metadata, ports, spend guards, and documentation paths for all 16 microservices on every commit.
6. **Microservice Test Tracking in `git_hygiene_guard.py`**:
   The git hygiene guard scans `services/*/tests/` to guarantee that all newly authored microservice tests are tracked and not accidentally omitted from version control.

---

## 8. Theme Assets & Binary Archive Isolation (`services/dnk_shopify/assets/themes/`)

### The Anti-Pattern
Binary archives and packaged bundles (e.g. `DNK_Ecom_v1_0_0.zip`, `DNK_Horizon_Tinker_Theme_v1.0.0.zip`) placed directly in service root (`services/dnk_shopify/`) or in root `artifacts/`.
- Placing them in `artifacts/` is catastrophic: `artifacts/` is in `.gitignore` and purged by `workspace_janitor.py`.
- Placing them in service roots pollutes the repository root/service trees and violates domain asset containment.
- Placing `.liquid` template snippets in `apps/web/snippets/` violates frontend web layer boundaries.

### The Canonical Resolution
1. **Dedicated Assets Subdirectory**: Store persistent theme archives in `services/dnk_shopify/assets/themes/`.
2. **Hierarchical Path Resolution**: Adapters (`theme_adapter.py`) and orchestrators (`theme_migration_orchestrator.py`) must inspect `assets/themes/` first before falling back to service root:
   ```python
   # Priority 1: Canonical assets/themes directory
   canonical_path = shopify_dir / "assets" / "themes" / f"{theme_name}.zip"
   if canonical_path.exists():
       return canonical_path
   # Priority 2: Service root fallback (legacy)
   root_path = shopify_dir / f"{theme_name}.zip"
   if root_path.exists():
       return root_path
   ```
3. **Strict 8-Root Guard Enforcement**: `artifacts` must remain excluded from `ALLOWED_ROOT_DIRS` in `scripts/system/root_hygiene_guard.py`. Any loose templates in `apps/web/` must be purged.

---

## 9. Unified Runtime & Dependencies Storage Invariant (DEC-033 Compliance)

### The Anti-Pattern: Local Physical Dependency Directories
Installing heavy, standalone dependency folders (`node_modules/`, independent unlinked `.venv` copies) directly within `apps/`, `services/`, or `packages/`:
- Consumes gigabytes of redundant SSD space across workspace subdirectories.
- Severely degrades `git status`, IDE indexers (VSCode, Spotlight, Obsidian), and AST traversal speed.
- Directly violates the Zero-Bloat Invariant (Rule 10 AGENTS.md, DEC-033).

### The Canonical Resolution
1. **Centralized Runtime SSOT (`~/.dnk_runtime`)**:
   - **Python**: The central virtual environment lives exclusively at `~/.dnk_runtime/venv`. The repository root must contain only an atomic symlink `./.venv -> ~/.dnk_runtime/venv`.
   - **Node.js / pnpm**: Packages are hardlinked to global store `~/.pnpm-store` / `~/Library/pnpm/store/v10` (0 bytes duplicate storage). Heavy virtual stores or shared module trees reside in `~/.dnk_runtime/node_environments/` or use pnpm shared workspace symlinks, never unmanaged physical duplicate folders.
2. **Deterministic Audit & Hygiene Check**:
   - Audit compliance and stale caches via `scripts/system/purge_stale_environments_and_cache.py`.
   - Any physical `node_modules` (>50MB) or unlinked `.venv` inside `apps/` or `packages/` must be flagged, audited, and replaced with centralized runtime links.

---

## 10. PNPM Workspace Monorepo & Inter-Package Linkage Invariant

### The Anti-Pattern: Brittle Relative `file:../` Package Bindings
In multi-package setups (`apps/web`, `packages/teleprompter_core`, `packages/video_audit_core`), using relative file paths in `package.json`:
```json
// ANTI-PATTERN: Breaks pnpm -r recursive runs, versioning, and symlink deduplication
"dependencies": {
  "@dnk/video-audit-core": "file:../video_audit_core"
}
```
Furthermore, integration tests attempting deep relative imports across package boundaries (e.g. `import { reburnReferenceFixture } from '../../../video-audit-core/src/fixtures/reburn-reference.js'`) fail when folder structures evolve or when packages are migrated.

### The Canonical Resolution
1. **Root `pnpm-workspace.yaml`**:
   Define canonical monorepo workspace packages at repo root:
   ```yaml
   packages:
     - 'apps/*'
     - 'packages/*'
   ```
2. **Workspace Protocol (`workspace:*`)**:
   Always link sibling monorepo packages using `workspace:*`:
   ```json
   "dependencies": {
     "@dnk/video-audit-core": "workspace:*"
   }
   ```
   Combined with `pnpm config set virtual-store-dir ~/.dnk_runtime/pnpm_virtual_store --global`, this produces a unified workspace symlink tree with 0-byte redundant storage.
3. **Workspace Build & Export Contract**:
   When a package declares entry points to `./dist/index.js` or `./dist/index.d.ts`, build the dependency with `pnpm --dir packages/<dep> build` (or `tsc`) so consuming packages resolve exports cleanly.
4. **Targeted Consumer Imports**:
   Consumer integration tests MUST import shared modules via package name (`import { ... } from '@dnk/video-audit-core'`) rather than fragile relative directory traversal.
5. **Legacy Folder Consolidation Before Purge**:
   When consolidating non-canonical root directories (e.g. `templates/plugin/` -> `core/templates/plugin/`), verify and update default lookup paths in CLI runners, registry engines, and test fixtures before deleting the root directory to avoid cascading test suite regressions.


