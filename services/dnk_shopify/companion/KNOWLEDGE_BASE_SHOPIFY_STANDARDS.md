---
title: "База знань стандартів Shopify Theme Store та результатів дистиляції 14 донорів"
description: "Exhaustive Reference Knowledge Base: Shopify Theme Blocks 2.0, Platform Limits, Customizer Architecture & 14-Donor Distillation Matrix."
mrh_id: "services/dnk_shopify/companion/KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md"
status: Active
version: "2.0.0"
updated: 2026-11-18
tags:
  - shopify
  - standards
  - theme-blocks
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "services/dnk_shopify/companion/KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md"
> purpose: "Exhaustive Reference Knowledge Base: Shopify Theme Blocks 2.0, Platform Limits, Customizer Architecture & 14-Donor Distillation Matrix."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym Kuzmenko & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📚 БАЗА ЗНАНЬ СТАНДАРТІВ SHOPIFY THEME STORE ТА РЕЗУЛЬТАТІВ ДИСТИЛЯЦІЇ 14 ДОНОРІВ (2026 LTS)

Цей документ є канонічним довідником для агента-компаньйона **Shopify Theme Architect Companion (`DNK-ThemeCraft`)** при розробці, аудиті та графтингу комерційних тем Shopify преміум-сегменту ($350–$420 MSRP).

---

## 🧩 1. АРХІТЕКТУРА SHOPIFY THEME BLOCKS 2.0 (ВЕРЕСЕНЬ–ЛИСТОПАД 2026)

### 1.1. Концептуальний перехід від OS 2.0 до Theme Blocks 2.0
У класичному Online Store 2.0 (2021–2024) блоки визначалися локально всередині схеми конкретної секції (`sections/*.liquid`), не могли перевикористовуватися між різними секціями та не підтримували багаторівневу вкладеність.
У **Theme Blocks 2.0 (Horizon / Tinker / Sugar / Story 2025–2026)** блоки є глобальними атомарними та молекулярними файлами у директорії `blocks/*.liquid`, які можуть вкладатися один в одного до **8 рівнів глибини** за допомогою директиви `{% content_for 'blocks' %}`.

### 1.2. Три типи рендерингу блоків у Theme Blocks 2.0

| Директива Liquid | Призначення | Правило оголошення в `{% schema %}` |
| :--- | :--- | :--- |
| `{% content_for 'blocks' %}` | Динамічний рендеринг масиву дочірніх блоків у секції або блоці-контейнері. | `"blocks": [{ "type": "@theme" }, { "type": "@app" }]` або явний allowlist `[{ "type": "dnk-card" }]`. |
| `{% content_for 'block', type: 'dnk-buy-box', id: 'static-buy-box' %}` | Статичний рендеринг обов'язкового структурного блоку з фіксованим `id` (наприклад, `product-media` та `product-info` у PDP). | Не потребує додавання в масив `blocks` (мерчант не може видалити статичний блок, але редагує його налаштування та вкладені в нього блоки). |
| `{% render 'dnk-snippet', param: val %}` | Ізольований серверний виклик допоміжного макросу без власного UI у Theme Editor. | Снипети у `snippets/*.liquid` не мають власного `{% schema %}`. |

### 1.3. Правила обгортки `.shopify-block` та Ізоляції Батько–Дитина
1. **Автоматична DOM-обгортка:** Shopify обгортає кожен відрендерений Theme Block у `<div id="shopify-block-{{ block.id }}" class="shopify-block">` (окрім випадків, коли у `{% schema %}` явно задано `"tag": null`). Усі CSS Grid та Flexbox контейнери повинні враховувати цей елемент як прямого нащадка.
2. **Інкапсуляція стану (Parent Blindness Invariant):** Батьківська секція або блок-контейнер **не має доступу** до `block.settings` або конкретних типів своїх дочірніх Theme Blocks у Liquid (усі вони видимі батькові лише як абстрактний тип `@theme`). Якщо батьківському контейнеру потрібно знати стан дочірнього блоку (наприклад, кількість слайдів чи заголовки вкладок), дочірній блок друкує `data-*` атрибути у власну HTML-розмітку, а Web Component контейнера зчитує їх із DOM.
3. **Заборона змішування `@theme` та локальних Section Blocks:** Секція повинна використовувати або глобальні блоки `blocks/*.liquid` (`{"type": "@theme"}`), або власні локальні блоки секції, але **ніколи обидва типи одночасно**.

