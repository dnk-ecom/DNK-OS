---
title: "Канонічна майстер-специфікація побудови теми DNK-Ecom для Shopify Theme Store ($350–$420 MSRP)"
status: approved
type: specification
domain: shopify
author: "Antigravity (Chief Architect) & Gerych-root (Auditor) & DNK-e.com Maksym"
version: "3.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/projects/dnk_ecom/MASTER_SPECIFICATION_DNK_ECOM_THEME_STORE.md"
> purpose: "Вичерпна інженерна специфікація побудови флагманської теми DNK-Ecom у DNK OS: повний синтез 10 донорів, відповідність офіційним стандартам Shopify Theme Store ($350-$420 MSRP), Zero-Framework Web Components, 100% Theme Blocks 2.0 та Core Web Vitals 90+ Green."
> canonical_source: true
> alters_files:
>   - "docs/projects/dnk_ecom/MASTER_SPECIFICATION_DNK_ECOM_THEME_STORE.md"
> triggers_tasks: []
> status: "Approved"
> version: "3.0.0"
> updated_at: "2026-11-16"
> author: "Antigravity (Chief Architect) & Gerych-root & DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ КАНОНІЧНА МАЙСТЕР-СПЕЦИФІКАЦІЯ ПОБУДОВИ ТЕМИ DNK-ECOM
## Проходження офіційної сертифікації та комерційний продаж у Shopify Theme Store ($350–$420 MSRP)

---

## ⚡ 1. EXECUTIVE SUMMARY ТА АРХІТЕКТУРНА ТРІАДА

```mermaid
flowchart TD
    subgraph Donors ["1. 10 Донорів світового рівня (Джерело ДНК)"]
        D1["Sugar (296 блоків, sizes-scope, CSS-токени)"]
        D2["Shrine Pro (Cart Drawer V2, Tiered Rewards)"]
        D3["Story (Журнальний Lookbook, Parallax)"]
        D4["Ella (8 Mega Menu, Ajax Faceted Filters)"]
        D5["Casaio (Quantity Breaks v2, UGC)"]
        D6["Elixir (Advertorials, Comparison Tables)"]
        D7["Ascendify (28 вбудованих CRO-віджетів)"]
        D8["KS-Origin (HTML5 dialog, 0 KB баласту)"]
        D9["Tinker (Horizon Baseline, settings_schema)"]
        D10["DNK-Ecom-Sections (166 авторських сніпетів Максима)"]
    end

    subgraph ThemeStoreGates ["2. 7 Ворот якості Shopify Theme Store"]
        G1["100% Theme Blocks 2.0 (content_for 'blocks')"]
        G2["Zero Framework (100% Web Components)"]
        G3["Core Web Vitals (LCP < 1.8s, CLS = 0, INP < 150ms)"]
        G4["100% i18n Локалізація (t: ключі, uk.json + en.default)"]
        G5["WCAG 2.1 AA Accessibility (ARIA, TrapFocus)"]
        G6["Ліміти платформи (Templates <= 512KB, Blocks <= 300)"]
        G7["Zero DRM / Zero Telemetry (100% Cleanroom)"]
    end

    subgraph DNKOSCore ["3. Цільовий продукт: DNK Sovereign 1.0.0 Apex"]
        C1["services/dnk_shopify/DNK_Sovereign_Apex/"]
        C2["LocalStorefrontManager (0.2 ms офлайн-тести)"]
        C3["DNK-ThemeCraft Companion (AI-агент розробки)"]
        C4["Повний релізний ZIP-архів ($350-$420 MSRP)"]
    end

    Donors --> C1
    ThemeStoreGates --> C1
    C1 --> DNKOSCore
```

---

## 🔍 2. АУДИТ РЕПОЗИТОРІЮ DNK_OS: ПОТОЧНИЙ СТАН ТА GAP-АНАЛІЗ

На основі поглибленого інспектування репозиторію **`DNK_OS`** зафіксовано наступні результати:

