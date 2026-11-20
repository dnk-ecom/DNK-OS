---
title: "Dnk Taskdna Proposal Review Policy V1.0"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_TASKDNA_PROPOSAL_REVIEW_POLICY_v1.0.md"
> purpose: "Document: Dnk Taskdna Proposal Review Policy V1.0"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/DNK_TASKDNA_PROPOSAL_REVIEW_POLICY_v1.0.md"
> # purpose: "Human-in-the-loop Governance, Review & Approval Policy v1.0 for TaskDNA Proposals"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-09"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# DNK TaskDNA Proposal Review & Approval Policy v1.0

## 1. Executive Summary & Purpose

The **TaskDNA Proposal Review & Approval Policy** defines a non-bypassable, human-in-the-loop governance firewall within DNK OS.

Its sole directive:
> **No TaskDNA Proposal draft synthesized from Atomic Assimilation Blocks (DNK-AAB) may ever become an execution task, trigger an agent, mutate repository code, or invoke Swarm workflows without explicit, recorded human approval by Maxim (`maksym`).**

```text
┌───────────────────────┐
│  Atomic Assimilation  │
│     Blocks (AAB)      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   TaskDNA Proposal    │
│    (status: draft)    │ ◄── Immutable file in Git
└───────────┬───────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│             Human-in-the-Loop Review Gate              │
│                                                        │
│  [1] Technical Review     [2] Formal Rejection         │
│      (status: reviewed)       (status: rejected)       │
│                                                        │
│  [3] Explicit Approval                                 │
│      (status: approved, reviewer == 'maksym')          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Independent Review Records (Append-Only in Git)       │
│  docs/tech/taskdna_proposals/reviews/<proposal_id>/    │
│  ├── REVIEW-20260909T170000Z-technical-audit.yaml     │
│  └── REVIEW-20260909T180000Z-human-approval.yaml       │
└────────────────────────────────────────────────────────┘
```

---

## 2. Invariants & Zero-Execution Security Guarantees

1. **Zero Automatic Dispatch**:
   The creation or approval of a review record **NEVER** creates a live TaskForest task, does **NOT** spawn an orchestrator worker, and does **NOT** trigger background jobs.
2. **Immutability of Source Proposals**:
   The original proposal YAML file (`docs/tech/taskdna_proposals/<proposal_id>.yaml`) is strictly **read-only and immutable**. Its internal `status` field remains `draft`. Reviews are appended as independent audit artifacts.
3. **Sole Approval Authority**:
   Only the identity `"maksym"` is authorized to emit an `approved` decision. All other identities (including automated agents like `gerych_prime`) can emit only neutral technical assessments (`reviewed`) or recommendations.
4. **Mandatory Explicit Rationale**:
   Empty or whitespace-only rationales are strictly rejected by both Pydantic validation and CLI enforcement.
5. **Decoupled Task Execution**:
   Converting an approved proposal into an actionable TaskForest / TaskDNA task is a distinct, separate operational phase governed by manual operator intervention.

---

## 3. Proposal Lifecycle States

```text
    ┌──────────┐
    │  draft   │
    └────┬─────┘
         │
         ├───► [technical review] ───► reviewed (no execution authority)
         │
         ├───► [formal approval]  ───► approved (only if reviewer == 'maksym')
         │
         └───► [rejection]        ───► rejected (with documented rationale)
```

| Lifecycle State | Execution Allowed? | Authorized Roles | Mandatory Artifacts |
| :--- | :--- | :--- | :--- |
| **`draft`** | ❌ Strictly Prohibited | `aab_to_taskdna` | Proposal YAML file in `docs/tech/taskdna_proposals/` |
| **`reviewed`** | ❌ Strictly Prohibited | `maksym`, `gerych_prime`, Peer Reviewers | Review YAML with `decision: reviewed`, non-empty `rationale` |
| **`rejected`** | ❌ Strictly Prohibited | `maksym` | Review YAML with `decision: rejected`, non-empty `rationale` |
| **`approved`** | ⚠️ Authorized for planning only (no auto-exec) | `maksym` **ONLY** | Review YAML with `decision: approved`, `reviewer: maksym`, non-empty `rationale`, explicit `risks_accepted` |

---

## 4. Multi-Review Resolution Protocol

A proposal may accumulate multiple technical reviews and reassessments over its lifecycle.
The **Current Effective Decision** is resolved by the following deterministic algorithm:
1. Scan `docs/tech/taskdna_proposals/reviews/<proposal_id>/` for all valid review files conforming to `dnk-taskdna-proposal-review/v1.0`.
2. Order reviews chronologically by `reviewed_at` (ISO-8601 UTC timestamp).
3. The **latest valid review** dictates the proposal's current state:
   - If the latest review has `decision: approved`, the proposal is considered **Approved**.
   - If the latest review has `decision: rejected`, the proposal is considered **Rejected**.
   - If the latest review has `decision: reviewed`, the proposal remains in **Under Review** (non-executable).
   - If no reviews exist, the proposal remains in **Draft** state.

---

## 5. Storage & File Organization

All reviews are version-controlled in Git under repo-relative paths:
```text
docs/tech/taskdna_proposals/reviews/
└── <proposal_id>/
    └── REVIEW-<UTC-timestamp>-<slug>.yaml
```

Each review file contains:
- `schema_version`: `"dnk-taskdna-proposal-review/v1.0"`
- `review_id`: e.g. `TDR-20260909-human-approval`
- `proposal_id`: e.g. `TDP-20260909-research-to-taskdna-assimilation-workflow`
- `decision`: `reviewed` | `approved` | `rejected`
- `reviewer`: Identifier of the reviewer (e.g. `maksym`)
- `reviewed_at`: ISO-8601 UTC timestamp
- `rationale`: Explanation for the decision
- `risks_accepted`: List of documented risks accepted by the reviewer
- `conditions_before_execution`: Prerequisites to satisfy prior to any future task creation
- `linked_evidence`: Traceable paths to evidence notes, benchmark outputs, or audit reports
