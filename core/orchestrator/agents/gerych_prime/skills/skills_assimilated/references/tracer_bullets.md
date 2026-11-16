# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/tracer_bullets.md"
# purpose: "Reference guide for tracer-bullet decomposition and DAG task tickets."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🎯 Tracer-Bullet Task Decomposition (DAG Tickets)

Assimilated from `mattpocock/skills/engineering/to-tickets` and `to-spec`.

## 1. What is a Tracer Bullet?
A **tracer bullet** is a thin, end-to-end vertical slice of functionality through all layers of the architecture (CLI/UI -> Router -> Core Engine -> Storage).
- It is NOT a prototype (it is production-grade code).
- It is NOT an architectural layer (we don't build "all database models first", then "all endpoints").
- It proves the end-to-end plumbing immediately.

## 2. DAG Ticket Rules
Each decomposed ticket must define:
1. **Goal**: One clear observable outcome.
2. **Target File Whitelist**: Exact files touched.
3. **Negative Scope**: What this ticket explicitly will NOT do.
4. **Blocking Edges**:
   - `blocked_by`: IDs of prerequisite tickets that must be Green before starting.
   - `blocks`: IDs of tickets waiting on this one.
5. **Deterministic Verification**: Exact command (e.g. `pytest tests/...`) proving completion.

## 3. Integration with TaskDNA & Gerych Triage
- Run `dnk_decompose_task_dna(goal)` to produce the DAG tree.
- Tasks with no blocking prerequisites enter the **Ready Frontier** and can be dispatched in parallel via `dnk_swarm_parallel`.
- Limit each slice to ≤ 25 tool calls per turn to eliminate context exhaustion.
