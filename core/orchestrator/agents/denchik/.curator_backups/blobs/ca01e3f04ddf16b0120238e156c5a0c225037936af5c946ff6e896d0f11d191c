# Domain Decoupling, Dynamic Meta-Path Import Shimming & Backward Compatibility Protocol

## 1. Overview & Architectural Motivation

In rapidly evolving platforms, `core/` often accumulates business-domain logic (e.g., e-commerce adapters, media rendering, speech models) and legacy experimental agent folders (`core/agents/`, `core/swarm/`, `core/coordinators/`, `core/services/`).

Leaving business domains in `core/` violates Clean Architecture and Domain-Driven Design (DDD):
- Business logic in `core/` creates circular dependencies with domain services (`services/dnk_*`).
- Monolithic `core/` bloats build and test blast radius for domain-specific changes.
- Legacy directories clutter the directory tree and confuse new developers and agents.

However, moving code directly breaks dozens of existing unit tests, scripts, API routers, and background jobs. The **Domain Decoupling & Dynamic Meta-Path Shimming Protocol** provides 100% backward compatibility during restructuring.

---

## 2. Dual-Layer Backward Compatibility Strategy

### Layer 1: File-Level Backward-Compatible Shims
For business domains moved out of `core/` (e.g., `core/shopify_liquid/` -> `services/dnk_shopify/shopify_liquid/`, `core/supervisor/` -> `services/dnk_shopify/supervisor/`, `core/video/` -> `services/dnk_media/video/`):
1. Move the real implementations to their canonical destination under `services/dnk_*` or `packages/*`.
2. Leave thin re-export files in the original locations with `DeprecationWarning`.

#### Canonical Shim Template:
```python
# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/module.py"
# purpose: "Backward-compatibility re-export for services.dnk_domain.module."
# canonical_source: false
# status: "Deprecated"
# --- END DNK-MRH-HEADER ---

"""Backward-compatibility re-export. Canonical location is services.dnk_domain.module."""

import warnings
from services.dnk_domain.module import *  # noqa: F401, F403
import services.dnk_domain.module as _canonical

warnings.warn(
    "Importing from 'core.domain.module' is deprecated. Use 'services.dnk_domain.module' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [name for name in dir(_canonical) if not name.startswith("_")]
```

---

### Layer 2: Dynamic Meta-Path Redirection (`sys.meta_path`)
For consolidated or deleted legacy subpackages (e.g., `core/agents/`, `core/swarm/`, `core/coordinators/`, `core/services/`) that were merged into `core/orchestrator/`, `core/security/`, or `core/rag/`:
Instead of maintaining lingering dead directories with dozens of trivial shims, install a lightweight custom `MetaPathFinder` in `core/__init__.py`.

#### Canonical Dynamic Meta-Path Finder Implementation:
```python
import sys
import warnings
from importlib.abc import Loader, MetaPathFinder
from importlib.util import find_spec
import importlib

_LEGACY_MODULE_MAP = {
    # Legacy agents / coordinators -> orchestrator
    "core.agents.agent_with_plugins": "core.orchestrator.agent_with_plugins",
    "core.coordinators.agent_coordinator": "core.orchestrator.agent_coordinator",
    "core.coordinators.engine_adapter": "core.orchestrator.engine_adapter",
    "core.coordinators.quantum_engine": "core.orchestrator.quantum_engine",
    "core.coordinators.subagents": "core.orchestrator.subagents",
    "core.swarm.swarm_director": "core.orchestrator.swarm_director",
    # Legacy core.services -> core.security & core.rag
    "core.services.security_gate_service": "core.security.security_gate_service",
    "core.services.improvement_security_service": "core.security.improvement_security_service",
    "core.services.rag_service": "core.rag.rag_service",
    "core.services.timeline_knowledge_service": "core.rag.timeline_knowledge_service",
}

class _AliasLoader(Loader):
    def __init__(self, target_name: str):
        self.target_name = target_name

    def exec_module(self, module):
        target = importlib.import_module(self.target_name)
        module.__dict__.update(target.__dict__)
        module.__file__ = getattr(target, "__file__", None)
        module.__path__ = getattr(target, "__path__", None)

class _LegacyCoreFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname in _LEGACY_MODULE_MAP:
            target_name = _LEGACY_MODULE_MAP[fullname]
            warnings.warn(
                f"Importing '{fullname}' is deprecated; please use '{target_name}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            target_spec = find_spec(target_name)
            if target_spec is not None:
                target_spec.loader = _AliasLoader(target_name)
                return target_spec

        # Dynamic prefix redirects with fallback (e.g., core.canvas -> packages.domains.canvas)
        for pfx, target_pfx in _LEGACY_PREFIX_REDIRECTS.items():
            if fullname == pfx or fullname.startswith(pfx + "."):
                target_name = target_pfx + fullname[len(pfx):]
                try:
                    target_spec = find_spec(target_name)
                except Exception:
                    target_spec = None
                if target_spec is not None:
                    return spec_from_loader(fullname, loader=_AliasLoader(target_name, fullname))
                # Fallback to local package path if domain module not yet relocated
                return None
        return None

if not any(isinstance(finder, _LegacyCoreFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _LegacyCoreFinder())
```

---

## 3. Dynamic Prefix Redirection & Domain Migration Strategy

When decoupling multi-submodule domains from `core/` into `packages/domains/`:
1. **Never move all files in a single pass without shims**: Decoupling 100+ files breaks active test suites and external callers.
2. **Configure prefix redirection with fallback**:
   ```python
   _LEGACY_PREFIX_REDIRECTS = {
       "core.canvas": "packages.domains.canvas",
       "core.lakehouse": "packages.domains.lakehouse",
       "core.mindmap": "packages.domains.mindmap",
   }
   ```
   If `importlib.util.find_spec(target_name)` returns `None`, `find_spec` returns `None`. Python will automatically fall back to the existing path under `core/`, allowing incremental migration of modules without breaking unmigrated siblings.

---

## 4. Root Hygiene & Constructor Storage Defaults Invariant

When standardizing file paths and templates across domain modules:
- **Canonical Directories Only**: All template fixtures, approval queues, and storage logs must reside under canonical directories (e.g. `core/templates/canvas/` or `.data/`), **NEVER** in the repository root (`templates/`).
- **Default Argument Pitfall**: Default string paths in model constructors or module constants (e.g. `DEFAULT_PENDING_FILE = "templates/canvas/approvals/pending_approvals.jsonl"`) will create an unauthorized `templates/` folder at repo root during unit test execution or CLI invocations, immediately failing `root_hygiene_guard.py`.
- **Enforce Root Guard**: Always specify canonical prefixes (e.g. `core/templates/...`) in default constants and test fixture setups.

---

## 5. Test Fixture & Migration Discovery Invariant

When database migrations or schemas are relocated (e.g. from `db/migrations/` to `infra/migrations/db/migrations/`):
- Verification test fixtures must not assume a single hardcoded relative path.
- Always implement progressive fallback path resolution:
```python
candidate_paths = [
    root_dir / "infra" / "migrations" / "db" / "migrations",
    root_dir / "db" / "migrations",
]
migrations_dir = next((p for p in candidate_paths if p.is_dir()), None)
assert migrations_dir is not None, f"Migrations directory not found in candidates: {candidate_paths}"
```

---

## 4. PEP 8 Package Standardization

- Monorepo package directory names under `packages/` must follow PEP 8 snake_case conventions (`packages/video_audit_core/` instead of `packages/video-audit-core/`).
- Any legacy hyphenated directory should be migrated and symlinks phased out, synchronizing references in `pyproject.toml`, workspace path configurations, and test suites.
