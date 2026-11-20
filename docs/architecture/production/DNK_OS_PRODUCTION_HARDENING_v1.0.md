---
title: "DNK OS Production Hardening Master Specification v1.0"
description: "Canonical Master Specification for DNK OS Production Hardening: Docker Sandbox, Security, Monitoring, Scalability, CI/CD & DR"
mrh_id: "docs/architecture/production/DNK_OS_PRODUCTION_HARDENING_v1.0.md"
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
> mrh_id: "docs/architecture/production/DNK_OS_PRODUCTION_HARDENING_v1.0.md"
> purpose: "Canonical Master Specification for DNK OS Production Hardening: Docker Sandbox, Security, Monitoring, Scalability, CI/CD & DR"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛡️ DNK OS Production Hardening Master Specification v1.0

> **System:** DNK OS MVP — Minimum Viable Runtime (MVR)  
> **Phase:** Phase 3 (Production Hardening)  
> **Transition:** MVR Prototype / Experimental → Production-Ready Enterprise System  
> **Document Status:** Canonical Master Specification (Locked)  

---

## 1. Executive Summary

The **DNK OS Production Hardening Specification** establishes the definitive architectural, operational, and security blueprint to transition DNK OS from a Minimum Viable Runtime (MVR) into a resilient, high-throughput, enterprise-grade production operating system.

### Strategic Transition (MVR → Production)
While MVR validated core agent orchestration, in-memory plugin registries, and spatial UI canvas interactions, Production Hardening fortifies every layer against untrusted code execution, systemic failures, security breaches, and high-concurrency bottlenecks.

```
       [ MVR Prototype ]                         [ Production Hardening (Phase 3) ]
  • Local Subprocess Runs           ───►   • Ephemeral Docker Sandbox (gVisor / Non-Root)
  • In-Memory / File State          ───►   • Redis Cluster + PostgreSQL 16 (Patroni Replicas)
  • Basic Console Logging           ───►   • OpenTelemetry Traces + Prometheus + Grafana Loki
  • Unrestricted Network & Dev      ───►   • Zero-Trust RBAC, Vault KMS, WORM Audit Logs
  • Manual Script Starts            ───►   • Kubernetes HPA + KEDA Workers + Canary CI/CD
```

### The 5 Core Pillars
1. **Docker Sandbox Isolation**: True multi-tenant isolation, strict cgroups v2 resource quotas, and zero-egress network boundaries for plugin runs.
2. **Zero-Trust Security**: Multi-factor authentication (MFA/WebAuthn), HashiCorp Vault secrets management, RBAC, and tamper-evident audit trails.
3. **Observability & Telemetry**: Full-fidelity Prometheus metrics, distributed OpenTelemetry tracing, structured JSON logs, and PagerDuty incident response.
4. **Elastic Scalability & Performance**: Kubernetes autoscaling, transaction connection pooling, distributed Redis caching, and independent worker scaling.
5. **CI/CD & Zero-Regression Automation**: Automated quality gates, image provenance signing (Cosign), and zero-downtime blue-green/canary deployments.

### Target Key Performance Indicators (KPIs)
- **Availability & Uptime**: **99.9%** (less than 43.8 minutes of unplanned downtime per month).
- **Spatial UI & Canvas Latency**: **< 100 ms** (p95 end-to-end WebSocket synchronization).
- **Plugin Execution Startup**: **< 1.0 s** (p95 cold start to first sandbox instruction).
- **Security Incident Objective**: **0 uncontained security incidents / 0 privilege escalations**.

---

## 2. Docker Sandbox Spec

*For in-depth architectural and syscall details, refer to the dedicated technical document:*  
👉 **`docs/production/docker_sandbox_spec.md`**

### 2.1 Container Isolation
- **Per-Plugin Ephemeral Containers**: Each plugin execution is strictly allocated to a distinct, single-use container instance.
- **Resource Limits (cgroups v2)**:
  - **Memory Limit**: 512 MB hard ceiling (OOM-killer terminates runaway scripts immediately). Swap is disabled.
  - **CPU Quota**: 1.0 vCPU core equivalent (100,000 µs quota per 100,000 µs period).
  - **Process Limit**: Hard ceiling of 64 processes/threads (`PidsLimit: 64`) to eliminate fork bomb vectors.
  - **Storage Limit**: 512 MB temporary scratch space.
- **Network Isolation**:
  - Default network mode is `--network none`. Containers are instantiated without network interfaces.
  - Outbound internet access is physically blocked unless the plugin manifest explicitly requests egress AND the request is approved through the Human-in-the-Loop (HITL) gate.
  - Approved outbound traffic passes through an internal egress proxy with strict domain whitelisting and rate limiting.