### 2.1. Що вже розгорнуто та працює на 100%:
1. **Базова збірка `DNK_Sovereign_Apex`**:
   - Розташування: [`services/dnk_shopify/DNK_Sovereign_Apex/`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS/services/dnk_shopify/DNK_Sovereign_Apex/).
   - Обсяг: **348 файлів** (77 блоків, 38 секцій, 121 сніпет, 88 ассетів, 15 шаблонів, 5 локалей).
   - Валідація: **100% Strict Liquid PASS** (`260 file(s) checked, 0 problem(s)` у `local-storefront check`).
2. **Офлайн-рантайм `LocalStorefrontManager`**:
   - Розташування: [`services/dnk_shopify/runtime/local_storefront.py`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS/services/dnk_shopify/runtime/local_storefront.py).
   - Швидкість: **1.2 – 2.5 мс** на повний рендер сторінок; WebSocket live-reload (10 ms feedback).
   - Інтеграція: CLI команди `lsf-*` та 5 FastMCP інструментів для автономних агентів.
3. **Агент-компаньйон `DNK-ThemeCraft`**:
   - Розташування: [`services/dnk_shopify/companion/`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS/services/dnk_shopify/companion/).
   - База знань: граф таксономії на 7.3 МБ, 30 ранжованих золотих молекул, специфікації Shopify 2026-10.
4. **Автоматичні тести якості**:
   - `services/dnk_shopify/tests/`: **16/16 тестів пройдено успішно** (`test_brick.py` + `test_local_storefront.py`).

### 2.2. Ідентифіковані інженерні розриви (Gaps to Close):
| Область | Поточний стан у `DNK_OS` | Цільовий рівень для Theme Store | Необхідна дія |
|---|---|---|---|
| **Theme Blocks 2.0** | 77 блоків у `blocks/` | **200–220 блоків** (покриття Sugar + Story) | Додати відсутні атоми (Lookbook піни, Mega-Menu таби, Comparison tables) |
| **Сніпети Максима** | Частково інтегровано | **166 авторських сніпетів** (`dnk-ecom-sections`) | Перенести сніпети `auto-add-gifts`, `fomo`, `delivery-date` в `snippets/` з `t:` ключами |
| **Mega Menu** | 1 стандартне меню | **8 комерційних типів Mega Menu** (з Ella 7.3.1) | Створити секцію `header-mega-menu.liquid` з табами, брендами та товарами |
| **Advertorial / Pre-lander** | Тільки стандартні сторінки | **Чистий лейаут `landing.liquid`** (з Elixir) | Створити безхедерний конверсійний лейаут для D2C реклами |
| **WCAG 2.1 AA** | Базова доступність | **100% клавіатурна навігація + ARIA Live** | Перевірити TrapFocus у всіх діалогах, кнопки закриття дроверів, контрасти |

---

## 🧬 3. СИНТЕЗ 10 СУПЕРСИЛ ДОНОРІВ У DNK-ECOM

