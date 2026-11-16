# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/task_dna_lifecycle_and_live_canvas_hud_protocol.md"
# purpose: "TaskDNA Lifecycle Engine & Live Obsidian Canvas HUD Protocol (Anti-Poisoning & Worktree Invariants)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🧬 TaskDNA Lifecycle Engine & Live Obsidian Canvas HUD Protocol

## 1. Context & Architectural Mission
Operationalizes the **Anti-Poisoning State Machine** and **Real-Time Visual Swarm HUD** (`core/orchestrator/task_dna_lifecycle.py`), connecting autonomous subagents, audit gates, human founder approval, and knowledge ingestion into a tamper-proof pipeline visualized on Obsidian JSON Canvas 1.0.

---

## 2. Finite State Machine & Role Invariants

The lifecycle strictly enforces the following transition sequence:

```
[RESEARCH_RAW]  (Author: gerych_researcher)
       │
       ▼ submit_for_audit
  [AUDIT_GATE]   (Auditor: gerych_auditor, SecurityGateResult: PASSED / QUARANTINED)
       │
       ▼ founder_signoff
[FOUNDER_APPROVAL] (Founder: Maxim / Antigravity, Decision: APPROVED / REJECTED)
       │
       ▼ complete_librarian_ingest
[LIBRARIAN_INGEST] (Librarian: herich_librarian, Destination: docs/notes/<NNN>_<slug>.md)
       │
       ▼
  [COMPLETED]
```

### Critical Security Rule: Zero-Direct-Memory-Write (ZDMW)
- `RESEARCHER` cannot transition tasks directly to `LIBRARIAN_INGEST` or `COMPLETED`.
- Attempting unauthorized jumps or transitions without prior gate passage raises `LifecycleSecurityViolation`.
- If an audit fails (`QUARANTINED` / `FAILED`), the task is immediately transitioned to `REJECTED` and quarantined from production memory stores.

---

## 3. Real-Time Canvas HUD Synchronization (`Swarm_Live_HUD.canvas`)

The engine generates and refreshes Obsidian JSON Canvas 1.0 diagrams via `sync_to_canvas(output_path)`:
- **Columns & Spatial Geometry**:
  - `RESEARCH_RAW`: $x = 0$, Group Color `2` (Orange)
  - `AUDIT_GATE`: $x = 360$, Group Color `6` (Cyan)
  - `FOUNDER_APPROVAL`: $x = 720$, Group Color `5` (Purple)
  - `LIBRARIAN_INGEST / COMPLETED`: $x = 1080$, Group Color `4` (Green)
  - `REJECTED / QUARANTINED`: $x = 1440$, Group Color `1` (Red)
- **Node Structure**: Formatted markdown card with task title, domain badge, author, audit status, and security token.
- **Edges**: Bidirectional or unidirectional arrow edges mapping dependencies (`depends_on`).

---

## 4. Operational Code Recipe

```python
from core.orchestrator.task_dna_lifecycle import (
    TaskDNALifecycleEngine,
    AgentRole,
    SecurityGateResult,
    LifecycleSecurityViolation,
)

# 1. Initialize engine with persisted database
engine = TaskDNALifecycleEngine(db_path="docs/notes/Canvas/swarm_tasks_db.json")

# 2. Researcher creates raw task
task = engine.create_task(
    title="SOTA Assimilation",
    domain="research",
    author="gerych_researcher",
    description="Analyze AST patterns and license compatibility",
)

# 3. Submit for audit gate
engine.submit_for_audit(task.id, actor_role=AgentRole.RESEARCHER)

# 4. Auditor validates security and license
engine.record_audit_result(
    task.id,
    actor_role=AgentRole.AUDITOR,
    result=SecurityGateResult.PASSED,
    report_file="docs/reports/AUDIT-001.md",
)

# 5. Founder sign-off
engine.founder_signoff(
    task.id,
    actor_role=AgentRole.FOUNDER,
    approved=True,
    notes="Approved for ingestion",
)

# 6. Librarian archives into Obsidian Vault
engine.complete_librarian_ingest(
    task.id,
    actor_role=AgentRole.LIBRARIAN,
    vault_note_path="docs/notes/177_example.md",
)

# 7. Render Live Canvas HUD
engine.sync_to_canvas("docs/notes/Canvas/Swarm_Live_HUD.canvas")
```

---

## 5. Pitfalls & Troubleshooting

1. **`validate_json_canvas` Return Contract**:
   - `core/obsidian/json_canvas_builder.py:validate_json_canvas(data)` returns a 2-tuple: `(is_valid: bool, errors: list[str])`.
   - Never access `result.is_valid`; unpack with `is_valid, errors = validate_json_canvas(...)`.

2. **Root Hygiene Guard on Auxiliary Dirs (`.worktrees/`)**:
   - `scripts/system/root_hygiene_guard.py` asserts the strict 8-root directory whitelist.
   - Creating `.worktrees/` in `$HUB_ROOT` trips the hygiene check immediately. Always configure Git worktrees in `.git/worktrees/` or prune stale worktrees before running the gate.

3. **Virtualenv Execution Boundary**:
   - Always run engine scripts and tests using `.venv/bin/python` to ensure Pydantic v2 schemas and JSON Canvas builders are resolved properly.
