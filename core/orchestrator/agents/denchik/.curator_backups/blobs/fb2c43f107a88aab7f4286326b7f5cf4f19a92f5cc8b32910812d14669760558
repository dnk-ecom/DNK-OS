# Repository Topology Audit, Graphify Orphan & Duplicate Elimination Protocol

## 1. Overview & Context

In large evolving monorepositories (>15,000 files across multiple languages), codebase sprawl, orphaned modules, copy-pasted implementations, and monolithic God-nodes degrade developer velocity, inflate LLM context windows, and increase regression risk.

This protocol defines the canonical, zero-waste process to audit, map, clean, and consolidate complex directory structures using **Graphify AST Dependency Graphs**, deterministic clone detection, and multi-agent swarm verification without breaking production tests.

---

## 2. The Triad of Codebase Hygiene

A complete repository audit requires combining three complementary engineering layers:

| Layer | Primary Tool | Role & Scope | Token Cost |
| :--- | :--- | :--- | :--- |
| **1. AST Call & Dependency Graph** | **Graphify** (`Graphify-Labs`) / Tree-sitter | Maps directed invocation topology, identifies in-degree=0 (Orphan candidates), detects God-nodes, and calculates reverse blast radius (`graphify affected`). | **0 tokens** (Local AST) |
| **2. Dead Code & Clone Detectors** | **jscpd** (Clones), **Knip** (TS/JS), **Vulture** (Python) | Locates physical text/token code duplicates across folders and flags unexported/unused functions, types, and dependencies. | **0 tokens** (Deterministic CLI) |
| **3. Multi-Agent Swarm Verification** | **Gerych Swarm** (`gerych_auditor`, `gerych_researcher`, `dnk_dev_fullstack`) | Reasoned consolidation plans, architecture mapping in Obsidian/SCONES, AST-safe refactoring, and fail-closed test gating (`verify_all.sh`). | Controlled budget (MASE) |

---

## 3. Four-Phase Stepwise Audit & Elimination Pipeline

### Phase 1: Zero-Token Deterministic Filesystem Inventory
*Never feed 17,000 raw file paths into an LLM context.*
Execute a lightweight Python script (`scripts/system/audit_dnk_hub_topology.py`) to generate `artifacts/audit/DNK_HUB_INVENTORY.json`:
1. **8 Canonical Roots Validation**: Partition by `apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`.
2. **SHA-256 Exact Duplicate Detection**: Hash every file excluding `.git`, `node_modules`, `.venv`, and `__pycache__` to identify 100% identical files immediately.
3. **Artifact & Giant File Scan**: Identify orphaned binary blobs, large unindexed JSON dumps (>1MB), and missing `.gitignore` coverage.
4. **MRH Header Compliance**: Check compliance with `DNK-STD-0075`.

### Phase 2: AST Topological Graph Extraction & Candidate Ledger
1. Run local headless extraction:
   ```bash
   graphify extract . --code-only
   ```
2. Classify graph nodes:
   - **Orphan Nodes (`in_degree == 0`)**: Modules or classes that are never imported or called. Exclude entry points (`main.py`, `page.tsx`, `test_*.py`, CLI scripts).
   - **God Nodes**: High-centrality architectural bottlenecks (top degree centrality). Flag for decomposition.
   - **Subsystem Communities**: Topological clusters discovered via Leiden/Louvain community detection.
3. Generate the **Audit Action Ledger**:
   - `[KEEP]`: Active, well-referenced components.
   - `[PRUNE]`: Orphaned files with verified 0 references and 0 dynamic registrations.
   - `[CONSOLIDATE]`: Multi-instance duplicate modules (e.g. utilities in `apps/` vs `services/`).

### Phase 3: Hierarchical Obsidian & SCONES Architecture Mapping
1. Create/update architecture documentation at root-level and 2nd-level directory boundaries (`./docs/notes/repo_map/` or `.canvas` graph).
2. Each module entry must document:
   - Purpose and ownership.
   - Canonical entry points.
   - Core inbound and outbound dependencies.
