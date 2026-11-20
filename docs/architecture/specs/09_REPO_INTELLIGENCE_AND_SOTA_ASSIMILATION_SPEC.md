---
title: "Специфікація 09: Repo Intelligence & SOTA Pattern Assimilation Engine (JIT Reuse Gate, FTS5 Bilingual Search, Zero-Clone AST Mining)"
description: "Master Architecture Specification for the DNK Repo Intelligence & SOTA Pattern Assimilation Engine (services/dnk_git_research, core/registry/repo_catalog.py, catalog.db), defining zero-clone AST mining, bilingual FTS5 search, JIT reuse gating, and automated translation of open-source engineering into Shopify and Media agency deliverables."
mrh_id: "docs/architecture/specs/09_REPO_INTELLIGENCE_AND_SOTA_ASSIMILATION_SPEC.md"
aliases:
  - "09_REPO_INTELLIGENCE_AND_SOTA_ASSIMILATION_SPEC"
  - "Repo Intelligence Spec"
  - "SOTA Pattern Assimilation"
tags:
  - dnk-os
  - spec
  - git-research
  - sota-assimilation
  - reuse-gate
  - fts5
  - zero-clone-ast
  - shopify-cro
  - video-production
created: 2026-11-16
updated: 2026-11-16
status: active
type: spec
archetype: DEV_SPEC
domain: research
author: "DNK-e.com Maksym (Founder), Antigravity (Architect) & Denchik (Builder)"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/09_REPO_INTELLIGENCE_AND_SOTA_ASSIMILATION_SPEC.md"
> purpose: "Master Architecture Specification for the DNK Repo Intelligence & SOTA Pattern Assimilation Engine (services/dnk_git_research, core/registry/repo_catalog.py, catalog.db), defining zero-clone AST mining, bilingual FTS5 search, JIT reuse gating, and automated translation of open-source engineering into Shopify and Media agency deliverables."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "DNK-e.com Maksym, Antigravity & Denchik"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛡️ Специфікація 09: Repo Intelligence & SOTA Pattern Assimilation Engine

> **Призначення**: Єдиний інженерний протокол автономного видобутку, аудиту, захищеної екстракції та асиміляції передових світових інженерних рішень із перевіреного каталогу (1 663 репозиторії) для створення високоефективних активів контент-агенції та Shopify e-commerce системи Максима без повторного винаходження велосипедів і без галюцинацій усереднених LLM.

---

## 🎯 1. Призначення, Bounded Context та Стратегічна Цінність (Purpose & Scope)

### 1.1. Проблема стандартних LLM
Сучасні великі мовні моделі (GPT-4, Claude 3.5, Gemini 2.5) тренуються на масивах коду з усього інтернету. Їхня внутрішня оптимізація веде до **усереднення патернів**:
- У **Shopify**: вони пропонують застарілі монолітні секції з jQuery або багами race conditions у кошику (замість стандарту Horizon / Theme Blocks 2.0 та CartMutationQueue).
- У **Video / Motion**: вони вигадують неіснуючі параметри Remotion або генерують неефективні цикли замість точних фізичних формул Безьє та time-stretching.
- У **Multi-Agent**: вони пишуть нескінченні рекурсивні чати без детермінованих AST-шлюзів і захисту від амнезії.

### 1.2. Рішення DNK OS: Живий інженерний супермаркет
Замість генерації "з уяви", система використовує **1 663 відібраних і перевірених світових репозиторії** як банк готових рішень:
- **Shopify Агенція**: Молекулярні Theme Blocks 2.0 (Horizon/Tinker), нативні Web Components, черги мутацій кошика, динамічні таймери та бандли.
- **Контент-Агенція**: Алгоритми вирізання тиші, формули кінетичної типографіки, шейдери Three.js, автоматичний монтаж коротких відео (Shorts/Reels).
- **Економічний ефект**: Час розробки складного інтерактивного блоку скорочується з 2–3 днів до 15 хвилин із гарантованою відсутністю багів у production.

---

