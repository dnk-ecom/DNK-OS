<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/phased_roadmap_tracking_and_task_note_sync_protocol.md"
purpose: "Protocol for real-time task note synchronization, phase status tracking, and verifiable metrics logging."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-15"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Phased Roadmap Tracking & Task Note Synchronization Protocol

## 🎯 Context & User Preference Invariant
When executing multi-phase roadmaps or structured refactorings, founder-level operational leverage requires continuous visibility and strict tracking. The agent must never proceed to subsequent phases or announce completion without immediately synchronizing the state in the dedicated task tracking note (e.g., `docs/notes/MY TASKS/YYYYMMDD/<phase_spec>.md`).

> **Rule**: After completing ANY phase or atomic slice, synchronously record the implementation details, hard metrics, and current project status in the corresponding task note BEFORE asking to proceed.

---

## 📋 The 4-Step Phase Synchronization Workflow

### 1. Hard Metric Verification First
Before updating the note, execute the targeted verification suite and collect hard numbers:
- Test collection status: `pytest --collect-only -q` (total tests collected vs errors).
- Targeted test run: `pytest <target_test_files> -v` (passed count, duration).
- Architecture & path hygiene: `bash scripts/verify_all.sh` or targeted preflight checks (0 absolute path violations).

### 2. Task Checklist Check-off (`[x]`)
In the active phase section of the task note:
- Change pending checkboxes `[ ]` to completed `[x]`.
- Append a concise 1-2 line summary of the exact root cause identified and the technical fix implemented.
- Include the verifiable gate result (e.g., `Gate Result: pytest --collect-only: 2,968 tests collected, 0 errors (+167 recovered)`).

### 3. Global Status & Trajectory Update
Update the status tracking section (Section 8 in `GERYCH_TASK_TEMPLATE.md`):
- **Current State**: Update from `Planned` or `In Progress` to `PHASE X COMPLETED (Ready for Phase X+1)`.
- **Verified Metrics**: Record the exact test counts, sanitized files, and path hygiene status.
- **Next Slice Target**: Explicitly declare the next scheduled phase according to the sequential plan ("все по черзі").

### 4. Transparent User Briefing
Present the user with:
1. Exact relative and absolute file paths to the updated tracking note.
2. Structured summary of what was physically executed (root cause -> fix -> metrics).
3. Clear prompt asking for confirmation to transition to the next phase.

---

## ⚠️ Pitfalls to Avoid
- **Narrative Claims without Note Sync**: Announcing in chat that a phase is done without updating the tracking file forces the user to manually verify if the note was maintained.
- **Unchecked Checkboxes**: Leaving `[ ]` markers in completed sections causes context confusion across agent handoffs and context window compactions.
- **Vague Statuses**: Writing "Tests pass" instead of `2,968 / 2,968 tests collected with 0 errors` violates Maxim's verifiable evidence invariant.
