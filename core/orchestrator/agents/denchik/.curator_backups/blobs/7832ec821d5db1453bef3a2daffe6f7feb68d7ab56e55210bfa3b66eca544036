# Shopify Theme Blocks 2.0 Battle Playbook & Clyro-Style Agentic Pipeline (v2.0)

## Overview
This reference formalizes the v2.0 evaluation matrix for Shopify Theme Blocks 2.0 compliance, benchmarking themes (KS Origin, Tinker, Story, Casaio), and documents the two-phase agentic storefront synthesis pipeline (Pre-design Prototype -> 4-Gate Shopify Helix Synthesis) with decoupled client reactivity and strict depth-bounded DAG compilation.

---

## 0. Binary Gate 0: License & Compliance Pre-Screening
Before scoring architectural purity, any theme under assimilation must pass the binary legal gate:
- **Track 1: Permissive Open-Source (MIT / Apache 2.0 / BSD)**:
  - Direct code reuse and component assimilation into `DNK-ecom` is permitted.
  - *Benchmark Reference*: **KS Origin (KondaSoft)** (100% MIT).
- **Track 2: Commercial / Copyleft (Shopify Theme Store / GPL / AGPL)**:
  - Direct code copying is strictly forbidden.
  - Clean-room architectural synthesis only: reverse-engineer container grid patterns and schema designs without copying source.
  - *Benchmark References*: **Shopify Tinker 4.2.0**, **Story Basic 4.0.0**, **Casaio 1.1.0**.

---

## 1. The 10-Principle Theme Blocks 2.0 Architectural Evaluation Matrix

1. **P1: Pure Block Atomicity (`blocks/`) (15%)**
   - Zero monolithic sections > 350 lines.
   - Target: > 80% UI components decomposed into standalone `blocks/*.liquid`.
2. **P2: Nested Blocks Support (`content_for 'blocks'`) (15%)**
   - Native `{% content_for 'blocks' %}` used in sections and container blocks instead of flat `{% for block in section.blocks %}`.
3. **P3: Contextual Binding via `closest.*` (10%)**
   - Use `closest.product`, `closest.collection` in nested child blocks instead of global `all_products` or leaky variable scopes.
4. **P4: Schema Isolation & Block Targeting (10%)**
   - Strict declaration of `target`, `accepts`, and `valid_children` in block `{% schema %}`.
5. **P5: Dawn Snippet Elimination (10%)**
   - UI elements (e.g., `product-card.liquid`) must be autonomous blocks in `blocks/`, not static includes in `snippets/`. Snippets are reserved for pure logic helpers.
6. **P6: Modular Web Components JS (10%)**
   - Zero monolithic `global.js`. Independent `customElements.define` micro-controllers scoped per block.
7. **P7: Lazy Assets & Performance (10%)**
   - Non-render-blocking CSS via `media="print" onload="this.media='all'"`. Critical styles inlined. Target: 95+ Mobile PageSpeed, 0 CLS.
8. **P8: Decoupled Event Bus Protocol (10%)**
   - Standardized lightweight Pub/Sub event bus (`window.dnkBus`) for decoupled communication between independent Web Components (variants, cart drawer, pricing).
9. **P9: App Block Compatibility (`@app`) (5%)**
   - All universal container sections/blocks must explicitly accept app blocks (`"accepts": ["@app", "@default"]`).
10. **P10: AST Predictability & Max Depth Invariant (5%)**
    - JSON templates (`templates/*.json`) must pass deterministic validation via `ThemeBlocksDAGCompiler` (`services/dnk_shopify/tools/template_compiler.py`).
    - **Max Nesting Depth Invariant <= 3**: Section (1) -> Container Block (2) -> Leaf Block (3). Nesting depth >= 4 is rejected to prevent Shopify Theme Customizer UI thread freezes.

---

## 2. Competitive Theme Scorecard Summary (v2.0)

- **KS Origin (KondaSoft)**: 95/100 🏆 (Track 1 MIT, 213 files, 19k LOC Liquid, 5.2k LOC JS, 29 snippets, 71 `closest.*`, clean Web Components). Benchmark baseline for DNK Store Studio.
- **Shopify Tinker 4.2.0**: 84/100 (Track 2 Commercial, 481 files, 71k LOC Liquid, 106 `closest.*`, 45 `content_for 'blocks'`). SOTA reference for nested container grid layouts.
- **Story Basic 4.0.0**: 74/100 (Track 2 Commercial, 390 files, 52k LOC Liquid, hybrid blocks/snippets).
- **Casaio 1.1.0**: 54/100 (Track 2 Commercial, 520 files, 78k LOC Liquid, monolithic snippets). Reference only for CRO widget patterns (packaged as separate add-on blocks, not core theme).

---

## 3. Decoupled Event Bus Specification (`assets/dnk-event-bus.js`)

