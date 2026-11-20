---
name: shopify_cro_blocks
description: Production procedural skill for synthesizing SaaP Dual-Ready v2.0 CRO Theme Blocks in Shopify Tinker 4.2.0.
version: 2.0.0
author: DNK Swarm (dnk_shopify & gerych_prime)
category: shopify
---

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/shopify_cro_blocks/SKILL.md"
# purpose: "Canonical Procedural Production Skill for Shopify Dual-Ready v2.0 CRO Theme Blocks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-13"
# author: "DNK Swarm (dnk_shopify & gerych_prime)"
# --- END DNK-MRH-HEADER ---
-->

# 🛍️ Unified Shopify CRO Theme Blocks Production Skill (Dual-Ready v2.0)

## 1. Scope, Purpose & Governance
This skill defines the canonical standard for generating, injecting, and maintaining high-converting, atomic Conversion Rate Optimization (CRO) Theme Blocks in **Shopify Tinker 4.2.0** and **Online Store 2.0**.

### Core Governance Rules:
- **DEC-001**: Production theme runtime is strictly **Tinker 4.2.0** (Theme Blocks 2.0 architecture). Legacy monolithic sections are deprecated.
- **DEC-002**: **3-Shells Architecture** (`_blocks`, `main-product`, `main-cart`) paired with **Dual-Ready v2.0** block design.
- **DEC-005**: Offline skill distillation invariant: core skill file `SKILL.md` must remain strictly $\le 750$ lines. Detailed schemas and raw implementations reside in `references/`.
- **Zero-Dependency Invariant**: Blocks must never require external jQuery, Lodash, or bulky UI libraries. All interactive features are powered by native HTML5 Web Components and Vanilla ES6+.

---

## 2. The 3 Shells Architecture (DEC-002)

Every Shopify CRO theme assembly adheres to the 3 distinct shells:

```
┌────────────────────────────────────────────────────────┐
│                   SHELL 1: _blocks/                    │
│  Atomic, self-contained, theme-agnostic blocks         │
│  (e.g. dnk-free-shipping-bar, dnk-delivery-estimator)  │
└──────────────────────────┬─────────────────────────────┘
                           │ injected into
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│  SHELL 2: main-product  │       │   SHELL 3: main-cart    │
│  Contextual PDP Shell   │       │  Cart Drawer & Drawer   │
│  Auto-injection slots   │       │  Instant AJAX Sync      │
└─────────────────────────┘       └─────────────────────────┘
```

1. **Shell 1 (`_blocks/` or `blocks/`)**:
   - Atomic components located in `blocks/*.liquid`.
   - Contain their own schema, CSS layers, and Web Component scripts.
   - Usable as independent app blocks or native theme blocks in the Shopify Customizer.
2. **Shell 2 (`main-product.liquid`)**:
   - The product detail page (PDP) contextual shell.
   - Exposes dynamic block injection zones around buy buttons, gallery, and descriptions.
3. **Shell 3 (`main-cart.liquid` / `cart-drawer.liquid`)**:
   - The shopping cart shell.
   - Listens to Section Rendering API events and updates thresholds/progress bars without page refreshes.

---

## 3. Dual-Ready v2.0 Block Anatomy

Each CRO Theme Block is structured into 3 distinct, strictly isolated parts:

### Part 1: Schema Contract (`{% schema %}`)
- Fully compliant with Tinker 4.2.0 Theme Blocks 2.0.
- Declares `"target": "section"` or `"target": "head"`.
- Uses snake_case setting keys with semantic defaults.
- Zero trailing commas (strict Shopify Theme Check compliance).

### Part 2: Scoped Styles (`@layer theme, cro-blocks`)
- Encapsulated inside `@layer cro-blocks` to prevent leakage into theme typography or grid containers.
- Uses CSS variables bound to block settings:
  ```css
  @layer theme, cro-blocks;
  @layer cro-blocks {
    #dnk-block-{{ block.id }} {
      --dnk-accent: {{ block.settings.accent_color }};
      margin: 12px 0;
    }
  }
  ```

### Part 3: Isolated Web Component (Zero-Dependency Vanilla JS)
- Registered via `customElements.define` with a uniqueness check (`if (!customElements.get(...))`).
- Uses `AbortController` in `connectedCallback`/`disconnectedCallback` for clean event handling.
- Listens to native browser & Shopify events (`cart:updated`, `shopify:block:select`).

---

## 4. The 4 Essential CRO Block Patterns

For complete ready-to-use production implementations, see [cro_block_patterns.md](./references/cro_block_patterns.md):

| Pattern | Block File | Primary CRO Metric | Trigger / Integration |
|---|---|---|---|
| **A. Free Shipping Bar** | `blocks/dnk-free-shipping-bar.liquid` | Average Order Value (AOV) | Real-time threshold calculation via `cart.total_price` & `cart:updated` |
| **B. Dynamic Delivery Estimator** | `blocks/dnk-delivery-estimator.liquid` | Conversion Rate & Reduced Friction | Cutoff countdown, dynamic delivery dates, GeoIP country flag via FlagCDN |
| **C. Sticky Add-to-Cart** | `blocks/dnk-sticky-atc.liquid` | Mobile ATC Rate | `IntersectionObserver` observing primary PDP ATC button; AJAX `/cart/add.js` |
| **D. Scarcity Countdown Timer** | `blocks/dnk-countdown-timer.liquid` | Purchase Urgency / FOMO | LocalStorage/cookie state persistence, tabular-nums clock animation |

---

## 5. Step-by-Step Block Synthesis Workflow

When synthesizing a new CRO block for `services/dnk_shopify`:

```
Step 1: Define Schema & Settings
  └─ Determine inputs: colors, typography, toggles, thresholds.
  └─ Format into valid JSON {% schema %} per dual_ready_schema_standard.md.

Step 2: Markup & Liquid Context Resolution
  └─ Assign unique block id: assign block_id = block.id | default: section.id.
  └─ Render semantic HTML tags with data-* attributes.

Step 3: Encapsulate Scoped Styles
  └─ Wrap in @layer cro-blocks.
  └─ Apply CSS custom properties and mobile-first media queries.

Step 4: Attach Custom Element
  └─ Implement class extending HTMLElement.
  └─ Bind lifecycle hooks and AJAX event dispatchers.

Step 5: Verification & Quality Gate
  └─ Run AST syntax tests and Liquid balance checks.
  └─ Validate line count: SKILL.md ≤ 750 lines.
```

---

## 6. Verification & Quality Gates

To verify block integrity, execute the following deterministic gates:

1. **Schema Syntax Verification**:
   Extract and parse the JSON payload inside `{% schema %}...{% endschema %}` with `json.loads()` to catch syntax errors or invalid trailing commas.
2. **Liquid Tag Balance Check**:
   Ensure all `{% if %}`, `{% unless %}`, `{% case %}` tags have matching closing tags (`{% endif %}`, `{% endunless %}`, `{% endcase %}`).
3. **Core-Size Ratchet (DEC-005)**:
   ```bash
   wc -l core/skills/shopify_cro_blocks/SKILL.md
   # Must return ≤ 750 lines
   ```
4. **Pytest Suite**:
   ```bash
   ./.venv/bin/pytest tests/core/test_shopify_cro_blocks_skill.py
   ```

---

## 7. Reference Documentation

- [Dual-Ready Schema Standard](./references/dual_ready_schema_standard.md): Detailed schema specs, setting types, and `render_tag.liquid` contract.
- [Production CRO Patterns](./references/cro_block_patterns.md): Full source code for the 4 core CRO block patterns.
