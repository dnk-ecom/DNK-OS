---
title: "Domain Rules"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "packages/DOMAIN_RULES.md"
> purpose: "Document: Domain Rules"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# --- DNK-MRH-HEADER ---
# mrh_id: "packages/DOMAIN_RULES.md"
# purpose: "Domain governance rules, shared library standards, and export invariants for packages/."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# 📦 packages/ Domain Governance Rules

## 1. Purpose & Scope
The `packages/` domain contains pure, reusable libraries, shared SDKs, domain adapters, and foundational plugins.
- `packages/dnk_os`: Core contracts, schemas, and shared utilities
- `packages/adapters`: Third-party integration adapters (GitHub, Shopify, Redis, AI Providers)
- `packages/plugins`: Pluggable agent capabilities and extensible hooks
- `packages/archify`: Visual architecture and diagram generation engines
- `packages/swarm_simulation`: Multi-agent customer behavior & funnel simulation models
- `packages/video_audit_core` & `packages/teleprompter_core`: Video analytics and generation toolkits

## 2. Dependency Invariants
- ✅ **ALLOWED**: Self-contained internal utilities and standard library dependencies.
- ✅ **ALLOWED**: Export clean Python modules accessible via `$PYTHONPATH`.
- ❌ **FORBIDDEN**: Upward imports from `apps/` or `services/`. Packages must be pure providers, never consumers of application state.
- ❌ **FORBIDDEN**: Side-effects upon module import (e.g. initiating database connections or spawning background threads immediately at top-level import).
- ❌ **FORBIDDEN**: Absolute file paths (`/Users/...`).

## 3. Engineering Standards
- All packages should provide clean `__init__.py` exposing only public symbols via `__all__`.
- Type annotations (`typing`) and docstrings are mandatory for public APIs.

## 4. Verification Gate
```bash
# Run package unit tests
pytest tests/plugins/ -q
```
