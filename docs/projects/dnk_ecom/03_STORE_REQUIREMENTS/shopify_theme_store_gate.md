---
title: "Критерії 100% Проходження Модерації Shopify Theme Store"
description: "Суворий перевірочний список усіх вимог модерації Shopify Theme Store."
mrh_id: "docs/projects/dnk_ecom/03_STORE_REQUIREMENTS/shopify_theme_store_gate.md"
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
> mrh_id: "docs/projects/dnk_ecom/03_STORE_REQUIREMENTS/shopify_theme_store_gate.md"
> purpose: "Суворий перевірочний список усіх вимог модерації Shopify Theme Store."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏆 Критерії 100% Проходження Модерації Shopify Theme Store

## 1. Продуктивність (Performance & Speed)
- [x] **Zero Third-Party JS Frameworks**: Жодного jQuery, React, Lodash, Alpine.js у коді теми. Тільки чисті W3C Custom Elements.
- [ ] **Lighthouse Mobile Score $\ge 90$**: Тестування сторінок index, collection, product на мобільному емуляторі.
- [ ] **Lighthouse Desktop Score $\ge 98$**.
- [x] **CLS (Cumulative Layout Shift) $\le 0.05$**: Всі зображення та відеоплеєри мають жорсткий CSS `aspect-ratio` до завантаження файлу.
- [x] **Критичні CSS-токени в Head**: `dnk-tokens.css` завантажується інлайново або з `preload: true`.

---

## 2. Доступність (Accessibility & WCAG 2.2 AA)
- [x] **Skip to Content Link**: Перший фокусний елемент у DOM (`<a class="dnk-skip-link" href="#MainContent">`).
- [ ] **Контраст Кольорів**: Текст до фону $\ge 4.5:1$, елементи UI та кнопки $\ge 3.0:1$.
- [ ] **Повна Клавіатурна Навігація**: Доступ до всіх пунктів меню, кошика та модальних вікон через `Tab` / `Shift+Tab`.
- [ ] **Focus Traps**: Модальні вікна (Cart Drawer, Quick View, Mobile Menu) блокують фокус усередині та закриваються на `Escape`.
- [ ] **Семантичні ARIA-атрибути**: `aria-expanded`, `aria-controls`, `aria-label` для всіх інтерактивних кнопок без тексту.

---

## 3. Архітектура та Стандарти Коду (Code Integrity)
- [x] **100% Theme Blocks 2.0**: Блоки знаходяться у папці `blocks/`, імена схем $\le 25$ символів.
- [x] **Заборона застарілих тегів**: Жодних `{% stylesheet %}` та `{% javascript %}` всередині секцій чи блоків (вони блокують кешування та CSSOM).
- [ ] **100% Локалізація (i18n)**: Жодного захардкодженого англійського чи українського слова в Liquid-шаблонах. Усі рядки прописані через `{{ 'general.xxx' | t }}` у `locales/en.default.json`.
- [ ] **7 Клієнтських Шаблонів**: Повна наявність валідних JSON-шаблонів `templates/customers/*.json`.
- [ ] **Розмір Шаблонів**: Жоден файл у `templates/*.json` не перевищує ліміт 512 КБ.
- [ ] **Zero Console Errors**: Відсутність будь-яких помилок чи unhandled rejection у консолі браузера.

---

## 4. Конверсійні Елементи без "Податку на Додатки" (No-App CRO)
- [ ] **AJAX Cart Drawer**: Оновлення без перезавантаження сторінки через Section Rendering API.
- [ ] **Dynamic Free Shipping Progress**: Багаторівневий розрахунок залишкової суми до безкоштовної доставки.
- [ ] **Visual Category Swatches**: Нативні свотчі кольорів та патернів через Category Metafields (без додатків).
- [ ] **Sticky Add to Cart**: Липка смужка покупки на мобільних пристроях.
- [ ] **Quantity Breaks / Volume Pricing**: Вбудована прогресивна знижка від кількості.