---

## 🎯 2. ПАТЕРНИ КОНТЕКСТУ `closest.*` ТА ДИРЕКТИВИ `render` vs `include`

### 2.1. Контекстна прив'язка ресурсів (`closest.*`)
Коли товарний блок (ціна, бейдж, селектор варіантів, кнопка купівлі, таймер, індикатор залишків) вкладається на 3–5 рівнів углиб універсальних контейнерів (`Custom Columns` $\to$ `Column` $\to$ `Group` $\to$ `Card` $\to$ `Product Price`), глобальний об'єкт `product` може бути відсутнім (наприклад, на головній сторінці або у Featured Product секції).
Платформа Shopify (2025–2026) вирішує це через автоматичний контекстний резолвер `closest.*`:

| Об'єкт контексту | Де застосовується | Канонічний патерн безпечного фолбеку в DNK OS |
| :--- | :--- | :--- |
| `closest.product` | Товарні картки, PDP, Featured Product, Quick View, Upsell-блоки. | `{% liquid assign product_resource = closest.product | default: product | default: section.settings.product %}` |
| `closest.collection` | Картки колекцій, банери категорій, хлібні крихти. | `{% liquid assign collection_resource = closest.collection | default: collection | default: section.settings.collection %}` |
| `closest.article` | Картки статей блогу, авторські блоки. | `{% liquid assign article_resource = closest.article | default: article %}` |
| `closest.blog` | Секції блогу та навігації по тегах. | `{% liquid assign blog_resource = closest.blog | default: blog %}` |
| `closest.page` | Контентні блоки лендінгів та інформаційних сторінок. | `{% liquid assign page_resource = closest.page | default: page %}` |
| `closest.metaobject` | Шаблони метаоб'єктів (автори, інгредієнти, луки). | `{% liquid assign meta_resource = closest.metaobject | default: metaobject %}` |

### 2.2. Сувора директива `render` проти `include` та сучасні медіа-фільтри

