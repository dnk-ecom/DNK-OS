---
title: "DNK OS Agent Handoff & Session Checkpoint Template"
description: "Canonical Session Checkpoint & Agent Handoff Template under ADR-006 Cognitive Guardrails."
mrh_id: "docs/templates/HANDOFF_TEMPLATE.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - dnk/templates
  - dnk/handoff
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/templates/HANDOFF_TEMPLATE.md"
> purpose: "Canonical Session Checkpoint & Agent Handoff Template under ADR-006 Cognitive Guardrails."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

> ```

# 🔄 DNK OS Agent Handoff & Session Checkpoint Template (ADR-006)

> **Cognitive Guardrails & Anti-Degradation Protocol (ADR-006)**  
> This template is triggered when an agent session reaches **~20 tool calls**, **~40k tokens**, or finishes an atomic slice.  
> Prevents Gemini Flash attention entropy, context compaction blindness, and lost execution state.  
> Every handoff MUST be bound to a GitHub Issue (Task Tracker SSOT) and committed to the `DNK_HUB` repository (Codebase SSOT).

---

## 📌 1. Session Metadata & SSOT Traceability

- **Task ID / Spec**: `TASK-DNK-...` *(ref: `docs/tasks/...`)*
- **GitHub Issue**: `#<ISSUE_NUMBER>` *(verify via `gh issue view <ISSUE_NUMBER>`)*
- **Git Branch**: `dnk-mvp/...`
- **Latest Commit**: `<COMMIT_HASH>` *(run `git log -1 --oneline`)*
- **Outgoing Agent / Persona**: `[e.g. gerych_builder | dnk_dev_fullstack | dnk_mentor]`
- **Incoming Agent / Persona**: `[e.g. gerych_auditor | dnk_mentor | gerych_builder]`
- **Checkpoint Trigger**: `[ADR-006 Tool-Call Limit (>=20) | Token Budget (>=40k) | Slice Complete | User Interrupt]`
- **Timestamp**: `YYYY-MM-DD HH:MM:SS UTC`

---

## 🎯 2. Goal & Intent Recap

- **Primary Objective**: Brief 1-2 sentence statement of what this work session set out to achieve.
- **Task Boundaries (Anti-Scope)**: Key restrictions preserved during this run (e.g. zero new top-level dirs, no absolute paths).

---

## ✅ 3. Completed Work in this Slice

List physical modifications performed during this session (deterministic proof over verbal claims):

| Action | Relative File Path | Concrete Modifications / Symbols |
| :--- | :--- | :--- |
| `[NEW]` | `services/dnk_media/api/router.py` | Added FastMCP endpoint `dnk_media_synthesize` |
| `[MODIFY]` | `core/orchestrator/swarm.py` | Updated agent dispatch router |
| `[DELETE]` | `services/dnk_legacy/` | Removed redundant legacy folder |

- **Key Commits Created**:
  - `<hash>`: `feat(domain): description of atomic slice`

---

## 🔍 4. Deterministic Verification Evidence (Machine Proof)

Never declare progress without physical execution evidence (`exit code 0`):

```bash
# Executed command:
./scripts/system/verify_all.sh --affected
# or
.venv/bin/pytest tests/path/to/test.py
```

- **Execution Verdict**: `[PASSED (exit code 0) | FAILED]`
- **Tests Passed**: `X passed in Y.YYs`
- **Cleanliness of Working Tree**: `git status -s` -> `clean`

---

## 🏛️ 5. Architectural Decisions Formulated

Record any decisions made during this session so the next agent does not guess or re-invent:

1. **Decision 1**: Description of why approach X was chosen over Y.
2. **Decision 2**: Configuration or contract parameters established.

---

## ⚠️ 6. Blockers, Open Debt & Hidden Risks

1. **Active Blockers**: Any external or tooling failures encountered.
2. **Technical Debt**: Anything temporary that requires cleanup in the next slice.
3. **Pre-Mortem Risk**: What could break if the next step is executed naively?

---

## 🚀 7. Immediate Next Action (First Step for Resuming Agent)

The resuming agent MUST follow this action-first instruction upon wakeup:

1. **Immediate Next Step**: The exact tool-call or script command to execute first.
2. **Next Slice Target File Whitelist**:
   - `path/to/file_1.py`
   - `path/to/file_2.py`
3. **Verification Command for Next Slice**:
   - `pytest tests/target/test_file.py`
