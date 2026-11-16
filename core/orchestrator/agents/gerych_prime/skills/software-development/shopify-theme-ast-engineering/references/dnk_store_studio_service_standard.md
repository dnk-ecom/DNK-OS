# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/dnk_store_studio_service_standard.md"
# purpose: "Reference architecture for DNK Store Studio under DNK_SERVICE_SPECIFICATION_STANDARD_v1.0"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🏪 DNK Store Studio: Canonical Microservice Standard (v1.0)

## 1. Overview & Service Positioning
- **Product Name**: DNK Store Studio (`services/dnk_store_studio`)
- **Offer**: "Універсальна студія генерації веб-компонентів, CRO-механік та автономних лендінгів з адаптером для Shopify OS 2.0"
- **Architecture Boundary & Domain Division (ADR 168)**: 
  - `services/dnk_store_studio` (Port 8081): **Universal Web & CRO Component Studio** (Platform-Agnostic Core: HTML5, Tailwind CSS, Vanilla JS, Design Tokens, Visual Reverse Engineering, Standalone Prototypes, CRO Cart Drawer, PDP Bundles + Platform Exporter Layer `ShopifyThemeAdapter`).
  - `services/dnk_shopify` (Port 8000/8009): **Store Fleet & Deployment Gateway** (Platform-Specific: Shopify Admin GraphQL API, OAuth/tokens, Webhook Event Bus, Storefront Theme Deployment, and Canonical Theme Submodule SSOT `services/dnk_shopify/DNK-e.com`).
- **Base Theme Engine**: DNK Ecom (based on Shopify Horizon Tinker)
- **Specification Standard**: `docs/specs/DNK_SERVICE_SPECIFICATION_STANDARD_v1.0.md`
- **Architectural Decision Record**: `docs/notes/168_architectural_split_dnk_shopify_and_dnk_store_studio.md`
- **Manifest Schema**: `docs/schemas/service_card.schema.yaml` (`apiVersion: dnk.hub/v1alpha1`, `kind: ServiceCard`)
- **Port**: 8081 | **Health**: `/api/v1/dnk_store_studio/health`

## 2. Mandatory Unified Microservice Anatomy
```text
services/dnk_store_studio/
├── service_manifest.yaml     # ServiceCard (apiVersion: dnk.hub/v1alpha1, kind: ServiceCard)
├── README.md                 # Overview, agent roles, quickstart CLI & API curl
├── main.py                   # Consolidated FastAPI app, routers, models, backward-compat exports
├── docs/
│   ├── SPECIFICATION.md      # Functional specs, limits, invariants, dual-loop model
│   ├── ARCHITECTURE.md       # Component diagram, data flow, AST engine, VLM integration
│   └── RUNBOOK.md            # Local verification commands, failure diagnostics, test recipe
├── schemas/
│   ├── contracts.py          # Inbound/outbound Pydantic contracts (TaskPayload, TaskResponse)
│   └── domain_models.py      # Domain schemas (TinkerBlockNode, ThemeMigrationResult, etc.)
├── src/
│   ├── router.py             # FastAPI APIRouter with /tasks, /health, /metrics
│   ├── media_api.py          # Shopify GraphQL/REST Media API client
│   ├── app/                  # Service bridge, super-admin, launchpad routers
│   ├── adapters/             # Theme converters and adapters
│   └── engine/               # Transpiler, Liquid compiler, Vite pipeline, theme exporters
├── data/                     # Mega component registry, scan reports, bundle definitions
├── tools/
│   └── service_tools.py      # MCP tools for agent dispatch
└── tests/
    ├── test_core_contract.py # Contract validation (manifest, schema, router, tools)
    └── test_domain_logic.py  # Unit tests for domain logic

Note: Themes are NOT stored locally inside `themes/` to avoid massive file duplication. All theme paths target the SSOT at `services/dnk_shopify/` (`DNK-e.com` submodule and `DNK_Horizon_Tinker` working copy).

## 3. Dual-Loop Operational Model
1. **Developer Loop (Infrastructure & Core Theme)**:
   - Maintains the base DNK Ecom theme engine (`theme_adapter.py`, `mechanical_transpiler.py`, `liquid_compiler.py`, `shopify_vite_pipeline.py`).
   - Adapts legacy themes into isolated Tinker blocks (`blocks/*.liquid`).
   - Ensures AST validity, JSON Schema compliance, and CI test coverage.
2. **Customer / Agent Loop (High-Level Interaction)**:
   - Gerych (Hermes Prime) or human store owner sends conversational intents (`POST /tasks` or MCP tools).
   - Domain engines synthesize full stores, cart drawers, or bundles without manual coding.
   - Outputs ready-to-deploy Shopify OS 2.0 theme ZIPs.

## 4. MCP Tools & API Interface
Exposed via `tools/service_tools.py` and `main.py`:
- `dnk_store_studio_migrate_theme(source_theme_path, target_theme_path, block_prefix)`
- `dnk_store_studio_synthesize_store(niche, store_name, conversion_focus)`
- `dnk_store_studio_generate_blocks(html_content, component_type, style_tokens)`
- `shopify_builder_compile_section(html, section_name)`
- `shopify_builder_cart_drawer(config)`
- `shopify_builder_pdp_bundles(config)`
- `shopify_validate_liquid(liquid_code)`

## 5. Domain Separation & Deduplication Invariant (ADR 168)
- **Single Responsibility Principle & Platform Agnosticism**:
  - `dnk_store_studio` operates as a **Platform-Agnostic Web Studio**: generates clean HTML/Tailwind/Vanilla JS artifacts, landing pages, and CRO modules without immediate Shopify entanglement. Contains the `ShopifyThemeAdapter` exporter layer to convert universal components into Shopify OS 2.0 theme blocks and sections.
  - `dnk_shopify` acts as the **Store Fleet & Deployment Gateway**: handles Shopify GraphQL Admin API calls, OAuth credentials, store telemetry, webhook subscriptions, and pushes compiled themes/sections into live stores.
- **Zero-Duplication Invariant**: Never keep duplicate sprint runner engines (`sprint*_engine.py`) or duplicate theme copies. Upstream themes are hosted exclusively under `services/dnk_shopify/`.
