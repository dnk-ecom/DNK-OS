# Graphify AST Blast Radius & Contract Alignment Guide

## Overview

`graphify` provides a local, token-free AST call and dependency graph parsed via Tree-sitter across Python and TypeScript codebases. It indexes modules, classes, functions, files, and method calls into a directed graph (`graphify-out/graph.json`).

## Key Commands for Refactoring & Audits

### 1. Reverse Blast Radius (`affected`)
Before modifying, renaming, or removing an API router, service, or core class, find every test and file that imports or references it:
```bash
graphify affected "apps/api/routers/canvas.py"
```
Output:
- Immediate list of all affected test files (e.g. `tests/canvas/test_canvas_api_and_ws.py`).
- Immediate list of importing modules (e.g. `apps/api/main.py`).

### 2. Dependency Call Path (`path`)
Trace the direct path between a client-facing module and a backend service:
```bash
graphify path "apps/web/components/Canvas.tsx" "apps/api/routers/canvas.py"
```

### 3. God Nodes Identification (`god-nodes`)
Identify architectural bottlenecks and high-centrality files:
```bash
graphify god-nodes --top 10
```

## Synergy: Triad Contract Alignment Protocol (Audit Slice 0.2-A)

When auditing API contracts between FastAPI and Next.js / frontend:
1. **Graphify AST Engine**: Extract static code dependencies, importers, and downstream tests in <200ms without tokens.
2. **FastAPI OpenAPI Introspection**: Generate normalized route endpoints (`GET /api/v1/...`), tags, and duplicate `operation_id` occurrences.
3. **Frontend String Scanner**: Search for client HTTP fetch URLs (`fetch('/api/...')`, `axios.get(...)`) in `apps/web/` to match declared routes with active consumers.
4. **Compile Contract Matrix**: Output structured mapping into `docs/audit/API_FRONTEND_CONTRACT_MAP_v0.1.md` and `.json`.

## Common Pitfall: The Triple Route Registration Anti-Pattern

When refactoring legacy FastAPI applications with high router counts, watch out for:
1. **Manual Root Mount**: `app.include_router(canvas.router)`
2. **Manual Prefixed Mount**: `app.include_router(canvas.router, prefix="/api")`
3. **Dynamic Autoloader Mount**: A `pkgutil.iter_modules()` loop that scans the routers folder and includes `mod.router` again!

**Symptoms**:
- Dozens of `UserWarning: Duplicate Operation ID` on server boot.
- Route aliasing where some UI components use `/canvas` and others `/api/canvas`.
- Ghost tests passing against legacy un-prefixed routes while production relies on `/api/`.

**Zero-Regression Remediation Procedure**:
1. Run `python3 scripts/audit_api_frontend_contracts.py` in read-only mode to generate `API_FRONTEND_CONTRACT_MAP_v0.1.json`.
2. Inspect `graphify affected "apps/api/routers/<router>.py"` to determine test blast radius.
3. Unify frontend clients on a single canonical client (`apiClient.ts` targeting `/api/v1`).
4. Replace dynamic autoloader with an explicit, single-mount canonical router registry.
5. Provide a temporary 307/308 redirect middleware for root routes during transitional testing.
