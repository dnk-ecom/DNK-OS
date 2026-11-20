---
title: "Керівництво та Архітектурний Блупрінт: Розробка Agent-First Shopify Теми на Базі Skeleton Theme та Theme Blocks 2.0"
description: "Comprehensive engineering blueprint for pioneering an Agent-First, Theme Blocks 2.0 theme from scratch based on Shopify/skeleton-theme, integrating battle-tested conversion mechanics from DNK_Ecom_v1_0_0 and reverse-engineered injection patterns from Section Store and Design Packs."
mrh_id: "docs/architecture/blueprints/AGENTIC_THEME_BLOCKS_V2_AND_SKELETON_BLUEPRINT.md"
aliases:
  - "AGENTIC_THEME_BLOCKS_V2_AND_SKELETON_BLUEPRINT"
  - "Agent-First Theme Blueprint"
  - "Shopify Canvas Theme Architecture"
tags:
  - dnk-os
  - architecture
  - shopify
  - skeleton-theme
  - theme-blocks-v2
  - conversion-rate-optimization
  - dnk-ecom
created: 2026-10-09
updated: 2026-10-09
status: active
type: blueprint
archetype: DEV_GUIDE
domain: shopify
author: "DNK-e.com Maksym (Founder), Antigravity (Architect) & Gerych Prime (Builder)"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/blueprints/AGENTIC_THEME_BLOCKS_V2_AND_SKELETON_BLUEPRINT.md"
> purpose: "Comprehensive engineering blueprint for pioneering an Agent-First, Theme Blocks 2.0 theme from scratch based on Shopify/skeleton-theme, integrating battle-tested conversion mechanics from DNK_Ecom_v1_0_0 and reverse-engineered injection patterns from Section Store and Design Packs."
> canonical_source: true
> alters_files: []
> triggers_tasks: ["TASK-SHOPIFY-AGENTIC-THEME-002"]
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-10-09"
> author: "DNK-e.com Maksym, Antigravity & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🚀 Архітектурний Блупрінт: Створення Agent-First Теми Нового Покоління (Shopify Canvas & Theme Blocks 2.0)

На світовому ринку Shopify станом на жовтень 2026 року **практично відсутні комерційні теми**, розроблені за новітньою офіційною специфікацією `Shopify/skeleton-theme` (Agent-First Block Composition). Традиційні розробники залишаються заручниками застарілих JSON-шаблонів Sections 2.0 (стандарт 2022 року).

Даний документ фіксує повну стратегію та покроковий інженерний план створення власної теми та бібліотеки блоків DNK OS, що стане основою для нашої автономної студії **Shopify Canvas**.

---

## 🏛️ 1. Порівняльний Аналіз Трьох Архітектурних Поколінь

