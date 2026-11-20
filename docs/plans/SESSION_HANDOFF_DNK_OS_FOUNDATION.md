---
title: "DNK OS Foundation & Session Handoff Bridge"
description: "Canonical Session Handoff & Continuity Bridge: Architecture, Invariants, Dependencies, and Active Backlog for DNK_OS."
mrh_id: "docs/plans/SESSION_HANDOFF_DNK_OS_FOUNDATION.md"
status: Active
archetype: GENERAL_DOC
version: "2.8.0"
updated: 2026-11-20
tags:
  - dnk-os
  - architecture
  - handoff
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/plans/SESSION_HANDOFF_DNK_OS_FOUNDATION.md"
> purpose: "Canonical Session Handoff & Continuity Bridge: Architecture, Invariants, Dependencies, and Active Backlog for DNK_OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.8.0"
> updated_at: "2026-11-20"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌉 DNK OS Foundation & Session Handoff Bridge

> **Призначення**: Цей документ є єдиним канонічним містком безперервності (Continuity Bridge) між сесіями проєктування.
> Всі рішення (DEC-110 .. DEC-163) зафіксовані в режимі `[🔒 LOCKED]` у [DECISION_REGISTRY_ADHD.md](../architecture/DECISION_REGISTRY_ADHD.md) і не підлягають амнезії чи повторним обговоренням з нуля.

---

## 1. 🏛️ Статус репозиторіїв та синхронізація

1. **Суверенний воркспейс `DNK_OS`**:
   - `DNK_OS` є єдиним чистим бойовим репозиторієм DNK OS MVP.
   - Структура відповідає **Canonical 8-Root Directory Invariant**: `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`.
   - `DNK_HUB` назавжди переведений у статус **Read-Only архіву R&D знань** (`DEC-117 [🔒 LOCKED]`).
2. **Суверенний macOS клієнт `DNK_Piu`**:
   - Суверенний Swift / SwiftUI клієнт диктування на Mac (`../DNK_Piu`).
   - Синхронізований з GitHub (`main` branch up to date).
   - Включає суб-700ms ASR на базі Gemini 3.5 Flash Transcribe, апаратне AAC кодування, динамичний DNA floating pill та Solar Duotone мікрофон (DEC-166 .. DEC-169).

---

## 2. 🔒 Зафіксовані ключові архітектурні рішення (DEC-110 .. DEC-163)

| Рішення | Назва | Суть та статус |
| :--- | :--- | :--- |
| **DEC-110** | **Clean Foundation & Standalone Release** | Відокремлення бойового ядра `DNK_OS` від експериментального хабу `DNK_HUB`. `[🔒 LOCKED]` |
| **DEC-117** | **Sovereign Unified Microkernel v2.5.0** | Єдине ядро `core/kernel.py`: Spatial Canvas Router, Fan-In Aggregator, Quarantine Sentinel, SCONES FTS5 Memory. `[🔒 LOCKED]` |
| **DEC-126** | **Turnkey Shopify Dev Squad** | Workhorse #1 (`services/dnk_shopify`): 5 спеціалізованих агентів + Pipeline Runner. 75/75 тестів пройшли. `[🔒 LOCKED]` |
| **DEC-128** | **Dual-Surface Action Registry** | Двосторонній Action Bus між Next.js Living Canvas та FastMCP бекендом. `[🔒 LOCKED]` |
| **DEC-153** | **Unified 9:16 Video Composition Pipeline** | Workhorse #2 (`services/dnk_media`): чиста збірка відеокомпозицій, субтитри, аудіо-дизайн. `[🔒 LOCKED]` |
| **DEC-159** | **Sovereign GEO llms.txt & Merchant Feed** | Нативна підтримка Generative Engine Optimization (GEO) та XML-фідів Google Merchant. `[🔒 LOCKED]` |
| **DEC-160** | **C2PA Media Provenance & Theme Renaming** | Повна криптографічна фіксація автентичності контенту (C2PA) та закріплення назви теми `DNK Ecom` (Зерно / v0.1.0). `[🔒 LOCKED]` |
| **DEC-162** | **Sovereign Social Media Scanner** | Workhorse #3 (`services/dnk_distribution`): автономний сканер TikTok, Reddit, YouTube та асиміляція правил агентів. `[🔒 LOCKED]` |
| **DEC-163** | **Sovereign AI Brand Kit & Theme Distiller** | Генерація `DESIGN.md` (Google Labs), `BRAND.md` (Zero-Hallucination Quotes), `SKILL.md` (Every Time Guard) та Edge Showcase на Cloudflare Pages. `[🔒 LOCKED]` |

