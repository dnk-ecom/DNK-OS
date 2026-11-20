---
title: "Dnk Os Harness Integration V1.0"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_OS_HARNESS_INTEGRATION_v1.0.md"
> purpose: "Document: Dnk Os Harness Integration V1.0"
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
> # mrh_id: "docs/architecture/specs/DNK_OS_HARNESS_INTEGRATION_v1.0.md"
> # purpose: "Technical Specification for DNK OS Harness Integration v1.0 unifying Plugin Governance and Canvas Control into a single orchestration layer."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-10"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌐 DNK OS Harness Integration Specification v1.0

> **Status:** Active / Integration Specification v1.0
> **Scope Identifier:** `INTEGRATION-001`
> **Target Release:** DNK OS MVP Architecture (MVR)
> **Authors:** Maksym Kuzmenko (Founder) & Gerych Prime (Chief Builder)

---

## 1. Executive Summary & Objectives

The **DNK OS Harness Integration v1.0** defines the authoritative orchestration specification connecting the **Plugin Governance Subsystem** (ingestion, certification, registry, capability graph, deterministic execution, audit logging, and health monitoring) with the **Canvas Control Plane Subsystem** (spatial visual nodes, OCC 3-way conflict resolution, real-time message protocol, and human-in-the-loop approval gates).

This specification creates a unified, bidirectional orchestration layer where:
1. **Plugin Governance** provides verified, sandboxed, and certified capability metadata, execution telemetry, and lifecycle state.
2. **Canvas Control Plane** provides an interactive, collaborative, and fail-closed spatial cockpit for visual DAG inspection, operator approvals, and real-time state synchronization.

### 1.1 Non-Goals & Strict Invariants
- **Zero Runtime Modifications:** This specification establishes integration models and protocols without altering the active execution runtime or existing schemas.
- **No In-Tree Plugin Execution:** Plugins remain declared, certified, and sandboxed; this specification does not trigger or activate production plugin execution.
- **No External Network Dependencies:** All contracts, schemas, and verification hooks operate 100% locally with relative paths (`./`, `../`).
- **Zero Secrets / Zero Network Calls:** No credentials, environment secrets, live sockets, or remote services are accessed.

---

## 2. Integrated System Architecture

The integration layer bridges two autonomous pipelines into a cohesive control loop:

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#16191c',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#34d399',
    'lineColor': '#34d399',
    'secondaryColor': '#102219',
    'tertiaryColor': '#16191c',
    'tertiaryTextColor': '#ffffff',
    'titleColor': '#ffffff',
    'textColor': '#ffffff',
    'mainBkg': '#16191c',
    'nodeBorder': '#34d399',
    'clusterBkg': 'transparent',
    'clusterBorder': 'rgba(255, 255, 255, 0.16)',
    'edgeLabelBackground': '#102219',
    'fontSize': '13px'
  }
}}%%
flowchart TD
    subgraph Plugin Governance
        A[GitHub Intake] --> B[Sandbox Runner]
        B --> C[Certification]
        C --> D[Registry]
        D --> E[Capability Graph]
        E --> F[Execution Plan]
        F --> G[Execution Engine]
        G --> H[Audit Log]
        H --> I[Health Metrics]
    end

    subgraph Canvas Control
        J[Control Plane] --> K[OCC 3-Way Merge]
        K --> L[WebSocket/SSE Protocol]
        L --> M[Human-in-the-Loop Approval]
    end

    Plugin Governance --> Canvas Control
    Canvas Control --> Plugin Governance
