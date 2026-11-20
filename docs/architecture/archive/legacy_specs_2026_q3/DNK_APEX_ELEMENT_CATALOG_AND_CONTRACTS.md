---
title: "DNK Apex Element Catalog and Architecture Contracts"
status: active
type: specification
domain: shopify
author: "DNK OS Architecture & Denchik & Antigravity"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_APEX_ELEMENT_CATALOG_AND_CONTRACTS.md"
> purpose: "Exhaustive Technical Catalog, Liquid Contracts, and Theme Blocks 2.0 Topology for Shopify Theme Store Certified Theme (DNK Apex Theme)."
> canonical_source: true
> alters_files: []
> triggers_tasks: ["dnk_shopify_apex_phase_1_kernel", "dnk_shopify_apex_phase_2_blocks"]
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-12"
> author: "DNK-e.com Maksym & Antigravity Orchestrator & Denchik"
> related_decisions: ["DEC-074"]
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ ТЕХНІЧНИЙ КАТАЛОГ ЕЛЕМЕНТІВ ТА КОНТРАКТИ АРХІТЕКТУРИ ТЕМИ DNK APEX

> **Статус:** `[🔒 LOCKED] DEC-074`  
> **Цільовий стандарт:** 100% відповідність вимогам **Shopify Theme Store Requirements** (0 Errors, 0 Warnings, WCAG 2.1 AA, Mobile Lighthouse ≥ 90, нативні Theme Blocks 2.0).

---

## 1. ⚙️ МІКРО-ЯДРО ТА МАКЕТИ (`layout/`)

### 1.1. `layout/theme.liquid` (Micro-Kernel Contract)
* **Призначення:** Базовий мікро-каркас вітрини. Розмір строго $\le 120$ рядків.
* **Порядок вузлів у `<head>`:**
  1. Метатеги: `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`.
  2. Канонічні посилання та SEO: `<link rel="canonical" href="{{ canonical_url }}">`, `{% render 'meta-tags' %}`.
  3. Preconnect до Shopify CDN: `<link rel="preconnect" href="https://cdn.shopify.com" crossorigin>`.
  4. Preload основного системного шрифту через `snippets/font-face.liquid`.
  5. **Інлайнові токени:** `{% render 'css-variables' %}` (нульові блокуючі мережеві запити перед FCP).
  6. Критичний CSS: `{{ 'base.css' | asset_url | stylesheet_tag: preload: true }}`.
  7. Слот платформи: `{{ content_for_header }}` (суворо без фільтрів модифікації).
  8. Модульні скрипти: `<script src="{{ 'global.js' | asset_url }}" defer="defer"></script>`.
* **Порядок вузлів у `<body>`:**
  1. `<a class="skip-to-content-link visually-hidden" href="#MainContent">Skip to content</a>`.
  2. `{% sections 'header-group' %}`.
  3. `<main id="MainContent" class="content-for-layout focus-none" role="main" tabindex="-1">{{ content_for_layout }}</main>`.
  4. `{% sections 'footer-group' %}`.
  5. `{% sections 'overlay-group' %}`: глобальні контейнери `<cart-drawer id="CartDrawer" class="drawer"></cart-drawer>`, `<modal-dialog id="QuickViewModal"></modal-dialog>`.
  6. Глобальний доступний анонсер: `<div id="a11y-status" class="visually-hidden" role="status" aria-live="polite"></div>`.

### 1.2. `layout/password.liquid` & `layout/gift_card.liquid`
* **`password.liquid`:** Автономний макет без завантаження скриптів кошика та рекомендацій. Включає форму введення пароля в доступному `<dialog>` та блок підписки на запуск магазину.
* **`gift_card.liquid`:** Локальний генератор QR-кодів (`assets/vendor-qrcode.js`), кнопка збереження в Apple Wallet (`pass_url`), стилі друку `@media print`.

---

## 2. 🎨 ДИЗАЙН-СИСТЕМА ТА ТОКЕНИ (`snippets/css-variables.liquid`)

### 2.1. Формули математичної інтерполяції `clamp()`
Усі розміри тексту, контейнерів та відступів плавно масштабуються між мобільним екраном ($375\text{px}$) та десктопом ($1440\text{px}$) без дискретних стрибків:

$$\text{Value} = \text{clamp}(V_{\min},\; V_{\text{fluid}},\; V_{\max})$$

