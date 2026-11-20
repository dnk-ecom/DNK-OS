---
title: "DNK OS Security Hardening Specification v1.0"
description: "Comprehensive Security Hardening Specification: Auth, RBAC, Secrets, Immutable Audit & Supply Chain for DNK OS"
mrh_id: "docs/architecture/production/security_hardening_spec.md"
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
> mrh_id: "docs/architecture/production/security_hardening_spec.md"
> purpose: "Comprehensive Security Hardening Specification: Auth, RBAC, Secrets, Immutable Audit & Supply Chain for DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛡️ DNK OS Security Hardening Specification v1.0

> **System:** DNK OS MVP — Production Hardening  
> **Sub-Phase:** Phase 3.2 (Zero-Trust Security & Governance)  
> **Target Compliance:** SOC 2 Type II / GDPR-Ready / CIS Benchmark  
> **Document Status:** Canonical Security Specification  

---

## 1. Zero-Trust Security Philosophy

DNK OS operates under a strict **Zero-Trust Architecture (ZTA)**. Neither internal services, autonomous swarm agents, nor user clients are implicitly trusted, regardless of physical or network location. Every interaction requires explicit cryptographic authentication, least-privilege authorization, and tamper-evident audit logging.

```
       +-------------------------------------------------------------+
       |   Client / Admin (Maksym) / Agent API Request               |
       +------------------------------+------------------------------+
                                      |
                                      v
  [ GATE 1: Authentication ] ──> JWT RS256 / OAuth2 / WebAuthn MFA
                                      |
                                      v
  [ GATE 2: Authorization ]  ──> RBAC + Plugin Capability ACL
                                      |
                                      v
  [ GATE 3: Secrets Broker ] ──> HashiCorp Vault / Dynamic Injection
                                      |
                                      v
  [ GATE 4: Isolation ]      ──> Ephemeral Docker Sandbox (Non-Root)
                                      |
                                      v
  [ GATE 5: Audit Log ]      ──> SHA-256 Hash-Chained WORM Audit Trail
```

---

## 2. Authentication (AuthN) Architecture

### 2.1 API & Human Authentication
- **OAuth 2.0 / OpenID Connect (OIDC)**: All interactive sessions and REST/WebSocket API requests authenticate using standard OAuth2 Bearer tokens with RS256 asymmetric signing.
- **Access Tokens**: Short-lived JWTs (lifespan: **15 minutes**). Token payload encodes tenant ID, user role, subject ID, and session nonce.
- **Refresh Tokens**: Long-lived (7 days), stored in HTTP-only, secure, `SameSite=Strict` cookies with automatic token rotation and reuse detection.

### 2.2 Multi-Factor Authentication (MFA)
- **Mandatory MFA Policy**: Multi-Factor Authentication is enforced for all administrative and owner roles (`admin`, `maksym`, `security_officer`).
- **Supported Factors**:
  1. **FIDO2 / WebAuthn**: Hardware security keys (YubiKey, Apple Touch ID / Passkeys).
  2. **TOTP (RFC 6238)**: Time-based One-Time Password via authenticator apps (1Password, Google Authenticator).
- **MFA Challenge Scope**:
  - Initial system login.
  - Step-up re-authentication required when executing sensitive operations:
    - Granting destructive plugin permissions (network egress, filesystem write).
    - Deploying or activating newly ingested plugins.
    - Exporting audit logs or modifying cryptographic keys.

---

## 3. Authorization (AuthZ) & Permission Matrix

### 3.1 Role-Based Access Control (RBAC)

| Role | Description | Canvas Operations | Plugin Operations | Secrets Access | Audit Access |
|---|---|---|---|---|---|
| **Owner / Founder** (`maksym`) | Full system authority, root governance | Full Read / Write / OCC Resolve | Author, Register, Approve, Execute | View Metadata / Rotate | Full WORM Export |
| **System Admin** (`admin`) | Infrastructure & platform administrator | Read / Layout Edit | Register, Verify, Sandbox Manage | Configure Providers | View & Alert |
| **Developer / Builder** (`developer`) | Plugin and agent workflow developer | Read / Edit own workspace nodes | Author, Test in Sandbox | Scoped Dev Secrets | View own logs |
| **Viewer / Auditor** (`viewer`) | Read-only compliance & telemetry viewer | Read-only (Pan/Zoom, View telemetry) | None (View manifest only) | None | Read-only Audit |

