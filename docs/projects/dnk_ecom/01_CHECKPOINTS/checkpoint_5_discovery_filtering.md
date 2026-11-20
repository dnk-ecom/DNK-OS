---
title: "Checkpoint 5: Catalog Discovery, Section Rendering Facets & Quick View"
description: "Живий лог та специфікація Checkpoint 5: Сітка каталогу, Section Rendering API фільтрація та картка товару."
mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_5_discovery_filtering.md"
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
> mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_5_discovery_filtering.md"
> purpose: "Живий лог та специфікація Checkpoint 5: Сітка каталогу, Section Rendering API фільтрація та картка товару."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔍 Checkpoint 5: Catalog Discovery, Section Rendering Facets & Quick View

## 1. Контекст та Мета
* **Ціль**: Побудувати надшвидку систему навігації та фільтрації товарного каталогу без перезавантаження сторінки через офіційний Shopify Section Rendering API. Реалізувати високоефективну картку товару з ефектом вторинного зображення та 1-click Quick Add.
* **Цільові файли в гілці `mvp`**:
  - `assets/dnk-facets.js` — W3C Custom Element `<dnk-facets>` для безшовного AJAX-оновлення сітки каталогу та синхронізації адресного рядка через `history.pushState`.
  - `sections/main-collection.liquid` — координаційна секція каталогу з бічною панеллю фільтрів (ціновий діапазон, чекбокси наявності/кольору/розміру) та пагінацією.
  - `sections/featured-collection.liquid` — гнучка секція рекомендованих товарів для головної сторінки з налаштуванням ліміту та перегляду всіх товарів.
  - `snippets/product-card.liquid` — 0-CLS картка товару зі secondary hover image та інтеграцією з `CartMutationQueue`.

## 2. Аналіз Донорів: Що було не так
* **Dawn 15.0**: Фільтри Dawn реалізовані через громіздкий `facets.js`, який надмірно маніпулює DOM-деревом і часто ламає фокус клавіатури під час пагінації.
* **Tinker (Horizon)**: Відмінна чиста структура, але відсутній 1-click Quick Add на картці товару, що знижує конверсію в імпульсивних нішах (beauty, accessories, fashion).

## 3. Суверенне Рішення DNK (Чому саме так)
* **Нативний Section Rendering API (`dnk-facets.js`)**:
  - Запит формується як `GET /collections/{handle}?{params}&sections=main-collection`.
  - Оновлюються виключно вузли `#DnkProductGrid` та стан фільтрів, без перерендерингу хедера чи футера.
* **0-CLS та Мобільна Ергономіка**:
  - Картка товару має суворе співвідношення сторін `aspect-ratio: 1 / 1` та скелетонний стан завантаження.
  - Кнопка швидкого додавання `Quick Add` з'являється при наведенні на десктопі та доступна без відкриття сторінки товару.
* **Синхронізація Історії Браузера**:
  - Повна підтримка кнопок "Назад" та "Вперед" у браузері через подію `window.addEventListener('popstate')`.

## 4. Машинний Доказ (Machine Proof)
```bash
$ just shopify-checkpoint 5
Gate Checkpoint 5: Collection Grid, Section Rendering Facets & Quick View -> ✅ PASSED
  ✓ File: sections/main-collection.liquid: Found mandatory file: sections/main-collection.liquid
  ✓ Collection grid and card components: Discovery grid and product card components verified

$ python3 -c "from services.dnk_shopify.tools.theme_ast_validator import validate_theme_file; ..."
Total liquid files: 20, All clean? True

$ git -C ../DNKEcom/DNK-Ecom_git_mirrow/mvp log -1 --oneline
e015319 feat(catalog): complete Checkpoint 5 - Collection Grid, Section Rendering Facets & Quick View
```
* **Статус воріт**: `✅ PASSED` (Коміт: `e015319`).