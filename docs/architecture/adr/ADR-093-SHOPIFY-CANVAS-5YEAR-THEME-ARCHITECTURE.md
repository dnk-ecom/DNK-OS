---
title: "ADR-093: 5-Year Shopify Theme Architecture Standard (2026–2031) — Horizon / Theme Blocks 2.0 & Shopify Canvas"
description: "5-Year Shopify Theme Architecture Standard (2026-2031) for Shopify Canvas, AI Sidekick & Horizon Theme Blocks 2.0."
mrh_id: "docs/architecture/adr/ADR-093-SHOPIFY-CANVAS-5YEAR-THEME-ARCHITECTURE.md"
status: Active
archetype: ADR
version: "2.0.0"
updated: 2026-11-18
tags:
  - adr
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/adr/ADR-093-SHOPIFY-CANVAS-5YEAR-THEME-ARCHITECTURE.md"
> purpose: "5-Year Shopify Theme Architecture Standard (2026-2031) for Shopify Canvas, AI Sidekick & Horizon Theme Blocks 2.0."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ ADR-093: 5-Year Shopify Theme Architecture Standard (2026–2031) — Horizon / Theme Blocks 2.0 & Shopify Canvas

## 1. Контекст, Проблематика та Вердикт (Context, Problem & Executive Summary)

На горизонті **5 років (2026–2031)** безальтернативним стандартом для клієнтських магазинів та генератора тем із візуального полотна DNK Hub є **чиста архітектура Horizon / Theme Blocks 2.0** (100% Block-First з атомарними примітивами в `blocks/` та рекурсивними контейнерами `_group.liquid`), посилена нативними **Web Components (Custom Elements)** та **CSS Grid / Subgrid**.

Класичні монолітні OS 2.0 теми (на базі Dawn) та гібридні преміум-теми перетворяться на критичний технічний борг протягом 18–24 місяців через несумісність із **Shopify Canvas** та **AI Sidekick**.

---

## 2. Чому саме Horizon (Theme Blocks 2.0) — прямий фундамент під Shopify Canvas

Візуальний редактор нового покоління (**Shopify Canvas + AI Sidekick**) працює не з пласкими фіксованими секціями, а з деревом компонентів (**AST / DOM Tree**), де кожен вузол на полотні відповідає одному файлу в `blocks/*.liquid`:

1. **Прямий мапінг Canvas Frame ➔ `blocks/_group.liquid`**:
   У Figma / DNK Canvas / Shopify Canvas будь-який Auto-Layout фрейм (рядок, колонка, сітка, картка) напряму серіалізується у вкладений блок `blocks/_group.liquid` із налаштуваннями `direction`, `gap`, `alignment` через `{% content_for 'blocks' %}`.
2. **Генерація блоків через AI Sidekick (`{"type": "@theme"}`)**:
   Вбудований AI-генератор Shopify створює нові блоки на льоту і вставляє їх лише в ті секції та групи, які приймають глобальні `@theme` блоки. У монолітних секціях OS 2.0 AI-генерація та вільний drag-and-drop заблоковані самою схемою.
3. **Статична типізація даних через `liquid_doc` (`{% doc %}`)**:
   Офіційний стандарт Shopify для передачі пропсів у сніпети та блоки (`@param`, `@example`), який дозволяє візуальному полотну (та транспілятору в DNK OS) автоматично будувати UI-контроли без ручного парсингу коду.

---

## 3. Перевірка припущення: 3 критичні приховані ризики Block-First архітектури та їх нейтралізація

Перехід на 100% гнучке блочне полотно несе три інженерні загрози, які жорстко обмежуються архітектурними бар'єрами DNK OS:

### Ризик 1: «DOM-Soup» та деградація Core Web Vitals (INP / LCP)
- **Чому виникає**: Дозвіл вкладати блоки на 8 рівнів углиб (`Section -> Group -> Group -> Grid -> Card -> Group -> Button`) породжує 10–15 зайвих `<div>`-обгорток із inline CSS-змінними на кожен блок. На каталогах із 48 товарами це роздуває DOM понад 3 000 вузлів.
- **Архітектурне рішення**: Жорстке обмеження глибини вкладеності до **3–4 рівнів** та обов'язкове використання **статичних блоків** (`{% content_for 'block', type: '_product-card', id: 'card' %}`) у циклах колекцій замість динамічних списків.

### Ризик 2: Параліч мерчанта в Theme Customizer («Синдром порожнього Figma-листа»)
- **Чому виникає**: Коли секція складається з 40 мікроблоків (окремо відступ, окремо бейдж, окремо заголовок), контент-менеджер випадково ламає мобільну верстку одним перетягуванням.
- **Архітектурне рішення**: **Двошарова модель блоків**:
  - *Atomic Blocks* (`text`, `button`, `image`) — відкриті для Canvas / AI.
  - *Compound Preset Blocks* — складні комерційні вузли запаковані в готові пресети в `schema.presets` із заблокованими критичними токенами відступів.

