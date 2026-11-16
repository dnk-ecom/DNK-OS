<!-- --- DNK-MRH-HEADER ---
mrh_id: "packages/dnk_hermes_ext/patches/README.md"
purpose: "DNK patch kit for hermes-agent v0.23 (upstream 2bd378ed): Vertex ADC, model normalize, DNK banner. Tracked copy; source of the commits is ../DNK_Vibe/hermes-agent branch feature/v0230-dnk-gcp."
canonical_source: true
alters_files: []
triggers_tasks: ["S1b"]
status: "Draft"
version: "0.1.0"
updated_at: "2026-11-06"
author: "DNK-e.com Maksym & Claude"
--- END DNK-MRH-HEADER -->

# 🛡️ DNK OS: Hermes Agent Enhancements & Adaptation Kit

Ця директорія містить повний набір архітектурних доробок, патчів та утиліт для безшовної адаптації офіційного **NousResearch/hermes-agent** під стандарти **DNK OS**.

Будь-який агент (Гєрич, Денчик, Антігравіті, Codex, Claude) або розробник може розгорнути всі доопрацювання на свіжу версію Hermes **однією командою**:

```bash
bash dnk_patches/install_dnk_enhancements.sh
```

---

## ⚡ Що вирішують наші доопрацювання (Architecture Matrix)

| Підсистема | Файл | Що було в Upstream | Що додано в DNK OS |
| :--- | :--- | :--- | :--- |
| **Google Cloud Vertex AI ADC** | `agent/vertex_adapter.py` | Жорстко очікував `GOOGLE_APPLICATION_CREDENTIALS` (файл сервісного акаунта). При роботі через gcloud auth / ADC часто падав або мав застарілий токен. | Додано SSOT-синхронізацію проекту (`_reload_dnk_active_env`), захист від протухання токена (`_TOKEN_BEARER_MAX_AGE_SEC = 3000s`) та авто-генерацію токена через `gcloud auth print-access-token`. |
| **Model Normalization** | `hermes_cli/model_normalize.py` | Передавав моделі на ендпоінт Vertex AI як `gemini-4-argon` або `gemini-3.7-flash`, що викликало помилку `HTTP 400 Malformed publisher model`. | Автоматичне префіксування `google/` для всіх моделей Gemini/Imagen на Vertex AI OpenAPI ендпоінті. Тепер можна вказувати модель як з префіксом, так і без нього. |
| **Адаптивність банера (Width Guard)** | `hermes_cli/banner.py` | Upstream друкував ASCII-логотип при ширині `>= 95`, хоча сам логотип мав 101+ символ. У спліт-панелях VS Code (80–90 колонок) графіка розсипалася на "кашу". | Жорсткий розрахунок реальної ширини рядків (`req_width + 4`) та підтримка порожнього логотипу `banner_logo: ''` для скінів. |
| **Захист від розриву слів в ASCII-арті** | `hermes_cli/banner.py` | Rich переносив рядки ASCII-малюнка по звичайних пробілах між символами. | Автоматична заміна звичайних пробілів у hero-блоці на нерозривні (`\u00a0`), що гарантує 100% збереження геометрії малюнка. |
| **Динамічна вітрина можливостей DNK OS** | `hermes_cli/banner.py` | Статичний список інструментів англійською, повідомлення "Skills toolset disabled", нуль контексту про рої агентів та MCP. | Повноцінний фірмовий банер: живий статус MCP-серверів з українськими описами, ротація корисних команд, випадкова вибірка активних інструментів, динамічне сканування 7+ агентів рою (`core/orchestrator/agents`) та вітрина навичок. |
| **Zero-Local-Env Hygiene** | `.venv` | Репозиторій міг створити важкий локальний `.venv` на 1–3 ГБ. | Автоматичне монтування симлінка `.venv -> ~/.dnk_runtime/venvs/hermes-agent` (0 байт дублікатів на диску). |

---

## 📦 Склад директорії `dnk_patches/`

```text
dnk_patches/
├── README.md                      # Цей документ (Single Source of Truth для агентів)
├── install_dnk_enhancements.sh    # Автоматичний скрипт встановлення в 1 команду
├── dnk_os_full_hermes_v0230.patch # Єдиний кумулятивний патч для v0.23.0+
├── dnk-os.yaml                    # Фірмовий скін DNK OS з адаптивним hero-логотипом
├── 0001-feat-vertex-adapt-...     # Окремий патч 1: Vertex AI ADC & Token Rotation
├── 0002-fix-cli-enforce-...       # Окремий патч 2: Banner Column Bounds & Skin Empty Logo
├── 0003-fix-banner-sanitize-...   # Окремий патч 3: ASCII Hero Whitespace Non-Breaking Guard
├── 0004-feat-banner-port-...      # Окремий патч 4: Dynamic Capabilities Showcase
└── 0005-feat-normalize-auto-...   # Окремий патч 5: Auto-prefix google/ on Vertex AI
```

---

## 🚀 Як застосовувати на нових версіях Hermes (v0.24.0+)

Коли виходить новий реліз `NousResearch/hermes-agent`:

1. Оновлюємо або викачуємо репозиторій:
   ```bash
   cd ../DNK_Vibe/hermes-agent   # відносно MY_LIFE_WORK
   git checkout -b feature/v0240-dnk-gcp
   ```

2. Запускаємо єдину команду інсталяції:
   ```bash
   bash dnk_patches/install_dnk_enhancements.sh
   ```

3. Якщо в новій версії суттєво змінилися номери рядків у файлах, скрипт автоматично спробує `git apply -3` (3-way merge). Якщо виникне конфлікт, скористайтеся описом вище для ручного внесення 3 ключових блоків:
   - `_reload_dnk_active_env` та `_TOKEN_BEARER_MAX_AGE_SEC` у `agent/vertex_adapter.py`
   - `if provider == "vertex": return f"google/{name}"` у `hermes_cli/model_normalize.py`
   - Блок `if _is_dnk:` у `hermes_cli/banner.py`

---

## 🧪 Валідація та перевірка працездатності

Після запуску переконайтеся, що всі модулі функціонують:

```bash
# 1. Перевірка нормалізації моделей
./.venv/bin/python -c "
from hermes_cli.model_normalize import normalize_model_for_provider
assert normalize_model_for_provider('gemini-4-argon', 'vertex') == 'google/gemini-4-argon'
print('Model Normalization: OK')
"

# 2. Контрольний запит через Vertex AI
./.venv/bin/python cli.py --provider vertex --model gemini-4-argon -q "Say: DNK OS Enhancements Verified" --oneshot
```


## Змінні середовища

- `DNK_AGENTS_DIR` — шлях до каталогу агентів рою для банера (наприклад `core/orchestrator/agents` у HUB). Без неї банер показує вбудований список.
