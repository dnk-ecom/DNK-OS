---
name: ukrainian-humanizer
description: Use when generating, editing, or auditing Ukrainian text, product descriptions (Shopify PDP), or social copy to eliminate AI slop, English translationese calques, russianisms, and bureaucratic passive voice.
version: 1.0.0
author: DNK Swarm (gerych_prime)
category: creative
---

# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/SKILL.md"
# purpose: "Canonical Ukrainian Copywriting & Anti-Slop Humanizer Skill with deterministic 5-check detection and translationese stripping."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

# 🇺🇦 Ukrainian Humanizer & Native Copywriting Engine (v1.0.0)

## 1. Mission & Architectural Lineage
This skill synthesizes best-in-class open-source and internal DNK OS text engineering practices into a single Ukrainian-native system:
1. **Wikipedia & Blader/DanGeo13 `humanizer` (34 AI Tells)**: Eliminates significance inflation, negative parallelisms, rule-of-three triads, and sycophantic closers.
2. **Epoko77-ai `im-not-ai` (Non-English Translationese Taxonomy & Route Gate)**: Targets structural **translationese** (English syntax dressed in Ukrainian morphology), enforces **Content Anchor Preservation**, and applies a deterministic **Over-Edit Guard** (warns $>30\%$, stops $>50\%$).
3. **Jakeschincariol `linkedin-agent-skill/li-human` (5-Check Quantitative Panel & Invisible Watermark Scrubber)**: Deterministically strips zero-width Unicode watermarks (`U+200B`..`U+FEFF`), normalizes Ukrainian typography (`«лапки»`, `’`), and scores text across 5 axes (`BURSTINESS`, `SPECIFICITY`, `SLOP DENSITY`, `FINGERPRINT`, `VOICE`).
4. **DNK OS Internal Standards (`shopify_dynamic_pdp_playbook`, `video-retention-engineering`, `brand_compliance.py`)**: Integrates conversion-focused sensory copywriting, dynamic burstiness, and regulatory safety.

---

## 2. Deterministic CLI Pipeline (Run First — Never Eyeball Alone)

Two zero-dependency Python tools live in `core/skills/ukrainian_humanizer/scripts/` and read `references/uk_slop_lexicon.json`:

```bash
# 1. Diagnose & get route_hint (light | standard | heavy) + 5-check panel score
python3 core/skills/ukrainian_humanizer/scripts/uk_detect.py draft.txt

# 2. Deterministically scrub invisible watermarks, fix «лапки»/apostrophes, and strip lexicon calques
python3 core/skills/ukrainian_humanizer/scripts/uk_humanize.py draft.txt -o clean.txt --report

# 3. Rewrite flagged structural sentences, then prove the Before/After delta
python3 core/skills/ukrainian_humanizer/scripts/uk_detect.py draft.txt clean.txt
```

### Route-Based Processing (`route_hint`)
- **`light` (`HUMAN SCORE >= 70`, `min_check >= 55`)**: Run `uk_humanize.py` for typography/invisible character hygiene and make minimal surgical tweaks.
- **`standard` (`50 <= HUMAN SCORE < 70`)**: Run `uk_humanize.py`, then rewrite sentences flagged under `STRUCTURAL TELLS` and boost the weakest signal reported by `uk_detect.py`.
- **`heavy` (`HUMAN SCORE < 50`)**: The draft is formulaic AI slop. Extract the **Content Anchors** (facts, numbers, dimensions, materials, user benefit) and rebuild paragraphs from scratch using native Ukrainian active syntax.

---

## 3. Hard Constraints (The 4 Immutable Laws)

1. **Content Anchors Are Immutable**: Numbers, prices (`грн`, `$`), measurements (`мм`, `г`, `мл`), model names, dates, URLs, and core product claims must survive 100% intact. Never invent fake specifications to boost specificity.
2. **Subtraction Over Invention**: Do not replace AI metaphors (`гобелен можливостей`) with new floral metaphors. Replace them with concrete actions or delete them.
3. **Ukrainian Typographic Standard**:
   - External quotes: `«кутові лапки»` (never English `“...”` or straight `"..."`).
   - Apostrophe: `’` (`U+2019`) in Ukrainian words (`м’який`, `зв’язок`, `п’ять`).
   - Dash vs Hyphen: Hyphen (`-`) inside compound words without spaces (`будь-який`, `бізнес-план`); em-dash (`—`) with spaces between sentence clauses — strictly capped at **max 1 em-dash per paragraph**.
