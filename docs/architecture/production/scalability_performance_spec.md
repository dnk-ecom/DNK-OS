---
title: "DNK OS Scalability & Performance Technical Specification v1.0"
description: "Technical Specification for Kubernetes Autoscaling, Redis Caching, PostgreSQL Topology & High-Concurrency Performance in DNK OS"
mrh_id: "docs/architecture/production/scalability_performance_spec.md"
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
> mrh_id: "docs/architecture/production/scalability_performance_spec.md"
> purpose: "Technical Specification for Kubernetes Autoscaling, Redis Caching, PostgreSQL Topology & High-Concurrency Performance in DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🚀 DNK OS Scalability & Performance Technical Specification v1.0

> **System:** DNK OS MVP — Production Hardening  
> **Sub-Phase:** Phase 3.4 (High-Concurrency Architecture & Performance Optimization)  
> **Target Scale:** 1,000+ Concurrent Sandbox Executions / Sub-100ms Latency  
> **Document Status:** Canonical Technical Specification  

---

## 1. High-Concurrency Scale-Out Architecture

DNK OS architecture is fully decoupled to allow independent scaling of user-facing spatial UI servers, WebSocket connection managers, and asynchronous background sandbox execution pools.

```
                                  [ Cloudflare CDN / Global Anycast Edge ]
                                                    |
                                                    v
                                      [ Kubernetes Ingress (Traefik) ]
                                                    |
                      +-----------------------------+-----------------------------+
                      |                                                           |
                      v                                                           v
        [ Next.js Spatial UI Pods ]                                [ FastAPI Backend Core Pods ]
        - Stateles SSR / Static Assets                            - Stateless API & WebSocket Gate
        - HPA: 2 to 20 Pods                                       - HPA: 3 to 30 Pods
                      |                                                           |
                      +-----------------------------+-----------------------------+
                                                    |
                                    +---------------+---------------+
                                    |                               |
                                    v                               v
                    [ Redis Cluster (v7.2) ]         [ PgBouncer Connection Pool ]
                    - Canvas State Cache (TTL 1h)    - Transaction Pooling (max 500)
                    - Pub/Sub Event Exchange                        |
                    - Distributed Lock (Redlock)                    v
                                                     [ PostgreSQL 16 Primary (Write) ]
                                                            |          | (Streaming Repl)
                                                            v          v
                                                     [ Read Replica 1 ] [ Read Replica 2 ]
                                                            ^
                                                            | Read queries
                                    +-----------------------+-------+
                                    |
                    [ KEDA Autoscaler (Queue-based) ]
                                    |
                                    v
                 [ Ephemeral Sandbox Worker Nodes ]
                 - Node Auto-provisioning (Karpenter)
                 - Isolated Host Pool for Container Execution
                 - 1,000+ Concurrent Sandbox Containers
```

---

## 2. Horizontal Scaling & Autoscaling Policies

### 2.1 Kubernetes Horizontal Pod Autoscaler (HPA)
- **FastAPI Core Service**:
  - Minimum Pods: `3` (High-Availability across 3 Availability Zones).
  - Maximum Pods: `30`.
  - Scaling Triggers:
    - Target Average CPU Utilization: `70%`.
    - Target Average Memory Utilization: `75%`.
    - Custom Metric: `active_websocket_connections_per_pod` > `500`.

### 2.2 Worker Pool Autoscaling with KEDA (Kubernetes Event-driven Autoscaling)
- Background plugin executions are dispatched via Redis Streams or RabbitMQ queues.
- **KEDA ScaledObject**:
  - Dynamically provisions worker pods based on queue depth:
    - Target Queue Depth: `5 tasks / worker`.
    - Scale Down Stabilization Window: `300 seconds` (to prevent flapping).
  - Integrates with AWS Karpenter or GCP Cluster Autoscaler to dynamically spin up dedicated compute instances (`c6i.4xlarge` / `n2-standard-16`) during high-demand bursts.

---

## 3. Caching & State Management Tier (Redis Cluster)

### 3.1 Redis Cluster Architecture & Topology
- **Cluster Deployment**: 3 Master + 3 Replica nodes with automatic failover (< 3s detection).
- **Eviction Policy**: `volatile-lru` with memory limit cap per node (8GB).

### 3.2 Cache Invalidation & Strategies

| Data Entity | Cache Key Pattern | TTL | Invalidation Strategy |
|---|---|---|---|
| **Canvas State** | `dnk:canvas:{tenant_id}:{canvas_id}` | 1 hour | Write-through on OCC 3-way merge commit; pub/sub invalidation push. |
| **Plugin Metadata** | `dnk:plugin:meta:{plugin_id}:{version}` | 24 hours | Immutable by version; explicit purge on plugin deprecation. |
| **User Session & RBAC** | `dnk:session:{session_token_hash}` | 15 min | Sliding window refresh; immediate purge on logout or permission revocation. |
| **Health Scores** | `dnk:health:scores:{tenant_id}` | 60 sec | Periodic refresh from background Prometheus evaluator. |

### 3.3 Static Assets CDN Tier
- Cloudflare CDN caches Next.js build artifacts (`_next/static/*`), icons, vector assets, and documentation.
- Cache-Control: `public, max-age=31536000, immutable` for hashed assets.

---

## 4. Database Topology & Performance Tuning (PostgreSQL 16)

### 4.1 Primary-Replica Topology
- **Primary Node (Read/Write)**: Handles all mutations (canvas updates, plugin registrations, approval logs).
- **Read Replicas (x2)**: Asynchronous physical streaming replication for telemetry queries, analytical reports, and audit trail reads.
- **Failover**: Automated failover managed by Patroni / AWS Aurora with target RTO < 30 seconds.

### 4.2 Connection Pooling (PgBouncer)
- Microservices connect through local sidecar or centralized PgBouncer instances.
- **Pool Mode**: `transaction` pooling.
- **Settings**:
  - `default_pool_size`: 50 per database.
  - `max_client_conn`: 5,000.
  - `reserve_pool_size`: 10.
  - `server_idle_timeout`: 60s.

---

## 5. Performance Targets & Latency Budgets

| Operational Metric | Target Benchmark | Maximum Threshold | Measurement Methodology |
|---|---|---|---|
| **Canvas State Update Latency** | **< 50 ms** | **< 100 ms** | Round-trip WebSocket mutation ack to Spatial UI client. |
| **Plugin Execution Startup** | **< 350 ms** | **< 1,000 ms** | From API trigger to first sandbox process instruction execution. |
| **Concurrent Sandbox Executions**| **1,000+ concurrent** | Sustained capacity | Distributed stress test with k6 / Locust across worker nodes. |
| **OCC 3-Way Merge Resolution** | **< 15 ms** | **< 30 ms** | Server-side graph diff and version collision check. |
| **API Endpoint Throughput** | **5,000+ RPS** | Sustained capacity | Core metadata and health endpoints under load. |

---

## 6. High-Load Benchmark & Chaos Validation Plan

1. **Synthetic Load Injection**:
   - Simulated 1,000 concurrent client sessions emitting canvas transformations and plugin execution triggers.
   - Target metrics verified via Grafana dashboard under sustained 30-minute load.
2. **Chaos Engineering (LitmusChaos / Chaos Mesh)**:
   - Random worker pod termination (`kill -9`).
   - Redis master node failure (verifying seamless switch to replica).
   - Network partition simulation between API pods and PostgreSQL primary.
