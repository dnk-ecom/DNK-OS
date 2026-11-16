# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/mvr_canvas_frontend_sse_hitl_wiring.md"
# purpose: "Reference architecture for Next.js 14 / XYFlow frontend wiring with resilient W3C SSE streaming, Zustand store, and 1-Click HITL node controls."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Next.js 14 / XYFlow Frontend Wiring: SSE Streams & 1-Click HITL Node Controls

## Overview
This reference specifies the client-side integration architecture connecting Next.js 14 and XYFlow (ReactFlow v11+) to the MVR Core backend via resilient Server-Sent Events (SSE) and Human-in-the-Loop (HITL) approval gateways.

---

## 1. W3C Resilient SSE Stream Client (`mvr_stream_client.ts`)
- **Transport**: Native browser `EventSource` listening to `/api/v1/mvr/stream`.
- **Reconnection with Backoff**:
  - Automatically caches the latest event ID into `sessionStorage` (`mvr_last_event_id`).
  - Appends `?last_event_id=<id>` on reconnect so the server replays missed ring-buffer history.
  - Implements exponential backoff: $T_{backoff} = \min(1000 \times 1.5^n, 30000)$ ms.
- **Lifecycle Envelope**:
  - Typed envelopes (`MvrEventEnvelope`) carrying `event_id`, `event_type`, `timestamp`, `source_agent`, and `payload`.
  - Dispatches typed handlers: `TASK_DISPATCHED`, `TASK_STEP_PROGRESS`, `WAITING_APPROVAL`, `APPROVAL_RESOLVED`, `TASK_COMPLETED`, `TASK_FAILED`, `CANVAS_NODE_MOVED`.

---

## 2. Zustand Canvas Store (`mvrCanvasStore.ts`)
- **State Model**:
  - `nodes: Node<AgentTaskData>[]`: XYFlow nodes representing swarm subtasks.
  - `edges: Edge[]`: Dependency and action bus connections.
  - `pendingApprovals: HitlApprovalRequest[]`: Active HITL queue requiring operator intervention.
  - `activeDrawerApprovalId: string | null`: Selected approval inspected in operator drawer.
  - `streamStatus: 'connecting' | 'connected' | 'disconnected' | 'error'`.
- **Optimistic UI with Failure Rollback**:
  - Operator clicks "Approve" / "Reject".
  - Store immediately transitions the local node status to `RUNNING` or `REJECTED` and removes the request from `pendingApprovals`.
  - If the REST POST (`/api/v1/mvr/hitl/decision`) rejects or times out, the store automatically reverts node status back to `WAITING_APPROVAL` and restores the item into `pendingApprovals`.

---

## 3. Spatial Custom Nodes: `AgentTaskNode` (`AgentTaskNode.tsx`)
- **XYFlow Node Registration**:
  - Registered in `NodeRegistry.ts` / `CanvasEngine.tsx` as `agentTask: AgentTaskNode`.
- **Agent Badge & Color Invariants**:
  - `gerych_builder`: Indigo theme (`#6366f1`).
  - `dnk_shopify`: Emerald theme (`#10b981`).
  - `dnk_dev_fullstack`: Amber theme (`#f59e0b`).
  - `gerych_auditor`: Rose theme (`#f43f5e`).
- **Live Status Pulsing**:
  - `WAITING_APPROVAL`: Amber badge with continuous CSS radar pulse (`animate-ping`).
  - `RUNNING`: Blue/Indigo badge with rotating spinner.
  - `COMPLETED`: Green check badge.
  - `FAILED`: Red alert badge.
- **1-Click Inline Action Controls**:
  - Embedded inside the node card: "Approve" (green) and "Reject" (red) buttons directly callable without opening modal dialogs for fast-path operational flow.
  - "Inspect Diff" button opens `HitlApprovalDrawer` for deep scrutiny of blast radius.
- **Defensive Data Normalization Invariant**:
  - Initial nodes, template definitions, and deserialized graphs may omit fields like `taskId` or swap keys (`agent` vs `targetAgent`).
  - Custom nodes MUST normalize `data` at top of component:
    ```tsx
    const rawData = (data || {}) as Record<string, any>;
    const nodeData = {
      ...rawData,
      taskId: rawData.taskId || id || 'task-unknown',
      targetAgent: rawData.targetAgent || rawData.agent || 'gerych_prime',
      title: rawData.title || 'Agent Task',
    };
    ```
  - Defensive rendering: `{(nodeData.taskId || id || 'task').slice(0, 8)}`. Never call `.slice()` or `.toLowerCase()` on unchecked raw properties.

---

## 4. Operator Inspection: `HitlApprovalDrawer` (`HitlApprovalDrawer.tsx`)
- **Drawer Panels**:
  - Blast Radius summary (target module, affected files count).
  - Safety level badge (`sandboxed` vs `live_environment`).
  - Artifacts inspector showing generated code or configuration diffs.
  - Rejection rationale input for structured human feedback to agents.

---

## 5. Verification & Testing Patterns
- **Path Hygiene**: Ensure zero absolute paths (`/Users/...`) in TypeScript/TSX code.
- **SSR Safety**: Wrap `sessionStorage` and `EventSource` in `typeof window !== 'undefined'` guards.
- **Mocking SSE in Jest/Vitest**: Mock `global.EventSource` with simulated `onmessage` and `onerror` dispatchers.