4. **Over-Edit Guard**: For editing existing human drafts, keep character/word `change_rate_pct <= 30%` (hard stop at `50%`). For regenerating raw AI slop from scratch, verify that 100% of factual anchors survive.

---

## 4. The 8 Core Categories of Ukrainian AI Slop (Taxonomy `UK-A` .. `UK-H`)

### `UK-A`: Англійський синтаксичний калькуляж (Translationese)
LLMs think in English token patterns and map them word-for-word onto Ukrainian grammar:
- **Хибні перехідні конструкції**:
  - ❌ *«Більше того,» / «Крім того,» / «Тим не менш,»* на початку кожного другого речення.
  - ✅ Видаляйте їх у 80% випадків — нехай логіка речень сама веде читача. Коли зв'язка справді потрібна: *«До того ж», «Також», «Утім,», «Проте»*.
- **Кальки з `through / via / in terms of`**:
  - ❌ *«Через використання нашого додатку ви отримуєте...»*, *«У плані продуктивності це рішення...»*, *«Незалежно від того, чи ви новачок, чи професіонал...»*
  - ✅ *«У додатку ви за 2 кліки...»*, *«Працює на 40% швидше...»*, *«Підійде і для першого запуску, і для щоденної роботи в цеху.»*
- **Зайві присвійні займенники (`your / our / its`)**:
  - ❌ *«Покращте ваш досвід пиття кави на вашій кухні за допомогою нашої кавоварки.»*
  - ✅ Українська мова уникає займенникового дублювання: *«Заварюйте густе еспресо вдома без зайвого клопоту.»*

### `UK-B`: Канцелярит, безособовий пасив та віддієслівні іменники
- **Безособові пасиви на `-но/-то` та `-ться`**:
  - ❌ *«Нами було розроблено систему, якою забезпечується висока надійність та здійснюється контроль.»*
  - ✅ Живий підмет + активне дієслово: *«Ми зібрали систему, яка тримає навантаження і сама перевіряє тиск.»*
- **Нагромадження іменників на `-ння / -ття` (Nominalization bloat)**:
  - ❌ *«Забезпечення оптимізації процесу приготування шляхом впровадження нагріву...»*
  - ✅ Замінюйте віддієслівні іменники на дієслова: *«Нагріває воду за 15 секунд і заощаджує час зранку.»*

### `UK-C`: Русизми та граматичні покручі в генераціях LLM
Через змішування східнослов'янських токенів у корпусах навчання LLM часто генерують ненормативні форми:
- **Активні дієприкметники на `-учий/-ючий`, `-ачий/-ячий` (суворо заборонено)**:
  - ❌ *«вражаючий дизайн», «діюча речовина», «миючий засіб», «оточуюче середовище», «слідкуючий датчик»*.
  - ✅ *«виразний дизайн», «активна речовина», «засіб для миття», «довкілля», «датчик руху»* або підрядне речення (*«який вражає»*).
- **Лексичні кальки**:
  - ❌ *«приймати участь», «приймати рішення», «співпадати», «на протязі дня», «в свою чергу», «по замовчуванню», «самий кращий», «давайте розглянемо»*.
  - ✅ *«брати участь», «ухвалювати рішення», «збігатися», «протягом дня», «своєю чергою», «за замовчуванням», «найкращий», «розгляньмо»*.

### `UK-D`: Штучний пафос та роздуття значущості (Significance Inflation)
- ❌ *«У сучасному швидкоплинному світі...», «відіграє ключову роль», «відкриває нові горизонти», «виводить на новий рівень», «є яскравим свідченням», «неперевершена симфонія смаку та інновацій»*.
- ✅ Починайте з конкретного болю, сценарію або фізичної деталі продукту. Замість прикметника «інноваційний» або «неперевершений» дайте цифру або відчутний факт (*«корпус із анодованого алюмінію товщиною 2 мм, не дряпається в рюкзаку разом із ключами»*).

### `UK-E`: Синтаксичні кліше та театральні конструкції
- **Негативний паралелізм («Це не просто X — це Y»)**:
  - ❌ *«Це не просто лампа — це ваш персональний оазис затишку та продуктивності.»*
  - ✅ *«Лампа світить теплим спектром 2700K без мерехтіння, тож очі не печуть після вечірнього читання.»*
