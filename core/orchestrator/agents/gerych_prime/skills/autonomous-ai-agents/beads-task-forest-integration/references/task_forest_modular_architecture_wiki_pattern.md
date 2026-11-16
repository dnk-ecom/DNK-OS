# Task Forest Integration in Modular Architecture Wiki

## Overview
This reference defines how the Task Forest hierarchical taxonomy (Field -> Sector -> Tree -> Bush -> Flower) is organized within the DNK OS Modular Architecture Wiki (`docs/notes/MY TASKS/1. АРХІТЕКТУРА/`).

## Directory-Anchored Task Branches
Each architecture module (e.g. `01. Аудит репозиторіїв та інʼєкція логіки`, `09. Task Manager системи`) hosts its domain-specific Task Forest branches inside its local `TASKS/` subdirectory:

```text
📁 XX. Module Name/
└── 📁 TASKS/
    ├── tree_feature_alpha.md      # Tree Level: Major architectural epic / milestone
    ├── bush_slice_01.md           # Bush Level: Atomic task slice (bound by MASE <= 25 tools)
    └── flower_leaf_actions.md     # Flower Level: Atomic tool calls & sub-checklists
```

## Frontmatter & Schema Standard
Each task file in `TASKS/` must carry structured frontmatter for Obsidian Dataview:

```yaml
---
title: "Tree: Feature Name"
task_type: "tree"              # field | sector | tree | bush | flower
status: "in_progress"          # pending | in_progress | completed | blocked
priority: "P1"
assigned_agent: "gerych_builder"
dependencies: []
tags:
  - task-forest
  - module-XX
---
```

## Dynamic MOC Aggregation
The parent `00. INDEX.md` dynamically surfaces all tasks in the module using a Dataview query:

```dataview
TABLE file.mtime as "Оновлено", assigned_agent as "Агент", status as "Статус", priority as "Пріоритет"
FROM "docs/notes/MY TASKS/1. АРХІТЕКТУРА/XX. Module Name/TASKS"
SORT priority ASC
```
