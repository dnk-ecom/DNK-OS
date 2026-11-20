---
title: "DNK OS Monitoring & Observability Technical Specification v1.0"
description: "Technical Specification for Prometheus Metrics, OpenTelemetry Tracing, Structured JSON Logging & PagerDuty Alerting"
mrh_id: "docs/architecture/production/monitoring_observability_spec.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/production/monitoring_observability_spec.md"
> purpose: "Technical Specification for Prometheus Metrics, OpenTelemetry Tracing, Structured JSON Logging & PagerDuty Alerting"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📊 DNK OS Monitoring & Observability Technical Specification v1.0

> **System:** DNK OS MVP — Production Hardening  
> **Sub-Phase:** Phase 3.3 (Observability & Telemetry Pipeline)  
> **Target Framework:** Prometheus / OpenTelemetry (OTel) / Grafana Loki / PagerDuty  
> **Document Status:** Canonical Technical Specification  

---

## 1. Observability Architecture & Pipeline

DNK OS implements the three pillars of modern cloud observability—Metrics, Logs, and Traces—unified via open standards (OpenTelemetry) to provide end-to-end visibility across the visual canvas, backend API, worker pools, and isolated sandbox containers.

```
+---------------------------------------------------------------------------------------------------+
| DNK OS Observability Fabric                                                                       |
|                                                                                                   |
|  +--------------------+   +-----------------------+   +----------------------+                    |
|  | Next.js Spatial UI |   | FastAPI Backend Core  |   | Docker Sandboxes     |                    |
|  | - Web Vitals       |   | - HTTP & WS Endpoints |   | - Ephemeral Runs     |                    |
|  | - OCC Sync Metrics |   | - TaskDNA Scheduler   |   | - cgroup v2 Telemetry|                    |
|  +---------+----------+   +-----------+-----------+   +----------+-----------+                    |
|            |                          |                          |                                |
|            | OTLP / HTTP              | OTLP / gRPC              | Daemon Collector               |
|            +--------------------------+--------------------------+                                |
|                                       v                                                           |
|                     +-----------------------------------+                                         |
|                     | OpenTelemetry Collector (Contrib) |                                         |
|                     | - Batching, Filtering, Redaction  |                                         |
|                     +-----+-----------+-----------+-----+                                         |
|                           |           |           |                                               |
|               Metrics     |     Traces|           | Logs                                          |
|               v           |           v           v                                               |
|      +-----------------+  |  +-----------------+  +-----------------+                             |
|      | Prometheus Core |  |  | Jaeger / Tempo  |  | Grafana Loki    |                             |
|      +--------+--------+  |  +--------+--------+  +--------+--------+                             |
|               |           |           |                    |                                      |
|               +-----------+-----+-----+--------------------+                                      |
|                                 v                                                                 |
|                 +-------------------------------+                                                 |
|                 | Unified Grafana Dashboard     |                                                 |
|                 +---------------+---------------+                                                 |
|                                 |                                                                 |
|                                 v Alertmanager                                                    |
|                 +-------------------------------+                                                 |
|                 | PagerDuty / Opsgenie Incident |                                                 |
|                 +-------------------------------+                                                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Metrics Specification (Prometheus)

### 2.1 Golden Signals & System Metrics
DNK OS exports standardized Prometheus metrics scraped via `/metrics` (authenticated) on all core services:

| Metric Name | Type | Labels | Description / Objective |
|---|---|---|---|
| `dnk_http_requests_total` | Counter | `method`, `route`, `status_code` | HTTP request rate and throughput. |
| `dnk_http_request_duration_seconds` | Histogram | `method`, `route`, `le` | HTTP request latency (Target: p95 < 100ms). |
| `dnk_active_websocket_connections` | Gauge | `tenant_id` | Live concurrent spatial UI WebSocket sessions. |
| `dnk_websocket_messages_total` | Counter | `direction`, `type` | Spatial canvas event exchange rate. |
| `dnk_canvas_occ_conflicts_total` | Counter | `canvas_id`, `resolution` | Number of OCC 3-way merge conflicts encountered. |

### 2.2 Custom Plugin & Sandbox Telemetry Metrics

| Metric Name | Type | Labels | Description / Objective |
|---|---|---|---|
| `dnk_plugin_executions_total` | Counter | `plugin_id`, `version`, `status` | Total count of plugin runs (`success`, `failed`, `timeout`). |
| `dnk_plugin_execution_duration_seconds` | Histogram | `plugin_id`, `le` | Execution time inside Docker sandbox (p95 < 1.0s). |
| `dnk_plugin_health_score` | Gauge | `plugin_id` | Algorithmic health score (0.0 to 1.0) based on error rates and latency. |
| `dnk_sandbox_active_containers` | Gauge | `worker_node` | Number of currently running container instances. |
| `dnk_sandbox_oom_events_total` | Counter | `plugin_id` | Number of containers terminated by cgroups OOM killer. |
| `dnk_sandbox_timeout_events_total` | Counter | `plugin_id` | Number of containers terminated due to execution timeout. |

---

## 3. Structured Logging Specification (Grafana Loki / ELK)

### 3.1 JSON Log Schema
All system logs are emitted to `stdout` in single-line structured JSON adhering to the DNK OS Log Schema:

```json
{
  "timestamp": "2026-09-10T12:00:00.123Z",
  "level": "INFO",
  "service": "dnk_api_core",
  "environment": "production",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "tenant_id": "ws-alpha-001",
  "actor_id": "usr_maksym_001",
  "event": "canvas.node.mutation",
  "payload": {
    "node_id": "node_agent_builder_01",
    "position": {"x": 250, "y": 420},
    "version": 4
  },
  "message": "Canvas node position updated successfully"
}
```

### 3.2 Sensitive Data Redaction
- Log forwarders (Fluentbit / Promtail) enforce automatic redaction masks on all fields containing:
  - Authorization tokens (`Bearer ...` -> `Bearer [REDACTED]`).
  - Credit card numbers, API keys, passwords, and private email addresses.

---

## 4. Distributed Tracing Specification (OpenTelemetry)

### 4.1 Trace Context Propagation (W3C TraceContext)
- Distributed traces adhere strictly to the W3C `traceparent` and `tracestate` headers across HTTP, WebSocket, and asynchronous worker queues.
- Every canvas mutation or plugin invocation receives a unique `trace_id`.

### 4.2 Critical Traced Flows & Spans

```
[Spatial UI] Canvas Interaction (trace_id: 4bf92f3...)
  │
  ├─ [HTTP/WS] POST /api/v1/plugins/run  (duration: 82ms)
  │    │
  │    ├─ [FastAPI] Authenticate & Authorize  (duration: 4ms)
  │    ├─ [FastAPI] Validate Capability ACL   (duration: 2ms)
  │    ├─ [Vault] Fetch Ephemeral Token       (duration: 8ms)
  │    │
  │    └─ [WorkerPool] Queue Task Dispatch    (duration: 3ms)
  │
  └─ [Worker Node] dnk_sandbox_manager (trace_id: 4bf92f3...)
       │
       ├─ [Docker API] Create Ephemeral Container (duration: 35ms)
       ├─ [Container] Execute Plugin Entrypoint   (duration: 340ms)
       ├─ [Docker API] Collect Result & Teardown  (duration: 18ms)
       └─ [WebSocket] Push Result to Spatial UI   (duration: 12ms)
