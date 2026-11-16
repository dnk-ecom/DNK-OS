---
name: shopify-theme-craft-companion
description: Use when auditing, sanitizing, extracting, or validating commercial Shopify themes ($350-$420 MSRP) with Theme Blocks 2.0 and Web Components.
version: 2.0.0
---

# --- DNK-MRH-HEADER ---
# mrh_id: "_Shopify_Theme_DEV_Workflow/companion/SKILL.md"
# purpose: "Comprehensive Skill Definition for Shopify Theme Architect Companion (DNK-ThemeCraft v2.0.0)"
# canonical_source: true
# alters_files: ["blocks/dnk-*.liquid", "sections/dnk-*.liquid", "snippets/dnk-*.liquid", "assets/dnk-*.js", "assets/dnk-*.css"]
# triggers_tasks: ["shopify-ast-audit", "cleanroom-sanitizer", "atomic-component-extractor", "theme-store-validator"]
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym Kuzmenko & Gerych-root / Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

# 🛠️ Навичка: Shopify Theme Architect Companion (`DNK-ThemeCraft` v2.0.0)

Ця навичка перетворює автономного агента (на базі Google Gemini 4 Carbon або Claude Opus) на головного інженера-архітектора комерційних тем Shopify найвищого ґатунку ($350–$420 MSRP), інтегрованого в ядро **DNK OS** (`ws-alpha-001`).

---

## 🧭 1. Спеціалізовані суб-навички (Core Capabilities)

### 1.1. `shopify-ast-audit` (Глибокий синтаксичний парсинг Liquid & JSON)
* **Призначення:** Детермінований аналіз структури шаблонів, секцій, блоків та снипетів на рівні абстрактного синтаксичного дерева (AST) усіх 14 воркплейсів-донорів.
* **Алгоритм та правила перевірки:**
  1. **Попереднє очищення коментарів (Comment-Stripping Invariant):** Перед пошуком директив обов'язково видаляти блоки `{% comment %}...{% endcomment %}` та інлайн-коментарі `{% # ... %}`, щоб уникнути хибних спрацьовувань на задокументовані приклади (як у `blocks/_slide.liquid` чи `blocks/_tab.liquid`).
  2. **Аудит застарілих тегів та фільтрів Liquid:**
     - Повна заборона `{% include %}` $\to$ заміна виключно на ізольований `{% render 'snippet', var: val %}`.
     - Повна заборона `{{ ... | img_url }}` $\to$ заміна на `{{ ... | image_url: width: ... | image_tag }}`.
  3. **Топологія Theme Blocks 2.0 та вкладеності:**
     - Класифікація файлів у `blocks/*.liquid` на **Атоми** (листові блоки без вкладеності), **Молекули** (складені функціональні блоки з контекстом `closest.*`) та **Організми/Контейнери** (блоки, що викликають `{% content_for 'blocks' %}` або статичний `{% content_for 'block', type: '...', id: '...' %}`).
     - Перевірка глибини вкладеності: до **8 рівнів** для динамічних `content_for 'blocks'` та до **2 рівнів** рекурсії для статичних блоків.
     - Перевірка контекстної прив'язки ресурсів через `closest.product`, `closest.collection`, `closest.article` із безпечним ланцюжком фолбеків:
       `{% liquid assign product_resource = closest.product | default: product | default: section.settings.product %}`.
  4. **Валідація JSON-схем (`{% schema %}`):**
     - Сувора відповідність RFC 8259 (відсутність trailing commas та коментарів).
     - Перевірка наявності `{"type": "@theme"}` та `{"type": "@app"}` у масиві `blocks` секцій для повної сумісності з Shopify App Extensions.
     - Валідація умов видивості `visible_if`: довжина $\le 250$ символів, дозволені лише оператори `==`, `!=`, `and`, `or` (заборонені `>`, `<`, `>=`, `<=`, дужки `()` та застосування на `product`/`collection`/`page`/`blog`/`article` пікерах).
     - Валідація `range` налаштувань: не більше **101 кроку** (`(max - min) / step <= 101`).
     - Перевірка розміщення `"category"`: виключно всередині об'єктів масиву `"presets"`, ніколи на верхньому рівні `{% schema %}`.
  5. **Контроль квот (512KB Quota Guard):**
     - Шаблони `templates/*.json` та `sections/*.json` $\le 512\text{ KB}$ (жорсткий ліміт платформи), комерційний цільовий поріг DNK $\le 350\text{ KB}$.
     - Liquid-файл секції $\le 25\text{ KB}$, максимум 300 файлів у `blocks/` на тему, максимум 20 section groups.