### 2.2 Security Containment Profiles
- **Non-Root Execution**: Runs under unprivileged user `dnkrunner` (`UID:GID 10001:10001`). `no-new-privileges: true` is enforced.
- **Read-Only Root Filesystem**: The entire rootfs (`/`) is mounted immutable (`ro`).
- **Tmpfs Mounts**: `/tmp` (128MB) and `/run` (16MB) mounted via in-memory `tmpfs` with `rw,noexec,nosuid,nodev`.
- **Seccomp-BPF & AppArmor Profiles**: Restrictive syscall filters block dangerous calls (`ptrace`, `mount`, `reboot`, `setns`, `bpf`), while AppArmor denies raw hardware access, device access, and configuration reads.

### 2.3 Container Lifecycle
- **Just-In-Time Spawning**: Containers are provisioned on demand when a task is dispatched.
- **Immediate Destruction**: Upon task completion, failure, or timeout, the container is forcibly stopped, removed (`docker rm -f`), and scratch volumes are purged.
- **Hard Execution Timeout**: Configurable timeout between **5 and 30 seconds** (default 10s). An asynchronous watchdog issues `SIGTERM` followed by `SIGKILL` after a 2-second grace period.

### 2.4 Image Management & Supply Chain
- **Minimal Base Images**: Distroless or hardened Python (`3.12-slim`) and Node.js (`20-alpine`) bases containing only standard libraries.
- **Build Once, Deploy Many (BODM)**: Images are pre-built in CI with pinned lockfiles and immutable SHA-256 digests.
- **Cryptographic Signing**: All images are signed via **Cosign / Sigstore**; the runtime verifies signatures prior to launching any container.

---

## 3. Security Hardening Spec

*For in-depth architectural and credential management details, refer to the dedicated technical document:*  
👉 **`docs/production/security_hardening_spec.md`**

### 3.1 Authentication (AuthN)
- **API Authentication**: Stateless OAuth 2.0 / OIDC Bearer tokens with RS256 asymmetric signing. Short-lived access tokens (15-minute lifespan) paired with rotating refresh tokens stored in HTTP-only, `SameSite=Strict` cookies.
- **Multi-Factor Authentication (MFA)**: Mandatory for administrative and owner accounts (`maksym`, `admin`). Supports FIDO2 / WebAuthn hardware keys (Passkeys, YubiKey) and TOTP (RFC 6238). Step-up authentication triggered for dangerous capabilities.

### 3.2 Authorization (AuthZ) & Capabilities
- **Role-Based Access Control (RBAC)**:
  - `maksym` (Owner): Complete authority, root governance, full WORM audit export.
  - `admin` (System Admin): Infrastructure management, worker scaling, provider setup.
  - `developer` (Builder): Workspace-scoped canvas editing, sandbox plugin testing.
  - `viewer` (Auditor): Read-only canvas inspection, telemetry dashboards, audit inspection.
- **Plugin-Level Capability Grants**: Strict manifest-driven permissions defining permitted filesystem paths, network egress domains, system resources, and scoped secret keys.

### 3.3 Secrets Management (HashiCorp Vault / AWS Secrets Manager)
- **Zero Secrets in Code**: No API keys, database credentials, or signing keys stored in repositories or `.env` files.
- **Dynamic Ephemeral Credentials**: Temporary database leases (1 hour) generated on demand.
- **Memory-Only Injection**: Secrets are injected via authenticated in-memory gRPC exchange into tmpfs or scrubbed environment variables, with automated stdout regex redaction.

### 3.4 Audit Trail & Compliance
- **Write-Once-Read-Many (WORM) Audit Log**: Every user action, canvas mutation, plugin run, and approval decision is immutably recorded.
- **Cryptographic Hash Chaining**: SHA-256 hash chains (`prev_event_hash`) guarantee tamper evidence. Daily anchors backed up to S3 Object Lock.
- **Compliance Alignment**: SOC 2 Type II trust criteria and GDPR privacy by design.

### 3.5 Vulnerability Scanning & Governance
- **Container Scanning**: Automated Trivy / Snyk scans during CI; Critical and High CVEs fail builds.
- **Dependency Scanning**: Dependabot / Renovate daily automated scanning with pinned package hashes.

---

## 4. Monitoring & Observability Spec

*For in-depth metric schemas, tracing spans, and alert rules, refer to the dedicated technical document:*  
👉 **`docs/production/monitoring_observability_spec.md`**

