---
title: "ADHD Vibe-Coder Decision Registry (SSOT)"
aliases:
  - "DECISION_REGISTRY_ADHD"
  - "ADHD Decision Registry"
tags:
  - dnk-os
  - architecture
  - decisions
  - adhd-registry
created: 2026-10-12
updated: 2026-10-27
status: approved
type: architecture
domain: core
author: "DNK-e.com Maksym & Antigravity"
version: "1.1.0"
---
> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
>
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/DECISION_REGISTRY_ADHD.md"
> # purpose: "Canonical ADHD Decision Registry & Vibe-Coder Action Ledger for DNK OS."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.3.0"
> # updated_at: "2026-11-01"
> # author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# ⚡ ADHD VIBE-CODER DECISION REGISTRY (SSOT)

> **Залізне Правило:** Будь-яке рішення зі статусом `[🔒 LOCKED]` **ЗАБОРОНЕНО обговорювати заново**. Агент зчитує цей реєстр, бере наступну задачу з чеклиста і видає тільки стислий ADHD-звіт (до 1 екрана, нуль теоретичних лекцій).

---

## 🔒 1. ЗАТВЕРДЖЕНІ РІШЕННЯ (Більше не пережовуємо)

| ID | Рішення | Технічний Стандарт | Статус |
| --- | --- | --- | --- |
| **DEC-001** | Shopify Theme Runtime | **Tinker 4.2.0 (Theme Blocks 2.0)**. Відкидаємо сирий skeleton-theme для продакшену. | 🔒 LOCKED |
| **DEC-002** | Архітектура теми | **3 Оболонки (`_blocks`, `main-product`, `main-cart`) + Dual-Ready Блоки v2.0**. | 🔒 LOCKED |
| **DEC-003** | Роль Гєрича (Hermes) | **Чистий Білдер коду**. Заборонено веб-серфінг і читання блогів. Працює зрізами MASE ≤ 25 дій. | 🔒 LOCKED |
| **DEC-004** | Склад команди агентів | **4 Dev-Агенти** (Architect, Builder, Librarian, Auditor) + **4 Runtime** (Intel, Wordsmith, Theme, Launch). | 🔒 LOCKED |
| **DEC-005** | База 1900 посилань | **Офлайн-дистиляція у скіли**. Ніякого сирого RAG. Конвертація у компактні `SKILL.md` (≤ 750 рядків). | 🔒 LOCKED |
| **DEC-006** | Формат відповідей вайбкодеру | **ADHD-стиль**: Максимум 1 екран, статус ➔ 3 тези ➔ 1 кнопка дії. Жодних довгих лекцій. | 🔒 LOCKED |
| **DEC-007** | Детерміновані рішення та чеки | **Jev Engine (`core/orchestrator/decision_draft.py`)**: Zero-Trust Hard Gates, Abstention Protocol (<5% margin / <70 score), криптографічний чек `jvr_0dc5a8cd49753128a831` (SHA-256). | 🔒 LOCKED |
| **DEC-008** | Стратегічний фокус DNK OS | **Dogfooding-First Production Engine**. Харнес — внутрішня фабрика комерційних артефактів (Shopify, медіа, воронки). Жодного венчурного пітчингу сирого софту. Продаж кінцевого результату. | 🔒 LOCKED |
| **DEC-009** | Вайрфрейми & Сторінки | **Shopify OS JSON-First (`templates/page.*.json`) + Visual Preview Graph**. Пряма збірка з реєстру Theme Blocks 2.0 (Tinker). Нуль сторонніх генераторів (Stitch). Клієнт правитиме в нативному Theme Customizer. | 🔒 LOCKED |
| **DEC-010** | 6-Етапний Клієнтський Воркфлоу | **Shopify Production Pipeline v1.0**: 1) Onboarding Intake ➔ 2) Deep Research & CRO ➔ 3) 2x Wireframes (Theme Blocks) ➔ 4) Brand Injection ➔ 5) Media & Local Customizer Test ➔ 6) Theme Push & Deploy. | 🔒 LOCKED |
| **DEC-011** | SOTA Repo Search & Deep Intel | **Bilingual Intent Query Expander (UA ➔ EN) + Weighted BM25 (Tier 1 x3.0, Tier 2 x2.0, Track 1 x1.5) + get_repo_deep_intel() FastMCP Contract**. Локальний SQLite FTS5 (<15ms, 0 байт хмарних витрат). | 🔒 LOCKED |
| **DEC-012** | Архітектура Agent Harness | **Zero-Framework Microkernel (ADR-091)**. DNK OS — самостійний бізнес-харнес. Жодних важких сторонніх фреймворків (OpenHands/CrewAI) у ядрі. Hermes (Гєрич) — виключно зовнішній CLI Dev-воркер. Прямий роутинг на моделі (Gemini 4 Argon / Claude / Grok). | 🔒 LOCKED |
| **DEC-013** | Синтез теми DNK-Ecom (5 Донорів) | **Ядро: Story Basic 4.0.5**; **Агентні блоки & події: KS Origin 1.0.0**; **Розширений CRO функціонал: Casaio 1.1.0 + Ella 7.3.1**; **Конверсійні блоки v2: Shrine Pro 1.9.0**; **База перевірених секцій 2.0: DNK_Ecom_sections_v.1.0.0 + Ascendify 2.10.0**. Сувора ізоляція стилів, нуль сирого перенесення легасі-JS. | 🔒 LOCKED |
| **DEC-014** | Zero-Weight-Claim & Live Official Source Gate | **Заборона відповідей із ваг LLM щодо лімітів/мов платформ**. Перед будь-яким твердженням про те, що підтримує чи не підтримує зовнішня платформа (Shopify, Meta, Google), обов'язкова жива перевірка (`web_search`/`web_extract` по `shopify.dev`/`help.shopify.com` або інспекція живого браузера). Shopify Account нативно підтримує `Українська (Бета-версія)` ➔ `locales/uk.schema.json`. | 🔒 LOCKED |
| **DEC-015** | 5-Річна Архітектура Shopify Тем (2026–2031) під Shopify Canvas | **Чиста Horizon v4.3+ / Theme Blocks 2.0 (4-Шарова Формула, ADR-093)**. Поділ на публічні `@theme` атомарні блоки, `_group.liquid` Auto-Layout контейнери (ліміт глибини ≤ 3–4 рівні) та захищені приватні `_block.liquid` комерційні вузли. Ізольовані Web Components (`<cart-drawer>`, `<variant-selects>`) поза мікроблоками. | 🔒 LOCKED |
| **DEC-016** | Двотрекове Сховище та Молекулярна Транспіляція | **DNK Component Vault (`services/dnk_shopify/dnk_component_vault/`) + Легке Ядро (`DNK-e.com` < 8MB)**. 2 538 молекул з 9 донорів живуть в ізольованих чистих гілках за назвою теми (`<theme-slug>`). Відібрані золоті вузли зберігаються у Vault із `node.manifest.json` (--dnk-* токени, Web Components, UK i18n) і монтуються в живу тему `staging`/`main` за 0.1 секунди. | 🔒 LOCKED |
| **DEC-018** | Стандарт гілок і тегів тем у `DNKShopify/DNK-e.com` | **Гілка = чиста назва теми `<theme-slug>` (kebab-case без префіксів `donor/` чи версій). Кожна нова версія = атомарний Commit + анотований Scoped Tag `<theme-slug>-v<X.Y.Z>` + синхронний bump `theme_version` у `config/settings_schema.json`**. | 🔒 LOCKED |
| **DEC-019** | Zero-Trace Seamless Visual Injection Engine | **5-Шаровий Конвеєр (`packages/plugins/dnk-seamless-injection`)**: 1) SAM 2 + Grounding DINO (`feather 1.5–2.0px`) ➔ 2) LaMa FFC Inpainting ➔ 3) Displacement & Shading Map ➔ 4) CoTracker3 Deformable Warp (`550+ точок`, `60fps`) ➔ 5) Poisson Blend + RGB Sensor Grain. Hard Gates перед Shopify CDN: `LPIPS < 0.04`, `Edge Gradient > 0.98`, `Zero-OCR = 0`. | 🔒 LOCKED |
| **DEC-020** | Дворівнева Модель Gerych & Контекстна Дієта | **Повсякденна розробка: `gemini-3.8-flash`, Архітектурні сесії: `gemini-4-argon`. Fallback-ланцюг: `3.7-flash` ➔ `4-argon` (ескалація) ➔ NVIDIA `llama-3.2` (відсічено моделі <3.7). Усунуто мережеві затримки запуску (`npx -y` та remote TLS): всі MCP переведені в `disabled_mcp_servers` на прямі локальні шляхи node ➔ старт прискорено до ~1.5с, стоячий контекст скорочено до ~4.5k токенів**. Конфігурація збережена для JIT активації. | 🔒 LOCKED |
| **DEC-021** | Скорочення стоячого контексту | **Зменшення overhead з 34.3k до 18.8k токенів (-45%)**. Профілювання toolsets, focus posture, відсікання нерелевантних скілів. | 🔒 LOCKED |
| **DEC-022** | Єдине джерело правди (SSOT) & Anti-Split-Brain | **`DNK_HUB` — єдина фабрика і SSOT**. `DNK_OS_APP` — клієнтський артефакт експорту (`scripts/export_standalone_app.py`). Заборона ручного дублювання коду. | 🔒 LOCKED |
| **DEC-023** | DNK Polaris-Spatial Design System (DPS-DS) | **Центральні токени (`packages/archify/schemas/dnk_polaris_design_tokens.json`) з двоканальним експортом у Tailwind v4 (`apps/web`) та CSS Custom Properties для Shopify Theme Blocks 2.0**. | 🔒 LOCKED |
| **DEC-024** | Native SCONES Memory Plugin & Review-on-Stop | **Нативний плагін пам'яті (`core/hermes_agent/plugins/memory/scones/`) під контракт `MemoryProvider` з авто-префетчем (<=1200 токенів), 90 SOTA-базами та детермінованим гейтом ScallopBot Review-on-Stop (AST + відносні шляхи) перед коммітом**. Усунено нескінченний цикл ре-екзекуції у харнесі. | 🔒 LOCKED |
| **DEC-025** | Folder as Harness & Subagent Folding Protocol | **Згортання 12 оргчарт-агентів у модульні скіли (`core/skills/*/SKILL.md`) під тріаду: Antigravity, Gerych Prime, Gerych Auditor**. Файлова система Markdown та SQLite WAL як кінцевий автомат стану. | 🔒 LOCKED |
| **DEC-026** | Dual-Surface Ingestion & Agent-Native Assimilation | **Двоканальна дія (FastMCP + Web UI) на базі Pydantic-схем у Python Microkernel**. Відкидання TypeScript Nitro; Voice/Text інтейк через `core/harness/intake.py`. | 🔒 LOCKED |
| **DEC-027** | Obsidian Visual Shell Harness & Dual-Vault Parity | **Obsidian як просторовий копіт System 1 (11 плагінів, Excalidraw, K-Plex, 3 CSS-сніпети)** з програмним керуванням через Local REST API (`:27123`). Дзеркальна синхронізація з `DNK_OS_APP` при єдиному SSOT у `DNK_HUB` (`docs/notes/`). | 🔒 LOCKED |
| **DEC-028** | Living Bio-Organism Architecture & Single Foundry Unification | **Трансформація DNK OS у біо-робота з 6 живими системами та ліквідація Split-Brain**. `DNK_HUB` єдиний SSOT; `DNK_OS_APP` лише ціль компіляції експорту. | 🔒 LOCKED |
| **DEC-029** | Agentic Bio-Organism Core v1 & Dual-Surface Canvas-Chat Engine | **Симбіоз Людини (Obsidian Excalidraw) та Агента (FastMCP Core)**. Двосторонній стрім статусів вузлів через Event Envelope v1, MRH-скан <10ms без токен-блоату, ліквідація дублюючих канвасів. | 🔒 LOCKED |
| **DEC-030** | Dual-Surface Living Documentation Engine (`DNK-Ecom_OS`) | **Fumadocs (Next.js MDX) + OpenAPI 3.1 Reflection + Native `/llms.txt` & FastMCP Doc Server**. Заміна важкого хмарного Fern/Mintlify локальним Fumadocs для людей та детермінованим `/llms.txt` для агентів. Хроніка розробки `content/journey/` генерується автоматично. | 🔒 LOCKED |
| **DEC-031** | Agent-First Self-Healing Architecture & 10-Day Sunsetting of DNK_HUB | **`DNK-Ecom_OS` — суверенна цільова система, а не зовнішній сайт-вітрина. Документація створюється першочергово ДЛЯ АГЕНТІВ (What/Why/How + AST-прив'язка + відтворювані верифікатори для миттєвого ремонту/покращення будь-якого вузла), для Людини — лише ключові стратегічні рішення. Повна дистиляція та депрекація `DNK_HUB` за 10 днів**. | 🔒 LOCKED |
| **DEC-032** | Дворівневий мовний стандарт: STE-Agentic (STE-Lite) + Precision English | **Відхилено 100% ASD-STE100 (кастрація архітектури, +40% токенів, лінтинг-податок). Затверджено STE-Agentic для контуру дій (runbooks, invariants, task_dna: імператив, <=20 слів/крок, нуль розмитих модальностей, 1 дієслово = 1 дія, детермінований exit code 0) та Precision Technical English для людини й ADR**. | 🔒 LOCKED |
| **DEC-033** | Zero-Repository-Bloat & Centralized System Runtime (`~/.dnk_runtime`) | **Заборона фізичних `node_modules` (>500MB) та локальних середовищ усередині цільових репозиторіїв (`DNK-Ecom_OS`). Репо містить ВИКЛЮЧНО чистий вихідний код, схеми та специфікації (< 2MB). Усі залежності та білд-артефакти виносяться в централізоване системне середовище `~/.dnk_runtime/` або глобальні кеші. Ніяких "Франкенштейнів"**. | 🔒 LOCKED |
| **DEC-034** | Sovereign Agent Microkernel (< 400 LOC) & Hermes Deprecation | **Заміна моноліту Hermes (291 МБ) на протокольне мікроядро**. Спирається на SOTA аудит 5 лабораторій: MCP (Anthropic), Stateless Handoff (OpenAI Swarm), Task Ledger (Microsoft), Prompt Caching (Google). | 🔒 LOCKED |
| **DEC-035** | Tri-Surface Knowledge Mesh (Obsidian + Fumadocs + SCONES Graph) | **Єдиний субстрат знань: `DNK-Ecom_OS/content/` одночасно є Obsidian Vault для просторового мислення людини, базою Fumadocs для веб-порталу та графовою пам'яттю SCONES для агентів**. Wikilinks `[[DEC-*]]` та `[[INV-*]]` компілюються через `fumadocs-obsidian`, а SCONES індексує ребра графа для запитів агента в <= 2 хопи. | 🔒 LOCKED |
| **DEC-036** | Code Execution with MCP (Anthropic Code Mode / CE-MCP) | **Заміна покрокового JSON tool-calling на програмну оркестрацію в sandbox**. Агент пише суцільний Python/TypeScript скрипт, який викликає FastMCP-сервери локально в 1 крок, скорочуючи витрати токенів контексту на 98.7%–99% та ізолюючи сирі масиви даних у RAM пісочниці. | 🔒 LOCKED |
| **DEC-037** | Subtraction Engine & C-Suite Chair Architecture у новому додатку DNK OS | **6 поліпшень з Chief of Staff v2 та Bloatbot (`4-Part Chair Anatomy`, `Zero-Mutation Bloatbot`, `Heartbeat Fail-Loud`, `Morning/End ADHD-ритми`, `Front-Door Born Lazy`, `Buildbot 1-Page Gate`) реалізуються безпосередньо у новому додатку `DNK_OS_APP` / `DNK-Ecom_OS`**. Заборонено перевантажувати легасі-контур DNK_HUB. | 🔒 LOCKED |
| **DEC-038** | Elephant-Goldfish Model (EGM) Dual-Phase Architecture & Zero-Context Review Protocol | **Розподіл розробки на Elephant (глибокий контекст + інтерактивний дизайн спеки під правилом ZERO CODE) та Goldfish (ізольовані свіжі субагенти з 0 контексту для безжального стрес-тестування спеки та коду)**. Запобігає «швидкості сміття» (velocity of slop) у вайбкодингу. Повна інтеграція Google EGM у контур рев'ю DNK OS. | 🔒 LOCKED |
| **DEC-039** | Native Shopify CLI Tunnel Preview for Human Canvas (Zero Simulation Emulator) | **Заміна симуляції Liquid на нативний Shopify CLI тунель (`shopify theme dev`) у WebView/iFrame**. 100% точність візуалу, Hot Reload, нульова симуляція стану. | 🔒 LOCKED |
| **DEC-040** | Task Forest & Spatial Canvas DAG Synchronization Engine (Chat-to-DAG Event Mesh) | **Асинхронна трансляція реплік та дій чату в просторове полотно JSON Canvas 1.0 та граф Task Forest**. Діалоги не губляться в логах, а автоматично проєктуються на `ThoughtDAG` (8 типів NodeKind, алгоритм Кана проти циклів, геометрична авто-кластеризація проти спагеті, 5-фазовий TaskDNA Gated Lifecycle). | 🔒 LOCKED |
| **DEC-041** | Living Spec Ratchet Engine & 3-Zone Evolutionary SSOT | **Програмний рушій еволюційного ядра (`core/agent_kernel/spec_ratchet.py`)**. Запобігає «цвинтарю знань»: детектує технічні рішення в чатах, підтримує 3-зонні специфікації доменів (`LOCKED INVARIANTS`, `ACTIVE CAPABILITIES`, `PENDING MUTATIONS`), генерує атомарні таски для Герича та автоматично просуває верифікований код без зламу існуючих систем. | 🔒 LOCKED |
| **DEC-042** | Denchik Sovereign Master Developer Architecture | **Суверенний інженерний профіль розробника (`core/orchestrator/agents/denchik/`) з нативним FastMCP Code Mode sandbox, Task Forest DAG sync, та Review-on-Stop quality gate**. Забезпечує роботу подвійного ядра: повнофункціонального TUI та мікроядра < 400 LOC (`denchik --microkernel`). | 🔒 LOCKED |
| **DEC-043** | Headless Node-Based Canvas Core Runtime (CONTRACT-002 & OCC) | **Автономний рантайм просторового графа (`core/canvas/node_canvas_core.py`)**. Реалізує детерміноване ядро керування станом полотна: повна підтримка CONTRACT-002 (8 типів NodeKind), топологічне сортування за алгоритмом Кана проти циклів, Optimistic Concurrency Control (OCC) із 3-way злиттям, двосторонній імпорт/експорт JSON Canvas 1.0 та компіляція сфокусованого контексту підграфа для LLM. | 🔒 LOCKED |
| **DEC-044** | Chord Delta Protocol & TypeScript Code Mode Sandbox (Pi Engine Assimilation) | **Асиміляція архітектури earendil-works/pi (Mario Zechner, MIT)**: 1) `@earendil-works/chord` — транзакційний дельта-протокол (`OpBatch`) для 60 FPS live-синхронізації полотна Canvas без надлишкової передачі повного JSON-стану; 2) `@earendil-works/codemode` — динамічна генерація `.d.ts` описів FastMCP/інструментів (`declare const tools: { ... }`) для безпечного запуску скриптів агентом; 3) `OutputBuffer` truncation для захисту від переповнення контексту термінальними логами. | 🔒 LOCKED |
| **DEC-045** | SCONES Vitality Receipts & Working-Tree Overlay (Entire Assimilation) | **Асиміляція Entire-Brain та Entire-Graph у когнітивну пам'ять DNK OS**: 1) `Vitality Receipts` — лічильник корисності та згасання (`vitality_score` / `decay`) фактів та правил у `SconesMemoryStore` (`core/memory/scones_store.py`). Запобігає старінню бази знань та відсікає мертвий контекст; 2) `Working-Tree Overlay` — формула `effective_state = AST(base_commit) ⊕ fresh_parse(git_diff)` для миттєвої видимості незбережених змін без повного реіндексації проекту; 3) Розподіл ролей: Antigravity проектує архітектуру та специфікації, Денчік є головним білдером та конструктором усіх агентів. | 🔒 LOCKED |
| **DEC-046** | Working-Tree AST Symbol Index & Dynamic Overlay Engine (`core/analyzers/ast_overlay_engine.py`) | **Детермінована локальна індексація символів без звернення до LLM**: 1) Формула `Effective AST = Base Index ⊕ Fresh Parse (Git Diff)` за патерном Entire Graph: кешований AST для незмінних файлів + блискавичний парсинг незакоміченого диффу; 2) Однокрокове розв'язання символів `dnk_resolve_symbol(name)` (визначення, сигнатура, callers, callees) замість 5-8 пошукових викликів grep; 3) Асиметричне оновлення ребер: вихідні виклики та визначення оновлюються на льоту, вхідні ребра від незмінних файлів зберігаються. | 🔒 LOCKED |
| **DEC-047** | Sovereign Clean-Room Media Studio (M2 Protocol & GCP Vertex AI Engine) | **Суверенна медіа-студія у `services/dnk_media`**: чиста кімната (AGPL-3.0 імунітет, 0 сирих Rust файлів SeeCut), Pydantic M2 протокол блокування ревізій (`revision`, `operationId`), Google Cloud TTS (український голос `Chirp3-HD-Achernar`) + Vertex AI Gemini, FFmpeg 8.1.2 + Pillow 13.0 скляні плашки та вертикальний рендеринг 9:16 reels з 1 виклику FastMCP. | 🔒 LOCKED |
| **DEC-048** | Sovereign Clean-Room Reverse Engineering Harness (REA + Helix 4 Hard Gates) | **Автономний харнес реверс-інжинірингу в `core/cleanroom_re/`**: 1) Ізоляція донорів у `../DNK_Vibe/` через `safe_repo_clone.py`; 2) Асиміляція інструментів `morluto/rea` (404k⭐, MIT) через FastMCP bridge (`rea-agents`); 3) Helix 4 Hard Gates (`scripts/system/helix_re_gate_runner.py`): Exit code 2 бар'єр (Spec-first, Zero-code contamination); 4) Двотермінальний автономний запуск: Денчік (`denchik.sh`) конструює модулі харнесу, Гєрич проводить аудит бібліотеки. | 🔒 LOCKED |
| **DEC-049** | Zero-Loss Spatial Pinning Protocol & Visual Brain SSOT (`core/canvas/canvas_pin.py`) | **Атомарна фіксація рішень та задач із чату безпосередньо у візуальне полотно `docs/canvas/dnk_brain.canvas`**. Запобігає «розмовній амнезії»: жодна домовленість фаундера з агентами не вважається прийнятою без створення або оновлення ноди через `canvas_pin.py`. Детермінований захист від циклів алгоритмом Кана, двостороння синхронізація з `apps/canvas/` через SSE-міст (`canvas_bridge.py`) та підтримка JSON Canvas 1.0. | 🔒 LOCKED |
| **DEC-051** | Denchik Iron Man Super-Builder Engine & Canvas Multi-Agent Swarm Bridge | **Суверенний екзоскелет Денчіка (`core/iron_man/`) та SSE Bridge (`scripts/system/canvas_bridge.py` v2.0.0)**: 1) `MathDistiller` (вилучення AST і FSM інваріантів); 2) `CodeModeSandbox` (ізольований запуск Python у пам\x27яті без bloat tool-calls); 3) `SotaLens` (clean-room аудит ліцензій та донорів у `../DNK_Vibe/`); 4) `GoldfishGate` (машинний доказ `RCPT-...` перед закриттям задач); 5) Рантайм-маршрутизація 4 агентів ростера на полотні. | 🔒 LOCKED |
| **DEC-050** | Automated Pre-Commit Adversarial Quality Gate & Anti-Tautology AST Shield | **Двоконтурний локальний цензор перед закриттям задач агентом**: 1) `anti_tautology_guard.py` — AST-сканування тестових наборів на відсутність тавтологій (`assert True`, порожні тести, неавторизовані скіпи); 2) `auto_precommit_guard.py` — автоматичний прогін 8 системних перевірок (гігієна Git, регресійні тести, відсутність абсолютних шляхів `/Users/...`); 3) Обов'язкова умова закриття таски Денчіком — exit code 0 обох цензорів. | 🔒 LOCKED |
| **DEC-052** | Sovereign JIT Agent Paradigm & In-RAM Code Mode | **Депрекація розмовних чат-роїв (CrewAI/ChatDev) на користь Single Sovereign JIT Agent (Денчік)**. Базовий контекст промпту ≤ 5,200 токенів. Динамічне розкриття інструментів on-demand (`tool_search` / `tool_describe`). Обробка та фільтрація важких даних у Python RAM через FastMCP `execute_code` (-98.4% токенів, 0 токенів витоку). Ефемерні Goldfish-воркери (≤ 20k токенів) для ізольованого pre-commit цензору та TDD-циклів. | 🔒 LOCKED |
| **DEC-053** | Parallel Candidate Isolation Protocol (Two-Phase Commit & Anti-Collision) | **Заборона паралельного запису двох агентів у єдиний цільовий файл (Anti-Race Condition)**. Паралельні задачі зобов'язані декларувати роздільні файлові маніфести або писати в кандидати `docs/audit/candidates/<agent_id>/`. Фінальний комміт у спільний SSOT здійснюється виключно координатором/оркестратором після детермінованого аудиту. Заборонено запуск браузерних двигунів (`browser_exec`, Chromium) під час текстових/кодових аудитів. | 🔒 LOCKED |
| **DEC-054** | Gerych Prime Deprecation & Archival Transition (Denchik Sovereign SSOT) | **Офіційна депрекація активного білдера Gerych Prime та закріплення Denchik як єдиного Sovereign Master Developer**. Gerych переведено в режим Cold Knowledge Archive (тільки читання та історичний аудит логів). Кодова активність, генерація сервісів та TDD-цикли виконуються виключно Денчіком (`scripts/system/denchik.sh`) через екзоскелет `core/iron_man/`. `scripts/system/gerych.sh` виводить депрекейшн-попередження. | 🔒 LOCKED |
| **DEC-056** | Triggered Clean-Room Donor Scout Protocol (SotaLens + DNK_Vibe) | **Алгоритмічний імпорт рішень із GitHub через ізольований зовнішній карантин `../DNK_Vibe/`**. Пошук запускається виключно за тригером високої алгоритмічної складності (>200 рядків, AST/Canvas/Video/Math). Заборонено для CRUD та Polaris. Автоматичний аудит ліцензій (тільки MIT/Apache-2.0/BSD через `SotaLens.audit_license()`). Клонування строго через `safe_repo_clone.py --depth 1`. Робочий репозиторій `DNK_HUB` залишається 100% чистим. Після вилучення математичного алгоритму карантинна папка негайно видаляється. | 🔒 LOCKED |
| **DEC-057** | Senior Dev Solution Ladder & Anti-Generative Bloat Protocol (Ponytail Assimilation) | **6-щаблева драбина рішень лінивого сеньйора перед написанням коду**: 1) YAGNI (викинути непередбачену гнучкість); 2) Reuse (перевикористати наявний компонент репо); 3) Stdlib (нативний Python stdlib / HTML5 замість зовнішніх бібліотек); 4) Existing Deps (тільки встановлені залежності, заборона нових пакетів без схвалення); 5) One-Liner (пряма простота над зайвими обгортками); 6) Minimal Code + 1 Test. Заборона мертвих `// TODO:` ➔ заміна на обов'язковий формат `# shortcut: <ліміт>, trigger: <подія>`. 4-пунктова рубрика рев'ю (What / Problem / Fix / If skipped). | 🔒 LOCKED |
| **DEC-058** | Hybrid Elephant-Goldfish JIT Architecture & ThoughtDAG Context Wires (thoughtdag + single-agent-loop assimilation) | **Двоконтурна архітектура суверенного розробника (Денчік)**: 1) **Elephant Orchestrator**: Денчік як єдине ядро коду (контекст ≤ 6,000 токенів), що керує виконанням; 2) **Goldfish Tool-Workers**: Доменні воркери (`dnk_shopify`, `dnk_media`, `gerych_auditor`) викликаються строго через ізольовані субпроцеси за патерном `04-as-tool.md` і повертають чистий JSON-receipt (0 витоку пам'яті чи схем); 3) **ThoughtDAG Disk/SQLite Wires**: Граф задач персиститься на диску/SQLite, у промпт потрапляє тільки активний вузол + прямі батьки (≤ 1,500 токенів), блокуючи Compaction Amnesia та отруєння рантайму. | 🔒 LOCKED |
| **DEC-055** | Denchik Super-Builder Protocol v3 (MASE + In-RAM FastMCP + SCONES Gate) | **4-фазний непорушний конвеєр виконання інженерних задач для Денчіка**: Phase 1 — In-RAM Deconstruct (`execute_code` для аналізу таски та зрізів з 0 спалених токенів); Phase 2 — Working-Tree AST Overlay (0.05с пошук символів через `SkillsBridge` та читання зрізів); Phase 3 — Atomic TDD & Zero-Tautology Pass (тести з реальними `assert` + `anti_tautology_guard`); Phase 4 — SCONES Memory & Pre-Commit Censor (`scones_remember`, 8/8 гейтів `auto_precommit_guard`, генерація машинного `RECEIPT-*.json`). Заборонено починати код без Фази 1 або закривати таску без Фази 4. | 🔒 LOCKED |
| **DEC-059** | Decoupled Sovereign Agent Architecture (Sovereign Microkernel Engine + Lean CLI Runner) | **Розділення суверенного бізнес-ядра агента (`core/agent_kernel/` per DEC-034) та термінального рантайму**: 1) `scripts/system/denchik.sh` + `denchik_engine.sh` — єдині канонічні точки запуску Денчіка; 2) `gerych.sh` редуковано до архівного stub-перенаправлення (DEC-054); 3) Хірургічне відсікання зайвого баласту Hermes (заборона падінь через сторонні SSL/CA бандли за рахунок auto-healing у `ssl_guard.py`); 4) Прямий виклик Google Vertex AI (Gemini 3.8 Flash) без сторонніх посередників. | 🔒 LOCKED |
| **DEC-060** | Headless FastMCP Runtime Wire Harness & CLI Lifecycle Engine | **Фізична склейка ядра DNK OS (`core/harness/dnk_runtime_wire.py`, `core/harness/mcp_server.py`, `core/harness/cli.py`)**: координація NodeCanvasCore (DAG CONTRACT-002, Kahn's check), SconesMemoryStore (епізодична/семантична пам'ять) та JITSkillMounter (динамічний монтаж скілів <= 4000 токенів). Єдиний FastMCP та CLI інтерфейс (`dispatch`, `branch`, `complete`, `status`) із JSON Canvas 1.0 персистентністю. | 🔒 LOCKED |
| **DEC-061** | 4-Stage Clean-Room Donor Assimilator (Task DAG Satellite Engine) | **Автоматизація чистокімнатної асиміляції донорів (`core/harness/donor_assimilator.py`) за специфікацією `DNK Task Dag System.md`**: 1) Stage 1: Contract (AST DTO extraction); 2) Stage 2: Pure Logic (ізоляція детермінованих формул f(x)->y); 3) Stage 3: Clean Code & local test verification; 4) Stage 4: Memory Gate (exit code 0), експорт Markdown-нотатки в Obsidian з K-Plex онтологією для ручних правок користувачем, ін'єкція екстракту <= 500 токенів у Головну задачу. | 🔒 LOCKED |
| **DEC-062** | Sovereign Task Forest Dispatcher & Unified Mission Control Architecture | **Еволюція від розмовного чату до нативного диспетчера задач DNK OS (Dogfooding Fast-Path)**: 1) Відкидається побудова стороннього UI з нуля — диспетчер інтегрується як просторовий Drawer/Overlay в `apps/canvas` та `apps/web` над `apps/api/routers/tasks/forest.py`; 2) Асиміляція телеметрії з `antigravity-taskboard` (Live Cost/Token usage, Attention/Chime система, Ordered Subtasks, перевірка Files Accessed); 3) Збереження 5-рівневої таксономії (Поле ➔ Сектор ➔ Дерево ➔ Кущ ➔ Квітка) та Bottom-Up Rollup замість плаского Kanban; 4) Двоконтурний рантайм: Antigravity (Mentor/Architect) + Denchik CLI (`denchik.sh` / `core/harness/dnk_runtime_wire.py`) із єдиним джерелом правди в Task Forest DAG. | 🔒 LOCKED |
| **DEC-063** | Agent-Native Enterprise Mesh & Deterministic Approval Chains | **Асиміляція патернів Eggent 3.0 та захист від семантичної ентропії**: 1) Концепція «1 Співробітник = 1 Людина + 1 Агент» переводиться з хаотичного розмовного чату на строго типізовані шини подій Pydantic (`core/domain/agent_mesh_models.py`); 2) Впровадження `ApprovalChainGate` для послідовних багатосторонніх погоджень (Sales ➔ Legal ➔ Finance ➔ Exec) із криптографічним хешуванням (`signature_sha256`) та детекцією підміни документів mid-flight (`DocumentTamperedError`); 3) Захист точок публічного входу (пошта, lead chat, форми) через евристичний сканер непрямих ін'єкцій `PromptInjectionScanner`; 4) Відмова від пласких RAG-сховищ на 2000 файлів на користь K-Plex Compass і Task Forest із жорстким лімітом контексту (<= 4000 токенів). | 🔒 LOCKED |
| **DEC-069** | Universal Molecular Theme Deconstruction & Canonical Donor Git Worktree Engine | **Уніфікація SSOT донорів тем, Cleanroom десанітизація та двоконтурний агентивний протокол (`main` + `donor-lab`)**: 1) `DNKShopify/DNK-e.com` (`DNK-Ecom_git_mirrow`) закріплено як єдине канонічне джерело донорів у Git Worktrees (10 тем, 3 732 молекули, 100% Cleanroom); 2) `main` виступає виробничим ядром із регламентом `AGENTS.md`, а `donor-lab` — R&D лабораторією та матрицею графтингу; 3) Тріада агентів: Antigravity (Mentor/Architect), Denchik (FastMCP Builder), Gerych23 (Terminal Auditor на DNK OS Core v0.23.0, `gemini-4-argon` via `gerych4`); 4) Розгорнуто самопокращуваний воркфлоу `_Shopify_Theme_DEV_Workflow/` з автоматичним AST-сканером, екстрактором та Геном-Реєстром. | 🔒 LOCKED |
| **DEC-070** | SOTA Agent Harness Architecture & Harness² Assimilation | **Асиміляція патернів Google Cloud AI Research `harness2` (arXiv:2610.14224)**: 1) Blind Anonymized Tournament (`selection.py`) для змагального аудиту (Builder vs Auditor) без упереджень моделі; 2) `SurfaceSpec` токен-кепи (`always_on_max` ≤ 6,000) та жорстка валідація відносних шляхів `normalize_rel` у Ring-0 Pre-Tool Hook (`hermes_pre_tool_hook.py`); 3) Структурований `<experience>` дистилятор регресійних помилок у `core/skills_curator.py`. Відхилено: експоненційний оверхед $4k$ ролаутів на користь MASE ≤ 25 дій. Звіт: `docs/architecture/reports/HARNESS2_SOTA_AUDIT_AND_ASSIMILATION_REPORT.md`. | 🔒 LOCKED |
| **DEC-071** | Elixir 1.6.2 Molecular Sterilization, Transitive BFS Vault Ingestion & Staging-Lab Grafting | **Вичерпна молекулярна дистиляція та Cleanroom-стерилізація Elixir 1.6.2 DNK**: 1) Зрізано пропрієтарний Base64/RC4 DRM-пейлоад у `assets/elxr-core.js` (-17,558 B, `node --check` exit 0), ліквідовано `Shopify.license_key`; 2) 100% транзитивне замикання у `distilled_vault/elixir-1.6.2` (135 блоків, 109 сніпетів включно з 33 BFS 2-го/3-го рівнів, 66 асетів включно з 52 core ESM, 4 локалі, 0 missing deps); 3) Зґрафчено 35 чистих блоків (G2-G6 Advertorial, Listicle, Comparison Table) у `staging-lab` (`569e789`) з проходженням `shopify theme check --fail-level error` (0 помилок, exit 0). | 🔒 LOCKED |

