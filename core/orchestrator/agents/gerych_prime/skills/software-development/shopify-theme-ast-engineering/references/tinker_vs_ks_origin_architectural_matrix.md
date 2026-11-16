<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/tinker_vs_ks_origin_architectural_matrix.md"
purpose: "Architectural audit, concrete metrics, and SOTA engineering standards comparing Tinker (v4.2.0) vs KS-Origin (main)."
status: "Active"
version: "1.1.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym & Gerych"
--- END DNK-MRH-HEADER -->

# 🏛️ Architecture Comparison & SOTA Patterns: Tinker (v4.2.0) vs KS-Origin (main)

A comparative architectural reference guide and SOTA engineering standard for building high-performance, agentic Shopify OS 2.0+ themes.

---

## 1. Concrete Codebase Metrics & Volume Analysis

| Metric | Shopify Tinker v4.2.0 | KS-Origin (main by KondaSoft) | Architectural Factor |
| :--- | :--- | :--- | :--- |
| **Origin & License** | Shopify Official Reference / Theme Store | KondaSoft Open Source / **MIT License** | Full commercial & reuse freedom with KS Origin |
| **Total Files** | 481 files | **213 files** | 2.3x lower file clutter in KS Origin |
| **Total Liquid Lines**| 71,644 lines | **19,130 lines** | **3.7x leaner Liquid code**; eliminates Dawn snippet sprawl |
| **Total JS Lines** | 23,438 lines across 81 files | **5,216 lines across 16 files** | **4.5x lighter JavaScript runtime**; native ES modules |
| **Total CSS Lines** | 2,055 lines across 3 files | **8,043 lines across 36 files** | Modular component-level styles with lazy loading |
| **Blocks Count** | 82 blocks | 62 blocks | KS uses clean `_product-*` atomic subblocks |
| **Sections Count** | 40 sections | 35 sections | 14 shared core section types |
| **Snippets Count** | **145 snippets** | **29 snippets** | **Eliminates Dawn legacy snippet delegation** |
| **Web Components** | 75 custom elements | 32 custom elements | Consolidated, zero-dependency `HTMLElement` extensions |
| **AI Specification**| None | **`AGENTS.md` included** | Built specifically for LLMs / AI Coding Agents |

---

## 2. Core Architectural Invariants from KS-Origin (SOTA Rules)

### Invariant A: Direct Block Rendering vs Snippet Sprawl
- **Anti-Pattern (Tinker / Dawn Legacy):** `blocks/product-card.liquid` captures children and renders `snippets/product-card.liquid`, which in turn renders `snippets/price.liquid`, `snippets/buy-buttons.liquid`, etc.
- **SOTA Pattern (KS-Origin):** Eliminates `snippets/product-card.liquid` entirely. `blocks/product-card.liquid` renders `<article class="product-card">` directly, binds CSS variables, and renders nested subblocks via `{% content_for 'blocks', closest.product: closest.product %}`.

### Invariant B: Asynchronous Non-Render-Blocking CSS Delivery
From `snippets/theme-assets.liquid`:
```liquid
{% comment %} Critical CSS loaded synchronously with preload {% endcomment %}
{{ 'base.css' | asset_url | stylesheet_tag: preload: true }}
{{ 'critical.css' | asset_url | stylesheet_tag: preload: true }}

{% comment %} Non-critical styles loaded via print-onload flip {% endcomment %}
<link id="lazy-styles" rel="stylesheet" href="{{ 'lazy-styles.css' | asset_url }}" media="print" onload="this.media='all'">
<link rel="stylesheet" href="{{ 'quick-add.css' | asset_url }}" media="print" onload="this.media='all'">

{% comment %} Route-conditional stylesheets based on request.page_type {% endcomment %}
{% case request.page_type %}
  {% when 'product' %}
    <link rel="stylesheet" href="{{ 'main-product.css' | asset_url }}" media="print" onload="this.media='all'">
    <link rel="stylesheet" href="{{ 'product-gallery.css' | asset_url }}" media="print" onload="this.media='all'">
  {% when 'collection' %}
    <link rel="stylesheet" href="{{ 'main-collection.css' | asset_url }}" media="print" onload="this.media='all'">
    <link rel="stylesheet" href="{{ 'facets.css' | asset_url }}" media="print" onload="this.media='all'">
{% endcase %}
```

### Invariant C: Spacing Calculation & Liquid Schema Rules
Merchant-friendly pixel sliders in schema (`settings_schema.json` / sections / blocks) must always be dynamically converted to `em` units in Liquid:
```liquid
{% style %}
  #block-{{ block.id }} {
    --pt: {{ block.settings.padding_top | divided_by: 16.0 }}em;
    --pb: {{ block.settings.padding_bottom | divided_by: 16.0 }}em;
  }
{% endstyle %}
```
- Block spacing range: `0` to `80px`, step `2px`.
- Section spacing range: `0` to `160px`, step `2px`.
- Resulting `em` units ensure spacing scales fluidly with font-size changes.

### Invariant D: RGB Triplet CSS Variables for Alpha Compositing
Colors in `:root` must be stored as space-separated RGB triplets, not hex codes:
```css
:root {
  --color-surface: 255 255 255;
  --color-text: 24 24 24;
}

/* Allows instant alpha compositing without calculating new hex values */
.element {
  background-color: rgb(var(--color-surface) / 0.85);
  color: rgb(var(--color-text));
}
```

### Invariant E: Mobile-First Responsive Breakpoints
1. Base styles: Mobile (no media query).
2. Tablet: `@media (min-width: 600px)`.
3. Desktop: `@media (min-width: 1200px)`.
4. Selector isolation: Never group CSS selectors with commas (`.btn, .link { ... }` ❌). Keep rules isolated so components can be modified or purged without side-effects.

---

## 3. Storefront Events & Storefront Actions (AI-Ready Runtimes)

### Native Storefront Events Web Component
KS-Origin implements an automated intersection-observer tracking component:
```html
<s-view-event
  data-event="product_view"
  data-payload='{"product_id": {{ product.id }}}'
></s-view-event>
```
Handled natively in `assets/storefront-events.js` via standard Web Pixel APIs and custom events.

### Standardized Cart Actions (`window.Shopify.actions`)
Replaces manual ad-hoc fetch mutations with formal action contracts:
```javascript
// Assets: storefront-actions.js
window.Shopify.actions.updateCart({
  updates: { [variantId]: quantity }
}).then(response => {
  document.dispatchEvent(new CustomEvent('shopify:cart:updated', { detail: response }));
});
```

---

## 4. Synthesis Recommendation for DNK OS

1. **Foundational Architecture**: Adopt **KS-Origin** as the base boilerplate for DNK Store Studio themes due to its MIT license, 3.7x smaller Liquid footprint, zero build steps, and native `AGENTS.md` alignment.
2. **Component Migration**: When porting complex conversion-optimized blocks from proprietary themes (e.g. Casaio or Tinker bundles), transpile them directly into KS-Origin's `blocks/` directory using native HTML5 `<dialog>` and `HTMLElement` Web Components.