### 4.1 Metrics Architecture (Prometheus & OpenTelemetry)
- **Golden Signals**: Continuous scraping of HTTP/WebSocket request rates, error rates (5xx), request latencies (p50, p95, p99), and system concurrency.
- **Custom Domain Metrics**:
  - `dnk_plugin_executions_total`: Execution throughput categorized by plugin, version, and status.
  - `dnk_plugin_execution_duration_seconds`: Histogram measuring execution duration within the sandbox.
  - `dnk_plugin_health_score`: Real-time health index (0.0 - 1.0) for every registered plugin.
  - `dnk_canvas_occ_conflicts_total`: Collision metrics for concurrent spatial canvas updates.
  - `dnk_sandbox_oom_events_total` & `dnk_sandbox_timeout_events_total`: Sandbox isolation health telemetry.

### 4.2 Centralized Structured Logging (Grafana Loki / ELK)
- **JSON Schema Logging**: Single-line structured JSON output for all backend and worker services.
- **Context Injection**: Mandatory propagation of `trace_id`, `span_id`, `tenant_id`, and `actor_id` in log headers.
- **Automated PII Redaction**: Stream forwarders mask authorization headers, passwords, and sensitive keys.

### 4.3 Distributed Tracing (OpenTelemetry)
- **End-to-End Traces**: W3C TraceContext propagated from Next.js Spatial UI → FastAPI Gateway → Worker Queues → Sandbox Container.
- **Visual Span Analysis**: Granular latency breakdown across database queries, Redis cache lookups, container cold starts, and WebSocket broadcasts.

### 4.4 Alerting & Incident Response (PagerDuty / Opsgenie)
- **Severity Tiers**:
  - **P1 (Critical)**: Outage, data corruption, uptime < 99.0% → SLA < 5 min (PagerDuty on-call, phone escalation).
  - **P2 (High)**: Sandbox degradation, WebSocket disconnect spike, p95 latency > 500ms → SLA < 15 min.
  - **P3 (Medium)**: Non-blocking worker failure, memory warning → SLA < 2 hours.
  - **P4 (Low)**: Informational notices, routine certificate renewals → Next business day.

---

## 5. Scalability & Performance Spec

*For in-depth topology diagrams, caching protocols, and benchmark scripts, refer to the dedicated technical document:*  
👉 **`docs/production/scalability_performance_spec.md`**

### 5.1 Horizontal Scaling & Worker Pools
- **Kubernetes HPA**: Stateless Next.js UI pods (2 to 20 instances) and FastAPI backend pods (3 to 30 instances) scale based on CPU (70%), memory (75%), and active WebSocket connections.
- **KEDA Event-Driven Worker Scaling**: Sandbox execution workers scale dynamically based on Redis/RabbitMQ queue backlog, backed by AWS Karpenter / GCP node auto-provisioning.

### 5.2 Multi-Tier Caching
- **Redis Cluster (v7.2)**: High-availability in-memory cluster caching canvas graph states (TTL 1h), plugin metadata (TTL 24h), and active user sessions.
- **Cloudflare CDN Edge**: Edge caching for all compiled Next.js assets, documentation, and icons with immutable cache headers.

### 5.3 High-Performance Database Topology (PostgreSQL 16)
- **Primary-Replica Cluster**: Single primary node for write transactions paired with two asynchronous streaming read replicas for telemetry and queries.
- **Connection Pooling**: PgBouncer running in transaction pooling mode handling up to 5,000 client connections with minimal overhead.

### 5.4 Performance Budgets & Benchmarks
- **Canvas State Update Latency**: **< 100 ms** (Target: < 50 ms).
- **Plugin Execution Startup**: **< 1.0 s** (Target: < 350 ms).
- **Concurrent Plugin Executions**: **1,000+ simultaneous container executions** without degradation.
- **OCC 3-Way Merge Time**: **< 30 ms** (Target: < 15 ms).

---

## 6. CI/CD Spec

### 6.1 Continuous Integration (CI) Pipeline
Every pull request and commit must pass automated CI checks via GitHub Actions:
1. **Formatting & Linting**: `ruff check`, `black --check`, `eslint`, and `prettier`.
2. **Type Safety**: `mypy --strict` for Python and `tsc --noEmit` for TypeScript/React.
3. **Unit & Integration Tests**: 100% test pass rate with minimum 85% branch coverage.
4. **Security Analysis**: Container scanning with Trivy and SAST with Bandit / CodeQL.
5. **MRH Header Validation**: Verification that all altered files adhere to `DNK-STD-0075`.

### 6.2 Continuous Deployment (CD) Pipeline
- **Canary & Blue-Green Releases**: Deployments to production utilize ArgoCD or Kubernetes native rolling updates with traffic routing (10% canary for 15 minutes, followed by 100% promotion upon clean metrics).
- **Automated Rollback**: Deployment immediately rolls back if error rate exceeds 0.5% or p95 latency spikes by more than 20% during the canary window.

