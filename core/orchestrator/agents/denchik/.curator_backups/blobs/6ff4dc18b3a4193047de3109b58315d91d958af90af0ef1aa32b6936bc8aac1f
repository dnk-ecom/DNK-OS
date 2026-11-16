# --- DNK-MRH-HEADER ---
# mrh_id: "references/saap_fastmcp_registry_and_backward_compatibility_invariants.md"
# purpose: "Canonical architectural invariants for SaaP FastMCP Dynamic Registry, In-Memory Caching, and Backward Compatibility."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-15"
# author: "Gerych Prime & Antigravity (Mentor)"
# --- END DNK-MRH-HEADER ---

# SaaP FastMCP Dynamic Tool Registry, In-Memory Caching & Backward Compatibility Invariants

## Core Principles

When extending service registries or manifest discovery engines with dynamic tool capabilities (such as FastMCP and ToolRAG), maintain three non-negotiable architectural invariants:

1. **100% Manifest Backward Compatibility**:
   - Upgrades from `v1alpha1` to `v1alpha2` (e.g. introducing `fastmcp_tools` alongside legacy `capabilities`) must be non-breaking.
   - Pydantic models must define new fields with default factories (`Field(default_factory=list)`) and dual-sync validators so that manifests omitting the new field parse cleanly without validation errors.
   - Legacy flat-dictionary manifests must continue to parse without exception.
   - Pre-existing verification test suites (e.g. `tests/verification/test_service_registry.py`) must remain 100% green without modifying the tests.

2. **In-Memory Tool Catalog Caching with Auto-Invalidation**:
   - Repeated ToolRAG evaluations and dynamic prompt injections must not cause repeated disk I/O.
   - Aggregated catalog snapshots are cached in memory (e.g. `self._fastmcp_catalog`).
   - Dynamic service registration (`register_service()`) must automatically invalidate the cache.
   - Explicit cache invalidation (`invalidate_cache()`) and forced re-scans (`force_refresh=True`) must be exposed for hot-reloading.

3. **Strict Scanning Boundary & Path Confinement**:
   - Discovery scanners must NOT traverse the entire repository tree.
   - Monorepo services must strictly adhere to the `services/dnk_*` naming convention; non-dnk directories (e.g. temporary scratch dirs, cache folders) are skipped.
   - Plugins must be scanned strictly under `packages/plugins/`.
   - Security boundary enforcement: attempts to register or load manifests originating outside sanctioned subpaths (e.g. `apps/` or `core/`) must be explicitly rejected with security exceptions.

4. **Contract Testing & Dual-Schema Compatibility during Service Manifest Migration**:
   - When migrating a service card/manifest to `apiVersion: dnk.os/v1alpha2`, `kind: ServicePluginCard` (e.g. `services/dnk_store_studio/service_manifest.yaml`), existing contract test suites (such as `tests/contracts/test_service_card_contract.py`) that strictly require legacy `service_card.yaml` will fail unless updated.
   - Contract test suites must implement dual-schema branching:
     * Services migrated to v1alpha2 `service_manifest.yaml` are validated using Pydantic `ServicePluginCard` models.
     * Legacy services with `service_card.yaml` continue to validate against v1alpha1 JSON Schema.
     * `ServiceRegistry` provides backward-compatible loader aliases (`load_manifest = register_service_from_file`).
   - Pre-flight test sanity: before executing multi-module test batches, verify workspace cleanliness (`git status -s`) to prevent cascading syntax or collection errors caused by untracked or corrupted sibling modules.

5. **ServicePluginCard Schema Contract for `canvas_widgets`**:
   - `canvas_widgets` entries are strictly validated via Pydantic model `ServiceCanvasWidgetCard` in `tests/contracts/test_service_card_contract.py`.
   - Mandatory field specification:
     * `node_type`: string identifier (e.g. `MediaRetentionNode`)
     * `display_name`: human-readable title (do NOT use `title` or `name`)
     * `category`: widget classification category (e.g. `media-engineering`, `marketing`)
     * `icon`: icon name (e.g. `Video`, `Activity`)
     * `component_path`: frontend component path (e.g. `apps/web/src/components/canvas/nodes/MediaRetentionNode.tsx`)
     * `inputs`: list of socket specs, each containing `socket_id`, `label`, and `type` (do NOT use loose `{name, type}`)
     * `outputs`: list of socket specs, each containing `socket_id`, `label`, and `type`
   - Using non-standard keys or omitting mandatory socket fields (`socket_id`, `label`) triggers fail-closed `ValidationError` during contract suite execution.

6. **Auditor Microservice Executable Entrypoint Pattern (`main.py`)**:
   - Every service declared with transport protocol `fastmcp` or `http` running via CLI subprocess (`python3 -m services.<name>.main`) must provide an executable `main.py` entrypoint.
   - The entrypoint must:
     * Instantiate `app = FastAPI(title=..., version=..., description=...)` with DNK-MRH header.
     * Include the domain's API router (`app.include_router(router)`).
     * Expose a CLI execution block using `uvicorn.run(app, host="0.0.0.0", port=PORT)` bound to the service's canonical port from `service_manifest.yaml`.
   - Import verification recipe:
     `.venv/bin/python3 -c "from services.<service_name>.main import app; print(app.title)"`

7. **Contract and Core Registry Test Resiliency across Formula and Schema Expansions**:
   - When core engines expand algorithmic outputs (e.g. `script_doctor` expanding hook formulas from 3 to 6 variations), contract and integration test assertions must use floor/relational assertions (`assert len(prescriptions) >= 3`) rather than brittle equality checks (`== 3`) unless checking an exact fixed enum.
   - For `ServiceRegistry` plugin assertions, verify presence of FastMCP tools (`assert len(card.fastmcp_tools) >= 1`) and ensure that endpoints reflect FastMCP routing conventions (e.g. `/mcp/` path prefix or explicit endpoints).
