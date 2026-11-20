---
title: "ШАБЛОН ІНСАЙТУ ТА ПРОДУКТОВОЇ ІДЕЇ: [Назва Ідеї]"
description: "ШАБЛОН ІНСАЙТУ ТА ПРОДУКТОВОЇ ІДЕЇ: [Назва Ідеї]"
mrh_id: "docs/architecture/research/competitors/TEMPLATE_INSIGHT.md"
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
> mrh_id: "docs/architecture/research/competitors/TEMPLATE_INSIGHT.md"
> purpose: "ШАБЛОН ІНСАЙТУ ТА ПРОДУКТОВОЇ ІДЕЇ: [Назва Ідеї]"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 💡 ШАБЛОН ІНСАЙТУ ТА ПРОДУКТОВОЇ ІДЕЇ: [Назва Ідеї]

## 📋 Метадані
---
mrh_id: "docs/research/competitors/insights/INSIGHT_XX.md"
author: "Maxim"
license: "DNK-INTERNAL"
source_type: "competitor_observation"
source_reference: "competitor_a/001-dashboard.png" # або лінк на аналіз
derivative_status: "adapted" # adapted | adopted | drop
created_at: "2026-08-11"
status: "Draft" # Draft | Under Review | Approved | Rejected
---

## 🔍 Спостереження (Observation)
* **Що ми побачили у конкурента:** [Детальний опис поведінки системи чи інтерфейсу]
* **Докази (evidence):** [Посилання на скріншот `001-[name].png` або відео]

## 🩹 Біль, що вирішується (Pain Point)
* **Яку проблему це вирішує для користувача:** [Опис болю, який конкурент намагається закрити, і наскільки успішно]

## 🚀 Продуктова ідея для DNK OS
* **Концепція реалізації:** [Як саме ми впроваджуємо це в екосистему DNK OS з урахуванням нашої специфіки]
* **Чому це краще, ніж у конкурента:** [Наша унікальна перевага, наприклад: інтеграція в Task Forest або автономні агенти]

---

## 🛡️ Zero-Regression Gate (Обов'язковий бар'єр)
*Нова ідея не приймається в DNK OS без проходження цього гейту!*

1. **Концепція Прототипу (Prototype Specification):**
   * [Опис мінімального робочого коду або скрипта, який підтверджує життєздатність ідеї]
2. **Сценарій Тестування (Test Scenario):**
   * [Кроки тестування для ручної або автоматичної перевірки, які підтверджують відсутність регресії в існуючих модулях]
3. **Обґрунтування Цінності (Value Justification / ROI):**
   * [Який бізнес-результат або економія часу/токенів досягається? Чому це варте ресурсів розробки?]

---

## 🌸 Трансляція у Flower (Тільки після затвердження "Adopt" або "Adapt")
* **Посилання на Flower Task:** `docs/tasks/Sector_XX_.../Tree_XX_.../Bush_.../Flower_XX_...md`
* **Критерії Приймання (Acceptance Criteria):**
  - [ ] [Критерій 1]
  - [ ] [Критерій 2]
* **Ризики (Risks & Mitigations):**
  - [Опис ризику] ➔ [Спосіб запобігання]
* **Метод Перевірки (Verification Method):**
  - [Як саме Maxim чи Gerych перевірять фічу перед релізом]