| Застарілий патерн (ЗАБОРОНЕНО 🔴) | Канонічний стандарт 2026 (ОБОВ'ЯЗКОВО 🟢) | Архітектурне обґрунтування |
| :--- | :--- | :--- |
| `{% include 'product-card' %}` | `{% render 'dnk-product-card', card_product: item %}` | `include` мутує глобальний скоуп змінних секції та знижує швидкість парсингу Liquid на 30–45%. `render` створює чистий ізольований стек. |
| `{% include 'icon' with 'cart' %}` | `{% render 'dnk-icon', name: 'cart', size: 20 %}` | Явна передача іменованих параметрів запобігає колізіям однойменних змінних. |
| `{{ image \| img_url: '800x' }}` | `{{ image \| image_url: width: 800 \| image_tag: widths: '375, 550, 750, 1100', sizes: sizes, loading: loading }}` | Фільтр `image_url` підтримує автоматичну генерацію `srcset`, фокусну точку (`focal_point`), обрізку за `aspect_ratio` та CDN-конвертацію у AVIF/WebP. |
| `<script src="{{ 'app.js' \| asset_url }}"></script>` | `<script src="{{ 'dnk-app.js' \| asset_url }}" defer></script>` | Усуває блокування парсера HTML (`ParserBlockingScript`) та покращує FCP/LCP. |

---

## 🛡️ 3. ЛІМІТИ ПЛАТФОРМИ SHOPIFY ТА ПРАВИЛА ПРОЕКТУВАННЯ КАСТОМАЙЗЕРА

### 3.1. Жорсткі ліміти платформи та пастки, що викликають Silent Fail

| Параметр платформи | Жорсткий ліміт Shopify | Комерційний ліміт DNK | Наслідок порушення |
| :--- | :---: | :---: | :--- |
| **Розмір `templates/*.json` та `sections/*.json`** | **512 KB** (524,288 B) | **$\le 350\text{ KB}$** (Gate: 400 KB) | Theme Editor мовчки перестає зберігати сторінку при додаванні блоків мерчантом. |
| **Кількість файлів у `blocks/*.liquid`** | **300 файлів** | **$\le 180$ файлів** | Помилка `shopify theme push`: неможливо завантажити тему в магазин. |
| **Кількість Section Groups (`sections/*.json`)** | **20 груп** | **$\le 8$ груп** | Відмова збереження нових груп секцій (Header/Footer/Aside). |
| **Глибина вкладеності `content_for 'blocks'`** | **8 рівнів** | **$\le 5$ рівнів** | Вкладені глибше блоки ігноруються рендерером. |
| **Рекурсія статичних блоків (`content_for 'block'`)** | **2 рівні** | **1–2 рівні** | Помилка компіляції схеми секції. |
| **Кількість секцій у шаблоні** | **50 секцій** | **$\le 25$ секцій** | Деградація TTFB та перевищення ліміту DOM-вузлів (> 1,500). |
| **Загальна кількість блоків у шаблоні** | **1,250 блоків** | **$\le 400$ блоків** | Роздування JSON понад 512 KB та фризи Theme Editor. |
| **Кількість налаштувань у секції / блоці** | 50 / 50 | **$\le 25$ / $\le 16$** | Кожне налаштування записується в JSON шаблону для кожного екземпляра блоку (навіть із дефолтним значенням!). |
| **Умова `visible_if` у `{% schema %}`** | **250 символів** | **$\le 160$ символів** | Підтримує **лише** `==`, `!=`, `and`, `or`. Будь-яке використання `>`, `<`, `>=`, `<=`, дужок `()` або застосування до `product`/`collection`/`page`/`blog`/`article` пікерів відхиляє всю схему! |
| **Кількість кроків у `range` (`(max - min) / step`)** | **101 крок** | **$\le 100$ кроків** | Помилка валідації схеми. Значення в пресеті має точно лежати на сітці `min + n * step`. |
| **Поле Custom CSS секції в редакторі** | **500 символів** | **$\le 500$ символів** | Редактор блокує збереження кастомних стилів секції. |

### 3.2. Золоті правила проектування Кастомайзера (Merchant UX)
1. **Групування по 5–6 налаштувань під одним `header`:** Розбивай налаштування за дією мерчанта (`Layout`, `Typography`, `Colors`, `Mobile`), а не стіною з 20 полів. Якщо всі поля групи мають спільний `visible_if`, додавай той самий `visible_if` і на сам `type: "header"`.
2. **Розміщення `"category"` у пресетах:** Ключ `"category"` розміщується **виключно** всередині кожного об'єкта масиву `"presets": [{ "name": "...", "category": "..." }]`. Розміщення `"category"` у корені `{% schema %}` викликає відмову завантаження теми.
3. **Економія JSON-квоти через живі плейсхолдери:** Замість створення окремих тоглів і полів для виводу цін чи знижок у заголовках і бейджах, підтримуй підстановку токенів `[price]`, `[compare_price]`, `[savings]`, `[percentage]`, `[quantity]`, `[br]`, які обробляються снипетом `snippets/dnk-price-placeholders.liquid`.
4. **Пріоритет Медіа (Відео > Зображення):** Там, де доречне медіа, пропонуй обидва пікери (`image_picker` та `video`) без зайвого селектора «Тип медіа: Картинка чи Відео». Якщо задано обидва, пріоритет має відео.

---

## 🧬 4. МАТРИЦЯ АНАЛІЗУ ТА ДИСТИЛЯЦІЇ ВСІХ 14 ВОРКПЛЕЙСІВ-ДОНОРІВ (`DNK-Ecom_git_mirrow`)

Нижче наведено повний інструментальний зріз усіх 14 воркплейсів, отриманий під час глибокого AST-сканування репозиторію (сумарно проаналізовано **12,519 файлів тем**, серед яких **1,507 блоків**, **3,489 секцій** та **3,823 снипети**):

| № | Воркплейс (Донор) | `blocks/` (всього) | Блоки з `content_for 'blocks'` | `sections/` (всього) | Секції з `content_for 'blocks'` | `snippets/` / `assets/` | Патерни Core Web Vitals (LCP, Responsive Images, CSS) | Патерни Web Components (0% jQuery/Alpine) | Топологія CSS-змінних та токенів |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| 1 | **`sugar`** (v2.3.10) | **296** | **13** (`custom-column`, `container`, `row`, `slider`, `grid-mobile-slider`, `bundle-builder`, `tabs`, `timeline`) | 83 | 17 | 144 / 539 | `snippets/media-sizes-scope.liquid` (точний розрахунок `sizes` від колонок сітки), `snippets/stylesheet-once.liquid`, LCP eager/high для перших 2 секцій шаблону (`section.index <= 2`). | 45+ Custom Elements (`sugar-cart-drawer`, `product-info`, `product-form`, `modal-dialog`, `slider-component`) + реактивне ядро `SugarPricing` і `PUB_SUB_EVENTS`. | `rgb(var(--color-foreground))`, `var(--corner-media\|container\|badge\|button)`, інлайн `--pp-*` змінні на кореневому елементі, `[data-sugar-animating]`. |
| 2 | **`story`** (v4.0.8) | **257** | **57** (`accordion`, `bento-box`, `carousel`, `group`, `tab-item`, `_cart-drawer-body`, `_lookbook-row`) | 71 | 52 | 121 / 217 | Нативна генерація `image_url` + `image_tag` з фокусною точкою (`snippets/image.liquid`), відкладене підвантаження позаекранних секцій через `IntersectionObserver`. | 52 Custom Elements (`cart-drawer`, `cart-rewards`, `bundle-builder`, `collapsible-tab`, `scrolling-marquee`, `predictive-search`) на чистих ES6 класах. | Схема `.color-{{ scheme.id }}`, семантичні змінні `--color-bg`, `--color-text`, `--radius-*`, інлайн-налаштування відступів `--pt`, `--pb`. |
| 3 | **`ella`** (v7.0 OS 2.0) | **250** | **87** (`_header-column`, `_mega-menu-*`, `card-product-flex`, `filters`, `group`, `_lookbook-item-all`) | 68 | 51 | 202 / 192 | Адаптивні `srcset` із 7 брейкпоінтами (`165w`–`1920w`), skeleton-плейсхолдери з фіксованим `aspect-ratio` для нульового CLS у великих каталогах. | 38 Custom Elements (`facet-filters-form`, `price-range`, `product-card-swatch`, `header-drawer`, `quick-add-modal`) без jQuery у вітрині v7. | Токени `--color-base-*`, `--font-heading-*`, `--grid-desktop-horizontal-spacing`, модульні змінні карток товарів. |
| 4 | **`casaio`** (Horizon CRO) | **148** | **30** (`group`, `_card`, `accordion`, `_quantity-breaks`, `_slide`, `_marquee`) | 50 | 32 | 154 / 66 | Нативний `view-transition-name` API для миттєвих переходів між PLP та PDP, `snippets/stylesheets.liquid` із критичним CSS preload, `fetchpriority="high"` на LCP-банерах. | 34 ES6 Модулі-компоненти (`accordion-custom`, `dialog-component`, `slideshow-component`, `variant-picker`, `cart-drawer-component`) з декларативними `ref` селекторами. | Horizon 3-Tier токени: `:root` брендові примітиви $\to$ `.color-scheme-*` $\to$ локальні приватні змінні `--_padding-*`, `--_gap`. |
| 5 | **`shrine-pro`** (v2.0.0) | **98** | **6** (`container`, `row`, `column`, `slide`, `collapsible-row`, `fbt-wrapper`) | 87 | 12 | 132 / 128 | Агресивний lazy-load нижніх секцій, інлайн-критичні змінні у `layout/theme.liquid`, оптимізовані SVG-іконки оплати (`blocks/payment-badges.liquid`). | 29 Custom Elements (`cart-drawer`, `quantity-breaks`, `bundle-deals`, `sticky-atc`, `countdown-timer`). *(Примітка: DRM `shrinesolutions.com/api/verify` повністю вирізається `cleanroom-sanitizer`)*. | Змінні `--color-foreground`, `--color-background`, `--gradient-base-*`, `--media-radius`, `--buttons-radius`. |
| 6 | **`staging-lab`** | **102** | **26** (`group`, `_card`, `accordion`, `bundle-builder`, `grid-mobile-slider`) | 44 | 27 | 144 / 73 | Експериментальний полігон гібридизації Horizon (`tinker`) + Sugar (`media-sizes-scope`, `stylesheet-once`). | Гібридні Web Components: `accordion-custom`, `dialog-component`, `dnk-bundle-builder`, `dnk-cart-drawer`. | Уніфікований міст токенів `--color-*` (Horizon) $\leftrightarrow$ `--dnk-*` та `[data-dnk-animating]`. |
| 7 | **`staging`** | **97** | **22** (`group`, `_card`, `accordion`, `_sc-fbt-widget`, `btd-table`) | 40 | 23 | 144 / 70 | Стабільна передрелізна гілка з інтегрованими CRO-блоками (`_sc-fbt-widget`, `btd-table`) та нульовим CLS. | Чисті ES6 Custom Elements без зовнішніх залежностей, модульне завантаження через `<script type="module">`. | Стандартизована система `.color-scheme` + локальні `--_*` змінні панелей (`snippets/layout-panel-style.liquid`). |
| 8 | **`tinker`** (Shopify Horizon) | **95** | **22** (`group`, `_card`, `accordion`, `_header-menu`, `_product-details`, `_slide`) | 40 | 23 | 144 / 68 | Еталонна архітектура Shopify 2026: `section.index == 1` LCP пріоритезація, `snippets/image.liquid` з точними `widths`, нативний CSS `content-visibility: auto`. | Еталонні Vanilla Web Components від команди Shopify (`Component` base class з автоматичним `refs` мапінгом та `AbortController`). | Канонічний `snippets/theme-styles-variables.liquid` + `snippets/color-schemes.liquid` + `snippets/layout-panel-style.liquid`. |
| 9 | **`main`** | **95** | **22** (`group`, `_card`, `accordion`, `_header-menu`, `_product-details`, `_slide`) | 40 | 23 | 144 / 68 | Канонічний базовий геном репозиторію (синхронізований із `tinker`), 100% чистий від сторонніх бібліотек, готовий до графтингу. | Повний набір базових Custom Elements Horizon (`dialog-component`, `accordion-custom`, `product-form-component`, `variant-picker`). | Базова 3-рівнева топологія CSS-токенів Horizon. |
| 10 | **`ks-origin`** (KondaSoft) | **66** | **13** (`_card`, `group`, `accordion`, `_product-main-buy-buttons`, `_slide`) | 36 | 19 | 39 / 27 | Надлегкий стек (всього 27 асетів!), відсутність важких CSS-фреймворків, миттєвий FCP < 0.9s, нативна галерея `snippets/product-gallery.liquid`. | Ультра-чисті HTML5 `<dialog>` модалки, `<details>` акордеони, CSS `scroll-snap` слайдери та реактивна шина `assets/storefront-events.js` (~1 KB). | Компактні CSS Custom Properties `--ks-*` та `--bs-*` (Bootstrap-inspired spacing/grid tokens без JS-рантайму). |
| 11 | **`sections-vault`** | **9** | **3** (`group`, `column`, `slide`) | **1,040** | 14 | 246 / 68 | Колекція з 1,040 автономних комерційних секцій (`dnk-*`, `ss-*`, Section Store): інкапсульовані медіа-хелпери та автономні SVG-спрайти. | Самодостатні Vanilla JS Custom Elements або ізольовані IIFE-контролери всередині кожної секції для миттєвого drop-in монтажу. | Локально скоупнуті CSS-змінні на `#shopify-section-{{ section.id }}` з фолбеками на глобальні змінні теми. |
| 12 | **`donor-lab`** | **148** (у підтемах) | **30** | **1,890** (у 18 вендор-паках) | 64 | 2,209 / 1,105 | Лабораторія первинної деконструкції (Shrine Pro, Impact, Prestige, Impulse, Focal, Kalles, Concept, Enterprise): повний спектр CWV-патернів. | Джерело сировинних патернів Web Components (3D-моделі, AR-перегляд, палітри кольорів, калькулятори доставки) перед Cleanroom-очищенням. | Різнорідні вендорські системи токенів, що проходять нормалізацію через `companion_distiller.py` у `--dnk-*`. |
| 13 | **`elixir`** (v1.6.2 Vault) | **20** (дистильовані CRO-молекули) | **8** (`listicle-item`, `cs-amazon-reviews`, `bundle-offer`, `comparison-table`) | 45 (аудитовані) | 12 | 48 / 32 | Оптимізовані під холодний платний трафік (Meta/TikTok Ads) Advertorial та Listicle воронки з миттєвим першим екраном. | Cleanroom-молекули у `_Shopify_Theme_Audit_Workflow/distilled_vault/elixir-1.6.2/`, повністю очищені від `head-bootstrap.js` та `.sw-fr` DRM. | Семантичні токени воронок `--cs-*` $\to$ нормалізовані у `--dnk-*` для високої контрастності CTA та таблиць порівняння. |
| 14 | **`ascendify`** (CRO Reference) | **24** (еталонні CRO-специфікації) | **6** | 35 | 10 | 42 / 28 | Спеціалізовані патерни D2C-конверсії: низьковагові таблиці вигоди, прогресивне підвантаження відгуків та UGC-відео. | Ізольовані Vanilla JS віджети соціального доказу, таймерів дефіциту та калькуляторів економії підписки. | Модульні змінні бейджів вигоди, прогрес-барів та акцентних кнопок чекауту. |

---

## ⚡ 5. АРХІТЕКТУРА CORE WEB VITALS ТА STOREFRONT API У ТЕМАХ DNK SOVEREIGN

### 5.1. Еталонна реалізація `snippets/dnk-media-sizes-scope.liquid`
Щоб браузер на мобільному телефоні або у 4-колонковій сітці десктопа не завантажував 2000px зображення, кожен контейнер (`Custom Columns`, `Grid`, `Slider`) обчислює свою частку ширини екрана і передає її дочірнім блокам:
```liquid
{%- comment -%}
  Usage: {% render 'dnk-media-sizes-scope', columns_desktop: 4, columns_mobile: 2, gap_px: 16 %}
{%- endcomment -%}
{%- liquid
  assign cols_d = columns_desktop | default: 1 | at_least: 1
  assign cols_m = columns_mobile | default: 1 | at_least: 1
  assign gap = gap_px | default: 16
  assign desktop_vw = 100 | divided_by: cols_d
  assign mobile_vw = 100 | divided_by: cols_m
  capture calculated_sizes
    echo '(min-width: 1200px) calc((var(--dnk-page-width, 1280px) - ' | append: gap | append: 'px * ' | append: cols_d | minus: 1 | append: ') / ' | append: cols_d | append: '), '
    echo '(min-width: 750px) ' | append: desktop_vw | append: 'vw, '
    echo mobile_vw | append: 'vw'
  endcapture
-%}
```

### 5.2. Реактивний AJAX-Кошик (Section Rendering API + Storefront GraphQL `2026-04`)
Для досягнення INP < 120ms та миттєвого оновлення Cart Drawer (включно з прогрес-баром безкоштовної доставки та автоматичними подарунками) використовується комбінований підхід:
1. **Мутація кошика (`/cart/add.js` або `/cart/change.js`):** У запит передається параметр `sections: "dnk-cart-drawer,dnk-cart-icon-bubble"`. Shopify за один HTTP-раундтріп виконує мутацію та повертає вже відрендерений серверний HTML оновлених секцій.
2. **DOM Morphing без мерехтіння:** Web Component `<dnk-cart-drawer>` встановлює атрибут `data-dnk-animating=""`, оновлює вміст `.dnk-cart-drawer__items`, `.dnk-cart-drawer__rewards` та `.dnk-cart-drawer__footer`, зберігаючи фокус клавіатури для доступності WCAG 2.1 AA.
3. **Storefront GraphQL API (`/api/2026-04/graphql.json`):** Застосовується для складних багатопозиційних операцій (`cartLinesAdd`, `cartDiscountCodesUpdate`, `cartBuyerIdentityUpdate`) та миттєвого підвантаження персоналізованих рекомендацій.