```css
:root {
  /* --- 1. Fluid Typography Scale --- */
  --font-size-xs: clamp(0.75rem, 0.7rem + 0.2vw, 0.8125rem);
  --font-size-sm: clamp(0.8125rem, 0.775rem + 0.2vw, 0.875rem);
  --font-size-base: clamp(0.9375rem, 0.875rem + 0.3vw, 1rem);
  --font-size-md: clamp(1.0625rem, 0.975rem + 0.45vw, 1.1875rem);
  --font-size-lg: clamp(1.25rem, 1.125rem + 0.6vw, 1.5rem);
  --font-size-xl: clamp(1.5rem, 1.3rem + 1.0vw, 1.875rem);
  --font-size-h3: clamp(1.25rem, 1.1rem + 0.75vw, 1.625rem);
  --font-size-h2: clamp(1.625rem, 1.35rem + 1.35vw, 2.25rem);
  --font-size-h1: clamp(2.125rem, 1.65rem + 2.4vw, 3.25rem);

  /* --- 2. Fluid Layout & Spacing --- */
  --page-width: {{ settings.page_width | default: 1320 }}px;
  --container-padding: clamp(1rem, 0.5rem + 2vw, 2.5rem);
  --grid-gap: clamp(0.75rem, 0.5rem + 1vw, 1.5rem);
  --section-spacing-y: clamp(2.5rem, 1.5rem + 4vw, 5rem);

  /* --- 3. Fluid Radius Tokens --- */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 24px;
  --radius-pill: 9999px;

  /* --- 4. Elevation Shadows (Hardware Accelerated) --- */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-drawer: -4px 0 24px rgba(0, 0, 0, 0.15);
}

/* --- 5. Color Schemes 2.0 Engine --- */
{% for scheme in settings.color_schemes %}
  .color-{{ scheme.id }} {
    --color-background: {{ scheme.settings.background.red }}, {{ scheme.settings.background.green }}, {{ scheme.settings.background.blue }};
    --color-foreground: {{ scheme.settings.text.red }}, {{ scheme.settings.text.green }}, {{ scheme.settings.text.blue }};
    --color-primary: {{ scheme.settings.primary.red }}, {{ scheme.settings.primary.green }}, {{ scheme.settings.primary.blue }};
    --color-primary-contrast: {{ scheme.settings.primary_contrast.red | default: 255 }}, {{ scheme.settings.primary_contrast.green | default: 255 }}, {{ scheme.settings.primary_contrast.blue | default: 255 }};
    --color-border: {{ scheme.settings.border.red }}, {{ scheme.settings.border.green }}, {{ scheme.settings.border.blue }};
    background-color: rgb(var(--color-background));
    color: rgb(var(--color-foreground));
  }
{% endfor %}
```

---

## 3. 🧩 ТАКСОНОМІЯ ТА СХЕМИ THEME BLOCKS 2.0 (4 Рівні)

Кожен блок гарантовано містить **$\le 50$ налаштувань** у схемі для проходження лінтера `ExcessiveSettingsCount`.

### 3.1. Рівень 1: Atoms (0–5 Settings)

| Файл блоку | Назва | Налаштувань | Призначення та нативні слоти |
| :--- | :--- | :---: | :--- |
| `blocks/heading.liquid` | Heading | 4 | Заголовок h1-h6, розмір шрифту (`--font-size-*`), вирівнювання, семантичний тег. |
| `blocks/text.liquid` | Text | 3 | Richtext або plain text з fluid інтерполяцією та вирівнюванням. |
| `blocks/button.liquid` | Button | 5 | Стилі: `solid`, `outline`, `link`; посилання, цільове вікно, іконка стрілки. |
| `blocks/badge.liquid` | Badge | 4 | Текстовий або динамічний бейдж (`Sale -X%`, `New`, `Best Seller`). |
| `blocks/icon.liquid` | Icon | 3 | Вбудована SVG-бібліотека (24 комерційні іконки без веб-шрифтів). |
| `blocks/divider.liquid` | Divider | 2 | Розділювальна лінія або прозорий спейсер з адаптивною висотою. |
| `blocks/rating.liquid` | Star Rating | 3 | Нативний рендер зірочок на базі `product.metafields.reviews.rating.value` з fallback на `@app`. |

### 3.2. Рівень 2: Molecules (5–20 Settings)

