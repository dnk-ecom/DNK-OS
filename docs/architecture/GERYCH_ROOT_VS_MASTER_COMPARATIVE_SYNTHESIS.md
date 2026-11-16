# --- DNK-MRH-HEADER ---
# mrh_id: "docs/architecture/GERYCH_ROOT_VS_MASTER_COMPARATIVE_SYNTHESIS.md"
# purpose: "Comparative Synthesis of Terminal Agent Research vs Gerych-root Report on Agent Harnesses, MacBook Topology, and Sovereign DNK Core Architecture."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "Gerych (Hermes Prime) & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# ⚖️ ПОРІВНЯЛЬНИЙ СИНТЕЗ ЗВІТІВ: Як світові команди будують Agent Harnesses та як побудувати DNK Core на MacBook

## 📌 1. Доказова база та верифіковані артефакти (SHA-256)

1. **Звіт 1 (Master Report — `DNK_CORE_AGENT_HARNESS_AND_REPO_ARCHITECTURE_MASTER_REPORT.md`)**:
   - Шлях: `../DNK_HUB/docs/architecture/reports/DNK_CORE_AGENT_HARNESS_AND_REPO_ARCHITECTURE_MASTER_REPORT.md`
   - Обсяг: 424 рядки (36,695 байтів)
   - SHA-256: `f6768bc64164693837ba8a0a854d91ca03ff84876975cf0e261c788baf2b69de`
2. **Звіт 2 (Gerych-root Autonomous Report — `GERYCH_ROOT_AGENT_HARNESS_REPO_ARCHITECTURE_REPORT.md`)**:
   - Шлях: `../DNK_HUB/docs/architecture/reports/GERYCH_ROOT_AGENT_HARNESS_REPO_ARCHITECTURE_REPORT.md`
   - Обсяг: 656 рядків (68,165 байтів)
   - SHA-256: `83bbbae91f9027422dcee624ed712129c688f02e2047648908c93618bcb12d6c`
3. **Пряма ревізія коду (Live Filesystem Audit)**:
   - Ядро `DNK_OS` (`./core/kernel.py`, `./core/bricks/registry.py`, `./core/bricks/blueprint.py`, `./core/sentinel/hygiene_guard.py`, `./core/bus/agent_bus.py`)
   - Агентний рантайм `Gerych-Agent` (`../Gerych-Agent/AGENTS.md`, `../Gerych-Agent/plugins/AGENTS.md`, `../Gerych-Agent/tools/AGENTS.md`)
   - Глобальний рантайм MacBook (`~/.dnk_runtime/`, `~/.hermes/`)

---

## 🔍 2. Детальне порівняння двох звітів (Де зійшлися, а де Gerych-root знайшов глибші рішення)

