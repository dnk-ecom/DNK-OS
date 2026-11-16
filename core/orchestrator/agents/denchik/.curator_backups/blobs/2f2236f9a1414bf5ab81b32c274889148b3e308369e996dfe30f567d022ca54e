<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/bulletproof_task_formulation_and_v3_spec_protocol.md"
purpose: "Bulletproof Task Formulation Protocol v3.0: 5 Golden Laws, Anti-Scope Hygiene, Algorithmic Pseudocode & Dual-Optics Swarm Execution Gate"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "3.0.0"
updated_at: "2026-09-09"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🛡️ Bulletproof Task Formulation Protocol v3.0 (SPEC-TASK-003)

## 1. Executive Context & Invariant
When the human visionary or lead architect provides a task (like `DNK-AAB Foundation v0.1`), autonomous agents often suffer from **Context Window Bloat**, **Tool Budget Exhaustion (90/90)**, **Algorithmic Hallucinations** in edge cases, and **Scope Drift**.
This protocol formalizes the **5 Golden Laws of Task Formulation**, distilled directly from the comprehensive audit of DNK OS task specifications and agent execution patterns.

## 2. The 5 Golden Laws of Bulletproof Tasks

```text
[Human / Architect Vision]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│ 1. ANTI-SCOPE FIRST (Negative Boundaries)              │
│    - Explicit list of forbidden paths & actions        │
│    - Eliminates destructive refactoring & drift        │
├────────────────────────────────────────────────────────┤
│ 2. STRICT FILE WHITELIST                               │
│    - Explicit paths for [NEW] and [MODIFY]             │
│    - Hard block on ad-hoc helper/util sprawl           │
├────────────────────────────────────────────────────────┤
│ 3. PRE-DECLARED INTERFACES & ALGORITHMIC PSEUDOCODE    │
│    - Complete signatures for models, classes, methods  │
│    - Explicit pseudocode for boolean / filter logic    │
├────────────────────────────────────────────────────────┤
│ 4. TOOLCHAIN & ENVIRONMENT PRECONDITIONS (SSOT)        │
│    - Python 3.12, .venv, pre-installed libraries       │
│    - Zero-guessing on Pydantic vs Schema SSOT          │
├────────────────────────────────────────────────────────┤
│ 5. PHASED MASE SLICING (≤25 Tools/Turn) + DUAL-OPTICS   │
│    - 4 micro-phases: Contracts → Core → CLI → Evidence │
│    - Terminal text for humans + JSON/MRH for machines  │
└────────────────────────────────────────────────────────┘
```

### Law 1: Anti-Scope First (Negative Scope / Forbidden Actions)
Never rely on an agent to deduce boundaries. Put forbidden actions prominently near the top of the task:
- What databases or files MUST NOT be mutated (e.g. `catalog.db`).
- What core modules or orchestrators MUST NOT be touched.
- What automation MUST NOT be built in this slice (e.g. "Do NOT build auto-task creation from AAB").

### Law 2: Strict File Whitelist (No Scope Drift)
Enumerate every single target file explicitly.
- If an artifact is not in the whitelist, the agent is forbidden from creating it.
- Prevents random `utils.py`, `helpers.py`, or unreviewed configuration files.

### Law 3: Pre-declared Interface Contracts & Algorithmic Invariants (Pseudocode)
When a task includes filtering, deduplication, conflict resolution, or graph traversal:
- Never leave boolean rules ambiguous (e.g. "exclude conflicts").
- Provide 3–5 lines of deterministic pseudocode.
- Define whether conflict checks are bidirectional:
  ```python
  # Bidirectional Conflict Invariant:
  # Candidate C is rejected if C.id in Selected.conflicts_with OR Selected.id in C.conflicts_with
  ```

### Law 4: Toolchain Preconditions & Single Source of Truth (SSOT)
Clarify environment and dependency constraints up front:
- Python version (`3.12+`), virtual environment path (`./.venv/bin/python`).
- Existing vs missing libraries (e.g. `pydantic>=2.0`, `pyyaml`, `jsonschema`).
- Explicitly resolve dual-layer ambiguities:
  - When both JSON Schema and Pydantic models are requested, state: *"Pydantic v2 is the runtime SSOT; JSON Schema is the external serializable contract."*

### Law 5: Phased MASE Slicing (≤ 25 Tools per Turn) & Dual-Optics Verification
Monolithic 16-file tasks cause context fragmentation. Slice the task into 4 sequential checkpoints:
1. **Phase 1: Contracts & Fixtures** (Schema YAML, Example YAML, Pydantic Models).
2. **Phase 2: Core Engine** (Parser, Registry, Core Unit Tests).
3. **Phase 3: CLI & Adapters** (CLI Scripts, Human-readable formatting, E2E Tests).
4. **Phase 4: Evidence & Knowledge Harvesting** (Obsidian Note with MRH/wikilinks, Evidence JSON).

## 3. Human CLI Output Contract
Always define the human-readable terminal output format alongside `--json`:
```text
Human-Readable Format:
[<ID>] <Title> | domain: <domain> | score: <score> | status: <status>
```
This prevents agents from over-engineering unreadable tables or dumping raw objects to stdout.

## 4. Cross-References
- Canonical Task Template: `docs/templates/GERYCH_TASK_TEMPLATE.md` (v3.0)
- Knowledge Note: `docs/notes/127_bulletproof_task_formulation_standard_and_agentic_workflow.md`
- Mentor Intake Protocol: `references/chief_architect_mentor_and_human_task_intake_protocol.md`