### Ризик 3: Вибух JSON-шаблонів (`templates/*.json` > 150 KB)
- **Чому виникає**: Глибоко вкладені дерева блоків збільшують розмір JSON-шаблонів у 3–5 разів, що уповільнює парсинг у Customizer та створює конфлікти при git-мерджах.
- **Архітектурне рішення**: Винесення повторюваних патернів у `sections/` або `snippets/` із суворим `{% doc %}` контрактом та автоматична очистка сирітських блоків через `services/dnk_shopify/tools/theme_cleanroom_neutralizer.py`.

---

## 4. Граничні умови (Boundary Conditions — Де Theme Blocks 2.0 ЗАБОРОНЕНО застосовувати)

Навіть через 5 років візуальний Canvas не замінить детерміновану комерційну бізнес-логіку. **Суворо заборонено** розбивати на вільні користувацькі мікроблоки:
1. **Cart Drawer & Ajax Cart Calculation**: кошик, апсейли, пороги безкоштовної доставки — виключно єдиний ізольований Web Component `<cart-drawer>`.
2. **Variant Picker & Combined Listings**: перемикання SKU з високою кількістю комбінацій — має працювати через Section Rendering API як цілісний вузол `<variant-selects>`.
3. **Faceted Search & Filtering**: фільтри колекцій та сортування каталогу.
4. **Checkout**: повністю працює на React-базованих Checkout UI Extensions та Shopify Functions (Liquid і Theme Blocks там не існують).

---

## 5. Порівняння архітектур за 5 векторами на горизонті 5 років (2026–2031)

| Вектор оцінки | Класична OS 2.0 (Dawn / Старі платні) | Гібридна (Prestige v11 / Pipeline v8) | Чиста Horizon + Compound Blocks (Стандарт DNK OS) |
| :--- | :--- | :--- | :--- |
| **1. Сумісність з Shopify Canvas & AI Sidekick** | ❌ Низька (жорсткі пласкі секції) | ⚠️ Часткова (лише в 2–5 спецсекціях) | ✅ **100% нативна** (кожен блок = вузол Canvas) |
| **2. Масштабованість (100x SKU / Мультибренд)** | ⚠️ Дублювання коду між секціями | ⚠️ Важкий JS-бандл (300–500 KB) | ✅ **Висока** (єдиний блок реюзається у всій темі) |
| **3. Підтримуваність (Tech Debt за 5 років)** | ❌ Вимре до 2028 року | ⚠️ Подвійна підтримка старих і нових схем | ✅ **Мінімальний борг** (офіційний курс Shopify) |
| **4. Безпека та валідація схем** | ⚠️ Ручні JSON-помилки | ⚠️ Часті колізії типів блоків | ✅ **Сувора AST-валідація** (`@theme` + приватні `_blocks`) |
| **5. Швидкодія (CWV / LCP / INP)** | ✅ Швидка за рахунок простоти | ❌ Перевантажена легасі-скриптами | ✅ **Надшвидка** (CSS Variables + Native Web Components) |

---

## 6. Еталонний рецепт «Ідеальної Архітектури DNK Theme 2026–2031» (4-Шарова Формула)

Для всіх клієнтських магазинів та генерації тем із візуального Canvas у DNK Hub застосовується 4-шарова формула на базі ядра Horizon v4.3+:

1. **Шар 1 — Базове ядро**:
   Shopify Horizon (`v4.3.0+` / Tinker `4.2.0+`) як фундамент замість Dawn. Жодного jQuery, жодних важких сторонніх фреймворків — тільки нативні Custom Elements (Web Components) та декларативні CSS-змінні.
2. **Шар 2 — Строга ієрархія `blocks/` (Правило 3 рівнів)**:
   - **Публічні атомарні блоки** (`blocks/text.liquid`, `button.liquid`, `image.liquid`, `icon.liquid`): доступні через `{"type": "@theme"}` для вільного комбінування на Canvas та генерації через Shopify Sidekick.
   - **Контейнерні фрейми** (`blocks/_group.liquid`, `blocks/grid.liquid`): відповідають за Flexbox / CSS Grid розкладку (аналог Auto-Layout у Figma).
   - **Приватні бізнес-блоки з префіксом `_`** (`blocks/_product-card.liquid`, `blocks/_buy-buttons.liquid`, `blocks/_price.liquid`): жорстко типізовані комерційні вузли, захищені від випадкового видалення чи поломки верстки.
3. **Шар 3 — Design Tokens через CSS Custom Properties (ADR-008 сумісність)**:
   Секції та групи не плодять монолітні CSS-класи на кожен випадок, а передають CSS-змінні (`--gap`, `--padding-block`, `--color-scheme`) у `style="..."`, що дозволяє миттєво транспілювати будь-який вузол із DNK Visual Canvas прямо в JSON-шаблон Shopify.
4. **Шар 4 — Автоматичний Cleanroom-конвеєр (`dnk_shopify`)**:
   Кожна тема перед релізом або імпортом проходить через `services/dnk_shopify/tools/theme_cleanroom_neutralizer.py` (перевірка дерева `schema.blocks`, fallback-плейсхолдери для `request.design_mode`, очистка `shopify://shop_images/`).

---

## 7. Золоте правило (One-Line Rule)

> **Будувати всі нові проекти виключно на ядрі Horizon (Theme Blocks 2.0) з чітким поділом на вільні атомарні блоки (`@theme`) для дизайну/Canvas та захищені приватні блоки (`_block.liquid`) для e-commerce логіки (PDP/Cart).**
