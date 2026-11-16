# Embedded Self-Documenting Canvas Manifest Pattern

## Purpose & Core Problem
When agents or humans build visual canvases in Obsidian via `.excalidraw.md`, the visual JSON drawing contains nodes and links, but often lacks the deep architectural narrative, operational trigger modes, and execution invariants. If stored solely in chat or external notes, future agents and human operators lose the rationale ("Why was it built this way?").

Because Obsidian Excalidraw files are hybrid markdown documents, everything placed outside the `%% ... %%` comment block is valid, first-class Markdown:
- Fully readable by agents via `read_file`.
- Indexed by Obsidian quick switcher, full-text search, backlinks, and Dataview.
- Preserved when switching between Excalidraw drawing view and Markdown view.

## Canonical Structure of a Self-Explaining `.excalidraw.md`

```markdown
---
title: "System / Workflow Title"
aliases: ["Canvas Alias"]
tags: [excalidraw, dnk-hub, architecture]
excalidraw-plugin: parsed
---
<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "docs/notes/Excalidraw/XXX_name.excalidraw.md"
# purpose: "Visual spatial canvas & self-documenting operational guide."
# canonical_source: true
# --- END DNK-MRH-HEADER ---
-->

==⚠ Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document to interact with the visual canvas. ⚠==

# 🧭 Architectural Manifest & Operational Guide

## ❓ Why was it built this way? (Root Causes & Architectural Rationale)
- **Problem addressed**: Solo agent syndrome, context rot (>64k), lack of negative scope.
- **Solution applied**: Multi-stage pipeline, strict file whitelisting, atomic execution slices (MASE <= 25 tools).

## 👤 Human Operator Guide (Maxim)
- How to trigger workflows in 1-2 sentences.
- Trigger commands: `«Склади спеку: ...»`, `«В роботу: ...»`, `«Аудит задачі: ...»`.
- Visual interaction: Cmd+Click on node links opens target files.

## 🤖 AI Agent Protocol (Gerych Prime & Swarm Workers)
- Step 0: Autonomous Triage (`dnk_triage_task`).
- Step 1: Context Injection (User memory + AST symbol resolution via `dnk_resolve_symbol`).
- Step 2: Strict Anti-Scope & Targeted File Whitelist.
- Step 3: MASE Slices (<= 25 tools per slice).
- Step 4: Verification Gate (`scripts/verify_all.sh` 100% Green) + YAML Completion Report.

## 🗺️ Visual Station Matrix
| Station # | Name | Color | Responsibility |
|---|---|---|---|
| 1 | Inception | Light Blue | Raw user intent & trigger modes |
| 2 | Context Injection | Purple | Memory, AST symbols, SCONES |
| 3 | Specification | Green | Anti-scope, whitelist, MASE |
| 4 | Swarm Engine | Amber | Distributed workers (builder, auditor) |
| 5 | Verification | Dark Slate | Master Quality Gate & Evidence JSON |

## 🔗 Linked System Files
- [[docs/templates/GERYCH_TASK_TEMPLATE.md]]
- [[docs/templates/INTENT_TEMPLATE.md]]
- [[scripts/verify_all.sh]]

# Excalidraw Data

## Linked System Files
- ...

%%
## Drawing
```json
{ ... }
```
%%
```

## Python Generator Recipe
Automate generation using a dedicated script (e.g. `scripts/system/generate_task_workflow_excalidraw.py`) that writes the markdown header, renders the element nodes with calculated bounding boxes, bindings, and colors, and wraps the JSON payload in `%%\n## Drawing\n```json\n...\n```\n%%\n`.