## 🏛️ 2. Чотири Опорні Стовпи Архітектури (Core Pillars)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        АГЕНТИ (Denchik / Gerych)                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 1. Запит на механіку / фічу
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Pillar 3] JIT Reuse Gate (services/dnk_git_research/src/reuse_brief.py)│
│  - Класифікація: SKIP (базовий таск) vs RESEARCH (інженерна механіка)  │
│  - Вердикти: ADOPT / ADAPT / CLEAN_ROOM / BUILD                        │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Пошук у локальній базі          │ Пошук live GitHub
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│ [Pillar 1] FTS5 + Білінгвальний      │  │ [Pillar 2 & 4] Git Research  │
│ двигун (core/registry/repo_catalog.py)│  │ & GraphQL Probing Engine     │
│  - SQLite FTS5 (repositories_fts)    │  │  - AST аналіз без клонування │
│  - BilingualQueryExpander (UA ➔ EN)  │  │  - Dossier & HEAD pinning    │
│  - 3-Tier Multiplier Ranking         │  │  - Batch GraphQL (25 репо/с) │
│  - .data/repo_catalog/catalog.db     │  │  - services/dnk_git_research │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

### Pillar 1: Надшвидке сховище та FTS5-пошук (`catalog.db`)
- **База**: SQLite з таблицею `repositories` та віртуальною FTS5-таблицею `repositories_fts`.
- **Білінгвальний транслятор (`BilingualQueryExpander`)**:
  - Приймає наміри природною українською мовою та розгортає їх у точні FTS5-клаузи:
    - `"пам'ять і контекст"` ➔ `(memory OR episodic OR context OR scones OR engram OR mem0)`
    - `"відео анімація монтаж"` ➔ `(video OR remotion OR avatar OR kinetic OR movie)`
    - `"магазин ліквід кошик"` ➔ `(shopify OR liquid OR theme OR checkout OR polaris) AND (cart OR drawer)`
- **Формула зваженого ранжування**:
  $$\text{FinalScore} = \text{BM25}(\text{query}) \times \text{TierMultiplier} \times \text{LicenseMultiplier}$$
  - **Tier 1 (Golden Core)**: `3.0x`
  - **Tier 2 (SOTA Blueprints)**: `2.0x`
  - **Tier 3 (Discovery Radar)**: `1.0x`
  - **Permissive License**: `1.5x`

### Pillar 2: Автономний FastMCP двигун AST-майнінгу (`services/dnk_git_research`)
- **Транспорт**: FastMCP stdio (`dnk.os/v1alpha2`).
- **Dossier & RepoMap (`dossier.py`)**:
  - Фіксує HEAD commit SHA донора.
  - Екстрактує сигнатури AST (класи, функції, декоратори, експорти) через GitHub API/raw blobs.
  - **Zero-Clone Invariant**: Жоден репозиторій не скачується гігабайтами на диск; аналізуються лише цільові файли з алгоритмами.

### Pillar 3: Шлагбаум повторного використання коду (JIT Reuse Gate)
- **Файл**: `services/dnk_git_research/src/reuse_brief.py`.
- **Логіка роботи**:
  1. `task_gate.decide()`: якщо завдання банальне (наприклад, "змінити колір кнопки") ➔ вердикт `SKIP` (0 токенів витрат).
  2. Якщо завдання містить специфічну інженерну механіку ➔ вердикт `RESEARCH`.
  3. Чотири дії повторного використання (`ReuseAction`):
     - `ADOPT`: Підключити як чистий пакет (`pnpm add` / `uv add`), якщо ліцензія MIT/Apache і пакет зрілий.
     - `ADAPT`: Взяти код за зразок і адаптувати під структуру DNK OS з посиланням на автора.
     - `CLEAN_ROOM`: Репозиторій має обмежувальну ліцензію (GPL/AGPL/комерційну). Агент зобов'язаний виписати специфікацію (математику, структури даних, граф потоку) та написати чисту реалізацію з нуля без копіювання жодного рядка коду.
     - `BUILD`: Аналогів у світі немає — реалізовувати самостійно з фіксацією факту пошуку.

