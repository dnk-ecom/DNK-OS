# Ghost Runtime Trees, Gitignore Leaks & Deprecation Shim Hygiene Protocol

This reference documents the diagnostic procedure, root causes, and remediation rules for ghost directory trees, physical shim elimination, dynamic meta-path redirection, and canonical root directory hygiene in the DNK OS monorepo.

---

## 1. The Gitignored Recursive Runtime Tree Trap

### Anatomy of the Failure
When an agent framework, runner, or daemon is hosted inside a gitignored directory (e.g. `core/hermes_agent/` where `.gitignore` contains `core/hermes_agent/`), several hazards converge:
1. **Unintentional Git Tracking vs Gitignore**:
   If individual files are added with `git add -f` (e.g., `core/hermes_agent/agent/vertex_adapter.py`), Git continues tracking that file while completely ignoring all sibling and child directories.
2. **Recursive Execution & Shadow Trees**:
   If an agent or subprocess executes with its working directory set to the nested folder (or resolves relative paths `./core/...` from within itself), it creates a shadow replica: `core/hermes_agent/core/orchestrator/agents/...`.
3. **Invisibility to Git Status**:
   Because `core/hermes_agent/` or `logs/` is in `.gitignore`, `git status` never flags the dozens of megabytes, hundreds of subfolders, cache stores, or duplicate models being generated inside `core/hermes_agent/core/` or `core/orchestrator/agents/<agent>/core/`.
4. **Agent CWD Misconfiguration Trap**:
   When an agent daemon (e.g. `herich_librarian`) runs with CWD set to its agent folder (`core/orchestrator/agents/herich_librarian/`) and a logging or state path is specified relative to root (`core/orchestrator/agents/.../logs/gateway.log`), the relative resolution spawns a nested shadow tree: `core/orchestrator/agents/<agent>/core/orchestrator/agents/...`. Because `logs/` is gitignored, this ghost directory remains completely invisible to standard `git status`.
5. **Tool & Ast Pollution**:
   Fast symbol search, find, or un-anchored linters traverse this shadow tree, returning duplicate or stale symbols and confusing code discovery.

### Remediation Protocol
- **Single Root Execution**: Daemons, agents, and test runners must always bind `$HUB_ROOT` as the sole working directory.
- **Dedicated Runtime State Isolation**: Runtime state, cache, profiles, and locks must be placed in `~/.dnk_runtime/` or standard user cache, never inside source folders.
- **Audit Rule for Gitignored Source Trees**:
  Run periodic check for nested untracked trees inside gitignored paths or repeating segments:
  ```bash
  python3 -c "import os; [print(r) for r, d, f in os.walk('.') if ('core/' in r and r.count('core') > 1) or ('services/' in r and r.count('services') > 1)]"
  ```
  Any path with repeating canonical segments (`core/.../core` or `services/.../services`) indicates an unauthorized recursive shadow tree and must be purged with `rm -rf`.

---

## 2. Deprecation Shim Lifecycle & Phased Purge

### The Problem
During domain decoupling (e.g., migrating `core/video` -> `services/dnk_media/video`), re-export shims emitting `DeprecationWarning` prevent breaking downstream callers. However, if left unchecked:
- Router layers (`apps/api/routers/`) continue importing from `core.*` indefinitely.
- Tests continue targeting old paths or checking for outdated file fixtures (`core/tests/` or `core/docs/schemas/`).
- Physical shim files/directories in `core/` clutter the tree and obscure whether code is active logic or dead scaffolding.

### Three-Phase Cleanup Invariant
1. **Phase A (Decouple & Physical Shims)**:
   - Move implementation to `services/dnk_<domain>/`.
   - Leave thin physical shims in `core/<domain>/` with `warnings.warn(..., DeprecationWarning)`.
2. **Phase B (Callsite Migration & Zero-File Dynamic Redirection)**:
   - Migrate all API routers (`apps/api/routers/`) and client packages directly to `services.dnk_*` imports.
   - Delete physical directory shims (`core/video/`, `core/shopify_liquid/`, `core/supervisor/`, `core/voice/`).
   - Register dynamic import hooks (`_LegacyCoreFinder`) in `core/__init__.py` to catch external callers without leaving physical directories on disk.
3. **Phase C (Hard Deprecation & Removal)**:
   - Once all external callers are verified migrated across all consumers, prune the dynamic redirection mapping entirely.

---

## 3. Dynamic Meta-Path Import Interception (`_LegacyCoreFinder`)

To achieve zero physical shim directories while retaining 100% backward compatibility for dynamic or third-party callers:

