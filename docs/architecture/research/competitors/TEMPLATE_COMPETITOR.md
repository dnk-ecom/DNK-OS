---
title: "ШАБЛОН АНАЛІЗУ КОНКУРЕНТІВ: [Назва Конкурента]"
description: "ШАБЛОН АНАЛІЗУ КОНКУРЕНТІВ: [Назва Конкурента]"
mrh_id: "docs/architecture/research/competitors/TEMPLATE_COMPETITOR.md"
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
> mrh_id: "docs/architecture/research/competitors/TEMPLATE_COMPETITOR.md"
> purpose: "ШАБЛОН АНАЛІЗУ КОНКУРЕНТІВ: [Назва Конкурента]"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔍 ШАБЛОН АНАЛІЗУ КОНКУРЕНТІВ: [Назва Конкурента]

## 📊 Загальна Інформація
* **Сайт:** [URL]
* **Джерело (source_url):** [URL на джерело інформації/документацію]
* **Дата захоплення (captured_at):** [YYYY-MM-DD]
* **Рівень впевненості (confidence):** [Low | Medium | High] (Чому саме так?)

---

## 🔬 Докази та Скріншоти (Evidence)
*Правило іменування скріншотів: `<flow-number>-<screen-name>.png` (наприклад, `001-dashboard.png`)*

### [Screen ID: screen_001]
* **Файл:** `assets/screenshots/001-[screen-name].png`
* **Опис доказу (evidence):** [Що саме зафіксовано на скріншоті, яка функціональність]
* **Джерело / URL:** [Додаткове посилання на конкретну сторінку]

---

## 🎯 Слабкі Місця & Біль Користувачів (Pain Points)
*(Аналіз відгуків та відкритих джерел)*
1. **[Біль 1]:** [Опис проблеми]

---

## 🎨 Візуальний Аналіз (Excalidraw Map)
* **Схема Excalidraw:** `[Дивитись схему](./assets/diagrams/[competitor_name]-user-flow.excalidraw)`
  *(Кожен вузол у схемі має посилатися на відповідний `screen_id`)*

---

## ⚖️ Рішення щодо адаптації (Decision / Actionability)
*Оберіть статус рішення: **Adopt** (повне впровадження як є) | **Adapt** (модифікація під архітектуру DNK OS) | **Drop** (відхилено через невідповідність критеріям цінності)*

### [Рішення 1]: [Назва ідеї]
* **Статус:** [Adopt | Adapt | Drop]
* **Обґрунтування (decision):** [Чому саме це рішення, у чому цінність для DNK OS]
* **Зв'язок з Insight:** Посилання на `INSIGHT_XX.md`
