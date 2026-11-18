---
title: "DNK Sovereign 1.0.0 Apex - Agent Governance & Architecture"
description: "Unified Architecture Invariants for DNK Sovereign 1.0.0 Apex Core."
mrh_id: "services/dnk_shopify/DNK_Sovereign_Apex/AGENTS.md"
status: Active
version: "1.1.0"
updated: 2026-11-18
tags:
  - shopify
  - apex
  - governance
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "services/dnk_shopify/DNK_Sovereign_Apex/AGENTS.md"
> purpose: "Unified Architecture Invariants for DNK Sovereign 1.0.0 Apex Core."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.1.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 👑 DNK Sovereign 1.0.0 Apex (Main Production Core)

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

3. **Zero-DRM & Zero-Framework (Pure Native Web Standards)**:
   - 0% Alpine.js, 0% jQuery, 0% React/Vue runtime overhead.
   - 100% standard W3C Web Components with Custom Elements and ES Modules.
   - Fluid typography via `clamp()` with zero Cumulative Layout Shift (CLS = 0.00).

4. **100% Theme Blocks 2.0 Architecture**:
   - Granular nesting (`blocks/*.liquid`), contextual rendering, and modern drag-and-drop hierarchy via `content_for 'blocks'`.
   - Dual-Level Quantity Breaks (Level 1: Inline within Quantity Selector, Level 2: Modular V2 Block).

5. **Internationalization (i18n)**:
   - Complete 1:1 translation parity between `locales/en.default.json` and `locales/uk.json`.

---

## 👥 Multi-Agent Swarm Roles & R&D Hub

- **Antigravity (Chief Mentor & Head of Orchestration)**: System architecture, invariants enforcement, and PR reviews.
- **Гєрич (Gemini 4 Carbon via Vertex AI in Terminal)**: Deep AST audit, SHA-256 controller, forensic deconstruction, running via `gerych-root`.
- **Денчік (Autonomous Builder & Master Developer)**: Code synthesis, FastMCP, Liquid transpilation, and Shopify CLI deployment.
- **R&D Lab & Knowledge Core (`donor-lab` branch)**:
  All 7 theme ecosystem audits (Ascendify, Casaio, Elixir, KS Origin, Shrine, Story, Sugar), 11 donor profiles, master blueprints (06, 08, 09, 10 Master Brain), and distillation tools reside in [`https://github.com/DNKShopify/DNK-e.com/tree/donor-lab`](https://github.com/DNKShopify/DNK-e.com/tree/donor-lab).

---

## 🌳 Branch Lifecycle & Promotion Gate

```
[Cleanroom Donors (Read-Only)]
  tinker, sugar, story, casaio, ella, shrine-pro, ks-origin, ascendify, elixir (v1.6.2)
       │
       ▼ (Grafting via deconstruct_donors.py)
[staging-lab] ──▶ 137 Theme Blocks 2.0 (includes 35 Elixir CRO & Advertorial blocks)
       │
       ▼ (Promotion via PR after schema & uk.json checks)
[staging] ──────▶ Pre-release testing, preview environments
       │
       ▼ (Strict PR & 7-Gate Integrity verification)
[main] ─────────▶ Sovereign Production Core ($350-$420 MSRP Grade)
```

---

## 🧬 11 Donor Genomes Catalog (`donor-lab`)

| Donor Branch | Cleanroom Version | Primary Genetic Contribution & CRO Role | Cleanroom Status |
| :--- | :--- | :--- | :--- |
| `donor/tinker` | Tinker 4.4.0 DNK | Canonical Horizon Core 2.0 architecture foundation | 🛡️ 100% Clean |
| `donor/sugar` | Sugar 2.3.12 DNK | Theme Blocks 2.0 gold standard, No-App Suite, 1172 tokens | 🛡️ 100% Clean |
| `donor/story` | Story 4.0.8 DNK | Premium Brand Storytelling & Modular Cart Drawer v4.0.8 | 🛡️ 100% Clean |
| `donor/casaio` | Casaio 1.1.0 DNK | Horizon + D2C CRO, Quantity Breaks, Lumin Reviews | 🛡️ 100% Clean |
| `donor/ella` | Ella 7.3.1 DNK | Enterprise Mega-Menu, High-SKU Collections & Filtering | 🛡️ 100% Clean |
| `donor/shrine-pro` | Shrine Pro 1.9.0 DNK | DTC Conversion Monster: Bundles, Upsells, Sticky Cart | 🛡️ 100% Clean |
| `donor/ks-origin` | KS Origin 1.0.0 DNK | Ultra-Light HTML5 `<dialog>` modals & base event bus | 🛡️ 100% Clean |
| `donor/ascendify` | Ascendify 2.10.0 DNK | 28 Built-in CRO Apps, Super-PDP sections library | 🛡️ 100% Clean |
| `donor/elixir` | **Elixir 1.6.2 DNK** | **DTC Advertorials, Comparison Tables, Listicles & Limited-Time Sales (35 TB 2.0 blocks)** | **🛡️ 100% Cleanroom (0 DRM, 0 Pixels)** |
| `donor/dnk-ecom-sections` | Sections 1.0.0 | 100 Sanitized CRO Sections & Cart Drawer adapters | 🛡️ 100% Clean |
| `donor/sections-vault` | Sections Vault | 1,040 standalone Single-File sections (`ss-*`, `qq-*`) | 🛡️ 100% Clean |

---

## 📚 Master Architecture Specs & Reference

- **Molecular Theme Architecture (DEC-076)**: [`docs/architecture/DNK_ECOM_AGENTIC_THEME_AND_ECOSYSTEM_MASTER_CORE.md`](https://github.com/DNKShopify/DNK-e.com/blob/donor-lab/docs/architecture/DNK_ECOM_AGENTIC_THEME_AND_ECOSYSTEM_MASTER_CORE.md)
- **Documentation Architecture & Agent Harness Spec**: [`docs/architecture/DNK_ECOM_THEME_DOCUMENTATION_AND_AGENT_HARNESS_SPECIFICATION.md`](https://github.com/DNKShopify/DNK-e.com/blob/donor-lab/docs/architecture/DNK_ECOM_THEME_DOCUMENTATION_AND_AGENT_HARNESS_SPECIFICATION.md)
- **Elixir Knowledge Base & Docs Audit**: [`audits/themes/elixir/ELIXIR_DOCUMENTATION_AND_KNOWLEDGE_BASE_AUDIT.md`](https://github.com/DNKShopify/DNK-e.com/blob/donor-lab/audits/themes/elixir/ELIXIR_DOCUMENTATION_AND_KNOWLEDGE_BASE_AUDIT.md)
- **Agentic Agency Framework**: [`docs/architecture/DNK_AGENTIC_AGENCY_MASTER_FRAMEWORK.md`](https://github.com/DNKShopify/DNK-e.com/blob/donor-lab/docs/architecture/DNK_AGENTIC_AGENCY_MASTER_FRAMEWORK.md)
- **Donor Directory Passport**: [`donor-lab/DIRECTORY.md`](https://github.com/DNKShopify/DNK-e.com/blob/donor-lab/DIRECTORY.md)
- **Theme Check Command**: `PATH="/opt/homebrew/opt/ruby/bin:$PATH" shopify theme check --fail-level error`

