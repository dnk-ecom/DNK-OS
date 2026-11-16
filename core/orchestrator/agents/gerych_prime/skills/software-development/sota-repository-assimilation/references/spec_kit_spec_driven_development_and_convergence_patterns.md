# Spec Kit: Spec-Driven Development (SDD), Governance & Convergence Patterns

## Overview
Assimilated patterns from GitHub (`github/spec-kit`, 138k+ ⭐, MIT License).
Spec Kit introduces Spec-Driven Development (SDD), where code is strictly subordinate to iterative, human-supervised specifications. It bridges the gap between high-level intent, architectural constraints, and deterministic execution.

## Core Architectural Invariants

### 1. Inversion of Power: Code Serves Specs
- Traditional agent development: Prompt -> Code -> Prompt Patch -> Code Churn.
- Spec-Driven Development:
  1. `Constitution`: Fundamental principles, architecture standards, quality invariants.
  2. `Specify`: Goal, User Stories, Acceptance Criteria (Functional & Non-Functional).
  3. `Plan`: Technical stack, schemas, API contracts, architectural boundaries.
  4. `Tasks`: Atomic task DAG with explicit dependencies and verification criteria.
  5. `Implement`: Atomic code synthesis per task.
  6. `Converge`: Automated AST & test reconciliation until code matches spec.

### 2. The Convergence Loop (`/speckit-converge`)
- Continuous reconciliation process:
  - Compares generated code against the Acceptance Criteria defined in `Specify` and `Plan`.
  - Flags specification drift, phantom features, or missing edge-case handling.
  - Generates delta remediation tasks until 100% convergence is proven by machine tests.

### 3. Isolated Workflows: Bug Fixing & Idea Assessment
- **Bug Fixing Sub-Protocol**:
  - `Assess`: Reproduce bug, capture stack trace, identify boundary condition failure.
  - `Fix`: Minimal atomic patch strictly targeting root cause.
  - `Test`: Deterministic regression test guaranteeing zero regressions.
- **Idea Assessment Protocol**:
  - `Intake` -> `Research` -> `Define` -> `Shape` -> `Decide`.
  - Enforces Pre-Mortem and Skeptic Alternatives before code commits.

## DNK OS Assimilation & Mapping

| Spec Kit Concept | DNK OS Native Implementation | Agent Owner |
|---|---|---|
| `constitution.md` | `AGENTS.md` + `core/orchestrator/agents/*/SOUL.md` | `dnk_mentor` (Antigravity) |
| `specify.md` | `dnk_intent_discovery` + `docs/templates/GERYCH_TASK_TEMPLATE.md` | `gerych_prime` |
| `plan.md` | `dnk_decompose_task_dna` (TaskDNA DAG) | `gerych_prime` |
| `tasks.md` | TaskForest atomic slices (MASE protocol <=25 tools) | `gerych_prime` |
| `implement.md` | Swarm execution (`gerych_builder`, `dnk_dev_fullstack`, `dnk_shopify`) | Domain Workers |
| `converge.md` | Master Quality Gate (`verify_all.sh`) + `gerych_auditor` review | `gerych_auditor` |

## Pitfalls & Epistemic Armor Countermeasures
1. **Specification Bloat**: Do not allow specifications to grow into unmaintainable multi-thousand-line documents. Scope every spec to an atomic slice (<= 150 lines per spec).
2. **Tautological Convergence**: Never accept conversational convergence declarations ("It matches the spec!"). Demand deterministic machine proof (`pytest`, `tsc`, `exit code 0`).
3. **Overhead Latency**: For single-file fixes, bypass the full 5-stage spec ceremony using the fast-path Bug Fix protocol (`assess -> fix -> test`).
