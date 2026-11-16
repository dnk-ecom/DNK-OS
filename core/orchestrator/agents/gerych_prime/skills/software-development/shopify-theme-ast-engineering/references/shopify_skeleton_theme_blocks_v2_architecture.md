# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_skeleton_theme_blocks_v2_architecture.md"
# purpose: "Architectural audit, Shopify Canvas (Oct 2026), Sidekick agentic editor, StorefrontRenderer partial-rendering, and skeleton-theme specification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-06"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🦴 Shopify Skeleton Theme, Canvas & Agentic Block Architecture (Oct 2026)

## 1. Executive Summary & Canvas Paradigm
Shopify's `skeleton-theme` (Oct 2026) and the launch of **Shopify Canvas** (Oct 1, 2026) represent a fundamental paradigm shift away from the legacy Online Store 2.0 (Dawn/Sections) toward **spatial, AI-native, sectionless block-first composition**.

### What is Shopify Canvas?
- **Infinite Spatial Workspace**: Rather than editing a single page in an isolated iframe sidebar, Canvas lays out the entire store (Home, PDP, Collection, Cart, Checkout) on a single zoomable visual canvas (similar to Figma/Miro).
- **Live Code Execution**: Renders live executing storefront code with full interactivity, animation, dynamic device responsiveness, and multi-product previewing.
- **Sidekick AI Co-pilot**: Merchants collaborate with Sidekick using natural language to adjust global tokens (colors, radii, typography) and compose blocks.
- **Underlying Engine**: Driven by StorefrontRenderer (SFR) with the platform feature flag `shop.features.agentic_editor_enabled?`.

---

## 2. How to Enable, Launch & Test Canvas

### Store Requirements & Permissions:
1. **Store Tier**: Development store created under a Shopify Partner account or an active merchant store with the Canvas/Sidekick beta enabled.
2. **Mandatory Permission**: The staff member / collaborator account **MUST** have the **"Edit code"** permission in `Settings > Users and permissions`. Without "Edit code", Canvas cannot be opened.
3. **Admin Entry Point**:
   - Navigate to `Online Store > Themes`.
   - Look for the button **"Design in Canvas"** or create a new theme draft via **"Create theme in Canvas"**.
4. **Current Beta Launch Constraints**:
   - Themes edited in Canvas create an isolated branch/draft and do not receive automatic Theme Store updates.
   - Canvas themes do not appear when an app lists store themes via the standard Admin REST/GraphQL API.
   - At launch, Canvas does not yet support third-party Theme Store apps/embeds, Shopify Markets overrides, or multi-language translation workflows.

### Local Development & CLI Workflow:
```bash
# 1. Update Shopify CLI to latest release
npm install -g @shopify/cli@latest

# 2. Clone skeleton-theme (reference implementation)
git clone https://github.com/Shopify/skeleton-theme.git
cd skeleton-theme

# 3. Start local development server targeting the Canvas-enabled store
shopify theme dev --store=<your-canvas-dev-store>.myshopify.com

# 4. Strict Theme Check (zero overrides allowed)
shopify theme check
```

---

## 3. Skeleton Theme `AGENTS.md` Dialect & Invariants

Shopify's official `AGENTS.md` in `skeleton-theme` sets strict non-negotiables:

### 🚫 Prohibitions:
- **No `sections/` folder**: Zero sections, no `{% section %}` or `{% sections %}` tags.
- **No JSON templates**: Zero `templates/*.json`. Every page is declared directly in `templates/*.liquid`.
- **No schema presets**: Blocks do not define presets in their `{% schema %}`.
- **No inlined CSS/JS**: Zero `{% stylesheet %}` or `{% javascript %}` tags in Liquid. All styling and scripts reside in `assets/`.
- **No hardcoded routes**: Always use `routes.*` (`routes.cart_url`, `routes.root_url`, `routes.all_products_collection_url`).

### 🧩 Composition Rules:
1. **Template-Owned Containers**:
   ```
   layout/theme.liquid    → {% block 'container' %} (header) + <main>{{ content_for_layout }}</main> + {% block 'container' %} (footer)
   layout/password.liquid → <main>{{ content_for_layout }}</main>
   templates/*.liquid     → {% block 'container' %} → blocks / snippets / inline HTML
   ```
2. **The `{% block %}` Tag**:
   ```liquid
   {% block 'name', named_param: value %}
     Body content accessible as {{ content }}
   {% endblock %}
   ```
   - Always include the closing `{% endblock %}` tag, even when the block body is empty.
   - Named parameters matching schema settings populate `block.settings.<id>`.
   - Content between tags is exposed as `{{ content }}` (NOT `{{ block.content }}`).
   - Executable `{% block %}` tags are permitted **ONLY** in `layout/` and `templates/`, never nested directly inside block/snippet files.
   - Root elements of blocks must include `{{ block.shopify_attributes }}` for Canvas visual selection.