---

## ⚖️ КРИПТОГРАФІЧНІ ЧЕКИ РІШЕНЬ (DECISION RECEIPTS)

### ⚖️ Decision Receipt: `jvr_0dc5a8cd49753128a831`

- **Subject:** Adopt Deterministic Hard Gates, Abstention Protocol, and Cryptographic Receipts (Jev Assimilation)
- **Status:** `SELECTED` | **Selected:** `jev_deterministic_receipts`
- **Confidence:** `0.93` | **Margin:** `+52.1 pts`
- **Integrity SHA-256:** `0dc5a8cd49753128a831969ecfffe70a8d672856f6c91e0a9b83b3813958ebfc`

| Rank | Candidate | Eligible | Score | Hard Gate Findings |
| --- | --- | --- | --- | --- | --- |
| 1 | `jev_deterministic_receipts` (Jev Deterministic Hard Gates & Receipts Engine) | 🟢 | 93.1 | None (Clean) |
| 2 | `raw_llm_judgment` (Raw LLM Conversational Self-Evaluation) | 🟢 | 41.0 | None (Clean) |

**Rationale:**

- Candidate 'jev_deterministic_receipts' passed all hard gates and leads with score 93.1 (margin: +52.1 pts).

---

### [🔒 LOCKED] ADR-091: DNK OS Agentic Microkernel Architecture

- **Subject:** Agentic Microkernel Architecture, 4-Layer Separation, and Pydantic SSOT Contracts
- **Status:** `[🔒 LOCKED]` (ADR-091)
- **Rationale:** Strict separation of System One (triage, compactor, gates <100ms) from System Two (generative swarm agents) and L1-L4 memory hierarchy. All core coordination governed by typed Pydantic contracts (`KernelTaskRequest`, `KernelTriageReceipt`, `KernelDecisionReceipt`, `KernelCompletionReceipt`). Zero standing context bloat and strict negative scopes.
- **Reference:** `docs/architecture/adr/ADR-091-DNK-OS-AGENTIC-MICROKERNEL-SPECIFICATION.md`

---

### [🔒 LOCKED] ADR-092: Canonical Local Port & Address Registry (SSOT)

