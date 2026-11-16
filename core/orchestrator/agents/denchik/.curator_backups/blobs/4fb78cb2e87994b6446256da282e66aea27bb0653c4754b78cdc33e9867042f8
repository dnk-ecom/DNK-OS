# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/spec_first_brick_extraction_and_sovereign_kernel_synthesis.md"
# purpose: "Protocol for synthesizing sovereign microkernels (DNK OS) from SOTA tools (OnePersonCompany, Scallopbot, FreeLLM) via Spec-First Clean-Room extraction instead of monolithic inheritance."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-25"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🏛️ Spec-First Brick Extraction & Sovereign Kernel Synthesis Protocol

## 1. Problem Statement: The Monolithic Inheritance Trap
When assimilating multi-agent platforms or all-in-one frameworks (e.g. `OnePersonCompany`, `Scallopbot`, `FreeLLMAPI`):
- **Naive Attempt**: Cloning the foreign repository directly into production or wrapping its entrypoints.
- **Consequences**:
  1. *Runtime Bloat*: Foreign dependency trees (Node 24+, heavy Python packages) pollute the 30–50MB lightweight target (e.g., `DNK_OS_APP`).
  2. *Monolithic Coupling*: Tight coupling between storage, UI, and orchestrator prevents adaptation to DNK OS invariants (FastMCP, SCONES SQLite WAL, Task Forest DAG).
  3. *Loss of Sovereign Control*: Upstream updates break local extensions; license compliance risks escalate.

## 2. The Spec-First Synthesis Architecture (Clean-Room ADR-007)

Instead of adopting foreign runtimes, execute the **Spec-First Clean-Room Invariant**:

```
[System Specification (Bus 1, 2, 3)] ──> [FTS5 Catalog Query] ──> [Selective Brick Extraction] ──> [Clean-Room Synthesis]
```

### Three Sovereign System Busses (The Target Spec):
1. **Control Bus (Bus 1)**: FastMCP tool interfaces & JSON-RPC action handlers. Zero ad-hoc REST endpoints for internal agent tools.
2. **State & Memory Bus (Bus 2)**: SCONES SQLite WAL database + Task Forest DAG execution graph. All state changes are bitemporal and queryable.
3. **UI / Canvas Bridge (Bus 3)**: React 19 / Vite / Tailwind UI with Canvas-to-Code synchronization. Pure decoupled client layer.

## 3. Case Studies: Extracted Bricks vs Rejected Runtimes

### Case A: `tashfeenahmed/OnePersonCompany` (Venture Portfolio Management)
- **Extracted Bricks (Clean-Room)**:
  - *Chief of Staff Daily Briefing Pattern*: Context synthesis prioritizing high-yield founder decisions.
  - *Venture Card & Metric UI*: Tailored React dashboard widgets for tracking venture statuses.
- **Rejected Runtime**:
  - Node 24 monorepo architecture, direct Stripe Webhook couplings, monolithic backend routes.

### Case B: `tashfeenahmed/scallopbot` (Agentic Autonomous Bot)
- **Extracted Bricks (Clean-Room)**:
  - *Bio-inspired Memory Decay & Consolidation*: Memory scoring algorithm with forgetting curves and retrieval thresholds.
  - *MCP-Native Routing Mechanism*: Tool invocation routing through isolated sub-agent prompts.
- **Rejected Runtime**:
  - Hardcoded Telegram-centric event loop and single-file agent dispatchers.

### Case C: `tashfeenahmed/freellmapi` (LLM Aggregation & Routing)
- **Extracted Bricks (Clean-Room)**:
  - *Failover & Multi-Provider Fallback Logic*: Deterministic ranking of free and low-cost LLM endpoints.
- **Rejected Runtime**:
  - Express/Koa custom HTTP server and rigid provider wrappers.

## 4. Execution Workflow for Swarm Agents

1. **Lock the Spec**: Define target schemas (Pydantic / TypeScript types) in `docs/specs/` before opening foreign repos.
2. **Scan Catalog via FTS5**: Search `catalog.db` specifically for the sub-problem (e.g., `sqlite3 catalog.db "SELECT ... FROM repo_fts WHERE repo_fts MATCH 'memory decay'"`).
3. **Isolate in Sandbox**: Shallow clone only into `../DNK_Vibe/<repo_name>/` (Sandbox Isolation Invariant).
4. **Extract Logic into Bricks**: Implement standalone adapter in `packages/` or `core/` adhering to target schemas.
5. **Verify with Machine Proof**: Run deterministic test suite (`verify_all.sh`) ensuring 0 weight increase and exit code 0.