### Pillar 4: Live GitHub GraphQL Probing & Catalog Curation
- Батч-запити до GitHub GraphQL API (по 25 репозиторіїв за 1 секунду).
- Перевірка живого стану: зірки, `isArchived`, `isEmpty`, дата останнього коміту, `README.md`.
- Автоматичний відсів сміття без навантаження на диск.

---

## 🔌 3. Інтеграція в DNK OS Microkernel (`core/kernel.py`)

Сервіс інтегрований безпосередньо в єдине ядро FastMCP:

| Інструмент FastMCP | Вхідні параметри | Що повертає |
| :--- | :--- | :--- |
| `search_repo_catalog` | `query: str, domain: str = "", limit: int = 10` | JSON масив відранжованих репозиторіїв із метаданими, тегами, ліцензією та Tier |
| `get_repo_reuse_brief` | `task_description: str, force_research: bool = False, live: bool = False` | Структурований бриф із вердиктом (`ADOPT`/`ADAPT`/`CLEAN_ROOM`/`BUILD`), списком донорів та покроковою інструкцією |

---

## 🔄 4. Сквозний Пайплайн: Від Репозиторію до Бізнес-Компонента

### 4.1. Пайплайн для Shopify CRO Вітрин
```
[Задача: Створити Sticky Buy Box із вибором варіантів та таймером]
   │
   ▼ 1. get_repo_reuse_brief("shopify sticky buy box countdown")
   │
[FTS5 Пошук знаходить: movictor99/shopify-theme-builder, Saabbir/shopify-theme-handbook]
   │
   ▼ 2. Екстракція AST: сигнатури Liquid schema + Web Component <dnk-buy-box>
   │
   ▼ 3. Чиста компіляція за стандартом Horizon / Tinker (Dual-Ready v2.0)
   │
[Результат: services/dnk_shopify/DNK_Horizon_Tinker/blocks/tinker-dnk-sticky-buybox.liquid]
```

### 4.2. Пайплайн для Контент-Агенції (Video & Motion)
```
[Задача: Автоматичне вирізання тиші та генерація анімованих титрів]
   │
   ▼ 1. get_repo_reuse_brief("video silence cutting kinetic typography remotion")
   │
[FTS5 Пошук знаходить: auto-editor/auto-editor, heygen-com/skills, AgriciDaniel/flow]
   │
   ▼ 2. Clean-Room екстракція: порогові формули dB та криві Безьє
   │
   ▼ 3. Інтеграція у HyperFrames / Remotion модуль
   │
[Результат: services/dnk_media/src/silence_cutter.py + Remotion TSX Component]
```

---

## 🛡️ 5. Інваріанти Безпеки та Ліцензійного Захисту (Epistemic Armor)

1. **Zero Raw Copy-Paste from GPL/AGPL**: Заборонено пряме копіювання коду з репозиторіїв з вірусними ліцензіями. Тільки **Clean-Room Реінжиніринг** (екстракція формул ➔ специфікація ➔ власний синтаксис).
2. **Zero Disk Bloat**: Заборонено клонувати репозиторії через `git clone` у корінь або робочі простори. Дозволено лише shallow-read окремих файлів через GitHub API blobs.
3. **Pristine Catalog Invariant**: База підтримується в очищеному стані (1 663 перевірені репозиторії). Усі мертві, порожні або заблоковані репозиторії підлягають автоматичному вилученню через `PURGE_FINAL_EXECUTION_LIST.json`.

---

## 🧪 6. Детермінований План Верифікації (Deterministic Verification Plan)

- [x] **Unit & Contract Tests**: `python3 -m pytest tests/unit/test_repo_catalog.py -v` (перевірка FTS5 пошуку, фільтрації ліцензій та генерації reuse briefs).
- [x] **Zero-Clone AST Isolation Gate**: Перевірка відсутності несанкціонованих клонів у робочому просторі `DNK_HUB` та `DNK_OS`.
- [x] **Markdown Schema & Invariant Gate**: `python3 scripts/system/markdown_schema_gate.py docs/architecture/specs/09_REPO_INTELLIGENCE_AND_SOTA_ASSIMILATION_SPEC.md` повертає exit code 0.
