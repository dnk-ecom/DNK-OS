---
title: "Dnk Service Specification Standard V1.0"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_SERVICE_SPECIFICATION_STANDARD_v1.0.md"
> purpose: "Document: Dnk Service Specification Standard V1.0"
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
> # mrh_id: "docs/architecture/specs/DNK_SERVICE_SPECIFICATION_STANDARD_v1.0.md"
> # purpose: "Canonical specification standard v1.0 for autonomous agentic services and Core boundary isolation in DNK OS."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-07"
> # author: "DNK-e.com Maksym, DNK Mentor & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ DNK Service Specification Standard v1.0

## 1. Executive Summary & Core Invariant

This specification defines the universal architecture, governance model, and communication protocols for **autonomous domain services** (`services/<service_name>/`) operating within the **DNK OS** ecosystem.

### Invariant 1: Zero-Bloat Core
The DNK OS Core (`core/`) is strictly an orchestrator, security gate, and global memory bus. It **MUST NOT** contain domain-specific knowledge, external third-party SDK dependencies (e.g. Shopify GraphQL, Remotion video rendering, CRM models), or vendor documentation.

### Invariant 2: Autonomous Domain Encapsulation
Every domain service under `services/` is an independently shippable, testable, and documentable unit of capability. It owns its internal AST engines, data schemas, tools, tests, and domain documentation.

---

## 2. Universal Service Architecture Layout

Every autonomous service adheres to the standard directory layout:

```text
services/<service_name>/
  service_manifest.yaml         # DNK Service Card (Metadata, Capabilities, APIs, Ops)
  README.md                     # High-level overview, ownership, quick start

  docs/                         # Domain knowledge base
    SPECIFICATION.md          # Domain business rules, external API limits, data shapes
    ARCHITECTURE.md           # Internal AST parsers, component graphs, state lifecycle
    RUNBOOK.md                # Local troubleshooting, verification commands, diagnostics

  schemas/                      # Strict Pydantic contracts (Inbound / Outbound SSOT)
    contracts.py              # TaskInput, TaskOutput, Artifact models
    domain_models.py          # Domain-specific AST and business objects

  src/                          # Business logic & Domain execution engine
    router.py                 # FastAPI service router (Health, Tasks, Webhooks)
    engine/                   # Specialized algorithms (e.g. Liquid AST, Video rendering)

  tools/                        # Model Context Protocol (MCP) exported tools
    service_tools.py          # Declarations published to Core Swarm Router

  tests/                        # Autonomous test suite
    test_core_contract.py     # 🛡️ CONTRACT GATE: Verifies Core compatibility before registration
    test_domain_logic.py      # Unit & integration tests for internal engine
```

---

## 3. The DNK Service Card (`service_manifest.yaml`)

The **DNK Service Card** is the single source of truth (SSOT) passport used by the Core's `ServiceRegistry` to discover, validate, and route tasks to the service.

### Full Schema Reference (`docs/schemas/service_card.schema.yaml`)

```yaml
apiVersion: dnk.os/v1alpha1
kind: ServiceCard
metadata:
  service_id: dnk_shopify
  name: "Shopify Storefront & Liquid AST Engine"
  description: "Autonomous service for Liquid AST engineering, section generation, and Shopify theme QA."
  version: "1.0.0"
  owner: "agent:dnk_shopify"              # Format: agent:<id> | team:<id> | person:<id>
  tier: "tier-2-satellite"               # tier-1-core | tier-2-satellite | tier-3-community
  lifecycle: "production"                # experimental | incubating | production | deprecated

spec:
  domain: "ecommerce"
  entrypoint: "services.dnk_shopify.src.router:router"
  docs_path: "services/dnk_shopify/docs/SPECIFICATION.md"
  
  # Protocol contract declaration
  protocol:
    task_api:
      standard: "agent-protocol"
      version: "v1"
      compatibility: "native"             # native | adapter | partial

  # Dependency references (Logical capabilities and vault secrets)
  depends_on:
    capabilities:
      - "core.security_gate"
      - "core.scones_memory"
    resources:
      - secret_ref: "shopify_admin_token" # Logical reference in Vault, NEVER raw secret

  # APIs & MCP tools published to the Core
  provides_apis:
    agent_protocol: "/api/v1/shopify/tasks"
    mcp_tools:
      - name: "shopify_validate_liquid"
        description: "Validates Liquid template code or file syntax for Shopify themes."
      - name: "shopify_generate_section"
        description: "Synthesizes an autonomous theme section with schema and CSS."

  # External upstream APIs consumed by this service
  consumes_apis:
    - name: "shopify_admin_graphql"
      version: "2026-07"
      type: "graphql"

  # Operational & Safety Envelope (SRE)
  operations:
    health_endpoint: "/api/v1/shopify/health"
    metrics_endpoint: "/api/v1/shopify/metrics"
    spend_guard:
      max_tokens_per_task: 50000
      max_cost_usd_per_run: 0.15
```

