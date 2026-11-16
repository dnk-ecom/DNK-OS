---
title: "Сесія 02: Майстер-аудит Shopify Local Theme DEV (Companion Knowledge Base)"
status: approved
type: report
domain: shopify
author: "Antigravity & Gerych-root"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/companion/audits/02_LOCAL_STOREFRONT_SESSION_AUDIT.md"
> purpose: "Канонічний майстер-аудит донора 02: Shopify Local Theme DEV (local-storefront) для бази знань агента-компаньйона DNK-ThemeCraft."
> canonical_source: false
> original_source: "SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/Local_Storefront_DEV_Audit/SESSION_AUDIT_SHOPIFY_LOCAL_THEME_DEV.md"
> alters_files: []
> triggers_tasks: []
> status: "Approved"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "Antigravity & Gerych-root"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ ДОНОР 02: SHOPIFY LOCAL THEME DEV (LOCAL-STOREFRONT ENGINE)

> **Повний канонічний звіт:** [`SESSION_AUDIT_SHOPIFY_LOCAL_THEME_DEV.md`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNKEcom/Audit_Shopify_Themes_Sell_WF/Local_Storefront_DEV_Audit/SESSION_AUDIT_SHOPIFY_LOCAL_THEME_DEV.md)  
> **Робочий каталог сесії:** [`Audit_Shopify_Themes_Sell_WF/Local_Storefront_DEV_Audit/`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNKEcom/Audit_Shopify_Themes_Sell_WF/Local_Storefront_DEV_Audit/)  
> **Локальний репозиторій ядра:** [`/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_Vibe/local-storefront`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_Vibe/local-storefront) (чистий Rust, 6 крейтів)

## 🔑 КЛЮЧОВІ ДИСТИЛЬОВАНІ ЗНАХІДКИ ТА АРХІТЕКТУРА:
1. **Sub-millisecond Rust Runtime (170–300 мкс)**: Заміна хмарного `shopify theme dev` (800–2500 мс) на детермінований локальний Liquid strict2 парсер (Ruby 5.14 порт).
2. **Theme Blocks 2.0 & `closest` Context**: Повна офлайн-підтримка рекурсивних блоків, що дозволяє запускати теми Sugar v2.3.10, Story v4.0.8 та Horizon без зв'язку з Shopify.
3. **Storefront AJAX & Section Rendering APIs**: Локальна емуляція `/cart.js`, `/cart/add.js`, `/cart/update.js` та `?section_id=...` для роботи Cart Drawer, Upsell та динамічних фільтрів.
4. **Власний Visual Customizer**: WebSocket Live-Reload канал (`GET /__lsf/livereload`) та Control API (`POST /__lsf/reload`) для миттєвого відображення правок у Visual Studio DNK OS (10 ms).
5. **Генерація прототипів за 30 секунд**: AI-агент генерує JSON-файли каталогу (`shopify-local/products/*.json`), `local-storefront` миттєво підхоплює вітрину, а після затвердження клієнтом — магазин пушиться в живий Shopify в один клік.
