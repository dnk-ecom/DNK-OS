---
title: "Дворівнева Архітектура Агентів та Протокол Handoff (DEC-025)"
description: "Architecture specification for C-Suite Tandem (Strategist + Auditor) and Folder-as-Harness Handoff to 3 Core Workhorses (DEC-025)."
mrh_id: "docs/architecture/blueprints/TWO_TIER_AGENT_HANDOFF_PROTOCOL.md"
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
> mrh_id: "docs/architecture/blueprints/TWO_TIER_AGENT_HANDOFF_PROTOCOL.md"
> purpose: "Architecture specification for C-Suite Tandem (Strategist + Auditor) and Folder-as-Harness Handoff to 3 Core Workhorses (DEC-025)."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ Дворівнева Архітектура Агентів та Протокол Handoff (DEC-025)

## 1. Концепція та Мета
Протокол дворівневої організації агентів реалізує засади рішення **DEC-025 (Folder as Harness & Subagent Folding Protocol)**:
1. **Tier-1 (C-Suite Штаб)**: Керуючий тандем двох головних персон у `core/orchestrator/agents/`:
   - **Стратег Prime 👑** (`core/orchestrator/agents/strategist/`): Chief Spatial Orchestrator & TaskDNA Master. Керує полотном `apps/canvas/`, декомпонує задачі на DAG-графи, формує контекстні дроти та готує специфікації для доменних лідів.
   - **Аудитор Gate ⚔️** (`core/orchestrator/agents/auditor/`): Adversarial Security & Quality Gatekeeper. Забезпечує нуль підлабузництва (Anti-Sycophancy), обов'язковий Pre-Mortem, 3-Flaws Rule, граничні умови та детермінований Machine Proof (`exit code 0`).
2. **Tier-2 (Core Workhorses / Folder-as-Harness)**:
   - Спеціалізовані доменні ліди без standing context bloat:
     - `services/dnk_shopify/` (Shopify Lead — Liquid AST, Themes, Cart Drawer)
     - `services/dnk_media/` (Media & VTON Lead — Video Generation, Remotion, Audio/Subtitles)
     - `services/dnk_distribution/` (Distribution & Logistics Lead — Orders, Inventory, Fulfillment)

---

## 2. Діаграма Потоку Делегування (Sequence Diagram)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#16191c',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#34d399',
    'lineColor': '#34d399',
    'secondaryColor': '#102219',
    'tertiaryColor': '#16191c',
    'tertiaryTextColor': '#ffffff',
    'titleColor': '#ffffff',
    'textColor': '#ffffff',
    'mainBkg': '#16191c',
    'nodeBorder': '#34d399',
    'clusterBkg': 'transparent',
    'clusterBorder': 'rgba(255, 255, 255, 0.16)',
    'edgeLabelBackground': '#102219',
    'fontSize': '13px'
  }
}}%%
sequenceDiagram
    autonumber
    actor Founder as 👤 Фаундер (Максим)
    participant UI as 🎨 Canvas UI (Copilot Dock)
    participant Strat as 👑 Стратег Prime
    participant Audit as ⚔️ Аудитор Gate
    participant Lead as 🛠️ Workhorse Lead (Shopify/Media/Distribution)

    Founder->>UI: Вводить ціль або створює задачу
    UI->>Strat: runAgentTask(goal) [Persona: Strategist]
    Strat->>UI: Стрімінг TaskDNA DAG (Ноди на полотні)
    Strat->>Audit: Запит на верифікацію специфікації (Pre-Mortem & Boundaries)
    Audit->>Audit: Пре-мортем аналіз (3 приховані ризики, 5 векторів)
    alt Ризики не усунуто або є порушення
        Audit-->>Strat: REJECTED (Перелік блокерів)
        Strat-->>UI: Відображення червоного бейджа рецензії
    else Усі інваріанти дотримано
        Audit-->>Strat: APPROVED (AuditorCertificate, exit code 0)
        Strat->>UI: Оновлення бейджа: "Auditor Gate: APPROVED"
        Strat->>Lead: Stateless Handoff (HandoffTaskSpec, Whitelist, Negative Scope)
        Lead->>Lead: Атомна імплементація (MASE: ≤25 tool calls, ≤8 tools)
        Lead-->>Audit: Запит на фінальний детермінований аудит (git diff + tests)
        Audit->>Audit: Запуск ensure_dnk_tui_integrity.py та verify_all.sh
        Audit-->>UI: Машинний доказ: exit code 0, статус COMPLETED
    end
```

---

## 3. Правила та Інваріанти Протоколу Handoff

1. **Folder-as-Harness**:
   Кожен сервісник у `services/` є самостійним ізольованим харнесом з власним `service_manifest.yaml` та FastMCP роутером. Заборонено прямий крос-сервісний імпорт внутрішніх функцій.
2. **Нуль Мутацій без Сертифіката Аудитора**:
   Будь-який кодосинтез у `services/` блокується без наявності `AuditorCertificate` зі статусом `APPROVED`.
3. **Строгий Target File Whitelist & Negative Scope**:
   Стратег зобов'язаний явно декларувати білий список файлів для модифікації. Будь-які модифікації за межами `services/<workhorse>/` відхиляються.
4. **Тільки Відносні Шляхи**:
   Усі шляхи в специфікаціях повинні бути відносними (`./`, `../`). Абсолютні шляхи заборонені.