### 3.2 Fine-Grained Plugin-Level Permissions (Capability ACLs)
Plugins and autonomous agents are constrained by explicit Capability Grants defined in their signed manifests:

```yaml
capabilities:
  filesystem:
    read: ["/workspace/input.json"]
    write: ["/workspace/output/"]
  network:
    egress_enabled: false
    allowed_domains: []
  system:
    max_memory_mb: 512
    max_cpu_cores: 1.0
    timeout_seconds: 15
  secrets:
    permitted_keys: ["STRIPE_PUBLIC_KEY"] # Read-only, pre-scoped
```

---

## 4. Secrets Management Architecture

### 4.1 Secrets Storage: HashiCorp Vault / AWS Secrets Manager
- **Zero Secrets in Git / Environment**: Hardcoded API keys, database passwords, or private signing keys in git repositories or static `.env` files are strictly prohibited.
- **Vault Engine**: HashiCorp Vault (or AWS Secrets Manager with KMS encryption) is the centralized Single Source of Truth (SSOT) for all operational credentials.
- **Dynamic Ephemeral Secrets**: Database connections and cloud credentials utilize dynamic short-lived leases (e.g. 1-hour database credentials generated on-demand).

### 4.2 Runtime Secret Injection
- Secrets are NEVER persisted to the container image or written to host disk.
- Workers retrieve temporary secrets at the moment of execution via authenticated gRPC calls to the internal `dnk_vault_client`.
- When passed to a containerized sandbox, secrets are injected exclusively into a high-security in-memory filesystem (`tmpfs` with permission `0400`) or transient environment variable scrubbed immediately after process spawning.
- Process logs automatically redact all sensitive patterns (`sk_live_.*`, `ghp_.*`, `Bearer .*`) via an output stream regex filter.

---

## 5. Audit & Compliance Architecture

### 5.1 Immutable Audit Log (WORM Trail)
Every action within DNK OS—canvas node movement, plugin registration, sandboxed execution, approval decision, and role modification—is recorded in a Write-Once-Read-Many (WORM) audit ledger.

```json
{
  "audit_event_id": "evt_01HXYZ9876543210ABCDEF",
  "timestamp": "2026-09-10T12:00:00.000Z",
  "actor": {
    "user_id": "usr_maksym_001",
    "role": "maksym",
    "ip_address": "127.0.0.1",
    "user_agent": "DNK-Spatial-UI/1.0"
  },
  "action": "PLUGIN_EXECUTION_APPROVED",
  "target": {
    "entity_type": "plugin",
    "entity_id": "plg_shopify_sync_v2",
    "version": "2.1.0"
  },
  "context": {
    "approval_id": "appr_771829",
    "execution_id": "exec_99210",
    "capabilities_granted": ["filesystem.read", "network.egress"]
  },
  "prev_event_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "event_hash": "a54f128e6c9b1092a4...3b21"
}
```

### 5.2 Cryptographic Hash Chaining
- Each audit log entry includes the SHA-256 hash of the immediately preceding entry (`prev_event_hash`), creating an unalterable, append-only Merkle-style chain.
- Daily cryptographic anchors are signed with an offline GPG key and backed up to an immutable S3 bucket with Object Lock (Compliance Mode).

### 5.3 Regulatory Compliance Readiness
- **SOC 2 Type II**: Enforces controls for Security, Availability, Processing Integrity, and Confidentiality.
- **GDPR / Privacy by Design**: Data minimization in audit logs; user PII encrypted at rest using AES-256-GCM; explicit data retention and deletion policies.

---

## 6. Vulnerability Scanning & Supply Chain Defense

### 6.1 Container Image Vulnerability Scanning (Trivy / Snyk)
- All container base images and production service containers are scanned during CI build pipelines.
- **Blocking Gates**:
  - Any **Critical** or **High** CVE with an available vendor fix blocks the build immediately.
  - Builds must produce a signed Software Bill of Materials (SBOM) in SPDX and CycloneDX formats.

### 6.2 Automated Dependency Governance
- **Dependabot & Renovate**: Daily automated dependency monitoring scanning `pyproject.toml`, `package.json`, and Dockerfiles.
- **Pinned Hashes**: All Python wheels and npm packages must resolve to pinned cryptographic digests to prevent dependency hijacking or typosquatting attacks.
