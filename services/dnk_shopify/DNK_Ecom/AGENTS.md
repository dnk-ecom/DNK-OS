---
title: "DNK-Ecom-Zerno-v.0.1.0 - Agent Governance & Architecture"
description: "Unified Architecture Invariants for DNK-Ecom-Zerno-v.0.1.0 Core."
mrh_id: "services/dnk_shopify/DNK_Ecom/AGENTS.md"
status: Active
version: "0.1.0"
updated: 2026-11-20
tags:
  - shopify
  - zerno
  - governance
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "services/dnk_shopify/DNK_Ecom/AGENTS.md"
> purpose: "Unified Architecture Invariants for DNK-Ecom-Zerno-v.0.1.0 Core."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "0.1.0"
> updated_at: "2026-11-20"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌾 DNK-Ecom-Zerno-v.0.1.0 («Зерно») (Main Production Core)

Welcome to the sovereign e-commerce flagship core of DNK-e.com.
This repository branch (`main`) is the single source of truth for the production-ready theme ($350–$420 MSRP grade).

---

## 🛡️ Core Invariants & Quality Standards

1. **Mandatory 7-Gate Integrity Gate (Anti-Regression Barrier)**:
   - Every commit and PR must strictly pass all 7 gates of `python3 tools/verify_theme_integrity.py .`:
     * **Gate 1: Protected Organs Whitelist (POW)**: Absolute prohibition against deleting protected components (`snippets/quantity-breaks.liquid`, `snippets/qb-v2-migration.liquid`, `blocks/product_quantity-selector.liquid`, `blocks/product_quantity-breaks-v2.liquid`, `sections/cart-drawer.liquid`, etc.).
     * **Gate 2: Zero Dangling References**: Zero `MissingTemplate` errors on `{% render %}` and `{% section %}`.
     * **Gate 3: Template Structure Integrity**: All blocks and sections referenced in `templates/*.json` must exist.
     * **Gate 4: Cleanroom Zero-DRM**: 0 DRM calls, 0 killswitches (`document.body.innerHTML = ""`).
     * **Gate 5: Quotas & JS Engine**: All templates $\le 512\text{ KB}$, all JS passes `node --check`.
     * **Gate 6: Localization Parity**: 100% translation key parity between English and Ukrainian schemas.
     * **Gate 7: Live Storefront Smoke Test**: 0 Liquid runtime errors on live endpoints.

2. **Theme Check Zero-Offense Policy**:
   - Every commit must strictly maintain 0 errors and 0 warnings under `shopify theme check`.