### 6.3 Zero-Regression Quality Gates
- **100% Green Test Suite**: Merges blocked if a single test fails.
- **Zero Vulnerabilities**: Builds blocked on any unpatched High/Critical CVE.
- **Performance Budget Gate**: Automated benchmark runs in CI must not regress latency by > 5%.

---

## 7. Disaster Recovery Spec

### 7.1 Automated Backup Policies
- **Database Backups (PostgreSQL)**:
  - Continuous Point-in-Time Recovery (PITR) using WAL archiving (retained for 30 days).
  - Daily full database snapshots stored in an off-site, multi-region encrypted S3 bucket.
- **Audit Log Ledger Backups**: Continuous streaming to immutable S3 Object Lock storage with WORM compliance.
- **Configuration & Infrastructure as Code**: GitOps repository holds 100% of declarative Kubernetes manifests and Terraform definitions.

### 7.2 Recovery Objectives
- **Recovery Time Objective (RTO)**: **< 1 hour** (maximum acceptable duration to restore full operational service after a catastrophic failure).
- **Recovery Point Objective (RPO)**: **< 15 minutes** (maximum acceptable data loss window via continuous WAL streaming).

### 7.3 Multi-AZ High Availability & Automatic Failover
- All critical services (API pods, Redis Cluster, PostgreSQL replicas) are distributed across a minimum of **3 distinct Availability Zones (Multi-AZ)**.
- Automated failover for database (Patroni / AWS Aurora) switches to the standby replica in under 30 seconds with zero manual intervention.

---

## 8. Roadmap

```
2026-Q4  Week 1-3          Week 3-5          Week 5-7          Week 7-9          Week 9-10
         [ Phase 3.1 ] ──► [ Phase 3.2 ] ──► [ Phase 3.3 ] ──► [ Phase 3.4 ] ──► [ Phase 3.5 ]
         Docker Sandbox    Security          Observability     Scalability       CI/CD & DR
```

### Phase 3.1: Docker Sandbox Isolation
- **Duration**: 2–3 тижні
- **Scope**:
  - Implement `dnk_sandbox_manager` service using Docker API / containerd.
  - Configure gVisor (`runsc`), Seccomp-BPF filters, and AppArmor strict profiles.
  - Build minimal signed base images for Python 3.12 and Node.js 20.
  - Implement ephemeral container lifecycle state machine and supervisor timeout watchdog.
- **Milestone**: Untrusted plugin executes safely within cgroup limits and terminates under 10 seconds.

### Phase 3.2: Security Hardening & Zero-Trust Governance
- **Duration**: 2–3 тижні
- **Scope**:
  - Integrate OAuth 2.0 / OIDC and WebAuthn MFA step-up authentication.
  - Implement fine-grained RBAC and plugin capability manifest enforcement.
  - Deploy HashiCorp Vault with dynamic secret leases and memory-only injection.
  - Build cryptographic hash-chained WORM audit trail with daily S3 Object Lock backup.
- **Milestone**: Complete zero-trust boundary operational; zero secrets stored on disk.

### Phase 3.3: Monitoring & Observability Pipeline
- **Duration**: 2 тижні
- **Scope**:
  - Deploy OpenTelemetry Collector and instrument API, UI, and worker services.
  - Configure Prometheus scraping for Golden Signals and custom plugin health metrics.
  - Set up structured JSON logging pipeline into Grafana Loki with automatic PII masking.
  - Implement PagerDuty / Opsgenie alert rules and on-call escalation policies.
- **Milestone**: End-to-end tracing operational; real-time dashboard displaying sub-100ms metrics.

### Phase 3.4: Scalability & Performance Optimization
- **Duration**: 2–3 тижні
- **Scope**:
  - Deploy Kubernetes HPA and KEDA queue-based autoscaling for sandbox worker pools.
  - Set up Redis 7.2 Cluster with pub/sub invalidation and canvas state caching.
  - Configure PostgreSQL 16 primary-replica cluster with PgBouncer transaction pooling.
  - Execute distributed stress testing validating 1,000+ concurrent sandbox executions.
- **Milestone**: System sustains 1,000+ simultaneous plugin runs with p95 latency < 100ms.

### Phase 3.5: CI/CD, Zero-Regression & Disaster Recovery
- **Duration**: 1–2 тижні
- **Scope**:
  - Author GitHub Actions pipelines with Trivy container scanning and Cosign image signing.
  - Implement canary / blue-green deployment pipelines with automatic rollback triggers.
  - Set up automated PostgreSQL PITR backups and multi-region S3 disaster recovery replication.
  - Conduct simulated disaster recovery drill validating RTO < 1h and RPO < 15m.
- **Milestone**: Fully automated, zero-regression delivery pipeline verified in staging.
