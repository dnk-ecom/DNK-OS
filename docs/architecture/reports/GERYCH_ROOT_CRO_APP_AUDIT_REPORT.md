---
title: "Gerych-Root Всебічний Технічний Аудит: `Omar92953/the-ultimate-cro-app` (CRO Toolbox)"
description: "Comprehensive Technical Audit of Omar92953/the-ultimate-cro-app comparing local commit 7ea1589 against upstream 5819cf4/6c6bb3f and evaluating architectural gaps against DNK OS / DNKEcom."
mrh_id: "docs/architecture/reports/GERYCH_ROOT_CRO_APP_AUDIT_REPORT.md"
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
> mrh_id: "docs/architecture/reports/GERYCH_ROOT_CRO_APP_AUDIT_REPORT.md"
> purpose: "Comprehensive Technical Audit of Omar92953/the-ultimate-cro-app comparing local commit 7ea1589 against upstream 5819cf4/6c6bb3f and evaluating architectural gaps against DNK OS / DNKEcom."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 Gerych-Root Всебічний Технічний Аудит: `Omar92953/the-ultimate-cro-app` (CRO Toolbox)

> **Інженерний вердикт:** Між нашою локальною ревізією `7ea15893c2892029dc7446ed4ebacd317dd48476` та апстрімом `5819cf4a71d2baa97e1aa0e915d618cc55691685` (98 комітів; або 100 комітів включно з найсвіжішим `origin/main` `6c6bb3fd2a929ed75c82be2cc53659e2a1010a2f`) репозиторій **CRO Toolbox** пройшов шлях від функціонального MVP до бойового продукту, загартованого реальними ревізіями **Shopify App Store Review (вимоги 2.1.1, 2.3.1, 4.3, 5.1.4, 5.6.1, 5.8.7)**. Ключовий архітектурний зсув порівняно з нашим первинним аудитом (`098_the_ultimate_cro_app_sota_assimilation_audit.md`) — перехід від чистої концепції «Zero-DB» до **Гібридної Двоконтурної Архітектури Стану (Hybrid Dual-Plane Storage)**: нульова затримка SSR на вітрині через `$app:*` Metaobjects/Metafields + 26 операційних таблиць у Prisma (SQLite/PostgreSQL із увімкненим Supabase RLS) для фонових розкладів, лояльності, трекінгу, білінгу та статистичного A/B/C/D тестування.

---

## 📊 1. Зіставлення стану репозиторію (`HEAD` vs `origin/main`)

