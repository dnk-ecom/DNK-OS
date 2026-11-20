<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/shopify_cro_blocks/references/dual_ready_schema_standard.md"
# purpose: "Technical specification for SaaP Dual-Ready v2.0 Block Schema and render_tag standard in Shopify Tinker 4.2.0."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-13"
# author: "DNK Swarm (dnk_shopify & gerych_prime)"
# --- END DNK-MRH-HEADER ---
-->

# 📐 SaaP Dual-Ready v2.0: Theme Block Schema & Rendering Standard

## 1. Executive Summary & Paradigm

The **Dual-Ready v2.0** architecture provides bidirectional compatibility for Shopify theme components across both modern **Theme Blocks 2.0** (Tinker 4.2.0, Dawn 15+, Horizon) and classical **Online Store 2.0** sections/snippets:

1. **Native Mode (Theme Blocks 2.0)**: Executed autonomously inside `blocks/*.liquid`. Zero snippet dependency. Direct placement into container blocks (e.g. `main-product_details.liquid`) or root templates.
2. **Hybrid / Fallback Mode (OS 2.0)**: The exact same markup and logic can be rendered as a snippet `snippets/<block-name>.liquid` driven by a parent section schema via `{% render '<block-name>', block: block %}`.

---

## 2. Block Schema Specification (Tinker 4.2.0 JSON)

Every Dual-Ready block contains a strictly validated `{% schema %}` payload. Below is the canonical schema layout:

```json
{
  "name": "t:blocks.cro_widget.name",
  "target": "section",
  "class": "dnk-cro-block-wrapper",
  "settings": [
    {
      "type": "header",
      "content": "Visual Appearance"
    },
    {
      "type": "color",
      "id": "accent_color",
      "label": "Accent Color",
      "default": "#10b981"
    },
    {
      "type": "color",
      "id": "background_color",
      "label": "Background Color",
      "default": "#f0fdf4"
    },
    {
      "type": "range",
      "id": "border_radius",
      "min": 0,
      "max": 24,
      "step": 2,
      "unit": "px",
      "label": "Border Radius",
      "default": 8
    },
    {
      "type": "range",
      "id": "padding_vertical",
      "min": 4,
      "max": 32,
      "step": 4,
      "unit": "px",
      "label": "Vertical Padding",
      "default": 12
    },
    {
      "type": "header",
      "content": "Behavior & Triggers"
    },
    {
      "type": "checkbox",
      "id": "enable_animation",
      "label": "Enable Pulse Animation",
      "default": true
    }
  ],
  "presets": [
    {
      "name": "DNK CRO Widget Default"
    }
  ]
}
```

### Schema Rules & Constraints:
- `"target": "section"` or `"target": "head"`: Declares compatibility with Theme Blocks 2.0.
- **Unique Setting IDs**: IDs must use snake_case and be descriptive (`shipping_threshold`, `cutoff_hour`, `accent_color`).
- **No Trailing Commas**: Shopify's Theme Check and API strictly reject schemas with trailing commas.
- **I18n Translatability**: Schema names and labels should support translation keys (`t:sections...` or clean English fallback).

---

## 3. The `render_tag.liquid` Unified Contract

To achieve Dual-Ready capability without duplicating code, blocks encapsulate their rendering context resolution:

```liquid
{%- comment -%}
  Dual-Ready Context Resolver:
  Supports both native block execution (where `block` is provided by Theme Blocks 2.0)
  and section-level snippet render (where `block` is passed via `{% render '...', block: block %}`).
{%- endcomment -%}

{%- liquid
  assign current_block = block
  assign block_id = current_block.id | default: section.id | append: '-cro'
  assign b_settings = current_block.settings
-%}

<div
  id="dnk-block-{{ block_id }}"
  class="dnk-cro-block dnk-cro-block--{{ current_block.type | handleize }}"
  data-block-id="{{ block_id }}"
  {{ current_block.shopify_attributes }}
>
  <!-- Inner Component Content -->
</div>
```

---

## 4. CSS Cascading Layers Standard (`@layer theme, cro-blocks`)

Dual-Ready blocks must **never** conflict with parent theme typography or grid styles. All block styles are encapsulated in `@layer cro-blocks`:

```css
@layer theme, cro-blocks;

@layer cro-blocks {
  #dnk-block-{{ block_id }} {
    --dnk-accent: {{ b_settings.accent_color | default: 'var(--color-primary, #10b981)' }};
    --dnk-bg: {{ b_settings.background_color | default: 'var(--color-background, #ffffff)' }};
    --dnk-radius: {{ b_settings.border_radius | default: 8 }}px;
    --dnk-padding-y: {{ b_settings.padding_vertical | default: 12 }}px;

    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    margin: 12px 0;
    padding: var(--dnk-padding-y) 16px;
    background: var(--dnk-bg);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: var(--dnk-radius);
    font-family: inherit;
    font-size: 14px;
    line-height: 1.4;
    color: var(--color-foreground, #1f2937);
  }

  @media (max-width: 640px) {
    #dnk-block-{{ block_id }} {
      padding: calc(var(--dnk-padding-y) * 0.8) 12px;
      font-size: 13px;
    }
  }
}
```

---

## 5. Zero-Dependency Web Component Lifecycle Contract

Dual-Ready blocks use native custom elements (`customElements.define`) to ensure:
1. **Isolation**: No global scope pollution, no reliance on external jQuery or heavy libraries.
2. **Re-hydration**: Seamless support for Section Rendering API and dynamic theme events (`shopify:block:select`, `shopify:block:deselect`).

```javascript
if (!customElements.get('dnk-cro-widget')) {
  class DnkCroWidget extends HTMLElement {
    constructor() {
      super();
      this.abortController = null;
    }

    connectedCallback() {
      this.abortController = new AbortController();
      const signal = this.abortController.signal;

      this.initEvents(signal);
      this.render();
    }

    disconnectedCallback() {
      if (this.abortController) {
        this.abortController.abort();
      }
    }

    initEvents(signal) {
      // Listen for Cart updates (Section Rendering API / AJAX)
      document.addEventListener('cart:updated', this.onCartUpdated.bind(this), { signal });

      // Listen for Theme Customizer block inspection
      document.addEventListener('shopify:block:select', (event) => {
        if (event.detail.blockId === this.dataset.blockId) {
          this.highlight();
        }
      }, { signal });
    }

    onCartUpdated(event) {
      const cart = event.detail?.cart;
      if (cart) {
        this.updateState(cart);
      }
    }

    render() {
      // Dynamic DOM manipulation
    }

    highlight() {
      this.classList.add('is-customizer-focused');
    }
  }

  customElements.define('dnk-cro-widget', DnkCroWidget);
}
```
