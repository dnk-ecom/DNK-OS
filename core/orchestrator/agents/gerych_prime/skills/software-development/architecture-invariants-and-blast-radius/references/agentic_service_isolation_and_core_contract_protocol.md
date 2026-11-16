# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/agentic_service_isolation_and_core_contract_protocol.md"
# purpose: "Canonical architectural protocol for Core vs Autonomous Services boundary isolation, DNK Service Card, and Contract Testing in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-07"
# author: "DNK-e.com Maksym, DNK Mentor & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛡️ Agentic Service Isolation & Core Contract Protocol (v2.0.0)

## 1. Architectural Invariant: Zero-Knowledge Core
The system Core (`core/`) MUST NOT contain domain-specific knowledge, schemas, or documentation belonging to individual vertical services (e.g. Shopify, Liquid, Remotion, E-commerce, Marketing).

- **Core Responsibility**: Generic agent orchestration, task lifecycle, SCONES global memory, security guardrails, token budgeting, and the dynamic service discovery bus.
- **Service Responsibility (`services/<service_name>/`)**: Complete self-contained domain autonomy. The service owns its documentation, data models, AST parsers, API adapters, and isolated unit tests.

---

## 2. Directory Layout of an Autonomous Agentic Service (Golden-Path)
Each service directory under `services/` must be scaffolded from `templates/service/` and adhere to:

```text
services/<service_name>/
├── service_manifest.yaml         # DNK Service Card (SSOT passport for Core & Catalog)
├── README.md                     # High-level overview, ownership, quick start
│
├── docs/                         # Domain knowledge base
│   ├── SPECIFICATION.md          # Domain business rules, external API limits, data shapes
│   ├── ARCHITECTURE.md           # Internal AST parsers, component graphs, state lifecycle
│   └── RUNBOOK.md                # Local troubleshooting, verification commands, diagnostics
│
├── schemas/                      # Strict Pydantic contracts (Inbound / Outbound SSOT)
│   ├── contracts.py              # TaskInput, TaskOutput, Artifact models
│   └── domain_models.py          # Domain-specific AST and business objects
│
├── src/                          # Business logic & Domain execution engine
│   ├── router.py                 # FastAPI service router (Health, Tasks, Webhooks)
│   └── engine/                   # Specialized algorithms (e.g. Liquid AST, Video rendering)
│
├── tools/                        # Model Context Protocol (MCP) exported tools
│   └── service_tools.py          # Declarations published to Core Swarm Router
│
└── tests/                        # Autonomous test suite
    ├── test_core_contract.py     # 🛡️ CONTRACT GATE: Verifies Core compatibility before registration
    └── test_domain_logic.py      # Unit & integration tests for internal engine
```

---

## 3. The DNK Service Card Standard (`service_manifest.yaml`)
Replaces legacy flat JSON manifests. Governed by JSONSchema at `docs/schemas/service_card.schema.yaml`.

```yaml
apiVersion: dnk.os/v1alpha1
kind: ServiceCard
metadata:
  service_id: dnk_shopify
  name: "Shopify Storefront & Liquid AST Engine"
  description: "Autonomous service for Liquid AST engineering, section generation, and theme QA."
  version: "1.0.0"
  owner: "agent:dnk_shopify"              # agent:<id> | team:<id> | person:<id>
  tier: "tier-2-satellite"               # tier-1-core | tier-2-satellite | tier-3-community
  lifecycle: "production"                # experimental | incubating | production | deprecated

spec:
  domain: "ecommerce"
  entrypoint: "services.dnk_shopify.src.router:router"
  docs_path: "services/dnk_shopify/docs/SPECIFICATION.md"
  
  # Protocol contract declaration with explicit compatibility grade
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

## 4. Mandatory Verification & Contract Gates
1. **Service Card Schema Validation**: Every `service_manifest.yaml` is validated against `docs/schemas/service_card.schema.yaml` via:
   - Dynamic Contract Test Suite: `pytest tests/contracts/test_service_card_contract.py -v`
   - CLI Standards Validator: `./.venv/bin/python scripts/system/verify_service_standards.py [--service <name>] [--strict] [--json]`
2. **Local Contract Gate**: Every service contains documentation at `spec.docs_path` (e.g. `services/<service>/docs/SPECIFICATION.md`). Note: if any discovered manifest references a missing docs file, dynamic contract tests will fail-closed.
3. **MRH Header Format Invariant**: Markdown documentation (`.md`) must use HTML comment delimiters `<!-- --- DNK-MRH-HEADER --- ... -->` for compliance with `scripts/system/check_mrh_headers.py` (run with `--fix` if formatting needs alignment).

---

## 5. Local Service Contract Suite Pattern (`tests/test_core_contract.py`)
Every new service must provide an autonomous test suite validating:
- **Manifest Structure**: `apiVersion == "dnk.os/v1alpha1"`, `kind == "ServiceCard"`, valid `metadata` and `spec`.
- **7-Block Topology**: Confirms `README.md`, `docs/` (SPECIFICATION, ARCHITECTURE, RUNBOOK), `schemas/`, `src/router.py`, `tools/service_tools.py`, `tests/`, and `service_manifest.yaml` exist.
- **Pydantic Schemas Roundtrip**: Instantiates `TaskInput`, `TaskOutput`, and domain models without schema validation errors.
- **Tool Dispatch**: Executes exposed MCP tools directly in test mode to guarantee zero runtime import errors.

### Verification Recipe:
```bash
# Step 1: Run isolated contract tests
./.venv/bin/pytest services/<service_name>/tests/test_core_contract.py -v

# Step 2: Validate against SaaP system standards
./.venv/bin/python3 scripts/system/verify_service_standards.py --service <service_name>
```

---

## 6. Decoupling Platform Ingest from Core Analytical Engines (Anti-God-Service)
When building specialized analytical processors (such as `dnk_video_retention_auditor` for FFmpeg pacing, acoustic RMS dynamics, or hook retention), strictly decouple the analytical engine from third-party media ingestion:
1. **Analytical Engine Invariant**: The analytical service accepts only local media file paths, pre-cached assets, or structured payloads. It contains zero scraping logic, anti-bot bypass, or heavy platform SDKs (`yt-dlp`, Instagram Graph, TikTok API).
2. **Platform Ingest Invariant**: Ingest services (e.g. `dnk_youtube_auditor`) own video discovery, URL validation, transcript/subtitle extraction, and caching media files locally into `cache/<platform>_media/{media_id}.mp4`.
3. **Bounded Chunk Caching**: To avoid multi-gigabyte downloads during analytical testing or signal verification, ingest services should download only an initial bounded probe segment (e.g., first 60 seconds) using `yt-dlp` download range filters or `download_ranges` callbacks, alongside full lightweight transcript fetches.
4. **Namespace Isolation in Routers & Pytest Monkeypatching**: Avoid importing functions directly into `router.py` (e.g. `from .engine.fetcher import fetch_data`) when `src/__init__.py` exposes `router`, because `sys.modules["services.X.src"].router` resolves to the `APIRouter` instance instead of the module. Import modules as namespaces (`from .engine import fetcher`) and call `fetcher.fetch_data(...)` so test fixtures can cleanly monkeypatch `services.X.src.engine.fetcher.fetch_data`.
5. **Orchestration**: The Ingest Service or Orchestrator downloads the media, pre-fetches transcripts, and then delegates the analytical task to the engine via Agent Protocol (`POST /api/v1/<service>/audit`). This preserves blast radius isolation, keeps test suites fast (<1s), and eliminates runtime scraping failures in pure analysis pipelines.