- **Subject:** Local Port Isolation for `DNK_HUB` Core Services and `../DNK_Vibe` Repositories
- **Status:** `[🔒 LOCKED]` (ADR-092)
- **Rationale:** Prevents port collisions (`3000`, `5173`, `8000`) across concurrently running apps. Core `DNK_HUB` services hold `3000`/`5173`/`8000`–`8003`, while every repository in `../DNK_Vibe/` must be registered in `core/registry/port_registry.yaml` within its dedicated `54100–54999` block (e.g. Open Design Local on `54301` Daemon / `54330` Web UI) before launch.
- **Reference:** `core/registry/port_registry.yaml`, `docs/notes/MY TASKS/0. Питання Архітектури/DNK_Local_Port_Registry_SSOT.md`

---

### [🔒 LOCKED] ADR-093: 5-Year Shopify Theme Architecture Standard (2026–2031) — Horizon & Shopify Canvas

- **Subject:** 100% Block-First Horizon (v4.3+) / Theme Blocks 2.0 Architecture with 4-Layer Formula for Shopify Canvas & AI Sidekick
- **Status:** `[🔒 LOCKED]` (ADR-093 / DEC-015)
- **Rationale:** Ensures 5-year forward compatibility with Shopify Canvas AST mapping (`Canvas Frame -> blocks/_group.liquid`), AI Sidekick `@theme` block generation, and `liquid_doc` (`{% doc %}`) static prop typing, while guarding against DOM-Soup (nesting cap ≤ 3–4 levels, static `_product-card` blocks in collection loops), Customizer merchant paralysis (Compound Preset Blocks), and JSON bloat via `theme_cleanroom_neutralizer.py`. Deterministic e-commerce logic (`<cart-drawer>`, `<variant-selects>`, Faceted Filtering, Checkout UI Extensions) remains strictly isolated from user microblocks.
- **Reference:** `docs/architecture/adr/ADR-093-SHOPIFY-CANVAS-5YEAR-THEME-ARCHITECTURE.md`, `docs/notes/MY TASKS/0. Питання Архітектури/Журнал/201026_shopify_5year_horizon_canvas_theme_architecture.md`

---

### [🔒 LOCKED] DEC-017: Casaio 1.1.0 Liquid Syntax & JSON Schema Sanitization

- **Subject:** Fixing 404 Fallback in Shopify Theme Customizer for `donor/casaio-1.1.0`
- **Status:** `[🔒 LOCKED]` (DEC-017)
- **Rationale:** Shopify Customizer automatically redirects to `/404` when `templates/index.json` fails compilation due to Liquid syntax errors or invalid JSON schemas in sections/blocks. Identified and resolved root causes: (1) Liquid `#` tag syntax errors in `blocks/_slide.liquid` and `snippets/variant-main-picker.liquid`, (2) Illegal trailing commas in `{% schema %}` JSON presets in `sections/slideshow.liquid`, `sections/section.liquid`, `sections/carousel.liquid`, and `sections/footer.liquid`, (3) Type error in `snippets/product-variations-picker.liquid`, (4) Missing keys in `locales/en.default.json` and `locales/en.default.schema.json`. Verified with `shopify theme check` (0 errors) and pushed to GitHub `origin donor/casaio-1.1.0`.
- **Reference:** Commit `b648431`, `services/dnk_shopify/DNK-e.com`

---

### [🔒 LOCKED] DEC-018: Node-Based Infinity Canvas Chat DAG Architecture (TaskForest + Node-RED Hybrid)

- **Subject:** Architectural Invariants for Chat-as-a-Node, Document/Task Spawning, and TaskForest DAG Integration
- **Status:** `[🔒 LOCKED]` (DEC-018)
- **Rationale:**
  1. *Decoupled Virtualization Guard*: Full-state streaming chat components are prohibited from direct in-node DOM embedding inside ReactFlow/Canvas. Chat nodes act as lightweight state cards; focused chat sessions run via a dedicated slide-out drawer or floating portal backed by SSE / FastMCP to prevent canvas FPS degradation.
  2. *Acyclic DAG vs Multi-Turn Chat*: Conversational multi-turn history is decoupled from the topological DAG structure. Chat emits discrete `Action Events` (Task Proposal, Decision Extract, Markdown Doc), which spawn downstream DAG nodes (`TaskForestNode`, `DocumentNode`) with deterministic parent-child edges.
  3. *SSOT Engine*: `services/dnk_node_tasks` (`graph_engine.py`, `conversational_intake.py`) serves as headless backend SSOT, rendered via `apps/web/components/canvas/TaskForestCanvas.tsx`.
- **Reference:** `docs/notes/MY TASKS/TASK-DNK-CANVAS-20261023-001_SOTA_CANVAS_CHAT_DAG_ASSIMILATION.md`

---

### [🔒 LOCKED] DEC-019: Tri-Audience Documentation & Client Delivery Portal (Fumadocs UI + Fern RBAC)

- **Subject:** Unified Documentation, Client Specification Builder, and Agent `/llms.txt` Delivery Portal
- **Status:** `[🔒 LOCKED]` (DEC-019)
- **Rationale:**
  1. *JSON/DB SSOT in `apps/api`*: Client specifications, milestones, and tickets are stored in `apps/api/routers/docs_portal.py` (`cache/docs_portal_db.json`) with live web creation and editing.
  2. *Full Interactive Client Mode*: Clients can both review/sign-off milestones & tickets (`Approve` / `Request Changes` with comments and hours tracking) and submit new specifications/tickets directly from `apps/web/app/docs/page.tsx`.
  3. *Full Email/Password RBAC*: Authenticated via HMAC-SHA256 signed Bearer tokens (`POST /api/v1/docs/auth/login`) with strict server-side filtering (`role=god | agent | client`) to prevent client payload leakage in DevTools.
  4. *Auto TaskDNA & TaskForest Conversion*: Approving a specification or ticket automatically synthesizes a `GERYCH_TASK_TEMPLATE v2.5` `TaskDNA` contract, mutates a live `TaskForest` Flower node (`apps/api/routers/tasks/forest.py`), and exposes zero-HTML Markdown via `/api/v1/docs/llms.txt` and `/api/v1/docs/raw/{slug}.md`.
- **Reference:** `apps/api/routers/docs_portal.py`, `apps/web/app/docs/page.tsx`

---

### [🔒 LOCKED] DEC-020: Gerych Runtime Model Tiering & Cold Boot Fast-Path

- **Subject:** Model escalation chain and MCP background decoupling for Gerych CLI/Daemon.
- **Status:** `[🔒 LOCKED]` (DEC-020)
- **Rationale:**
  1. *Daily Workhorse*: `gemini-3.8-flash` via Vertex AI is set as primary default for high throughput, sub-5s cache-accelerated latency, and low cost.
  2. *Architectural Heavy Weapon*: `gemini-4-argon` is reserved for Tier-3 architectural audits and high-complexity refactoring sessions.
  3. *Resilient Fallback Chain*: `gemini-3.8-flash` ➔ `gemini-3.7-flash` ➔ `gemini-4-argon` ➔ `meta/llama-3.2-11b-vision-instruct` (NVIDIA NIM).
  4. *Zero-Hanging Cold Boot*: Unmounted 7 heavy background MCP servers (`notion`, `postgresql`, `open-design`, etc.) from standing boot, slashing cold startup from 25s down to 4.1s.
- **Reference:** `~/.hermes/config.yaml`, `core/orchestrator/agents/gerych_prime/config.yaml`

---

### [🔒 LOCKED] DEC-021: Standing Context Reduction & Focused Platform Toolsets (Rule 4 Enforced)

- **Subject:** Eliminating standing context bloat (from 34.3k to 18.8k tokens) via platform toolset pruning, focus posture, and SOUL.md LOD distillation.
- **Status:** `[🔒 LOCKED]` (DEC-021)
- **Rationale:**
  1. *Platform Toolsets Constraint (`platform_toolsets.cli`)*: Replaced monolithic 77-tool `hermes-cli` bundle with 6 core toolsets (`terminal`, `file`, `web`, `skills`, `dnk_swarm`, `delegation`), pruning 28 unused tools (computer_use, clarify, session_search, desktop_ui, browser_*, tts, kanban_*, etc.) and slashing tool schema tokens from 23,673 to 9,461 (-14,212 tokens).
  2. *Coding Posture Focus & JIT Skills*: Configured `agent.coding_context: focus` and disabled non-coding/consumer skills (`apple`, `gaming`, `smart-home`, `hyperframes*`, `social-media`), cutting skills prompt tokens from ~14,500 down to 3,329.
  3. *SOUL.md Level-of-Detail (LOD)*: Modularized `SOUL.md` from 15.9KB (142 lines) down to 5.9KB (79 lines) by delegating governance rules to [AGENTS.md](../../AGENTS.md) as Single Source of Truth, saving ~3,000 prompt tokens.
  4. *Total Impact*: Total standing overhead slashed by **-15,502 tokens (-45%)**, from 34,346 tokens down to ~18,844 tokens at Step 0.
- **Reference:** `core/orchestrator/agents/gerych_prime/config.yaml`, `~/.hermes/config.yaml`, `core/orchestrator/agents/gerych_prime/SOUL.md`

---

### [🔒 LOCKED] DEC-022: DNK_HUB Unified SSOT & One-Way Two-Tier Export Guard

- **Subject:** Elimination of Split-Brain Anti-Pattern between `DNK_HUB` (Tier 1) and `../DNK_OS_APP` (Tier 2).
- **Status:** `[🔒 LOCKED]` (DEC-022)
- **Rationale:**
  1. *Single Source of Truth*: `DNK_HUB` is the sole development engine, knowledge factory, and code SSOT. All prompt updates, microkernel features, and specifications are authored and tested exclusively inside `DNK_HUB`.
  2. *Assimilation of Standalone Artifacts*: Consolidated 7 early core specifications (`01_CORE_AND_ACTION_BUS_SPEC`..`07_SHOPIFY_AGENTIC_THEME_ARCHITECTURE_SPEC`) into `docs/specs/`, 12 foundational ADRs (`ADR-001`..`ADR-012`) into `docs/adr/`, documentation templates (`Do not Delete - Example.md`, `Do not Delete - Draft.md`) into `docs/templates/`, and task trees into `docs/notes/task_forest/`.
  3. *Zero Manual Dual-Editing*: Editing files manually in `../DNK_OS_APP` is strictly deprecated. Clean standalone releases are generated exclusively via one-way packaging: `python3 scripts/export_standalone_app.py ../DNK_OS_APP`.
- **Reference:** `docs/architecture/TWO_TIER_DEVELOPMENT_PROTOCOL.md`, `scripts/export_standalone_app.py`

---

### [🔒 LOCKED] DEC-023: DNK Polaris-Spatial Design System (DPS-DS) & Core Synthesis

- **Subject:** Dual-Optics Design System & Core Synthesis uniting Shopify Polaris with Dark Teal Infinite Spatial Canvas.
- **Status:** `[🔒 LOCKED]` (DEC-023)
- **Rationale:**
  1. *Token SSOT*: Design tokens (Colors, Typography, Spatial Spacing, Elevations, Motion) are defined centrally in `packages/archify/schemas/dnk_polaris_design_tokens.json`.
  2. *Dual-Lens Export*: Tokens automatically compile into (a) Tailwind CSS v4 / React 19 tokens in `apps/web/src/design-system/tokens.ts`, and (b) CSS Custom Properties for Shopify Theme Blocks 2.0 (`services/dnk_shopify/DNK_Horizon_Tinker/assets/dnk-polaris-tokens.css`).
  3. *Zero-Slop UI Architecture*: Polaris Card & ResourceList patterns govern form controls and inspector drawers; Dark Teal Neo-Brutalist HUD governs `@xyflow/react` spatial canvas.
  4. *Clean Standalone Delivery*: Code is synthesized and tested in `DNK_HUB`, then exported to `../DNK_OS_APP` via `scripts/export_standalone_app.py` under the Two-Tier Invariant (DEC-022).
- **Reference:** `docs/notes/MY TASKS/TASK-DNK-APP-20261026-001_CORE_DESIGN_SYSTEM_SYNTHESIS.md`, `docs/architecture/adr/ADR-094-DNK-POLARIS-SPATIAL-DESIGN-SYSTEM.md`

---

### [🔒 LOCKED] DEC-024: Native SCONES Memory Plugin & Review-on-Stop Gate

- **Subject:** Connecting SCONES Cognitive Memory directly to Hermes Agent runtime and hardening verification gates.
- **Status:** `[🔒 LOCKED]` (DEC-024)
- **Rationale:**
  1. *Native Plugin Contract*: Created `core/hermes_agent/plugins/memory/scones/` implementing `MemoryProvider` ABC with symlink alias `dnk_hub_memory`. Hermes status confirms `Plugin: installed ✓` and `Status: available ✓`.
  2. *Active SCONES Recall*: Runtime automatically pre-fetches top lessons and 90 SOTA open-source blueprints into agent context bounded by <= 1200 tokens (LOD budget).
  3. *ScallopBot Review-on-Stop*: Deterministic pre-commit gate in `scripts/system/hermes_pre_tool_hook.py` performing zero-shot AST parse on all staged `.py` files and blocking forbidden absolute paths before commit/push.
  4. *Infinite Loop Fix*: Resolved `os.path.realpath` symlink discrepancy in `zero_waste_runner.py` and `session_sentinel.py` preventing CLI execution hangs.
- **Reference:** `docs/audit/DNK_OS_SYSTEM_MEMORY_AND_HARNESS_AUDIT_20261026.md`

---

### [🔒 LOCKED] DEC-025: Folder as Harness & Subagent Folding Protocol

- **Subject:** Assimilating Anthropic's "Folding Subagents into Main Loop" and "Folder as Harness" SOTA paradigm.
- **Status:** `[🔒 LOCKED]` (DEC-025)
- **Rationale:**
  1. *Subagent Folding*: Elimination of 12 "Org-Chart" subagents from `core/orchestrator/agents/`. Domain procedures become on-demand modular skills (`core/skills/*/SKILL.md`) under Progressive Disclosure / JIT-Tooling (ADR-007).
  2. *Triad Agent Topology*: Retain exactly 3 operational roles: (a) Antigravity (Orchestrator / Mentor), (b) Gerych Prime (Single-Loop Builder Harness), (c) Gerych Auditor (Isolated Fresh-Eyes Deterministic Verifier). Gerych Researcher is kept as an ephemeral disposable-context subagent only.
  3. *Folder as Harness Invariant*: Filesystem Markdown (`AGENTS.md`, `DECISION_REGISTRY_ADHD.md`, `task_forest/`) and SQLite WAL serve as the state machine and external memory, avoiding external black-box agent frameworks.
  4. *Anti-Pollution & Anti-Hijacking*: Enforce LOD slicing (<= 1200 tokens) and non-malleable test execution gates (`scripts/verify_all.sh`).
- **Reference:** `FOLDER_AS_HARNESS_AND_SUBAGENT_FOLDING_AUDIT.md`

---

### [🔒 LOCKED] DEC-026: Dual-Surface Ingestion & Agent-Native Assimilation Contract

- **Subject:** Assimilation of BuilderIO/agent-native patterns into DNK OS Python Microkernel without TypeScript/Nitro rewrite trap.
- **Status:** `[🔒 LOCKED]` (DEC-026)
- **Rationale:**
  1. *Dual-Surface Actions*: Actions over canvas and task nodes are defined once via Pydantic schemas in `apps/api/routers/` and exposed simultaneously as FastMCP Tools for agents and React hooks for the web UI.
  2. *Voice-to-TaskDNA Pipeline*: Voice/text capture routes through existing `apps/api/routers/intake.py` (`POST /api/v1/intake`) -> `core/harness/intake.py` (Ambiguity Gate & Grill-Me Session) -> `core/orchestrator/task_dna_lifecycle.py` (DAG node decomposition).
  3. *Zero-Nitro Invariant*: Reject direct importation of TypeScript Nitro server. Python microkernel remains SSOT for execution, AST gates, and SCONES memory.
- **Reference:** `AGENT_NATIVE_KERNEL_AND_VOICE_INTAKE_BLUEPRINT.md`

---

### [🔒 LOCKED] DEC-027: Obsidian Visual Shell Harness & Dual-Vault SOTA Integration

- **Subject:** Obsidian as native Spatial PKM and Visual Shell Harness for DNK OS with headless swarm automation.
- **Status:** `[🔒 LOCKED]` (DEC-027)
- **Rationale:**
  1. *Dual-Surface Architecture*: Obsidian acts as the spatial thinking cockpit (System 1) with Excalidraw, K-Plex, and Excalibrain, while the Python microkernel (`core/`, `apps/api/`) acts as deterministic execution (System 2).
  2. *The 11-Plugin SOTA Stack*: Strictly standardized roster (`obsidian-excalidraw-plugin`, `k-plex`, `excalibrain`, `excalidraw-extras`, `dataview`, `obsidian-hover-editor`, `mermaid-interactive-zoom`, `obsidian-local-rest-api`, `obsidian42-strange-new-worlds`, `quickadd`, `remotely-save`) with 3 CSS snippets (`dnk-flat-green`, `shopify-polaris-helix`, `full-width-view`).
  3. *Programmatic Swarm Bridge*: Autonomous agents programmatically query active notes and dispatch commands (`app:reload`, `open`) via Obsidian Local REST API / FastMCP on port `27123`.
  4. *Monorepo SSOT & Canonical 8-Root Invariant*: `DNK_HUB` is the sole development SSOT with notes housed in `docs/notes/`. Standalone release `DNK_OS_APP` receives 100% mirrored `.obsidian/` configurations and visual templates.
- **Reference:** `OBSIDIAN_VISUAL_SHELL_HARNESS_SPEC.md` | Skill: `core/skills/obsidian_visual_shell_harness/SKILL.md`

---

### [🔒 LOCKED] DEC-028: DNK OS Living Bio-Organism Architecture & Single Foundry Unification

- **Subject:** Transformation of DNK OS into a modular, self-learning living bio-organism (Cybernetic Bio-Robot) and 100% consolidation into DNK_HUB SSOT.
- **Status:** `[🔒 LOCKED]` (DEC-028)
- **Rationale:**
  1. *Single Foundry SSOT*: Complete elimination of Split-Brain reality. DNK_HUB is the sole development and R&D forge. All unique specifications and Excalidraw whiteboards from DNK_OS_APP are transferred and unified. DNK_OS_APP is designated exclusively as the automated compile target of scripts/export_standalone_app.py.
  2. *The 6 Living Organ Systems*:
     - Cerebrum & Decision Will: Dual mind (Maxim + Antigravity) with Epistemic Armor and Presupposition Inversion.
     - Central Nervous System: FastAPI microkernel + Action Bus (Event Envelope v1) + Door 8642 Gateway.
     - Sensory Organs: Headless AST symbol radar (<20ms), Obsidian/Excalidraw PKM, 2039 SOTA repo FTS5 radar (<15ms).
     - Immune System: Review-on-Stop zero-context git diff gate, Process Guard & Zombie Hunter (is_pid_alive auto-reap), scripts/verify_all.sh exit code 0.
     - Executive Motor Organs: 3 specialized workhorses (services/dnk_shopify, services/dnk_media, services/dnk_distribution) driven by Gerych Prime MASE <= 25 slices.
     - Living Cognitive Memory: Fast SQLite WAL session loop + SCONES 3-tier bio-sleep dream cycle (NREM clustering + REM spreading activation + mathematical half-life decay).
  3. *Knowledge-to-Agentic-Ideas Engine*: Continuous transformation of static notes and whiteboards into auto-synthesized GERYCH_TASK_TEMPLATE v2.5 specifications with closed-loop memory sync.
