# Service Modularization, Root Sentinel Resolution & Manifest Standards

This reference details the canonical patterns for modularizing services, resolving repository root in deeply nested core packages, handling headless/worker service manifests, and constructing backward-compatible shims with zero breaking changes.

---

## 1. Dynamic Root Sentinel Resolution (Zero Brittle Pathing)

### The Problem
When restructuring monorepo packages (e.g. moving `core/service_registry.py` to `core/registry/service_registry.py`), hardcoded ancestor references (`os.path.dirname(os.path.dirname(__file__))`) break silently. Furthermore, searching upward for generic directory names like `"services"` or `"core"` fails if parent directories contain homonymous subdirectories (e.g. `core/services/` inside `core/`).

### Canonical Sentinel Walk Pattern
Always resolve the repository root by iteratively traversing upward looking for authoritative root sentinel markers (`pyproject.toml`, `AGENTS.md`, or `.git`):

```python
from pathlib import Path
from typing import Optional

def resolve_repo_root(start_path: Optional[Path] = None) -> Path:
    current = (start_path or Path(__file__)).resolve()
    # Walk upward through parents
    for candidate in [current] + list(current.parents):
        if (candidate / "AGENTS.md").is_file() or (candidate / "pyproject.toml").is_file():
            return candidate
    # Fallback to CWD
    return Path.cwd().resolve()
```

---

## 2. Microservice Manifests: Headless Workers vs HTTP Services

### The Problem
Service registry models that enforce integer `port` defaults (e.g. `port: int = 8000`) cause headless background workers (such as event stream workers, canvas render workers, or queue processors) to register dummy ports. In strict environments, this triggers false-positive port collision alarms (`Port 8000 is claimed by multiple services`).

### Canonical ServiceCard Specification
1. In Pydantic manifest models:
   ```python
   class ServiceManifestModel(BaseModel):
       name: str
       version: str
       port: Optional[int] = None  # None for headless/worker services
       runtime: str
       spec: ServiceSpec
       operations: Optional[ServiceOperations] = None
   ```
2. In `service_manifest.yaml` for workers:
   ```yaml
   name: dnk_canvas_worker
   version: 1.0.0
   runtime: python
   # port is omitted for headless event stream workers
   spec:
     service_type: worker
     entrypoint: "src/worker.py"
     spend_guard:
       max_cost_per_turn_usd: 0.10
       max_monthly_budget_usd: 50.0
   operations:
     health_endpoint: "/health" # Internal probe or status check
   ```

---

## 3. Loose Script Modularization & Backward-Compatible Shimming

### Directory Encapsulation Standard
Loose Python scripts residing directly in `services/` (e.g. `services/alerting_service.py`) must be encapsulated into standard domain microservices:
```
services/
  └── dnk_alerting/
      ├── __init__.py
      ├── alerting_service.py
      ├── service_manifest.yaml
      ├── docs/
      │   └── SPECIFICATION.md
      └── tests/
          └── test_alerting_service.py
```

### Zero-Breaking Shim Pattern
Leave a lightweight deprecation shim in the legacy path (`services/alerting_service.py`) that issues a `DeprecationWarning` and re-exports all symbols dynamically:

```python
"""
services/alerting_service.py - Backward Compatibility Shim.

DEPRECATION NOTICE:
Direct import from `services.alerting_service` is deprecated.
Please migrate to `services.dnk_alerting.alerting_service`.
"""

import warnings
from services.dnk_alerting.alerting_service import (
    AlertingService,
    AlertSeverity,
    AlertPayload,
)

warnings.warn(
    "Importing from `services.alerting_service` is deprecated. "
    "Use `services.dnk_alerting.alerting_service` instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "AlertingService",
    "AlertSeverity",
    "AlertPayload",
]
```

---

## 4. Root Symlink Invariant (Canonical 8-Root Enforcement)

Root hygiene checkers (`scripts/system/root_hygiene_guard.py`) enforce the invariant that the repository root strictly contains the 8 canonical domains:
- `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`

Any symlink placed in the root directory (e.g. `Dockerfile -> infra/docker/Dockerfile` or `data -> ...`) is treated as an unauthorized root artifact and trips pre-commit gates fail-closed.
All tooling configurations, compose files, and container definitions must remain scoped inside `infra/` or their respective domain folders.