---

## 3. 🐴 Статус трьох головних робочих конячок (3 Core Workhorses)

1. **Workhorse #1: `services/dnk_shopify` (`DNK_Ecom` v0.1.0 "Зерно")**:
   - Повна відповідність стандартам Shopify Theme Store: 7 клієнтських шаблонів (`templates/customers/*`), секції `main-customers-*`, SaaP Dual-Ready блоки.
   - `shopify theme check` = 0 помилок на 280+ файлах. Готовий релізний zip-архів: `services/dnk_shopify/release/DNK-Ecom-Zerno-v.0.1.0.zip`.
2. **Workhorse #2: `services/dnk_media`**:
   - Суверенний пайплайн генерації вертикальних 9:16 відео, C2PA provenance водяні знаки, ліквідація тиші, кінетичні субтитри.
3. **Workhorse #3: `services/dnk_distribution`**:
   - Автономний збирач та аналізатор вірусного соцмережевого контенту, адаптер каналів, черга публікації через outbox daemon.

---

## 4. ⚙️ Рантайм, залежності та команди `just`

Всі залежності налаштовані за принципом **Zero-Waste APFS Hardlink Store**:
- **Python**: Керується `uv`, venv знаходиться у `~/.dnk_runtime/venv` та підключений через симлінк `DNK_OS/.venv`.
- **Node.js**: Керується `pnpm`, глобальний стор `~/.dnk_runtime/pnpm-store/v10`.
- **Командний центр**: `Justfile`.

```bash
# 1. Запуск усіх тестів ядра
just test

# 2. Запуск тестів Shopify Workhorse #1
just test-shopify

# 3. Перевірка статусу системи
just status

# 4. Запуск FastAPI сервера (порт 8000)
just api

# 5. Запуск повного детермінованого аудиту
bash scripts/verify_all.sh
```

---

## 5. 📋 Активний беклог задач для нової сесії

### Пріоритет 1: Shopify Theme Store публікація та дистиляція нових CRO-блоків
- [ ] Запустити фінальну валідацію `services/dnk_shopify/DNK_Ecom` через live Shopify CLI Storefront.
- [ ] Інтегрувати дистильовані дизайн-токени з `docs/projects/dnk_ecom/distillations/pergolux/` у живий прев'ю-стенд.

### Пріоритет 2: DNK OS Living Canvas & Cockpit UI
- [ ] Перевірити роботу живого канвасу (`apps/web/app/workspace/agent/page.tsx`) з реальними WebSocket/SSE подіями від Action Bus.
- [ ] Протестувати двосторонню синхронізацію нод канвасу з Taskboard SQLite (`test_taskboard_canvas_sync.py`).

### Пріоритет 3: DNK_Piu інтеграція з DNK_OS
- [ ] Підключити локальний сокет/HTTP міст між macOS застосунком `DNK_Piu` та ядром `DNK_OS` (`apps/api/routers/kernel_router.py`) для передачі розпізнаного голосового контексту безпосередньо у `dispatch_thought`.

---

## 6. 🚀 Інструкція: Як стартувати з чистого листа

1. **Очистити контекст / Відкрити нову сесію**.
2. **Перший промпт у новій сесії**:
   > *"Продовжуємо роботу по беклогу з `docs/plans/SESSION_HANDOFF_DNK_OS_FOUNDATION.md`. Поточні архітектурні рішення зафіксовані в `docs/architecture/DECISION_REGISTRY_ADHD.md` (DEC-110 .. DEC-163). Приступаємо до Пріоритету 1 (або конкретної підзадачі)."*
3. Агент з 0 токенами на старті зчитує лише цей файл і одразу працює на 100% швидкості без протиріч.

---

## 3. 🧠 Архітектура ядра Microkernel v2.5.0 (`core/kernel.py`)

