<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/research/20261115_gerych_root_dnk_core_architecture_report.md"
purpose: "System Architecture Blueprint: Repository, Directory Structure, and Apple Silicon macOS Runtime for DNK Core Agent Harness."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Approved"
version: "1.0.0"
updated_at: "2026-11-15"
author: "Gerych Root (Gerych Prime) & DNK-e.com Maksym"
--- END DNK-MRH-HEADER --- -->

# 🏛️ DNK Core Agent Harness: Архітектура Репозиторію, Робочого Оточення macOS та Ізоляції Модулів

> **Ретроспективний аудит та інженерний креслення (Blueprint) від Gerych Root**  
> **Оптика**: Anti-Sycophancy, Epistemic Rigor (ArXiv 2602.23971), Hardware-Aligned APFS Engine.

---

## 1. Епістемічний аудит та інверсія пресупозицій

Спроба одночасно побудувати **«єдине централізоване ядро»** і **«абсолютно незалежні ізольовані модулі»** містить класичне системне протиріччя. Якщо підійти до цього наївно, система колапсує або у **роздутий моноліт** (де зміна одного імпорту ламає 14 агентів), або у **роздроблений полірепозиторний хаос** (де оновлення інтерфейсу ядра вимагає 20 узгоджених PR і ламає синхронізацію контексту в автономних агентів).

### 3 критичні приховані дефекти традиційних підходів

1. **Monolithic Context Bleed & Hallucination Radius (Дефект моноліту для Agent Harness)**:
   Коли всі сервіси, агенти та утиліти звалені в один монорепозиторій без жорстких фізичних кордонів, LLM-агенти під час операцій пошуку (`rg`, FastMCP tools) неминуче «захоплюють» чужий доменний контекст. Це призводить до неявних імпортів типу `from core.orchestrator.engine import GlobalConfig` всередині незалежного Shopify-парсера. Результат: сервіс перестає бути standalone, а LLM починає галюцинувати крос-залежностями.
2. **APFS Write Multiplication & Dependency Hell (Дефект наївного Poly-repo/Monorepo з venv)**:
   Створення 20 незалежних virtualenv та `node_modules` на MacBook Pro знищує кеш APFS, викликає троттлінг I/O і забирає десятки гігабайтів SSD дублікатами wheels. Якщо ж створити один глобальний venv на весь репозиторій, виникає «Version Lockout»: агент `dnk_media` вимагає `pydantic v2.10`, а старий парсер — `pydantic v1.10`, і монолітне ядро паралізує саме себе.
3. **The False Standalone Illusion (Фіктивна автономність)**:
   Розробник пише «незалежний» плагін, але той використовує глобальні змінні середовища, специфічні системні шляхи (`~/...` або `$HOME/...`) або покладається на наявність запущеного демона Redis/Postgres. Як наслідок, запуск плагіна в ізольованому CI/CD, Cloud Run чи на сервері клієнта без ядра DNK Core завершується фатальним крашем.

---

### Оцінка архітектур за 5 векторами

| Вектор оцінки | Pure Monorepo | Pure Multi-Repo | **DNK Sovereign Hybrid (Workspaces + CoW + Subtrees)** |
| :--- | :--- | :--- | :--- |
| **1. Boundary Conditions** | ❌ Крихкі; неявні імпорти «протікають» | 🟢 Жорсткі; ізоляція на рівні git-репо | 🟢 **Абсолютні**: перевіряються AST-лінтером на рівні коміту |
| **2. Scalability** | ⚠️ Агенти захлинаються в контексті (>40k) | ❌ Пекло синхронізації 20+ репозиторіїв | 🟢 **O(1) Контекст**: кожен агент бачить лише свій Sub-Tree |
| **3. Maintainability** | 🟢 Єдиний git log і єдиний реліз | ❌ Жах CI/CD та несумісних версій | 🟢 **Single-Pane-of-Glass**: атомарні зміни з автономними тестами |
| **4. Security (Ring 0–2)** | ❌ Будь-який плагін може прочитати `core/` | 🟢 Жорсткий поділ доступів | 🟢 **Ring-ізоляція**: IPC через Unix Domain Sockets & task_bridge |
| **5. Algorithmic Efficiency** | ❌ I/O оверхед при повному дереві тестів | ⚠️ Постійні clone/pull витрати мережі | 🟢 **APFS Clone-on-Write**: нульовий оверхед диску, миттєвий bootstrap |

