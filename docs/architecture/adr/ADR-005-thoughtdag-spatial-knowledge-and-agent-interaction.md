---
title: "ADR-005: Інтеграція ThoughtDAG та просторово-агентивної взаємодії (Spatial Agent Interaction)"
description: "Architecture Decision Record: Assimilation of ThoughtDAG and Spatial Agent-User Interaction."
mrh_id: "docs/architecture/adr/ADR-005-thoughtdag-spatial-knowledge-and-agent-interaction.md"
status: Active
archetype: ADR
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - adr
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/adr/ADR-005-thoughtdag-spatial-knowledge-and-agent-interaction.md"
> purpose: "Architecture Decision Record: Assimilation of ThoughtDAG and Spatial Agent-User Interaction."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

> [!abstract] 🏛️ АРХІТЕКТУРНЕ РІШЕННЯ: THOUGHTDAG ТА ПРОСТОРОВО-АГЕНТИВНА ВЗАЄМОДІЯ
> Прийнято рішення інтегрувати принципи спрямованого ациклічного графа думок (**ThoughtDAG**) як основу для спільної роботи Людини та AI-агентів у візуальному просторі **DNK OS**. Рішення усуває лінійні обмеження звичайних чатів, запобігає деградації контексту через топологічну компіляцію вибіркових гілок та гарантує ациклічність міркувань завдяки вбудованій детекції циклів алгоритмом Кана.

<div align="center" style="margin-bottom: 16px;">
  <span style="background-color: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #0284c7;">Домен: Core / Spatial Canvas</span>
  <span style="background-color: #1e293b; color: #34d399; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #059669;">Статус: Accepted</span>
  <span style="background-color: #1e293b; color: #c084fc; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #7c3aed;">Оптика: Dual-Lens</span>
  <span style="background-color: #1e293b; color: #f59e0b; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #d97706;">Ідентифікатор: ADR-005</span>
</div>

`Навігація`: [[00_MOC_DNK_OS|🗺️ Головний MOC DNK OS]] ➔ [[docs/architecture/ARCHITECTURE_MAP|Карта Архітектури]] ➔ [[specs/05_SPATIAL_UI_AND_CANVAS_SPEC|06. Взаємодія Користувача і Фронтенду з Агентом]] ➔ **ADR-005: ThoughtDAG**

---

# 1. Контекст та Проблематика (Context & Problem Statement)

Традиційні підходи до взаємодії з LLM мають дві фундаментальні вади:
1. **Chat Bubble Trap**: Спілкування в лінійному чаті не дозволяє галузити дослідження, тестувати конкуруючі гіпотези та об'єднувати незалежні висновки в єдиний синтез.
2. **Context Bloat & Entropy**: При тривалій роботі лінійний контекст розростається (64k+ токенів), що викликає деградацію уваги моделей (Gemini/Claude attention degradation) та виснаження бюджету інструментів.

Дослідження SOTA-репозиторіїв `chenxiachan/thoughtdag` та `OpenFlowKit` продемонстрували ефективність графового структурування думок: кожна думка має тип (`Hypothesis`, `Claim`, `Evidence`, `Synthesis`) та пов'язана спрямованими ребрами (Context Wires).

---

# 2. Архітектурне Рішення (Decision)

1. **Декларативний DSL Думок (Thought DSL)**:
   - Введено лаконічний синтаксис опису графа для миттєвого імпорту/експорту між текстом, Obsidian-нотатками та полотном.
   - Підтримка типів: `Hypothesis` (H), `Claim` (C), `Evidence` (E), `Synthesis` (SYN).

2. **Детекція Циклів на рівні Ядра (Kahn's Topological Sort Algorithm)**:
   - Будь-який граф думок проходить валідацію алгоритмом Кана.
   - Спроби створити циклічну залежність миттєво відхиляються з локалізацією зациклених вузлів (`cycle_detected: true`).

3. **Multi-Parent Synthesis (Топологічний Мердж Гілок)**:
   - Можливість обрати довільну кількість батьківських гілок і злити їх в єдиний вузол синтезу.
   - Автоматичний розрахунок дедуплікованих предків та криптографічного SHA-256 fingerprint для кешування результатів.

4. **FastMCP Інструменти у `brick_03_spatial_canvas`**:
   - `canvas_parse_thought_dsl`: перетворює DSL у валідний граф нод і ребер.
   - `canvas_export_thought_dsl`: експортує стан полотна у чистий DSL.
   - `canvas_merge_thought_context`: синтезує нову ноду з кількох батьків.
   - `canvas_compile_thought_context`: збирає лише релевантний висхідний контекст для цільової ноди з підрахунком орієнтовних токенів.

5. **UI-Шторка Thought DSL Studio у DNK Studio (`apps/web`)**:
   - Реалізовано компонент `StitchThoughtDagDrawer.tsx` для візуального імпорту, тестування пресетів, мерджу гілок та вивантаження на полотно.

---

# 3. Наслідки Рішення (Consequences)

### Позитивні:
- **Суворе дотримання бюджету токенів (LOD $\le 4\text{k}$)**: агент отримує не весь чат, а тільки топологічних предків вузла, над яким працює.
- **Повна прозорість для Фаундера**: Максим бачить на канвасі логічний ланцюг, чому агент прийшов до певного висновку або рішення.
- **Можливість паралельного дослідження**: агент чи людина можуть паралельно розробляти гіпотезу H1 та гіпотезу H2, після чого однією кнопкою виконати Multi-Parent Synthesis.

### Негативні та Компроміси:
- Додатковий рівень конвертації між React Flow нодами полотна та абстрактними Pydantic-моделями ThoughtDAG (вирішено через централізований `canvasStore` та REST API `/api/v1/thoughtdag/`).

---

## 🔗 4. Пов'язані Документи

- [[00_MOC_DNK_OS|🧭 Головний MOC DNK OS]]
- [[specs/05_SPATIAL_UI_AND_CANVAS_SPEC|Специфікація 06: Взаємодія Користувача і Фронтенду з Агентом]]
- [[specs/04_THOUGHT_TO_PLAN_PIPELINE_SPEC|Специфікація 04: Task Forest DAG Engine]]
- [[docs/adr/ADR-002-task-forest-dag-execution|ADR-002: Task Forest DAG Execution]]
- [[docs/adr/ADR-004-tauri-desktop-client-architecture|ADR-004: Tauri Desktop Architecture]]
