# 🔄 Legacy Theme to Tinker Migration & Semantic Design Synthesis

This reference document defines the exact workflow and algorithms for migrating legacy monolithic Shopify themes (Shopify OS 1.0/2.0) into the modern modular Tinker (Shopify 3.0 / Horizon block-first) architecture, synthesizing new blocks using the Editable-Design visual prior paradigm, and positioning the commercial product as **DNK Store Studio**.

---

## 💎 Product Positioning & The Core Offer (MANDATORY INVARIANT)

* **Product Name**: **DNK Store Studio**
* **The Core Offer**:
  > **«Агентивний сервіс створення висококонверсійних магазинів на платформі Shopify»**
  > *(Agentic high-converting store creation & optimization service on Shopify)*

### Founder-Level Positioning Rule:
- **Never pitch or name tools around low-level implementation mechanics** (e.g., "theme migrator", "Liquid AST parser", "Tinker block synthesizer"). Customers and founders buy **business outcomes**:
  1. **High Conversion Rate (CR)**: 1-click sticky add-to-cart, frictionless checkout, social proof.
  2. **Average Order Value (AOV) Boost**: Smart bundles, quantity breaks, in-cart drawer upsells.
  3. **High Speed (Time-to-Market)**: Autonomous swarm creation in hours instead of months with design agencies.
  4. **Performance**: 100/100 Core Web Vitals and zero layout shift.
- The engineering stack (Tinker 3.0, Graphify, Liquid AST Transpiler, Editable-Design) is the **underlying unfair advantage** that delivers this offer with zero errors and maximum speed.

---

## 1. The Monolith-to-Block Problem

Legacy themes (e.g. `DNK_Ecom_v1_0_0.zip`) bundle entire page concepts into single monolithic sections (1,500+ lines in `main-product.liquid` or `main-cart.liquid`) with tight coupling:
- Markup mixes layout containers, pricing badges, swatch logic, and cart triggers.
- Snippets (`snippets/*.liquid`) are invoked via `{% render %}` or legacy `{% include %}` with undocumented parent-scope assumptions.
- Global `settings.*` keys are hardcoded in nested HTML blocks.

In contrast, **Tinker 4.3.1 (Shopify 3.0)** uses an atomic **Block-First Architecture**:
- Sections act as lightweight container scaffolding (`@app` or block renderers).
- Features are decoupled into independent `blocks/*.liquid` files, each declaring its own isolated `{% schema %}`.
- Merchants can drag-and-drop, reorder, or duplicate individual features directly in the Theme Editor.

---