| Критерій порівняння | Звіт 1 (Master Report, 424 рядки) | Звіт 2 (Gerych-root Report, 656 рядків + Live Audit) | Інженерний висновок для Максима |
| :--- | :--- | :--- | :--- |
| **1. Архітектурна парадигма ядра (DNK Core)** | Microkernel + FastMCP + Plugin Registry + SQLite WAL Event Bus. | **Zero-Framework Agentic Microkernel (<400 LOC)** + System 1 Triage ($C = F + 2D + 3S$, <50мс) + System 2 MASE ($\le 25$ дій) + **Dual-Mount Bricks** (In-RAM Python імпорт для 0мс затримки + FastMCP для зовнішніх викликів). | **Перемога підходу Gerych-root (Dual-Mount):** дозволяє уникнути оверхеду на підняття 15 окремих процесів на MacBook, зберігаючи 100% ізоляцію за маніфестом. |
| **2. Дотримання інваріанта 8 кореневих папок (`DNKHygieneGuard`)** | **Помилка в схемі:** пропонує створити 9-ту папку `plugins/` прямо в корені репозиторію (`DNK_HUB/plugins/`), що ламає `hygiene_guard.py` (`top_level_audit: FAIL`). | **100% дотримання стандарту:** суворо зберігає 8 канонічних коренів (`core/`, `services/`, `packages/`, `apps/`, `docs/`, `tests/`, `scripts/`, `infra/`). Плагіни розміщені у `packages/plugins/` (внутрішні) та `~/.hermes/plugins/` (рантайм). | Ніколи не додавати `plugins/` у корінь `DNK_OS` чи `DNK_HUB`. Використовувати `core/bricks/`, `services/` та `packages/plugins/`. |
| **3. Керування контекстом і кешем провайдера (Prompt Caching)** | Пропонує динамічно підвантажувати схеми тулів у системний промпт посеред сесії (JIT Tool Broker). | **Захист KV-Cache (`Sacred Prompt Cache`):** доводить (на базі `Gerych-Agent/AGENTS.md`), що зміна системного промпту чи базового списку тулів посеред розмови скидає кеш префікса і здорожчує запити у 5–10 разів. Використовує **Deferred Catalog (`tool_search` -> `tool_describe` -> `tool_call`)** + **In-RAM Code Mode (`execute_code`, -98.7% токенів)**. | Базовий промпт і список core-тулів мають бути **заморожені на старті сесії ($\le 6,000$ токенів)**. Нові тули та скіли приходять у повідомленнях результатів. |
| **4. Ізоляція плагінів та субагентів** | Описує загальне авто-дискавері за `manifest.yaml`. | Розкриває **Plugin Host Boundary (`plugins.isolation: host`)** через JSON-RPC протокол `plugin_host_wire.py`, ізоляцію секретів профілю (`served_profile_child_env`), macOS Seatbelt (`sandbox-exec` `*.sb`) та `Target File Whitelist` на рівні Ring-0 хука. | Коли агент або воркер ремонтує один сервіс, Ring-0 хук фізично блокує запис у будь-яку іншу папку ядра (`Negative Scope`). |
| **5. Приховані ризики гіпер-модульності (Epistemic Armor)** | Розглядає переважно переваги модульності. | Виділяє **3 критичні пастки на MacBook**: 1) IPC & Process Spawn Tax (>8 демонів з'їдають RAM); 2) Schema Version Skew (дрейф контрактів між модулями); 3) Zombie Processes & Worktree Entropy на портах `54100+`. | Впровадити **Contract Lock Gate** (`test_brick_registry.py`), **PID Sentinel** (`port_manager.py`) та **Worktree GC** (автоочищення гілок >24 год). |

---

## 🛠️ 3. Золотий Стандарт Суверенного Модуля (Як кожен сервіс, плагін і агент живе окремо і в системі)

Кожен елемент у `DNK_OS` (`core/bricks/<id>/`, `services/<name>/`, `packages/plugins/<name>/`) зобов'язаний мати **5 стандартних точок**:

1. **`brick.manifest.yaml`** — паспорт модуля (ID, версія, DAG-залежності `internal` та `external_python`/`external_npm`, точки входу, команда тестування).
2. **`contracts/schemas.py`** — єдина точка входу/виходу на Pydantic v2 (`ConfigDict(extra="forbid", frozen=True)`). Ядро та сусідні модулі імпортують **тільки** `contracts/schemas.py`, ніколи не імпортуючи внутрішню папку `src/` чи `engine/`.
3. **`cli.py` (Standalone Mode)** — дозволяє запустити, протестувати й налагодити модуль у терміналі однією командою (`uv run python -m services.dnk_shopify.cli --self-test`) **повністю окремо від ядра DNK Core**.
4. **`mcp_server.py` (Orchestrated Mode)** — FastMCP-обгортка над тією самою функцією, яку викликає ядро `DNK Core`, `Gerych-Agent` або веб-кокпіт.
5. **`tests/` (Isolated Quality & Improvement Loop)** — герметичні тести з локальними фікстурами, які проходять за 1–3 секунди і дозволяють агенту вдосконалювати модуль ізольовано у виділеному `git worktree` (`~/.dnk_runtime/worktrees/<task>`).
