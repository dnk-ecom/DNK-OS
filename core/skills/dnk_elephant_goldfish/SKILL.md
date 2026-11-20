---
title: "DNK Elephant-Goldfish Review Protocol (EGM)"
name: dnk_elephant_goldfish
description: "Use when designing, drafting, or reviewing non-trivial architecture specs, ADRs, or complex features. Implements Google's Elephant-Goldfish Model (EGM) dual-system review protocol."
category: architecture
tags:
  - architecture
  - spec-driven-development
  - multi-agent-review
  - zero-context-audit
  - epistemic-armor
created: 2026-10-27
updated: 2026-10-27
version: "1.0.0"
status: active
domain: core
author: "DNK-e.com Maksym & Gerych Prime"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/dnk_elephant_goldfish/SKILL.md"
> purpose: "Operational workflow for Google Elephant-Goldfish Model (EGM) dual-system review inside DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: ["TASK-DNK-AUDIT-EGM-20261027-001"]
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-10-27"
> author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```
> > [!summary] 📋 Контекст для ШІ-агента
> > Операційний скіл контуру рев'ю Elephant-Goldfish Model (EGM).

# 🐘🐟 DNK Elephant-Goldfish Review Protocol (EGM)

## 📌 Overview
The Elephant-Goldfish Model (EGM) separates **deep-context spec exploration** from **zero-context isolated review**.
- **The Elephant (Deep Context)**: `dnk_mentor` (Antigravity) & Gerych Prime hold project history, user intent, and codebase maps.
- **The Goldfish (Zero-Context Swarm)**: Isolated subagents dispatched via `delegate_task` with zero dialogue history. They review the written specification against strict rubrics, eliminating hallucination cascades and sycophantic confirmation bias.
- **The Human (Maxim)**: Makes strategic trade-offs, dismisses out-of-scope nits, and locks architecture before code synthesis.

---

## ⚡ Core Invariants & Rules
1. **Artifact-First Protocol (Anti-Chat Dump)**: All specs, ADRs, and designs MUST be written directly to workspace files (`specs/*.md`, `docs/designs/*.md`). Never dump raw multi-page specs into conversation turns.
2. **Zero-Context Isolation**: Goldfish subagents MUST NOT receive dialogue history. They receive ONLY the target spec path, related schemas/contracts, and specific evaluation criteria.
3. **Phase-1 Zero-Write Barrier**: No code files (`apps/`, `services/`, `core/`) may be written until the spec passes Goldfish review with **0 Blockers** and a consensus score of **≥ 4.0 / 5.0**.
4. **Epistemic Armor Enforcement**: Reviewers are forbidden from sycophantic praise tokens (per AGENTS.md Section 6). Evaluations must lead with the concrete verdict and list failure conditions first.

---

## 🛠️ Step-by-Step EGM Review Workflow

### Step 1: Elephant Spec Drafting (Artifact-First)
- Engage `dnk_mentor` (Antigravity) or Gerych Prime to explore requirements and customer user journeys (CUJs).
- Write the draft specification to `specs/<SPEC_NAME>.md` adhering to `docs/templates/Do not Delete - Example.md`.
- Ensure the document includes:
  * Section 1: Mermaid Architecture Topology (`%%{init: {'theme': 'base', ...}}%%`).
  * Section 2: Human Intent & Target Scenarios.
  * Section 3: Machine Contract, Target File Whitelist, and Negative Scope.
  * Section 4: MASE Slices (≤ 25 actions/slice) and Acceptance Matrix.

### Step 2: Dispatch Isolated Goldfish Subagents (Parallel Review)
Dispatch 4 independent leaf subagents using `delegate_task(role="leaf")`. Each runs in a clean context:

```python
# 1. Zoom Out Critic (YAGNI, Simplicity, Codebase Reuse)
delegate_task(
    role="leaf",
    goal="Audit spec for YAGNI, unnecessary abstractions, and codebase reuse.",
    context="Spec file: specs/<SPEC_NAME>.md. Check if similar utilities exist in core/ or services/. Flag over-engineering."
)

# 2. Comprehension Auditor (Self-Containment & Naive Reader)
delegate_task(
    role="leaf",
    goal="Audit spec for clarity, missing definitions, and implicit assumptions.",
    context="Spec file: specs/<SPEC_NAME>.md. Assume no prior project knowledge. Identify ambiguous requirements."
)

# 3. Design Critic (Failure Modes, Scale, Bottlenecks, Quotas)
delegate_task(
    role="leaf",
    goal="Adversarial stress-test: identify failure modes, memory leaks, API quota limits, and security vectors.",
    context="Spec file: specs/<SPEC_NAME>.md. Focus on scale (100x), retry logic, and error handling."
)

# 4. Implementation Readiness (Actionability, Signatures, File Mappings)
delegate_task(
    role="leaf",
    goal="Audit implementation readiness: verify exact file paths, schemas, and deterministic test assertions.",
    context="Spec file: specs/<SPEC_NAME>.md. Answer: Can an engineer implement this without asking clarifying questions?"
)
```

### Step 3: Synthesis & Triaged Reporting
The Synthesizer (`gerych_auditor`) consolidates findings into a structured report:
- **Deduplication**: Merge identical observations across reviewers.
- **Severity Classification**:
  * 🔴 **Blocker**: Architectural flaw, missing contract, invariant breach. Halts progress.
  * 🟡 **Major**: Unhandled edge case, performance concern. Must be resolved before commit.
  * 🟢 **Nit**: Stylistic preference, comment clarity. Optional.
- **Dimension Scoring (1–5)**:
  1. *Architecture & Soundness*
  2. *Implementation Feasibility*
  3. *Long-term Maintainability*
  4. *Strategic Alignment*

### Step 4: Resolution & Quality Gating
1. If **Score < 4.0** or **Blockers > 0**: Return to Step 1. The Elephant patches `specs/<SPEC_NAME>.md`.
2. If **Score ≥ 4.0** and **Blockers == 0**: Present final summary to Human Architect (Maxim).
3. Upon human approval: Lock decision in `docs/architecture/DECISION_REGISTRY_ADHD.md` and proceed to Phase 2 (MASE Code Synthesis).

---

## 📊 Rubrics & Scoring Standards
| Score | Status | Action Required |
| :---: | :--- | :--- |
| **5.0** | Flawless | Ready for immediate implementation. |
| **4.0 - 4.9** | Approved with Nits | Minor revisions; proceed to implementation. |
| **3.0 - 3.9** | Revise & Resubmit | Major architectural gaps or ambiguous contracts. |
| **< 3.0** | Rejected | Fundamental redesign required by Elephant. |

---

## 🛡️ Verification Command
```bash
# Validate that the generated spec strictly conforms to DNK standards
python3 scripts/system/doc_standard_guardian.py --file specs/<SPEC_NAME>.md
```
