# Zero-Breaking Modular Shimming & 4-Layer Core Restructuring Protocol

## 1. Context & Motivation

In enterprise monorepos (such as DNK OS), core services and engines often start as flat modules in `core/`. As the system scales to dozens of services, agents, and apps, this flat namespace leads to circular imports, lack of layer boundaries, and unclear blast radius.

Restructuring `core/` into a strict 4-Layer Modular Architecture without breaking existing dependencies across `apps/`, `services/`, and external SDKs requires the **Zero-Breaking Shimming Protocol**.

---

## 2. The 4-Layer Core Architectural Hierarchy

All components inside `core/` belong strictly to one of 4 layers:

| Layer | Domain Responsibilities | Canonical Subdirectories |
|---|---|---|
| **Layer 1: Foundations & Registries** | Low-level storage engines, service & repo registries, accounting primitives | `core/stores/`, `core/registry/`, `core/accounting/` |
| **Layer 2: Swarm Orchestration & Bus** | Task graph decomposition, AST pattern assimilation, swarm routing, event bus | `core/orchestrator/`, `core/action_bus/` |
| **Layer 3: UI, Runtime & Telemetry** | Canvas OCC graph engine, Hermes runtime wrappers, skill managers, local telemetry | `core/canvas/`, `core/hermes_agent/`, `core/skills/`, `core/telemetry/` |
| **Layer 4: Security & Governance** | Multi-tenant auth engine, secret vaults, role-based capability gates | `core/security/` |

---

## 3. The Backward-Compatible Shim Pattern

When moving `core/<module>.py` to `core/<subsystem>/<module>.py`:
1. Move the real implementation into the target directory.
2. Ensure the target directory has a valid `__init__.py`.
3. In place of the old file `core/<module>.py`, create a backward-compatible shim.

### Canonical Shim Implementation
```python
# --- DNK-MRH-HEADER ---
# mrh_id: "core/<module>.py"
# purpose: "Backward-compatible import shim redirecting to core.<subsystem>.<module>"
# status: "Deprecated-Shim"
# version: "1.0.0"
# --- END DNK-MRH-HEADER ---

"""
DEPRECATED: Use core.<subsystem>.<module> instead.
This module is preserved as a backward-compatible shim for existing services and routers.
"""

import warnings

# Emit deprecation warning on import
warnings.warn(
    "Importing from 'core.<module>' is deprecated and will be removed in future releases. "
    "Use 'core.<subsystem>.<module>' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all public symbols and provide dynamic __all__
from core.<subsystem>.<module> import *  # noqa: F401, F403
import core.<subsystem>.<module> as _module

__all__ = [name for name in dir(_module) if not name.startswith("_")]
```

### Why Dynamic `__all__` is Mandatory
Static wildcards (`from ... import *`) do not always propagate when third-party tools inspect modules via `getattr()` or `importlib`. Dynamically computing `__all__` using `dir(_module)` guarantees:
- `from core.<module> import Foo` works seamlessly.
- `import core.<module>; core.<module>.Foo` works seamlessly.
- `from core.<module> import *` exports exactly what the target module exports.

---

## 4. Subsystem Name Collision Resolution

When an existing subsystem already contains a file with the same name (e.g. `core/occ_merge.py` [1,012 LOC] vs `core/canvas/occ_merge.py` [468 LOC]):
1. **Do not overwrite** either file blindly.
2. Inspect the symbol definitions and test suites targeting each file.
3. Rename the incoming file to a distinct canonical name (e.g. `core/canvas/graph_occ_merge.py`), and point the root shim (`core/occ_merge.py`) to the renamed target.
4. Verify that existing tests for both files pass independently.

---

## 5. Verification Protocol

Always execute an automated two-track verification script:
```python
import importlib

modules_to_test = [
    # Verify canonical targets
    "core.stores.atomic_store",
    "core.registry.service_registry",
    "core.orchestrator.swarm_engine",
    "core.canvas.canvas_engine",
    "core.security.auth_engine",
    
    # Verify backward-compatible shims
    "core.atomic_store",
    "core.service_registry",
    "core.swarm_engine",
    "core.canvas_engine",
    "core.auth_engine",
]

for mod in modules_to_test:
    m = importlib.import_module(mod)
    assert m is not None, f"Failed to import {mod}"
print("All modules and shims verified successfully!")
```

Then test kernel instantiation and root hygiene:
```bash
.venv/bin/python3 -c "from core.kernel import FastMCPKernel; k = FastMCPKernel()"
python3 scripts/system/root_hygiene_guard.py
python3 scripts/system/auto_precommit_guard.py
```
