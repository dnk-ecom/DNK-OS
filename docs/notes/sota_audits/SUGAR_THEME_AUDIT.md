---
title: "Sugar Theme SOTA Reverse-Engineering Dossier"
description: "SOTA Competitor Reverse-Engineering Dossier: Sugar Theme 2.2.3/2.3.6 (Cart Drawer, Sticky Product, Vendor Loader, Product Form) for Apex CRO."
mrh_id: "docs/notes/sota_audits/SUGAR_THEME_AUDIT.md"
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
> mrh_id: "docs/notes/sota_audits/SUGAR_THEME_AUDIT.md"
> purpose: "SOTA Competitor Reverse-Engineering Dossier: Sugar Theme 2.2.3/2.3.6 (Cart Drawer, Sticky Product, Vendor Loader, Product Form) for Apex CRO."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔬 Sugar Theme SOTA Reverse-Engineering Dossier

> **Контекст**: Дослідження здійснено в рамках задачі `node_t3_sugar_theme_audit` на канвасі `docs/canvas/projects/dnk_ecom/main.canvas`.
> **Джерело донора**: `../DNKEcom/DNK-Ecom_git_mirrow/sugar/assets/` (`sugar-cart-drawer.js`, `sticky-product.js`, `product-form.js`, `vendor-runtime-loader.js`, `global.js`).

---

## 1. 🛒 Shared Cart State Architecture (`sugar-cart-drawer.js@2.2.3`)

### Проблема, яку вирішує Sugar:
Коли на сторінці одночасно присутні: Drawer, Sticky ATC, Free Shipping Bar, Progress Bar та Upsell Blocks, кожен компонент традиційно відправляє окремий запит до `/cart.js`, створюючи race conditions та перевантаження мережі.

### Рішення Sugar (`window.SugarCart`):
1. **In-Flight Deduplication & 1500ms Cache**:
   ```javascript
   // Один спільний кеш для всіх віджетів
   const MAX_AGE_MS = 1500;
   let cache = null;
   let inflight = null;
   ```
2. **Shopify Line Re-Keying Resolution (`resolveKey`)**:
   Коли до кошика застосовується автоматична знижка, Shopify перераховує `key` рядка (наприклад, `123456:hash1` $\to$ `123456:hash2`). Якщо фронтенд намагається змінити кількість за старим ключем — API повертає HTTP 400 (`no valid id or line parameter`).
   `SugarCart.resolveKey(key)` знаходить відповідний рядок за `lineIdentity(variant_id + properties + selling_plan)` у свіжому кеші.
3. **Нормалізація знижок (`normalize`)**:
   Мутації `/cart/change` повертають знижки вкладеними (`entry.discount_application`), а `/cart.js` — плоскими. Sugar приводить їх до єдиного формату.

---

## 2. 📌 Sticky Product Web Component (`sticky-product.js@2.3.6`)

### Анатомія та інваріанти:
1. **Чистий Web Component**:
   Клас `StickyProduct extends HTMLElement`, реєстрація без зовнішніх бібліотек.
2. **IntersectionObserver прив'язка**:
   Відстежує появу/зникнення головної кнопки `product-form [type="submit"]` у в'юпорті. Спливаючий бар показується лише тоді, коли основна кнопка скролиться вгору (`visibility: after_button`).
3. **Двостороння синхронізація з Offers Block**:
   ```javascript
   // Запобігання нескінченним циклам оновлення кількості
   this.isUpdatingQuantity = false;
   ```
   Якщо покупець обрав 3 одиниці товару в головній формі (Tiered Discount), Sticky Bar автоматично підхоплює кількість, ціну та Selling Plan (підписку), не ламаючи вибір.
4. **Skip Cart / Direct Checkout**:
   Підтримка прямих редіректів на `/checkout` за атрибутом `data-skip-cart="true"`.

---

## 3. ⚡ Zero-Bloat DOM-Demand Loader (`vendor-runtime-loader.js@2.0.0`)

### Проривний підхід до LCP та TBT:
1. **DOM-Demand Execution**:
   Скрипти Splide (слайдери) та Alpine.js завантажуються виключно за умови, якщо в поточному DOM знайдено відповідні селектори (`.splide`, `[x-data]`). Сторінки без слайдерів не завантажують жодного байту бібліотеки.
2. **Inert Scripts (`type="sugar/later"`)**:
   ```html
   <script type="sugar/later" data-src="{{ 'sugar-pricing.js' | asset_url }}"></script>
   ```
   Другорядні скрипти (пошукові підказки, калькулятор доставки) активуються тільки після завершення первинного рендерингу або за першим تاпом/скролом користувача (`pointerdown`, `keydown`, `scroll`).
3. **MutationObserver реактивність**:
   Автоматично виявляє нові блоки, додані через Shopify Theme Editor або Section Rendering API, і домаунчує потрібні рантайми на льоту.

---

## 4. 📝 Handshake Форми та Кошика (`product-form.js@2.2.0`)

### Механізм гарантованого апгрейду:
1. **`getUpgradedCart()`**:
   ```javascript
   await Promise.race([
     customElements.whenDefined('sugar-cart-drawer'),
     new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 2000))
   ]);
   customElements.upgrade(cartElement);
   ```
   Гарантує, що клік на Buy Button не викличе звичайний reload сторінки, якщо скрипт кошика завантажився на мілісекунду пізніше.
2. **Pre-submit валідація додаткових полів (`cartExtras.validate`)**:
   Обов'язкові кастомні поля (гравіювання, розмір) валідуються перед відправкою до AJAX `/cart/add.js`.

---

## 5. 🎯 Контракт екстракції для `Apex CRO Theme` (downstream `node_t1_dual_ready_blocks`)

Ці 4 інженерні рішення кристалізуються як обов'язкові специфікації для **Denchik**:

| Компонент Sugar | Цільовий блок Apex CRO | Інваріант реалізації в DNK OS |
| :--- | :--- | :--- |
| `SugarCart` cache | `services/dnk_shopify/DNK_Sovereign_Apex/assets/dnk-cart-bus.js` | Zero-dependency ES6 модуль, 1500ms кеш, обробка `cart:updated`. |
| `StickyProduct` | `services/dnk_shopify/DNK_Sovereign_Apex/blocks/sticky_atc_bar.liquid` | Tinker 4.2.0 Theme Block 2.0, Web Component `<dnk-sticky-atc>`, IntersectionObserver. |
| Tier Offers sync | `services/dnk_shopify/DNK_Sovereign_Apex/blocks/tiered_discount_table.liquid` | Таблиця знижок із динамічним оновленням через cart-bus, синхронізація кількості. |
| Runtime Loader | `services/dnk_shopify/DNK_Sovereign_Apex/snippets/dnk-runtime-loader.liquid` | Відкладене завантаження `type="dnk/later"`, 0 CLS, 0 TBT блокування. |

---

> **Статус**: Аудит затверджено. Готово до кристалізації в ноду `node_t3_sugar_theme_audit` та передачі в `node_t1_dual_ready_blocks`.
