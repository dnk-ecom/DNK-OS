---
title: "Mermaid Diagram Template"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/obsidian-vault-hygiene/templates/mermaid_diagram_template.md"
> purpose: "Document: Mermaid Diagram Template"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/note-taking/obsidian-vault-hygiene/templates/mermaid_diagram_template.md"
# purpose: "Canonical Obsidian-compatible Mermaid diagram template with mandatory label quoting and unquoted edge text."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-08"
# author: "Gerych Prime & DNK OS"
# --- END DNK-MRH-HEADER ---

# Canonical Mermaid Diagram Template for Obsidian

Always wrap node labels and subgraph titles in explicit double quotes `["..."]` to prevent parser collisions with parentheses `()`, colons `:`, or apostrophes `'`.

CRITICAL INVARIANT FOR EDGES & THEMING:
1. **Never use double quotes inside edge labels** (`|...|`). Edge labels between pipes MUST be plain text (`Router -->|1. Читає контракт| Card`), NEVER `Router -->|"..."| Card` which throws `Expecting 'LINK', 'UNICODE_TEXT', 'EDGE_TEXT', got 'STR'`.
2. **Never use reverse labeled arrows** (`Target <--|label| Source`). Always orient forward (`Source -->|label| Target`) or bidirectional (`Source <-->|label| Target`).
3. **Never hardcode custom HEX fills** (`style Node fill:#hex,stroke:#hex`). Omit manual `style ... fill:#...` so Obsidian's theme engine automatically adapts between Dark and Light palettes.
4. **Preserve top-down hierarchy in `flowchart TD`**. Do not create cyclic feedback loops from bottom layers to top layers (e.g. `ServiceDocs --> Router`), which causes Dagre to invert ranks and flip the diagram upside-down. Use bidirectional `<-->` or downward response edges.
5. **Multi-Column Matrix Layout for Multi-Level Architectures (4–8 levels/stages)**: Use a root `flowchart LR` pairing 2–3 vertical subgraphs (`direction TB`), connected by bold inter-tier bridges (`TierA ==>|Handoff| TierB`). This keeps diagram height compact (<500px), maintains 100% font size, and avoids the "High Tower / Endless Scroll" downscaling effect.

### Pattern A: 3-Tier Vertical Service Stack (`flowchart TD`)

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
    %% -------------------------------------------------------------
    %% SUBGRAPH 1: Core Orchestrator
    %% Always quote subgraph title when it contains parentheses
    %% -------------------------------------------------------------
    subgraph Core ["ЯДРО СИСТЕМИ (DNK OS Core)"]
        direction TB
        Router["Task Router / Swarm Coordinator"]
        SCONES["Пам'ять SCONES & Сесії"]
        Security["SpendGuard & Auth Gate"]
    end

    %% -------------------------------------------------------------
    %% SUBGRAPH 2: Standardized Protocol
    %% -------------------------------------------------------------
    subgraph Protocol ["ВІДКРИТИЙ СТАНДАРТИЗОВАНИЙ ПРОТОКОЛ"]
        direction TB
        Card["service_manifest.yaml: DNK Service Card"]
        AgentProto["Agent Protocol: /tasks, /steps, /artifacts"]
        MCP["MCP Tools: Tools Discovery & Execution"]
    end

    %% -------------------------------------------------------------
    %% SUBGRAPH 3: Autonomous Vertical Service
    %% -------------------------------------------------------------
    subgraph Service ["АВТОНОМНИЙ СЕРВІС (Domain Service)"]
        direction TB
        ServiceRouter["FastAPI Service Router (/health, /metrics)"]
        Worker["Воркери сервісу (Domain Logic / AST Engine)"]
        ServiceDocs["docs/SPECIFICATION.md & ARCHITECTURE.md"]
    end

    %% Interactions and Connections (Note: NO quotes inside pipes |...|!)
    Router -->|1. Читає контракт ServiceCard| Card
    Router -->|2. Викликає задачу POST /tasks| AgentProto
    Router -->|3. Запитує інструменти| MCP

    Card -->|Визначає конфігурацію| ServiceRouter
    AgentProto -->|Маршрутизує виконання| Worker
    MCP -->|Експортує тули| Worker
    Worker -->|Фіксує знання| ServiceDocs

    Worker -.->|Зберігає контекст сесії| SCONES
    Worker -.->|Перевіряє бюджети токенів| Security
```

### Pattern B: 2-Column Multi-Tier Architectural Matrix (`flowchart LR` + `direction TB`)

Ideal for multi-level taxonomies, SOTA audits, and dual-layer engines (e.g. Session vs Persistent memory). Prevents vertical letterboxing and fits 100% inside desktop and laptop viewports:

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
flowchart LR
    %% Column 1: Ephemeral / Fast Tier
    subgraph FastTier ["⚡ Шар 1: Сесійна Оптимізація & Віртуалізація"]
        direction TB
        L1["🔍 <b>Рівень 1: Tool Schema Virtualization</b><br><div align='left'>• Dynamic Pruning & Lazy Loading схем<br>• On-demand опис інструментів (&lt;3k tax)</div>"]
        L2["📦 <b>Рівень 2: Observation Sidecars</b><br><div align='left'>• Externalization важких виводів на диск<br>• result_ref та детерміноване маскування</div>"]
        L3["⚡ <b>Рівень 3: Hierarchical DAG Engine</b><br><div align='left'>• SQLite FTS5 індексування історії сесії<br>• Багаторівневий зум D0-D2 без втрат</div>"]
        L1 --> L2 --> L3
    end

    %% Column 2: Strategic / Long-Term Tier
    subgraph LongTier ["🧠 Шар 2: Стратегічна Пам'ять & Еволюція"]
        direction TB
        L4["📋 <b>Рівень 4: Continuity Ledgers</b><br><div align='left'>• 'Compound, Don't Compact' підхід<br>• Файли передачі стану (YAML Handoffs)</div>"]
        L5["🌿 <b>Рівень 5: Git-like Context Controller</b><br><div align='left'>• Ізоляція спроб у CONTEXT_BRANCH<br>• Чистий мердж успішних артефактів</div>"]
        L6["🏛️ <b>Рівень 6: GraphRAG & Cognitive Memory</b><br><div align='left'>• AST семантичні графи коду (SurrealDB)<br>• SCONES L0–L3 довготривалі знання</div>"]
        L4 --> L5 --> L6
    end

    %% Inter-Tier Bridge (unquoted edge label)
    FastTier ==>|Ескалація перевірених артефактів| LongTier
```
