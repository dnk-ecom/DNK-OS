---
title: "Skill Curator & Continuous Improvement Digest"
description: "Skill Curator & Continuous Improvement Digest"
mrh_id: "docs/notes/Skill Curator Digest.md"
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
> mrh_id: "docs/notes/Skill Curator Digest.md"
> purpose: "Skill Curator & Continuous Improvement Digest"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 Skill Curator & Continuous Improvement Digest
*Last Synced: 2026-11-16 23:11 | Total Observations: 2 | Pending: 2 | Structural Barriers Required: 1*

## 📊 Summary Pulse
- **High-Generality Opportunities (Score ≥ 0.75)**: 2
- **Second Violation Invariant Triggers (2+ Occurrences)**: 1
- **Sibling Propagation Audits**: 2

---

## 🚨 Second Violation Invariants (Deterministic Barrier Required)
> *Rule: If an agent violates a rule twice, DO NOT reword prompts. Build a hook, AST check, or linter.*

### ⚠️ `dnk-shopify`: Hardcoded absolute path
- **Observation ID**: `obs-0002-dnk-shopify`
- **Violations Count**: 2
- **User Correction**: Always use relative paths ../ or ./
- **Mandated Structural Action**: Implement pre-tool hook check in `scripts/system/hermes_pre_tool_hook.py` or unit test in `tests/`.
- **Siblings to Protect**: `shopify-theme-ast-engineering`

---

## 🔍 Pending Observations Queue (Evaluated via Generalisability Test)

#### [🟢 General 1.0] `dnk-shopify` — `obs-0001-dnk-shopify`
- **Failure Mode**: Hardcoded absolute path
- **Context**: Exporting liquid asset
- **Correction**: Always use relative paths ../ or ./
- **Siblings Checked**: shopify-theme-ast-engineering
- **Action**: Stage into SKILL.md

#### [🟢 General 1.0] `dnk-shopify` — `obs-0002-dnk-shopify`
- **Failure Mode**: Hardcoded absolute path
- **Context**: Exporting liquid asset second time
- **Correction**: Always use relative paths ../ or ./
- **Siblings Checked**: shopify-theme-ast-engineering
- **Action**: Stage into SKILL.md

