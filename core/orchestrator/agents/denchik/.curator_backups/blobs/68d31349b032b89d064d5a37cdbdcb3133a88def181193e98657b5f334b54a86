# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/dnk_shopify_agents_hooks_workflows_registry.md"
# purpose: "Canonical unified registry of all DNK OS Shopify Theme and Admin agents, skills, hooks, gates, and workflows."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# Canonical Registry: DNK OS Shopify Theme & Admin Agents, Hooks, Gates, and Workflows

Per **ADR-004-F** (`Consolidation of 3 Core Workhorses`), `services/dnk_store_studio` has been consolidated into `./services/dnk_shopify/studio/`. All Shopify Theme (Storefront/Liquid) and Shopify Admin (Admin API/Operations) capabilities reside under `./services/dnk_shopify/`, `./apps/api/`, and `./apps/shopify/`.

---

## 1. Agents & Sub-Agents

### A. Primary Swarm Worker
- **`dnk_shopify`**:
  - System Prompt: `./core/orchestrator/agents/dnk_shopify/prompts/system.md`
  - Service Manifest & Contract: `./services/dnk_shopify/dnk_manifest.yaml`, `./services/dnk_shopify/CONTRACT.md`
  - Theme Agent Template: `./services/dnk_shopify/templates/AGENTS.shopify-theme.md`

### B. Studio Sub-Agents (`./services/dnk_shopify/studio/orchestrator.py` — `DNKShopifyOrchestrator`)
1. **`Theme Agent` (`execute_theme_agent`)**: Global theme sections, layouts, and CSS variables (`sections/custom-hero.liquid`).
2. **`Section Agent` (`execute_section_agent`)**: Interactive OS 2.0 sections and quizzes (`sections/quiz-selector.liquid`).
3. **`Content Agent` (`execute_content_agent`)**: Advertorials, listicles, and CRO landing templates (`templates/page.advertorial.liquid`).

---

## 2. Pre-Commit Hooks, AST Validators & Admin Webhooks

### A. Storefront / Theme Hooks & Gates
1. **Native Liquid Validator (`dnk_shopify_validate_liquid` / `shopify.validate_liquid`)**:
   - Defined in `./core/orchestrator/tool_aliases.py`. Validates Liquid tag balance and `{% schema %}` JSON before file writes.
2. **Pre-Commit AST Validator (`./services/dnk_shopify/tools/theme_ast_validator.py`)**:
   - Blocks Shopify Theme Importer landmines: forbids `{% stylesheet %}` / `{% javascript %}`, enforces block `name <= 25` chars, and prevents pipe filters inside `image_tag` arguments.
3. **Theme Verification Script (`./core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/scripts/verify_shopify_theme.py`)**:
   - Checks UTF-8 BOM, trailing commas in `{% schema %}`, trailing content after `{% endschema %}`, and `section` scope propagation in `product-media-gallery`.
4. **Exhaustive Theme Integrity Gate (`./services/dnk_shopify/tools/validate_theme_integrity.py`)**:
   - 4-tier validation for migrated themes (JSON syntax, Shrine PRO tokens, App Embeds: TripleWhale/Judge.me/Klaviyo, and Cart Drawer block structure).
5. **Harness Convergence Gate (`evaluate_harness_gate` in `./services/dnk_shopify/server.py`)**:
   - Deterministic DOM/visual gate verifying `HarnessContract` (`visualPass: true`, `openDeltas: 0`).

### B. Shopify Admin Webhooks & Event Bus
1. **`ShopifyWebhookIngestor` (`./apps/api/services/shopify_webhook_ingestor.py`)**:
   - Validates `X-Shopify-Hmac-Sha256` signature and enforces idempotency (TTL deduplication by `webhook_id`) for `orders/create`, `checkouts/update`, `products/update`, and `inventory_levels/update`.
2. **`ShopifyWebhookEventBus` & `ShopifyWebhookBridge`**:
   - Files: `./apps/api/services/shopify_webhook_event_bus.py`, `./apps/api/services/shopify_webhook_bridge.py`, `./apps/api/routers/shopify_webhooks.py`, DB audit model `./apps/api/db/models/shopify_webhook_event.py`.