---

### 1.2. `cleanroom-sanitizer` (Санація від DRM, ліцензійних замків та сторонніх трекерів)
* **Призначення:** Забезпечення 100% юридичної та технічної чистоти коду (Track-2 Cleanroom Standard) перед графтингом будь-якого компонента з донорів.
* **Матриця відомих загроз донорів та їх нейтралізація:**
  1. **Sugar (`sugar`):**
     - *Загроза:* Телеметрія в `assets/global.js` (~рядок 3802) до `https://Check.Sugarthe.me/check` з відправкою `window.Shopify.shop`, версії та ролі теми; документаційні посилання `app.sugarthe.me/icons` у `{% schema %}`; штампи релізу `{% # sugar:<path>@<release> %}` на рядку 1.
     - *Санація:* Повне видалення мережевого пінгу `Check.Sugarthe.me/check`, очищення штампів релізу, заміна посилань іконок на локальний каталог `snippets/dnk-icon.liquid`, трансформація атрибутів `data-_sf` / `data-sugar-animating` у `data-dnk-id` / `data-dnk-animating`.
  2. **Shrine Pro (`shrine-pro`):**
     - *Загроза:* Активний DOM-wiping DRM у `assets/global.js` (`shrinesolutions.com/api/verify`, `validLicense`), який виконує `document.body.innerHTML = ''`, та секція перевірки `sections/main-Verification.liquid`.
     - *Санація:* Повне видалення `sections/main-Verification.liquid`, вирізання класів перевірки ліцензії з JS, ізоляція CRO-віджетів у чисті W3C Custom Elements.
  3. **Elixir (`elixir`):**
     - *Загроза:* Дворівневий DRM (`elixirtheme.com/api/v1/license/verify`), ECDSA-сторож `head-bootstrap.js`, обфусковані `eval()` / `atob()` пейлоади та блокувальний оверлей `.sw-fr`.
     - *Санація:* Використання виключно очищених шаблонів розмітки з `_Shopify_Theme_Audit_Workflow/distilled_vault/elixir-1.6.2/` (наприклад, `blocks/listicle-item.liquid`, `cs-amazon-reviews.liquid`) із підключенням до нативного ядра `assets/dnk-core.js`.
  4. **Сторонні трекери та зовнішні CDN:**
     - Повне видалення хардкод-викликів `fbq()`, `ttq.`, `gtag()`, Klaviyo/Hotjar скриптів (делегування виключно нативному Shopify Customer Events API).
     - Заміна будь-яких зовнішніх CDN (`cdn.jsdelivr.net`, `unpkg.com`, `cdnjs.cloudflare.com`) на локальні автономні модулі в `assets/dnk-*.js`.

---