| Параметр | Локальний клон (`DNKEcom`) | Цільовий апстрім завдання (`5819cf4`) | Актуальний `origin/main` (15.11.2026) |
|---|---|---|---|
| **Шлях (Relative)** | `../DNKEcom/GitHub_Shopify_Apps/the-ultimate-cro-app` | `origin/main` (PR #385) | `origin/main` (PR #387) |
| **Повний 40-char Commit SHA** | `7ea15893c2892029dc7446ed4ebacd317dd48476` | `5819cf4a71d2baa97e1aa0e915d618cc55691685` | `6c6bb3fd2a929ed75c82be2cc53659e2a1010a2f` |
| **Дата коміту** | 2026-10-27 (PR #328) | 2026-11-13 19:31:51 +0200 (PR #385) | 2026-11-14 13:53:12 +0200 (PR #387) |
| **Дистанція від локального `HEAD`** | Базова точка (0 комітів) | **+98 комітів попереду** | **+100 комітів попереду** |
| **Масштаб змін (`git diff --stat`)** | — | **232 файли змінено** (`+4,025` / `-676` рядків) | **235 файлів змінено** (`+4,136` / `-679` рядків) |
| **Кількість моделей Prisma** | 25 моделей | **26 моделей** (`+OfferSchedule`) | **26 моделей** (`+OfferSchedule`) |
| **Shopify App Version** | `cro-toolbox-40+` | `cro-toolbox-80` | `cro-toolbox-80+` |
| **Ліцензійний трек DNK OS** | `UNLICENSED` (Track 2 Clean-Room) | `UNLICENSED` (Track 2 Clean-Room) | `UNLICENSED` (Track 2 Clean-Room) |

### Що додано у 2 фінальних комітах понад `5819cf4` (`5819cf4..6c6bb3f`):
1. **`3a9657fc8b91de60e121eb51fa124fdbd3bcfc95` (PR #386 — `app/components/ErrorPage.tsx`, `app/routes/app.tsx`)**: Автоматичне одноразове перезавантаження даних маршруту (`useRevalidator`) при тимчасовому збої (наприклад, коли токен сесії Shopify запізнився у фоновій вкладці), з обмеженням не частіше 1 разу на 60 секунд через `sessionStorage` та логуванням реальної помилки в консоль браузера.
2. **`6c6bb3fd2a929ed75c82be2cc53659e2a1010a2f` (PR #387 — `site/src/content/blog/back-in-stock-alerts-shopify.md`)**: Новий SEO-гайд по сповіщеннях про появу товару в наявності (Back-in-Stock Alerts) та оновлення журналу дистрибуції (`docs/outreach/posted.md`).

---

## 🧭 2. Порівняння нової версії апстріму з планами DNK OS / DNKEcom

Наш первинний аудит (`./docs/notes/sota_audits/098_the_ultimate_cro_app_sota_assimilation_audit.md` та `./docs/tech/sota_assimilation/SOTA_THE-ULTIMATE-CRO-APP_ASSIMILATION.md`, зафіксований 2026-10-19) описував архітектуру станом на ранню версію (`cro-toolbox-35+`). Зіставлення наших припущень і поточних модулів `./services/dnk_shopify` із реальною еволюцією апстріму виявляє наступні зміни:

| Архітектурний вимір | Що було зафіксовано у планах DNK OS (`098_..._audit.md`) | Реальний стан в апстрімі (`5819cf4` / `6c6bb3f`) | Поточна імплементація у `./services/dnk_shopify` |
|---|---|---|---|
| **Модель збереження даних** | «Zero-Database Merchant Storage»: у Prisma лише `Session` та `McpGrant`; усі дані тільки в `$app:*` Metaobjects. | **Hybrid Dual-Plane Storage (26 таблиць Prisma)**: вітринні офери у `$app:*` Metaobjects, але розклади (`OfferSchedule`), перегляди A/B (`AbView`), лояльність (8 таблиць), трекінг (5 таблиць), повернення (`ReturnRequest`), білінг (`UsageExtra`, `UsageEvent`) живуть у Postgres із RLS. | Відсутній шар синхронізації між Prisma/SQLite та Shopify `$app:*` Metaobjects. |
| **Двигун A/B тестування** | Не деталізований у первинному звіті; у `./services/dnk_shopify/src/ab_engine.py` заплановано серверний SHA-256 бакетинг і Байєсівську оцінку. | **Клієнтсько-серверний A/B/C/D контур (до 4 версій)**: рендеринг усіх активних варіантів у Liquid SSR, миттєве приховування необраних у `theme/snippets/ucro-ab.liquid` з інтеграцією **Shopify Customer Privacy API**, запис атрибута кошика `_cro_ab`, підрахунок через двопропорційний **z-тест** (Abramowitz & Stegun 7.1.26). | `./services/dnk_shopify/src/ab_engine.py` містить Python-клас `ABTestEngine` (SHA-256 + Bayesian Monte-Carlo), але не має Liquid-сніпета з Customer Privacy API та прив'язки до `_cro_ab` у Shopify Function. |
| **Життєвий цикл оферів за часом** | Відсутній у первинному плані. | **Scheduled Offers Pro (`app/lib/schedule.ts`)**: IANA-таймзона магазину (`shop.ianaTimezone`), подвійний перерахунок DST-зсуву, UI-колесо часу (`TimeWheel.tsx`), фоновий воркер кожні 5 хв (`startSchedules()`), що викликає канонічні `saveRule`/`saveDeal`/`saveBundle`. | Не імплементовано у `./services/dnk_shopify`. |
| **Cart Validation Function** | Блокування голих бандлів (`_ucro_merged`) та базові min/max правила. | **Розділення етапів `buyerJourney.step` + мультивалютність**: мінімуми ігноруються на `CART_INTERACTION` (щоб не блокувати додавання першого товару в порожній кошик) і спрацьовують лише на чекауті; грошові ліміти масштабуються на `presentmentCurrencyRate`; додано третій контур — **Points Guard** (`checkPoints`). | Не імплементовано у `./services/dnk_shopify`. |
| **Post-Purchase Extension** | Базовий опис підпису JWT у `api.post-purchase.tsx`. | Виділені маршрути `api.post-purchase.offer.tsx` та `api.post-purchase.sign.tsx` із обов'язковим `loader = postOnlyLoader` для обробки CORS `OPTIONS` preflight у React Router 7 (вимога App Store 5.6.1) + діагностика `checkConnection()` з адмінки. | Відсутній шаблон CORS-безпечного React Router 7 loader/action для Post-Purchase. |
| **MCP Сервер та AI-інструменти** | 21 MCP-інструмент для оферів, бандлів та секцій. | Розширено інструментами трекінгу (`app/lib/mcp/tracking-tools.server.ts`: `get_tracking_setup`, `set_carrier_link`, `set_tracking_source`) + генератор першоособового промпту `trackingGuide(store)` для підключення будь-якого кур'єра без витоку секретного webhook URL. | Skill `./core/skills/the_ultimate_cro_app_assimilated/SKILL.md` помилково прив'язаний до `target_worker: "dnk_video_ai_creator"` замість `dnk_shopify`. |

---

## 🔬 3. Детальний технічний розбір оновлень апстріму (`7ea1589..5819cf4` / `6c6bb3f`)

### 3.1. Розклад оферів (Scheduled Offers Pro) з підтримкою таймзон магазину
* **Ключові файли**: `app/lib/schedule.ts`, `app/lib/schedule.server.ts`, `app/components/ScheduleCard.tsx`, `app/components/TimeWheel.tsx`, `prisma/migrations/20261107000000_offer_schedule/migration.sql`, `prisma/postgres/migrations/20261107000000_offer_schedule/migration.sql`, `test/app/schedule.test.ts`.
* **Архітектура та алгоритм**:
  1. **Таймзона магазину та захист від переходів на літній/зимовий час (DST)**: Функція `shopTimeZone(admin, shop)` запитує GraphQL-поле `shop { ianaTimezone }` і кешує його в пам'яті процесу (`Map<string, string>`). У `app/lib/schedule.ts` функція `toInstant(m: LocalMoment, timeZone: string)` переводить локальну дату (`YYYY-MM-DD`) і час (`HH:MM`) у `Date` (UTC) без зовнішніх бібліотек (zero-dependency `Intl.DateTimeFormat`). Щоб момент біля переходу DST потрапляв на правильний бік зсуву, обчислення `offsetMinutes()` виконується **двічі послідовно**:
     ```ts
     let at = new Date(guess - offsetMinutes(new Date(guess), timeZone) * 60_000);
     at = new Date(guess - offsetMinutes(at, timeZone) * 60_000);
     ```
     Також перевіряється `new Date(guess).toISOString().slice(0, 10) !== m.date`, що відсікає неіснуючі календарні дати (наприклад, `2026-04-31`).
  2. **Одноразові тригери (`startDone` / `endDone`)**: Модель `OfferSchedule` у Prisma має композитний первинний ключ `@@id([shop, type, handle])` (де `type` — `"rule" | "deal" | "bundle"`) та прапорці `startDone` і `endDone`. Фоновий планувальник `startSchedules()` запускається кожні 5 хвилин (`5 * 60_000` мс) і перемикає статус офера (`active: true` на старті, `active: false` на завершенні) **рівно один раз**. Завдяки цьому, якщо мерчант вручну вимкне або увімкне офер посеред запланованого вікна, планувальник не перезапише його ручний вибір на наступному 5-хвилинному тіку.
  3. **Канонічний пайплайн збереження**: `setActive()` у `schedule.server.ts` не змінює метаполя напряму в обхід бізнес-логіки, а викликає ті самі функції, що й UI-редактори (`saveRule`, `saveDeal`, `saveBundle`), автоматично оновлюючи конфігурацію Shopify Discount Function (`$app:discounts.config`) та вітринні `$app:*` метаоб'єкти.
  4. **UI/UX (`TimeWheel.tsx` та `ScheduleCard.tsx`)**: Замість довгого випадаючого списку на 48 пунктів створено компонент `TimeWheel` із двома незалежними барабанами прокрутки (години `00..23` та хвилини з кроком 5 хв `00..55`, висота рядка `ROW = 28px`, дебаунс скролу `120ms` та клавіатурна навігація `ArrowUp`/`ArrowDown`). У PR #351 (`6d718d6`) виправлено прив'язку перемикачів `Switch` до збережених значень (`checked={!!value.start}`), щоб кнопка `Discard` у Shopify SaveBar коректно скидала стан форми.

### 3.2. Розширене A/B тестування до 4 версій (A/B/C/D) зі статистичним z-тестом
* **Ключові файли**: `app/lib/ab-tests.ts`, `app/lib/ab-tests.server.ts`, `app/components/AbResults.tsx`, `app/routes/app.offers.tests.tsx`, `theme/snippets/ucro-ab.liquid`, `theme/blocks/ucro-upsell.liquid`, `theme/blocks/ucro-cross-sell.liquid`, `test/app/ab-tests.test.ts`.
* **Архітектура та математична модель**:
  1. **Структура даних зі зворотною сумісністю**: У `AbTest` збережено поле `b: AbOverrides` для версії B і додано опціональний масив `more?: AbOverrides[]` для версій C та D (`AB_GROUPS = ["A", "B", "C", "D"]`). Функція `functionAb(test, rule)` записує C і D у поле `v: { C: ..., D: ... }` конфігурації знижок лише тоді, коли вони реально присутні, не роздуваючи JSON метаполя для звичайних A/B тестів.
  2. **SSR + Consent-First клієнтський розподіл (`theme/snippets/ucro-ab.liquid`)**:
     - Liquid рендерить у DOM усі активні варіанти офера (`data-ab="<testId>" data-ab-g="A|B|C|D"`), де варіанти B/C/D мають атрибут `hidden`.
     - Інлайн-скрипт `ucro-ab.liquid` виконується синхронно одразу після блоку: читає `localStorage.getItem('ucs-ab-' + id)`, видаляє з DOM (`parentNode.removeChild`) усі необрані варіанти та знімає `hidden` із обраного варіанту ще до старту скриптів офера (0 CLS / 0 миготіння).
     - **Інтеграція з Shopify Customer Privacy API**: До отримання згоди на аналітику (`window.Shopify.customerPrivacy.analyticsProcessingAllowed()`) покупець завжди бачить контрольну версію `A`, жодні дані не пишуться в `localStorage` чи кошик. Після надання згоди (`visitorConsentCollected`) випадково обирається група з `'ABCD'.slice(0, n)`, синхронізується в атрибут кошика `_cro_ab` (`<testId>:<group>`) через `/cart/update.js` і раз на добу відправляє beacon на `/apps/ucro/ab`. Якщо покупець відкликає згоду, функція `forget()` очищує всі ключі `ucs-ab-*` у `localStorage`.
  3. **Двопропорційний статистичний z-тест (`compareVersions` у `app/lib/ab-tests.ts`)**:
     - Захист від передчасних висновків (Anti-Peeking Guard): поки кожна група не набере мінімум **`MIN_VIEWS = 100`** переглядів, а сумарна кількість замовлень по всіх групах не досягне **`MIN_ORDERS = 10`**, вердикт завжди `"wait"` (`leader: null, sure: null`).
     - Усі варіанти ранжуються за конверсією в замовлення (`rate = orders / views`). Найкращий варіант (`best`) порівнюється з **другим найкращим (`next`)** за допомогою двопропорційного z-тесту:
       $$p_{\text{pooled}} = \frac{\text{orders}_x + \text{orders}_y}{\text{views}_x + \text{views}_y}, \quad SE = \sqrt{p_{\text{pooled}}(1 - p_{\text{pooled}})\left(\frac{1}{\text{views}_x} + \frac{1}{\text{views}_y}\right)}, \quad z = \frac{r_x - r_y}{SE}$$
     - Нормальний розподіл `normalCdf(z)` обчислюється поліноміальною апроксимацією **Абрамовіца і Стегуна (формула 7.1.26)** з точністю $7.5 \times 10^{-8}$. Достовірність: $\text{sure} = \text{round}((1 - 2(1 - \Phi(|z|))) \times 1000) / 10\%$.
     - Пороги вердикту: `sure >= 95%` ➔ `"clear"`, `80% <= sure < 95%` ➔ `"likely"`, `< 80%` ➔ `"close"`.

### 3.3. Виправлення Shopify App Store Review (Вимога 5.6.1: React Router 7 Post-Purchase CORS Bug)
* **Ключові файли**: `app/lib/cors.ts`, `app/lib/post-purchase-api.server.ts`, `app/lib/post-purchase.server.ts`, `app/routes/api.post-purchase.offer.tsx`, `app/routes/api.post-purchase.sign.tsx`, `app/routes/app.checkout.after-purchase.tsx`, `test/app/post-purchase-cors.test.ts`, `test/app/post-purchase-save.test.ts`.
* **Корінь проблеми (Root Cause)**:
  - Розширення `cro-post-purchase` виконується в ізольованій пісочниці Shopify Checkout (`https://extensions.shopifycdn.com`) і відправляє `POST` із заголовком `Content-Type: application/json` на сервер додатку (`/api/post-purchase/offer` та `/api/post-purchase/sign`).
  - Браузер перед `POST` автоматично надсилає CORS preflight-запит методом `OPTIONS`.
  - **Специфіка React Router v7**: React Router маршрутизує всі `OPTIONS`-запити у функцію **`loader`**, а НЕ в **`action`**! Оскільки маршрути мали лише `action` (або їхній `loader` не повертав `204 No Content` із CORS-заголовками), React Router відхиляв `OPTIONS` preflight, браузер блокував основний `POST`, а Post-Purchase розширення мовчки нічого не показувало (причина відхилення App Store **5.6.1** від 2026-11-11, виправлено в коміті `5c9e370` / PR #373).
* **Інженерне рішення**:
  1. Створено модуль `app/lib/cors.ts` із заголовками `CORS` (`Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type, Authorization`) та універсальним лоадером:
     ```ts
     export const preflight = (request: Request) =>
       request.method === "OPTIONS"
         ? new Response(null, { status: 204, headers: { ...CORS, "Access-Control-Max-Age": "86400" } })
         : null;
     export const postOnlyLoader = ({ request }: { request: Request }) =>
       preflight(request) ?? corsJson({ error: "Method not allowed" }, 405);
     ```
  2. Обидва маршрути (`api.post-purchase.offer.tsx` та `api.post-purchase.sign.tsx`) експортують `export const loader = postOnlyLoader;`, а всі помилки авторизації (`400`, `401`, `404`, `405`) повертаються через `corsJson(...)`, щоб розширення могло прочитати тіло помилки крос-доменно.
  3. **Жива самодіагностика (`checkConnection` у `post-purchase-api.server.ts`)**: На сторінці налаштування After-purchase offer додано кнопку «Test connection», яка із сервера виконує реальний зовнішній `fetch(..., { method: "OPTIONS", headers: { Origin: "https://extensions.shopifycdn.com", ... } })` та тестовий `POST` із токеном `"connection-test"` (очікуючи `401` із заголовком `access-control-allow-origin: *`) + перевіряє, чи обраний товар активний і в наявності.
  4. **Виправлення багу повторного збереження (`d56c28e766e30c6b1aa2117263b73d4bc1395928`, PR #375)**: Обгортка `gql()` кидає виняток на будь-який `userError` від Shopify GraphQL API. Раніше `ensureDefinition()` при кожному збереженні викликав `metafieldDefinitionCreate`, який на другому збереженні повертав помилку `TAKEN` (`"Key is in use for Shop metafields"`), блокуючи будь-які подальші зміни чи вимкнення офера. Тепер `ensureDefinition()` спочатку шукає визначення через `metafieldDefinitions(first: 1, ownerType: SHOP, namespace: "cro_toolbox", key: "post_purchase")` і створює його лише за відсутності.

### 3.4. Виправлення Cart Validation Function (`CART_INTERACTION`) та мультивалютні ліміти (`presentmentCurrencyRate`)
* **Ключові файли**: `extensions/cro-validation/src/cart_validations_generate_run.graphql`, `extensions/cro-validation/src/cart_validations_generate_run.js`, `extensions/cro-validation/tests/rules.test.js` (коміт `ee50515`, PR #377).
* **Суть проблеми та рішення**:
  1. **Пастка мінімального замовлення в кошику (`buyerJourney.step`)**: Shopify запускає `cart_validations_generate_run` не лише під час оформлення замовлення, а й на кожну дію в кошику (`CART_INTERACTION`). Коли мерчант встановлював правило `minTotal: 1000`, `minItems: 3` або `minPerProduct: 2`, спроба покупця додати найперший товар у порожній кошик відхилялася самою функцією валідації — покупець фізично не міг набрати кошик до мінімуму!
  2. **Розділення `MINIMUMS` vs `MAXIMUMS`**: До вхідного GraphQL-запиту додано `buyerJourney { step }` та `presentmentCurrencyRate`. У `cart_validations_generate_run.js` створено множину `const MINIMUMS = new Set(["minTotal", "minItems", "minPerProduct"]);`. Якщо `input.buyerJourney?.step === "CART_INTERACTION"`, усі правила з `MINIMUMS` пропускаються і перевіряються лише на етапах чекауту (`CHECKOUT_INTERACTION` / `CHECKOUT_COMPLETION`). Водночас правила перевищення лімітів (`maxTotal`, `maxItems`, `maxPerProduct`), `checkBundles` (захист від голих бандлів) та `checkPoints` (захист товарів за бали лояльності) діють негайно і в кошику.
  3. **Мультивалютність (`presentmentCurrencyRate`) та форматування цін**: Ліміти `minTotal` і `maxTotal` задаються мерчантом у базовій валюті магазину, але `cart.cost.subtotalAmount.amount` надходить у валюті покупця (`currencyCode`). Тепер ліміт множиться на курс презентаційної валюти (`const limit = r.value * rate`), а плейсхолдер `{limit}` у повідомленні про помилку форматується функцією `price(limit, currency)` (наприклад, `"The minimum order is EGP 1,000."` замість сирого числа `"1000"`).

### 3.5. 5 способів трекінгу посилок, вимкнення тріального 17TRACK та AI Guide / MCP Tools
* **Ключові файли**: `app/lib/tracking-guide.ts`, `app/lib/tracking.ts`, `app/lib/tracking/tracking.server.ts`, `app/lib/mcp/tracking-tools.server.ts`, `app/lib/copy-text.ts`, `app/lib/plans.ts`, `app/routes/app.tracking-returns.tsx`, `test/app/tracking.test.ts`.
* **Архітектурні деталі**:
  1. **5 уніфікованих способів підключення (`TRACKING_WAYS`)**:
     - **Спосіб 1 (`courier_app`)**: Офіційний Shopify-додаток самої кур'єрської служби (безкоштовно, пріоритет №1 — записує трекінг-номери та події прямо в замовлення Shopify, звідки Track page читає їх автоматично).
     - **Спосіб 2 (`own_key`)**: Власний API-ключ мерчанта від агрегаторів **17TRACK, AfterShip, TrackingMore або Ship24** (зберігається в зашифрованому вигляді через `lib/tracking/secret.server.ts`).
     - **Спосіб 3 (`webhook`)**: Приватний Webhook URL, куди кур'єр, 3PL-склад або Zapier/Make надсилає JSON (`{ number, status: "info|transit|out|delivered|problem", estimated, events: [...] }`), або нативні вебхуки 17TRACK/AfterShip/TrackingMore/Ship24.
     - **Спосіб 4 (`carrier_link`)**: Шаблон прямого посилання з плейсхолдером `{number}` для локальних перевізників, яких Shopify не знає (`MAX_CARRIER_LINKS = 20`, підтримується wildcard `*`).
     - **Спосіб 5 (`manual`)**: Ручне додавання статусів мерчантом в адмінці для індивідуальних чи власних доставок.
  2. **Захист економіки підписок (`LIVE_TRACKING` у `app/lib/plans.ts`)**: Вбудований пул живих відправлень за рахунок акаунта розробника в 17TRACK (200/міс на Growth, 500/міс на Pro) вимкнено у продакшені (`LIVE_TRACKING = process.env?.CRO_TEST_LIVE_TRACKING === "1"`), поки немає платних підписників, щоб не витрачати тріальний ліміт 17TRACK, але збережено під тестовим прапорцем у `npm run test:app`.
  3. **AI Guide (`trackingGuide(store)`) та 3 нових MCP-інструменти (`tracking-tools.server.ts`)**:
     - Функція `trackingGuide(store)` генерує структурований промпт від першої особи для ChatGPT / Claude / Gemini, який інструктує AI-асистента спочатку запитати назву кур'єра та країну, перевірити в інтернеті безкоштовні способи (офіційний Shopify-додаток кур'єра, прямий вебхук, сумісність із 4 агрегаторами) і провести мерчанта крок за кроком. **Інваріант безпеки**: приватний `webhookUrl` ніколи не вставляється у скопійований промпт.
     - Для роботи кнопки «Copy AI guide» всередині крос-доменного iframe Shopify Admin (де `navigator.clipboard` часто блокується політиками дозволів) створено `app/lib/copy-text.ts`, який спочатку використовує прихований `<textarea>` + `document.execCommand("copy")`, а `navigator.clipboard.writeText` тримає як фолбек.
     - До MCP-сервера додано 3 інструменти: `get_tracking_setup` (повертає поточне джерело, список перевізників із останніх відправлень магазину та схему вебхука), `set_carrier_link` та `set_tracking_source`.

### 3.6. Supabase Row-Level Security (RLS) та синхронізація схем Postgres/SQLite
* **Ключові файли**: `prisma/postgres/migrations/20261113000000_enable_rls/migration.sql`, `prisma/schema.prisma`, `prisma/postgres/schema.prisma`, `test/app/schema-sync.test.ts` (PR #350 `f24a01e` та RLS міграція).
* **Проблема та рішення**:
  1. **Інцидент розсинхронізації схем (PR #350)**: Локальна розробка використовує `prisma/schema.prisma` (SQLite), а продакшен на Render — `prisma/postgres/schema.prisma` (PostgreSQL). Під час деплою Scheduled Offers таблиця `OfferSchedule` була додана в SQLite, але пропущена в Postgres-міграції, що зламало продакшен.
  2. **Детермінований тест-гейт (`test/app/schema-sync.test.ts`)**: Додано автоматичний тест, який парсить усі блоки `model <Name> { ... }` в обох файлах схем, перевіряє `assert.deepEqual(models("prisma/postgres/schema.prisma"), models("prisma/schema.prisma"))`, а також гарантує, що кожна папка міграції в `prisma/migrations/` починаючи з `20261107000000` має дзеркальний аналог у `prisma/postgres/migrations/`.
  3. **Закриття PostgREST через Supabase RLS (`20261113000000_enable_rls/migration.sql`)**: Supabase за замовчуванням експонує всі таблиці схеми `public` через публічний PostgREST API для ролей `anon` та `authenticated` (попередження `rls_disabled_in_public`). Оскільки бекенд додатку підключається через Prisma від імені суперкористувача `postgres` (який обходить RLS), міграція вмикає RLS на всіх таблицях без жодної політики (`ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY`), повністю закриваючи публічний REST-доступ до всіх 26 таблиць без жодного впливу на роботу Prisma.

### 3.7. Маркетинговий SEO-сайт (Astro) та AI-Discovery (`llms.txt`)
* **Ключові файли**: `site/src/content/blog/*.md`, `site/src/lib/feature-keywords.ts`, `site/src/keywords/shopify-loyalty-app.ts`, `site/src/lib/llms.ts`, `site/src/pages/llms.txt.ts`, `site/src/pages/llms-full.txt.ts`, `site/src/pages/index.astro`.
* **Масштаб контент-машини**:
  1. У директорії `site/src/content/blog/` станом на `5819cf4` налічується **25 експертних статей** (та 26 статей станом на `6c6bb3f`). Між `7ea1589` та `5819cf4` було **створено/оновлено 9 блог-матеріалів** (7 нових + 2 оновлених, а у `6c6bb3f` додано 8-му нову статтю):
     - Нові у `5819cf4`:
       1. `how-to-add-a-size-chart-to-shopify.md`
       2. `increase-customer-lifetime-value-shopify.md`
       3. `reduce-returns-shopify.md`
       4. `schedule-a-sale-on-shopify.md`
       5. `shopify-loyalty-program-setup.md`
       6. `shopify-referral-program.md`
       7. `show-estimated-delivery-date-on-shopify.md`
     - Нова у `6c6bb3f` (8-ма нова стаття):
       8. `back-in-stock-alerts-shopify.md`
     - Оновлені у `5819cf4` (відповідно до нових функцій A/B/C/D та вимкнення тріального live tracking):
       - `ab-testing-offers-on-shopify.md`
       - `order-tracking-page-that-sells.md`
  2. **Programmatic SEO & LLM Ingestion**: Додано генератор `site/src/lib/feature-keywords.ts` (окрема посадкова сторінка під кожне пошукове ключеве слово функції), лендінг `shopify-loyalty-app.ts`, автоматичну генерацію OpenGraph-прев'ю (`site/src/pages/og/[slug].png.ts`) та індексацію ціннісних фактів у `/llms.txt` і `/llms-full.txt` для цитування AI-пошуковиками (ChatGPT Search, Perplexity, Claude).

### 3.8. Інші критичні знахідки з ревізії App Store (`#349`–`#386`)
1. **Пастка однорядкового `#graphql` коментаря (`cd7b6f1`, PR #383 + `test/app/graphql-tags.test.ts`)**: У `ab-tests.server.ts` та `loyalty.server.ts` запит валюти магазину був записаний в один рядок: `` `#graphql query CroShopCurrency { shop { currencyCode } }` ``. Оскільки символ `#` у GraphQL коментує весь рядок до `\n`, весь запит перетворювався на коментар, сервер отримував порожню відповідь і фолбечив валюту на `USD` (`$`) для всіх магазинів! Додано CI-тест `test/app/graphql-tags.test.ts`, який забороняє будь-який текст після `#graphql` на тому ж рядку.
2. **Підтримка пробілів у шляхах при компіляції теми (`ce33d99`, PR #349 — `scripts/build-theme.mjs`)**: Замінено перевірку `import.meta.url === \`file://\${process.argv[1]}\`` на `import.meta.url === pathToFileURL(process.argv[1]).href`, оскільки в папках із пробілами (наприклад, `Shopify apps` або `DNKEcom Theme Dev`) `import.meta.url` містить `%20` і CLI-скрипт `build-theme.mjs` мовчки нічого не виконував.
3. **Локалізація назв блоків у Checkout Editor (`8644e34`, PR #376)**: У `extensions/cro-thank-you/shopify.extension.toml` змінено `name = "t:name"` на явну назву `name = "CRO Toolbox thank-you page"`, бо редактор чекауту Shopify відображав сирий ключ `"t:name"`.

---

## ⚖️ 4. Матриця архітектурних розривів (Gaps) між DNK OS / DNKEcom та Апстрімом

| ID | Компонент / Підсистема | Стан в Апстрімі (`Omar92953/the-ultimate-cro-app`) | Стан у `DNK_HUB` / `DNKEcom` | Рівень розриву (Gap Severity) | План Clean-Room Асиміляції (Track 2) |
|---|---|---|---|---|---|
| **GAP-01** | **Локальний клон у `DNKEcom`** | Коміт `6c6bb3fd2a929ed75c82be2cc53659e2a1010a2f` (`cro-toolbox-80+`). | Коміт `7ea15893c2892029dc7446ed4ebacd317dd48476` (відстає на 100 комітів, відсутній файл `AUDIT_the-ultimate-cro-app.md`). | 🔴 **Високий (Дрейф еталона)** | Оновити локальний референс у `../DNKEcom/GitHub_Shopify_Apps/the-ultimate-cro-app` до `origin/main`, прогнати `test:app` та `test:functions`, створити `AUDIT_the-ultimate-cro-app.md` за Протоколом §12. |
| **GAP-02** | **A/B/C/D Engine + Customer Privacy API** | Повний цикл: SSR-варіанти ➔ `ucro-ab.liquid` (Consent-aware) ➔ `_cro_ab` у кошику ➔ Shopify Function знижка ➔ двопропорційний z-тест (Abramowitz & Stegun). | У `./services/dnk_shopify/src/ab_engine.py` є лише ізольований Python-клас без інтеграції з Shopify Customer Privacy API, атрибутами кошика та Wasm Functions. | 🔴 **Високий (Юридичний / Функціональний)** | Асимілювати патерн Consent-First бакетингу та двопропорційного z-тесту з анти-пікінг бар'єром (`MIN_VIEWS=100`, `MIN_ORDERS=10`) у `dnk_shopify`. |
| **GAP-03** | **Cart Validation (`buyerJourney.step` & Multi-Currency)** | Розділення `CART_INTERACTION` vs `CHECKOUT_INTERACTION` для мінімумів + множення грошових порогів на `presentmentCurrencyRate`. | Відсутній у поточних шаблонах валідації `dnk_shopify`. | 🔴 **Критичний (Блокує покупців у кошику)** | Впровадити інваріант `buyerJourney.step !== "CART_INTERACTION"` для всіх min-правил та масштабування `presentmentCurrencyRate` у генератор Shopify Functions. |
| **GAP-04** | **React Router 7 Post-Purchase CORS Preflight** | `postOnlyLoader` відповідає `204` на `OPTIONS` у `loader`; є вбудований self-test `checkConnection()`. | У документації `098_..._audit.md` описано лише JWT-підпис без згадки про пастку `OPTIONS` у `loader` React Router 7. | 🟠 **Середній (Блокер App Store 5.6.1)** | Зафіксувати патерн `postOnlyLoader` як обов'язковий стандарт для всіх Checkout / Post-Purchase API-маршрутів у `dnk_shopify`. |
| **GAP-05** | **Scheduled Offers з подвійним DST-коригуванням** | `toInstant()` на базі `Intl.DateTimeFormat` + одноразові прапорці `startDone`/`endDone` у БД. | Відсутній механізм відкладеного запуску/зупинки оферів з урахуванням `shop.ianaTimezone`. | 🟠 **Середній (Функціональний Pro-рівень)** | Синтезувати чистий модуль розкладу з подвійною перевіркою DST-зсуву та одноразовими переходами станів. |
| **GAP-06** | **Маршрутизація скіла `the_ultimate_cro_app_assimilated`** | Повноцінний Shopify CRO та E-com стек. | У `./core/skills/the_ultimate_cro_app_assimilated/SKILL.md` вказано `target_worker: "dnk_video_ai_creator"` та `services/dnk_video/`. | 🟡 **Низький (Метадані оркестрації)** | Перенаправити `target_worker` у `SKILL.md` на `dnk_shopify` та оновити архітектурний індекс до версії 2.1.0. |
| **GAP-07** | **Захист схем БД та GraphQL-тегів у CI** | Автотести `test/app/schema-sync.test.ts` (SQLite == Postgres), `test/app/graphql-tags.test.ts` (`#graphql\n`) та Supabase RLS міграція. | Немає автоматичної перевірки на однорядковий `#graphql query` коментар у TS/JS адаптерах. | 🟡 **Низький (Надійність CI)** | Додати AST/regex правило перевірки `#graphql` тегів та RLS-міграцій у перевірочні гейти `dnk_shopify`. |

---

## 🛡️ 5. П'ятивекторна інженерна оцінка (5-Vector Critique) стану Апстріму (`6c6bb3f`)

1. **Гранічні умови (Boundary Conditions)**:
   - Бюджет Liquid-компілятора (`scripts/build-theme.mjs`) все ще працює поблизу стелі Shopify Theme App Extension (~86–88 KB із 100 KB ліміту та 248 із 250 ключів локалізації). Додавання A/B/C/D варіантів у `ucro-upsell.liquid` та `ucro-cross-sell.liquid` збільшує розмір DOM на сторінці товару пропорційно до кількості активних версій (до 4 копій розмітки блоку до спрацювання `ucro-ab.liquid`).
2. **Масштабованість (100x Load)**:
   - Воркер `startSchedules()` використовує `setInterval(..., 5 * 60_000)` всередині веб-процесу Node.js (`globalThis.croScheduleTimer`). При горизонтальному масштабуванні на декілька інстансів Render виникне стан гонитви (race condition) між воркерами, які одночасно читають `startDone: false`. Для enterprise-навантаження у DNK OS необхідний `SELECT ... FOR UPDATE SKIP LOCKED` або розподілений cron-лідер.
3. **Підтримуваність та технічний борг (Maintainability)**:
   - Підтримка двох окремих файлів схем (`prisma/schema.prisma` для SQLite та `prisma/postgres/schema.prisma` для Postgres) створювала ризик розсинхронізації, але автор елегантно закрив це детермінованим тестом `test/app/schema-sync.test.ts`.
4. **Вектори безпеки (Security Attack Vectors)**:
   - Ввімкнення RLS на всіх таблицях Postgres (`20261113000000_enable_rls`) закрило критичну діру Supabase PostgREST.
   - Неприпустимість витоку секретного `webhookUrl` у промпт AI-асистента (`trackingGuide`) та перевірка HMAC/JWT у Post-Purchase реалізовані бездоганно.
5. **Обчислювальна ефективність (Performance)**:
   - Нульове споживання зовнішніх пакетів для статистики (поліном Абрамовіца-Стегуна в 6 рядків коду) та таймзон (`Intl.DateTimeFormat`) тримає серверний бандл мінімальним і швидким.