3. Ingest foundational architectural patterns into SCONES memory (`scones_add_memory`).

### Phase 4: Swarm MASE (Mandatory Atomic Slice Execution) & Safe Migration
All mutations must occur in atomic slices (<= 25 tool calls):
1. **Audit Gate**: Before removing or modifying any file:
   ```bash
   graphify affected "<target_file>"
   ```
   If affected nodes > 0, verify and update all callers or corresponding tests first.
2. **Consolidation**: Move shared logic into canonical shared packages (`packages/` or `core/`).
3. **Fail-Closed Verification**:
   ```bash
   bash scripts/verify_all.sh
   ```
   Must remain **100% Green** before committing. No orphan file may be pruned without green tests.

---

## 4. Key Pitfalls to Avoid

1. **Blind Deletion of Dynamic Imports**: FastAPI router auto-discovery, CLI plugin loaders, or runtime reflection may not produce static AST edges in Graphify. Always cross-check entry points before marking a file as dead.
2. **Monolithic Audit LLM Context Dump**: Attempting to list all files across an entire repository in a single prompt causes token budget exhaustion (budget breach) and hallucinated file paths. Always use deterministic JSON inventory artifacts.
3. **Unverified Duplication Merges**: Merging two slightly divergent files without checking call signatures can break downstream callers. Always rely on `graphify affected` and run targeted pytest suites.

---

## 5. Production-Hardened Ballast & Symlink Consolidation Patterns

### 1. SQLite Database Vacuuming & Rotated Log Sanitation
Before executing AST analysis or code modifications, reclaim local disk ballast from long-running agent persistence databases:
```bash
# Compact agent SQLite state database (reclaims fragmented pages)
sqlite3 "core/orchestrator/agents/gerych_prime/state.db" "VACUUM;"

# Prune rotated telemetry logs
rm -f core/orchestrator/agents/gerych_prime/logs/*.log.*
```

### 2. Protected Entrypoint Invariant Gate (In-Degree = 0)
When scanning for orphan candidates with `in-degree == 0`, never mark a node for removal if it matches any of the following runtime contracts:
- **FastAPI / Starlette Routers**: `@router.get`, `@router.post`, `APIRouter()`
- **App Factories & Servers**: `FastAPI()`, `create_app()`, `@app`
- **FastMCP Tool Definitions**: `@mcp.tool`, `FastMCP()`
- **CLI & Module Entrypoints**: `if __name__ == '__main__':`, `def main():`, `__init__.py`
- **Next.js / Framework Routing**: `page.tsx`, `layout.tsx`, `route.ts`, `route.js`, `page.js`, `middleware.ts`
- **Database Migrations**: Alembic / SQL migration scripts

### 3. Relative Symbolic Link Consolidation for Identical Multi-Megabyte Assets
When consolidating 100% identical large templates or assets across sibling folders (e.g., multi-theme Shopify sections `featured-product.liquid`):
```bash
# Verify 0 broken blast radius
~/.local/bin/graphify affected "featured-product.liquid" --graph services/graphify-out/graph.json

# Replace duplicate with relative symbolic link pointing to canonical SSOT
ln -sf ../../DNK-e.com/sections/featured-product.liquid services/dnk_shopify/DNK_Horizon_Tinker/sections/featured-product.liquid
```
This guarantees 100% build tool and test compatibility while instantaneously eliminating thousands of duplicate lines and megabytes of git bloat.

### 4. JSON MRH Compliance Standard (DNK-STD-0075)
When storing structured audit ledgers in JSON (`docs/audit/*.json`), encapsulate the MRH header in an `_mrh` dictionary to ensure `python3 scripts/system/check_mrh_headers.py` passes:
```json
{
  "_mrh": {
    "mrh_id": "docs/audit/GRAPHIFY_ORPHAN_CANDIDATES.json",
    "purpose": "Graphify AST reachability scan ledger",
    "status": "Active",
    "version": "1.0.0",
    "author": "Gerych Prime & DNK Swarm"
  },
  "safe_orphan_candidates": [...]
}
```
