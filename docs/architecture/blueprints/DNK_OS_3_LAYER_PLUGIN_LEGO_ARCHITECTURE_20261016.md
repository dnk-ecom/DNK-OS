---
title: "DNK OS: 3-Рівнева Агентивна Архітектура (`[🔒 LOCKED] DEC-105`)"
description: "Canonical Obsidian Architecture Blueprint recording Maxim"
mrh_id: "docs/architecture/blueprints/DNK_OS_3_LAYER_PLUGIN_LEGO_ARCHITECTURE_20261016.md"
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
> mrh_id: "docs/architecture/blueprints/DNK_OS_3_LAYER_PLUGIN_LEGO_ARCHITECTURE_20261016.md"
> purpose: "Canonical Obsidian Architecture Blueprint recording Maxim"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ DNK OS: 3-Рівнева Агентивна Архітектура (`[🔒 LOCKED] DEC-105`)

Пов'язані нотатки: [[011_DNK_OS_AGENTIC_HARNESS_ARCHITECTURE]] | [[013_SOTA_SKILLS_AND_THOUGHT_DAG_ENGINE]] | [[000_INDEX_DASHBOARD]]

---

## 🎯 1. Формулювання Засновника (Максим — Vibe-Coder Blueprint)

1. **Ядро та Агентивний Харнес (Mind-Map Ноди)**:
   > *«Будуємо ядро — в самому ядрі є агентивний харнес, який допомагає опрацьовувати звернення Мена-Вайбкодера і структурувати їх на спеціалізовані задачі та чати у вигляді нод - майнд карт і на основі цих нод - задач підбирати потрібних агентів та навички та інші технічні фішки для виконання?»*
2. **Сервіси як Плагіни та Агенти як Кубики Лего (Закон Ізоляції Компетенцій Оркестратора)**:
   > *«Як побудувати правильно технологічно зрілу та сучасну команду агентів, яка буде працювати з ядром так, щоб ми будували Сервіси як плагіни, а в сервісах агенти були як кубики лего, завдяки яким виконуються задачі, але важливо щоб системний (оркестратор Ядра) не виконував задачі, які не є в його компетенції, а делегував підключеним сервісам та їх агентам?»*
3. **Автономний Сервіс Пошуку та Асиміляції (GitHub + Бібліотека ➔ Специфікації)**:
   > *«Як правильно інтегрувати сервіси які ми додали в бібліотеку або знайшли в github.com щоб розбудовувати та покращувати DNK OS, чи має оркестратор підключати потрібний сервіс пошуку та асиміляції щоб опрацьовувати та створювати правильні задачі та специфікації, отримавши задачі та мої ідеї у вигляді людської мови?»*

---

## 🧠 2. Детальна Технічна Відповідь та Архітектурний Синтез

Спираючись на 195 SOTA-документів нашої бази, 1,997 репозиторіїв у `catalog.db` та синтез 12 світових лідерів (`obra/superpowers`, `addyosmani/agent-skills`, `mattpocock/skills`, `affaan-m/ECC`, `chenxiachan/thoughtdag`, `ximing/tributary`, `winlp4ever/canvas-harness`):

### Рівень 1: Ядро та Агентивний Харнес (`core/kernel.py` + `thought_companion.py`)
* **Вхід**: Ідея людською мовою від Вайбкодера.
* **Socratic & Doubt-Driven Gate**: Якщо впевненість <95%, `FirstThoughtCompanionAgent` ставить 1–2 точкові питання та проганяє ідею через **Epistemic Armor** (3 приховані ризики, граничні умови, скептична альтернатива).
* **Транспіляція у Mind-Map (`ThoughtDAGGraph`)**:
  * Ідея перетворюється на ациклічний граф (`PROJECT` ➔ `HYPOTHESIS` ➔ `TASK` ➔ `SYNTHESIS`), розкладений алгоритмом `TributaryLayoutEngine`.
  * Кожна нода отримує лише хешований контекст батьківських нод (`upstream_fingerprint`), а при зміні верхньої ноди `propagate_staleness_bfs` підсвічує залежні ноди як `stale`.
  * До кожної ноди прикріплюється **Паспорт Виконання**: `Role Capsule`, `LOD Skills`, `Target Files Lock` та розрахунок `BlastRadiusAnalyzer`.

### Рівень 2: Сервіси як Плагіни (`ServicePluginRegistry`) та Агенти як Кубики Лего (`LegoAgentPipeline`)
* **Закон Ізоляції Оркестратора (`OrchestratorCompetenceGuard`)**: Оркестратор Ядра (`dnk_companion_architect`) фізично заблокований від прямих мутацій продуктового коду (`apps/`, `services/`). При спробі прямої мутації спрацьовує детермінований бар'єр `direct_execution_allowed=False` з обов'язковим делегуванням у відповідний Сервіс-Плагін.
* **Сервіс = Плагін (`ServicePluginManifest`)**: Кожен сервіс (`dnk_sota_assimilation_plugin`, `dnk_shopify_plugin`, `dnk_media_studio_plugin`, `dnk_code_fullstack_plugin`) реєструється в Ядрі зі своїм доменом, списком дозволених директорій (`allowed_directories`) та внутрішнім набором Лего-кубиків.
* **Агент = Кубик Лего (`LegoAgentBrick`)**: Кожен кубик загорнутий у жорстку капсулу (`<= 8` інструментів, `<= 6,000` токенів контексту) і збирається у конвеєр:
  1. `[Brick 1: SOTA Scout & Spec]` — підтягує патерни з бібліотеки та формує специфікацію.
  2. `[Brick 2: Tracer-Bullet Builder]` — виконує атомарний вертикальний зріз у межах `target_files_lock`.
  3. `[Brick 3: 4-Axis Doubt Auditor]` — перевіряє результат за 4 критеріями (`addyosmani/agent-skills`: Spec Compliance, Code & Type Quality, Security & Blast Radius, Simplicity) та блокує відмовки через `ADDY_OSMANI_ANTI_RATIONALIZATION_TABLE`.

### Рівень 3: Автономний Сервіс Пошуку та Асиміляції (`SOTAAssimilationBridge`)
* Коли надходить ідея людською мовою, першим кроком запускається `SOTAAssimilationBridge.synthesize_spec_from_idea(human_idea, domain)`.
* **Локальний контур**: Пошук у `catalog.db` (1,997 репозиторіїв) та графі знань `K-Plex Smart Linker`.
* **Зовнішній контур (GitHub Two-Track License Gate)**:
  * **Track 1 (MIT / Apache 2.0 / BSD)**: Пряма екстракція AST-структур і патернів.
  * **Track 2 (GPL / AGPL)**: Clean-Room Reverse Engineering (синтез чистої специфікації без копіювання чужого коду).
* На виході формується `SOTAAssimilationSpecPayload` із критеріями приймання та SHA-256 відбитком специфікації.

---

## 🛠️ 3. Фізична Реалізація у `DNK_OS_APP`

* **Модуль**: `core/orchestrator/service_plugin_registry.py`
* **API Ендпоінти**:
  * `GET /api/v1/orchestrator/plugins` — реєстр усіх підключених Сервіс-Плагінів, їхніх Лего-кубиків та правил Anti-Rationalization.
  * `POST /api/v1/orchestrator/plugins/execute` — повний цикл обробки ноди: перевірка компетенції Оркестратора ➔ SOTA Assimilation Spec ➔ конвеєр Лего-кубиків ➔ 4-Reviewer Doubt Gate.
* **Тести**: `tests/unit/test_service_plugin_lego_pipeline.py`
