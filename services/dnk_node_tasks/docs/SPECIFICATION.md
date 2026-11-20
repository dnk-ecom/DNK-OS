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
> mrh_id: "services/dnk_node_tasks/docs/SPECIFICATION.md"
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
mrh_id: "services/dnk_node_tasks/docs/SPECIFICATION.md"
purpose: "Human-readable service specification for dnk_node_tasks."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-13"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER ---
-->

# DNK Node Tasks — Service Specification v1.0

## 1. Overview

`dnk_node_tasks` is a **Workflow** tier-1 core service providing conversational intake, mathematical DAG cycle detection, stage gating, and bottom-up progress rollup for node-based tasks and ideas in DNK OS.

## 2. Domain & Tier

| Field       | Value              |
|-------------|--------------------|
| Domain      | `workflow`         |
| Tier        | `tier-1-core`      |
| Lifecycle   | `production`       |
| Owner Agent | `dnk_dev_fullstack`|

## 3. Core Capabilities

### 3.1 Conversational Intake
Parses informal natural language requests into typed `NodeItem` objects with stage allocations (`INCEPTION`, `SPECIFICATION`, `EXECUTION`, `VERIFICATION`).

### 3.2 DAG Cycle Detection & Verification
Evaluates new dependency edges using Kahn's algorithm / DFS topological sort to guarantee acyclicity before persisting graph mutations.

### 3.3 Progress Rollup Engine
Calculates weighted completion percentages across child nodes and propagates completion status to root milestone nodes.

## 4. Entrypoint

```
services.dnk_node_tasks.graph_engine:NodeTaskGraphEngine
```

## 5. Dependencies

| Resource       | Type       | Required |
|----------------|------------|----------|
| `postgres_dsn` | Secret     | ✅ |
| `redis_url`    | Secret     | ✅ |
| `core.security_gate` | Capability | ✅ |

## 6. MCP Tools Exposed

| Tool Name                    | Description |
|------------------------------|-------------|
| `node_tasks_parse_intake`    | Parses user text into structured task ideas |
| `node_tasks_detect_cycle`    | Validates DAG edges to ensure acyclic state |
| `node_tasks_compute_rollup`  | Computes bottom-up milestone progress |

## 7. Spend Guard

- Max tokens/task: `20,000`
- Max cost/run: `$0.10 USD`

## 8. Health & Metrics

- Health: `GET /api/v1/node-tasks/health`
- Metrics: `GET /api/v1/node-tasks/metrics`