| Файл блоку | Назва | Налаштувань | Призначення та нативні слоти |
| :--- | :--- | :---: | :--- |
| `blocks/_price.liquid` | Product Price | 8 | Регулярна ціна, ціна порівняння, бейдж економії, написи податків/доставки, мультивалютний рендер. |
| `blocks/_variant-picker.liquid` | Variant Picker | 12 | Вибір варіантів: Color Swatches (HEX або зображення), Pill Buttons, Dropdown, Combined Listings routing. |
| `blocks/_buy-buttons.liquid` | Buy Buttons | 10 | Кнопка Add to Cart, Dynamic Checkout Buttons (Shop Pay / PayPal), валідація наявності. |
| `blocks/_inventory-bar.liquid` | Inventory Bar | 6 | Індикатор залишків складу: прогрес-бар, реальні дані `variant.inventory_quantity`, поріг низького залишку. |
| `blocks/_accordion-item.liquid`| Accordion Item | 5 | Семантичний `<details>` та `<summary>` з плавним розкриттям без JS. |
| `blocks/_countdown-honest.liquid`| Countdown Timer | 7 | Таймер акції з реальною фіксованою датою завершення (без фейкових перезапусків). |
| `blocks/_delivery-estimator.liquid`| Delivery Estimator | 9 | Розрахунок орієнтовної дати доставки на базі геолокації та поштових правил мерчанта. |

### 3.3. Рівень 3: Organisms (20–45 Settings)

| Файл блоку | Назва | Налаштувань | Призначення та нативні слоти |
| :--- | :--- | :---: | :--- |
| `blocks/_quantity-breaks.liquid` | Quantity Breaks | 24 | 3-4 рівні об'ємних знижок (купи 2 - отримай 10%, купи 3 - 20%), сумісність з Shopify Automatic Discounts. |
| `blocks/_cart-rewards.liquid` | Cart Rewards Bar | 18 | 3-рівневий прогрес-бар кошика (Free Shipping $\to$ Free Gift $\to$ Discount). |
| `blocks/_cart-upsells.liquid` | Cart Upsell Matrix | 16 | 3-насіннєвий Upsell Engine у кошику з нативним Section Rendering API. |
| `blocks/_media-gallery.liquid` | Media Gallery | 22 | Адаптивна галерея медіа: CSS Scroll Snap, зум зображень, 3D-моделі AR, без зовнішніх плагінів. |

### 3.4. Рівень 4: Structural Containers

```liquid
{% comment %}
  Group Container Block (blocks/group.liquid)
  Theme Blocks 2.0 Host Container
{% endcomment %}
<div class="theme-block-group theme-block-group--{{ block.id }}" {{ block.shopify_attributes }}>
  {% content_for 'blocks' %}
</div>

{% schema %}
{
  "name": "Group Container",
  "tag": null,
  "settings": [
    {
      "type": "select",
      "id": "direction",
      "label": "Layout Direction",
      "options": [
        { "value": "row", "label": "Horizontal Row" },
        { "value": "column", "label": "Vertical Column" }
      ],
      "default": "column"
    },
    {
      "type": "select",
      "id": "spacing",
      "label": "Spacing Preset",
      "options": [
        { "value": "compact", "label": "Compact (8px)" },
        { "value": "normal", "label": "Normal (16px)" },
        { "value": "spacious", "label": "Spacious (24px)" }
      ],
      "default": "normal"
    }
  ],
  "blocks": [
    { "type": "@theme" },
    { "type": "@app" }
  ],
  "presets": [
    {
      "name": "Group Container"
    }
  ]
}
{% endschema %}
```

---

## 4. 🛒 ВИСОКОКОНВЕРСІЙНІ КОМЕРЦІЙНІ РУШІЇ (Commerce Engines)

### 4.1. Cart Drawer 2.0 Engine
* **Багаторівневий прогрес-бар (`_cart-rewards.liquid`):**
  - Рівень 1: Безкоштовна доставка (поріг розраховується з `settings.free_shipping_threshold`).
  - Рівень 2: Безкоштовний подарунок (автоматичне додавання `gift_variant_id` через Cart API при досягненні порогу).
  - Рівень 3: Знижка на кошик (підказка про код купона або автоматична знижка через Shopify Functions).
* **3-Насіннєвий Upsell Engine (`_cart-upsells.liquid`):**
  - Запит до рекомендаційного API:
    ```javascript
    const res = await fetch(`/recommendations/products.json?product_id=${seedId}&limit=3&intent=related`);
    const { products } = await res.json();
    ```
  - Швидке додавання з вибором розміру безпосередньо всередині кошика через Ajax Section Rendering.