- **Reference:** `docs/notes/MY TASKS/0. Питання Архітектури/Журнал/261026_dnk_os_living_bio_organism_architecture.md`

---

### [🔒 LOCKED] DEC-029: Agentic Bio-Organism Core v1 & Dual-Surface Canvas-Chat Orchestration Engine

- **Subject:** Dual-Surface symbiosis between Human Cockpit (Obsidian Excalidraw) and Autonomous Swarm (FastMCP Microkernel), bi-directional live node synchronization, and zero-bloat machine mechanics.
- **Status:** `[🔒 LOCKED]` (DEC-029)
- **Rationale:**
  1. *Dual-Surface Symbiosis*: Obsidian Excalidraw infinite canvas (System 1) serves as the spatial thinking & human steering interface, while FastAPI / FastMCP microkernel (System 2) executes deterministic MASE ≤ 25 tool slices.
  2. *Bi-directional Chat-to-Canvas Stream*: Chat logs strictly follow the ADHD Protocol (Action-First, zero flattery, 1 screen max) and dispatch Event Envelope v1 events to live update Node Canvas statuses (`Planned` ➔ `In_Progress` ➔ `Review` ➔ `Completed`).
  3. *Zero-Bloat Agent Mechanics SSOT*: System mechanics and technical data are stored in MRH-annotated Markdown & typed Pydantic contracts (`docs/architecture/specs/`), readable by any agent in <10ms with zero standing overhead (≤ 6k tokens).
  4. *Pruning Obsolete Solutions*: Permanent elimination of custom proprietary canvas engines from scratch, split-brain repos, TypeScript Nitro, and unauthorized microservices.
- **Reference:** `docs/architecture/specs/DNK_AGENTIC_BIO_ORGANISM_CORE_V1_SPEC.md` | Whiteboard: `docs/notes/MY TASKS/1. АРХІТЕКТУРА/14. Просторовий інтерфейс та Visual Shell/Excalidraw/003_DNK_Agentic_Bio_Organism_Core_v1.excalidraw.md`

---

### [🔒 LOCKED] DEC-034: Sovereign Agent Microkernel (< 400 LOC) & Hermes Deprecation Architecture

- **Subject:** Replacement of 291 MB monolithic Hermes framework with a protocol-first, sovereign Python microkernel (`core/agent_kernel/`) based on frontier SOTA audit.
- **Status:** `[🔒 LOCKED]` (DEC-034)
- **Rationale:**
  1. *MCP as Universal Tool Bus*: Elimination of custom tool wrappers in favor of Anthropic's Model Context Protocol (JSON-RPC 2.0 stdio/SSE).
  2. *Stateless Function Handoffs*: Adoption of OpenAI Swarm pattern (`AgentHandoff`) for subagent delegation without background supervisor bloat.
  3. *Structured Task Ledger*: Microsoft Magentic-One 10-line Markdown ledger to prevent goal drift and context pollution.
  4. *Prompt Caching & Leaf Isolation*: Google/Anthropic caching + disposable leaf subagents for zero-waste execution.
  5. *Clean Model Transport*: Meta Llama Stack-inspired unified `httpx.AsyncClient` supporting Gemini 3.8 Flash, Claude 3.7, GPT-5.
- **Reference:** `docs/research/SOTA_FRONTIER_AGENT_ARCHITECTURES_2026_REPORT.md` | Matrix: `docs/tech/sota_assimilation/FRONTIER_LABS_AGENT_MATRIX_2026.json`

---

### [🔒 LOCKED] DEC-036: Code Execution with MCP (Anthropic Code Mode / CE-MCP)

- **Subject:** Adoption of Code Execution over MCP (Code Mode) for high-efficiency, zero-bloat agent tool orchestration.
- **Status:** `[🔒 LOCKED]` (DEC-036)
- **Rationale:**
  1. *98.7% - 99% Token Reduction*: Eliminates upfront JSON schema dumps (15k-40k tokens) by treating MCP tools as on-demand Python/TS library interfaces.
  2. *Zero Context Pollution (Data Isolation)*: Heavy intermediate payloads (database rows, 200KB documents) remain in execution runtime memory; only the final distilled answer returns to LLM context.
  3. *Single-Turn Orchestration*: Complex multi-step operations (loops, conditionals, transformations, retries) execute in 1 step via deterministic code instead of N prone-to-drift LLM inference roundtrips.
  4. *FastMCP Synergy*: FastMCP serves as the declarative server development framework (`@mcp.tool()`), while Code Execution serves as client-side programmatic orchestration.
- **Reference:** `docs/notes/054_code_execution_of_mcp_architecture.md` | Skill: `core/skills/mcp_code_execution/SKILL.md`

### [🔒 LOCKED] DEC-038: Elephant-Goldfish Model (EGM) Dual-Phase Architecture & Zero-Context Review Protocol

- **Subject:** Dual-surface split between Elephant (Deep Context Spec Design) and Goldfish (Zero-Context Isolated Swarm Review) to eliminate AI slop velocity in vibecoding.
- **Status:** `[🔒 LOCKED]` (DEC-038)
- **Rationale:**
  1. *Elephant Invariant (Strict Zero Code)*: Elephant sessions maintain long-horizon architectural context and interactively draft Markdown specs (`docs/designs/*.md`). Writing application code in this phase is strictly prohibited.
  2. *Goldfish Swarm (Zero-Context Isolation)*: Ephemeral, isolated subagents are launched with zero conversational history. They ingest exclusively the draft spec and target code to audit 4 vectors: Zoom Out (YAGNI/reuse), Comprehension (clarity/unambiguity), Design Critic (resilience/quotas), and Implementation Readiness.
  3. *Post-Implementation Drift Reporting*: Automatic diff between physical code and accepted design spec via drift analysis (`/egm-drift-report`) to prevent architectural degradation.
- **Reference:** `docs/tech/sota_assimilation/google_elephant_goldfish_model.md` | Skill: `core/skills/dnk_elephant_goldfish/SKILL.md`

---

### [🔒 LOCKED] DEC-039: Native Shopify CLI Tunnel Preview for Human Canvas (Zero Simulation Emulator)

- **Subject:** Replacing synthetic Craftile/AST Liquid simulation engines with headless native Shopify CLI (`shopify theme dev`) embedded in WebView/iFrame.
- **Status:** `[🔒 LOCKED]` (DEC-039)
- **Rationale:**
  1. *Zero Simulation Code Invariant*: Abandon client-side Liquid/Shopify state simulation. Liquid is rendered natively by Shopify Cloud via official development theme tunnel.
  2. *Native Shopify CLI Bridge*: Background worker executes `shopify theme dev --store <dev-store> --theme-editor-sync` exposing `http://127.0.0.1:9292` with live Hot Reload and WebSocket file synchronization.
  3. *WebView / iFrame Surface*: Front-end Canvas (Studio/Tauri/Next.js) renders the local proxy inside an isolated iFrame/WebView, ensuring 100% visual and functional fidelity (real products, real cart drawer, real OS 2.0 theme blocks).
  4. *3-Flaws Boundary Protection*:
     - *Latency mitigation*: Local file watcher + fast APFS updates (<400ms).
     - *Frame framing/CSP guard*: Restrict browsing inside preview proxy boundaries, prevent unauthorized checkout breakout.
     - *Session hygiene*: Automatic lifecycle management and cleanup of ephemeral development themes on process exit.
- **Reference:** `docs/notes/MY TASKS/0. Питання Архітектури/Журнал/271026_shopify_cli_native_canvas_tunnel_architecture.md`

### [🔒 LOCKED] DEC-040: Task Forest & Spatial Canvas DAG Synchronization Engine (Chat-to-DAG Event Mesh)

- **Subject:** Dual-surface synchronization converting natural language chat dialogues and agent executions into persistent Task Forest and JSON Canvas 1.0 DAG graphs.
- **Status:** `[🔒 LOCKED]` (DEC-040)
- **Rationale:**
  1. *Zero Ephemeral Loss (Anti-Amnesia)*: Every goal, subtask, tool call, and decision from chat sessions is persisted as a structured `ThoughtNode` (CONTRACT-002) rather than an abandoned line in transcript logs.
  2. *Anti-Spaghetti Geometric Layout*: Fixed column stride (460px), card width (250px), and automated topological clustering eliminate visual noise and prevents node explosion.
  3. *5-Phase TaskDNA Gated Lifecycle*: Strict safety barrier (`RESEARCH_RAW` -> `AUDIT_GATE` -> `FOUNDER_APPROVAL` -> `LIBRARIAN_INGEST` -> `COMPLETED`) prevents untrusted data from mutating memory.
  4. *Deterministic FastMCP Projection*: `core/canvas/canvas_agent.py` updates `.canvas` files programmatically in 1 step without incurring LLM token overhead during ordinary chat turns.
- **Reference:** `docs/architecture/specs/DNK_TASKFOREST_CANVAS_DAG_SYNTHESIS.md` | Tests: `tests/canvas/test_workflow_dag_schemas.py`

### [🔒 LOCKED] DEC-041: Living Spec Ratchet Engine & 3-Zone Evolutionary SSOT

- **Subject:** Programmatic execution engine (`core/agent_kernel/spec_ratchet.py`) bridging conversational discoveries into living domain specifications and verified code.
- **Status:** `[🔒 LOCKED]` (DEC-041)
- **Rationale:**
  1. *Elimination of Knowledge Graveyard*: Prevents disconnected markdown notes by routing all technical proposals into 3-zone domain living specs (`services/*/SPEC.md`).
  2. *3-Zone Evolutionary Separation*:
     - `LOCKED_INVARIANTS`: Immutable business contracts (Zero Broken Checkout, Storefront API contracts).
     - `ACTIVE_CAPABILITIES`: Working, tested modules and endpoints.
     - `PENDING_MUTATIONS`: Structured delta proposals waiting for execution.
  3. *Additive-Only Strangler Fig Pattern*: Enforces non-breaking integration; new features enter pending queue and only promote to active after 100% test pass.
  4. *Autonomous Task Ignition*: Generates canonical Gerych task files directly from pending proposals, bridging the execution gap.
- **Reference:** `services/dnk_shopify/SPEC.md` | Engine: `core/agent_kernel/spec_ratchet.py` | Tests: `tests/core/test_spec_ratchet.py`

### [🔒 LOCKED] DEC-042: Denchik Sovereign Master Developer Architecture

- **Subject:** Sovereign Master Developer Agent Package (`denchik`) and Autonomous Engineering Execution Engine.
- **Status:** `[🔒 LOCKED]` (DEC-042)
- **Rationale:**
  1. *Sovereign Profile Decoupling*: Denchik is fully decoupled from temporary symlinks into a sovereign profile package (`core/orchestrator/agents/denchik/`) containing dedicated `SOUL.md`, `agent_card.yaml`, and `config.yaml`.
  2. *SOTA Engineering Tool Whitelist*: Configured with native FastMCP Code Mode sandbox (`sandbox_code_mode`), SCONES memory synchronization (`scones_memory`), AST architecture symbol resolver (`repo_map`), Task Forest Obsidian Canvas DAG sync (`canvas_agent`), and git diff verification (`git_researcher`).
  3. *Review-on-Stop Quality Gate*: Mandatory workspace diff inspection and deterministic quality gate verification (`scripts/verify_all.sh` / targeted test suites) prior to task completion, eliminating verbal hallucinations.
  4. *Zero-Waste CLI & Dual Kernel*: Seamless launch via global `denchik` binary, supporting both the full streaming TUI and the ultra-lightweight `< 400 LOC` Sovereign Microkernel (`denchik --microkernel`).
- **Reference:** `core/orchestrator/agents/denchik/SOUL.md` | `core/orchestrator/agents/denchik/agent_card.yaml` | `scripts/system/denchik.sh` | Research: `docs/research/NOUSRESEARCH_HERMES_VS_DENCHIK_CORE_SOTA_AUDIT_2026.md`

### [🔒 LOCKED] DEC-043: Headless Node-Based Canvas Core Runtime (CONTRACT-002 & OCC)

- **Subject:** Sovereign Headless Graph Runtime (`core/canvas/node_canvas_core.py`) coordinating spatial DAG state, OCC concurrency, chat event synchronization, and JSON Canvas 1.0 projections.
- **Status:** `[🔒 LOCKED]` (DEC-043)
- **Rationale:**
  1. *Headless Graph Invariant*: Decouples the mathematical DAG state from visual UI layers, rendering into Obsidian JSON Canvas 1.0 and Excalidraw deterministically.
  2. *Kahn Cycle Rejection*: Topological ordering with strict cycle detection on every `add_edge()` prevents circular agent execution deadlocks.
  3. *Optimistic Concurrency Control (OCC)*: Multi-version revision tracking (`version`, SHA-256 ETag) and 3-way graph merging resolve simultaneous edits between human (Obsidian) and AI (chat) without data loss.
  4. *CONTRACT-002 Context Slicing*: `extract_subdag()` and `compile_context_for_llm()` compile upstream ancestry for any active task, providing focused LLM context under 2000 tokens.
- **Reference:** `core/SPEC.md` | Engine: `core/canvas/node_canvas_core.py` | Tests: `tests/core/test_node_canvas_core.py` (11 passed)

### [🔒 LOCKED] DEC-044: DNK Android Teleprompter Architecture (Compose Overlay & CameraX)

- **Subject:** Android Native Talking-Head Teleprompter Engine fork based on `google/jetpack-camera-app`.
- **Status:** `[🔒 LOCKED]` (DEC-044)
- **Rationale:**
  1. *Foreign Repo Quarantine*: Base upstream repository cloned into `../DNK_Vibe/jetpack-camera-app` via `scripts/system/safe_repo_clone.py`, keeping `DNK_HUB` workspace 100% clean.
  2. *Top-Center Cutout Alignment*: Teleprompter ribbon anchors directly below `WindowInsets.displayCutout` (front camera punch-hole) in `CaptureLayout.kt`, ensuring natural gaze alignment without eye shift.
  3. *Zero-Bloat On-Device Speech Sync*: Real-time word tracking powered by native `android.speech.SpeechRecognizer` (0 MB model overhead, zero thermal throttling).
  4. *Slot-Based Compose Layering*: Non-destructive integration via slot composable `teleprompterContent` over `viewfinder` Box in `CaptureLayout.kt`.
- **Reference:** `../DNK_Vibe/jetpack-camera-app` | Entry: `feature/preview/.../PreviewScreen.kt` & `ui/components/capture/.../CaptureLayout.kt`

### [🔒 LOCKED] DEC-044: SOTA Architecture Assimilation — get-bb/bb Agentic IDE

- **Subject:** Assimilation of `get-bb/bb` architectural patterns: Git Worktree task isolation, Server vs Host-Daemon decoupling, 3-tier plugin contracts, and self-hosted MCP bridge.
- **Status:** `[🔒 LOCKED]` (DEC-044)
- **Rationale:**
  1. *Git Worktree Task Isolation*: Subagent threads (Gerych / Denchik) run inside isolated git worktrees created on demand (`environment-git-worktree`), eliminating dirty workspace states and merge conflicts on main branch.
  2. *Server vs Host-Daemon Decoupling*: Policy, state, and thread persistence live in Hono/SQLite (`apps/server`), while raw system primitives (pty terminals, execution environments) live in a lightweight host daemon (`apps/host-daemon`).
  3. *3-Tier Plugin Standard*: Standardized architecture: UI (`app.tsx`) + Policy (`server.ts`) + Host Execution (`host.ts`) + Type Contract (`contract.ts`).
  4. *Two-Way MCP Bridge*: Expose DNK OS agents and `bb` commands via a unified FastMCP bridge (`search`, `read`, `run`), enabling cross-IDE control from Claude Desktop, Antigravity, and terminal agents.
- **Reference:** Specification: `docs/tech/sota_assimilation/get_bb_bb.md` | SCONES ID: `SCONES-MEM-1793228362391` | Quarantine: `../DNK_Vibe/bb`

### [🔒 LOCKED] DEC-047: Sovereign Clean-Room Media Studio (M2 Protocol & GCP Vertex AI Engine)

- **Subject:** Sovereign Clean-Room Media Studio in `services/dnk_media` assimilating SeeCut M2 Deterministic Write Protocol + `poseljacob/agentic-video-editor` + Google Cloud Vertex AI (Imagen 3, Gemini 2.5/3.8 Flash, Chirp3-HD TTS) + Remotion / FFmpeg 7.
- **Status:** `[🔒 LOCKED]` (DEC-047)
- **Rationale:**
  1. *AGPL-3.0 Immunity & Clean-Room Invariant*: No foreign Rust/C++ code from SeeCut is imported into `DNK_HUB`. Only the deterministic MCP M2 protocol specification (leased mutation, revision lock, idempotent `operationId`) is assimilated into pure Python/Pydantic.
  2. *Tri-Agent Swarm Division*: Antigravity (Architect / Verification Gates), Denchik (Chief Builder / Code Construction in `services/dnk_media`), Gerych (FastMCP runtime & SCONES integration).
  3. *GCP Native Multimodal Engine*: Bypasses domestic Chinese aggregators (GrsAI/Tencent) via verified SSOT `dnk.dev.os@gmail.com` on `project-17fe1d8a-b1f4-46ac-87e` (Vertex AI Gemini, Cloud TTS Chirp3-HD Ukrainian voices).
  4. *Chat-First Remotion + FFmpeg Assembly*: Visual Pointer & Chat-first editing on React/Remotion + deterministic lossless hard-cuts and audio mixing via local FFmpeg 7.
- **Reference:** Specification: `services/dnk_media/` | SCONES Reference: `core/.../seecut_agent_native_media_editor_and_mcp_write_protocol.md` | Sandbox: `../DNK_Vibe/agentic-video-editor`

### [🔒 LOCKED] DEC-048: Sovereign Clean-Room Reverse Engineering Harness (REA + Helix 4 Hard Gates)

- **Subject:** Autonomous Reverse Engineering Harness in `core/cleanroom_re/` assimilating `morluto/rea` (404k⭐, MIT), `PlevanTem/ui-reverse-engineer`, and Shopify Helix 4 Hard Gates.
- **Status:** `[🔒 LOCKED]` (DEC-048)
- **Rationale:**
  1. *Clean-Room Separation & License Immunity*: All external repositories are strictly cloned into isolated quarantine `../DNK_Vibe/` via `safe_repo_clone.py`. Main workspace indexer is 100% isolated.
  2. *REA MCP Tooling*: Assimilate and wrap `rea-agents` MCP server (`npx rea-agents mcp`) for local AST, JS bundle, and runtime DOM analysis without sending code to third-party clouds.
  3. *Physical Gate Barrier*: Enforce `scripts/system/helix_re_gate_runner.py` Exit Code 2 barrier before any reconstructed code enters `DNK_HUB`. Required artifacts: `01_design_tokens_and_spatial_spec.md`, `02_data_contracts_and_state_machine.md`, `03_feature_graph_task_dna.json`.
  4. *Autonomous Terminal Dual-Swarm*: Gerych (Hermes Prime) runs audit/intake in Terminal 1, while Denchik (`scripts/system/denchik.sh`) constructs the sovereign harness in Terminal 2.