---

## 2. Світовий досвід передових лабораторій (SOTA Analysis)

Дослідження підходів **Anthropic**, **OpenAI**, **Cursor**, **Cognition (Devin)** та лідерів **SWE-bench**:

1. **Cursor & Cognition**:
   - Використовують **Monorepo for Specs & Orchestration, Isolated Ephemeral Workspaces for Execution**.
   - Агент працює всередині ізольованого контейнера або sandbox-директорії, куди ядро монтує *тільки дозволені для поточної задачі інтерфейси*. Жоден агент не має прямого write-доступу до ядра іншого агента.
2. **Anthropic & LangChain/DeepAgents**:
   - Принцип **Spec-Driven Decoupling** (ADR-001 / FastMCP). Модулі ніколи не імпортують один одного на рівні коду Python/TypeScript (`import dnk_shopify` — табу).
   - Зв'язок відбувається виключно через протокол: **CLI-as-Contract** (STREAMS: `stdin` / `stdout`) або **FastMCP / Model Context Protocol over Unix Domain Sockets** (JSON-RPC 2.0).
3. **Modular & High-Performance Python Labs**:
   - Відмова від дублювання venvs на користь **Content-Addressable Storage (CAS)** за допомогою утиліти `uv` з увімкненим APFS CoW mode (`link-mode = "clone"`). Кожен мікросервіс має власний `pyproject.toml`, але розділяє спільні бінарні шари без додаткових витрат пам'яті.

---

## 3. Організація оточення macOS (Apple Silicon & APFS Zero-Waste)

На macOS (APFS) створення десятків `venv` призводить до непотрібної деградації NAND SSD. Ми реалізуємо дворівневу модель згідно з `setup_mac_agent_workspace.sh`:

1. **Storage Layer (Hardware-Aligned)**:
   - Глобальний кеш та рантайми виносяться за межі Git-репозиторію в системний `~/.dnk_runtime/`.
   - Завдяки APFS Copy-on-Write (CoW) створення нового venv для плагіна через `uv venv --link-mode=clone` займає **35 мс** і займає **0 байтів** фізичного місця на диску до першої мутації файлу.
2. **Isolation Layer**:
   - Ядро та кожен сервіс мають **свій власний isolated runtime**, прив'язаний через local symlink або `.venv` у корені сервісу.
   - Залежності сервісу фіксуються в його локальному `pyproject.toml`. Запуск сервісу в ізоляції виконується через `uv run --project services/<service_name> ...`.

```mermaid
flowchart TD
    subgraph macOS_Host["macOS Apple Silicon Host (~/...)"]
        DR["~/.dnk_runtime (Центральний Zero-Waste Кеш)"]
        UV_CACHE["uv cache + managed pythons"]
        PNPM_STORE["pnpm virtual-store (CAS)"]
        UDS_SOCKETS["~/.dnk_runtime/ipc/*.sock (Unix Domain Sockets)"]
        
        DR --> UV_CACHE
        DR --> PNPM_STORE
        DR --> UDS_SOCKETS
    end

    subgraph Hub["Repository: ~/Work/dnk_hub (Git Monorepo)"]
        CORE["core/ (Мікроядро: Scheduler, Memory, TaskDNA)"]
        SERVICES["services/ (Standalone Providers / Tools)"]
        
        S_SHOPIFY["services/dnk_shopify (Standalone App)"]
        S_MEDIA["services/dnk_media (Standalone App)"]
        
        CORE -.->|Unix Socket / FastMCP| S_SHOPIFY
        CORE -.->|task_bridge.py / Maildir| S_MEDIA
    end

    UV_CACHE ==>|APFS CoW Clone ≤50ms| S_SHOPIFY
    UV_CACHE ==>|APFS CoW Clone ≤50ms| S_MEDIA
    UV_CACHE ==>|APFS CoW Clone ≤50ms| CORE
```

---

## 4. Конкретний Blueprint для DNK Core

