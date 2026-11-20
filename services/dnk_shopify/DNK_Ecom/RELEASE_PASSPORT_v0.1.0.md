---
title: "DNK-Ecom-Zerno-v.0.1.0 Release Passport"
status: active
type: passport
domain: shopify
author: "DNK-e.com Maksym & Antigravity"
version: "0.1.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "services/dnk_shopify/DNK_Ecom/RELEASE_PASSPORT_v0.1.0.md"
> purpose: "Official Release Passport and Quality Gate Certification for DNK-Ecom-Zerno-v.0.1.0 ($350–$420 MSRP)."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "0.1.0"
> updated_at: "2026-11-20"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌾 DNK-Ecom-Zerno-v.0.1.0 («Зерно») — Official Release Passport

---

## 📌 1. Product Overview & Market Positioning
- **Theme Name**: `DNK-Ecom-Zerno-v.0.1.0` («Зерно» / `Zerno`)
- **Version**: `0.1.0` (Frozen until full working theme is approved)
- **Release Date**: 20 November 2026
- **Target Retail Price (MSRP)**: \$350 – \$420
- **Shopify Theme Store Category**: Multi-category D2C High-Conversion Flagship
- **Benchmark Donors**: Story, Shrine Pro, Sugar, Casaio, Tinker (Horizon 4.4.0 baseline)

---

## 🛡️ 2. Quality Gate & Certification Metrics
| Inspection Gate | Tool / Validator | Result | Target Metric |
| :--- | :--- | :--- | :--- |
| **Shopify Theme Check** | `shopify theme check --path .` | **0 Errors across theme files** | 0 errors |
| **Customer Templates** | Mandatory Suite Audit | **7/7 Present** (`account`, `login`, `register`, `addresses`, `order`, `activate`, `reset`) | 100% Present |
| **SaaP Theme Blocks** | SaaP Dual-Ready v2.0 Standard | **100% Valid Static & Dynamic Block Targets** | Zero broken block refs |
| **Locale Dictionaries** | Multilingual Schema Audit | **`en.default.json`, `uk.json` fully synchronized** | 100% Matching keys |
| **Zero External Tracking** | Cleanroom Sanitization Gate | **0 Foreign Pixels / 0 Remote CDNs** | 100% Cleanroom |

---

## 🧱 3. Included SaaP Dual-Ready v2.0 Blocks & SOTA Modules
1. **Sticky Add To Cart (`blocks/product_sticky-atc.liquid`)**:
   - Floating / Docked responsive modes with variant selector, real-time pricing and dynamic Add to Cart integration.
2. **Smart Cart Drawer 2.0**:
   - Structural clean blocks: `cart-drawer_empty.liquid`, `cart-drawer_body.liquid`, `cart-drawer_footer.liquid`.
   - In-drawer live subtotals, free shipping / rewards progress calculation, and 1-click upsells.
3. **Quantity Breaks V2 (`blocks/product_quantity-breaks-v2.liquid`)**:
   - Volume pricing tiers, gift unlocks, upsells, and schedule options.
4. **Pricing & Unit Price Architecture**:
   - Native integration with `snippets/price.liquid`, `snippets/unit-price.liquid`, and `snippets/price-styles.liquid`.
