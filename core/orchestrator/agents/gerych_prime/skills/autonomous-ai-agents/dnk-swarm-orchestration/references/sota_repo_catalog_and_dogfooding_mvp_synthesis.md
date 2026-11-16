# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/sota_repo_catalog_and_dogfooding_mvp_synthesis.md"
# purpose: "Runbook and architectural protocol for standalone repo catalog FTS5 integration, zero-amnesia decision drafting, and dogfooding-first MVP verification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🏛️ SOTA Repo Catalog & Dogfooding MVP Synthesis Protocol

## 📌 Context & Purpose
When synthesizing a clean, standalone product (e.g. `DNK_OS_APP` / Product v1) from a vast R&D hub (`DNK_HUB`) and historical thought sessions (such as `20261015_142409_ed92ff`), the agent must extract and encapsulate the best architectural solutions without leaking workspace paths or creating fragile cross-repo dependencies.

This protocol codifies:
1. **Autonomous Knowledge & Repo Catalog Engine (`core/registry/repo_catalog.py`)** with SQLite WAL + FTS5 BM25 ranking.
2. **Zero-Discussion-Amnesia Decision Draft Engine (`core/orchestrator/decision_draft.py`)** enforcing 3 hidden risks, skeptic alternatives, and RFC-8785 canonical hash receipts.
3. **Dogfooding Integration Ladder**: Exposing capabilities through FastMCP tools, CLI subcommands (`python core/kernel.py --cli ...`), and REST API endpoints simultaneously.
4. **Standalone Quality Gate Invariant**: Enforcing 0 absolute paths, 0 hub leaks, 100% Markdown schema compliance, and 100% test pass rates under `scripts/verify_all.sh`.

---

## 🛠️ 1. Architecture of the 3-Tier SOTA Repo Catalog

To avoid dragging a 50MB external database into lightweight standalone client environments:

1. **Self-Contained Seed Golden Core (80 Archetypes)**:
   - Hardcode an in-memory / zero-external-dependency dictionary of Tier 1 Golden Core solutions:
     - `thoughtdag`: Graph of Thoughts, branch pruning, Kahn's cycle-free DAG execution.
     - `canvas-harness`: Role-scoped agent capsules, tool caps (`MAX_TOOLS=8`), token diet.
     - `tributary`: Causal tree layout, branch diffing, localization contracts.
     - `dim0`: Graph wiring, input/output port type validation (`Wire(from_node, to_node)`).
     - `dagster`: Context fingerprinting (SHA-256) and deterministic caching.
     - `skeleton-theme`: Theme Blocks 2.0 and Shopify Liquid AST transpilation.
2. **Local SQLite FTS5 WAL Index**:
   - Store locally in `.data/repo_catalog.db`.
   - On cold start, auto-migrate schema:
     ```sql
     CREATE VIRTUAL TABLE IF NOT EXISTS repos_fts USING fts5(
         slug, title, description, category, tags, maturity_tier
     );
     ```
   - If SQLite FTS5 module is unavailable in restricted environments, implement a transparent Python token-match fallback.

---

## 🛡️ 2. Zero-Discussion-Amnesia Decision Draft Engine

To eliminate cyclical debate and lost context across sessions:

1. **Input Contract**:
   - `decision_id`: Short unique handle (e.g. `DEC-012`).
   - `title`: Precise architectural title.
   - `proposed_solution`: Concrete proposed direction.
   - `context`: Background constraints.
2. **Mandatory Epistemic Armor (3 Risks + Skeptic Alt)**:
   - The engine automatically computes:
     - 3 hidden operational/security risks.
     - Boundary failure conditions.
     - Minimalist skeptic alternative.
3. **Receipt Issuance**:
   - Generates deterministic JSON string via RFC-8785 canonical keys.
   - Computes `RECEIPT-SHA256` = `sha256(canonical_json)[:16]`.
   - Appends locked record to `docs/architecture/DECISION_REGISTRY_ADHD.md` with status `[🔒 LOCKED]`.

---

## 🚀 3. Tri-Interface Dogfooding Matrix

Every core capability added to the standalone app must be reachable via three layers:

| Layer | Entry Point | Contract |
|---|---|---|
| **FastMCP** | `@mcp.tool()` in `core/kernel.py` | `search_repo_catalog(query, category, limit)`<br>`evaluate_decision_draft(decision_id, title, proposed_solution)` |
| **CLI** | `run_cli_command()` | `python core/kernel.py --cli catalog <query>`<br>`python core/kernel.py --cli decision <DEC-ID> <title> <solution>` |
| **REST API** | `apps/api/main.py` | `POST /api/v1/registry/repos/search`<br>`POST /api/v1/system/decision` |

---

## 🧪 4. Standalone Verification & Pitfall Avoidance

### Common Pitfalls
- **Async CLI Tests without `@pytest.mark.asyncio`**: Calling async CLI dispatchers in pytest tests raises unhandled coroutine warnings. Always mark async tests with `@pytest.mark.asyncio`.
- **ADR Metadata Drift in Schema Gates**: Markdown schema validators (`markdown_schema_gate.py`) often require specific frontmatter keys (`archetype`, `category`, `status`, `author`, `date`, `tags`). Ensure newly synthesized ADRs include all mandatory fields.
- **Leaked Absolute Paths**: Using `__file__` resolution or string paths that point to `/Users/...` will trip `verify_all.sh` Gate 1. Use relative path resolution (`Path(".").resolve()`) or repository root relative markers.
