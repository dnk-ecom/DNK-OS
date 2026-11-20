---
title: "Skill Specification Template: {SKILL_NAME}"
description: "Canonical Skill Specification Template (SKILL_SPEC) enforcing Core-Size Ratchet (<= 750 lines) and LOD retrieval."
mrh_id: "docs/templates/agent/SKILL_SPEC_TEMPLATE.md"
status: Active
archetype: SKILL_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - dnk/templates
  - dnk/skill-spec
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/templates/agent/SKILL_SPEC_TEMPLATE.md"
> purpose: "Canonical Skill Specification Template (SKILL_SPEC) enforcing Core-Size Ratchet (<= 750 lines) and LOD retrieval."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "Antigravity & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

> ```

# 🧠 Skill Specification: {SKILL_NAME}

> [!abstract] **Паспорт Скіла (Skill Core-Size Ratchet)**
> **Максимальний розмір ядра (`SKILL.md`)**: `≤ 750 рядків`  
> **Архітектура**: Level-of-Detail (LOD). Вторинні каталоги та детальні схеми виносяться в `references/` або `scripts/`.  
> **Цільова аудиторія**: AI Swarm Agents, Agent Builders.

---

## 🎯 1. Призначення та Тригери Активації (Overview & Activation)

### Коли активувати скіл
Вкажіть точні тригери та ключові слова, при появі яких у завданні агент зобов'язаний прочитати цей скіл.

### Межі застосування
- Що вирішує цей скіл.
- Що категорично не входить у зону відповідальності цього скіла.

---

## 🛠️ 2. Необхідні Інструменти та Оточення (Prerequisites & Tools)

- **Обов'язкові інструменти**: `{e.g. view_file, run_command}`.
- **Вимоги до оточення**: Python venv (`./.venv/bin/python3`) або робочі пакети.
- **Заборонені дії**: Заборонено модифікацію зовнішніх модулів без оголошення в завданні.

---

## 🧭 3. Покроковий Алгоритм Виконання (Workflow & Instructions)

Опишіть стислий, чіткий покроковий процес:

1. **Крок 1**: Підготовча перевірка вхідних даних та конфігурації.
2. **Крок 2**: Виконання основної операції або запуску скрипта.
3. **Крок 3**: Валідація результату та отримання коду повернення.

---

## 📚 4. Рівні Деталізації та Додаткові Матеріали (LOD References)

Якщо розмір опису загрожує перевищити ліміт 750 рядків, деталі виносяться в підкаталоги:
- `references/api_reference.md` — Детальний опис складних структур та специфікацій.
- `scripts/helper_script.py` — Автоматизований утилітний скрипт для швидкого виконання.
- `examples/workflow_example.json` — Еталонний приклад робочого payload.

---

## 🏁 5. Критерії Успіху (Definition of Done)

- [ ] Всі операції виконуються без помилок (`exit code 0`).
- [ ] Кількість рядків у ядрі `SKILL.md` не перевищує 750.
- [ ] Відсутні абсолютні шляхи та сикофантичні вирази.
