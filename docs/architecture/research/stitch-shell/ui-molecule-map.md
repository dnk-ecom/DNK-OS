---
title: "UI Molecule Map: Canvas Grid Layout"
description: "Карта молекулярних областей та сітка інтерфейсу Stitch."
mrh_id: "docs/architecture/research/stitch-shell/ui-molecule-map.md"
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
> mrh_id: "docs/architecture/research/stitch-shell/ui-molecule-map.md"
> purpose: "Карта молекулярних областей та сітка інтерфейсу Stitch."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# UI Molecule Map: Canvas Grid Layout

Візуальне розташування молекул Stitch на екрані користувача:

```
┌─────────────────────────────────────────────────────────────┐
│ [DNK_OS_MVP]             [- 100% + Reset]    [Export] [Share]│ ◄ StitchTopHeader
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌──────────────┐                                ┌───────┐   │
│ │ glm-5.2      │                                │   S   │   │
│ │ Thoughts     │                                │   H   │   │
│ │ & Console    │      (Infinite Canvas Grid)    │   D   │   │ ◄ StitchRightToolbar
│ │              │                                │   M   │   │
│ │ [Logs]       │                                │   F   │   │
│ └──────────────┘                                └───────┘   │
│ ◄ StitchLeftAgentPanel                                      │
│                                                             │
│                        ┌───────────────────┐                │
│                        │ [Pill 1] [Pill 2] │                │
│                        ├───────────────────┤                │
│                        │ [Prompt Input...] │                │
│                        └───────────────────┘                │
│                         ◄ StitchPromptDock                  │
└─────────────────────────────────────────────────────────────┘
```