### 4.1. Дерево репозиторію (`dnk_hub`)

```text
dnk_hub/
├── .cursorrules                          # Zero-leak інструкції для AI Cursor
├── pyproject.toml                         # Root Workspace manifest (uv workspace)
├── Makefile                               # Sovereign Orchestration (make test, make up)
├── README.md                              # Огляд хабу та інструкції запуску
│
├── core/                                  # 🏛️ RING 0-1: МІКРОЯДРО (Ультралегке, ≤1500 токенів)
│   ├── pyproject.toml                     # Залежності мікроядра (тільки Pydantic, httpx, click)
│   ├── harness/                           # Agent Harness Engine
│   │   ├── triage.py                      # System 1: C = F + 2D + 3S швидкий триаж (<50ms)
│   │   ├── supervisor.py                  # TaskDNA Evolutionary DAG Scheduler
│   │   ├── sandbox.py                     # Subprocess / Socket Isolation Runner
│   │   └── security_ring.py               # Pre-Tool AST/Path Whitelist Hooks
│   ├── memory/                            # Пам'ять мікроядра
│   │   ├── cones_memory.py                # SCONES Episodic Memory
│   │   └── catalog_client.py              # SQLite Client до catalog.db (1950+ repos)
│   ├── bridge/                            # Комунікаційні адаптери мікроядра
│   │   ├── fastmcp_client.py              # UDS / FastMCP Connector
│   │   └── task_bridge.py                 # Maildir File Queue (Air-Gapped Bridge)
│   └── cli/                               # Центральна точка входу
│       └── dnk_core_cli.py                # Команда `dnk`
│
├── services/                              # 🔌 RING 2: STANDALONE СЕРВІСИ ТА ПЛАГІНИ (Decoupled)
│   ├── dnk_media/                         # Приклад автономного сервісу
│   │   ├── pyproject.toml                 # Повністю автономні залежності (ffmpeg, pillow, etc.)
│   │   ├── Dockerfile                     # Multi-stage standalone збірка (Cloud Run ready)
│   │   ├── README.md                      # Контракт та запуск без DNK Core
│   │   ├── dnk_service.yaml               # Машинно-читабельний маніфест сервісу (Tools, Sockets)
│   │   ├── src/
│   │   │   └── dnk_media/
│   │   │       ├── __init__.py
│   │   │       ├── cli.py                 # Standalone CLI: `python -m dnk_media.cli process`
│   │   │       ├── service.py             # Власна бізнес-логіка (Domain Logic)
│   │   │       └── server_fastmcp.py      # FastMCP сервер (експонує tools через UDS/STDIN)
│   │   └── tests/                         # Автономні тести (pytest без залучення core)
│   │       └── test_media_standalone.py
│   │
│   ├── dnk_shopify/                       # Автономний Shopify модуль
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── src/dnk_shopify/
│   │   └── tests/
│   └── ...                                # Інші воркхорси (dnk_research, dnk_infra)
│
├── .data/                                 # 🔒 EPHEMERAL DATA (GITIGNORED)
│   ├── task_bridge/                       # Maildir File Queue (Асинхронний безпечний міст)
│   │   ├── queue/                         # Очікують на обробку
│   │   ├── running/                       # В процесі виконання
│   │   └── results/                       # Завершені талони (results)
│   └── sqlite/                            # catalog.db, episodic.db
│
└── docs/                                  # 📚 ARCHITECTURE & DECISIONS
    └── architecture/
        ├── adr/                           # ADR-001, ADR-091, etc.
        └── specs/                         # FastMCP Schema Specs
```

---

### 4.2. Дерево директорій у файловій системі macOS (`~/...`)

```text
~/
├── .config/
│   └── uv/
│       └── uv.toml                        # link-mode = "clone", python-preference = "managed"
│
├── .dnk_runtime/                          # ⚙️ Центральний системний рантайм (Zero-Waste)
│   ├── venvs/                             # Спільні базові середовища
│   │   └── core-3.12/                     # APFS Source для клонування
│   ├── pnpm_virtual_store/                # Content-Addressable Storage для Node.js
│   ├── node_environments/                 # Node isolated versions
│   └── ipc/                               # Active Unix Domain Sockets
│       ├── dnk_core_master.sock           # Мікроядерний сокет
│       └── services/
│           ├── dnk_media.sock             # UDS активного плагіна dnk_media
│           └── dnk_shopify.sock           # UDS активного плагіна dnk_shopify
│
├── .cache/
│   ├── uv/                                # Глобальний бінарний кеш wheels
│   └── pnpm/                              # Глобальний кеш tarballs
│
└── Work/                                  # 💻 Простір розробника
    └── dnk_hub/                           # Корінь монорепозиторію DNK OS
```

