---
title: "Checkpoint 2: Global Chrome (Layout, Header & Footer)"
description: "Живий лог та специфікація Checkpoint 2: Global Chrome, theme.liquid та блоковий Header."
mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_2_global_chrome.md"
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
> mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_2_global_chrome.md"
> purpose: "Живий лог та специфікація Checkpoint 2: Global Chrome, theme.liquid та блоковий Header."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ Checkpoint 2: Global Chrome (Layout, Header & Footer)

## 1. Контекст та Мета
* **Ціль**: Побудувати доступну глобальну оболонку сайту на базі новітньої блокової архітектури Shopify (Theme Blocks 2.0). Забезпечити бездоганну роботу липкого хедера, адаптивного мобільного меню та семантичного футера.
* **Цільові файли в гілці `mvp`**:
  - `layout/theme.liquid` — головний шаблон (a11y skip-link, підключення токенів та `dnk-core.js`).
  - `sections/header.liquid` — координатор хедера (липкість, W3C Event Bus тригери).
  - `blocks/_header-logo.liquid` — приватний блок логотипа (0-CLS, адаптивне масштабування).
  - `blocks/_header-menu.liquid` — приватний блок меню (десктопний dropdown + мобільний drawer).
  - `sections/footer.liquid` — 4-колонковий семантичний футер із розсилкою, локалізацією та платіжними бейджами.

## 2. Аналіз Донорів: Що було не так
* **Dawn 15.0 / OS 2.0**: Хедер є монолітною секцією на 800+ рядків Liquid із жорстко вшитим логотипом і меню. Неможливо переставити елементи місцями через Customizer або використати AI Sidekick.
* **Tinker (Horizon)**: Відмінна ідея Theme Blocks у хедері (`_header-logo`, `_header-menu`), але перевантажена складними обчисленнями яскравості кольорів на Liquid (`color_brightness` loops), які уповільнюють TTFB (Time to First Byte).

## 3. Суверенне Рішення DNK (Чому саме так)
* **Лейаут (`layout/theme.liquid`)**:
  - Беремо мінімалістичну чистоту офіційного `skeleton-theme`.
  - Підключаємо критичні токени `dnk-tokens.css`, базу `dnk-base.css` та мікроядро `dnk-core.js`.
  - Додаємо обов'язковий доступний skip-link для проходження WCAG AA: `<a class="dnk-skip-link" href="#MainContent">Skip to content</a>`.
* **Блоковий Хедер (`sections/header.liquid`)**:
  - Використовуємо композицію Theme Blocks v2: `content_for 'block', type: '_header-logo'` та `content_for 'block', type: '_header-menu'`.
  - Усі перемикання (липкий хедер, відкриття мобільного меню, відкриття дровера кошика) транслюються через W3C Event Bus `window.DNK.events.emit('dnk:drawer:open', { target: 'cart' })`.
* **Семантичний Футер (`sections/footer.liquid`)**:
  - Чиста 4-колонкова адаптивна сітка (Бренд, Меню, Розсилка, Валюти/Мови).
  - 100% відповідність вимогам Shopify Theme Store щодо селекторів локалізації та відсутності сторонніх бібліотек.

## 4. Машинний Доказ (Machine Proof)
```bash
$ just shopify-checkpoint 2
Gate Checkpoint 2: Global Chrome, Accessible Header & Predictive Search -> ✅ PASSED
  ✓ File: layout/theme.liquid: Found mandatory file: layout/theme.liquid
  ✓ File: sections/header.liquid: Found mandatory file: sections/header.liquid
  ✓ File: sections/footer.liquid: Found mandatory file: sections/footer.liquid
  ✓ Global layout structure and script loading: Global chrome passes layout structure and runtime loading requirements

$ python3 services/dnk_shopify/tools/theme_ast_validator.py
✅ blocks/_header-logo.liquid: errors=0, warnings=0
✅ blocks/_header-menu.liquid: errors=0, warnings=0
✅ sections/header.liquid: errors=0, warnings=0
✅ sections/footer.liquid: errors=0, warnings=0
✅ layout/theme.liquid: errors=0, warnings=0

$ git -C ../DNKEcom/DNK-Ecom_git_mirrow/mvp log -1 --oneline
4e87aab feat(chrome): complete Checkpoint 2 - Global Chrome, Accessible Header & Footer
```
* **Статус воріт**: `✅ PASSED` (Коміт: `4e87aab`).