- **Reference:** Task Spec: `docs/tasks/TASK-DNK-CLEANROOM-RE-HARNESS-20261029-001.md` | Sandbox: `../DNK_Vibe/rea` | Enforcer: `scripts/system/helix_re_gate_runner.py`

---

### [🔒 LOCKED] DEC-049: Zero-Loss Spatial Pinning Protocol & Visual Brain SSOT (`core/canvas/canvas_pin.py`)

- **Subject:** Elimination of Chat Discussion Amnesia via Atomic Spatial Decision Pinning to JSON Canvas 1.0 (`docs/canvas/dnk_brain.canvas`).
- **Status:** `[🔒 LOCKED]` (DEC-049)
- **Rationale:**
  1. *Visual SSOT over Ephemeral Chat*: Chat is strictly for System 1 fast intake; Canvas is System 2 persistent memory. No architectural agreement or task is considered approved until it is pinned as a node in `docs/canvas/dnk_brain.canvas`.
  2. *Deterministic Kahn Cycle Rejection*: Automated cycle detection prevents circular dependencies between tasks/nodes before writing to disk.
  3. *Live Dual-Surface Bridge*: Standalone Canvas UI (`apps/canvas/`) automatically synchronizes with `docs/canvas/dnk_brain.canvas` via `canvas_bridge.py` (`/api/canvas/state` & `/api/canvas/pin`).
  4. *C-Suite Agent Enforcement*: Rule 5 added to `core/orchestrator/agents/strategist/SOUL.md`: Strategist Prime is mandated to pin approved decisions programmatically via `canvas_pin.py`.
- **Reference:** Implementation: `core/canvas/canvas_pin.py` | Tests: `tests/core/test_canvas_pin.py` | Canvas File: `docs/canvas/dnk_brain.canvas` | UI: `apps/canvas/`

---

### [🔒 LOCKED] DEC-051: Denchik Iron Man Super-Builder Engine & Canvas Multi-Agent Swarm Bridge

- **Subject:** Autonomous math distillation, FastMCP Code Mode sandbox, quarantined clean-room lens, and multi-agent SSE dispatch bridge.
- **Status:** `[🔒 LOCKED]` (DEC-051)
- **Rationale:**
  1. *Core Super-Builder Engine (`core/iron_man/`)*: Equips Denchik with (1) `MathDistiller` for AST and finite-state machine invariant extraction without vendor lock-in, (2) `CodeModeSandbox` for atomic in-memory execution to eliminate tool-chatter bloat, (3) `SotaLens` for read-only clean-room donor audits and license compliance, and (4) `GoldfishGate` for strict anti-tautology and cryptographic receipt generation (`RCPT-...`).
  2. *Multi-Agent Swarm Canvas Bridge (`scripts/system/canvas_bridge.py` v2.0.0)*: Real-time SSE dispatch routing the 4 core agent personas (👑 Стратег, ⚔️ Аудитор, 🦾 Денчік, 🛡️ Гєрич) directly to their domain engines with live state mutation in `docs/canvas/dnk_brain.canvas`.
  3. *Zero-Amnesia Spatial Pinning*: Every architectural consensus and task execution generates an immutable node on the visual canvas, permanently preventing chat amnesia.
- **Reference:** Implementation: `core/iron_man/` | Bridge: `scripts/system/canvas_bridge.py` | UI: `apps/canvas/` | Tests: `tests/core/test_iron_man_denchik.py` (10/10 passed)

---

### [🔒 LOCKED] DEC-052: Sovereign JIT Agent Paradigm & In-RAM Code Mode

- **Subject:** Transition from legacy chat-based swarms (CrewAI/ChatDev) to a Single Sovereign Agent (Denchik) with in-RAM FastMCP tool hydration.
- **Status:** `[🔒 LOCKED]` (DEC-052)
- **Rationale:**
  1. *Elimination of Compound Multi-Agent Error*: Chat-based swarm compounding degradation ($0.95^{10} \approx 60\%$) and prompt-bloat (>150k standing context) replaced by Single Sovereign Agent with context ceiling $\le 5,500$ tokens.
  2. *In-RAM Code Mode*: Tool filtering and AST transformation occur inside isolated Python RAM (`execute_code`), cutting context payload by 98.7% and preventing terminal output floods.
  3. *Ephemeral Goldfish Audits*: Quality gates executed by zero-context transient subprocesses rather than bloated permanent resident agents.
- **Reference:** Research: `docs/audit/RESEARCH_SINGLE_AGENT_JIT_VS_SWARM_2026.md` | Audit: `docs/audit/AUDIT_DNK_HUB_JIT_READINESS.md` | Core: `core/framework/fastmcp_dispatcher.py`

---

### [🔒 LOCKED] DEC-053: Parallel Candidate Isolation Protocol (Anti-Collision Two-Phase Commit)

- **Subject:** Elimination of agent race conditions and file collisions during parallel candidate runs.
- **Status:** `[🔒 LOCKED]` (DEC-053)
- **Rationale:**
  1. *Candidate Isolation*: Parallel runs must write outputs to isolated candidate namespaces (`docs/audit/candidates/<agent_id>/`) or disjoint target file whitelists.
  2. *Two-Phase Commit*: Physical mutation of canonical files occurs only after adversarial review and deterministic gate verification.
- **Reference:** Incident: `docs/audit/TASK-DNK-AGENT-SOVEREIGNTY-JIT-AUDIT-20261029-001_evidence.json` | Protocol: `docs/architecture/TWO_TIER_DEVELOPMENT_PROTOCOL.md`

---

### [🔒 LOCKED] DEC-054: Gerych Prime Deprecation & Denchik Sovereign SSOT

- **Subject:** Formal deprecation of Gerych Prime from active builder/mutation roles; Denchik coronation as Sovereign Master Developer.
- **Status:** `[🔒 LOCKED]` (DEC-054)
- **Rationale:**
  1. *Role Consolidation*: Active code synthesis, refactoring, and feature execution consolidated under Denchik (`scripts/system/denchik.sh`).
  2. *Cold Knowledge Archive*: Gerych transitioned to read-only cold archive (`core/orchestrator/agents/gerych_prime/state.db`) for retrospective historical auditing.
  3. *Skills Bridge JIT Integration*: Denchik equipped with `core/iron_man/skills_bridge.py` allowing on-demand execution of legacy skills without context bloat.
  4. *Mastery Verification*: Certified via deterministic machine receipt `RECEIPT-DENCHIK-MASTERY-20261029-001` across all 6 crucible dimensions (8/8 quality gates passed).
- **Reference:** Task: `docs/tasks/TASK-DNK-DENCHIK-MASTERY-VERIFICATION-20261029-001.md` | Receipt: `docs/audit/DENCHIK_MASTERY_RECEIPT_20261029.json` | Implementation: `core/iron_man/skills_bridge.py` | Tests: `tests/core/test_skills_bridge.py`

---

### [🔒 LOCKED] DEC-056: Triggered Clean-Room Donor Scout Protocol (SotaLens + DNK_Vibe)

- **Subject:** Алгоритмічний імпорт рішень із GitHub через ізольований карантин `../DNK_Vibe/` без засмічення головного репозиторію.
- **Status:** `[🔒 LOCKED]` (DEC-056)
- **Rules & Invariants:**
  1. *Trigger Condition*: Пошук на GitHub дозволений ВИКЛЮЧНО за наявності тригера високої алгоритмічної складності (AST-парсери, таймлайни, WebGL, WebRTC, складна математика або >200 рядків нетипового коду). Для звичайної бізнес-логіки, CRUD, роутерів FastAPI, Polaris-компонентів та міграцій БД пошук на GitHub СУВОРО ЗАБОРОНЕНО.
  2. *License Gate*: Дозволені тільки ліцензії MIT, Apache-2.0, BSD, Unlicense, автоматично перевірені через `SotaLens.audit_license()`. Репозиторії без ліцензії або з GPL/AGPL копілефтом блокуються fail-closed.
  3. *Zero-Pollution Quarantine*: Клонування здійснюється суворо через `python3 scripts/system/safe_repo_clone.py <url> --depth 1` у зовнішній каталог `../DNK_Vibe/`. Головний воркспейс `DNK_HUB` залишається 100% чистим від сторонніх `node_modules` чи `package.json`.
  4. *Surgical Extraction*: З донора вилучається виключно чистий математичний алгоритм, регулярний вираз або AST-логіка. Увесь інфраструктурний клей пишеться Денчіком нативно під стек DNK OS (Pydantic v2, MRH, Polaris).
  5. *Immediate Pruning*: Одразу після вилучення алгоритму та створення нативного TDD-тесту карантинна папка в `../DNK_Vibe/` примусово видаляється.
- **Reference:** Lens: `core/iron_man/sota_lens.py` | Intake: `scripts/system/safe_repo_clone.py` | Quarantine: `../DNK_Vibe/`

---

### [🔒 LOCKED] DEC-055: Denchik Super-Builder Protocol v3 (MASE + In-RAM FastMCP + SCONES Gate)

- **Subject:** Formalization of the 4-phase sovereign engineering execution pipeline in `core/orchestrator/agents/denchik/SOUL.md` v2.0.0 and `scripts/system/denchik.sh`.
- **Status:** `[🔒 LOCKED]` (DEC-055)
- **Rationale:**
  1. *Phase 1 (In-RAM Deconstruct)*: Dissect incoming tasks from `docs/tasks/` inside Python RAM via FastMCP `execute_code`. Evaluates AST scope, filters target file manifests, and reads SCONES memories with ZERO raw terminal token dumps.
  2. *Phase 2 (Working-Tree AST Overlay)*: Ultra-fast symbol discovery (< 0.05s) via `SkillsBridge` and AST indexers. Slices code targets with `StartLine`/`EndLine` reads, preventing full-file context exhaustion.
  3. *Phase 3 (Atomic TDD & Zero-Tautology Pass)*: Strict red-green-refactor cycle. Every new symbol or mutation is backed by a deterministic test with real assertions; validated by AST `anti_tautology_guard.py` (0 fake tests allowed).
  4. *Phase 4 (SCONES Memory & Pre-Commit Censor)*: Mandatory persistence gate via `scones_remember(topic, rule)`; automated adversarial review via `auto_precommit_guard.py` (8/8 checks passed with exit code 0); machine receipt emitted to `docs/audit/RECEIPT-*.json`.
- **Reference:** SOUL: `core/orchestrator/agents/denchik/SOUL.md` v2.0.0 | Launcher: `scripts/system/denchik.sh` v2.0.0 | Receipt: `docs/audit/DENCHIK_MASTERY_RECEIPT_20261029.json`

---

### [🔒 LOCKED] DEC-057: Senior Dev Solution Ladder & Anti-Generative Bloat Protocol (Ponytail Assimilation)

- **Subject:** Clean-room assimilation of the 6-rung senior developer solution ladder, explicit `# shortcut:` technical debt ledger, and 4-part review rubric from `DietrichGebert/ponytail`.
- **Status:** `[🔒 LOCKED]` (DEC-057)
- **Rationale & Invariants:**
  1. *The 6-Rung Solution Ladder*:
     - Rung 1: *Necessity (YAGNI)* — Eliminate unrequested flexibility and anticipatory abstractions.
     - Rung 2: *Project Reuse* — Check and reuse existing codebase helpers, models, and UI components first.
     - Rung 3: *Platform & Stdlib* — Use native HTML5, standard DOM APIs, and Python stdlib before reaching for external libraries.
     - Rung 4: *Existing Dependencies* — Restrict imports to already-installed packages (`uv`/`pnpm`). Adding new packages requires explicit architectural consent.
     - Rung 5: *Single-Line Idiomatic Simplicity* — Prefer direct, readable language constructs over custom helper functions.
     - Rung 6: *Minimal Physical Implementation & Targeted Test* — Write the smallest working code with exactly 1 non-trivial unit test targeting boundary conditions.
  2. *Explicit Technical Debt Ledger (`shortcut:` Convention)*:
     - Vague `// TODO:` or `// FIXME:` comments are strictly prohibited.
     - Temporary implementations or fallbacks must declare a ceiling and trigger:
       `# shortcut: <limit/ceiling>, trigger: <deterministic event/metric for refactoring>`
  3. *4-Part Review Rubric*:
     - Any architectural or pre-commit critique must state:
       (1) *What this is* -> (2) *Problem* -> (3) *Fix* (smallest diff, ideally deletion) -> (4) *If we skip it* (production impact).
- **Reference:** Session: `20261030_015009_dc42c3` | Donor: `DietrichGebert/ponytail` | Specification: `AGENTS.md` (Zero-Waste Protocol)

---

### [🔒 LOCKED] DEC-058: Hybrid Elephant-Goldfish JIT Architecture & ThoughtDAG Context Wires

- **Subject:** Dual-circuit Sovereign JIT Agent architecture assimilating `thoughtdag` (MIT) and `single-agent-loop-kit` (MIT).
- **Status:** `[🔒 LOCKED]` (DEC-058)
- **Rationale & Invariants:**
  1. *Elephant Orchestrator (Денчік)*: Single sovereign developer holding global task orientation. Bounded standing context <= 6,000 tokens. Eliminates multi-agent chat bloat.
  2. *Goldfish Tool-Workers (`04-as-tool.md`)*: Specialist domain workers (`dnk_shopify`, `dnk_media`, `gerych_auditor`) operate as isolated subprocesses (`subprocess.run`), returning deterministic typed JSON receipts. Never share mutable memory or pollute interpreter namespace (prevents Runtime Poisoning).
  3. *ThoughtDAG Disk/SQLite Context Wires*: Task graph state is persisted in SQLite/filesystem. The LLM prompt receives strictly the `active_node` and its direct dependency ancestors (<= 1,500 tokens). Intermediate raw tool dumps and `thinking` tokens are pruned from linear context to prevent Compaction Amnesia and attention degradation.
- **Reference:** Donor: `thoughtdag` & `single-agent-loop-kit` (`../DNK_Vibe/`) | Review: Denchik Sovereign Builder (Task 76) | Artifact: `THOUGHTDAG_SINGLE_LOOP_ASSIMILATION_REPORT.md`

---

### [🔒 LOCKED] DEC-052: ThoughtDAG Layered Context Wires & Zero-Degradation Task Pipeline

- **Subject:** Non-degrading task decomposition, context wires, branch isolation, and merge synthesis assimilating  (MIT).
- **Status:**  (DEC-052)
- **Rationale:**
  1. *Clean-Room Assimilation*: Distilled from quarantined donor  into sovereign Python Pydantic engine () and existing .
  2. *Zero Attention Bleed*: Parallel sub-tasks (, , ) receive strictly their upstream ancestors. Wires block cross-chatter, preventing prompt bloat and Gemini attention degradation.
  3. *Merge Synthesis*: Final release node acts as a fan-in accumulator combining only verified results from parallel branches, followed by GoldfishGate anti-tautology machine verification.
- **Reference:** Distillation:  | Engine:  | Tests:  (12/12 passed)

---

### [🔒 LOCKED] DEC-053: Agent-First Infinity Canvas Core (JIT Skills & Self-Diagnostics Engine)

- **Subject:** Agent-First Infinity Canvas Core with JIT Skill Mounting, Automated Self-Diagnostics, and ThoughtDAG Dynamic Workflow Spawning.
- **Status:**  (DEC-053)
- **Rationale:**
  1. *JIT Skill Mounting ()*: Eliminates context bloat by injecting only task-specific skills () to designated nodes on the fly while enforcing a strict <= 4,000 token ceiling.
  2. *Automated Graph Self-Diagnostics ()*: Detects cycles, orphaned edges, and blocked execution states () with quantified health scoring.
  3. *Autonomous Workflow Spawning ()*: Allows Denchik to spawn isolated 3-branch ThoughtDAG pipelines (Architecture, UI/Schema, Backend/Logic) with a final audit merge node directly onto .
- **Reference:** Implementation: `core/canvas/` | Bridge: `canvas_bridge.py` | Tests: `tests/canvas/` (11/11 passed)

---

### [🔒 LOCKED] DEC-059: Decoupled Sovereign Agent Architecture (Sovereign Microkernel Engine + Lean CLI Runner)