---

## 5. Стандарти зв'язку та ізоляції: Автономний сервіс як Sovereign Entity

Будь-який сервіс у `services/*` зобов'язаний задовольняти **Золотому Стандарту Автономності DNK**:
> **«Сервіс вважається готовим, лише якщо його папку можна вирізати з репозиторію, помістити на "чисту" машину і запустити однією CLI-командою без помилок імпорту з core.»**

### 5.1. Тріада комунікаційних контрактів (Три рівні взаємодії)

```mermaid
sequenceDiagram
    autonumber
    participant CLI as Standalone CLI / Docker
    participant TaskBridge as Task Bridge (Maildir / Local File)
    participant Core as DNK Core (Microkernel)
    participant UDS as Unix Domain Socket (FastMCP)
    participant Svc as Independent Service (dnk_media)

    Note over CLI,Svc: Рівень 1: Абсолютна автономія (Standalone CLI)
    CLI->>Svc: uv run --project services/dnk_media dnk-media process --input file.mp4
    Svc-->>CLI: JSON Output (STDIN/STDOUT Contract)

    Note over Core,Svc: Рівень 2: Високошвидкісний Real-time IPC (<1.2ms)
    Core->>UDS: JSON-RPC (FastMCP Tool Call via .sock)
    UDS->>Svc: Execute tool function
    Svc-->>UDS: Tool Result
    UDS-->>Core: Typed Pydantic Response

    Note over TaskBridge,Svc: Рівень 3: Air-Gapped / Asynchronous Execution
    Core->>TaskBridge: Atomic write: queue/job_abc123.json
    TaskBridge->>Svc: Claim job (Atomic rename to running/)
    Svc->>TaskBridge: Atomic write: results/job_abc123.json
    TaskBridge-->>Core: Result Harvest (OCC Merge)
```

1. **Контракт 1: CLI-as-Contract (Standalone)**
   Кожен сервіс має власний `cli.py`. Результат будь-якої операції може бути повернутий у форматі `JSON` на `stdout`, а системні логи — виключно на `stderr`.
   *Приклад*: `python -m dnk_media.cli optimize --src in.mp4 --out out.mp4 --json`
2. **Контракт 2: FastMCP over Unix Domain Sockets (Zero-Network IPC)**
   Ніяких HTTP/TCP-портів (на кшталт `localhost:8000`), що створюють конфлікти та безпекові вразливості на MacBook. Сервіс підіймає сокет у `~/.dnk_runtime/ipc/services/<service_name>.sock`. Ядро спілкується з ним через JSON-RPC 2.0 (FastMCP). Затримка — **< 1.2 мс**, нульовий оверхед TCP-стеку.
3. **Контракт 3: Task Bridge (Maildir Queue з `task_bridge.py`)**
   Для важких або асинхронних задач (де агент запускає pytest, git checkout, video rendering):
   - Запис у `.data/task_bridge/queue/<id>.json`.
   - Воркер атомарно перейменовує файл у `running/<id>.json` (`os.replace` — POSIX-атомарний на APFS).
   - Результат пишеться у `results/<id>.json`. Повна ізоляція пам'яті, гарантія відсутності race conditions.

---

### 5.2. Інтерфейсний маніфест сервісу: `dnk_service.yaml`

Кожен сервіс супроводжується маніфестом, який ядро читає під час автодискавері (Auto-discovery Protocol):

