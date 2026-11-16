# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/two_axis_review.md"
# purpose: "Reference guide for two-axis adversarial code review (Standards + Spec)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# ⚖️ Two-Axis Code Review (Standards vs Spec)

Assimilated from `mattpocock/skills/engineering/code-review`.

## 1. The Two Axes

### Axis 1: Standards Review
- Code style, naming conventions, type safety.
- MRH Header presence (`DNK-STD-0075`).
- Path hygiene (relative paths `./` and `../` only, zero `/Users/...`).
- Security invariants: no leaked tokens, no split-route bypasses, bounded inputs.
- Test coverage & non-tautological assertions.

### Axis 2: Spec Review
- Does the code actually fulfill the requested user intent?
- Are boundary conditions handled (empty inputs, network drops, timeouts)?
- Does it introduce unintended regressions or break adjacent modules?
- Are error messages informative and structured?

## 2. Swarm Review Execution
In DNK OS, this is executed via `gerych_auditor`:
- Red-Team Auditor vs Blue-Team Builder.
- Runs `bash scripts/verify_all.sh` as the deterministic pre-commit gate.