3. **LiquidDoc Documentation (`{% doc %}`)**:
   Every block starts with typed params:
   ```liquid
   {% doc %}
     @param {string} tag - HTML tag wrapper (e.g. 'div', 'section')
     @param {string} [alignment] - Flexbox alignment
     @param {string} content - Child content outlet
   {% enddoc %}
   ```

---

## 4. Server Partial Rendering (`{% partial %}`)
Skeleton Theme introduces partial-page hydration via `@shopify/partial-rendering`:
- **Liquid Tag**:
  ```liquid
  <div {{ block.shopify_attributes }}>
    {% partial 'liquid-tip' %}
      <p>{{ dynamic_tip_text }}</p>
    {% endpartial %}
  </div>
  ```
- **Client JS Runtime**:
  ```javascript
  import { partials } from "@shopify/partial-rendering";
  // Refreshes the DOM slice while preserving focus, scroll, and input state
  await partials.refresh("liquid-tip");
  ```
- **Platform Gate**:
  Guarded by `shop.features.agentic_editor_enabled?`. Without this flag, StorefrontRenderer raises `Unknown tag 'partial'`.

---

## 5. Horizon vs Skeleton Integration Matrix for DNK OS

| Dimension | Track 1: Production Public (Horizon / Tinker) | Track 2: Next-Gen Canvas (Skeleton v2) |
|---|---|---|
| **License** | Proprietary Shopify (No Theme Store redistribution) | Permissive **MIT** (Official Theme Store base) |
| **Structure** | `sections/*.liquid` + `templates/*.json` | `blocks/*.liquid` + `templates/*.liquid` |
| **Editor** | Classic Theme Customizer + Sections drag-and-drop | Shopify Canvas (Infinite spatial UI) + Sidekick |
| **App Blocks** | Fully supported (Theme App Extensions) | Evolving (Pending app block integration in Canvas) |
| **Partial Hydration** | Section Rendering API (`?section_id=...`) | `@shopify/partial-rendering` (`{% partial %}`) |
| **DNK CRO Blocks** | Encapsulated as section blocks or custom sections | Refactored into clean `blocks/*.liquid` with `{% doc %}` |

---

## 6. The Merchant Canvas Trap: Skeleton vs Tinker Baseline

### The Paradox:
- `skeleton-theme` is **Agent-First**: Designed for AI coding agents and developers writing code directly in `templates/*.liquid`.
- `tinker_baseline` (and Horizons / Dawn 15+) is **Merchant-First**: Designed for merchants visually composing layouts in Shopify Theme Customizer via `templates/*.json`.

### Why Rapidly Filling `skeleton-theme` with `settings_schema.json` is a Trap:
1. **Lack of Drag-and-Drop in Customizer**:
   Because `skeleton-theme` uses `templates/*.liquid`, the standard Shopify Theme Editor cannot add, delete, or reorder sections or blocks dynamically on the page. The merchant cannot build landing pages or rearrange marketing sections without editing code.
2. **Platform Feature Flag Lock (`agentic_editor_enabled`)**:
   `{% partial %}` in `skeleton-theme` triggers `Liquid error: Unknown tag 'partial'` on standard merchant stores that lack the closed-beta flag.

---

## 7. DNK Hybrid Canvas Engine Architecture (The Golden Path)

To achieve **1-second agentic page generation** while giving clients **100% native visual drag-and-drop in Shopify's official Canvas**, implement the **Hybrid Canvas Engine**:

1. **Storage Layer (JSON Templates)**:
   - Use standard `templates/*.json` (`index.json`, `product.json`, `page.landing.json`).
   - Enables Gerych (AI) to generate or mutate complete page layouts in <1s via RFC 6902 JSON patches.
   - Preserves 100% visual drag-and-drop and block reordering for the merchant in the official Shopify Theme Customizer.

2. **Universal Canvas Container Section (`sections/canvas-section.liquid`)**:
   - Ultra-minimalist container section using the Tinker `_blocks.liquid` bridge pattern:
   ```liquid
   {% capture children %}
     {% content_for 'blocks' %}
   {% endcapture %}
   <div class="dnk-canvas-section" {{ section.shopify_attributes }}>
     {{ children }}
   </div>
   {% schema %}
   {
     "name": "Canvas Section",
     "blocks": [{ "type": "@theme" }, { "type": "@app" }],
     "presets": [{ "name": "Canvas Section" }]
   }
   {% endschema %}
   ```

3. **Composable Atomic Blocks (`blocks/*.liquid`)**:
   - Built following `skeleton-theme` best practices: typed with `{% doc %}`, zero-bundler Vanilla Web Components, scoped CSS variables, and mandatory `{{ block.shopify_attributes }}` on root.
   - Houses all CRO elements (AOV tiers, sticky ATC, countdowns, shipping progress) as independently draggable blocks.