```

---

## 5. Alerting Architecture & Severity Matrix

### 5.1 Severity Matrix & Routing (PagerDuty / Opsgenie)

| Severity | Definition | Response SLA | Notification Channel | Escalation Path |
|---|---|---|---|---|
| **P1 - Critical** | Total system outage, data corruption, active security breach, uptime < 99.0% | < 5 minutes | PagerDuty On-Call, Phone Call, SMS, Slack #war-room | Maksym + Lead Architect |
| **P2 - High** | Sub-system failure (e.g. Docker sandboxes blocked, WebSocket disconnects > 5%, p95 latency > 500ms) | < 15 minutes | PagerDuty, Slack #ops-alerts | On-Call Engineer |
| **P3 - Medium** | Non-critical plugin failure, background cron failure, memory usage > 80% | < 2 hours | Slack #dev-monitoring | Team Backlog |
| **P4 - Low** | Informational warning, minor certificate expiry warning (> 14 days) | Next business day | Email / Slack #digest | Scheduled Sprint |

### 5.2 Core Prometheus Alert Rules

```yaml
groups:
  - name: dnk_os_critical_alerts
    rules:
      - alert: DNKHighErrorRate
        expr: (sum(rate(dnk_http_requests_total{status_code=~"5.."}[5m])) / sum(rate(dnk_http_requests_total[5m]))) * 100 > 1.0
        for: 2m
        labels:
          severity: P1
        annotations:
          summary: "DNK OS HTTP 5xx error rate exceeds 1% (current: {{ $value }}%)"

      - alert: DNKSpatialCanvasLatencyHigh
        expr: histogram_quantile(0.95, sum(rate(dnk_http_request_duration_seconds_bucket{route="/api/v1/canvas/sync"}[5m])) by (le)) > 0.100
        for: 3m
        labels:
          severity: P2
        annotations:
          summary: "Canvas synchronization p95 latency exceeds 100ms"

      - alert: DNKSandboxOOMSpike
        expr: sum(rate(dnk_sandbox_oom_events_total[5m])) > 5
        for: 1m
        labels:
          severity: P2
        annotations:
          summary: "Spike in container OOM kills detected in sandbox pool"
```