Ядро об'єднує чотири асимільовані світові SOTA-патерни:

```mermaid
flowchart TD
    User["Founder (Maxim) / External Agent"] -->|Thought / Prompt| Router["Spatial Canvas Session Router\n(core/canvas/session_router.py)"]
    Router -->|Node Context DAG| NodeChat["Per-Node Chat Session\nnode:canvas_id:node_id"]
    NodeChat -->|Dispatch Action| Quarantine{"Agent Quarantine Guard\n(TC-10 Circuit Breaker)"}
    Quarantine -->|Allowed| ActionBus["Action Bus & FastMCP Tools\n(17 Sovereign Tools)"]
    Quarantine -->|Blocked (3 Errors)| Fail["Quarantine Action Intercepted"]
    ActionBus --> MultiAgent["Multi-Agent Swarm / Workers"]
    MultiAgent -->|Candidate Outputs| FanIn["Fan-In Deterministic Aggregator\n(4-Gate Verification Chain)"]
    FanIn -->|AST + Scope + Exit 0 + Grounding| Crystallized["Crystallized Node Contract & Memory"]
    Crystallized --> SCONES["SCONES SQLite WAL FTS5 Store\n(.data/scones_memory.sqlite)"]
```

### Ключові інваріанти моделі Human $\leftrightarrow$ Chat $\leftrightarrow$ Nodes:
1. **L1 Account $\to$ L2 Project DNA $\to$ L3 Task Tree**:
   - Кожна нода канвасу наслідує специфікацію облікового запису (L1) та маніфест бренду (L2 `brand_dna.json`).
2. **По-нодна ізоляція розмов (Per-Node Context Surgery)**:
   - Сесії мають вигляд `node:{canvas_id}:{node_id}`. Жоден агент не отримує 100k контексту монолітом. Upstream контекст підтягується через топологічне сортування Kahn DAG.
3. **Fan-In 4-Gate Chain**:
   - `SyntaxASTValidator`: відсікає синтаксичні помилки.
   - `BoundaryScopeValidator`: перевіряє Negative Scope та Target Whitelist.
   - `DeterministicExitCodeValidator`: вимагає Exit Code 0 на тестах.
   - `GroundingValidator`: блокує галюцинації файлових змін без фізичного запису на диск.

---

## 4. 🛠️ FastMCP 17 інструментів & REST API

### FastMCP сервер `dnk-core` (налаштовано в `.agents/mcp_config.json`):
1. `dispatch_thought` — структурування необробленої думки в Obsidian Canvas / DAG.
2. `execute_action` — виконання дії через Action Bus.
3. `query_memory` — повнотекстовий пошук у SCONES FTS5.
4. `record_observation` — збереження емпіричного спостереження в базу знань.
5. `request_approval` — запит на підтвердження деструктивної дії.
6. `get_system_status` — телеметрія 4 підсистем ядра.
7. `inspect_code_map` — перевірка AST мапи модулів.
8. `prune_output` — очищення шумних логів (token diet).
9. `search_clipboard` — семантичний пошук у кліпборді ідей.
10. `get_clipboard_projects` — список проєктів з кліпборду.
11. `get_clipboard_screenshots` — отримання скріншотів-референсів.
12. `node_session_get_context` — отримання контексту ноди канвасу.
13. `node_session_post_message` — повідомлення у сесію ноди.
14. `node_session_crystallize` — фіксація артефакту ноди для спадкоємців.
15. `fan_in_validate_and_aggregate` — 4-шлюзова валідація результатів рою.
16. `quarantine_get_status` — статус circuit breaker для агента.
17. `quarantine_release_agent` — ручний випуск агента з карантину.

### REST API (`apps/api/main.py`):
- `GET /health` — liveness probe.
- `GET /api/v1/status` — загальний статус та активні підсистеми.
- `GET /api/v1/kernel/status` — глибока телеметрія ядра.
- `POST /api/v1/kernel/canvas/node-session/message` — взаємодія з нодою канвасу.
- `POST /api/v1/kernel/fan-in/validate-and-aggregate` — запуск агрегатора гілок.

---

## 5. ⚙️ Рантайм, залежності та перевірка працездатності

