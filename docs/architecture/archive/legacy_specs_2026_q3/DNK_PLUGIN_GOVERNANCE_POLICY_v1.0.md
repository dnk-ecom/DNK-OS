---
title: "Dnk Plugin Governance Policy V1.0"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_PLUGIN_GOVERNANCE_POLICY_v1.0.md"
> purpose: "Document: Dnk Plugin Governance Policy V1.0"
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
> # mrh_id: "docs/architecture/specs/DNK_PLUGIN_GOVERNANCE_POLICY_v1.0.md"
> # purpose: "Declarative Sandbox-First Plugin Governance Policy Specification v1.0 for DNK OS"
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-09"
> # author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# DNK OS Plugin Governance Policy v1.0 (Sandbox-First)

## 1. Executive Summary & Purpose

This specification defines the declarative governance policy layer governing the entire lifecycle of DNK OS plugins. 
To guarantee absolute runtime security, zero unverified execution, and strict tenant isolation, all plugins operate under a **Sandbox-First Default-Deny** paradigm.

Under no circumstances does an untrusted or uncertified plugin gain elevated permissions or direct access to system secrets, database engines, git write authorities, or unrestricted network sockets.

## 2. Plugin Lifecycle Architecture

The plugin lifecycle follows a deterministic, 5-stage unidirectional progression:

```text
[ draft ] ───► [ sandbox ] ───► [ evaluated ] ───► [ active ] ───► [ deprecated ]
    │                │                  │
    └────────────────┴──────────────────┴─────────────► [ deprecated ]
```

### 2.1 Lifecycle Stage Definitions & Minimal Invariants

| Lifecycle Stage | Security Profile | Mandatory Requirements & Invariants |
|-----------------|------------------|-------------------------------------|
| `draft` | `default-deny` | Syntactically valid Plugin Card, default-deny permissions (`secrets: none`, `git: none`, `database: none`, `external_write: none`). Minimal capabilities declaration. |
| `sandbox` | `default-deny` | Valid Card, isolated entrypoint, designated `contract_test_path`. Execution strictly isolated in sandbox harness. Default-deny permissions strictly enforced. |
| `evaluated` | `isolated-eval` | Green contract test suite, completed security review record (`security_review_path`), empirical evidence artifacts (`evidence_paths`). |
| `active` | `governed-least-privilege` | Explicit signed approval record from Maksym (`approved_by: "Maksym"`), passed contract tests, verified security review, evidence paths, certified SPDX license (unknown licenses forbidden), registered owner. |
| `deprecated` | `quarantined-read-only` | Documented `deprecation_reason` and optional replacement pointer. Execution disabled across all production runtimes. |

## 3. Security Model: Sandbox-First & Default-Deny

### 3.1 Strict Default-Deny Matrix

For `draft` and `sandbox` stages, permissions are strictly locked:

```yaml
permissions:
  filesystem: "none"      # Permitted values: "none" | "workspace_readonly"
  network: "none"         # Permitted values: "none" | "allowlist"
  secrets: "none"         # STRICTLY "none"
  git: "none"             # STRICTLY "none"
  database: "none"        # STRICTLY "none"
  external_write: "none"  # STRICTLY "none"
```

Any attempt to specify `secrets != none`, `git != none`, `database != none`, or `external_write != none` in `draft` or `sandbox` results in immediate validation failure.

### 3.2 Immutability & Self-Promotion Ban

1. **Self-Promotion Prohibited**: A plugin cannot modify its own lifecycle state or mutate its permissions. All transitions must be executed by the authorized system orchestrator or Maksym.
2. **Permission Expansion Control**: Any elevation of permissions beyond default-deny requires a discrete, signed policy approval record and adversarial review before transition.

## 4. Origin & Provenance Governance

Plugins must declare their origin category and fulfill specific provenance mandates:

- **`internal`**: Authored within DNK OS. `repository_url` must be `null`, `license_spdx` must be `"DNK-INTERNAL"`.
- **`open_source`**: Assimilated third-party packages. `repository_url`, `commit_sha`, and verified `license_spdx` (e.g. MIT, Apache-2.0, BSD-3-Clause) are mandatory. Unknown or unverified licenses are rejected.
- **`generated`**: Synthesized autonomously by LLM/Swarm agents. `provenance_note` referencing generation prompt, seed, or ADR is mandatory.
- **`vendor`**: Commercial or proprietary vendor integrations. Valid agreement/license reference required.

**License Invariant**: An unknown, ambiguous, or blank SPDX license (`license_spdx: "unknown"`) is strictly barred from ever reaching `active` lifecycle.

## 5. Declarative Plugin Card Schema

Each plugin must maintain a `plugin_card.yaml` adhering to `docs/schemas/dnk_plugin_card.schema.yaml`:

```yaml
schema_version: "dnk-plugin/v1.0"

id: "plugin-example-001"
name: "Example Plugin"
version: "0.1.0"
kind: "tool" # tool | memory | agent | service_adapter | ui_node | workflow

lifecycle: "draft" # draft | sandbox | evaluated | active | deprecated

origin:
  type: "internal" # internal | open_source | vendor | generated
  repository_url: null
  commit_sha: null
  license_spdx: "DNK-INTERNAL"
  assimilation_track: "internal"
  provenance_note: "docs/notes/102_plugin_sandbox_first_governance_v1_0.md"

entrypoint:
  type: "python" # python | mcp | http | container | frontend
  reference: "plugins/example_plugin:Plugin"

capabilities:
  provides:
    - "example.read"
  requires: []

permissions:
  filesystem: "none"
  network: "none"
  secrets: "none"
  git: "none"
  database: "none"
  external_write: "none"

governance:
  owner: "gerych_prime"
  risk_level: "low" # low | medium | high | critical
  approval_required_for_activation: true
  sandbox_profile: "default-deny"
  evidence_paths: []
  contract_test_path: null
  security_review_path: null
  approval_record: null
  deprecation_reason: null

compatibility:
  harness_api_version: "v0.1"
  required_core_capabilities: []
  conflicts_with: []
```

## 6. Verification & Governance Tooling

Policy compliance is verified deterministically via `scripts/system/plugin_policy.py`:

```bash
# Validate card syntax, schema, and security invariants
./.venv/bin/python3 scripts/system/plugin_policy.py validate templates/plugin/plugin_card.yaml

# Verify state transition legality
./.venv/bin/python3 scripts/system/plugin_policy.py check-transition \
  --from draft --to sandbox \
  --card templates/plugin/plugin_card.yaml
```

The CLI is purely declarative and analytical: it inspects cards, validates constraints, and checks policy. It never mutates the file or executes external code.