- **Правило трьох (Rule-of-Three Triads)**:
  - ❌ *«Швидко, надійно, ефективно.» / «Стиль, комфорт та довговічність у кожній деталі.»*
  - ✅ Використовуйте 2 конкретні факти або 4 деталі з поясненням.

### `UK-F`: Мета-підводки та нудотні висновки (Openers & Closers)
- ❌ Вступи: *«Варто зазначити, що...», «Не секрет, що...», «Давайте зануримося глибше...»*
- ❌ Фінали: *«Підводячи підсумки, варто сказати, що цей продукт стане незамінним помічником для кожного, хто цінує якість та комфорт.»*
- ✅ Обрізайте перший і останній абзаци ШІ-чернетки. Завершуйте текст конкретною деталлю комплектації, гарантії або прямим закриттям заперечення.

### `UK-G`: Монотонність ритму (Low Burstiness)
- Моделі будують речення однакової довжини (13–17 слів) та однакової структури (*Підмет — Присудок — Додаток*).
- **Правило українського ритму (`CV >= 0.45`)**: Чергуйте довгі інформативні речення (18–24 слова) з короткими, рубаними фразами (2–6 слів). Використовуйте природну інверсію (починайте речення з обставини або дії, коли це підсилює акцент).

### `UK-H`: Візуальний спам (Formatting Slop)
- ❌ Списки вигляду `- **Назва переваги:** довге пояснення...` у кожному блоці.
- ❌ Емодзі-маркери 🚀, 🔥, ✨, 💡, 🎯, 💎.
- ❌ Тире (`—`) у кожному реченні як замінник усіх розділових знаків.

---

## 5. E-Commerce & Product Description Playbook (Для описів товарів людям)

Коли ви генеруєте або редагуєте опис товару (Shopify PDP, каталог, лендинг, огляд), використовуйте формулу **«Фізика -> Сценарій -> Спокій»** замість абстрактних епітетів:

1. **Перший рядок (Хук через сценарій або контраст)**:
   - Заборонено починати з назви бренду та слів *«Представляємо вам інноваційний...»*.
   - Починайте з моменту використання: *«Коли вимикають світло посеред робочого дзвінка, роутер і ноутбук продовжують працювати ще 9 годин без перемикання кабелів.»*
2. **Трансформація характеристик у фізичний досвід (Feature -> Sensory Benefit)**:
   - Замість *«високоякісний матеріал»* -> *«матова кордура 1000D: краплі дощу скочуються, а бруд стирається вологою серветкою»*.
   - Замість *«ергономічний дизайн»* -> *«важить 180 г і лягає в долоню так, що великий палець одразу дістає до кнопки блокування»*.
3. **Чесна конкретика (Honest Limitation / Anti-Hype)**:
   - Живі люди довіряють текстам, які називають межі застосовності. Одна чесна деталь (*«Розрахований на кімнати до 25 м²; для великого опенспейсу краще взяти старшу модель»*) підвищує довіру сильніше за десять слів «найкращий».

---

## 6. Еталонний приклад трансформації (До / Після)

### ❌ ДО (Типовий україномовний AI Slop — `HUMAN SCORE: 14.2 FLAGGED`):
> “У сучасному швидкоплинному світі якісний сон відіграє ключову роль у нашому здоров'ї. Представляємо вам інноваційну ортопедичну подушку AeroSleep — це не просто подушка, це ваш персональний квиток у світ неперевершеного комфорту та відновлення! Більше того, завдяки використанню унікальної піни з ефектом пам'яті забезпечується безшовна підтримка шийного відділу хребта на протязі всієї ночі. Крім того, дихаючий чохол здійснює оптимальну терморегуляцію. Підводячи підсумки, AeroSleep стане незамінним помічником для кожного, хто цінує своє здоров'я!”

### ✅ ПІСЛЯ (`ukrainian_humanizer` — `HUMAN SCORE: 86.4 PASS`):
> Прокидатися без затерплої шиї та важкої голови — норма, якщо хребет вночі лежить рівно. В ортопедичній подушці «AeroSleep» працює щільна піна Memory Foam (50 кг/м³): вона за 3 секунди підлаштовується під вигин плеча й не провалюється під вагою голови до ранку. Висота валиків — 10 і 12 см, тож зручно спати і на боці, і на спині. Знімний чохол із бавовни та волокон Tencel відводить тепло, тому влітку обличчя не пітніє. Чохол легко розстебнути й випрати в машинці за 30 °C.
