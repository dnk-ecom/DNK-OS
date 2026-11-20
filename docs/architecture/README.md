---
title: "Directory Passport · `docs/architecture/`"
description: "Pullboard Directory Passport for docs/architecture: System blueprints, ADR registry, cross-module contracts, and architectural invariants."
mrh_id: "docs/architecture/README.md"
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
> mrh_id: "docs/architecture/README.md"
> purpose: "Pullboard Directory Passport for docs/architecture: System blueprints, ADR registry, cross-module contracts, and architectural invariants."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ Directory Passport · `docs/architecture/`

| Attribute | Value |
| :--- | :--- |
| **Directory** | `docs/architecture` |
| **Spec ID** | `D1` (`docs/SPEC.md#D1`) |
| **Domain** | System Architecture, ADRs & System Invariants |
| **Status** | Active · Approved |
| **Primary Gate** | `python3 scripts/system/check_mrh_headers.py --domain docs --audit` |

---

## 🎯 Purpose & Scope

The `docs/architecture/` directory is the single source of truth (SSOT) for DNK OS architectural designs, decision registries, system boundary contracts, and governance rules. It houses locked architectural decisions and blueprints governing all autonomous agents and developers.

---

## 🗺️ Subdirectory Topology & Key Documents

- `DECISION_REGISTRY_ADHD.md` — Single source of truth for locked architectural agreements (`[🔒 LOCKED]`).
- `TWO_TIER_DEVELOPMENT_PROTOCOL.md` — Autonomous R&D and standalone distribution protocols.
- `adr/` — Architectural Decision Records following standard RFC formats.
- `blueprints/` — High-level diagrams, data flow specifications, and service boundaries.

---

## 🛡️ Invariants & Rules

1. **Zero Discussion Amnesia**: All architectural decisions must be persisted in `DECISION_REGISTRY_ADHD.md`. Locked decisions are immutable without formal amendment (`T5`, `D4`).
2. **Relative Paths**: All references and file links must strictly use relative paths (`D5`).
3. **MRH Header**: Mandatory MRH header on every architecture document per DNK-STD-0075.
4. **Epistemic Armor**: Proposals must adhere to mandatory 3-flaws dissent and developer critique rubrics (`P4`).

---

## 🚦 Gate Command

```bash
python3 scripts/system/check_mrh_headers.py --domain docs --audit
```
