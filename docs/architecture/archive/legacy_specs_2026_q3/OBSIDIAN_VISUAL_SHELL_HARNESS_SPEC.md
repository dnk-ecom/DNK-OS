---
title: "Obsidian Visual Shell Harness Spec"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/OBSIDIAN_VISUAL_SHELL_HARNESS_SPEC.md"
> purpose: "Document: Obsidian Visual Shell Harness Spec"
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
> # mrh_id: "docs/architecture/OBSIDIAN_VISUAL_SHELL_HARNESS_SPEC.md"
> # purpose: "Canonical Architecture Specification for Obsidian as the DNK OS Visual Shell and Spatial PKM Harness."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-10-26"
> # author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ DNK OS Visual Shell & Spatial PKM Harness Specification

## 1. Executive Summary

This specification establishes **Obsidian** as the sanctioned **Visual Shell and Spatial PKM Cockpit** for **DNK OS**. Rather than building a redundant, fragile proprietary visual canvas from scratch, DNK OS leverages Obsidian's robust Electron environment, the **Excalidraw** infinite canvas, and **K-Plex** ontology engine as the high-bandwidth spatial interface between the human founder (Maxim) and the autonomous agent swarm (Hermes / Gerych Prime / Antigravity).

---

## 2. System Architecture & The Dual-Surface Model

DNK OS operates on a **Dual-Surface Architecture**:
1. **System 1 (Visual Shell & Cockpit)**: Powered by Obsidian. Serves as the spatial canvas for architecture drafting, ThoughtDAG exploration, task inception, and notes.
2. **System 2 (Execution Microkernel & Agent Swarm)**: Powered by the Python microkernel (`core/`, `apps/api/`, `services/`). Handles deterministic execution, FastMCP tool dispatch, AST gates, and SCONES memory.

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
graph TD
    User["Founder (Maxim)"] <-->|Spatial Drafting & ThoughtDAG| Obsidian["Obsidian Visual Shell (System 1)"]
    Obsidian <-->|Local REST API / FastMCP (Port 27123)| API["DNK OS REST & FastMCP Bridge"]
    API <--> Kernel["DNK OS Python Microkernel (System 2)"]
    Kernel <--> Swarm["Hermes Agent Swarm (Gerych Prime & Specialists)"]
    Kernel <--> SCONES["SCONES Adaptive Memory Engine"]
```

---

## 3. The Sanctioned 11-Plugin Ecosystem

The Obsidian Visual Shell requires strictly these 11 community plugins, maintained in lockstep across all development environments:

1. **`obsidian-excalidraw-plugin`** (`2.8.0`): Infinite canvas, compressed JSON storage, transclusion.
2. **`k-plex`** (`0.1.3`): Spatial relational navigator and semantic ontology suggester (`::p`, `::c`, `::f`, `::r`).
3. **`excalibrain`** (`0.2.14`): Graph visualization of frontmatter concepts.
4. **`excalidraw-extras`** (`1.0.0`): Helper drawing utilities and frames.
5. **`dataview`** (`0.5.67`): Reactive metadata aggregation and registry tables.
6. **`obsidian-hover-editor`** (`0.11.23`): Unpinned floating note editors.
7. **`mermaid-interactive-zoom`** (`1.0.4`): Interactive zoom/pan for Mermaid diagrams.
8. **`obsidian-local-rest-api`** (`5.1.0`): Headless HTTP/MCP bridge for agent swarm automation.
9. **`obsidian42-strange-new-worlds`** (`2.4.2`): Ambient cross-reference badges.
10. **`quickadd`** (`1.11.9`): Macro automation and atomic note capture.
11. **`remotely-save`** (`0.5.2`): Encrypted cloud synchronization.

---

## 4. The 3-Tier Design System

All visual rendering is controlled by three custom stylesheets located in `.obsidian/snippets/`:
- **`dnk-flat-green.css`**: Canonical DNK OS green aesthetic (`#10b981`), `fontFamily: 2`, zero-bleed text margins, pill status badges.
- **`shopify-polaris-helix.css`**: Shopify Polaris design tokens, elevation, and high-readability data grids.
- **`full-width-view.css`**: Gutter-free infinite canvas expansion across multi-monitor setups.

---

## 5. Two-Tier Vault Parity Protocol

To prevent split-brain drift:
- **Primary SSOT**: `DNK_HUB` is the sole development monorepo.
- **Distribution Mirror**: `DNK_OS_APP` receives mirrored configurations (`.obsidian/`) and visual assets via `scripts/export_standalone_app.py`.
- **Directory Invariant**: In `DNK_HUB`, all personal whiteboards and notes are stored strictly under `docs/notes/` (`docs/notes/whiteboards/`, `docs/notes/Excalidraw/`) to preserve the Canonical 8-Root Directory Invariant.

---

## 6. Programmatic Swarm Control (FastMCP & REST)

Agents interact with the running Obsidian instance through `http://127.0.0.1:27123` using bearer authentication:
- `POST /commands/app:reload/`: Forces immediate Electron hot-reload to invalidate in-memory caches.
- `POST /open/{path}`: Navigates Obsidian to any note or Excalidraw drawing.
- `GET /active/`: Reads the content of the currently focused document.

---

## 7. Quality Gates & Verification

Every CI/CD or PR run that touches Obsidian configurations must verify:
1. `python3 scripts/system/root_hygiene_guard.py` returns `exit code 0`.
2. All 11 plugins are present in `.obsidian/community-plugins.json`.
3. All 3 CSS snippets are enabled in `.obsidian/appearance.json`.
4. Excalidraw path points to `docs/notes/Excalidraw`.