Кожен донорський worktree надає критичну інженерну молекулу для нашої теми:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DNK-ECOM THEME STORE CORE                                   │
├───────────────────────────────┬───────────────────────────────┬─────────────────────────────┤
│ 1. Sugar 2.3.15               │ 2. Shrine Pro 2.0.0           │ 3. Story 4.0.9              │
│ • 12-col custom-columns       │ • Cart Drawer V2              │ • Lookbook з пінами         │
│ • media-sizes-scope (LCP)     │ • Tiered Free Gifts Bar       │ • Журнальний Parallax       │
│ • stylesheet-once (INP)       │ • Sticky Cart Trigger         │ • uk.schema.json парність   │
│ • [data-dnk-animating] (CLS)  │ • Апсейли в кошику            │ • Реактивні картки авторів  │
├───────────────────────────────┼───────────────────────────────┼─────────────────────────────┤
│ 4. Ella 7.3.1                 │ 5. Casaio 1.1.0               │ 6. Elixir 1.6.2 / 2.0       │
│ • 8 типів Mega Menu           │ • Quantity Breaks v2 (Tiers)  │ • Advertorial сайдбар       │
│ • Ajax Faceted Filters        │ • UGC каруселі та Lumin       │ • Comparison Table          │
│ • Wholesale Quick Order       │ • Інтерактивні таби           │ • Чистий landing.liquid     │
├───────────────────────────────┼───────────────────────────────┼─────────────────────────────┤
│ 7. Ascendify 2.10.0           │ 8. KS-Origin 1.1.0            │ 9. Tinker 4.5.0             │
│ • Super-PDP матриці           │ • Семантичний HTML5 <dialog>  │ • Horizon 3-рівневі токени  │
│ • Live Visitors каунтер       │ • storefront-events.js        │ • settings_schema.json SSOT │
│ • Before / After слайдери     │ • 0 KB стороннього JS         │ • Vanilla customElements    │
├───────────────────────────────┴───────────────────────────────┴─────────────────────────────┤
│ 10. DNK-Ecom-Sections (Власні напрацювання Максима — 166 авторських конверсійних сніпетів)  │
│ • auto-add-gifts   • cart-checkpoints-bar   • bundle-offer   • delivery-date                │
│ • dnk-shipping-estimator   • cart-fomo-block   • buy-more-discounts   • blinking-shipping   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 4. ЖОРСТКІ ІНВАРІАНТИ SHOPIFY THEME STORE ($350–$420 MSRP)

Для гарантованого проходження офіційної перевірки тема повинна суворо відповідати 7 критеріям:

### 4.1. Zero-Framework Policy (100% Web Components)
- **Заборонено:** jQuery, Alpine.js, React, Vue, Lodash, Axios.
- **Обов'язково:** Тільки нативні класи `HTMLElement` з реєстрацією через `customElements.define()`:
  ```javascript
  class DNKCartDrawer extends HTMLElement {
    connectedCallback() {
      this.initEvents();
    }
    disconnectedCallback() {
      this.cleanupEvents();
    }
  }
  customElements.define('dnk-cart-drawer', DNKCartDrawer);
  ```

### 4.2. 100% Theme Blocks 2.0 (Nestability & Context)
- Усі секції містять тег `{% content_for 'blocks' %}`.
- Підтримка блоків додатків через `@app`.
- Передача контексту товару/колекції в глибину до 8 рівнів через об'єкт `closest`:
  ```liquid
  {% content_for 'blocks', closest.product: _product %}
  ```

### 4.3. Core Web Vitals (90+ Green на Mobile)
- **LCP < 1.8s:**
  - Обов'язкове використання снипету `media-sizes-scope.liquid`, який ділить `100vw` на кількість колонок сітки на рівні Liquid (економія 70–85% ваги медіа).
  - Атрибути `loading="eager"` та `fetchpriority="high"` для головного банера та зображення товару в перших 2 секціях.
- **CLS = 0:**
  - Фіксовані `aspect-ratio` для всіх медіа-контейнерів до завантаження картинки.
  - Атрибут `[data-dnk-animating]` під час розгортання акордеонів/дроверів (запобігає ламанню `border-radius`).
- **INP / TBT < 150ms:**
  - Дедуплікація підключень CSS через `stylesheet-once.liquid` (видаляє дублікати `<link>` при 40+ однакових блоках на сторінці).

### 4.4. 100% Міжнародна локалізація (i18n)
- **Жодного захардкодженного англійського чи українського слова** у Liquid/JS файлах.
- Кожен рядок виводиться через фільтр: `{{ 'cart.general.free_shipping' | t }}`.
- Повна симетрична парність між `locales/en.default.json` та `locales/uk.json`.

### 4.5. Ліміти платформи Shopify (Platform Quota Guards)
- **Шаблони:** Розмір кожного файлу `templates/*.json` $\le 512\text{ KB}$ (цільовий $\le 300\text{ KB}$).
- **Секції:** Розмір коду однієї секції $\le 25\text{ KB}$.
- **Блоки:** Загальна кількість зареєстрованих блоків у темі $\le 300$.