### 1.3. `atomic-component-extractor` (Перетворення сторонніх блоків у стандарт `dnk-*`)
* **Призначення:** Молекулярна екстракція найкращих блоків, секцій та снипетів із 14 воркплейсів-донорів та їх конвертація в єдиний стандарт `dnk-*`.
* **5-етапний конвеєр трансформації:**
  1. **Канонізація неймспейсу:**
     - Перейменування файлів: `blocks/dnk-<slug>.liquid`, `sections/dnk-<slug>.liquid`, `snippets/dnk-<slug>.liquid`, `assets/dnk-<slug>.js`, `assets/dnk-<slug>.css`.
     - Заміна CSS-класів: `.sugar-*`, `.shrine-*`, `.story-*`, `.elixir-*`, `.cs-*` $\to$ `.dnk-*`.
     - Реєстрація Web Components: `customElements.define('dnk-<slug>', DNKComponentClass)`.
  2. **Нормалізація CSS-токенів (3-рівнева топологія `--dnk-*`):**
     - *Рівень 1 (Global Brand Primitives у `:root` / `assets/dnk-tokens.css`):* `--dnk-font-heading`, `--dnk-font-body`, `--dnk-page-width`, `--dnk-radius-sm`, `--dnk-radius-md`, `--dnk-radius-lg`, `--dnk-space-unit`.
     - *Рівень 2 (Scoped Color Schemes `.color-{{ section.settings.color_scheme }}`):* `--dnk-color-bg`, `--dnk-color-surface`, `--dnk-color-fg`, `--dnk-color-fg-muted`, `--dnk-color-accent`, `--dnk-color-border`.
     - *Рівень 3 (Component-Local Inline Properties):* Приватні інлайн-змінні з префіксом підкреслення `style="--_gap: {{ block.settings.gap }}px; --_cols-desktop: {{ block.settings.columns_desktop }};"` на кореневому тезі компонента замість інлайн-блоків `<style>`.
  3. **Семантична прив'язка анімацій:**
     - Заміна крихких селекторів за інлайн-стилями (`[style*="overflow"]`) на уніфікований атрибут `[data-dnk-animating]`, який встановлюється на час переходу (`transitionend` / Web Animations API).
  4. **Інтеграція Core Web Vitals макросів:**
     - Обов'язкове підключення `snippets/dnk-media-sizes-scope.liquid` для точного розрахунку атрибута `sizes` у вкладених блоках та сітках.
     - Дедуплікація CSS через `{% render 'dnk-stylesheet-once', asset: 'dnk-component.css' %}` або стандартний `{{ 'dnk-component.css' | asset_url | stylesheet_tag }}`.
  5. **Реактивна шина подій (Storefront Event Bus):**
     - Синхронізація кошика, селектора варіантів, бандлів та квізів через легковаговий Pub/Sub (`dnk:variant:change`, `dnk:cart:add`, `dnk:cart:refresh`, `dnk:modal:open`) за зразком `ks-origin/assets/storefront-events.js` та `sugar` `SugarPricing`.

---

### 1.4. `theme-store-validator` (Валідатор відповідності правилам Shopify Theme Store)
* **Призначення:** Фінальний передрелізний контроль якості перед подачею теми на офіційну модерацію Shopify Theme Store ($350–$420 MSRP).
* **Критерії сертифікації:**
  - **0% сторонніх JS-фреймворків:** Відсутність jQuery, Alpine.js, React, Vue, GSAP у вітрині; 100% нативні W3C Custom Elements, `<dialog>`, `<details>/<summary>`, CSS `scroll-snap`.
  - **Core Web Vitals 90+ Green:** Mobile Performance $\ge 90$, Accessibility $\ge 95$ (WCAG 2.1 AA), $\text{LCP} < 1.8\text{s}$ (`fetchpriority="high" loading="eager"` лише для `section.index == 1`), $\text{CLS} = 0$ (`< 0.05`), $\text{INP} < 120\text{ms}$.
  - **100% двомовна локалізація (i18n):** Усі видимі рядки вітрини та мітки `{% schema %}` використовують ключі `t:` із повним покриттям у `locales/en.default.json` + `locales/uk.json` та `locales/en.default.schema.json` + `locales/uk.schema.json`.
  - **Цілісність пресетів та схем:** Перевірка всіх `templates/*.json` та `sections/*.json` на входження значень `range` у межі `[min, max]` із кратністю `step`, а також наявність кожного дочірнього блоку в `blocks` allowlist батьківського контейнера.

---

## 🚀 2. Протокол виконання місій (Execution Protocol)

1. **Фаза розвідки та аудиту (`shopify-ast-audit`):**
   - Запустити `python3 ./companion_distiller.py --scan` або перевірити індекс `./GOLDEN_MOLECULES_INDEX.json` та матрицю `./KNOWLEDGE_BASE_SHOPIFY_STANDARDS.md`.
2. **Фаза санації та екстракції (`cleanroom-sanitizer` + `atomic-component-extractor`):**
   - Вилучити цільову молекулу з донора, очистити від DRM/телеметрії, нормалізувати префікси у `dnk-*` та токени у `--dnk-*`.
3. **Фаза верифікації (`theme-store-validator`):**
   - Перевірити JS-файли через `node --check <file.js>`.
   - Перевірити JSON-схеми та ліміт 512 KB через `python3 ./shopify_knowledge_indexer.py` та `shopify theme check`.
   - Зафіксувати 64-символьний SHA-256 хеш у `./GOLDEN_MOLECULES_INDEX.json`.
