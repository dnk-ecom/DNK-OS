<!-- --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/monorepo_pythonpath_and_service_topology_audit.md"
# purpose: "Guidance on monorepo PYTHONPATH configuration for packages/plugins and DDD service prefix invariants."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "Gerych Prime"
# --- END DNK-MRH-HEADER --- -->

# Monorepo PYTHONPATH & Service Topology Audit Protocol

## 1. Multi-Root PYTHONPATH Invariant (`packages/` & `services/`)
In a multi-root monorepo structure where packages or plugins reside under `packages/` (e.g. `packages/plugins/slack_plugin`), standard Python module discovery requires `packages/` to be explicitly added to `sys.path`.
- **Root Cause**: `pyproject.toml` may declare `packages` in package directories, but standalone scripts and pytest collectors running in subdirectories do not automatically resolve `plugins.<name>` unless `packages` is part of `PYTHONPATH`.
- **Enforcement Rules**:
  1. `tests/conftest.py` MUST ensure:
     ```python
     for extra in ["services", "packages"]:
         extra_path = str(ROOT / extra)
         if extra_path not in sys.path:
             sys.path.insert(0, extra_path)
     ```
  2. `scripts/verify_all.sh` MUST export:
     ```bash
     export PYTHONPATH="$HUB_ROOT:$HUB_ROOT/services:$HUB_ROOT/packages"
     ```
  Failure to include `$HUB_ROOT/packages` causes collection aborts (`ModuleNotFoundError: No module named 'plugins'`) across verification suites.

## 2. DDD Service Naming & Discovery Invariant (`services/dnk_*`)
All microservices located within `services/` MUST follow the invariant prefix `dnk_` (e.g., `services/dnk_alerting/`, `services/dnk_video_ai_creator/`).
- **Forbidden**: Unprefixed directory names (e.g., `services/media/`).
- **Remediation**: Rename uncanonical service directories to `services/dnk_<name>` or assimilate components into existing domain services.
- **Contract Test Alignment**: Dynamic service scanners in `tests/contracts/test_service_card_contract.py` scan `services/dnk_*`. Unprefixed folders bypass contract audits or cause schema validation failures.

## 3. Core Layer Demarcation (Clean 4-Layer Core)
To prevent core folder sprawl (e.g., accumulating 50+ arbitrary subfolders in `core/`):
- Active agent definitions must live strictly in `core/orchestrator/agents/`.
- Deprecated legacy directories (`core/agents/`, `core/swarm/`, `core/services/`) must be shimmed or pruned rather than left as parallel competing implementations.
- Active procedural skills must reside under `core/orchestrator/agents/gerych_prime/skills/`.

## 4. Root Namespace Shadowing via `sys.path.insert(0, ...)` (Pitfall & Invariant)
When an embedded framework or submodule (e.g., `core/hermes_agent/`) contains top-level folders matching standard monorepo namespaces (e.g., `plugins/`, `utils/`, `core/`):
- **Pitfall**: Doing `sys.path.insert(0, str(EMBEDDED_ROOT))` globally at the top of a test file permanently poisons `sys.path[0]`. Subsequent test collection for unrelated modules (e.g., `tests/integration/test_shopify_approval_preview.py`) importing `from plugins.<pkg>` will resolve to `core/hermes_agent/plugins/` instead of `packages/plugins/`, failing with `ModuleNotFoundError`.
- **Enforcement Rules**:
  1. NEVER insert embedded framework roots at index 0 of `sys.path` at module scope in test files.
  2. Use `sys.path.append(...)` or an isolated context manager/fixture:
     ```python
     @pytest.fixture
     def hermes_runtime_path(monkeypatch):
         monkeypatch.syspath_prepend(str(HERMES_AGENT_ROOT))
     ```
  3. Keep the monorepo root `$HUB_ROOT` and canonical roots (`services`, `packages`) strictly at the top of `sys.path`.

## 5. FastAPI Route Registry & Anti-Double-Mount Invariant
- **Pitfall**: Combining explicit `app.include_router(mod.router)` calls with dynamic discovery via `pkgutil.iter_modules(routers_pkg.__path__)` causes:
  1. Routers being mounted 2x or 3x (e.g., once bare, once under `/api`, and once dynamically).
  2. Deprecated / experimental router iterations (e.g., `canvas_router.py` vs `canvas_v3_router.py` vs `canvas.py`) being indiscriminately mounted, causing shadowed endpoints and OpenAPI schema pollution.
- **Enforcement Rules**:
  1. Use a single, declarative SSOT router registry in `apps/api/routers/__init__.py`.
  2. Group routers by domain (`routers/canvas/`, `routers/video/`, `routers/tasks/`).
  3. Eliminate unconstrained `iter_modules` auto-mounting in `apps/api/main.py`.