- **Subject:** Formal separation of Sovereign Business Kernel (`core/agent_kernel/` per DEC-034) from terminal shell runners; retirement of `gerych.sh` in favor of `denchik.sh` + `denchik_engine.sh`.
- **Status:** `[🔒 LOCKED]` (DEC-059)
- **Rationale:**
  1. *Decoupled Kernel vs Shell*: Бізнес-ядро агента (FastMCP інструменти `core/iron_man/`, SCONES пам'ять, Task Forest) повністю суверенні та ізольовані від термінального рантайму. Відкидається пастка написання термінального емулятора з нуля (YAGNI/DEC-057).
  2. *Sovereign Execution SSOT*: `scripts/system/denchik.sh` та `scripts/system/denchik_engine.sh` закріплені як єдині діючі лаунчери Master Developer. `scripts/system/gerych.sh` редуковано до легковагового архівного стаба з нотифікацією DEC-054.
  3. *Anti-Fragile SSL & Env Auto-Healing*: Впроваджено автоматичне самовідновлення у [core/hermes_agent/agent/ssl_guard.py](file://.//MY_LIFE_WORK/DNK_HUB/core/hermes_agent/agent/ssl_guard.py) та санітизацію у [scripts/system/denchik_engine.sh](file://.//MY_LIFE_WORK/DNK_HUB/scripts/system/denchik_engine.sh) — неіснуючі шляхи `SSL_CERT_FILE` автоматично скидаються на користь валідного системного certifi без падінь при перевстановленні чи міграціях віртуального оточення.
  4. *Direct Vertex AI Transport*: Пряме звернення до Google Vertex AI (Gemini 3.8 Flash) за системними OAuth2/ADC токенами, усуваючи сторонні залежності.
- **Reference:** Launchers: `scripts/system/denchik.sh`, `scripts/system/denchik_engine.sh` | Stub: `scripts/system/gerych.sh` | Guard: `core/hermes_agent/agent/ssl_guard.py`

---

### [🔒 LOCKED] DEC-060: Headless FastMCP Runtime Wire Harness & CLI Lifecycle Engine

- **Subject:** Unified headless coordination of NodeCanvasCore, SconesMemoryStore, and JITSkillMounter via FastMCP and CLI interfaces.
- **Status:** `[🔒 LOCKED]` (DEC-060)
- **Rationale:**
  1. *Core Integration SSOT*: [`core/harness/dnk_runtime_wire.py`](file://.//MY_LIFE_WORK/DNK_HUB/core/harness/dnk_runtime_wire.py) combines spatial DAG canvas (CONTRACT-002), cognitive memory (SCONES), and dynamic skill mounting into a single runtime loop.
  2. *Dual-Surface Exposure*: [`core/harness/mcp_server.py`](file://.//MY_LIFE_WORK/DNK_HUB/core/harness/mcp_server.py) exposes native FastMCP tools (`dnk_node_dispatch`, `dnk_node_branch`, `dnk_node_complete`, `dnk_node_status`) while [`core/harness/cli.py`](file://.//MY_LIFE_WORK/DNK_HUB/core/harness/cli.py) provides subcommands for terminal invocation.
  3. *Zero Attention Bleed & Context Diet*: Maximum prompt context bounded strictly at <= 4,000 tokens per node.
  4. *Deterministic Verification*: 5/5 unit and integration tests passing (`tests/core/test_dnk_runtime_wire.py` and `tests/core/test_dnk_harness_entrypoint.py`).
- **Reference:** Tasks: `TASK-DNK-CORE-20261031-001`, `TASK-DNK-CORE-20261031-002` | Tests: `tests/core/test_dnk_runtime_wire.py`, `tests/core/test_dnk_harness_entrypoint.py` (Exit code 0).

---

### [🔒 LOCKED] DEC-061: 4-Stage Clean-Room Donor Assimilator (Task DAG Satellite Engine)

- **Subject:** 4-Stage Clean-Room extraction pipeline (Contract DTO -> Pure Logic Formula -> Clean Code Verification -> Memory Gate & Obsidian Note Export) implementing `DNK Task Dag System.md`.
- **Status:** `[🔒 LOCKED]` (DEC-061)
- **Rationale:**
  1. *Context Diet & Anti-Bloat*: Satellite donor analysis runs in an isolated subtask. Only the distilled extract (<= 500 tokens) is injected into the parent task, keeping the main context clean (< 4,000 tokens).
  2. *Human-in-the-Loop & Manual Editability*: The assimilator automatically writes an Obsidian note to `docs/vault/tasks/TASK-ASSIMILATE-{donor}.md` with K-Plex Compass frontmatter (`up`, `north`, `west`, `east`). The user can edit formulas or fields by hand in Obsidian with `Cmd+S`, and the system preserves the manual overrides.
  3. *Deterministic Verification*: Each extracted formula is verified with a live Python assert before export. 5/5 unit tests passing (`tests/core/test_donor_assimilator.py`).
- **Reference:** Tasks: `TASK-DNK-CORE-20261101-001` | Specification: `Obsidian_Notes/Chats/DNK Task Dag System.md` | Engine: `core/harness/donor_assimilator.py` | Tests: `tests/core/test_donor_assimilator.py` (Exit code 0).

---

### [🔒 LOCKED] DEC-062: Sovereign Task Forest Dispatcher & Unified Mission Control Architecture

- **Subject:** Transition from linear chat interactions in Antigravity to an Agent-Native Task Forest Mission Control in DNK OS, assimilating token/cost accounting, attention chimes, and verification gates from `antigravity-taskboard` into `apps/canvas` and `apps/web`.
- **Status:** `[🔒 LOCKED]` (DEC-062)
- **Rationale:**
  1. *Dogfooding Fast-Path & Anti-UI-Bloat (DEC-008, DEC-057)*: Відкидається розробка стороннього третього UI з нуля. Замість цього просторовий диспетчер інтегрується безпосередньо у вже існуючий `apps/canvas` (JSON Canvas 1.0) та `apps/web` над діючим REST-роутером [`apps/api/routers/tasks/forest.py`](file://.//MY_LIFE_WORK/DNK_HUB/apps/api/routers/tasks/forest.py).
  2. *SOTA Telemetry Assimilation*: Асиміляція перевірених механізмів з прототипу `antigravity-taskboard` (`localhost:4040`):
     - **Cost & Token Usage**: облік вхідних некешованих токенів, cache hit ratio (еталон 98%+), вихідних токенів та витрат у USD ($) за актуальними рейтами моделі.
     - **Attention & Escalation**: аудіо-сповіщення (beep chimes), таймери Snooze (15m, 1h), Silence та статус Pending Review.
     - **Ordered Subtasks & Verification Gates**: сувора послідовна черга підзадач, обов'язковий машинний доказ (exit code 0 / acceptance rubric) та генерація 3 follow-up пропозицій.
     - **Files Accessed Table**: облік зачеплених файлів з `git diff` для блокування конфліктів у паралельних задачах (Scope Lock).
  3. *5-Level Spatial Forest Hierarchy (DEC-040)*: Завдання не зводяться до плаского Kanban, а зберігають природну таксономію DNK OS: 🌾 Поле ➔ 🏞️ Сектор ➔ 🌳 Дерево ➔ 🌿 Кущ ➔ 🌸 Квітка з рекурсивним Bottom-Up Rollup розрахунком прогресу.
  4. *Dual-Engine Control Loop*: Antigravity працює як інтерактивний Mentor / Architect, а Денчік (`denchik.sh` / `core/harness/dnk_runtime_wire.py`) — як автономний headless-виконавець. Обидва записують статус у єдине джерело правди (Task Forest DAG).
- **Reference:** Decisions: `DEC-040`, `DEC-042`, `DEC-060` | Prototype Donor: `.agents/plugins/antigravity-taskboard` | UI Targets: `apps/canvas/`, `apps/web/components/canvas/TaskForestCanvas.tsx` | Router: `apps/api/routers/tasks/forest.py`

---

### [🔒 LOCKED] DEC-063: Agent-Native Enterprise Mesh & Deterministic Approval Chains

- **Subject:** Assimilation of Eggent 3.0 enterprise paradigms (Human+Agent pairing, approval chains, document templating) into DNK OS with strict epistemic armor, cryptographic receipts, and indirect prompt injection defense.
- **Status:** `[🔒 LOCKED]` (DEC-063)
- **Rationale:**
  1. *From Conversational Chaos to Typed Mesh*: Спроба замінити корпоративні SaaS-інструменти неструктурованим листуванням агентів між собою ("зіпсований телефон") призводить до експоненційного зростання семантичної ентропії. Усі операції між агентами переводяться на строгі схеми Pydantic (`ApprovalChainSpec`, `ApprovalStep`) та транзакційні гейти.
  2. *Cryptographic Approval Receipts & Tamper-Proofing*: Багатоступеневе погодження документів (Sales ➔ Legal ➔ Finance ➔ Executive) захищене криптографічним хешуванням (`signature_sha256`) та перевіркою цілісності контенту (`document_payload_hash`). Будь-яка модифікація документа на середині ланцюга негайно викликає `DocumentTamperedError` та анулює попередні підписи.
  3. *Zero-Trust Ingress Sanitization*: Відкриття агентам прямого доступу до зовнішньої пошти чи публічних лід-чатів створює вектор критичної непрямої промпт-ін'єкції. Впроваджено обов'язковий санітайзер `PromptInjectionScanner`, що нейтралізує спроби підміни системних інструкцій (`ignore previous instructions`), jailbreak-шаблони та приховані HTML-коментарі до передачі у контекст моделі.
  4. *Hierarchical Knowledge over Flat Vector Buckets*: Відкидається звалювання 2000 сирих файлів у плаский хмарний векторний індекс (деградація уваги та темпоральна колізія). Знання компанії структурують через Obsidian SSOT, K-Plex Compass і Task Forest DAG із дотриманням бюджету контексту (<= 4000 токенів).
- **Reference:** Decision: `DEC-063` | Video Donor: `Eggent 3.0 (EF5MaqNqSQc)` | Implementation: `core/domain/agent_mesh_models.py`, `core/harness/approval_chain_gate.py`, `core/harness/prompt_injection_scanner.py` | Tests: `tests/core/test_approval_chain_gate.py` (7/7 passed).

---

### [🔒 LOCKED] DEC-064: Darkroom Engineering Standards Assimilation (Deslopper, Motion Physics & Strict Iteration Limits)

- **Subject:** Assimilation of Darkroom Engineering (`darkroomengineering/cc-settings`) production standards into Denchik's autonomous execution engine and DNK OS Canvas/Media layers.
- **Status:** `[🔒 LOCKED]` (DEC-064)
- **Rationale:**
  1. *Deslopper Protocol*: Автономний агент Denchik застосовує принципи `deslopper` (автовидалення мертвого коду, невикористаних імпортів, слоп-коментарів та анти-тавтологічну валідацію тестів) перед кожним коммітом у `scripts/verify_all.sh`.
  2. *Strict 2-Iteration Stop-Loss*: Якщо підхід до розв'язання задачі зазнає невдачі двічі поспіль, агент зупиняє циклічні спроби, підсумовує помилки та переходить до 2-3 альтернативних архітектурних рішень.
  3. *Motion Physics Tokens*: Прецизійні токени анімації (`--ease-out`, `--ease-in-out`, ліміт до 300-500мс) асимілюються в `apps/canvas` та `services/dnk_media` для запобігання візуальній втомі та перевантаженню процесора.
- **Reference:** Decision: `DEC-064` | Repository: `../DNK_Vibe/cc-settings` | Ingestion Card: `docs/tech/sota_assimilation/darkroomengineering_cc_settings.md` | Target: `Denchik Engine & apps/canvas/`

---

### [🔒 LOCKED] DEC-065: LobeHub Monolith Permanent Ban, Purge & Core AI DNA Assimilation (Gemini 3.8 / 4 Argon Thinking & GCP OAuth2 Relay)

- **Subject:** Complete purge and permanent ban of LobeHub monolith (`DNK_Vibe/lobehub`), removal of all Docker daemons/images, and assimilation of its Model Bank, Gemini Thinking Resolver, and GCP OAuth2 Token Relay into native DNK OS lightweight bricks.
- **Status:** `[🔒 LOCKED]` (DEC-065)
- **Rationale:**
  1. *Permanent Ban of Resource-Eating Monoliths*: Поєднання Next.js 16 + Webpack + Better-Auth + tRPC (70+ роутерів) споживає 6.9 ГБ RAM, викликає OOM-краші та дисковий тротлінг на Mac M1 (8 ГБ). Усі файли (6.0 ГБ на диску) та Docker-образи (2.4 ГБ) повністю видалені. Повторне завантаження фізичного LobeHub назавжди заблоковано в `scripts/system/safe_repo_clone.py` та `AGENTS.md`.
  2. *Gemini 3.8 & 4 Argon Thinking Resolver*: Асиміляція інваріанта Google API — `thinkingBudget` (число) та `thinkingLevel` (`minimal|low|medium|high`) є строго взаємовиключними; `includeThoughts: true` активується тільки при валідному бюджеті (Argon max 32k, Flash max 24k).
  3. *GCP OAuth2 Token Relay*: Динамічний обмін токенів `ya29...` (`gcloud auth print-access-token`) для безшовної ротації GCP акаунтів без статичних API ключів.
  4. *Zero-Waste Protocol*: Знання та патч збережені в `scripts/dnk_lobehub_gcp_auth_gemini4_argon.patch` та `docs/architecture/reports/LOBEHUB_ECOSYSTEM_AUDIT_AND_ASSIMILATION.md`.
- **Reference:** Decision: `DEC-065` | Audit Report: `docs/architecture/reports/LOBEHUB_ECOSYSTEM_AUDIT_AND_ASSIMILATION.md` | Patch: `scripts/dnk_lobehub_gcp_auth_gemini4_argon.patch` | Target: `core/llm_gateway.py` & DNK OS Agent Substrate.

---

### [🔒 LOCKED] DEC-066: Shopify GitHub Themes Ingestion, Audit & Compilation Pipeline

- **Subject:** Mandatory protocol for cloning, quarantine, external reference sanitization, static auditing, and packaging of Shopify themes from GitHub directly into `/Users/<username>/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/GitHub_Shopify_Themes/`.
- **Status:** `[🔒 LOCKED]` (DEC-066)
- **Rationale:**
  1. *Quarantine & Monorepo Hygiene*: Сторонні теми ніколи не завантажуються в `DNK_HUB`. Канонічна директорія інжекції — `SHOPIFY/DNKShopify/DNKEcom/GitHub_Shopify_Themes/`.
  2. *External Dependency Purge & Sanitization*: Вилучення або нейтралізація сторонніх трекерів, відсутніх сніппетів, мертвих CDN-лінків для гарантії рендерингу без помилок у Shopify Customizer.
  3. *Automated Audit & Packaging*: Створення `AUDIT_<theme-name>.md` та чистого архіву `<theme-name>-upload.zip` для миттєвого завантаження в тестовий магазин.
- **Reference:** Decision: `DEC-066` | Target: `~/.gemini/config/rules/shopify-github-themes-ingestion.md`, `AGENTS.md` (Rule 11), `.agents/rules/shopify-github-themes-ingestion.md` | Audit Case: `AUDIT_anvil-theme.md`.

---

### [🔒 LOCKED] DEC-067: Shopify GitHub Apps Ingestion, Audit & Dev Store Protocol

- **Subject:** Mandatory protocol for cloning, quarantine, foreign client_id decoupling, static auditing, test validation, and dev store testing of Shopify apps from GitHub directly into `/Users/<username>/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/GitHub_Shopify_Apps/`.
- **Status:** `[🔒 LOCKED]` (DEC-067)
- **Rationale:**
  1. *Quarantine & Monorepo Hygiene*: Сторонні додатки суворо заборонено клонувати або розпаковувати всередину `DNK_HUB`. Канонічна директорія інжекції — `SHOPIFY/DNKShopify/DNKEcom/GitHub_Shopify_Apps/`.
  2. *Strict Package Manager & Dependency Hygiene*: Встановлення залежностей виключно через `pnpm install`, ініціалізація локальної БД SQLite (`dev.sqlite`), очищення зайвих lock-файлів.
  3. *Foreign Credentials Decoupling*: Обов'язкове коментування/декоплінг чужих `client_id` в `shopify.app.toml` для запобігання помилкам HTTP 403 Forbidden ("You are not a member of the requested organization") при лінкуванні до Partner-організації розробника.
  4. *Compilation & Test Gates*: Обов'язкова перевірка `pnpm run build`, збірка Shopify Functions (`dist/function.wasm`), валідація unit-тестів (`pnpm test`), лінтера (`pnpm run lint`) та Theme App Extensions (`shopify theme check`).
  5. *Audit Report & Deployment Guide*: Формування вичерпного звіту `AUDIT_<app-folder>.md` з покроковою інструкцією запуску `shopify app dev` на магазині розробника.
- **Reference:** Decision: `DEC-067` | Target: `~/.gemini/config/rules/shopify-github-apps-ingestion.md`, `AGENTS.md` (Rule 12), `.agents/rules/shopify-github-apps-ingestion.md` | Audit Case: `AUDIT_daily-deal-shopify.md`, `AUDIT_seos-assistant.md`.

---

### [🔒 LOCKED] DEC-068: Shopify GitHub Agentic Workflows & AI Plugins Protocol

- **Subject:** Mandatory protocol for cloning, quarantine, skill inspection, MCP contract verification, and cross-platform agent parity of agentic Shopify workflows, AI plugins, and tool bundles directly into `/Users/<username>/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/GitHub_Agentic_Shopify_WF/`.
- **Status:** `[🔒 LOCKED]` (DEC-068)
- **Rationale:**
  1. *Quarantine & Workflow Hygiene*: Агентні воркфлоу, плагіни та набори скілів зберігаються виключно в ізольованій канонічній директорії `SHOPIFY/DNKShopify/DNKEcom/GitHub_Agentic_Shopify_WF/`. Заборонено засмічувати корінь чи підпапки `DNK_HUB`.
  2. *Skill & MCP Ingestion*: Повний аудит структури скілів (`SKILL.md`), скриптів автоматизації (Bash/Node) та контрактів Streamable HTTP / Stdio MCP серверів.
  3. *Cross-Platform Agent Parity*: Забезпечення сумісності скілів між екосистемами Antigravity, Claude Code та Codex.
  4. *Audit & Capabilities Documentation*: Формування комплексного аналітичного звіту `AUDIT_<workflow-folder>.md` з інвентарем скілів, інструментів та сценаріїв застосування.
- **Reference:** Decision: `DEC-068` | Target: `AGENTS.md` (Rule 13) | Audit Case: `AUDIT_sugar-theme-plugin.md`.

---

### [🔒 LOCKED] DEC-069: Universal Molecular Theme Deconstruction & Canonical Donor Git Worktree Engine

- **Subject:** Unified SSOT architecture for donor themes, cleanroom desanitization, self-improving molecular deconstruction, and two-hub agentic protocol (`main` core + `donor-lab` R&D) in `https://github.com/DNKShopify/DNK-e.com`.
- **Status:** `[🔒 LOCKED]` (DEC-069)
- **Rationale:**
  1. *Single Source of Truth (SSOT)*: Єдиним канонічним репозиторієм для тем-донорів є `https://github.com/DNKShopify/DNK-e.com` (локально: `DNK-Ecom_git_mirrow/`), де теми ізольовані в Git Worktrees (`sugar`, `story`, `casaio`, `ella`, `shrine-pro`, `tinker` тощо).
  2. *100% Cleanroom Protocol*: Усі донори очищені від DRM-перевірок, ліцензійних замків (ECDSA), сторонніх серверів перевірки та пікселів (FB, TikTok, GA). Кожна гілка містить власний Паспорт дистиляції та графтингу.
  3. *Двоконтурна модель репозиторію*:
     - `main`: Стабільне виробниче ядро DNK-Ecom Theme (Tinker 4.4.0 Horizon baseline) + `AGENTS.md` путівник онбордингу.
     - `donor-lab`: R&D Лабораторія, інвентар 10 тем (3 732 молекули) та матриця графтингу.
  4. *Тріада автономних агентів*: Antigravity (Mentor/Architect), Denchik (FastMCP Builder), Gerych23 (Terminal Auditor на DNK OS Core v0.23.0, Python 3.14, модель `google/gemini-4-argon` via `gerych4`).
  5. *Self-Improving Genome Loop*: Кожна проаналізована тема автоматично реєструє свої інновації в `03_SELF_IMPROVING_GENOME_REGISTRY.md` та збагачує специфікацію DNK Ecom.
- **Reference:** Decision: `DEC-069` | Targets: `DNK-Ecom_git_mirrow/main/AGENTS.md`, `DNK-Ecom_git_mirrow/donor-lab/README.md`, `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/`.

---

### [🔒 LOCKED] DEC-075: Establishment of Unified Sovereign Core DNK_OS & FastMCP Microkernel Host

- **Subject:** Unified Sovereign Core `DNK_OS` Architecture, FastMCP Microkernel Host, 6 Composable Production Bricks, Sovereign Cockpit CLI (`dnk-os`), and 100% Portability Standard Compliance.
- **Status:** `[🔒 LOCKED]` (DEC-075)
- **Rationale:**
  1. *Sovereign Core & Cockpit (`DNK_OS`)*: Директорія `MY_LIFE_WORK/DNK_OS` є єдиним суверенним ядром та основним робочим кабінетом вайбкодера (Максима) і команди автономних агентів (Antigravity mentor, Gerych terminal builder на Hermes 0.23, Denchik).
  2. *FastMCP Microkernel Host (`core/kernel.py`)*: Шлюз ядра з динамічним виявленням цеглин, топологічною резолюцією DAG-залежностей, реєстром портів, вартовим процесів (PID Sentinel) та шиною завдань агентів.
  3. *Composable LEGO Bricks (`core/bricks/`)*: 6 бойових цеглин (`brick_01_agentic_brain`, `brick_02_scones_memory`, `brick_03_spatial_canvas`, `brick_04_shopify_engine`, `brick_05_video_ai`, `brick_06_web_api_shell`), кожна з маніфестом, Pydantic-контрактами та FastMCP-сервером.
  4. *Sovereign Cockpit CLI (`dnk-os`)*: Глобальна утиліта в `~/.local/bin/dnk-os` для 1-екранного моніторингу (`dnk-os status`), керування цеглинами (`dnk-os brick`), портами (`dnk-os port`), очищення зомбі (`dnk-os clean`) та перевірки шлюзу (`dnk-os verify`).
  5. *100% Portability Compliance*: 0 абсолютних шляхів, багатоетапний Dockerfile (UID 1000, ripgrep/git/curl), compose.yaml з ротацією логів 50MB і томом SQLite WAL, авторозгортання `bootstrap.sh`. 3/3 зелених шлюзи у `verify_portability.sh` та `dnk-build --check`.
- **Reference:** Decision: `DEC-075` | Target: `../DNK_OS/` | Tools: `dnk-os`, `verify_portability.sh`, `dnk-build` | Related: `DEC-070`, `DEC-071`, `DEC-072`, `DEC-073`.

---

### [🔒 LOCKED] DEC-076: Molecular Theme Architecture & Autonomous Agentic Ecosystem Core for DNK Ecom

- **Subject:** Unified SSOT architecture for DNK Ecom storefront theme and autonomous agentic operation ecosystem, distilling molecular deconstructions of 5 donor ecosystems (Elixir, Shrine, Sugar, Story, Dawn), Store Spy RAG pipeline, and UCP/MCP protocols into a sovereign core.
- **Status:** `[🔒 LOCKED]` (DEC-076)
- **Rationale:**
  1. *Complete Elimination of Legacy Monoliths*: Повна відмова від 500KB+ секцій-монстрів (`shop-product-details.liquid` 574 KB, `cart.js` без черги). Перехід на стандарт Shopify Theme Blocks 2.0 (Horizon / Tinker architecture: Section -> Container -> Atomic Leaf Blocks) з лімітом <= 35 settings на блок, Scoped CSS та нативними Web Components (`<dnk-countdown>`, `<dnk-atc-bar>`, `<dnk-buy-box-tiers>`).
  2. *CartMutationQueue (Zero Race Conditions)*: Усі мутації `/cart/add.js`, `/cart/change.js`, `/cart/update.js` підпорядковані серіалізованій FIFO-черзі з `AsyncMutex`. Повна ліквідація хаотичних `setTimeout(..., 10)` для зв'язаних подарунків (linked gifts).
  3. *Rejection of Headless Subdomain Trap ($79/mo)*: Відхилення пропрієтарного підходу Elixir 2.0 (`elixir.page` на субдоменах `shop.domain.com`), який дробить SEO (29%+ трафіку), руйнує Meta CAPI EMQ через Safari ITP та створює вендор-лок $948/рік.
  4. *The DNK FastMCP Bypass (Native Speed on Single Domain)*: Агенти (Denchik, Gerych, Antigravity) компілюють висококонверсійні JSON-шаблони (`templates/product.hook-<slug>.json`, `templates/page.adv-<slug>.json`) за секунди та пушать їх напряму через Shopify Admin GraphQL API (`themeFilesUpsert`). Результат: миттєва збірка сторінок з AI, збереження 100% SEO, 10-бальний Meta EMQ і прямий нативний Shop Pay checkout без комісій.
  5. *Store Spy -> Offer DNA Pipeline*: Автономний конвеєр `services/dnk_media` + `services/dnk_shopify`: парсинг Meta Ads Library -> Whisper ASR + OCR кластеризація хуків за ROAS-вагою -> DOM/Vision екстракція цінової драбини Buy Box (`1x Anchor / 2+1 Best Value / 3+2 Max LTV`) -> авто-синтез Message-Matched лендінгу.
  6. *Universal Commerce Protocol (UCP / MCP)*: Вбудовані 14 інструментів Shopify UCP (`/.well-known/ucp`, `/agents.md`) для автономних покупок, модифікації кошика та пошуку по каталогу сторонніми AI-агентами.
- **Reference:** Decision: `DEC-076` | Target: `docs/architecture/DNK_ECOM_AGENTIC_THEME_AND_ECOSYSTEM_MASTER_CORE.md`, `services/dnk_shopify/DNK_Horizon_Tinker/`, `Audit_Shopify_Themes_Sell_WF/Elixir_Theme_Ecosystem_Audit/` | Related: `DEC-013`, `DEC-042`, `DEC-069`.

---

## ⚡ 2. ПОТОЧНИЙ ФОКУС (In Progress)

- [x] **TASK-DNK-OBSIDIAN-20261026-001**: Obsidian Vault Synchronization & 100% Configuration Parity with `DNK_OS_APP` (11 plugins, 3 CSS snippets, .obsidianignore, zero-lag indexing).
- [x] **TASK-DNK-APP-20261026-001**: SOTA Core Evaluation, DNK Polaris-Spatial Design System & Standalone App Assembly (Gerych Prime autonomous run).
- [x] **TASK-DNK-CANVAS-20261023-001**: SOTA Canvas Chat DAG & TaskForest Assimilation Audit (Gerych Prime autonomous run).
- [x] **TASK-01**: Скрипт експорту та кластеризації 1900 посилань `DNK_Bookmarks` за 12 доменами та інтеграція двомовного FTS5 пошуку з Tier-ранжуванням.
- [ ] **TASK-02**: Перетворення першого кластеру (Shopify CRO) на бойовий скіл `core/skills/shopify_cro_blocks/SKILL.md`.

---

## 📋 3. ЧЕРГА ДІЙ (Next Up)

1. [x] Довести [tinker-dnk-delivery-estimator.liquid](./services/dnk_shopify/DNK_Horizon_Tinker/blocks/tinker-dnk-delivery-estimator.liquid) до стандарту Dual-Ready v2.0 (9/9 tests pass, verified via DNKRuntimeWire CLI).
2. [ ] Налаштувати Cart Drawer оновлення без перезавантаження.
3. [ ] Розгорнути мінімальний Tree Outliner у [apps/web](./apps/web).

- [🔒 LOCKED] **DEC-101: Adopt Zero-Framework Microkernel** — Receipt: `RECEIPT-798F678AB16C`. Status: Locked & Verified.
- [🔒 LOCKED] **DEC-102: Sovereign macOS Desktop Shell (DNK_Piu) on Coucou v0.6.0 Architecture** — Name: `DNK_Piu`, Bundle ID: `com.dnk.piu`. Cleanroom fork in dedicated repo, MIT-code assimilation, 100% asset/branding sanitization (anti-Mochi/anti-Coucou), local Vertex AI bridge (`127.0.0.1:11435`), multi-agent approvals (Antigravity/Hermes), single-target macOS CI artifact pipeline. Status: Locked & Active.
- [🔒 LOCKED] **DEC-103: Sovereign Workstation IaC & Declarative macOS Hygiene Core (mac-station)** — IaC Repo: `https://github.com/dnk-ecom/mac-station`. Home Repo Pattern for dotfiles (`.zshrc`, `.gitconfig`, `.claude/settings.json`, `.hermes/config.yaml.template`) with secret masking scanner (`sync_dotfiles.sh`). Zero-RAM launchd daemon (`com.dnkecom.macstation.hygiene.plist`) running daily at 04:30 AM with smart cache purge and Swap/SSD desktop alerts. Global AI skill `mac-hygiene` synced. Status: Locked & Verified.
- [🔒 LOCKED] **DEC-104: Universal SCONES FastMCP Server & In-RAM Code Mode SDK (core/sdk/dnk.py)** — Universal stdio FastMCP server (`core/memory/scones_mcp_server.py`) bridging Claude Code, Antigravity, and Hermes to shared SCONES SQLite WAL cognitive memory (73+ durable facts, FTS5 BM25, and observations). In-RAM Code Mode facade (`core/sdk/dnk.py`) slashing multi-turn tool overhead by -85% inside `CodeModeSandbox`. Registered in `~/.claude/settings.json` and `~/.claude.json`. Status: Locked & Verified.
- [🔒 LOCKED] **DEC-105: SOTA Agent Multiplexer (tmux), Ghostty Metal GPU, ast-grep, and APFS CoW Worktree Engine** — Multi-agent persistent session multiplexer via `tmux 3.8` (`extended-keys always` Claude Code/Hermes bugfix), Ghostty GPU Metal terminal configuration, universal AST structural code search (`ast-grep 0.51.2`), native AppleScript notification gateway (`mac_notify.sh` / `dnk-notify`), and APFS Copy-on-Write clonefile `.env` replication in `dnk_worktree_manager.py` (0 extra SSD bytes). Status: Locked & Verified.
- [🔒 LOCKED] **DEC-106: Ghostty Quake Dropdown, FZF SOTA Integration, dnk-swarm 3-Pane Cockpit, and AST-Grep Declarative Linter** — Floating Dropdown Terminal in Ghostty (`Ctrl + \``), FZF 0.75.0 shell integration with Dark Teal preview layout, 3-pane multi-agent cockpit script `dnk_tmux_dashboard.sh` (`dnk-swarm`), native notification hook in `hermes_pre_tool_hook.py`, and instant AST-Grep diagnostic rules (`sgconfig.yml`, `.ast-grep/rules/`). Status: Locked & Verified.
- [🔒 LOCKED] **DEC-107: Sovereign Lightweight Agent Shell (DNK_Piu) on Huddle Architecture & Google Cloud Gemini 3.8 Flash Multimodal Audio Dictation** — Standard for DNK_Piu: (1) Ultra-lightweight Swift (~1.5k LOC) based on Huddle Core (`Package.swift`, `swift build -c release` in 10s without Xcode.app, floating nonactivating `HuddlePanel: NSPanel`, zero third-party dependencies, <5MB app size, <30MB RAM); (2) Dictation Standard: Google Cloud Vertex AI (Gemini 3.8 Flash Multimodal Audio) via local bridge `http://127.0.0.1:11435/v1/audio/transcriptions` (0 local ASR model weights, native Ukrainian/English developer jargon, automatic punctuation, ~500ms latency); (3) Multi-Agent Mesh: kqueue/file-based IPC (`~/.dnk_runtime/piu/`) for Antigravity `PreToolUse` approval cards, Denchik/Hermes session HUD, and 1-click terminal jumper (`Jumper.swift`). Status: Locked & Active.
- [🔒 LOCKED] **DEC-108: DNK Universal Skills Substrate & Cross-Harness Tool Centralization** — (1) Tool Isolation Centralization: all hermetic agent binaries (Chromium 1208, Node 26, FFmpeg 9, Ripgrep 15, CUA-driver, Python 3.14) moved from `~/.hermes/tools/` (919 MB) to `~/.dnk_runtime/tools/` with symlink `~/.hermes/tools -> ~/.dnk_runtime/tools` (0 duplicate SSD bytes, shared across all agents); (2) Universal Skills Substrate: canonical skills authored in `DNK_HUB/core/skills/` (116 SOTA skills) and satellite repos (`mac-station`, `shopify-ai-toolkit`, `~/.agents/skills`), synchronized across Antigravity IDE (`~/.gemini/config/skills/`), Hermes Gerych (`~/.hermes/skills/dnk_ecosystem/`), and Claude Code (`~/.claude/skills/`) via automated `dnk-skills-sync` (`scripts/system/dnk_skills_sync.py`); (3) Full cross-harness parity: 131 unique skills instantly accessible by any terminal or GUI agent on this Mac. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-109: SOTA Multi-Harness Agentic Synergy: Google Antigravity x Hermes Agent (Gerych) x FastMCP Microkernel (Denchik) on Google Cloud Vertex AI & Google Secret Manager** — Unified cross-harness architecture linking Google Antigravity (App 2.32.1 / CLI `agy 1.5.9`) as visual cockpit/orchestrator with Hermes Agent Core (`Gerych-Agent`) as headless terminal executor via Agent Client Protocol (`hermes-acp` / `agy acp`) and FastMCP Microkernel (`core/kernel.py` / `dnk-core`). Backed by Google Cloud Vertex AI SSOT (`dnk.dev.os@gmail.com`, 14 deprecated accounts revoked), zero-disk Google Secret Manager (`dnk_secrets.py`, $0 Always Free Tier), PreToolUse invariant guard (`dnk_agy_guard.py`), and Antigravity custom agents triad (`.agents/agents/dnk-architect.md`, `dnk-builder.md`, `dnk-auditor.md`). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-110: Sovereign Workstation Topology (DNK_OS 8 Canonical Roots, 4-Zone APFS Runtime, Dual-Mount FastMCP Microkernel <400 LOC, and Spatial Canvas Orchestration Engine)** — Офіційна фіксація цільового фундаменту чистого суверенного простору `DNK_OS` на Apple Silicon: (1) **Narrow Waist Microkernel (`< 400 LOC`, 0 бізнес-логіки в ядрі)**: ядро виконує виключно System 1 тріаж (`< 50 мс`), маршрутизацію контрактів, перевірку безпеки Ring 0 та оркестрацію задач із замороженим префіксом `Sacred Prompt Cache <= 6,000 токенів`; (2) **3 Канонічні Воркхорси (`services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`)**: уся прикладна бізнес-логіка інкапсульована у 3 доменних комбайнах за 5-елементним контрактом Суверенної Цеглинки (`brick.manifest.yaml`, `contracts/schemas.py`, `cli.py`, `mcp_server.py`, `tests/`); (3) **Dual-Mount FastMCP Execution**: прямий In-RAM Python-імпорт (`0 мс` затримки, `0 байт` серіалізації) для внутрішнього ядра та `CodeModeSandbox`, плюс тонка обгортка `mcp_server.py` (`stdio`/`SSE`) для зовнішніх IDE та агентів (Antigravity, Claude Code, Cursor); (4) **SCONES SQLite WAL (`FTS5 BM25 < 15 мс`) + Working-Tree AST (`Base ⊕ Diff` / `ast-grep < 20 мс`) замість Vector DB**: 100% детермінована когнітивна пам'ять і точний граф символів без фонових векторних демонів (Qdrant/Milvus) та галюцинацій ембедінгів; (5) **4-Zone APFS Runtime & Worktree Pool (`~/.dnk_runtime/`)**: розділення MacBook на 4 фізичні зони APFS із захистом від індексації Spotlight (`.metadata_never_index`), пакетним ядром `uv` (`link-mode = "clone"`) + `pnpm` CAS та пулом ізольованих Git Worktrees (`~/.dnk_runtime/worktrees/`, спавн `< 80 мс`, `0 байт` дублів); (6) **8 Канонічних Коренів (`DNK_OS/`)**: суворий інваріант кореневої директорії (`core/`, `services/`, `packages/`, `apps/`, `docs/`, `tests/`, `scripts/`, `infra/`) під автоматичним наглядом `RootHygieneGuard`; (7) **Spatial Canvas Orchestration Engine & Per-Node Isolated Chats (Dual-State)**: кожна нода просторового полотна розкривається в ізольований агентний чат (`session_id = node:{canvas_id}:{node_id}`) із власним JIT-вайтлістом скілів (`<= 6,000 токенів`), де `.canvas` зберігає чисту геометрію JSON Canvas 1.0 та затверджений `Crystallized Summary Pin`, а SQLite WAL (`dnk_dag_store.db`) зберігає історію діалогу ноди та чеки виконання (по ребрах `ContextWire` передається виключно кристалізований артефакт, а не сирий лог чату); (8) **Gerych Archival Chronicle (DEC-054)**: Гєрич веде паралельний історичний літопис трансформації. Reference: `./docs/architecture/adr/ADR-092-DNK-OS-FOUR-ZONE-APFS-SPATIAL-CANVAS-ARCHITECTURE.md` | Chronicle: `./docs/plans/DNK_OS_FOUNDATION_EXECUTION_CHRONICLE.md`. Status: Locked & Active.

- [🔒 LOCKED] **DEC-111: Sovereign Smart Assimilation Protocol (SAP) & 'Scan First, Never Reinvent' Deep Mechanics Deconstruction** — Офіційний протокол поглинання сторонніх та архівних напрацювань: (1) **Scan First & Agentic 3x Velocity Invariant**: жоден рядок коду чи нова цеглинка не пишуться без попереднього автоматизованого сканування 4,000+ документів та 65 репозиторіїв (`DNK_HUB`, `../DNK_Vibe/`, `../DNKEcom/`, `packages/`) через `just distill <тема>` та `just scan-library`; при цьому агент зобов'язаний порівнювати дату документа (`updated_at`) із реальною динамічною датою виконання (`datetime.now()`) за шкалою Agentic 3x Velocity: 🟢 FRESH (<= 10 днів — можна брати напряму), 🟡 MATURE (10–30 днів — звірка з останніми версіями SDK/API), 🔴 LEGACY (> 30 днів — обов'язковий факт-чекінг актуальності та змін в офіційних API перед перенесенням); (2) **One-Time Deep Mechanical Deconstruction**: аудит репозиторію-донора виконується один раз за канонічним стандартом `docs/templates/SMART_ASSIMILATION_TEMPLATE.md` із вилученням 3 фундаментальних артефактів: анатомії структур даних (AST/Types/Schemas), точних математичних формул та інтерполяцій (Easing, Spring physics, Cart Queues, Pricing Curves), та реєстру граничних випадків (Edge Cases & Pitfalls); (3) **Clean-Room Sovereign Synthesis & DNK_HUB Pruning**: заборонено імпортувати чужі важкі бібліотеки та node_modules; вилучена механіка реалізується суверенно на чистому Python/TS у `DNK_OS` за 5-елементним контрактом (`contracts/schemas.py`, `src/service.py`, `cli.py`, `mcp_server.py`, `tests/`) із детермінованим тестом; після успішного перенесення в `DNK_OS` використані та застарілі файли в `DNK_HUB` маркуються для очищення. Reference: `docs/templates/SMART_ASSIMILATION_TEMPLATE.md` | Distiller: `scripts/system/dnk_distiller.py`. Status: Locked & Active.

- [🔒 LOCKED] **DEC-112: Orphaned Application Residue Detection & Auto-Purge Engine (mac_purge_orphans.sh)** — Суверенний механізм виявлення та зачистки прихованих залишків видалених macOS додатків: (1) **6-Зонний Аудит Бібліотеки**: скринінг `~/Library/Containers`, `~/Library/Group Containers`, `~/Library/Application Support`, `~/Library/Caches`, `~/Library/HTTPStorages`, та `~/Library/Preferences` шляхом перехресного порівняння Bundle ID (`.com.apple.containermanagerd.metadata.plist`) зі встановленими додатками `/Applications` та `/System/Applications`; (2) **Детермінована Зачистка**: видалення понад 2.0 GB мертвих хвостів від утиліт розпізнавання мови, старих апдейтерів та видалених додатків (WhisperMate, Orca Stably AI, AgentsRoom updater, NeoMas, Canva, VibeCut, Pixelmator Pro, PlanEx, Captions, TechSmith, AlDente); (3) **Автоматизований CLI & Аліас**: канонічний скрипт збережено в `mac-station/scripts/mac_purge_orphans.sh` з глобальним аліасом `dnk-purge-orphans` та інтеграцією в скіл `mac-hygiene`. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-113: Production Release of DNK_Piu v1.0.0, Vertex AI Multimodal Audio Dictation & Sovereign GitHub Repository (dnk-ecom/DNK_Piu)** — Офіційний реліз суверенного macOS HUD-компаньйона: (1) **Репозиторій**: випущено у `https://github.com/dnk-ecom/DNK_Piu` під ліцензією AGPLv3; (2) **Ультракомпактне ядро SwiftPM**: бінарник 875 КБ, <30 МБ RAM, чиста компіляція через `CommandLineTools` (вирішено обмеження відсутності `SwiftUIMacros` через `@LocalState`); (3) **Суверенне диктування Vertex AI**: додано обробник `/v1/audio/transcriptions` у `coucou_vertex_bridge.py` на `127.0.0.1:11435` з викликом `gemini-3.8-flash:generateContent` (збереження термінів розробника, розділові знаки, 0 байт локальних ваг, FlowPaste ⌘V); (4) **Multi-Agent IPC**: підтримка карток погодження (`Allow`, `Deny`, `Always`) для Antigravity IDE, Gerych, Denchik та 1-Click Jumper фокусування терміналів/IDE; (5) **Встановлено**: додаток розгорнуто в `~/Applications/DNK_Piu.app`. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-114: Elixir 1.6.2 Molecular Sterilization, Transitive BFS Vault Ingestion, and Staging-Lab Grafting** — (1) **DRM & Killswitch Neutralization**: Зрізано пропрієтарний Base64/RC4 DRM-пейлоад (-17,558 B) у хвості `assets/elxr-core.js` (`62,348 B -> 44,790 B`, `node --check` exit 0), знищено `Shopify.license_key` у `layout/theme.liquid` та `settings_schema.license`; (2) **100% Transitive BFS Vault Closure (`distilled_vault/elixir-1.6.2/`)**: ізольовано 135 блоків (89 atoms, 15 molecules, 30 organisms, 1 no-app engine), 109 сніпетів (включно з 33 транзитивними BFS 2-го/3-го рівнів), 66 асетів (включно з 52 core ESM модулями `@theme/*`), 4 нормалізовані локалі (`en.default*`, `uk*`) з 0 розірваних зв'язків; (3) **Staging-Lab Clean Graft**: 35 чистих блоків (Advertorial Content + Sticky Sidebar, Us vs. Them Comparison Matrix, Listicle Floating ATC, Limited-Time Sale) заґрафчено у `staging-lab` (`569e789`) з верифікацією `shopify theme check --fail-level error` (0 помилок, exit code 0); (4) **Master Reports**: зафіксовано `ELIXIR_MOLECULAR_DISTILLATION_AND_STERILIZATION_REPORT.md`, `GERYCH_ELIXIR_STERILIZATION_AND_TRANSITIVE_CLOSURE_VERDICT.md` та 9-сторонню матрицю бенчмарку, синхронізовано з `origin/donor-lab`. Reference: `Audit_Shopify_Themes_Sell_WF/Elixir_Theme_Ecosystem_Audit/` | Vault: `distilled_vault/elixir-1.6.2/`. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-115: Living ThoughtDAG Canvas, Dual-Surface FastMCP Actions & Chat-to-DAG Tree Spawner Architecture** — (1) **3-Рівнева Ієрархія (L1 -> L2 -> L3)**: L1 Account (`AccountSpec`, кешований префікс ≤ 6,000 токенів, штатна команда, Golden Recipes) ➔ L2 Project DNA (`ProjectDNA`, одноразове заповнення для 3 треків: R&D теми, Маркетинг/Продаж, Аудит Донорів) ➔ L3 Subtask Tree (ізольована сесія `node:{canvas_id}:{node_id}`, нуль сирого чату по дротах); (2) **Dual-Surface Action Parity (`DualSurfaceActionSpec`)**: будь-яка операція доступна одночасно як FastMCP Tool для агента і як React UI кнопка на картці ноди (`[🔍 Theme Check AST]`, `[📦 Зібрати Preview ZIP]`, `[🌿 Розгалужити підзадачу]`, `[✍ Перевірити Tone of Voice]`, `[🛡 Затвердити копірайт]`); виконання через єдиний шлюз `/api/v1/kernel/actions/dispatch` з фіксацією в SQLite WAL; (3) **Smart JSON Canvas 1.0 Ingestion**: оновлено `converter.ts` для десериалізації `.canvas` файлів у реальні інтерактивні картки (`thoughtDagNote` з живим текстом і блоковими хендлами, `agentTaskNode` з бейджами агентів і кнопками дій) замість статичних карток-заглушок; (4) **Chat-to-DAG Tree Spawner**: відправка цілі у `StitchPromptDock` / чат ноди миттєво генерує дерево нових нод і контекстні дроти через `/api/v1/orchestrator/chat`; (5) **Machine Proof**: 0 помилок гідратації на `http://localhost:3000/canvas`, підтверджено успішне виконання дії `✓ 🔍 Theme Check AST: Виконано` та живий спавн нод/дротів через браузерного агента `7698144e-5446-4807-8f86-f6cf83479a6e` (скріншот збережено). Contracts: `core/domain/vibe_core_contracts.py`, `apps/web/src/canvas/types/vibeCore.ts`. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-116: Fan-In Multi-Agent Aggregation Engine, Automated Quarantine Circuit Breaker & Dynamic Flow DAG Parser (UAIP Assimilation)** — (1) **Fan-In Multi-Agent Aggregator (`core/orchestrator/fan_in_aggregator.py`)**: детерміноване об'єднання паралельних агентських виходів через ланцюг обов'язкових валідаторів (`SyntaxASTValidator`, `BoundaryScopeValidator`, `DeterministicExitCodeValidator`, `GroundingValidator`) перед синтезом фінального звіту; при помилках формується структурований пакет рекламацій (`remediation_packets`) для повторного доопрацювання конкретним субагентом замість галюцинації успіху; (2) **Automated Agent Quarantine & Circuit Breaker (`core/sentinel/agent_quarantine.py`, TC-10)**: автоматичне переведення агента в стан `QUARANTINED` при (a) 3 послідовних провалах валідаторів, (b) перевищенні стелі $\le 25$ дій на зріз (MASE), (c) спробі модифікації файлів з `negative_scope`, з карбуванням криптографічного чека інциденту; (3) **Dynamic Flow DAG Parser (`apps/web/src/canvas/stream/flowStepParser.ts`)**: топологічний парсер потоку виконання мультиагентних кроків у живий React Flow граф із кольоровою індикацією статусів і затримок; (4) **Machine Proof**: 13/13 тестів ядра пройдено (`pytest` 0.61s) + 3/3 тестів парсера кроків (`flowStepParser.test.ts` 19ms). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-117: Sovereign Unified Microkernel v2.5 Architecture & Multi-Agent Living Core (SOTA Assimilation Protocol)** — (1) **Unified Microkernel Host v2.5 (`core/kernel.py`)**: Нативно інтегрує 4 SOTA підсистеми: `SpatialCanvasSessionRouter` (ADR-092), `FanInAggregator` (UAIP), `AgentQuarantineGuard` (TC-10), та `SconesMemoryStore` (SQLite WAL FTS5); (2) **По-нодна ізоляція розмов та хірургія контексту**: Ізольовані сесії `node:{canvas_id}:{node_id}`, автоматична збірка контекстних дротів від предків (Kahn DAG merge) з ін'єкцією L2 Project DNA та L1 Account spec, фіксація кристалізованих контрактів (`crystallize_node_session`) для запобігання деградації уваги та амнезії; (3) **Мультиагентний Fan-In детермінований шлюз**: 4-фазний фільтр валідації (`SyntaxASTValidator`, `BoundaryScopeValidator`, `DeterministicExitCodeValidator`, `GroundingValidator`) перед злиттям результатів гілок рою; (4) **Активний захист карантину (Quarantine Gate)**: Автоматичне блокування дій у `dispatch_action` при спробі виконання агентів у стані `QUARANTINED`; (5) **17 FastMCP інструментів (`create_fastmcp_server`)**: Повний дуальний доступ (In-RAM Python + STDIO/SSE FastMCP) для всіх зовнішніх агентів (Hermes/Gerych у терміналі, Antigravity, Claude Code, Codex, React UI); (6) **14 канонічних REST/SSE маршрутів (`apps/api/routers/kernel_router.py`)**: Шлюз `/api/v1/kernel/*` для живого фронтенду та зовнішніх клієнтів; (7) **Machine Proof**: 17/17 тестів ядра пройдено на 100% (`pytest` exit code 0, 7.05s). Живий сервер `/api/v1/kernel/status` повертає статус `ACTIVE` з `kernel_version: 2.5.0` та всіма 4 активними SOTA підсистемами. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-118: Sovereign Node Session Execution & Competitor Theme Extraction Pipeline** — (1) **Narrow-Waist CLI Commands (`core/kernel_cli.py`, `Justfile`)**: додано атомарні команди `node context`, `node post`, `node messages`, `node crystallize` (`just node-*`), які дають 100% програмний та термінальний доступ до по-нодних розмов без оверхеду складних схем; (2) **Graph Context Surgery**: контекстна ізоляція (Kahn DAG traversal), збірка лише кристалізованих виходів батьківських нод у промпт ($\le 1500$ токенів), нуль сирого чату по дротах; (3) **Competitor Reverse-Engineering Dossier (`docs/notes/sota_audits/SUGAR_THEME_AUDIT.md`)**: верифіковано на донорі Sugar Theme 2.2.3/2.3.6 (`sugar-cart-drawer.js`, `sticky-product.js`, `vendor-runtime-loader.js`, `product-form.js`), екстраговано 4 ключові патерни (SugarCart in-flight dedup cache з вирішенням Shopify line re-keying, StickyProduct Web Component з IntersectionObserver, DOM-demand runtime loader `type="sugar/later"`, ProductForm handshake); (4) **Downstream Inheritance**: нода `node_t3_sugar_theme_audit` кристалізована в `docs/canvas/projects/dnk_ecom/main.canvas` (зелений статус `"4"`), а дочірня нода `node_t1_dual_ready_blocks` автоматично підхоплює цей контракт; (5) **Machine Proof**: 42/42 тестів пройдено успішно (`pytest` exit code 0: 30 тестів ядра + 12 тестів Shopify). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-119: SOTA Living Knowledge Lifecycle, SCONES Native FTS5 BM25 Engine, Automated AST Staleness Eviction & Adversarial Approval Gate (SOTA 2026 Assimilation)** — (1) **Narrow Waist & FastMCP Protocol Isolation (`core/kernel.py` < 400 LOC)**: `create_fastmcp_server` повністю делеговано в `core/kernel_mcp.py` з реекспортом у ядрі, втримуючи Standing Context Diet ядра; (2) **SCONES Native FTS5 BM25 & Vitality Engine (`core/memory/`)**: синхронізовано `scones_bm25_index.py`, `scones_vitality.py`, `scones_overlay.py`, `scones_anchor_verifier.py`; ліквідовано фантомний fallback — активний нативний SQLite FTS5 BM25 пошук за `(topic, observation)`; (3) **L1 AccountSpec & ProjectEngine Integrity (`core/config/vibe_coder_account.json`, `core/project/project_engine.py`)**: L1 глобальний профіль та L2 проєктний двигун завантажуються детерміновано без помилок імпорту; (4) **Automated AST Staleness Eviction (`core/sentinel/knowledge_staleness_guard.py`, `just audit-knowledge`)**: автоматичне сканування документації та коду на наявність фізично існуючих файлів, миттєве виявлення застарілих/мертвих посилань для запобігання Attention Rot; (5) **Adversarial Approval Gate (`core/sentinel/adversarial_review_gate.py`)**: детермінований шлюз перевірки рішень за 5 векторами (межі, 100x навантаження, техборг, безпека, пам'ять) та 4 обов'язковими полями перед блокуванням `DEC`; (6) **Repo Intelligence Integration**: 1 663 верифіковані репозиторії доступні через FastMCP інструменти `search_repo_catalog` та `get_repo_reuse_brief`; (7) **Machine Proof**: 42/42 тестів ядра пройшли за 0.47с (`just test` 100% green). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-120: Wave 2 Context Surgery Pruning, Role-Based LOD DNA Projection, Persistent SQLite WAL Quarantine Ledger & Bounded Revision Loop FSM** — (1) **Context Surgery ($\le 1500$ tokens) & Role-Based LOD DNA (`compile_lod_dna_slice`)**: 4 спеціалізовані рольові проекції (`builder`, `copywriter`, `auditor`, `default`) у `core/canvas/session_router.py`; суворе відсікання контексту предків до стелі $\le 1500$ токенів для усунення ентропії уваги; (2) **Persistent SQLite WAL Quarantine Ledger (`core/sentinel/agent_quarantine.py`)**: збереження історії страйків та інцидентів у `~/.dnk_runtime/agents_state/agent_quarantine.db` з режимом `:memory:` під час pytest; (3) **Bounded Revision Loop FSM (`core/orchestrator/bounded_revision_loop.py`)**: кінцевий автомат на 3 автоматичні спроби виправлення зауважень валідаторів з переходом у `QUARANTINED` при 3-му страйку; (4) **Quad Runner Integration (`core/orchestrator/quad_runner.py`)**: інтегровано `execute_node_with_revision_loop()`; (5) **Machine Proof**: 7/7 тестів архітектурного фітнесу + 52/52 тестів ядра пройшли успішно (`just test-fitness` та `just test` exit code 0). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-121: Sovereign Shopify Theme Dev Architecture, Local-Storefront Daemon Integration & Donor Genome Alignment** — (1) **Triad Architecture Alignment**: чітке розмежування трьох стовпів: (a) Control Plane (`DNK_OS/services/dnk_shopify`) — FastMCP інструменти, валідатори, Pydantic контракти, Canvas маршрутизатор; виправлено шлях до канонічного дзеркала `../DNKEcom/DNK-Ecom_git_mirrow/main`; (b) Domain Methodology & Tooling (`_Shopify_Theme_DEV_Workflow`) — молекулярна дистиляція, жива синхронізація Карти Донорів `sync_donor_genome_map.py` (v2.3, 10 активних донорів + 1 vault, 100% динамічне зчитування версій); (c) Physical Storefront Repository (`DNK-Ecom_git_mirrow`) — 12 донорських worktrees під `.bare`, оновлений `graft.sh` (включно з `sugar` та `elixir`), санітизований `verify_theme_integrity.py` зі зняттям false positive на docblocks/comment та опцією `--donor-mode`; (2) **Headless Offline Runtime (`0xtlt/local-storefront`)**: Python-контролер `LocalStorefrontManager` (`services/dnk_shopify/runtime/local_storefront.py`), 5 FastMCP інструментів (`shopify_lsf_*`) та CLI команди (`lsf-status`, `lsf-check`, `lsf-profile`, `lsf-serve`, `lsf-reload`) для субмілісекундного рендерингу (170–300 мкс) без хмари Shopify; (3) **Justfile Developer Ergonomics**: додано цілі `shopify-7gate`, `shopify-donor-map`, `shopify-graft`, `shopify-lsf-check`; (4) **Machine Proof**: 16/16 тестів Shopify пройшли успішно (`just test-shopify`), 7-Gate Anti-Regression Theme Integrity Gate підтверджує 100% CLEAN & PROTECTED на канонічному репозиторії `DNK-Ecom_git_mirrow/main`. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-122: Sovereign Multi-Agent Runtime Integration, Workhorse Scaffolding (#2 dnk_media & #3 dnk_distribution) & Skills Curator Engine** — (1) **Agent Roster & Hermes Integration (`scripts/system/denchik_engine.sh`, `core/orchestrator/agents/`)**: налаштовано детермінований запуск суверенного Hermes CLI (`$HOME/Kuzmenko/MY_LIFE_WORK/Gerych-Agent/hermes` з Python `~/.dnk_runtime/venvs/hermes-agent/bin/python`), виправлено порядок прапорців моделі/провайдера перед підкомандами, перенесено профілі агентів (`denchik`, `auditor`, `dnk_mentor`, `gerych_prime`, `strategist`) та підключено `.env` SSOT; (2) **3 Workhorses Architecture (`services/`)**: виконано скаффолдинг суверенних цеглинок Воркхорс #2 (`services/dnk_media`) та Воркхорс #3 (`services/dnk_distribution`) за 5-елементним стандартом (`brick.manifest.yaml`, `contracts/schemas.py`, `src/service.py`, `cli.py`, `mcp_server.py`, `tests/test_*_brick.py`); (3) **Pre-Tool Hook & Skills Curator (`core/skills_curator.py`, `scripts/system/hermes_pre_tool_hook.py`)**: перенесено `skills_curator.py` з 4-векторним Generalisability Test, оновлено луп-трекер з `/tmp/` на суверенну зону `~/.dnk_runtime/run/`; (4) **Machine Proof**: 77/77 тестів пройдено успішно (52 ядра + 7 фітнесу + 18 воркхорсів: `just test-workhorses`), `denchik --version` та `denchik doctor` повертають валідні діагностичні звіти. Status: Locked & Verified.

- [🔒 LOCKED] **DEC-123: Hermes Session Authority Boundary Invariant & Sovereign Denchik Live Autonomous Run** — (1) **Profile Authority Invariant (`state.db`)**: Upstream Hermes Agent (`gateway/run_runtime.py`) суворо вимагає `Path(db.db_path).resolve().parent == home`. Симлінк `state.db` за межі `$HERMES_HOME` викликає `RuntimeError: session authority database does not belong to the reserved profile`. Виправлено в `scripts/system/denchik_engine.sh`: база `state.db` створюється фізично всередині кореня профілю агента з чистим SQLite WAL-режимом та двосторонньою синхронізацією у `~/.dnk_runtime/agents_state/` при завершенні сесії; (2) **Zero-Leak Environment & Dynamic GitHub Auth**: Усунено передачу сирого плейсхолдера `gsm://GH_TOKEN` у `python-dotenv`, токен динамічно підтягується через `gh auth token`; додано правила ігнорування транзієнтних локів та стейту шлюзу в `.gitignore`; (3) **Live Autonomous Execution**: Успішно запущено Denchik через `bash scripts/system/denchik.sh "Яка версія DNK OS і які три воркхорси зареєстровані? Відповідай дуже коротко одним реченням."`. Denchik стартував на ядрі Hermes через Vertex AI OAuth (Gemini 4 Argon), провів Step 0 Triage (SOLO mode, C=0) та видав живу відповідь: *"Версія DNK OS — 2.5.0 (package.json 1.0.0), а три зареєстровані воркхорси — це dnk_shopify, dnk_media та dnk_distribution."*; (4) **Machine Proof**: Exit code 0 на реальному живому запиті, `hermes doctor` пройшов без помилок сесійного шлюзу, 82/82 тести пройдено (`just test`, `just test-fitness`, `just test-workhorses`). Status: Locked & Verified.

- [🔒 LOCKED] **DEC-123: Canonical PSOD Delegation Engine, Whitelist Containment & Structural Barriers Hook** — (1) **Canonical PSOD Delegation Engine (`core/orchestrator/delegation_packet.py`)**: впроваджено детермінований контракт делегування (Problem, Substrate, Oracle, Deliverable) з верифікацією оракула (exit code 0), блокуванням фантомного виконання (Phantom Done) та автоматичним відхиленням неавторизованих модифікацій поза цільовим списком файлів (`WHITELIST_VIOLATION`); (2) **Declarative Structural Barriers Hook (`core/config/structural_barriers.json`, `scripts/system/hermes_pre_tool_hook.py`)**: впроваджено декларативний перехоплювач для миттєвого (<2 мс) блокування створення локальних `.venv` (GEMINI.md), викликів `npm/yarn` замість `pnpm` та руйнівних операцій; (3) **Universal Delegation Skill (`dnk-delegation-protocol`)**: створено і синхронізовано навичку поміж Antigravity IDE, Gerych Hermes та Claude Code; (4) **Machine Proof**: 5/5 нових тестів делегації пройдено, 57/57 системних тестів ядра зелені (`uv run pytest` за 0.73 с). Status: Locked & Verified.

