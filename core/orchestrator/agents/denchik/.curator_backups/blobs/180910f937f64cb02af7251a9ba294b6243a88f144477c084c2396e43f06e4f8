<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/packages_and_core_consolidation_protocol.md"
purpose: "Canonical protocol for packages/ and core/ dual-namespace consolidation, adapter SSOT, plugin delineation, and deprecation warning elimination."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-15"
author: "Gerych Prime & DNK OS"
--- END DNK-MRH-HEADER -->

# Packages & Core Consolidation, Adapter SSOT & Deprecation Elimination Protocol

## 1. Architectural Motivation

In large-scale monorepos undergoing DDD (Domain-Driven Design) modularization, components often end up fragmented across both `core/` (the central platform) and `packages/` (shared libraries). Common manifestations include:
- **Dual Adapter Fragmentation**: Essential third-party framework adapters (Hermes, Patchright, LangGraph, PersonaLive, Iris, Archify) duplicated or split between `core/adapters/` and `packages/adapters/`.
- **Blurred Plugin Boundaries**: Mixing the plugin execution engine (sandboxing, lifecycle, policy verification) with concrete business plugins in the same directory.
- **Scattered Utilities**: Utility modules duplicated in ad-hoc subtrees (e.g. `packages/dnk_os/utils/`) instead of a single canonical `packages/utils/`.
- **Deprecation Warning Churn**: Test suites and verification scripts calling deprecated import shims (e.g., `core.supervisor` instead of `services.dnk_shopify.supervisor`), producing warnings that fail strict `-W error::DeprecationWarning` CI gates.

---

## 2. The 3 Consolidation Invariants

### Invariant 1: Single Source of Truth (SSOT) with Backward-Compatibility Facades
All third-party integration adapters, ports, and hardware/framework bridges live canonically in:
```
packages/adapters/
  ├── __init__.py                # Canonical exports of all adapters and port abstractions
  ├── hermes_adapter.py
  ├── dnk_patchright_adapter.py
  ├── canvas_adapter.py
  └── ... (all 23+ adapters)
```

To maintain 100% backward compatibility for existing services and external callers:
- `core/adapters/__init__.py` acts as a **Facade Re-export Layer**:
  ```python
  """
  Backward-compatible facade redirecting to packages.adapters.
  """
  import sys
  from packages.adapters import *  # noqa: F401, F403
  import packages.adapters as _pkg

  __all__ = getattr(_pkg, "__all__", [k for k in dir(_pkg) if not k.startswith("_")])
  ```
- Any import `from core.adapters import HermesAdapter` returns the exact same class object (`is` comparison evaluates to `True`) as `from packages.adapters import HermesAdapter`.

### Invariant 2: Engine vs Plugin Architectural Demarcation
Strict separation between execution infrastructure and domain plugins:
- `core/plugins/`: **Plugin Governance Engine**
  - Manages plugin lifecycle (`PluginLifecycle`), manifest contracts (`PluginCard`), sandboxing, capability validation, and security gates (`TrustKeyRegistry`, `PluginSecurityGate`).
  - Exports: `PluginManager`, `PluginCard`, `PluginLifecycle`, `validate_plugin_card_data`.
- `packages/plugins/`: **Ecosystem Business Plugins**
  - Houses pluggable domain functionality (e.g., `slack_plugin`, `notion_plugin`, `dnk_shopify_sync`).
  - Must NOT contain engine lifecycle logic.

### Invariant 3: Shared Utilities Canonicalization
Shared low-level primitives (such as structured JSON logging and metrics formatters) belong in:
```
packages/utils/
  ├── __init__.py
  └── logging.py                 # Structured JSON logger, formatters, setup_logging
```
Legacy namespaces (e.g. `packages/dnk_os/utils/logging.py`) must be converted to thin re-exports:
```python
from packages.utils.logging import JSONFormatter, get_logger, setup_logging

__all__ = ["setup_logging", "JSONFormatter", "get_logger"]
```

---

## 3. Deprecation Warning Elimination under Strict CI

When CI or verification scripts enforce `-W error::DeprecationWarning`:
1. **Direct Service Imports in Tests**:
   Update all tests targeting deprecated shims to use their canonical domain locations:
   - *Legacy*: `from core.supervisor import SupervisorEngine`
   - *Canonical*: `from services.dnk_shopify.supervisor import SupervisorEngine`
2. **Context-Managed Resource Handles**:
   Guard all file handles, ZIP archives, and socket connections with context managers (`with zipfile.ZipFile(...) as zf:`) to prevent `ResourceWarning: unclosed file` during strict warning evaluations.

---

## 4. Verification Pattern (`test_packages_consolidation.py`)

Always author an explicit test suite verifying the consolidation contracts:
```python
import pytest
import packages.adapters as pa
import core.adapters as ca
import core.plugins as cp
import packages.plugins as pp
from packages.utils.logging import get_logger, setup_logging

def test_adapters_consolidation_identity():
    # Verify that core.adapters re-exports the exact classes from packages.adapters
    assert pa.HermesAdapter is ca.HermesAdapter
    assert pa.DNKPatchrightAdapter is ca.DNKPatchrightAdapter
    assert pa.CanvasAdapter is ca.CanvasAdapter

def test_plugins_architectural_delineation():
    # core.plugins is governance engine
    assert hasattr(cp, "PluginManager")
    assert hasattr(cp, "PluginCard")
    # packages.plugins is the business plugin catalogue
    assert hasattr(pp, "AVAILABLE_PLUGINS")

def test_packages_utils_logging():
    logger = get_logger("consolidation_test")
    assert logger is not None
```
