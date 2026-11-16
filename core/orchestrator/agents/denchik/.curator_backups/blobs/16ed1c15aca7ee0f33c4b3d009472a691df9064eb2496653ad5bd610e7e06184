# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/architecture-invariants-and-blast-radius/references/production_hardening_and_sandbox_execution_protocol.md"
# purpose: "Canonical Architectural Invariants and Standards for Production Hardening: Sandbox Isolation, Zero-Trust Security, Observability, and Elastic Scalability"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-10"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Production Hardening & Sandbox Execution Protocol

This reference codifies the architectural rules and invariant standards required to transition DNK OS and associated agentic plugins from Minimum Viable Runtime (MVR) to high-concurrency, zero-trust production readiness.

---

## 1. Container Isolation Invariants (Docker / gVisor)

1. **Per-Execution Ephemerality**:
   - Every external plugin, tool invocation, or untrusted workflow executes in a short-lived container spawned dynamically per request.
   - Post-execution, the container is destroyed (`docker rm -f`) and its isolated storage purged.
2. **Security Sandboxing Profile**:
   - **Kernel Virtualization**: `gVisor` (`runsc`) runtime or strict seccomp/AppArmor policies blocking low-level kernel exploits.
   - **Least Privilege Execution**: Non-root user with UID/GID `10001:10001`.
   - **Filesystem Immutability**: Root filesystem mounted strictly `read-only` (`--read-only`).
   - **Ephemeral Scratchpad**: Writable storage restricted to `tmpfs` mounts at `/tmp` and `/run` with explicit size limits (max 64MB) and `noexec,nosuid,nodev`.
3. **Cgroups v2 Resource Governance**:
   - Strict hard caps: 512MB RAM (`--memory=512m`), 1 vCPU (`--cpus=1.0`), max 64 PIDs (`--pids-limit=64`).
   - Hard execution timeout watchdog: 5–30 seconds. On expiration, asynchronous supervisor sends `SIGTERM` followed by `SIGKILL` after a 2-second grace period.
4. **Network Default-Deny Policy**:
   - Default network mode is isolated (`--network none`).
   - External network access requires explicit manifest capability declaration and human-in-the-loop (Maksym) cryptographic approval.

---

## 2. Zero-Trust Security & Vault Invariants

1. **Authentication (AuthN)**:
   - Stateless OAuth 2.0 / OIDC Bearer tokens with RS256 asymmetric signatures.
   - Access tokens have a 15-minute expiration; refresh tokens are stored in HTTP-only, `SameSite=Strict` cookies.
   - Mandatory WebAuthn (FIDO2) / TOTP MFA for administrative, founder (`maksym`), and destructive capabilities.
2. **Dynamic Secrets Broker (HashiCorp Vault / AWS Secrets Manager)**:
   - Absolute zero-secret persistence in source code, Docker images, Git trees, or local storage.
   - Secrets are leased dynamically via Vault sidecars, injected strictly as in-memory environment variables or temporary ramdisk mounts, and revoked immediately upon task termination.
3. **Cryptographic WORM Audit Trail**:
   - Every state change, authentication event, capability grant, and plugin execution is recorded in an append-only audit log.
   - Log entries are linked via SHA-256 hash chaining (`current_hash = SHA256(prev_hash + log_payload)`), guaranteeing tamper evidence.
   - Long-term storage configured with S3 Object Lock in Compliance Mode.

---

## 3. Observability & Golden Signals Protocol

1. **Prometheus Golden Signals**:
   - **Latency**: P50, P90, P99 tracked per HTTP route, WebSocket message, and container startup. Target p95 < 100ms for Canvas updates, < 1s for sandbox startup.
   - **Traffic**: Request rates (`http_requests_total`, `dnk_plugin_executions_total`).
   - **Errors**: Error rate threshold < 0.1% of total requests.
   - **Saturation**: Host and container CPU, memory usage, cgroup throttles, and PgBouncer connection pool depth.
2. **OpenTelemetry Distributed Tracing**:
   - Context propagation via W3C `traceparent` headers across client, API gateway, task queue, and sandbox container.
3. **Structured Logging (Loki / ELK)**:
   - Standard JSON schema with mandatory fields: `timestamp`, `level`, `trace_id`, `span_id`, `service`, `event_type`, and sanitized `payload`.

---

## 4. Elastic Scalability & Persistence Rules

1. **KEDA & Kubernetes HPA**:
   - Stateless API and Web nodes scale horizontally based on CPU/memory thresholds (target 70%).
   - Container execution workers scale based on queue depth metrics (`keda.sh/scaler: redis-list` or RabbitMQ depth).
2. **Redis 7.2 Cluster Multi-Tier Caching**:
   - Canvas graph states and node hierarchies cached in Redis with TTL and OCC version tracking.
   - Cache invalidation adheres to cache-aside pattern on database mutations.
3. **PostgreSQL 16 & PgBouncer Pooling**:
   - Dedicated connection pooling (Transaction mode) handling up to 5,000 active client connections.
   - Write operations routed to Primary; read-heavy queries, audits, and analytics routed to Read Replicas.

---

## 5. CI/CD & Zero-Regression Gates

1. **Pre-Commit & Build Gates**:
   - 100% test pass rate (`bash scripts/verify_all.sh`).
   - Zero critical or high severity CVEs detected by container scanners (Trivy / Snyk).
   - Immutable image signing via Cosign prior to deployment.
2. **Safe Deployment Strategies**:
   - Automated Canary or Blue-Green rollouts with automated rollback if error rate > 0.5% or latency increases by > 20% in the evaluation window.
3. **Disaster Recovery Targets**:
   - Recovery Time Objective (RTO) < 1 hour.
   - Recovery Point Objective (RPO) < 15 minutes (continuous WAL archiving).