```

### 2.1 Component Mapping Matrix

| Layer | Plugin Governance Component | Canvas Control Component | Integration Role |
|---|---|---|---|
| **Discovery** | `PluginRegistry` (`core/plugins/registry.py`) | `CanvasControlPlane` (`core/canvas/control_plane.py`) | Converts certified Plugin Cards into interactive `CanvasNode` instances. |
| **Topology** | `PluginCapabilityGraph` (`core/plugins/capability_graph.py`) | Canvas Edges (`CanvasEdge`) | Maps plugin inputs/outputs into spatial DAG dependency edges. |
| **Execution** | `PluginExecutionEngine` (`core/plugins/execution_engine.py`) | Canvas Node Status & Metadata | Updates visual node state (`running`, `completed`, `failed`) and metrics. |
| **Quality** | `PluginHealthMetrics` (`core/plugins/health_metrics.py`) | Canvas Indicators & Badges | Feeds health scores (0-100) and degraded/warning flags into UI nodes. |
| **Safety** | `PluginPolicyEngine` & Execution Gating | `ApprovalManager` (`core/canvas/approval.py`) | Intercepts critical actions and requires operator approval before execution. |
| **Provenance**| `PluginAuditLogger` (`core/plugins/audit_log.py`) | Canvas Event Timeline (`CanvasMessage`) | Projects append-only audit events and approval decisions onto the canvas history. |

---

## 3. The 5 Key Integration Points

### 3.1 Point 1: Registry → Control Plane (Topological Projection)

#### 3.1.1 Mechanism
The `PluginRegistry` maintains the index of all certified and registered capabilities discovered in the workspace. When a canvas session initializes or registers updates, the `CanvasControlPlane` projects each registered plugin into a spatial node:
1. **Plugin Card Extraction**: The registry parses `PluginCard` manifests (`templates/plugin/cards/*.yaml`).
2. **CanvasNode Construction**:
   - `node_id`: Canonical plugin identifier (e.g. `plugin.shopify.sync`, `plugin.video.compose`).
   - `kind`: Set to `"plugin"`.
   - `label`: Human-readable name from `PluginCard.name`.
   - `position`: Deterministically laid out using topological rank from `PluginCapabilityGraph`.
   - `metadata`: Hydrated with `version`, `author`, `license`, `capabilities`, and `runtime` requirements.
3. **CanvasEdge Construction**:
   - For every edge `(source_capability -> target_capability)` resolved by `PluginCapabilityGraph.edges`, a corresponding `CanvasEdge` is established:
     - `edge_id`: `edge:<source_plugin>-><target_plugin>:<capability_name>`
     - `source`: Source `CanvasNode.node_id`
     - `target`: Target `CanvasNode.node_id`
     - `relation`: `"depends_on"` or `"pipes_to"`

#### 3.1.2 Data Transformation Contract
```yaml
# Input: PluginIndexEntry (core/plugins/registry.py)
PluginIndexEntry:
  plugin_id: "plugin.shopify.product_sync"
  name: "Shopify Product Sync"
  version: "1.0.0"
  status: "certified"
  capabilities: ["shopify.products.read", "shopify.products.write"]

# Output: CanvasNode (core/canvas/control_plane.py)
CanvasNode:
  id: "plugin.shopify.product_sync"
  type: "plugin"
  position: { x: 250, y: 120 }
  data:
    label: "Shopify Product Sync"
    status: "certified"
    version: "1.0.0"
    capabilities: ["shopify.products.read", "shopify.products.write"]
    health_score: 98.5
```

---

### 3.2 Point 2: Execution Engine → Canvas (State & Telemetry Projection)

#### 3.2.1 Mechanism
During DAG execution, `PluginExecutionEngine` processes an `ExecutionPlan`. As individual `ExecutionStep` instances advance through their lifecycle, execution status is streamed to the Canvas layer:
1. **Status Transition**:
   - Step `queued` / `pending` → CanvasNode visual style: muted/dashed border.
   - Step `running` → CanvasNode visual style: pulsing accent border with active worker badge.
   - Step `completed` → CanvasNode visual style: solid green border, output preview attached.
   - Step `failed` → CanvasNode visual style: solid red border, error drawer populated.
2. **Node Metadata Update**:
   - Upon completion of a step, `ExecutionStepResult` metrics (duration in ms, exit code, memory usage, token spend) are merged into the target node's `data.metrics`.
3. **CanvasEvent Generation**:
   - Every state transition produces a `CanvasMessage` of type `STATE_UPDATE` or `EVENT` routed through the OCC merge pipeline to ensure multi-agent visual consistency.

#### 3.2.2 Event Contract
```yaml
# Canvas State Update Event triggered by Execution Engine
CanvasMessage:
  protocol_version: "1.0"
  message_id: "msg_exec_98124"
  client_id: "execution_engine"
  type: "STATE_UPDATE"
  payload:
    node_id: "plugin.shopify.product_sync"
    mutation: "UPDATE_STATUS"
    new_status: "completed"
    duration_ms: 142
    exit_code: 0
    timestamp: "2026-09-10T06:00:00Z"
```

---

### 3.3 Point 3: Health Metrics → Canvas (Visual Observability & Warning States)

#### 3.3.1 Mechanism
`PluginHealthMetrics` computes deterministic health scores (0–100) based on execution history, crash ratios, latency trends, and sandbox security violations:
1. **Health Score Indicator**:
   - `score >= 90`: Green badge (`HEALTHY`).
   - `70 <= score < 90`: Amber badge (`DEGRADED`).
   - `score < 70`: Red badge (`CRITICAL` / `UNSTABLE`).
2. **Warning State Propagation**:
   - If a plugin has consecutive failed executions or sandbox violations, `PluginHealthStatus.status` transitions to `degraded` or `critical`.
   - The Canvas Control Plane updates the corresponding `CanvasNode` with warning glyphs, displaying tooltips detailing the root cause (e.g. `timeout`, `resource_cap_breached`, `schema_mismatch`).
   - In `CRITICAL` state, the node's downstream edges are dimmed, alerting the human operator to broken pipeline paths.

#### 3.3.2 Metric Binding Schema
```yaml
CanvasNodeVisualHealth:
  node_id: "plugin.video.compose"
  health_score: 64.2
  status: "degraded"
  consecutive_failures: 2
  warning_message: "Memory limit exceeded during Remotion render"
  visual_state:
    badge_color: "amber"
    border_style: "warning_dashed"
    downstream_warning: true
```

---

### 3.4 Point 4: Approval → Plugin Governance (Fail-Closed Execution Gate)

#### 3.4.1 Mechanism
The `ApprovalManager` (`core/canvas/approval.py`) serves as the strict security boundary between execution intent and physical execution:
1. **Critical Operation Interception**:
   - When an autonomous agent or execution plan requests a destructive, irreversible, or high-privilege action (e.g., deleting store products, modifying live theme code, issuing balance transfers, or removing critical graph topology), the action is classified as `critical`.
   - Instead of direct execution, the request is intercepted and registered as an `ApprovalRequest` with status `pending`.
2. **Operator Gate (Maksym Approval)**:
   - The Canvas displays an interactive approval modal / callout linked to the offending node.
   - The designated approver (`maksym`) evaluates the request context, payload diff, and safety blast radius.
3. **Execution Engine Unlock**:
   - `decision: "approved"`: The `ApprovalManager` signs the approval, moves the record to `approval_history.jsonl`, and emits an unlock token to `PluginExecutionEngine`, permitting step execution.
   - `decision: "rejected"`: The execution step fails with `ApprovalDeniedError`, preventing any state changes or execution runner invocation.

#### 3.4.2 Approval Protocol Lifecycle
```
[Agent Intent] ──> [Is Operation Critical?]
                         │
                 ┌───────┴───────┐
                 │ No            │ Yes
                 ▼               ▼
          [Auto-Execute]   [Create ApprovalRequest (status: pending)]
                                 │
                                 ▼
                     [Prompt Operator Maksym on Canvas]
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
            [decision: approved]    [decision: rejected]
                     │                       │
                     ▼                       ▼
        [Unlock Execution Engine]   [Abort Step with Error]
```

---

### 3.5 Point 5: Audit Log → Canvas History (Unified Temporal Audit Trail)

#### 3.5.1 Mechanism
The `PluginAuditLogger` (`core/plugins/audit_log.py`) records an immutable, append-only log of every plugin lifecycle event, sandbox execution, and policy decision:
1. **Timeline Projection**:
   - Every `AuditEvent` (actor, event_type, target, timestamp, status, payload_hash) is ingested into the Canvas temporal history buffer.
   - The Canvas timeline drawer displays an chronological activity stream directly correlated with active graph nodes.
2. **Approval Audit Coupling**:
   - All `ApprovalHistoryEntry` decisions made by Maksym are recorded both in `approval_history.jsonl` and mirrored as `plugin.approval.decided` events in `audit_log.jsonl`.
3. **Temporal Playback & Replay**:
   - The operator can inspect past graph states by scrubbing the canvas timeline, reviewing exact execution inputs, hashes, and approval justifications at any historical slice.

#### 3.5.2 Unified History Event Record
```yaml
UnifiedCanvasHistoryEvent:
  event_id: "evt_audit_44021"
  timestamp: "2026-09-10T06:05:12Z"
  actor: "maksym"
  category: "approval_decision" # plugin_execution | approval_decision | health_alert
  target_node_id: "plugin.shopify.product_sync"
  details:
    decision: "approved"
    action: "canvas.node.remove"
    reason: "Decommissioning legacy test sync node"
  audit_ref: "sha256:7f83b1657ff1..."
```

---

## 4. Informational CLI Interface

The DNK OS Harness provides an informational CLI designed for operator inspection and verification of integration topology without invoking execution engines:

```bash
# 1. Inspect holistic Harness overview (Plugins + Canvas status)
./.venv/bin/python3 scripts/system/dnk_harness.py overview

# 2. Inspect the 5 active integration points and binding status
./.venv/bin/python3 scripts/system/dnk_harness.py integration-points
```

### 4.1 Sample Output: `overview`
```text
================================================================================
                     DNK OS HARNESS ORCHESTRATION OVERVIEW
================================================================================
Plugin Governance Subsystem:
  - Registered Plugins:   14 certified
  - Capability Graph:     28 nodes, 42 edges (Acyclic: YES)
  - Health Metrics:       System Score: 98.2 / 100 (HEALTHY)
  - Audit Trail:          1,420 immutable events logged

Canvas Control Plane Subsystem:
  - Active Canvas Nodes:  28 mapped
  - Active Canvas Edges:  42 mapped
  - OCC Merge Protocol:   VectorClock synchronized (v4.2)
  - HITL Approval Gate:   0 pending, 34 historical decisions

Integration Status:      CONNECTED (100% contracts validated)
================================================================================
```

### 4.2 Sample Output: `integration-points`
```text
================================================================================
                   DNK OS HARNESS INTEGRATION POINTS (5/5)
================================================================================
[1] Registry -> Control Plane:      BOUND (PluginCard -> CanvasNode/Edge)
[2] Execution Engine -> Canvas:     BOUND (StepResult -> NodeState/Event)
[3] Health Metrics -> Canvas:       BOUND (HealthScore -> WarningBadges)
[4] Approval -> Governance:         BOUND (ApprovalRequest -> ExecUnlock)
[5] Audit Log -> Canvas History:    BOUND (AuditEvent -> TimelineDrawer)
================================================================================
```

---

## 5. Security & Boundary Verification

1. **Path Traversal Shield**: All referenced templates, cards, logs, and artifacts are strictly confined to relative paths (`./`, `../`). Absolute system paths (`/Users/...`, `/etc/...`) trigger strict validation rejections.
2. **Fail-Closed Governance**: If an integration contract between Canvas and Governance fails validation, the system falls back to read-only visualization and refuses automated step dispatch.
3. **Zero Mutation Invariant**: Reading or rendering the integration topology produces zero side effects, zero git mutations, and zero state churn.
