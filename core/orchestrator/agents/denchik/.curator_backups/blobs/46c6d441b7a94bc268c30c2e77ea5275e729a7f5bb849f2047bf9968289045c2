# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/fastapi_gateway_consolidation_and_ssot_registry_protocol.md"
# purpose: "Canonical Protocol for FastAPI Gateway Consolidation, Domain Package Organization, SSOT Router Registry, and Zero-Breaking Shims"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# FastAPI Gateway Consolidation, SSOT Registry & Domain Router Protocol

## 1. Context & Architectural Problem
In rapidly scaling monorepos, FastAPI application entry points (e.g. `apps/api/main.py`) frequently degrade into anti-patterns:
1. **Double / Triple Mounting**: Teams add dynamic autodiscovery (`pkgutil.iter_modules` over `apps/api/routers/`) while retaining legacy explicit `app.include_router(...)` calls. This causes dozens of routers to be registered twice: once under root (or prefixless) and once under `/api`.
2. **Duplicate Operation IDs & OpenAPI Corruption**: FastAPI silently or warning-level assigns duplicated `operationId`s in `openapi.json`, leading to SDK generation corruption, client routing unpredictability, and severe route table bloat.
3. **Flat Directory Sprawl**: Dozens of loosely related routers (e.g., 9 separate `canvas_*.py` files, 5 `video_*.py` files, 4 `task_*.py` files) clutter a single flat `routers/` folder.
4. **Fragile Relative Imports**: Moving modules to subdirectories breaks naive relative imports (`from ..lib import ...`).

---

## 2. Invariants & Rules

### Rule 1: Single Source of Truth (SSOT) Router Registry
- NEVER mix dynamic filesystem autodiscovery (`iter_modules`, `glob`) with explicit router mounting.
- Centralize all route inclusion into a dedicated registry module (`apps/api/routers/registry.py`) providing a single entry point:
  `register_routers(app: FastAPI) -> None`.
- The registry MUST enforce deduplication internally:
  ```python
  seen_routers: set[int] = set()

  def _mount(router, prefix="", tags=None):
      rid = id(router)
      if rid in seen_routers:
          return
      seen_routers.add(rid)
      app.include_router(router, prefix=prefix, tags=tags)
  ```

### Rule 2: Domain Package Grouping
Sprawling flat routers must be partitioned into cohesive domain packages:
- `apps/api/routers/canvas/` (`crud.py`, `v1.py`, `bridge.py`, `events.py`, `stream.py`, `stitch.py`, `v3.py`, `v3_ws.py`, `ws.py`, `__init__.py`)
- `apps/api/routers/video/` (`core.py`, `retention.py`, `shorts.py`, `audit.py`, `media_pipeline.py`, `__init__.py`)
- `apps/api/routers/tasks/` (`dna.py`, `forest.py`, `node.py`, `dna_v1.py`, `__init__.py`)

Each domain package `__init__.py` exposes an aggregated `router = APIRouter()` and/or granular sub-routers.

### Rule 3: Zero-Breaking Dynamic Facade Shims
Existing unit tests and external clients often import internal constants, helper functions, or factory methods directly from the old flat module path (e.g., `from apps.api.routers.canvas_router import _get_occ`).
- Naive `from .domain.module import *` DOES NOT export names beginning with an underscore (`_`).
- Canonical dynamic shim pattern:
  ```python
  from apps.api.routers.canvas import v1 as _target

  router = _target.router

  for _name in dir(_target):
      if not _name.startswith("__"):
          globals()[_name] = getattr(_target, _name)
  ```
This guarantees 100% backward compatibility for all callers without maintaining dual implementations.

### Rule 4: Absolute Import Hygiene in Reorganized Packages
When moving a module from `apps/api/routers/` to a subpackage `apps/api/routers/domain/`, relative imports change their root:
- `from ..lib.ssrf_guard import SSRFGuard` becomes relative to `routers/` instead of `apps/api/`.
- Replace with absolute package imports: `from apps.api.lib.ssrf_guard import SSRFGuard`.

### Rule 5: OpenAPI Operation ID Collision Prevention
FastAPI derives default `operation_id` from the endpoint function name and HTTP method.
When multiple decorators decorate the same handler function:
```python
# ANTI-PATTERN: Secondary decorator may cause operationId collision
@router.post("/contracts/negotiate")
@router.post("/negotiate/initiate")
def initiate_negotiation(...):
    pass
```
Ensure the primary canonical path is the topmost decorator or explicitly specify `operation_id="..."` on secondary aliases.

---

## 3. Verification Protocol

1. **Route Uniqueness & Collision Audit**:
   ```python
   pairs = []
   for r in app.routes:
       methods = tuple(sorted(getattr(r, "methods", None) or ("WS",)))
       pairs.append((methods, getattr(r, "path", "")))
   duplicates = [pair for pair, count in Counter(pairs).items() if count > 1]
   assert not duplicates, f"Duplicate routes found: {duplicates}"
   ```

2. **OpenAPI Schema Zero-Warning Generation**:
   ```python
   schema = app.openapi()
   assert "paths" in schema
   ```

3. **Domain & Shim Import Verification**:
   Verify direct domain import and legacy shim import resolve to identical objects.
