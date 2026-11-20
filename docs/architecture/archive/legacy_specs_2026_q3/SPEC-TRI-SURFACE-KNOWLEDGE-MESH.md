---
title: "Spec-Tri-Surface-Knowledge-Mesh"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/SPEC-TRI-SURFACE-KNOWLEDGE-MESH.md"
> purpose: "Document: Spec-Tri-Surface-Knowledge-Mesh"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/SPEC-TRI-SURFACE-KNOWLEDGE-MESH.md"
> # purpose: "Architecture Specification for Tri-Surface Knowledge Mesh: Obsidian Vault + Fumadocs MDX + SCONES Agent Memory (DEC-035)."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-10-27"
> # author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧠 Tri-Surface Knowledge Mesh Specification (DEC-035)

## 1. Architectural Mission
To eliminate all information asymmetry between **Human Spatial Thinking** (Obsidian Canvas & Graph), **Executive Web Presentation** (Fumadocs Portal), and **Autonomous Agent Execution** (SCONES Memory & FastMCP Tools). All three surfaces operate over a **Single Physical Substrate**: `../DNK-Ecom_OS/content/`.

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
    Substrate["📁 Shared Physical Substrate: DNK-Ecom_OS/content/"]
    
    Substrate -->|Direct File Mount| Obs["👤 Surface 1: Obsidian Vault (Spatial Graph & Canvas)"]
    Substrate -->|fumadocs-obsidian parser| Fuma["🌐 Surface 2: Fumadocs Web Portal (Next.js / Orama Search)"]
    Substrate -->|MRH & Wikilink Graph Extraction| Scones["🤖 Surface 3: SCONES Memory Graph (FastMCP Tool for Agents)"]
    
    Obs <-->|Bidirectional Wikilinks [[...]]| Fuma
    Fuma <-->|/llms.txt & Raw MDX Endpoints| Scones
    Scones -->|<= 2 Hops Resolution| AgentWorker["⚡ Autonomous Agent (Hermes/Gerych/Antigravity)"]
```

---

## 2. The 3 Surfaces

### Surface 1: Obsidian Spatial Harness (Human Mind)
- **Mount Target:** `../DNK-Ecom_OS/content/` (opened directly as an Obsidian Vault).
- **Capabilities:**
  - **Graph View:** Visualizes relationships between `DEC-*`, `INV-*`, `RB-*`, and domain modules.
  - **Excalidraw & Canvas:** Spatial canvas planning of pipelines and themes.
  - **Local REST API (`:27123`):** Allows agents to read active viewport notes programmatically.
- **Git Hygiene:** Local runtime states (`.obsidian/workspace*.json`, `.obsidian/cache`) are strictly ignored via `.gitignore`.

### Surface 2: Fumadocs Web Portal (Executive & API Explorer)
- **Parser Engine:** Integration of `@fumadocs/obsidian` package from `../DNK_Vibe/fumadocs/packages/obsidian`.
- **Supported Syntaxes:**
  - Standard Obsidian Wikilinks: `[[dec-001]]`, `[[dec-001#Technical Standard]]`, `[[inv-001-path-hygiene|Path Hygiene]]`.
  - Native Obsidian Callouts: `> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`, rendered as interactive Fumadocs `<Callout>` widgets.
  - File Embeds: `![[image.png]]` and text transclusions.
- **Search & Ingestion:** Built-in client-side WASM Orama full-text search.

### Surface 3: SCONES Agent Memory Graph (Autonomous Action)
- **Graph Schema:**
  - **Nodes:** ADR (`dec-*`), Invariant (`inv-*`), Runbook (`rb-*`), Service Symbol (`services/*`).
  - **Edges:** `depends_on`, `enforces`, `verifies_with`, `replaces`.
- **FastMCP Protocol Integration:**
  - `scones_resolve_link(symbol: str) -> LinkTarget`: Resolves any wikilink or symbol to its exact file, line, and invariant in $< 10\text{ms}$.
  - `scones_get_context_subgraph(node_id: str, depth: int = 1) -> str`: Returns targeted, token-diet markdown slice ($\le 1,200$ tokens) covering the node and its immediate neighbors.

---

## 3. Link Canonicalization Table

| Node Type | Obsidian Wikilink | Target Fumadocs Route | SCONES Node ID |
|---|---|---|---|
| **ADR (Decision)** | `[[dec-001]]` | `/docs/human/01_architecture_decisions/dec-001` | `adr:dec-001` |
| **Invariant** | `[[inv-001-path-hygiene]]` | `/docs/agent/invariants/inv-001-path-hygiene` | `inv:path-hygiene` |
| **Runbook** | `[[rb-001-verify-all]]` | `/docs/agent/runbooks/rb-001-verify-all` | `rb:verify-all` |
| **Roadmap** | `[[10-day-sunset-plan]]` | `/docs/human/02_roadmap_and_milestones/10-day-sunset-plan` | `milestone:10-day-sunset` |

---

## 4. Rollout & Autonomous Execution Plan (Gerych)

1. **Step 1 (Obsidian Vault Genesis):**
   - Create clean `.obsidian/` configuration inside `../DNK-Ecom_OS/content/` with graph settings.
   - Add `.obsidian/workspace*.json` to `../DNK-Ecom_OS/.gitignore`.
2. **Step 2 (Fumadocs Obsidian Plugin Wiring):**
   - Configure `fumadocs-mdx` with wikilink remark plugin or compile options from `../DNK_Vibe/fumadocs/packages/obsidian`.
   - Verify that `[[wikilinks]]` render as clickable Next.js links in `http://localhost:3000`.
3. **Step 3 (SCONES Graph Indexer):**
   - Implement `scripts/system/index_mesh_to_scones.py` in `DNK_HUB` to parse all wikilinks in `content/` and store the bidirectional adjacency list in `~/.dnk_runtime/scones/`.
4. **Step 4 (Verification Quality Gate):**
   - Run `bash ../DNK-Ecom_OS/scripts/verify_all.sh` to ensure size stays $\le 2\text{ MB}$ and exit code is 0.
