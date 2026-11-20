---
title: "Dnk Canvas Human In The Loop Approval V0.1"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_CANVAS_HUMAN_IN_THE_LOOP_APPROVAL_v0.1.md"
> purpose: "Document: Dnk Canvas Human In The Loop Approval V0.1"
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
> # mrh_id: "docs/architecture/specs/DNK_CANVAS_HUMAN_IN_THE_LOOP_APPROVAL_v0.1.md"
> # purpose: "Technical Specification for Canvas Human-in-the-Loop Approval MVP v0.1 (CANVAS-004)"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "0.1.0"
> # updated_at: "2026-09-10"
> # author: "DNK-e.com Maksym / Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# Canvas Human-in-the-Loop (HITL) Approval MVP Specification v0.1

## 1. Overview & Objectives

In the DNK OS Spatial Canvas Control Plane, autonomous agents and collaborative operators propose operations on the canvas graph. While routine layout adjustments and node additions can proceed automatically, high-impact or destructive operations must be intercepted by a Human-in-the-Loop (HITL) approval gate before mutation of `CanvasState`.

This specification formalizes the minimal HITL approval data models, evaluation rules, and persistence mechanics for `CANVAS-004`.

## 2. Invariants & Scope Boundaries

1. **Non-Invasive Architecture**:
   - Zero modifications to `CanvasControlPlane`, `OCC 3-Way Merge`, or `CanvasMessage` protocol.
   - Zero UI/Frontend components.
   - Zero live WebSocket or network socket dependencies.
   - Zero external services, secrets, or active plugin executions.
2. **Path Hygiene**:
   - Strictly relative path operations (`./`, `../`). Absolute system paths are rejected with `ValueError`.
3. **Fail-Safe Gate**:
   - Critical operations default to `status: "pending"` and require explicit approval by the designated approver (`maksym`) prior to execution.

## 3. Data Models

### 3.1 ApprovalRequest

```yaml
ApprovalRequest:
  request_id: "<uuid>"
  created_at: "<iso-8601-utc>"
  canvas_id: "<target-canvas-id>"
  operation_type: "canvas.node.remove"
  operation_payload: {}
  requester_id: "gerych_prime"
  approver_id: "maksym"
  status: "pending" # pending | approved | rejected
  reason: null
```

### 3.2 ApprovalHistoryEntry

```yaml
ApprovalHistoryEntry:
  request_id: "<uuid>"
  decided_at: "<iso-8601-utc>"
  approver_id: "maksym"
  decision: "approved" # approved | rejected
  reason: null
  canvas_id: "<target-canvas-id>"
  operation_type: "canvas.node.remove"
```

## 4. Operation Classification & Approval Rules

An operation requires human approval if it matches any of the following critical classifications:

| Operation Type | Condition | Action |
|---|---|---|
| `canvas.node.remove` | Any removal of a plugin/action node | Intercept -> Requires Approval |
| `canvas.edge.remove` | Any deletion of dependency/connector edge | Intercept -> Requires Approval |
| `canvas.state.reset` | Full graph purge or state wipe | Intercept -> Requires Approval |
| `canvas.node.move` | Movement with delta > 500px or `critical: true` | Intercept -> Requires Approval |
| `canvas.node.add` | Routine node spawn | Auto-permit (No approval needed) |
| `canvas.edge.add` | Routine edge connection | Auto-permit (No approval needed) |
| `canvas.node.update` | Metadata or label update | Auto-permit (No approval needed) |

## 5. Storage Contract

Approvals are stored in append-only JSONL files under relative paths:
- **Pending Requests**: `templates/canvas/approvals/pending_approvals.jsonl`
- **Decision History**: `templates/canvas/approvals/approval_history.jsonl`

## 6. CLI Interface

The CLI tool `scripts/system/canvas_approval.py` exposes:
1. `request`: Submits an approval request for evaluation.
2. `list-pending`: Enumerates pending approvals.
3. `decide`: Records an approval or rejection.
4. `history`: Reviews audit trail of decisions.
