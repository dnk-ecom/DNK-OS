---
title: "Специфікація 01: Архітектура Ядра та FastMCP Фабрики DNK OS"
aliases:
  - "01_CORE_ARCHITECTURE_SPEC"
  - "Архітектура Ядра"
tags:
  - dnk-hub
  - spec
  - architecture
  - microkernel
  - fastmcp
created: 2026-09-18
updated: 2026-09-19
status: active
type: spec
domain: core
author: "DNK-e.com Maksym & Gerych Prime"
version: "1.1.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/01_CORE_ARCHITECTURE_SPEC.md"
> # purpose: "Master Architecture Specification for DNK OS Standalone Agentic Application."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.1.0"
> # updated_at: "2026-09-19"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

> [!abstract] 🧠 МАЙСТЕР-СПЕЦИФІКАЦІЯ ЯДРА ТА СИСТЕМИ ПЛАГІНІВ
> DNK OS — це модульна агентивна операційна система для підприємців і творців. Система забезпечує реєстрацію користувача, налаштування Brand DNA у виділених робочих просторах та автономне виконання задач через інтелектуальне ядро та плагіни FastMCP.

<div align="center" style="margin-bottom: 16px;">
  <span style="background-color: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #0284c7;">Домен: Core Architecture</span>
  <span style="background-color: #1e293b; color: #34d399; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #059669;">Статус: Active</span>
  <span style="background-color: #1e293b; color: #c084fc; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #7c3aed;">Оптика: Dual-Lens</span>
  <span style="background-color: #1e293b; color: #f59e0b; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #d97706;">Специфікація: 01</span>
</div>

`Навігація`: [[00_MOC_DNK_OS|🗺️ Головний MOC DNK OS]] ➔ [[docs/architecture/ARCHITECTURE_MAP|Карта Архітектури]] ➔ **01. Архітектура Ядра**

---

# 🧠 DNK OS MVP: Master Architecture & Plugin-Core Specification

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
flowchart TD
    subgraph UI["1. User & Client Interface"]
        C_WEB["Web UI / Studio Dashboards"]
        C_OBS["Obsidian Canvas / Vault"]
    end

    subgraph Identity["2. Identity & Workspace Plane"]
        U_PROF["User Profile & Settings"]
        W_SPACES["Project Workspaces & Brand DNA"]
        AC_MAT["Capability & Auth Matrix"]
    end

    subgraph Core["3. Context Router & Gerych Engine"]
        LOD["Smart LOD Context Filter (≤ 4k tokens)"]
        DAG["TaskDNA DAG Decomposer"]
        VAL["Output Validator & Error Distiller"]
    end

    subgraph Plugins["4. FastMCP Plugin Fabric"]
        P_MEDIA["🎨 dnk_media (Images, Video, Canvas)"]
        P_COMM["🛍️ dnk_commerce (Shopify, Liquid)"]
        P_FIN["💰 dnk_finance (P&L, Margins)"]
        P_3RD["🧩 3rd-Party FastMCP Servers"]
    end

    UI -->|HTTP / WS / SSE| Identity
    Identity -->|Isolated Brand Context| Core
    Core -->|Context-as-Wires| Plugins
```

---

## 🎯 1. Концепція та Мета
**DNK OS** — це швидка, модульна агентивна операційна система для підприємців і творців.
Користувач реєструється, описує себе, створює ізольовані проекти, наповнює їх матеріалами (Brand DNA, контекст, стиль, активи) та керує роботою через **Розумне Ядро**, яке підключає спеціалізовані плагіни (візуал, фінанси, дистрибуція, аналітика) для автономного виконання задач.

---

## 🏛️ 2. Ключові Модулі Ядра (Core Subsystems)

| Підсистема | Роль та Обов'язки | Ключові Інваріанти |
| :--- | :--- | :--- |
| **Identity & Workspaces** | Профілі користувача, ізоляція проектів, збереження Brand DNA та реєстр активів. | Повний Air-Gap між проектами ([[docs/adr/ADR-003-workspace-isolation-and-brand-dna|ADR-003]]). |
| **Context Router** | Вибірка мінімально необхідного контексту для воркерів (LOD Context Filtering). | Розмір вхідного зрізу ≤ 4,000 токенів. |
| **Task Forest DAG** | Топологічна декомпозиція задач та паралельне виконання мікро-воркерами. | Вузли графа передають контекст по дротах ([[docs/adr/ADR-002-task-forest-dag-execution|ADR-002]]). |
| **FastMCP Fabric** | Стандартизована шина підключення зовнішніх модулів та доменних агентів. | Відкритий протокол JSON-RPC FastMCP ([[docs/adr/ADR-001-microkernel-fastmcp-architecture|ADR-001]]). |

---

## 🔄 3. Життєвий Цикл Виконання Задачі (Execution Lifecycle)

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
    actor User as Користувач / Canvas
    participant GW as API Gateway
    participant WS as Workspace & Brand DNA
    participant DAG as Task Forest Engine
    participant MCP as FastMCP Plugin

    User->>GW: 1. Постановка задачі у Проєкті
    GW->>WS: 2. Запит профілю Brand DNA
    WS-->>GW: Повернення контекстного зрізу (<4k токенів)
    GW->>DAG: 3. Побудова графа залежностей TaskDNA
    DAG->>MCP: 4. Виклик атомарного воркера (Context-as-Wires)
    MCP-->>DAG: Результат виконання інструменту
    DAG-->>GW: Завершення виконання зрізу
    GW-->>User: 5. Стрімінг прогресу (SSE) та артефакт
```

---

## 🔗 4. Пов'язані Специфікації та Документи
- [[specs/02_USER_IDENTITY_AND_SOUL_SPEC|02. Профіль, Простори та Brand DNA]]
- [[specs/01_CORE_AND_ACTION_BUS_SPEC|03. Фабрика Плагінів FastMCP]]
- [[specs/04_THOUGHT_TO_PLAN_PIPELINE_SPEC|04. Task Forest DAG Engine]]
- [[specs/01_CORE_AND_ACTION_BUS_SPEC|05. Контракти API Gateway]]

---

`Див. також`: [[00_MOC_DNK_OS|🗺️ Головний MOC DNK OS]] | [[docs/architecture/ARCHITECTURE_MAP|Карта Архітектури]] | [[context/SYSTEM_INVARIANTS|Системні Інваріанти]]