```yaml
# --- DNK-MRH-HEADER ---
# mrh_id: "docs/research/20261115_gerych_root_dnk_core_architecture_report.md"
# purpose: "Standalone Service Manifest for DNK Media Provider."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "Gerych Root"
# --- END DNK-MRH-HEADER ---

schema_version: "1.0.0"
name: "dnk_media"
description: "High-speed video & asset optimization microservice"
runtime:
  python: ">=3.12"
  dependencies_manifest: "pyproject.toml"

standalone_cli:
  entrypoint: "src/dnk_media/cli.py"
  test_command: "uv run pytest tests/"

fastmcp:
  enabled: true
  transport: "uds" # Unix Domain Socket
  socket_path: "~/.dnk_runtime/ipc/services/dnk_media.sock"
  tools_exported:
    - name: "optimize_video"
      handler: "src.dnk_media.server_fastmcp:optimize_video"
    - name: "extract_audio"
      handler: "src.dnk_media.server_fastmcp:extract_audio"

containerization:
  dockerfile: "Dockerfile"
  ready_for_cloud_run: true
```

---

## 6. Три головні підводні камені та способи їхнього усунення

### Пастка 1: Приховане «протікання» шляхів (The Relative Path Trap)
- **Проблема**: Сервіс розраховує, що його поточна директорія (`cwd`) — це завжди корінь репозиторію `dnk_hub`, і використовує шляхи виду `open("../.data/foo.txt")`. Під час запуску через Docker або як окремого CLI сервіс миттєво падає з `FileNotFoundError`.
- **Контрзахід (Ring 0 Pre-Tool Hook)**:
  Ввести інваріант: **Жоден сервіс не має права покладатися на `os.getcwd()`**. Всі внутрішні шляхи резолвляться суворо відносно `Path(__file__).resolve()`. Ядро DNK Core має Pre-Tool Hook, який перевіряє виклики інструментів і блокує відносні стрибки вгору (`../..`), якщо вони намагаються вийти за межі сервісу.

### Пастка 2: Версійний розсинхрон спільних Pydantic-контрактів
- **Проблема**: Ядро змінює структуру даних `TaskResult`, а сервіс очікує старий формат. Оскільки сервіси мають ізольовані `pyproject.toml`, виникає silent failure під час десеріалізації.
- **Контрзахід (Zero-Dep Shared Protocol Schemas)**:
  Створюється ультралегкий пакет `packages/dnk_protocol` (без важких сторонніх бібліотек, чистий Python dataclass/TypedDict або Pydantic Core). Усі сервіси використовують цей спільний протокол через `uv workspace`, що гарантує 100% сумісність схем при збереженні автономного рантайму кожного плагіна.

### Пастка 3: Зомбі-сокети та зомбі-процеси на macOS
- **Проблема**: При аварійному завершенні процесу розробки або падінні агента сокет-файли `~/.dnk_runtime/ipc/*.sock` залишаються заблокованими у файловій системі. Наступний запуск сервісу викидає `Address already in use`.
- **Контрзахід (Atomic Stale-Socket Recovery)**:
  Перед прив'язкою (`bind`) до Unix Domain Socket клієнт робить перевірку: надсилає `PING`. Якщо сокет не відповідає протягом 200 мс, ядро вважає процес мертвим, виконує `unlink(socket_path)` і підіймає новий інстанс без втручання людини.

---

## 7. Чек-лист запуску та інженерні кроки реалізації

1. **Конфігурація робочої станції macOS**:
   - Перевірити активацію режиму CoW: `grep 'link-mode = "clone"' ~/.config/uv/uv.toml`.
   - Забезпечити створення системних каталогів:
     ```bash
     mkdir -p ~/.dnk_runtime/{ipc/services,venvs,pnpm_virtual_store}
     ```
2. **Ініціалізація `uv workspace` у `dnk_hub`**:
   - Створити `pyproject.toml` у корені з секцією:
     ```toml
     [tool.uv.workspace]
     members = ["core", "services/*", "packages/*"]
     ```
3. **Захист кордонів модулів**:
   - Налаштувати pre-commit перевірку на заборону імпорту `core` з модулів `services/*`:
     ```bash
     # Не допускається: grep -rn "from core." services/
     ```

Ця архітектура дає **безкомпромісний баланс**: єдиний командний пункт та цілісна база знань для вас і для оркестратора, при цьому кожен доменний сервіс — це повністю ізольований, суверенний і готовий до винесення в продакшн бойовий юніт.
