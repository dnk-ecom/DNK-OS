# --- DNK-MRH-HEADER ---
# mrh_id: "_Shopify_Theme_DEV_Workflow/01_AUTONOMOUS_HERYCH_TASK_TEMPLATE.md"
# purpose: "Standardized Task Specification Template for Hermes Agent Gerych to Audit Any Donor Branch"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-10"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# 🤖 Бойове технічне завдання для Gerych23: Автономний аудит гілки-донора

Цей документ містить готовий канонічний шаблон завдання для запуску агента **Gerych23 (DNK OS Gerych Core v0.23.0 на Python 3.14, модель `gemini-4-argon`)** для аудиту, перевірки Cleanroom-статусу, молекулярної дистиляції та графтингу **будь-якої гілки-донора** з канонічного репозиторію:
- **GitHub**: [`https://github.com/DNKShopify/DNK-e.com/tree/[BRANCH]`](https://github.com/DNKShopify/DNK-e.com)
- **Локальний воркплейс**: `DNK-Ecom_git_mirrow/[BRANCH]/`

---

## 📋 Формуляр запуску завдання (Копіювати для запуску Gerych23)

```markdown
# ЗАВДАННЯ ДЛЯ GERYCH23: Молекулярний аудит, Cleanroom-паспорт та дистиляція гілки [BRANCH]

## 1. Ціль місії
1. Провести вичерпний інженерний аудит гілки-донора `[BRANCH]` у дзеркалі `DNK-Ecom_git_mirrow/[BRANCH]`.
2. Перевірити та підтвердити 100% Cleanroom-статус (відсутність DRM-перевірок, ліцензійних скриптів, зовнішніх трекерів).
3. Скласти або актуалізувати Архітектурний паспорт та Картку швидкого графтингу (`README.md` у самій гілці) з переліком Топ-8 Золотих Молекул.
4. Дистилювати унікальні атоми/молекули/двигуни в `distilled_vault/[BRANCH]/`.
5. Оновити Центральний Геном-Реєстр (`03_SELF_IMPROVING_GENOME_REGISTRY.md`) та Порівняльну Матрицю.

## 2. Білий список файлів (Target Whitelist)
- `DNK-Ecom_git_mirrow/[BRANCH]/README.md` (Архітектурний паспорт донора)
- `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/reports/AUDIT_[BRANCH].md`
- `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/reports/AUDIT_[BRANCH].json`
- `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/distilled_vault/[BRANCH]/`
- `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/03_SELF_IMPROVING_GENOME_REGISTRY.md`
- `Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/04_BENCHMARK_AND_COMPARISON_MATRIX.md`

## 3. Негативний скоуп (Negative Scope — СУВОРО ЗАБОРОНЕНО)
- Заборонено вносити недеструктивні або експериментальні зміни в Liquid-код самої гілки без фіксації в Cleanroom-звіті.
- Заборонено залишати активні виклики сторонніх трекерів (FB, TikTok, GA, Klaviyo) у дистильованих компонентах.
- Заборонено пропускати крок оновлення Геном-Реєстру: кожна сесія має збагачувати знання про створення DNK Ecom.

## 4. Дозволені інструменти (Sanctioned Tools)
- CLI утиліти сервісу: `python3 tools/theme_auditor.py`, `python3 tools/distill_molecules.py`, `python3 tools/benchmark_matrix.py`.
- Скрипт графтингу ядра: `python3 ../../../DNK_HUB/scripts/shopify/deconstruct_donors.py graft`.
- Bash та Git утиліти: `git status`, `git log`, `grep`, `wc`, `find`.

## 5. Покроковий план дій Gerych23 (5 обов'язкових кроків)

### Крок 1: Запуск автоматичного аудитора тем
```bash
python3 tools/theme_auditor.py \
  --theme-path "../../../DNK-Ecom_git_mirrow/[BRANCH]" \
  --output "reports/AUDIT_[BRANCH].json" \
  --markdown "reports/AUDIT_[BRANCH].md"
```
Зафіксувати показники: Maturity Score, кількість блоків у `blocks/`, співвідношення секцій, ліміт 512 KB для JSON-шаблонів.

### Крок 2: Верифікація Cleanroom-нейтралізації
- Перевірити `layout/theme.liquid`, `snippets/` та `assets/` на наявність:
  - ECDSA/Watchdog скриптів блокування вітрини;
  - Повноекранних блокувальних оверлеїв або перевірок токенів;
  - Трекінг-пікселів (`fbq`, `gtag`, `ttq`).
- Якщо знайдено залишки сторонніх перевірок — знешкодити їх та задокументувати у звіті.

### Крок 3: Молекулярна дистиляція у Vault
```bash
python3 tools/distill_molecules.py \
  --theme-path "../../../DNK-Ecom_git_mirrow/[BRANCH]" \
  --vault-path "distilled_vault/[BRANCH]"
```
Компоненти розкладаються по папках: `atoms/`, `molecules/`, `organisms/`, `engines/` із генерацією маніфесту.

### Крок 4: Складання Картки Графтингу в гілці донора
Перевірити наявність та наповнити `DNK-Ecom_git_mirrow/[BRANCH]/README.md` за стандартом:
- Архетип донора;
- Статистика файлів та зв'язності;
- Таблиця Топ-8 Золотих Молекул із готовими командами графтингу:
  `python3 scripts/shopify/deconstruct_donors.py graft --donor donor/[BRANCH] --file blocks/[FILE].liquid`

### Крок 5: Оновлення Геном-Реєстру та Матриці
- Внести нову картку в `03_SELF_IMPROVING_GENOME_REGISTRY.md` із прямим посиланням на гілку `https://github.com/DNKShopify/DNK-e.com/tree/[BRANCH]`.
- Перегенерувати матрицю: `python3 tools/benchmark_matrix.py`.

## 6. Критерії приймання завдання (Acceptance Gate)
- Exit code 0 для всіх скриптів.
- Наявність звітів `AUDIT_[BRANCH].md` та `AUDIT_[BRANCH].json`.
- Чистий маніфест дистиляції `distilled_vault/[BRANCH]/DISTILLATION_MANIFEST.json`.
- Зареєстрований запис у Геном-Реєстрі.
```

---

## 💡 Приклади швидкого запуску Gerych23 через `gerych4` (`google/gemini-4-argon`):

> [!TIP]
> Gerych23 працює на найновішому ядрі **DNK OS Gerych Core v0.23.0** (`DNK_Vibe/hermes-agent`, Python 3.14).
> Команда `gerych4` (або `gerych-argon`) в `~/.zshrc` автоматично підключає Vertex AI з моделлю **`google/gemini-4-argon`**.

```bash
# 1. Аудит та дистиляція гілки casaio (еталон L5 Atomic Gold):
gerych4 --query "Виконай аудит гілки casaio за інструкцією /Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/01_AUTONOMOUS_HERYCH_TASK_TEMPLATE.md" --oneshot

# 2. Аудит та дистиляція гілки ella (мега-маркет):
gerych4 --query "Виконай аудит гілки ella за інструкцією /Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/01_AUTONOMOUS_HERYCH_TASK_TEMPLATE.md" --oneshot

# 3. Аудит та дистиляція гілки shrine-pro (DTC комбайн):
gerych4 --query "Виконай аудит гілки shrine-pro за інструкцією /Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/01_AUTONOMOUS_HERYCH_TASK_TEMPLATE.md" --oneshot

# 4. Аудит та дистиляція гілки sugar (Theme Blocks 2.0 & No-App комбайн):
gerych4 --query "Виконай аудит гілки sugar за інструкцією /Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/01_AUTONOMOUS_HERYCH_TASK_TEMPLATE.md" --oneshot
```
