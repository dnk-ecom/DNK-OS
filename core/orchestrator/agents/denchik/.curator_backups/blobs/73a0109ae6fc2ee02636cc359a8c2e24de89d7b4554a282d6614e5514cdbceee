# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/scope_clamping_and_autonomy_tiering_protocol.md"
# purpose: "Scope Clamping, 4-Tier Autonomy Ladder, Pre-Execution Effort Estimation, and Hype Deconstruction."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-22"
# author: "DNK Swarm & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🗜️ Scope Clamping & Autonomy Tiering Protocol

## 1. 4-Tier Autonomy Ladder

When evaluating or designing multi-agent agentic workflows, always map the task to the lowest sufficient autonomy tier to prevent token bloat and ungrounded execution loops:

| Tier | Name | Mechanism | Primary Use Case | Risk / Overhead |
|------|------|-----------|------------------|-----------------|
| **Level 1** | **Solo + Subagents** | Ephemeral, isolated subagent dispatch (`delegate_task`, `dnk_swarm_parallel`). | Parallel lookups, isolated refactors, multi-domain generation. | Low overhead; transient lifetime. |
| **Level 2** | **Goal Loops** | Agent loop with deterministic exit criteria (`exit code 0`, schema validation). | Bug fixing, TDD cycles, test-driven validation. | High risk of infinite loop if exit condition is conversational. |
| **Level 3** | **Bot Mode / Profiles** | Persistent specialized agents with isolated SOUL, memory, and pruned toolsets (<6k tokens). | Dedicated domain specialists (`dnk_shopify`, `dnk_dev_fullstack`). | Setup overhead; needs strict sandboxing. |
| **Level 4** | **Async Kanban / DAG** | Persistent task boards with dependency DAGs, state persistence, and background execution. | Complex multi-stage roadmaps, long-running batch migrations. | Highest complexity; requires persistent DB and recovery. |

---

## 2. Scope Clamping Cheat Code

### The Problem
Generic multi-agent planners inflate prompts and spawn redundant workers (e.g. 2 researchers and 2 planners for a simple task), multiplying token burn by 2x-3x (e.g. 45,000+ tokens) without adding quality.

### The Rule: Clamp Before Dispatch
Every task assigned to a subagent or decomposed into TaskDNA MUST include explicit numerical clamps:
1. **Source Clamp**: Max N sources/URLs to inspect (e.g. `max_sources = 3..5`).
2. **Output Budget**: Strict length/token ceiling (e.g. `max_words = 500` or `limit: 80 lines`).
3. **Module Barrier**: Explicit `target_files` whitelist and `negative_scope` (strictly forbidden files).
4. **Deduplication Gate**: Forbid spawning duplicate agents of the same domain in the same tier.

*Empirical Result*: Scope clamping reduces token expenditure by 50%–65% and drops complexity classification from High to Medium/Low.

---

## 3. Pre-Execution Effort & Cost Estimation

Before running multi-worker pipelines or heavy autonomous cycles:
1. **Lightweight Triage**: Run Step 0 evaluation (`dnk_triage_task`) using a fast, low-cost model.
2. **Token & Budget Prediction**: Calculate estimated prompt + generation tokens and USD cost.
3. **SpendGuard Gate**: If estimated tokens exceed the workspace limit (e.g. >25,000 tokens for a non-epic task), halt and auto-apply Scope Clamping before requesting execution approval.

---

## 4. Hype Deconstruction Protocol for Media & External Claims

When auditing external technical videos, tutorials, or marketing releases:
1. **Filter Out**:
   - Marketing buzzwords, sponsored memberships, and paid template paywalls.
   - Verbal self-reporting ("the agent built an entire SaaS app in 10 minutes").
   - Multi-agent theatre (showing 5 agents conversing when a single script would suffice).
2. **Extract & Verify**:
   - Hard architectural mechanisms (runtime hooks, protocol schemas, process isolation).
   - Concrete cheat codes in development (speedups, token reductions, tooling tricks).
   - Commercializable positioning (cost transparency, human-in-the-loop workflows).

---

## 5. Cheat Codes in Marketing & Sales for Agentic Systems

1. **3-Stage Content Factory (Researcher -> HITL -> Copywriter)**:
   - Step 1: Agent gathers hard facts, data points, and competitive benchmarks.
   - Step 2: Human expert adds personal voice, strategic framing, and contrarian angles.
   - Step 3: Agent formats for multi-channel distribution. Eliminates generic AI boilerplate.
2. **Predictable Cost Estimator as B2B Offer Hook**:
   - Clients fear open-ended API bills. Displaying pre-execution cost guarantees (e.g. "$0.04 and 30s") converts cautious B2B buyers into paying users.
3. **Live Steering as Trust Engine**:
   - Providing mid-execution steering (out-of-band operator feedback) removes the "black box" fear and dramatically increases retention.
4. **4-Tier Value Pricing**:
   - Package services aligned with the Autonomy Ladder: Tier 1 (Assistant), Tier 2 (Guaranteed Goal Loop), Tier 3 (Dedicated Virtual Specialist), Tier 4 (Autonomous Swarm Studio).
