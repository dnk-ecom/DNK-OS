---
title: "Master Architecture Map: DNK OS Application"
description: "Master Architecture Map and Component Interaction Diagram for DNK OS."
mrh_id: "docs/architecture/blueprints/ARCHITECTURE_MAP.md"
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
> mrh_id: "docs/architecture/blueprints/ARCHITECTURE_MAP.md"
> purpose: "Master Architecture Map and Component Interaction Diagram for DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

> [!abstract] 🗺️ МАЙСТЕР-КАРТА АРХІТЕКТУРИ СИСТЕМИ
> Комплексна просторова та функціональна схема взаємодії клієнтського рівня, API-шлюзу, рушія Task Forest DAG, підсистеми ізоляції Workspace/Brand DNA та фабрики FastMCP плагінів.

<div align="center" style="margin-bottom: 16px;">
  <span style="background-color: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #0284c7;">Домен: System Architecture</span>
  <span style="background-color: #1e293b; color: #34d399; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #059669;">Статус: Active</span>
  <span style="background-color: #1e293b; color: #c084fc; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #7c3aed;">Оптика: Dual-Lens</span>
  <span style="background-color: #1e293b; color: #f59e0b; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; border: 1px solid #d97706;">Рівнів: 4 Тіри</span>
</div>

`Навігація`: [[00_MOC_DNK_OS|🗺️ Головний MOC DNK OS]] ➔ [[specs/01_CORE_AND_ACTION_BUS_SPEC|🏛️ Специфікація Ядра]] ➔ **Карта Архітектури**

---

# 🗺️ Master Architecture Map: DNK OS Application

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
    subgraph Tier1["1. Client Tier"]
        UI_TAURI["Tauri v2 Desktop Shell (Rust + React/Vite)"]
        UI_WEB["Web Dashboard (Headless / Remote)"]
        UI_OBS["Obsidian Vault / Excalidraw"]
        UI_MOB["Mobile Client / Studio"]
    end

    subgraph Tier2["2. API Gateway Layer"]
        GW["FastAPI Core Gateway"]
        AUTH["Auth & Rate Limiting"]
        SSE["SSE / WebSocket Dispatcher"]
        GW --- AUTH
        GW --- SSE
    end

    subgraph Tier3["3. Core Microkernel"]
        WS["Workspace & Identity Engine\n- Brand DNA Profiles\n- Asset Registry\n- Air-Gap Isolation"]
        DAG["Task Forest DAG Engine\n- Topological Planner\n- Context-as-Wires Router\n- Micro-Workers Pool"]
    end

    subgraph Tier4["4. FastMCP Plugin Fabric"]
        MCP_M["dnk_media\n(Visuals / Video)"]
        MCP_C["dnk_commerce\n(Shopify / Liquid)"]
        MCP_F["dnk_finance\n(Unit Economics)"]
        MCP_D["dnk_distribution\n(Content Feeds)"]
    end

    Tier1 -->|HTTP REST / SSE / WS| Tier2
    Tier2 -->|Session & Auth Context| WS
    Tier2 -->|Task Submissions| DAG
    DAG -->|Air-Gapped Assets| WS
    DAG -->|FastMCP JSON-RPC| Tier4
```

---

## 🏛️ Рівні Архітектури та Їх Відповідальність

### 1. Клієнтський Рівень (Client Tier)
- **Tauri v2 Desktop Shell**: Канонічний нативний клієнт (Rust runtime + React/Vite/Tailwind UI). Надає системний трей, нативні сповіщення, глобальні хоткеї та апаратне прискорення з мінімальним споживанням RAM (~30–50 МБ). Див. [[docs/adr/ADR-004-tauri-desktop-client-architecture|ADR-004]].
- **Obsidian Workspace**: Первинне середовище фіксації знань, перегляду специфікацій та взаємодії з агентом через [[Do not Delete - Draft|Draft.md]].
- **Visual Canvas**: Графічне відображення процесів у палітрі Flat Green (`#16382b` / `#86efac`) без налізань тексту.
- **Web / Studio UI**: Легковажні вебінтерфейси для віддаленого керування проектами та моніторингу задач.

### 2. Рівень Шлюзу (API Gateway Layer)
- Детермінована валідація вхідних запитів (Pydantic V2).
- Маршрутизація SSE-стрімів для передачі прогресу виконання підзадач у реальному часі.
- Детальні контракти описані в [[specs/01_CORE_AND_ACTION_BUS_SPEC|05_API_GATEWAY_CONTRACTS.md]].

### 3. Мікроядро (Core Microkernel)
- **Task Forest DAG Engine**: Планувальник топологічного графа задач. Забезпечує принцип Context-as-Wires, де кожен воркер отримує лише цільовий зріз даних (LOD ≤ 4k токенів). Див. [[specs/04_THOUGHT_TO_PLAN_PIPELINE_SPEC|04_TASK_FOREST_DAG_SPEC.md]] та [[docs/adr/ADR-002-task-forest-dag-execution|ADR-002]].
- **ThoughtDAG Spatial Brain**: Граф спрямованих думок, топологічний мердж та детекція циклів алгоритмом Кана для спільної роботи користувача та агента на полотні. Див. [[specs/05_SPATIAL_UI_AND_CANVAS_SPEC|06_USER_FRONTEND_AGENT_INTERACTION_SPEC.md]] та [[docs/adr/ADR-005-thoughtdag-spatial-knowledge-and-agent-interaction|ADR-005]].
- **Workspace & Identity**: Повна фізична ізоляція контексту між проектами користувача, збереження Brand DNA та налаштувань. Див. [[specs/02_USER_IDENTITY_AND_SOUL_SPEC|02_IDENTITY_AND_PROJECTS_SPEC.md]] та [[docs/adr/ADR-003-workspace-isolation-and-brand-dna|ADR-003]].

### 4. Фабрика Плагінів FastMCP (Plugin Fabric)
- Усі інструменти та доменні агенти підключаються як ізольовані мікросервіси через легковажний JSON-RPC протокол FastMCP.
- Стандарти створення описані в [[specs/01_CORE_AND_ACTION_BUS_SPEC|03_PLUGIN_SYSTEM_FASTMCP_SPEC.md]] та [[docs/adr/ADR-001-microkernel-fastmcp-architecture|ADR-001]].

---

`Див. також`: [[specs/01_CORE_AND_ACTION_BUS_SPEC|Специфікація Ядра]] | [[specs/05_SPATIAL_UI_AND_CANVAS_SPEC|Взаємодія Користувача і Фронтенду з Агентом]] | [[00_MOC_DNK_OS|Головний MOC]] | [[docs/guides/DEVELOPER_GUIDE|Гайд Розробника]]