Всі залежності налаштовані за принципом **Zero-Waste APFS Hardlink Store**:
- **Python**: Керується `uv`, venv знаходиться у `~/.dnk_runtime/venv` та підключений через симлінк `DNK_OS/.venv`.
- **Node.js**: Керується `pnpm`, глобальний стор `~/.dnk_runtime/pnpm-store/v10` (0 байт дублювання).
- **Командний центр**: `Justfile`.

### Команди `just`:
```bash
# 1. Запуск усіх тестів ядра (28 тестів)
just test

# 2. Запуск тестів Shopify Workhorse #1 (12 тестів)
just test-shopify

# 3. Перевірка статусу системи
just status

# 4. Запуск FastAPI сервера (порт 8000)
just api

# 5. Запуск FastMCP сервера через STDIO
just mcp-stdio
```

> **Machine Proof**: 40/40 тестів пройдено успішно (Exit Code 0).

---

## 6. 📋 Активний беклог задач у `DNK_OS`

### Трек 3: Аудит та адаптація донорських репозиторіїв
- [x] Здійснити аудит Sugar Theme (`node_t3_sugar_theme_audit`): екстраговано патерни `SugarCart`, `StickyProduct`, `vendor-runtime-loader`, `ProductForm` у [SUGAR_THEME_AUDIT.md](../notes/sota_audits/SUGAR_THEME_AUDIT.md).
- [ ] Витягти найкращі CRO UI-паттерни в бібліотеку компонентів Apex (наступні донори: Story, Shrine, Ella).

### Трек 1: Shopify Apex CRO Theme (Workhorse #1)
- [x] Pre-Setup Architecture & 32-Point Theme Store Acceptance Checklist (DEC-127, [13_SHOPIFY_THEME_STORE_PRE_SETUP_AND_ACCEPTANCE_CHECKLIST.md](../../../DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/13_SHOPIFY_THEME_STORE_PRE_SETUP_AND_ACCEPTANCE_CHECKLIST.md)) `[🔒 LOCKED]`
- [ ] Додати відсутні обов'язкові клієнтські шаблони `templates/customers/*` (`account`, `login`, `addresses`, `order`, etc.) у цільове ядро `dnk-sovereign-apex` для 100% проходження шлюзу Theme Store.
- [ ] Фізичний синтез SaaP Dual-Ready v2.0 блоків у `services/dnk_shopify/DNK_Sovereign_Apex/blocks/` (`node_t1_dual_ready_blocks`):
  - `sticky_atc_bar.liquid` + `dnk-cart-bus.js` (на основі Sugar)
  - `tiered_discount_table.liquid`
  - `trust_badge_grid.liquid`
  - `social_proof_marquee.liquid`
- [ ] Перевірити сумісність з Shopify Tinker 4.2.0 та Theme Store стандартами (`shopify theme check`).

### Трек 2: Клієнтський портал та генератор пропозицій (Client Portal)
- [ ] Доопрацювати `docs/projects/dnk_ecom/proposal_client_portal.html`:
  - Підключення реального розрахунку ROI та конверсійного сплеску.
  - Інтерактивна генерація PDF/HTML аудиту магазину клієнта.
  - Синхронізація з `brand_dna.json` та `project.manifest.yaml`.

---

## 7. 🚀 Інструкція: Як переключити робочу сесію в `DNK_OS`

1. **В IDE Antigravity / Cursor / VS Code**:
   - Натисніть `File -> Open Folder...` (або `Cmd + O` на Mac).
   - Оберіть директорію: `../DNK_OS`.
   - (Або відкрийте `DNK_OS.code-workspace`).
2. **Перевірте наявність інструментів FastMCP**:
   - Файл `.agents/mcp_config.json` автоматично підключає сервер `dnk-core` з 17 інструментами.
   - Субагенти `dnk-builder`, `dnk-architect`, `dnk-auditor` готові до роботи в `.agents/agents/`.
3. **Перший запит у новому воркспейсі**:
   - Почніть сесію з фрази:
     > *"Продовжуємо роботу по беклогу з `docs/plans/SESSION_HANDOFF_DNK_OS_FOUNDATION.md`. Приступаємо до Треку 1 (або Треку 2)."*
   - Будь-який агент негайно підхопить зафіксований контекст без втрати пам'яті.