To keep Web Components isolated without tight coupling or global spaghetti:
```javascript
window.dnkBus = window.dnkBus || {
  events: {},
  on(event, callback) {
    if (!this.events[event]) this.events[event] = [];
    this.events[event].push(callback);
    return () => this.off(event, callback);
  },
  off(event, callback) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  },
  emit(event, payload = {}) {
    if (this.events[event]) {
      this.events[event].forEach(cb => {
        try { cb(payload); } catch (e) { console.error(`[dnkBus: ${event}]`, e); }
      });
    }
    window.dispatchEvent(new CustomEvent(`dnk:${event}`, { detail: payload }));
  }
};
```

### Standardized Events:
- `variant:change`: Triggered by variant picker; updates pricing, inventory badges, and main media gallery.
- `cart:updated`: Emitted on line item mutations; synchronizes cart count badges and drawer contents.
- `cart:add:success`: Signals drawer components to reveal without page refresh.
- `drawer:toggle`: Unified open/close hook for slide-out menus and drawers.

---

## 4. Theme Blocks 2.0 DAG Template Compiler

Autonomous agents must never write raw JSON templates by hand. All mutations must route through `ThemeBlocksDAGCompiler` (`services/dnk_shopify/tools/template_compiler.py`):
- Enforces `MAX_RECOMMENDED_DEPTH = 3`.
- Enforces complete symmetry between `block_order` and `blocks` dictionary.
- Provides atomic mutation APIs: `add_section`, `add_block`, `remove_block`, `update_settings`.
- Validates clean exportable JSON structure.

---

## 5. Two-Phase Clyro-Style Agentic Storefront Pipeline

### Phase A: Visual Pre-Design & Prototype Synthesis
1. **Inspiration & Visual Mining**: Extract design tokens and structure from competitor DTC stores via vision tools.
2. **Design System Tokenization**: Formulate `DESIGN_SYSTEM.json` (typography, color semantic tokens, spacing scales, border radii).
3. **Interactive Fast Prototype**: Generate single-file HTML + Tailwind CSS prototype of the target page/section.
4. **Iterative Refinement**: Refine layout visually; back-propagate token mutations into the design system SSOT.

### Phase B: 4-Gate Shopify Helix Synthesis (Shopify AI Labs Workflow)
1. **Checkpoint Planner**: Break down generation into small, verifiable checkpoints ordered by dependency.
2. **Gate 1 - Behavior Gate (TDD & AST)**: Validate Liquid syntax (`dnk_shopify_validate_liquid`), schema JSON, and DAG depth (`ThemeBlocksDAGCompiler`).
3. **Gate 2 - UI Review Gate (Spatial Awareness)**: Multimodal visual diff comparing rendered Liquid with the HTML prototype.
4. **Gate 3 - Adversarial Review Gate (Red vs Blue)**: Red-team auditor vs Blue-team builder iterative loop until 0 defects remain.
5. **Gate 4 - HITL Sign-off**: Human verification checkpoint with learnings recorded in persistent memory.

---

## 6. 3rd-Party & CRO Widget Injection in Theme Blocks 2.0 Architecture

When injecting custom CRO widgets (such as delivery estimators, countdown timers, trust badges) into modern Theme Blocks 2.0 themes (e.g. Shrine Theme Pro, Horizon, Dawn 15+):

### 1. The Container Block Pattern
In Theme Blocks 2.0, `sections/main-product.liquid` no longer houses an inline `{%- case block.type -%}` loop. It delegates product information to container blocks:
```liquid
{% content_for 'block', id: 'details', type: 'main-product_details' %}
```
And the container block (`blocks/main-product_details.liquid`) renders dynamic child blocks via:
```liquid
{% content_for 'blocks' %}
```

### 2. Autonomous Leaf Block Creation (`blocks/<handle>.liquid`)
Create an independent leaf block that encapsulates rendering and schema presets:
```liquid
{% render 'widget-core-snippet', block: block %}

{% schema %}
{
  "name": "⚡ My Custom Widget",
  "tag": null,
  "settings": [ ... ],
  "presets": [
    { "name": "⚡ My Custom Widget" }
  ]
}
{% endschema %}
```

### 3. Container Whitelisting Invariant
For the leaf block to appear in Shopify Customizer's **+ Add block** menu inside product details, the container block (`blocks/main-product_details.liquid`) must declare it in its schema:
```json
{
  "type": "main-product_details",
  "blocks": [
    { "type": "@app" },
    { "type": "title" },
    { "type": "price" },
    { "type": "my-custom-widget" }
  ]
}
```
*Note*: Also register in `sections/featured-product.liquid` or `blocks/container--product.liquid` if the widget should be available across homepage featured products.

### 4. Template JSON Hierarchy Invariant (`templates/product.json`)
Theme Blocks 2.0 structures block instances hierarchically under the container block rather than flatly at the section root:
```json
{
  "sections": {
    "main-product": {
      "type": "main-product",
      "blocks": {
        "details": {
          "type": "main-product_details",
          "blocks": {
            "details-my_custom_widget": {
              "type": "my-custom-widget",
              "settings": {}
            }
          },
          "block_order": [
            "details-title",
            "details-price",
            "details-my_custom_widget"
          ]
        }
      }
    }
  }
}
```
Adding blocks to `sections["main-product"].blocks` instead of the inner `details.blocks` will cause silent drops or customizer schema mismatch.