---

## 3. Workflows & Pipelines (Theme vs. Admin)

### A. Shopify Store Theme Workflows (Storefront / Liquid / CRO)
1. **Dual-Track Store Synthesis (`DualTrackStoreEngine`)**:
   - Files: `./services/dnk_shopify/studio/engine/dual_track_store_engine.py`, CLI `./services/dnk_shopify/tools/harness_runner.py`, MCP `dual_track_synthesize_store`.
   - Modes: `clone_and_restyle` (reference URL/HTML cloning) and `generative_cro` (niche-driven synthesis with `contract.json`, `dynamics.json`, `gate.json`, `visual-deltas.md`).
2. **Mechanical Transpilation & RFC 6902 Template State**:
   - Files: `./services/dnk_shopify/studio/engine/mechanical_transpiler.py`, `./services/dnk_shopify/studio/engine/template_state_engine.py`, router `./apps/api/routers/shopify.py`.
3. **Merchant Launchpad 3-Step Flow**:
   - Router: `./services/dnk_shopify/src/app/merchant_launchpad_router.py` (`/vibe-config` -> `/transpile-tokens` -> `/deploy`).
4. **Super Admin Donor Assimilation & Theme Migration**:
   - Files: `./services/dnk_shopify/src/app/super_admin_router.py`, `./services/dnk_shopify/studio/engine/theme_migration_orchestrator.py` (MCP `shopify_migrate_theme`), `./services/dnk_shopify/studio/engine/theme_exporter.py`.
5. **CRO Component Engines**:
   - Cart Drawer (`./services/dnk_shopify/studio/engine/cart_drawer_engine.py`, MCP `shopify_build_cart_drawer`) and PDP Bundles (`./services/dnk_shopify/studio/engine/bundles_engine.py`, MCP `shopify_build_pdp_bundles`).

### B. Shopify Admin Workflows (Admin API / Sync / Flow / Extensions)
1. **One-Click Product Launch (`dnk_one_click_product_launch` / `shopify.launch_product`)**:
   - File: `./services/dnk_shopify/workflow_orchestrator.py` (4-stage pipeline: CMO -> Shopify Theme & Product -> Video AI Reel -> CFO Unit Economics).
2. **Bidirectional Theme & Asset Sync Supervisor (`ShopifySyncSupervisor`)**:
   - Files: `./services/dnk_shopify/supervisor/shopify_sync_supervisor.py`, `./services/dnk_shopify/supervisor/shopify_diff_engine.py`, `./services/dnk_shopify/supervisor/shopify_api.py`, router `./apps/api/routers/shopify_ast_router.py` (`/api/v3/shopify/theme-push`).
3. **Shopify Admin GraphQL & Bulk Operations**:
   - Files: `./apps/api/services/shopify_graphql_engine.py` (with `TokenBucketRateLimiter`), `./apps/api/services/shopify_bulk_operations.py`, MCP `sync_product_catalog`.
4. **Shopify Flow Automation (`ShopifyFlowEngine`)**:
   - File: `./apps/api/services/shopify_flow_engine.py` (`create_order_fulfillment_flow`, `create_inventory_alert_flow` via GraphQL `flowCreate`).
5. **Shopify Functions (WASM), Checkout UI Extensions & Embedded Admin**:
   - Backend: `./apps/api/services/shopify_functions_wasm_engine.py`, `shopify_dynamic_discount_service.py`, `shopify_cart_transform_service.py`, `shopify_checkout_customization_service.py`, `shopify_post_purchase_upsell.py`, `shopify_payment_gateway_handler.py`.
   - App & Extensions: `./apps/shopify/embedded-admin/DNKAdminDashboard.tsx`, `./apps/shopify/extensions/` (`checkout-upsell`, `checkout-loyalty`, `post-purchase-upsell`), `./apps/shopify/theme-extensions/dnk-app-blocks/`, `./apps/shopify/pixels/dnk_pixel/DNKPixel.tsx`.
