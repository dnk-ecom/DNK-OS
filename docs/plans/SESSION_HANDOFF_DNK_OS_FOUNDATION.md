---
title: "DNK OS Foundation & Session Handoff (DEC-110 / DEC-117)"
status: "Active"
type: "plan"
domain: "core"
author: "Antigravity & Maxim"
version: "1.0.0"
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
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "Antigravity & Maxim"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌉 DNK OS Foundation & Session Handoff Bridge

> **Призначення**: Цей документ є єдиним канонічним містком безперервності (Continuity Bridge) між сесією проєктування в інкубаторі `DNK_HUB` та суверенним бойовим воркспейсом **`DNK_OS`** (`/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS`).
> Всі рішення зафіксовані в режимі `[🔒 LOCKED]` і не підлягають амнезії чи повторним обговоренням з нуля.

---

## 1. 🏛️ Статус переходу та рольовий розподіл (DEC-110, DEC-117)

1. **Суверенний воркспейс `DNK_OS`**:
   - `DNK_OS` є єдиним чистим бойовим репозиторієм DNK OS MVP.
   - Структура відповідає **Canonical 8-Root Directory Invariant**: `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`.
   - `DNK_HUB` назавжди переведений у статус **Read-Only архіву R&D знань** (`DEC-117`). Жодна нова розробка в `DNK_HUB` не ведеться.

2. **Розподіл ролей агентів**:
   - **Antigravity (Mentor / Architect)**: Архітектурний нагляд, контроль інваріантів, якісні шлюзи, рев'ю PR.
   - **Denchik (Денчік — Sovereign Master Developer)**: Фізичне будівництво модулів, ліквідація дефектів, робота через FastMCP In-Memory Code Mode всередині `DNK_OS`.
   - **Gerych (Герич — Cold Knowledge Archivist)**: Тільки читання історичних логів та холодна ретроспектива (DEC-054).

---

## 2. 🔒 Зафіксовані архітектурні рішення (DEC-110 .. DEC-117)

| Рішення | Назва | Суть та статус |
| :--- | :--- | :--- |
| **DEC-110** | **Clean Foundation & Standalone Release** | Відокремлення бойового ядра `DNK_OS` від експериментального хабу `DNK_HUB`. Повна автономність без зовнішніх симлінків на код. `[🔒 LOCKED]` |
| **DEC-115** | **Apex 1.0.0 CRO Architecture & Theme Blocks 2.0** | Workhorse #1 (`services/dnk_shopify`): SaaP Dual-Ready блоки (Tinker 4.2.0 + Liquid AST), 7-gate валідація, Zero-App-Bloat. `[🔒 LOCKED]` |
| **DEC-116** | **Dynamic Client Proposal Engine** | Генератор комерційних пропозицій та клієнтський портал (`proposal_client_portal.html`) з ін'єкцією Brand DNA та матрицею цінності. `[🔒 LOCKED]` |
| **DEC-117** | **Sovereign Unified Microkernel v2.5.0** | Єдине ядро `core/kernel.py`, що нативно об'єднує 4 SOTA підсистеми: Spatial Canvas Router, Fan-In Aggregator, Quarantine Sentinel, SCONES FTS5 Memory. `[🔒 LOCKED]` |

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

### Трек 1: Shopify Apex CRO Theme (Workhorse #1)
- [ ] Завершити набір SaaP Dual-Ready v2.0 блоків у `services/dnk_shopify/theme_blocks/`:
  - `trust_badge_grid.liquid`
  - `tiered_discount_table.liquid`
  - `sticky_atc_bar.liquid`
  - `social_proof_marquee.liquid`
- [ ] Перевірити сумісність з Shopify Tinker 4.2.0 та Theme Store стандартами (`shopify theme check`).

### Трек 2: Клієнтський портал та генератор пропозицій (Client Portal)
- [ ] Доопрацювати `docs/projects/dnk_ecom/proposal_client_portal.html`:
  - Підключення реального розрахунку ROI та конверсійного сплеску.
  - Інтерактивна генерація PDF/HTML аудиту магазину клієнта.
  - Синхронізація з `brand_dna.json` та `project.manifest.yaml`.

### Трек 3: Аудит та адаптація донорських репозиторіїв
- [ ] Здійснити аудит донорських тем у `../DNKEcom/GitHub_Shopify_Themes/` за 3-етапним протоколом (Quarantine $\to$ Purge $\to$ Packaging).
- [ ] Витягти найкращі CRO UI-паттерни в бібліотеку компонентів Apex.

---

## 7. 🚀 Інструкція: Як переключити робочу сесію в `DNK_OS`

1. **В IDE Antigravity / Cursor / VS Code**:
   - Натисніть `File -> Open Folder...` (або `Cmd + O` на Mac).
   - Оберіть директорію: `/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS`.
   - (Або відкрийте `DNK_OS.code-workspace`).
2. **Перевірте наявність інструментів FastMCP**:
   - Файл `.agents/mcp_config.json` автоматично підключає сервер `dnk-core` з 17 інструментами.
   - Субагенти `dnk-builder`, `dnk-architect`, `dnk-auditor` готові до роботи в `.agents/agents/`.
3. **Перший запит у новому воркспейсі**:
   - Почніть сесію з фрази:
     > *"Продовжуємо роботу по беклогу з `docs/plans/SESSION_HANDOFF_DNK_OS_FOUNDATION.md`. Приступаємо до Треку 1 (або Треку 2)."*
   - Будь-який агент негайно підхопить зафіксований контекст без втрати пам'яті.
