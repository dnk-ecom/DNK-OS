<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/shopify_agent_kit_reverse_engineering_and_audit_playbook.md"
purpose: "Playbook for Shopify theme audit, reverse engineering, and client store deployment distilled from Shopify-Agents-Kit and AI-Toolkit."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-28"
author: "DNK-e.com Maksym & Gerych"
--- END DNK-MRH-HEADER -->

# Shopify Theme Reverse Engineering & Parallel Code Audit Playbook

Distilled from `Shopify/Shopify-AI-Toolkit` and `toilahuongg/Shopify-Agents-Kit` (`shopify-cc-kit`).

## 1. Multi-Agent Parallel Theme Audit (Code Investigator Pattern)

When onboarding an existing Shopify theme for refactoring or reverse-engineering, execute a two-phase audit to isolate risks before modifying Liquid code.

### Phase 1: Theme Inventory & Surface Mapping
Construct a structured inventory table across all 7 canonical theme directories:

| Component Type | Count | Key Files / Entry Points | Primary Dependencies |
|----------------|-------|--------------------------|----------------------|
| `layout/` | N | `theme.liquid`, `password.liquid` | Header/Footer sections |
| `sections/` | N | `main-product.liquid`, `header.liquid` | Embedded snippets, settings schema |
| `blocks/` | N | `price.liquid`, `variant-picker.liquid` | Nested blocks, LiquidDoc |
| `snippets/` | N | `icon-*.liquid`, `product-card.liquid` | Render parameters |
| `templates/` | N | `product.json`, `index.json` | Section order & type mappings |
| `assets/` | N | `base.css`, `global.js` | CSS custom properties, JS bundles |
| `locales/` | N | `en.default.json` | Schema and string translation keys |

### Phase 2: Parallel Auditor Subagents
Dispatch dedicated parallel audits via swarm workers or subagents:

1. **Dead Code & Orphan Asset Detector**:
   - Trace all `{% render 'snippet' %}` and `{% section '...' %}` calls against the filesystem.
   - Detect unreferenced snippets in `snippets/` and unreferenced images/JS/CSS in `assets/`.
   - Identify obsolete Liquid templates (`templates/*.liquid`) that have been superseded by `templates/*.json`.

2. **Legacy Monolith vs Modern Theme Block Auditor**:
   - Scan `sections/*.liquid` for monolithic blocks hardcoded inside the section body.
   - Flag sections lacking `{% content_for 'blocks' %}` or using deprecated `for block in section.blocks` where modern OS 2.0 Theme Blocks (`blocks/*.liquid`) should be extracted.

3. **Schema & Internationalization Gate**:
   - Verify every `{% schema %}` JSON block against `@shopify/theme-check`.
   - Identify hardcoded user-facing strings in Liquid that bypass `{{ 'general.text' | t }}` or `locales/en.default.json`.

---

## 2. Reverse Engineering Theme Flow (Extracting White-Label Base)

To repurpose a customized theme into a reusable, white-label foundation for new client stores:

1. **De-branding & Token Extraction**:
   - Decouple all brand-specific colors, typography, and logos from hardcoded CSS files (`assets/*.css`).
   - Route all design tokens through `config/settings_schema.json` and declare CSS custom properties in `layout/theme.liquid`:
     ```liquid
     :root {
       --font-heading: {{ settings.heading_font.family }}, {{ settings.heading_font.fallback_families }};
       --color-primary: {{ settings.primary_color }};
       --color-accent: {{ settings.accent_color }};
     }
     ```
2. **Template Sanitization (`templates/*.json`)**:
   - Strip merchant-specific product IDs, collection handles, and image URLs from `settings_data.json` and `templates/*.json`.
   - Replace with generic placeholder IDs or standard demo fixtures.
3. **Automated Storefront Visual Inspection**:
   - Use headless browser automation (`agent-browser` pattern) to capture full-page desktop/mobile screenshots of key templates (`index`, `product`, `collection`, `cart`).
   - Validate that responsive layouts, sticky cart bars, and drawers remain functional across viewport breakpoints.

---

## 3. Client Onboarding Deliverables Kit

When delivering a new client store on top of the synthesized theme, complement the theme with transactional templates:

1. **High-Fidelity Email Notification Suite**:
   - Implement responsive HTML/Liquid notification templates (Order Confirmation, Shipping Confirmation, Abandoned Checkout Recovery) matching the theme's visual branding.
2. **Interactive 3D Media Integration (Three.js Pattern)**:
   - For client stores requiring interactive 3D product visualizers or AR previews, encapsulate Three.js canvas components inside isolated `blocks/*.liquid` with strict client-only dynamic loading to avoid blocking core Web Vitals.