| Параметр | Покоління 1: Sections 2.0 (`DNK_Ecom_v1_0_0`) | Покоління 2: Theme Blocks 2.0 (`Tinker`) | Покоління 3: Agent-First (`Shopify/skeleton-theme`) |
| :--- | :--- | :--- | :--- |
| **Базова одиниця побудови** | Секція (`sections/*.liquid`) | Секція + Вкладені Блоки (`blocks/*.liquid`) | **Блок (`blocks/*.liquid`) без секцій** |
| **Шаблони сторінок** | Важкі JSON-файли (`templates/*.json`) | Важкі JSON-файли (`templates/*.json`) | **Чистий Liquid (`templates/*.liquid`) як Composition Root** |
| **Наявність папки `sections/`** | Так (105+ файлів) | Так (обов'язкові обгортки) | **НІ (папка `sections/` повністю ліквідована)** |
| **Теги рендерингу** | `{% section %}`, `{% render %}` | `{% content_for 'blocks' %}` | **`{% block 'name' %}`, `{% partial 'name' %}`** |
| **Динамічне оновлення сторінки** | Повний Ajax запит секції (`?section_id=...`) | Section Rendering API | **Частковий рендеринг `@shopify/partial-rendering`** |
| **Готовність до ШІ-агентів** | Низька (ризик поламати складний JSON) | Середня (велика кількість зв'язків) | **Максимальна (лінійний Liquid + LiquidDoc `{% doc %}`)** |
| **Сумісність із Shopify Canvas** | Обмежена секціями | Базова | **Рідна (Native Canvas & Agentic Editor)** |

---

## 🔬 2. Уроки Реверс-Інжинірингу: Section Store vs Design Packs

Аналіз фізично викачаних тем на магазині `test01010126` дав чітку картину того, як провідні гравці ринку інжектують свої компоненти:

### 2.1. Section Store (SS) — Стратегія "Автономного Острова"
* **Фізичні файли**: додає самодостатні секції `sections/ss-*.liquid` (наприклад, `ss-faq-pro`, `ss-feature-54`, `ss-scrolling-features`).
* **Шаблон воронки**: створює кастомний `templates/product.500-in-1-retro-games-pixboy.json`, у якому секції вибудовані в готову конверсійну послідовність.
* **Перевага**: повна ізоляція. Не змінює `templates/index.json` та `settings_data.json`, унеможливлюючи конфлікти в існуючих сторінках магазину.
* **Недолік**: відсутність глобальної дизайн-системи; кожна секція несе свої власні CSS змінні.

### 2.2. Design Packs (DP) — Стратегія "Theme Blocks Дизайн-Системи"
* **Фізичні файли**: додає 9 блоків `blocks/_dpb_-_styleguide-*.liquid` та 1 керівну секцію `sections/design_pack_-_design_system.liquid`.
* **Інвазія в тему**: модифікує `templates/index.json` (реєструє секцію та прив'язує всі 9 блоків у `block_order`), а також додає токени в `config/settings_data.json`.
* **Перевага**: використання офіційного механізму Theme Blocks та єдиного центру керування токенами (кольори, типографіка, радіуси кнопок).
* **Недолік**: при видаленні додатка в коді теми залишаються пошкоджені посилання на неіснуючі секції.

### 💡 Синтез для теми DNK OS:
1. **Токени**: централізований блок дизайн-системи `blocks/design-system.liquid` за прикладом DP, що передає CSS Custom Properties на рівень `:root`.
2. **Шаблони**: автоматична генерація конверсійних пресетів сторінок (Landing Bundles) за прикладом SS.
3. **Безпека**: нульова деструктивна мутація базових файлів мерчанта.

---

## 📦 3. Інвентаризація та План Міграції Доробку `DNK_Ecom_v1_0_0`

У `DNK_Ecom_v1_0_0` реалізовано одну з найбагатших бібліотек e-commerce конверсії. Нижче наведено розбиття на функціональні кластери та правила їх трансформації в нову архітектуру:

### 3.1. Кластер Cart Drawer & AOV Boosters
* **Старий стан**: 12 розрізнених файлів (`cart-drawer.liquid`, `cart-checkpoints-bar.liquid`, `cart-progress-bar.liquid`, `cart-fomo-block.liquid`, `cart-gift.liquid`, `estimated-shipping-cart-block.liquid`, `upsell-block.liquid`, `moneybackcheckcart.liquid`).
* **Нова архітектура**:
  - `blocks/cart-drawer.liquid` — базовий контейнер висувного кошика зі слотами для блоків.
  - `blocks/cart-progress.liquid` — прогрес-бар безкоштовної доставки з налаштуванням кількох порогів (Checkpoints).
  - `blocks/cart-timer.liquid` — FOMO таймер утримання броні кошика.
  - `blocks/cart-gift.liquid` — картка розблокованого безкоштовного подарунка.
  - `blocks/cart-upsells.liquid` — смарт-рекомендації (Cross-sell / Upsell) з можливістю додавання в 1 клік.
* **Partial Rendering**:
  ```liquid
  {% partial 'cart-items' %}
    {% for item in cart.items %}
      {% block 'cart-item', line_item: item %}{% endblock %}
    {% endfor %}
  {% endpartial %}
  ```
  При зміні кількості товару оновлюється лише контейнер `cart-items` та `cart-progress`, без жодного перезавантаження сторінки.

### 3.2. Кластер Product CRO (Картка Товару & Воронка)
* **Старий стан**: секції `bundle-deals.liquid`, `product-features.liquid`, `countdown-timer-bar.liquid`, `dnk-shipping-countdown-estimator.liquid`.
* **Нова архітектура**:
  - `blocks/product-bundle-tiers.liquid` — таблиця кількості "Купи більше — плати менше" (Tiered Pricing).
  - `blocks/shipping-estimator.liquid` — динамічний лічильник відправки замовлення ("Замовте протягом 1 год 45 хв і ми відправимо сьогодні").
  - `blocks/scarcity-badge.liquid` — динамічний індикатор залишків на складі ("Лишилося 3 шт").
  - `blocks/sticky-atc.liquid` — плаваюча панель додавання в кошик при скролі.

### 3.3. Кластер Social Proof & Довіра
* **Старий стан**: `facebook-reviews.liquid`, `trustpilot-reviews.liquid`, `trustpilot-reviews-2.liquid`, `image-with-reviews.liquid`, `comparison-slider.liquid`, `comparison-table.liquid`.
* **Нова архітектура**:
  - `blocks/review-card.liquid` — атомарний відгук із зірками та бейджем верифікації.
  - `blocks/comparison-table.liquid` — інтерактивна таблиця порівняння "Наш продукт проти звичайних аналогів".
  - `blocks/before-after-slider.liquid` — інтерактивний повзунок До/Після.

---

## 🛠️ 4. Технічний Стандарт Розробки Agent-First Блоків

Кожен компонент нової теми будується за непорушними правилами Shopify Skeleton:

### 4.1. Анатомія Файлу Блоку (`blocks/my-block.liquid`)
1. **Блок документації LiquidDoc (`{% doc %}`)**:
   ```liquid
   {% doc %}
     @name dnk-bundle-deals
     @description Блок пропозиції багаторівневих знижок для збільшення AOV
     @param {string} [title="Спеціальна пропозиція"] - Заголовок блоку
     @param {number} [discount_tier_1=10] - Знижка на 2 товари (%)
     @param {number} [discount_tier_2=20] - Знижка на 3 товари (%)
     @param {string} [content] - Додатковий текстовий опис
   {% enddoc %}
   ```
2. **Розмітка з атрибутами Shopify Canvas**:
   ```liquid
   <div class="dnk-bundle" {{ block.shopify_attributes }}>
     <h3 class="dnk-bundle__title">{{ block.settings.title | default: title }}</h3>
     <div class="dnk-bundle__tiers">
       <button type="button" class="dnk-bundle__tier" data-tier="1">Купи 2 (-{{ discount_tier_1 }}%)</button>
       <button type="button" class="dnk-bundle__tier" data-tier="2">Купи 3 (-{{ discount_tier_2 }}%)</button>
     </div>
     {% if content != blank %}
       <div class="dnk-bundle__content">{{ content }}</div>
     {% endif %}
   </div>
   ```
3. **Схема блоку (`{% schema %}`)**:
   ```liquid
   {% schema %}
   {
     "name": "DNK Bundle Deals",
     "settings": [
       { "type": "text", "id": "title", "label": "Заголовок", "default": "Спеціальна пропозиція" },
       { "type": "number", "id": "discount_tier_1", "label": "Знижка на 2 товари (%)", "default": 10 },
       { "type": "number", "id": "discount_tier_2", "label": "Знижка на 3 товари (%)", "default": 20 }
     ]
   }
   {% endschema %}
   ```

### 4.2. Непорушні Правила (Non-Negotiables)
- **Ніяких `presets` у схемі блоків**: пресети не дозволені у схемі Theme Blocks v2.
- **Ніяких `{% stylesheet %}` та `{% javascript %}`**: заборонено вставляти теги стилів чи скриптів всередину Liquid. Усі стилі — у `assets/critical.css` або `assets/base.css`, скрипти — у модульних JS-файлах `assets/*.js`.
- **Всі тексти через переклади**: використання `{{ 'general.cart.checkout' | t }}` для підтримки багатомовності.
- **Шляхи лише через `routes.*`**: ніяких жорстко захардкодcolumnжених посилань `/cart` чи `/checkout`.

---

## 🎯 5. Покроковий План Запуску Роботи з Нуля

```
КРОК 1: Ініціалізація Репозиторію
  ├── Копіювання чистої бази з skeleton-theme у цільовий робочий проєкт DNK Theme
  └── Налаштування .theme-check.yml (100% відповідність Shopify стандартам)

КРОК 2: Створення Токенів Дизайн-Системи
  ├── Розробка assets/base.css із підтримкою Dark/Light тем та палітри DNK OS
  └── Створення блоку blocks/design-system.liquid

КРОК 3: Портування Конверсійного Cart Drawer
  ├── Перенесення логіки з DNK_Ecom_v1_0_0 у blocks/cart-drawer.liquid
  ├── Реалізація шкал прогресу та подарунків через {% partial %}
  └── Підключення assets/cart-drawer.js через @shopify/partial-rendering

КРОК 4: Портування Набору CRO Блоків Картки Товару
  ├── Блоки бандлів (product-bundle-tier)
  ├── Блок терміновості (shipping-countdown)
  ├── Блок дефіциту (inventory-scarcity)
  └── Плаваючий бар покупки (sticky-atc)

КРОК 5: Створення Шаблонів-Воронок (Landing Presets)
  └── Складання templates/product.landing.liquid із контейнерів та блоків
```
