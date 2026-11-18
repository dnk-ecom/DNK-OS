---
title: "Контрактна Специфікація Компонентів та Шини Даних MVP v0.1.0"
description: "Точна контрактна специфікація подій, селекторів, Section Rendering API та мапінгу 32 файлів MVP."
mrh_id: "docs/projects/dnk_ecom/00_MVP_V010_COMPONENT_CONTRACTS.md"
status: approved
type: component_contracts
domain: shopify_theme_architecture
author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
version: "1.0.0"
date: 2026-11-18
---

> [!metadata]- ⚙️ Системні метадані (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/projects/dnk_ecom/00_MVP_V010_COMPONENT_CONTRACTS.md"
> purpose: "Точна контрактна специфікація подій, селекторів, Section Rendering API та мапінгу 32 файлів MVP."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Approved"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📐 Контрактна Специфікація Компонентів та Шини Даних MVP v0.1.0

---

## ⚡ 1. Словник Подій Глобальної Шини (`window.DNK.events`)

Усі компоненти взаємодіють виключно через типізовані події. Прямий доступ до внутрішнього DOM іншого компонента суворо заборонений:

| Подія (Event Name) | Payload (detail) | Емітер (Хто генерує) | Слухач (Хто реагує) |
|---|---|---|---|
| `dnk:cart:loading` | `{ isBusy: boolean }` | `CartMutationQueue` | `<dnk-cart-drawer>`, кнопки ATC (`[data-dnk-loading]`) |
| `dnk:cart:updated` | `{ cart: Object }` | `CartMutationQueue` | `<dnk-cart-drawer>`, `<dnk-cart-icon>`, прогрес-бар доставки |
| `dnk:cart:error` | `{ error: Error }` | `CartMutationQueue` | `<dnk-toast>`, форми товарів |
| `dnk:drawer:open` | `{ target: 'cart' \| 'menu' }` | Кнопки хедера, ATC | `<dnk-cart-drawer>`, `<dnk-mobile-menu>` |
| `dnk:drawer:close` | `{ target: string }` | Хрестик, Overlay, `Esc` | Активні дровери та модальні вікна |
| `dnk:variant:changed` | `{ variant: Object }` | `<dnk-variant-picker>` | Галерея медіа, ціна, Sticky ATC, бейдж наявності |

---

## 🌐 2. Контракт Section Rendering API

Для оновлення інтерфейсу без перезавантаження сторінки використовуються чисті запити до нативного Shopify Section Rendering API:

### 2.1. Додавання товару та оновлення кошика:
* **Запит**: `POST /cart/add.js` із тілом `{ items: [...], sections: ["cart-drawer", "cart-icon-bubble"] }`
* **Відповідь Shopify**: JSON із полем `sections: { "cart-drawer": "<html>...", "cart-icon-bubble": "<span>..." }`
* **Дія в JS**:
  1. `document.getElementById('DnkCartDrawerBody').innerHTML = sections['cart-drawer']`
  2. `document.getElementById('DnkCartCount').innerHTML = sections['cart-icon-bubble']`
  3. `window.DNK.events.emit('dnk:drawer:open', { target: 'cart' })`

### 2.2. Фільтрація каталогу товарів:
* **Запит**: `GET /collections/{handle}?filter.v.price.gte=100&sections=main-collection`
* **Дія в JS**: Оновлюється тільки DOM-вузол `#DnkProductGrid`, URL синхронізується через `history.pushState`.

---

## 🏷️ 3. Стандарт Data-Атрибутів та Селекторів

| Data-Атрибут | Призначення | Приклад Елемента |
|---|---|---|
| `data-action="add-to-cart"` | Тригер додавання товару | Кнопка покупки в картці або на PDP |
| `data-variant-id="123456"` | ID активного варіанта | Кнопка ATC, радіо-кнопка свотча |
| `data-drawer-trigger="cart"` | Відкриття висувного кошика | Іконка кошика в хедері |
| `data-drawer-trigger="menu"` | Відкриття мобільного меню | Кнопка-гамбургер у хедері |
| `data-dnk-loading="true"` | Блокування інтерфейсу від спам-кліків | Кнопки покупки, форми кошика |
| `data-theme="dark"` | Примусове перемикання кольорової схеми | Оболонка сайту `<html>` або окрема секція |

---

## 🗺️ 4. Мапінг 32 Файлів MVP v0.1.0 на Референсних Донорів

| # | Файл у `mvp/` | Тип | Референс Донора | Ключова Дистильована Механіка |
|---|---|---|---|---|
| 1 | `layout/theme.liquid` | Layout | **Shopify Skeleton** | Мінімалістичний чистий scaffold, skip-link |
| 2 | `config/settings_schema.json` | Config | **Tinker / Horizon** | Кольори, гарнітури, брендинг без перевантаження |
| 3 | `config/settings_data.json` | Config | **DNK Sovereign** | Пресет "Minimal Luxury" за замовчуванням |
| 4 | `locales/en.default.json` | Locale | **Tinker / Shrine** | 100% англійська мова для проходження Store |
| 5 | `locales/uk.json` | Locale | **DNK Sovereign** | 100% українська мова для клієнтських запусків |
| 6 | `assets/dnk-tokens.css` | Asset | **DNK Core** | W3C Design Tokens, Polaris Emerald / Obsidian |
| 7 | `assets/dnk-base.css` | Asset | **DNK Core** | CSSOM Reset, 12-col Subgrid, a11y focus rings |
| 8 | `assets/dnk-core.js` | Asset | **Sugar / Story** | `DnkElement`, `CartMutationQueue`, Cleanroom Fetch |
| 9 | `assets/dnk-cart-drawer.css` | Asset | **Shrine Pro** | Анімації висування дровера, градієнти прогрес-бару |
| 10 | `assets/dnk-cart-drawer.js` | Asset | **Shrine / Story** | Custom element `<dnk-cart-drawer>` |
| 11 | `assets/dnk-facets.js` | Asset | **Tinker** | Section Rendering API фільтрація каталогу |
| 12 | `assets/dnk-pdp.js` | Asset | **Story / Maestrooo** | Перемикання свотчів, 0-CLS галерея, Sticky ATC |
| 13 | `sections/header.liquid` | Section | **Tinker** | Липкий хедер на Theme Blocks (`_header-logo`, `_menu`) |
| 14 | `sections/footer.liquid` | Section | **Tinker** | Модульний футер із розсилкою та селектором валют |
| 15 | `sections/cart-drawer.liquid` | Section | **Shrine Pro** | AJAX Cart Drawer, багаторівневий прогрес-бар |
| 16 | `sections/main-product.liquid` | Section | **Tinker** | Холст PDP 2.0 під Theme Blocks (`content_for 'blocks'`) |
| 17 | `sections/main-collection.liquid` | Section | **Tinker** | Сітка каталогу з фільтрами та пагінацією |
| 18 | `sections/hero-banner.liquid` | Section | **Tinker / Story** | Hero-банер із блоками заголовка, кнопок і бейджів |
| 19 | `sections/featured-collection.liquid` | Section | **Tinker** | Карусель/сітка популярних товарів |
| 20 | `blocks/_group.liquid` | Block | **Tinker** | Рекурсивний контейнер Auto-Layout (до 8 рівнів) |
| 21 | `blocks/_header-logo.liquid` | Block | **Tinker** | Адаптивне лого з авто-розміром |
| 22 | `blocks/_header-menu.liquid` | Block | **Tinker / Story** | Десктопний dropdown + мобільний drawer |
| 23 | `blocks/product_media-gallery.liquid` | Block | **Story / Maestrooo** | Touch-swipe галерея з фіксованим aspect-ratio |
| 24 | `blocks/product_variant-picker.liquid` | Block | **Tinker** | Category Metafields Visual Swatches (0 apps) |
| 25 | `blocks/product_buy-buttons.liquid` | Block | **Sugar** | Кнопки покупки з Cleanroom Attribution Fetch |
| 26 | `blocks/product_sticky-atc.liquid` | Block | **Shrine Pro** | Липка смужка покупки для мобільних пристроїв |
| 27 | `blocks/product_quantity-breaks.liquid` | Block | **Shrine / Casaio** | Таблиця знижок від кількості (Volume Pricing) |
| 28 | `blocks/cart_shipping-bar.liquid` | Block | **Shrine Pro** | Динамічний прогрес безкоштовної доставки |
| 29 | `blocks/cart_upsell-item.liquid` | Block | **Shrine Pro** | 1-click крос-сейл товар безпосередньо в дровері |
| 30 | `snippets/product-card.liquid` | Snippet | **Story** | Картка товару з вторинним медіа при наведенні |
| 31 | `snippets/price.liquid` | Snippet | **Tinker** | Форматування ціни, знижок та ціни за одиницю |
| 32 | `snippets/icon.liquid` | Snippet | **Shopify Skeleton** | Універсальний інлайн-рендерер чистих SVG іконок |

---

## 🎯 5. Правило Оракула: Що вважається "Done"

Будь-який із 32 файлів вважається фізично завершеним, коли:
1. Його синтаксис валідується через `theme_ast_validator.py` та `node -c` (для JS).
2. Його створення переводить відповідні ворота `just shopify-checkpoint <id>` у стан `✅ PASSED`.
3. Коміт зафіксовано в гілці `mvp` з чітким префіксом `feat(...)`.
