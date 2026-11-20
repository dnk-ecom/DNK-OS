---
title: "ТЕХНІЧНЕ ЗАВДАННЯ: THIN-CLIENT SPECULATIVE HARNESS & CONTINUOUS SOTA SCOUT"
description: "Canonical Technical Task: Thin-Client Speculative Harness (Mac M1 8GB/256GB Governor) & Continuous SOTA Assimilation Engine"
mrh_id: "docs/tasks/active/TASK-DNK-CORE-20261117-001_THIN_HARNESS_AND_CONTINUOUS_SOTA_SCOUT.md"
status: Active
archetype: TASK_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - task
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tasks/active/TASK-DNK-CORE-20261117-001_THIN_HARNESS_AND_CONTINUOUS_SOTA_SCOUT.md"
> purpose: "Canonical Technical Task: Thin-Client Speculative Harness (Mac M1 8GB/256GB Governor) & Continuous SOTA Assimilation Engine"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🎯 ТЕХНІЧНЕ ЗАВДАННЯ: THIN-CLIENT SPECULATIVE HARNESS & CONTINUOUS SOTA SCOUT

**Дата:** 17 листопада 2026 року  
**Виконавці:** Antigravity (Архітектор) / Denchik (Master Builder)  
**Статус:** `Active` | Прив'язано до рішення `[🔒 LOCKED] DEC-137`

---

## 1. Контекст та Апаратне Обмеження (Hardware Governor Invariant)

Робоча станція Максима: **MacBook Pro M1 (8 ГБ RAM / 256 ГБ SSD)**.
- **Поточний стан:** Вільне місце на диску становить **~36 ГБ**, система активно утилізує пам'ять компресора (~3.2 ГБ у свопі).
- **Непорушне правило:** Заборонено локальне завантаження вагових коефіцієнтів моделей (GGUF, PyTorch checkpoints, Ollama daemons, Docker-контейнери понад 1 ГБ).
- **Принцип:** Асиметричний тонкий клієнт — локальний Mac виконує **виключно детермінований контроль** (< 150 МБ RAM), а весь нейроінтелект (System 1 та System 2) викликається через високошвидкісні хмарні API (Vertex AI, Gemini 2.5 Flash Lite, hosted Jev).

---

## 2. Ключові Архітектурні Пілари Реалізації

### Пілар 1: Zero-Local-Footprint System 1 Triage
- Замість локального демона `Ollaya` на 4 ГБ RAM, `core/system_one/triage.py` підключається до хмарних ендпоінтів (`Vertex AI Gemini 2.5 Flash Lite` або `TypeSafe Jev API`) із затримкою < 50 мс та вартістю $0.0001 / 1k рішень.
- 100% захист RAM та SSD від перевантаження.

### Пілар 2: Anthropic Code Mode First (DEC-036, DEC-133)
- Денчік виконує мульти-крокові задачі виключно через `execute_code_mode` (Python in-memory sandbox).
- 1 хід замість 20 послідовних викликів інструментів -> скорочення витрат токенів на 98.7%.

### Пілар 3: Автономний безперервний скаут світового фронтиру (`sota_continuous_scout.py`)
- Скрипт `scripts/system/sota_continuous_scout.py` на базі `gh search repos` регулярно сканує ключові топіки (System 1, Agent Harness, SWE-bench leaders, Code Mode, Context Compaction).
- Жодного клонування важких репозиторіїв; аналіз суворо через GitHub REST API / raw extraction.
- Автоматична генерація пульс-звітів у `docs/notes/sota_audits/` та поповнення каталогу знань.

### Пілар 4: Детермінований шлюз 100% першого проходу (Machine-as-a-Judge)
- Завдання вважається виконаним тільки за наявності машинного доказу:
  1. Синтаксична перевірка (Tree-sitter / Pyright / tsc --noEmit).
  2. Exit code 0 у `scripts/system/verify_all.sh` або юніт-тестах.
  3. Pre-commit аудит за матрицею ризиків `devagrawal09/jev-review`.
  4. При невдачі — миттєва авто-рефлексія SCONES (`query_error_solutions`) для самовиправлення до завершення ходу.

---

## 3. Критерії Прийняття (Acceptance Criteria)

1. [x] Впроваджено `scripts/system/sota_continuous_scout.py` з успішним прогоном та exit code 0.
2. [x] Згенеровано перший звіт `docs/notes/sota_audits/SOTA_FRONTIER_PULSE_2026-11-17.md`.
3. [x] Зафіксовано архітектурне рішення `DEC-137` у `docs/architecture/DECISION_REGISTRY_ADHD.md`.
4. [x] Підтверджено проходження юніт-тестів та лінтерів гігієни репозиторію.

---

## 4. Обмеження та Межі Задачі (Targeted File Whitelist & Negative Scope)

### Targeted File Whitelist Manifest
- `scripts/system/sota_continuous_scout.py`
- `docs/notes/sota_audits/SOTA_FRONTIER_PULSE_2026-11-17.md`
- `docs/architecture/DECISION_REGISTRY_ADHD.md`
- `docs/tasks/active/TASK-DNK-CORE-20261117-001_THIN_HARNESS_AND_CONTINUOUS_SOTA_SCOUT.md`

### Negative Scope / Заборони
- Заборонено локальне завантаження важких ваг (Ollama, GGUF, PyTorch checkpoints).
- Заборонено створення несанкціонованих кореневих директорій.
- Заборонено модифікацію `core/kernel.py`.
