---
title: "Shopify Theme Developer Pulse Report (2026-11-18)"
description: "Automated Continuous Shopify Developer Changelog & Theme Standards Pulse Report."
mrh_id: "docs/notes/shopify_pulse/SHOPIFY_THEME_PULSE_2026-11-18.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/notes/shopify_pulse/SHOPIFY_THEME_PULSE_2026-11-18.md"
> purpose: "Automated Continuous Shopify Developer Changelog & Theme Standards Pulse Report."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛍️ Shopify Theme Developer Pulse Report (2026-11-18)

> **Джерело:** Офіційний фід `https://shopify.dev/changelog/feed.xml`  
> **Знайдено релевантних оновлень для тем:** 8  

| Дата | Категорія | Оновлення | Ключові теми |
| :--- | :--- | :--- | :--- |
| Sat, 14 Nov 2026 | `Action Required` | [App security updates: Thank you, plus what's required next](https://shopify.dev/changelog/app-security-updates-thank-you-plus-what-s-required-next) | `block` |
| Fri, 13 Nov 2026 | `API` | [Checkout Function `cart.deliverableLine` inputs now model `cost` and link to their relevant `cart.line`](https://shopify.dev/changelog/checkout-function-cart-deliverableline-inputs-now-model-cost-and-link-to-their-relevant-cart-line) | `cart`, `checkout` |
| Fri, 13 Nov 2026 | `API` | [Market metafields break ties between equally specific markets by market handle](https://shopify.dev/changelog/market-metafields-break-ties-between-equally-specific-markets-by-market-handle) | `theme`, `liquid`, `storefront` |
| Fri, 13 Nov 2026 | `Action Required` | [Market.metafields matches keys in any case as of Storefront API version 2027-01](https://shopify.dev/changelog/market-metafields-matches-keys-in-any-case-as-of-storefront-api-version-2027-01) | `storefront` |
| Wed, 11 Nov 2026 | `Dev Dashboard` | [App IP allowlists now support IP addresses and ASNs together, and up to 250 IPs](https://shopify.dev/changelog/app-ip-allowlists-now-support-ip-addresses-and-asns-together) | `section` |
| Wed, 11 Nov 2026 | `Action Required` | [Storefront MCP policies and FAQs tool is being deprecated in favor of UCP MCP Ask tool](https://shopify.dev/changelog/storefront-mcp-policies-and-faqs-tool-is-being-deprecated-in-favor-of-ucp-mcp-ask-tool) | `storefront` |
| Tue, 10 Nov 2026 | `App store` | [Shopify App Store submission requirements: build, grow, then expand](https://shopify.dev/changelog/shopify-app-store-submission-requirements-build-grow-then-expand) | `section` |
| Fri, 06 Nov 2026 | `API` | [Partner apps must enable bulk operations before use](https://shopify.dev/changelog/partner-apps-must-enable-bulk-operations-before-use) | `section` |

## 💡 Ключові висновки для DNK Sovereign Ecom Theme:
1. **Сувора відповідність новим правилам Liquid**: Усі шаблони перевіряються через актуальний `theme-check` на валідність схем та відсутність застарілих тегів.
2. **Theme Blocks 2.0**: Кожен новий CRO-блок повинен підтримувати параметризацію `{% content_for "block" %}` та `visible_if` налаштування.
3. **Storefront & Checkout Functions**: Повна міграція з легасі-скриптів на нативні функції Shopify.