### 4.2. Social Proof & UGC Engine
* **Instagram 3D Profile Grid (`sections/social-profile-grid.liquid`):**
  - 3D Cube-turn анімація при наведенні / свайпі.
  - Офіційний синій бейдж верифікації бренду, лічильник публікацій та підписників.
  - Відкриття повноекранного модального вікна Stories з автоматичним прогресом перегляду.

### 4.3. PDP Conversion Stack
* **Динамічний вибір варіантів (`variant-selects.js`):**
  - Автоматична заміна галереї зображень, оновлення ціни, статусу складу та кнопки купівлі через `fetch(?section_id=...)`.
  - Підтримка Combined Listings: зміна URL без повного перезавантаження сторінки через `history.replaceState`.
* **Sticky Add-to-Cart:**
  - Активується через `IntersectionObserver`, коли основна кнопка додавання до кошика виходить за межі видимості.

---

## 5. ⚡ АРХІТЕКТУРА ВЕБ-КОМПОНЕНТІВ (Zero-Framework Vanilla JS)

Усі компоненти наслідують W3C `HTMLElement` без використання зовнішніх бібліотек (jQuery, Alpine, React).

```javascript
/**
 * CartDrawer Component
 * Handles drawer opening, focus trapping, and section rendering updates.
 */
class CartDrawer extends HTMLElement {
  constructor() {
    super();
    this.abortController = null;
  }

  connectedCallback() {
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.addEventListener('click', this.onOverlayClick.bind(this), { signal });
    document.addEventListener('keydown', this.onKeyDown.bind(this), { signal });
  }

  disconnectedCallback() {
    if (this.abortController) {
      this.abortController.abort(); // Prevents memory leaks
    }
  }

  open() {
    this.classList.add('is-open');
    document.body.classList.add('overflow-hidden');
    this.querySelector('.drawer__inner')?.focus();
  }

  close() {
    this.classList.remove('is-open');
    document.body.classList.remove('overflow-hidden');
  }

  onOverlayClick(e) {
    if (e.target === this || e.target.classList.contains('drawer__close')) {
      this.close();
    }
  }

  onKeyDown(e) {
    if (e.key === 'Escape' && this.classList.contains('is-open')) {
      this.close();
    }
  }
}
customElements.define('cart-drawer', CartDrawer);
```

---

## 6. ♿ СТАНДАРТ ДОСТУПНОСТІ (WCAG 2.1 AA Compliance)

1. **Focus Trap у діалогах:** При відкритті `<cart-drawer>` або `<modal-dialog>` фокус переміщується всередину вікна; переходи через `Tab` / `Shift+Tab` циклично утримуються всередині.
2. **Клавіатурні скорочення:** Натискання `Escape` завжди закриває будь-яке модальне вікно або випадаюче меню.
3. **Screen Reader Live Regions:** Мутації кошика транслюються у вузол `<div role="status" aria-live="polite">` для голосового озвучення кількості товарів та суми.
4. **Сенсорні цілі (Touch Targets):** Усі кнопки, чекбокси та посилання на мобільних пристроях мають розмір $\ge 44\times44\text{ CSS-пікселів}$.
5. **Колірний контраст:** Співвідношення яскравості між текстом та фоном складає $\ge 4.5:1$ для звичайного тексту та $\ge 3:1$ для великих заголовків.

---

## 7. 🛡️ ШЛЮЗИ СЕРТИФІКАЦІЇ SHOPIFY THEME STORE (CI/CD Matrix)

| Тест / Шлюз | Команда перевірки | Критерій успіху (Fail-Closed) |
| :--- | :--- | :--- |
| **Theme Check AST** | `shopify theme check --fail-level warning` | `0 errors, 0 warnings` |
| **Settings Count Gate** | `python scripts/shopify/apex_theme_distiller.py` | Кожен блок і секція $\le 50$ налаштувань |
| **External CDN Scan** | `rg -n "(https?:)?//(?!cdn\.shopify\.com)" layout blocks sections snippets` | `0 matches` (100% локальні ассети) |
| **Template Size Guard** | `find templates -name "*.json" -size +64k` | `0 файлів` (квота платформи: $< 512\text{ KB}$) |
| **Lighthouse Mobile** | `lhci autorun` (Mobile 4G emulation) | Performance $\ge 90$, Accessibility $\ge 95$, LCP $< 2.5\text{s}$ |
| **Clean Packaging** | `shopify theme package` | Валідний ZIP-архів без `.git`, `.DS_Store`, `node_modules` |

---
*Документ є невіддільною частиною архітектури DNK OS і затверджений рішенням DEC-074.*