---

## 4. Interaction Protocols: Core ↔ Service

### 4.1 Model Context Protocol (MCP) — Tool Exposure
Each service registers its tools via standard MCP definitions. The Core does not need to know the underlying implementation; it consumes tool schemas generated by the service's `tools/` package.

### 4.2 Agent Protocol (AI Engineer Foundation) — Task Lifecycle
Asynchronous long-running domain jobs follow the standard Agent Protocol REST lifecycle:
- `POST /api/v1/<service>/tasks` — Creates an execution task with `TaskPayload`.
- `POST /api/v1/<service>/tasks/{task_id}/steps` — Executes an atomic step or returns streaming steps.
- `GET /api/v1/<service>/tasks/{task_id}/artifacts` — Retrieves generated artifacts (files, AST models, diffs).

### 4.3 Pydantic SSOT
All inbound and outbound payloads are strictly typed using Pydantic v2. Schema violations are caught at the boundary before executing domain code.

---

## 5. Contract Testing Gate (`test_core_contract.py`)

A service **CANNOT** be merged or loaded into Core production unless its `tests/test_core_contract.py` passes 100% Green.

The contract test verifies:
1. **Manifest Validation**: `service_manifest.yaml` validates cleanly against `docs/schemas/service_card.schema.yaml`.
2. **Docs Completeness**: `docs/SPECIFICATION.md`, `ARCHITECTURE.md`, and `RUNBOOK.md` are present.
3. **Health Check Probe**: Service router exposes a functioning `/health` endpoint returning `{"status": "healthy"}`.
4. **Tool Integrity**: Every tool declared in `spec.provides_apis.mcp_tools` exists, is importable, and provides valid parameter schemas.

System-level verification of all service cards is performed via:
```bash
pytest tests/contracts/test_service_card_contract.py
```

---

## 6. Operational & Safety Envelope

### SpendGuard Protection
Each service must declare hard ceilings in `spec.operations.spend_guard`:
- `max_tokens_per_task`: Limits context explosion and LLM run-away loops.
- `max_cost_usd_per_run`: Maximum allowable spend in USD per invocation. Core's SpendGuard terminates execution if exceeded.

### Secret & Credential Reference Policy
Services **NEVER** accept raw secrets or API keys in task payloads. All dependencies on sensitive tokens must use `secret_ref`, which the Core resolves dynamically via the encrypted Vault (`core/vault.py`).

---

## 7. Lifecycle & Deprecation Policy

| Stage | Definition | Core Routing Policy |
| :--- | :--- | :--- |
| `experimental` | Alpha development, contract subject to changes | Restricted to development environments |
| `incubating` | Feature-complete, undergoing contract and stress tests | Available for staging and opted-in swarms |
| `production` | Fully hardened, passing 100% contract tests | Standard default routing target |
| `deprecated` | Slated for removal, replacement service declared | Warning emitted; blocked for new workflows |

---

## 8. Golden-Path Scaffolding

To maintain uniformity, new services are generated exclusively from the golden template:
- Template Source: `templates/service/`
- All files include mandatory DNK-MRH headers.
- Contract test suites are pre-wired.
