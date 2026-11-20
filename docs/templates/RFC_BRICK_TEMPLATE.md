---
title: "RFC Brick Specification Template"
description: "Canonical RFC Specification Template for DNK OS Composable Bricks (RFC-BRICK-XXX)."
mrh_id: "docs/templates/RFC_BRICK_TEMPLATE.md"
status: Active
archetype: DEV_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - dnk/templates
  - dnk/brick-architecture
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/templates/RFC_BRICK_TEMPLATE.md"
> purpose: "Canonical RFC Specification Template for DNK OS Composable Bricks (RFC-BRICK-XXX)."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "Antigravity, Gerych Prime & DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> ```

# 🧱 RFC-BRICK-XXX: [Brick Name Specification]

> **DNK OS Modular Brick Architecture & Clean-Room Release Protocol**  
> Every brick intended for modular standalone export to `DNK_OS_APP` MUST have an approved RFC-BRICK specification.  
> Unspecified or non-compliant bricks are physically rejected at the Pre-Export Quality Gate.

---

## 🎯 1. Brick Identification & Metadata

- **Brick ID**: `brick_XX_[domain_name]` *(e.g. `brick_07_distribution_hub`)*
- **RFC ID**: `RFC-BRICK-[XXX]` *(e.g. `RFC-BRICK-007`)*
- **Display Name**: `[e.g. Postiz & Social Distribution Hub]`
- **Version**: `1.0.0`
- **Category**: `[agentic_core | memory_store | ui_canvas | ecommerce_engine | media_pipeline | api_gateway]`
- **Domain Alignment**: `[services/dnk_shopify | services/dnk_media | services/dnk_distribution | core/]`
- **Author / Swarm Agent**: `[Antigravity / gerych_builder / dnk_dev_fullstack]`
- **Status**: `[Draft | In Review | Approved | Exported]`

---

## 🛑 2. Negative Scope & Boundaries (Anti-Scope)

Explicitly declare what this brick is STRICTLY FORBIDDEN to do, touch, or assume:

- ❌ **Zero Unsanctioned Microservices**: Creating new root directories under `services/` is prohibited. Must map to the 3 Core Workhorses or `core/`.
- ❌ **Zero Absolute Paths**: Hardcoding `/Users/...` or home directories is strictly blocked. Use repo-relative paths only.
- ❌ **Zero Secret Leaks**: No `.env*` files (except `.env.example`), API keys, credentials, or local caches may be exported.
- ❌ **Zero Unbounded Dependencies**: Every external package must specify explicit version bounds (e.g. `pydantic>=2.7.0`).
- ❌ **Do NOT Touch**: `[List specific unrelated modules, e.g. services/dnk_shopify_builder, data/catalog.db]`

---

## 🗺️ 3. Target File Whitelist & Directory Layout

The exact files and directories managed by this brick that will be tracked in `brick.manifest.yaml` and exported to `DNK_OS_APP`:

| Path Type | Relative Path | Purpose / Module |
| :--- | :--- | :--- |
| `[MANIFEST]` | `core/bricks/brick_XX_[name]/brick.manifest.yaml` | Brick metadata, DAG deps, quality gate |
| `[CONTRACT]` | `core/bricks/brick_XX_[name]/contracts/schemas.py` | Pydantic v2 schemas and exchange contracts |
| `[ENGINE]` | `services/dnk_[domain]/[engine].py` | Core domain engine |
| `[SERVER]` | `services/dnk_[domain]/mcp_server.py` | FastMCP tool server |
| `[TEST]` | `tests/[domain]/test_[engine].py` | Quality Gate regression suite |

---

## ⛓️ 4. Dependency DAG & Version Compatibility

### 4.1 Internal Brick Dependencies (DAG)
List other DNK bricks that MUST be loaded and exported before this brick:
- `brick_02_scones_memory` *(if memory/caching is needed)*
- `brick_01_agentic_brain` *(if LLM reasoning is required)*

### 4.2 External Python Dependencies (with explicit version constraints)
```yaml
external_python:
  - "fastapi>=0.110.0"
  - "pydantic>=2.7.0"
  - "httpx>=0.27.0"
```

### 4.3 External NPM Dependencies (if UI/Vite components are bundled)
```yaml
external_npm:
  - "@xyflow/react>=12.0.0"
```

---

## 🔌 5. Contracts, Schemas & FastMCP Entrypoints (Architecture & Models)

### 5.1 Python Contracts (SSOT)
- Primary Request Model: `[e.g. DistributionTaskRequest]`
- Primary Response Model: `[e.g. DistributionTaskResponse]`
- Schema Path: `core/bricks/brick_XX_[name]/contracts/schemas.py`

### 5.2 FastMCP Entrypoints
- Tool 1: `[e.g. schedule_post(payload: PostPayload) -> PostResult]`
- Tool 2: `[e.g. query_channel_analytics(channel_id: str) -> AnalyticsResult]`

---

## 🛡️ 6. In-Target Quality Gate & Security Isolation (Invariants & Limits)

- **Test Suite Pattern**: `tests/[domain]/test_*.py`
- **Minimum Test Coverage**: `85%`
- **Contract Roundtrip Test**: Verifies JSON serialization/deserialization between FastMCP and Pydantic schemas.
- **Environment Isolation**: `TESTING=1` must be set during test execution. Tests must not depend on live external secrets.
- **Secret Sanitization**: Must successfully pass `export_standalone_app.py` secret audit without copying `.env*` or credentials.

---

## ✅ 7. Definition of Done (DoD) & Pre-Export Checklist

Before this brick can be exported via `python3 scripts/system/export_standalone_app.py`:

- [ ] `brick.manifest.yaml` exists and validates against `core/bricks/registry.py` schema.
- [ ] No cyclic dependencies exist in internal brick DAG (`resolve_dependencies`).
- [ ] All paths declared in `paths` physically exist in `DNK_HUB`.
- [ ] Unit tests pass 100% Green in isolation (`pytest <test_suite>`).
- [ ] Standalone export test passes: `python3 scripts/system/export_standalone_app.py --bricks brick_XX_[name] --target-dir /tmp/dnk_test_export`.
- [ ] In-target test run exits with code `0`.
- [ ] Zero `.env*` files leaked in target directory.