### Implementation Pattern in `core/__init__.py`
```python
import importlib
import importlib.abc
import sys
import warnings

_LEGACY_CORE_REDIRECTS = {
    "core.video": "services.dnk_media.video",
    "core.shopify_liquid": "services.dnk_shopify.shopify_liquid",
    "core.supervisor": "services.dnk_shopify.supervisor",
    "core.voice": "services.dnk_media.voice",
}

class _LegacyCoreFinder(importlib.abc.MetaPathFinder):
    """Dynamically resolves legacy core.* imports to services.dnk_* without physical directories."""

    def find_spec(self, fullname: str, path=None, target=None):
        for legacy_prefix, new_prefix in _LEGACY_CORE_REDIRECTS.items():
            if fullname == legacy_prefix or fullname.startswith(legacy_prefix + "."):
                subpath = fullname[len(legacy_prefix):]
                target_module_name = new_prefix + subpath
                return importlib.machinery.ModuleSpec(
                    fullname,
                    _AliasLoader(target_module_name, legacy_prefix, new_prefix),
                    is_package=True,
                )
        return None

class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target_name: str, legacy: str, target: str):
        self.target_name = target_name
        self.legacy = legacy
        self.target = target

    def exec_module(self, module):
        warnings.warn(
            f"Importing '{module.__name__}' is deprecated; use '{self.target_name}' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        real_module = importlib.import_module(self.target_name)
        module.__dict__.update(real_module.__dict__)
        sys.modules[module.__name__] = real_module

if not any(isinstance(finder, _LegacyCoreFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _LegacyCoreFinder())
```

### Invariants:
- `sys.modules[module.__name__] = real_module`: Must cache the resolved module directly under the alias name to ensure sub-attribute lookups and repeated imports resolve in O(1) time without re-triggering the loader.
- Prefix matching allows both root legacy package (`core.video`) and nested modules (`core.video.remotion_renderer`) to resolve cleanly.

---

## 4. Canonical Root Directory Whitelist & Binary Artifacts Relocation

### Invariant
`scripts/system/root_hygiene_guard.py` enforces the Canonical Directory Standard. Only sanctioned root directories are permitted:
`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`, `artifacts/`.

### Binary Asset Relocation:
- Binary theme archives, `.zip` distributions, and prebuilt bundles must NEVER reside inside `services/` (e.g. `services/dnk_shopify/*.zip`).
- Relocate binary assets to `artifacts/themes/`.
- Ensure `artifacts/` is registered in `CANONICAL_ROOT_DIRS` in `scripts/system/root_hygiene_guard.py` and ignored in `.gitignore`.

### Test Runner State Hygiene:
- Tests or plugins creating scratch output MUST use `tmp_path` (pytest) or `.data/` (unified hidden state).
- Stray root directories such as `data/` or `templates/` instantly fail `root_hygiene_guard.py` with `UNAUTHORIZED ROOT DIRECTORY`. Always anchor file operations to `$HUB_ROOT / ".data"` or use `tempfile.TemporaryDirectory()`.

---

## 5. Pytest Multi-Root PYTHONPATH SSOT

### Invariant
`verify_all.sh` exports `PYTHONPATH="$HUB_ROOT:$HUB_ROOT/services:$HUB_ROOT/packages"`. To ensure developers and IDEs running bare `pytest` do not experience `ModuleNotFoundError: No module named 'plugins'`:
- Always declare the identical search paths in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  pythonpath = [".", "services", "packages"]
  ```
- Keep `verify_all.sh` and `pyproject.toml` strictly synchronized so CI and local test runs behave identically.

---

## 6. Empty Ghost Directories & Test Fixture Path Hygiene

### The Invariant
Under the Canonical 8-Root Directory Invariant (`AGENTS.md`), all test files and fixtures must reside in `tests/` (`tests/core/`, `tests/services/`, etc.). Non-canonical test folders such as `core/tests/` are strictly forbidden.

### The Ghost Directory Trap:
- Hardcoded test fixture constants pointing to `core/tests/` (e.g. `TEST_STORAGE_PATH = "core/tests/scones_test_storage.json"`) recreate `core/tests/` on every test run because underlying state engines (e.g. `SCONESMemoryEngine`, `VisualContextRegistry`) call `os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)`.
- When test cleanup deletes the json files via `os.remove()`, `core/tests/` remains as an empty untracked ghost directory that keeps respawning on every test execution.
- **Rule**: Never use source directories for transient test artifacts. Test storage paths must always be routed to `artifacts/test_storage/` (which is git-ignored and sanctioned by `root_hygiene_guard.py`) or use pytest's `tmp_path` fixture.

---

## 7. Monorepo Submodule Hygiene & Legacy Monolith Containment

### The Invariant
Per the Two-Tier Development Protocol (`docs/architecture/TWO_TIER_DEVELOPMENT_PROTOCOL.md`), legacy nested subfolders are deprecated and removed. All services reside directly at root (`services/dnk_*`).

### Submodule Traps:
1. **Duplicate Shadow Service Code**: Submodules (e.g. `services/dnk_shopify/DNK-e.com`) embedding nested duplicate service trees (`DNK-e.com/services/dnk_shopify`) confuse AST indexers and global searches.
2. **Untracked Cache Leaks & Tracked `.pyc` Traps**:
   - Python execution inside submodules generates `__pycache__` (`.pyc`) files that cause git to report `modified: ... (untracked content)`.
   - If a submodule was committed with `.pyc` files previously tracked in its git index, deleting `__pycache__` causes git to report deleted tracked files instead of clean state. In this scenario, run `git rm -f --cached **/*.pyc && git commit -m "chore: remove tracked pyc files"` inside the submodule.
3. **Remediation**:
   - Clean untracked submodule caches: `git submodule foreach --recursive "git clean -fdX"`.
   - Purge tracked binary bytecodes from submodule index if present.
   - Prefer independent external repositories or standalone client distribution packages (`scripts/export_standalone_app.py`) over embedding monolithic git submodules inside `services/`.