### 4.6. Zero-DRM & Zero-Telemetry
- 0 байт викликів до сторонніх серверів ліцензування (`sugarthe.me`, `shrinesolutions.com`, Clerk).
- Повний Cleanroom. Ліцензування виконується виключно внутрішніми механізмами Shopify Theme Store.

### 4.7. Доступність (WCAG 2.1 Level AA)
- Фокус-пастки (`TrapFocus`) у всіх модальних вікнах, меню та кошику-дровері.
- Закриття по клавіші `Escape`, керування табами через стрілки клавіатури.
- Кольоровий контраст тексту до фону не менше **4.5:1**.

---

## 🏗️ 5. АНАТОМІЯ ДИРЕКТОРІЙ ТА СТРУКТУРА ТЕМИ DNK-ECOM

Цільова структура файлів теми `themes/dnk-ecom` (або `services/dnk_shopify/DNK_Sovereign_Apex/`):

```
DNK-Ecom Theme (Theme Store Grade)/
├── assets/                          # Web Components, CSS токени, оптимізовані SVG
│   ├── dnk-tokens.css               # Horizon 3-рівневі токени (Fluid typography, колірні схеми)
│   ├── dnk-base.css                 # Скидання стилів, доступність, flex/grid сітки
│   ├── dnk-core.js                  # Реактивне ядро та Cart State Observer
│   ├── dnk-cart-drawer.js           # Cart Drawer V2, Tiered Rewards, Quick Add
│   ├── dnk-pdp.js                   # Галерея, селектор варіантів, Volume Pricing, Sticky ATC
│   ├── dnk-mega-menu.js             # 8 типів інтерактивного меню з табами (Ella)
│   ├── dnk-quiz.js                  # Multi-step Quiz Engine без сторонніх додатків
│   └── dnk-animations.css           # GPU-прискорені анімації на [data-dnk-animating]
├── blocks/                          # 200–220 Атомарних Theme Blocks 2.0
│   ├── pdp/                         # Блоки картки товару (ціна, свотчі, бандли, sticky bar)
│   ├── cart/                        # Блоки кошика (прогрес-бар, апсейли, нотатки, бейджі)
│   ├── layout/                      # Блоки розмітки (custom-columns, контейнери, відступи)
│   ├── editorial/                   # Контентні атоми (lookbook піни, timeline, comparison table)
│   └── cro/                         # Віджети довіри (before/after, гарантії, live visitors)
├── sections/                        # 35–40 Високомодульних секцій-контейнерів
│   ├── main-product.liquid          # Головний PDP-канвас (приймає будь-які блоки)
│   ├── custom-columns.liquid        # 12-колонковий універсальний конструктор
│   ├── main-cart-drawer.liquid      # Cart Drawer V2 з прогрес-баром подарунків
│   ├── header.liquid                # Хедер з підтримкою 8 типів Mega Menu
│   ├── lookbook-showcase.liquid     # Журнальний Lookbook з інтерактивними пінами
│   └── ...
├── snippets/                        # Легковажні ізольовані макроси та 166 сніпетів Максима
│   ├── media-sizes-scope.liquid     # Розрахунок responsive sizes на рівні Liquid (Sugar)
│   ├── stylesheet-once.liquid       # Дедуплікація підключення стилів блоків
│   ├── auto-add-gifts.liquid        # Авторський сніпет автододавання подарунків
│   ├── cart-checkpoints-bar.liquid  # Авторська шкала чекпоінтів у кошику
│   ├── dnk-shipping-estimator.liquid# Калькулятор вартості доставки
│   └── ...
├── config/                          # Схема та 3 комерційні демо-пресети
│   ├── settings_schema.json         # Валідована схема налаштувань редактора Shopify
│   └── settings_data.json           # 3 пресети: Apex D2C, High-SKU Mega, Luxury Story
├── layout/                          # Мастер-лейаути
│   ├── theme.liquid                 # Головний лейаут магазину
│   ├── password.liquid              # Сторінка захисту паролем
│   └── landing.liquid               # Безхедерний конверсійний лейаут для Advertorials
└── locales/                         # 100% Симетрична локалізація
    ├── en.default.json              # Базовий англійський переклад
    └── uk.json                      # Повний український переклад
```

