---
title: "COMPETITOR_MATRIX.md: Порівняльна Матриця Конкурентів DNK OS"
description: "COMPETITOR_MATRIX.md: Порівняльна Матриця Конкурентів DNK OS"
mrh_id: "docs/architecture/research/competitors/COMPETITOR_MATRIX.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/research/competitors/COMPETITOR_MATRIX.md"
> purpose: "COMPETITOR_MATRIX.md: Порівняльна Матриця Конкурентів DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📊 COMPETITOR_MATRIX.md: Порівняльна Матриця Конкурентів DNK OS

Цей документ містить глобальне порівняння архітектурних та продуктових можливостей DNK OS з ключовими конкурентами на ринку автономних агентських систем.

## 🎯 Глобальна Порівняльна Таблиця

| Критерій оцінювання | Competitor A (напр., CrewAI Ent.) | Competitor B (напр., Langflow) | DNK OS Opportunity (Наша Перевага) |
| :--- | :--- | :--- | :--- |
| **Agent visibility** (Видимість роботи агентів) | **Сильна** (детальні трейси логів виконання) | **Слабка** (візуальні граф-ноди без таймлайну) | **Єдина timeline-модель** (інтегрована в UI хронологія дій усіх субагентів) |
| **Human approval** (Гейти затвердження людиною) | **Часткова** (прості консольні переривання) | **Відсутня** (повністю автономний запуск без пауз) | **Supervisor approval gates** (роль-оркестратор `herich_librarian` блокує чутливі операції) |
| **Task decomposition** (Декомпозиція завдань) | **Немає** (лінійне виконання або прості списки) | **Є вручну** (користувач сам будує DAG-граф завдань) | **Автоматичне Task Forest** (агенти самі будують ієрархію Sector/Tree/Bush/Flower) |
| **Integrations** (Інтеграції) | **Shopify** (лише e-commerce конектори) | **API-first** (загальні REST конектори) | **Shopify + ERPNext + GitHub** (глибокі нативні конектори для повної автоматизації бізнесу) |
| **Audit trail** (Аудит-слід та безпека) | **Обмежений** (прості stdout логи) | **Добрий** (збереження конфігурацій графів) | **Immutable execution log** (незмінний лог виконання з криптографічним аудитом) |

---

## 🛠️ Інструкція з Оновлення Матриці
1. Критерії в цій таблиці є **єдиними та незмінними** для всіх аналізів конкурентів.
2. При додаванні нового конкурента в екосистему, обов'язково оновлюйте відповідні колонки або додавайте нові рядки/колонки для порівняння.
3. Кожне твердження в таблиці повинно мати доказ у відповідному аналізі конкурента (посилання на `screen_id` та `assets/screenshots/`).