## 2. Graph-Driven Migration Pipeline (Graphify + AST)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   GRAPHIFY MIGRATION PIPELINE                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INGEST & GRAPH: Extract AST call graph from legacy zip / directory  │
│    Legacy Section ──> Renders Snippets ──> Uses Settings ──> Assets    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. COMMUNITY DETECTION: Cluster monolithic markup into features       │
│    Monolithic Section ──> [Price Cluster] [Swatches] [Sticky ATC]      │
├────────────────────────────────────────────────────────────────────────┤
│ 3. BLOCK SYNTHESIS: Convert clusters into Tinker blocks                │
│    Cluster ──> blocks/tinker-*.liquid + isolated {% schema %}          │
├────────────────────────────────────────────────────────────────────────┤
│ 4. DEPENDENCY BUNDLING: Transfer required snippets & tokens            │
│    graphify path / affected ──> Zero broken snippets or missing SVGs   │
├────────────────────────────────────────────────────────────────────────┤
│ 5. TEMPLATE INTEGRATION: Re-wire templates/*.json via RFC 6902         │
│    template_state_engine.py ──> insert into block_order arrays         │
└────────────────────────────────────────────────────────────────────────┘
```

### Execution Steps:
1. **Extract Call Graph**:
   Run `ThemeIntelligence.build_dependency_graph()` to map all `render`, `section`, and `asset_url` calls.
2. **Cluster by Conversion Intent**:
   Use `ThemeAdapter.classify_component(name, content)` across categories:
   - `pdp_conversion`: sticky ATC, variant swatches, bundle offers, delivery countdowns.
   - `social_proof`: customer reviews, trust badges, star ratings.
   - `cart_and_checkout`: drawer upsells, free shipping progress bars.
3. **Decompose Markup**:
   Use `ThemeAdapter.adapt_legacy_section_to_tinker_block(section_name, target_block_name)`:
   - Strips top-level `{% schema %}` and `{% style %}` tags.
   - Emits a clean Tinker block in `blocks/tinker-[name].liquid`.
   - Synthesizes an isolated block schema (`name`, `tag: null`, `settings`).

---

## 3. Visual Prior Synthesis (Editable-Design Integration)

Inspired by the SOTA paradigm from `yejy53/Editable-Design` (**"Visual Prior, Without Pixel Shipping"**):

1. **Semantic HTML/CSS Layering**:
   - Design concepts (banners, promo grids, comparison tables) are drafted as semantic, layered HTML + Tailwind CSS with independent typography and images — never as flat pixel images (PNG/WebP).
2. **Mechanical Transpilation**:
   - Feed the semantic HTML into `services/dnk_shopify_builder/mechanical_transpiler.py`.
   - Structural text nodes become `type: "text"` or `"richtext"` settings.
   - Background and media elements become `type: "image_picker"` settings.
   - Design tokens map to CSS custom properties under `--dnk-*`.
3. **Automated Schema & Quality Gate**:
   - Validate against Shopify OS 2.0 / 3.0 schema specs using `liquid_compiler.validate_schema()`.
   - Run `shopify theme check` to ensure zero deprecated tags or unclosed blocks.

---

## 4. The 4-Stage MASE Migration Pipeline Pattern

When converting a full monolithic legacy theme (such as `DNK_Ecom_v1_0_0.zip`, 400+ files, 24k-line monolithic `main-product.liquid`) to the modular Tinker block architecture, divide execution into 4 deterministic slices:

| Slice | Stage | Core Deliverable & Invariants |
|---|---|---|
| **Slice 1** | **Scan & Dependency Extraction** | Ingest legacy zip into memory/temp; construct full dependency graph (AST parsing of `{% render %}`, `{% section %}`, `asset_url`). Sanitize Shopify JSON comments (`/* ... */`, `// ...`) with regex before parsing. |
| **Slice 2** | **Core PDP & Hero Deconstruction** | Extract monolithic markup into 8 isolated Tinker CRO blocks (`blocks/tinker-dnk-*.liquid`). Root element MUST contain `{{ block.shopify_attributes }}`. Each block defines its own `{% schema %}` with `"target": "section"`. |
| **Slice 3** | **OS 2.0 Template Generator** | Generate compliant Shopify OS 2.0 `templates/*.json` (`product.json`, `index.json`, `collection.json`, `cart.json`). Ensure each section specifies `"type"`, `"blocks"`, and strict `"block_order": [...]`. Validate via `validate_shopify_template_json()`. |
| **Slice 4** | **Packaging & API Endpoint** | Merge base Tinker framework with synthesized blocks and OS 2.0 templates. Package into binary ZIP distribution. Expose REST endpoints (`POST /migrate/dnk_ecom_to_tinker`) and register under DNK Agent Protocol v1. |

### 🛠️ Atomic CRO Tinker Blocks Inventory
Synthesize monolithic PDP and Hero features into modular, reorderable blocks:
1. `tinker-dnk-sticky-atc.liquid`: Viewport-docked quick conversion bar with live variant selector and instant checkout button.
2. `tinker-dnk-quantity-breaks.liquid`: Tiered volume pricing matrix (1x, 2x, 3x) with dynamic savings badges.
3. `tinker-dnk-countdown-timer.liquid`: Urgency countdown bar with customizable time limit and pulsing promo text.
4. `tinker-dnk-delivery-estimator.liquid`: Real-time stock status and dynamic delivery date calculation.
5. `tinker-dnk-bundle-offer.liquid`: Frequently Bought Together (FBT) 1-click multi-product bundle drawer.
6. `tinker-dnk-guarantee-benefits.liquid`: Risk-reversal assurance grid (30-day money back, SSL checkout, 24/7 support).
7. `tinker-dnk-hero-banner.liquid`: High-impact modular hero container with rich text and CTA controls.
8. `tinker-dnk-scrolling-ticker.liquid`: Continuous marquee ticker for store-wide announcements and social proof.

### 🧹 Shopify JSON Comment Stripping Recipe
```python
import re, json

def parse_shopify_json(raw_text: str) -> dict:
    # 1. Strip block comments /* ... */
    cleaned = re.sub(r'/\*.*?\*/', '', raw_text, flags=re.DOTALL)
    # 2. Strip single-line comments // ...
    cleaned = re.sub(r'//.*$', '', cleaned, flags=re.MULTILINE)
    return json.loads(cleaned.strip())
```
