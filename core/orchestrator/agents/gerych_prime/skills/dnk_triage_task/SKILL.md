---
name: dnk_triage_task
description: Autonomous complexity classifier and triage protocol before starting multi-file or multi-step tasks.
version: 1.0.0
author: "DNK-e.com Maksym"
metadata:
  hermes:
    tags: ["triage", "swarm", "complexity", "mase", "zero-waste"]
---

# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/dnk_triage_task/SKILL.md"
# purpose: "Autonomous complexity classifier and triage protocol before starting multi-file or multi-step tasks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# dnk_triage_task: Autonomous Complexity Classifier

## 1. Overview & Directive
`dnk_triage_task` is Step 0 of the Zero-Waste High-Velocity Protocol (ZWSP v2.5 / MASE).
It MUST be executed before any multi-file, multi-domain, or multi-step engineering task to classify execution complexity and prevent solo bottleneck exhaustion.

### Complexity Formula
$$C = F_{\text{files}} + (2 \times D_{\text{domains}}) + (3 \times S_{\text{stages}})$$

- $F_{\text{files}}$: Number of affected files.
- $D_{\text{domains}}$: Number of independent technical domains (e.g. backend, frontend, qa_security, ecom, media).
- $S_{\text{stages}}$: Number of sequential execution stages.

## 2. Routing Decisions

| Mode | Threshold | Action |
|------|-----------|--------|
| `SOLO` | $C \le 3$ | Execute directly as Gerych Prime, $\le 15$ tool calls per turn. |
| `SWARM_PARALLEL` | $C > 3$, $\ge 2$ independent domains | **IMMEDIATELY** dispatch workers via `dnk_swarm_parallel(tasks_json=...)` using the returned `execution_plan`. Solo file mutations are blocked by circuit breaker. |
| `SWARM_SEQUENTIAL` | $C > 3$, single domain with phases | Execute phased handoffs via `dnk_swarm_dispatch` with join barriers. |

## 3. Best Practices & Invariants
1. **Never loop on triage**: Run `dnk_triage_task(goal_or_prompt)` once at the beginning of the prompt.
2. **Obey parallel dispatch**: If `mode == 'SWARM_PARALLEL'`, the very next tool call MUST be `dnk_swarm_parallel`.
3. **Budget awareness**: Respect the 25-tool atomic slice budget (MASE).
