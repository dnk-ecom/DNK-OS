---
title: "Directory Passport · `docs/templates/`"
description: "Pullboard Directory Passport for docs/templates: Standardized document templates for tasks, specs, ADRs, SOPs, and intents."
mrh_id: "docs/templates/README.md"
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
> mrh_id: "docs/templates/README.md"
> purpose: "Pullboard Directory Passport for docs/templates: Standardized document templates for tasks, specs, ADRs, SOPs, and intents."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📐 Directory Passport · `docs/templates/`

| Attribute | Value |
| :--- | :--- |
| **Directory** | `docs/templates` |
| **Spec ID** | `D9` (`docs/SPEC.md#D9`) |
| **Domain** | Document Templates, Standards & Scaffolds |
| **Status** | Active · Approved |
| **Primary Gate** | `python3 scripts/system/check_mrh_headers.py --domain docs --audit` |

---

## 🎯 Purpose & Scope

The `docs/templates/` directory provides authoritative, standardized structural templates for new documentation, architectural decision records (ADRs), autonomous agent task assignments, business intents, and engineering specifications.

---

## 🗺️ Subdirectory Topology

- `tasks/` — Templates for task specifications (`GERYCH_TASK_TEMPLATE.md`, `TASK_FOREST_TEMPLATE.md`).
- `architecture/` — Architectural Decision Record (`ADR_TEMPLATE.md`) and Technical RFC scaffolds.
- `intents/` — Business intent definition scaffolds (`INTENT_TEMPLATE.md`).

---

## 🛡️ Invariants & Rules

1. **Template MRH Compliance**: All templates must provide a valid MRH header blueprint complying with DNK-STD-0075.
2. **Relative Paths**: Template links and file paths must strictly use relative path conventions (`D5`).
3. **Immutability of Core Contracts**: Structural fields required by validators (`mrh_id`, `purpose`, `status`) must be present in every template.

---

## 🚦 Gate Command

```bash
python3 scripts/system/check_mrh_headers.py --domain docs --audit
```
