---
name: ks_origin_assimilated
description: "Assimilated SOTA patterns and architecture from kondasoft/ks-origin."
version: "1.1.0"
category: "research"
assimilated_at: "2026-09-29"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_shopify"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/ks_origin_assimilated/SKILL.md"
purpose: "Assimilated SOTA patterns and architecture index for kondasoft/ks-origin."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.1.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🌐 KS-ORIGIN Assimilation Index

Meta-index for architecture, contracts, and component patterns assimilated from **[kondasoft/ks-origin](https://github.com/kondasoft/ks-origin)** (MIT License).

## 📌 Repository Intel & Legal Boundary
- **Repository**: `kondasoft/ks-origin`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `dnk_shopify` (with UI support from `gerych_builder`)
- **Architectural Directive**: Direct template and component integration is authorized.
- **Key Metric Advantage**: 3.7x leaner Liquid code (19k vs 71k lines in Dawn/Tinker), 4.5x lighter JS runtime (5.2k lines vs 23.4k lines), eliminates snippet sprawl (29 vs 145 snippets).

---

## 🏛️ 4 Core Architectural Patterns from KS-Origin

### 1. Theme Blocks & `{% doc %}` Tags
Modern Shopify OS 2.0+ architecture where sections embed reusable, nestable blocks (`blocks/*.liquid`) rather than delegating to sprawling legacy snippets (`snippets/product-card.liquid`).
- **Direct Block Rendering**: `blocks/product-card.liquid` renders `<article class="product-card">` directly, binds CSS variables (`--pt`, `--pb`), and renders nested subblocks via `{% content_for 'blocks', closest.product: closest.product %}`.
- **Atomic Subblocks (`blocks/_*.liquid`)**: Clean naming convention for private subblocks (e.g. `blocks/_product-card-form.liquid`, `blocks/_product-title.liquid`) keeping component trees modular and scope-isolated.
- **`{% doc %}` Tag Integration**: Embedded documentation at the head of Liquid blocks/sections parsed by Shopify Theme Check and AI Coding Agents for AST introspection without external documentation lookup:
  ```liquid
  {% doc %}
    @name Product Card
    @description Renders a product card with media, title, price, and buy actions.
    @param {product} closest.product - The product object to render.
  {% enddoc %}
  ```
- **Context Passing**: Parent context is passed cleanly downwards:
  ```liquid
  {% content_for 'blocks', closest.product: product %}
  ```

### 2. Agentic Commerce Protocol (`Shopify.actions` & `<s-view-event>`)
High-performance programmatic commerce surface designed specifically for autonomous shopping agents, AI bots, and modern Web Components without ad-hoc `fetch()` mutations.
- **Standardized Client Actions (`window.Shopify.actions`)**:
  ```javascript
  window.Shopify = window.Shopify || {};
  window.Shopify.actions = {
    getCart: async () => {
      const res = await fetch('/cart.js');
      return await res.json();
    },
    updateCart: async (updates) => {
      const res = await fetch('/cart/update.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates })
      });
      return await res.json();
    },
    openCart: () => {
      document.querySelector('cart-drawer')?.open();
    }
  };
  ```
- **Custom View Telemetry Web Component (`<s-view-event>`)**: Declarative HTML element backed by `IntersectionObserver` that emits standardized `shopify:view-event` telemetry:
  ```liquid
  <s-view-event data-event="{{ product | standard_event_data: 'view' }}">
    <!-- Product Card Content -->
  </s-view-event>
  ```
  ```javascript
  class SViewEvent extends HTMLElement {
    connectedCallback() {
      const data = this.dataset.event;
      if (!data) return;
      try {
        const payload = JSON.parse(data);
        document.dispatchEvent(new CustomEvent('shopify:view-event', { detail: payload }));
      } catch (e) {
        console.error('Invalid event JSON', e);
      }
    }
  }
  customElements.define('s-view-event', SViewEvent);
  ```

### 3. Zero-Bundler Import Maps & Lean Asset Pipeline
Eliminates heavy frontend build steps (Webpack/Vite) for storefront head scripts, relying on native browser ES module resolution.
- **Liquid Import Maps (`snippets/theme-head.liquid`)**:
  ```liquid
  <script type="importmap">
    { 
      "imports": { 
        "@shopify/standard-events": "https://cdn.shopify.com/storefront/standard-events.js" 
      } 
    }
  </script>
  <script src="{{ 'storefront-actions.js' | asset_url }}"></script>
  <script src="{{ 'storefront-events.js' | asset_url }}" type="module"></script>
  ```
- **Asynchronous Non-Render-Blocking CSS Delivery**: `print-onload` flip pattern for non-critical stylesheets combined with route-conditional loading:
  ```liquid
  {{ 'base.css' | asset_url | stylesheet_tag: preload: true }}
  {{ 'critical.css' | asset_url | stylesheet_tag: preload: true }}

  <link rel="stylesheet" href="{{ 'lazy-styles.css' | asset_url }}" media="print" onload="this.media='all'">
  <link rel="stylesheet" href="{{ 'quick-add.css' | asset_url }}" media="print" onload="this.media='all'">

  {% case request.page_type %}
    {% when 'product' %}
      <link rel="stylesheet" href="{{ 'main-product.css' | asset_url }}" media="print" onload="this.media='all'">
    {% when 'collection' %}
      <link rel="stylesheet" href="{{ 'main-collection.css' | asset_url }}" media="print" onload="this.media='all'">
  {% endcase %}
  ```

### 4. Theme Codex Protocol (Двофазний захист редагування схем)
Strict operational rules for AI coding agents to prevent Shopify live-reload errors and ensure design integrity:
- **Two-Phase Schema Mutation Protocol**:
  1. *Phase 1*: Mutate `.liquid` files (`sections/*.liquid`, `blocks/*.liquid`) and their `{% schema %}` definitions.
  2. *Phase 2*: After schema updates are saved, mutate dependent JSON files (`templates/*.json`, section-group JSON).
  - *Strict Rule*: NEVER batch schema changes and dependent JSON template changes in the same atomic tool call. The Shopify live uploader may process the JSON before the updated schema and reject unsupported settings.
- **Strict Schema Key Order**: `name` → `tag` → `class` → `settings` → `blocks` → `disabled_on`/`enabled_on` → `presets`.
- **Dynamic Mobile-First Spacing in EM**: Merchant settings remain in intuitive pixels (`0-80px` range, `2px` step for blocks; `0-160px` range, `2px` step for sections), but Liquid dynamically converts them to proportional `em` units:
  ```liquid
  {% style %}
    #block-{{ block.id }} {
      --pt: {{ block.settings.padding_top | divided_by: 16.0 }}em;
      --pb: {{ block.settings.padding_bottom | divided_by: 16.0 }}em;
    }
  {% endstyle %}
  ```
- **RGB Triplet CSS Variables for Alpha Compositing**: Space-separated RGB triplets in `:root` (`--color-surface: 255 255 255;`) allowing clean alpha transparency: `rgb(var(--color-surface) / 0.85)`.
- **CSS Selector Isolation**: Strict ban on grouping CSS selectors with commas (`.btn, .link { ... }` ❌). Each selector must have its own declaration block.
- **Mobile-First Responsive Breakpoints**: Base styles (mobile default) → Tablet (`@media (min-width: 600px)`) → Desktop (`@media (min-width: 1200px)`).

---

## 🧪 Quick Recipes (How to Use This Skill)

### Recipe A: Swarm Worker Task Delegation
Delegate implementation directly to **`dnk_shopify`**:
```python
from core.orchestrator.swarm_coordinator import SwarmCoordinator

coordinator = SwarmCoordinator()
res = coordinator.dispatch(
    agent="dnk_shopify",
    action="assimilate_adapter",
    payload={
        "technology": "kondasoft/ks-origin",
        "track": "Track 1: Direct Template Assimilation (Permissive)",
        "action": "Synthesize AST Liquid transformers, Shopify Functions (Wasm), and e-commerce schemas."
    }
)
```

### Recipe B: Clean Interface Contract Adoption
Integrate type-safe schemas into your local module:
```python
from pydantic import BaseModel, Field

class KsOriginThemeConfig(BaseModel):
    import_maps_enabled: bool = Field(default=True, description="Enable browser ES import maps")
    agentic_actions_enabled: bool = Field(default=True, description="Enable window.Shopify.actions")
    two_phase_schema_guard: bool = Field(default=True, description="Enforce two-phase schema/JSON mutation order")
```

## ⚠️ Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: Never hardcode absolute system paths. Always use `./` or `../`.
2. **[MRH_HEADER_INVARIANT]**: Any adapter or component generated from this pattern MUST carry `DNK-STD-0075` MRH header.
3. **[TWO_PHASE_SCHEMA_MUTATION]**: Never edit JSON templates simultaneously with Liquid schemas in the same tool call.
4. **[NO_SELECTOR_GROUPING]**: Keep all CSS selectors isolated without comma grouping to prevent cascading side-effects.
5. **[CANONICAL_TEMPLATE]**: Reference template located at `services/dnk_shopify/templates/AGENTS.shopify-theme.md`.
