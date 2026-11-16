# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_dual_ready_v2_cro_blocks_playbook.md"
# purpose: "Playbook for SaaP Dual-Ready v2.0 CRO Theme Blocks in Tinker 4.2.0 and OS 2.0."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "DNK Swarm (dnk_shopify & gerych_prime)"
# --- END DNK-MRH-HEADER ---

# 🛍️ SaaP Dual-Ready v2.0 CRO Theme Blocks Playbook (Tinker 4.2.0 & OS 2.0)

## Overview & Governance
- **DEC-001**: Tinker 4.2.0 as the unified Shopify Theme Runtime.
- **DEC-002**: 3 Shells (`_blocks/`, `main-product.liquid`, `main-cart.liquid`) & Dual-Ready v2.0 blocks (`@app` & `@theme`).
- **DEC-005**: Strict skill core size ratchet (≤ 750 lines) with LOD extraction into references.

## The 3-Part Dual-Ready Anatomy
1. **JSON Schema (`{% schema %}`)**:
   - Snake_case IDs, valid JSON without trailing commas.
   - Presets for Theme Customizer.
2. **Scoped CSS Layers (`@layer theme, cro-blocks`)**:
   - Zero conflicts with parent theme styles.
   - CSS custom properties (`--cro-*`) mapped from schema settings.
3. **Vanilla JS Custom Element (`customElements.define`)**:
   - Zero external libraries (no jQuery, no Lodash).
   - `AbortController` for clean listener teardown on section rendering.
   - Native integration with Shopify AJAX Cart API (`/cart/add.js`, `/cart/change.js`, `cart:updated`).

## 4 Core CRO Block Patterns
1. **Free Shipping Progress Bar**: Real-time threshold calculation and cart drawer integration.
2. **Dynamic Delivery Estimator**: Cutoff hour timer, business day calculation, FlagCDN country indicators.
3. **Sticky Add-to-Cart Bar**: IntersectionObserver activation, variant selection sync, AJAX cart submission.
4. **Scarcity Countdown Timer**: LocalStorage countdown persistence, pulse animation, urgency triggers.

See canonical production skill `core/skills/shopify_cro_blocks/SKILL.md` for complete implementation details.