---

## 🛠️ 6. ПОКРОКОВИЙ ПЛАН ПОБУДОВИ ТА ВПРОВАДЖЕННЯ ТЕМИ В DNK_OS

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Розробник / Агент
    participant Mirrow as Донорські Worktrees
    participant Apex as DNK_Sovereign_Apex
    participant LSF as LocalStorefront (Rust)
    participant Cert as 7-Gate Integrity

    Dev->>Mirrow: 1. Молекулярне вилучення компонентів (Sugar, Shrine, Story, Ella, Elixir)
    Dev->>Apex: 2. Санітизація коду, заміна класів на dnk-*, видалення DRM
    Dev->>Apex: 3. Інтеграція 166 авторських сніпетів Максима
    Dev->>LSF: 4. Офлайн-перевірка Liquid: npx local-storefront check (0.2 ms)
    LSF-->>Dev: 5. 0 errors, Strict Liquid сумісність підтверджена
    Dev->>Cert: 6. Прогін 7 воріт якості: just shopify-7gate
    Cert-->>Dev: 7. 100% CLEAN & PROTECTED (Exit Code 0)
    Dev->>Apex: 8. Пакування релізного ZIP-архіву для подачі в Theme Store
```

### Етап 1: Графтинг відсутніх блоків (доведення кількості до 200+)
- **З Sugar:** перенести повний набір блоків `custom-columns` (контейнери, відступи, колонки сітки).
- **З Story:** перенести Lookbook-піни (`lookbook-pin.liquid`) та паралакс-блоки.
- **З Shrine Pro:** доповнити Cart Drawer блоками `cart-rewards` та `cart-upsell`.
- **З Ella:** перенести 8 типів розмітки Mega Menu та асинхронні фасетні фільтри.
- **З Elixir:** перенести блоки `comparison-table` та сайдбар відгуків.
- **З Ascendify:** перенести віджети `before-after-slider`, `live-visitors`, `guarantee-badge`.

### Етап 2: Інтеграція 166 авторських сніпетів Максима (`dnk-ecom-sections`)
- Перенести всі 166 конверсійних сніпетів у `snippets/`.
- Перейменувати на системний префікс `dnk-*` для уникнення колізій.
- Замінити будь-який прямий текст на ключі `t:` з автоматичним додаванням перекладів в `en.default.json` та `uk.json`.

### Етап 3: Доведення доступності до стандарту WCAG 2.1 AA
- Забезпечити роботу TrapFocus у Web Component `dnk-modal-dialog` та `dnk-cart-drawer`.
- Додати атрибути `aria-live="polite"` для динамічних оновлень кошика та повідомлень про додавання товару.

### Етап 4: Автоматизована сертифікація та прогін у DNK_OS
- Виконати перевірку синтаксису через `just shopify-lsf-check`.
- Запустити профайлер рендерингу: `npx local-storefront profile /` (переконатися, що жодна секція не рендериться довше 10 мс).
- Запустити 7-Gate перевірку: `just shopify-7gate`.
- Сформувати фінальний релізний ZIP: `DNK_Ecom_Theme_Store_Ready_v1.0.0.zip`.

---

## 🏁 7. ВИСНОВОК ТА КРИТЕРІЙ ГОТОВНОСТІ ДО ПРОДАЖУ

Тема **`DNK-Ecom`** вважається готовою до подання на розгляд модераторів **Shopify Theme Store** за виконання наступних умов:
1. `npx local-storefront check` повертає **0 problem(s)**.
2. `shopify theme check --strict` повертає **0 errors, 0 warnings**.
3. Google Lighthouse Mobile Performance $\ge 90$ на сторінці товару та головній вітрині.
4. Усі шаблони $\le 350\text{ KB}$, жодна секція не перевищує $25\text{ KB}$.
5. 0 байт сторонніх мережевих запитів, повна автономність та ліцензування через Shopify Partner Dashboard.
