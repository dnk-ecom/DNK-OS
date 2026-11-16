---
title: "Specification"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/telemetry/analytics/docs/SPECIFICATION.md"
> purpose: "Document: Specification"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

<!--
--- DNK-MRH-HEADER ---
mrh_id: "services/dnk_analytics/docs/SPECIFICATION.md"
purpose: "Human-readable service specification for dnk_analytics."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-13"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER ---
-->

# DNK Analytics — Service Specification v1.0

## 1. Overview

`dnk_analytics` is an **Analytics** tier-2 satellite service responsible for gathering system telemetry, calculating LLM reasoning drift, tracking self-healing outcomes, and exposing standard Prometheus metrics for DNK OS.

## 2. Domain & Tier

| Field       | Value              |
|-------------|--------------------|
| Domain      | `analytics`        |
| Tier        | `tier-2-satellite` |
| Lifecycle   | `production`       |
| Owner Agent | `dnk_dev_fullstack`|

## 3. Core Capabilities

### 3.1 Prometheus Exposition
Generates OpenMetrics / Prometheus standard text format containing counters, gauges, and histograms for agent execution latency, token expenditures, and error rates.

### 3.2 Model Drift Detection
Monitors inference distributions and identifies prompt/reasoning drift across model providers (Gemini, Claude, Vertex AI).

### 3.3 Visual Shell Dashboard Telemetry
Provides structured JSON summaries powering Visual Shell frontend analytics and live health monitoring.

## 4. Entrypoint

```
services.dnk_analytics.telemetry_exporter:GeminiTelemetryExporter
```

## 5. Dependencies

| Resource               | Type   | Required |
|------------------------|--------|----------|
| `redis_url`            | Secret | ✅ |
| `prometheus_endpoint`  | Secret | ✅ |

## 6. MCP Tools Exposed

| Tool Name                           | Description |
|-------------------------------------|-------------|
| `analytics_export_metrics`          | Generates Prometheus metrics output |
| `analytics_check_drift`             | Evaluates model reasoning drift |
| `analytics_get_telemetry_snapshot`  | Provides snapshot for Visual Shell |

## 7. Spend Guard

- Max tokens/task: `15,000`
- Max cost/run: `$0.05 USD`

## 8. Health & Metrics

- Health: `GET /api/v1/analytics/health`
- Metrics: `GET /api/v1/analytics/metrics`
