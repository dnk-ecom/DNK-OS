# --- DNK-MRH-HEADER ---
# mrh_id: "Justfile"
# purpose: "Unified developer command center for DNK OS: runtime bootstrap, test runner, brick scaffolding, and verification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

export PYTHONPATH := "."

# Default goal: list available commands
default:
    @just --list

# -----------------------------------------------------------------------------
# 🛡️ VERIFICATION & TESTS
# -----------------------------------------------------------------------------

# Run all core SOTA unit tests in strict isolation
test:
    @uv run pytest tests/core -v

# Run Architecture Fitness Functions (Narrow Waist < 400 LOC, Zero Hub Bleed, SCONES FTS5)
test-fitness:
    @uv run pytest tests/core/test_architecture_fitness.py -v

# Run Shopify workhorse 7-gate integrity tests
test-shopify:
    @uv run pytest services/dnk_shopify/tests -v

# Run Media workhorse tests
test-media:
    @uv run pytest services/dnk_media/tests -v

# Run Distribution workhorse tests
test-distribution:
    @uv run pytest services/dnk_distribution/tests -v

# Run all 3 workhorse tests in parallel
test-workhorses:
    @uv run pytest services/dnk_shopify/tests services/dnk_media/tests services/dnk_distribution/tests -v

# -----------------------------------------------------------------------------
# 🛍️ SHOPIFY THEME DEV & MOLECULAR GRAFTING
# -----------------------------------------------------------------------------

# Run 7-Gate Anti-Regression Theme Integrity Gate on DNK Sovereign Apex or donor
shopify-7gate theme="":
    @uv run python3 -c "from services.dnk_shopify.src.service import DNKShopifyService; from pathlib import Path; s = DNKShopifyService(default_theme_path=Path('{{theme}}') if '{{theme}}' else None); r = s.run_7gate_integrity(); print(r['stdout']); exit(r['exit_code'])"

# Synchronize Donor Genome Map and update live audited donor catalog
shopify-donor-map:
    @python3 ../DNKEcom/Audit_Shopify_Themes_Sell_WF/_Shopify_Theme_DEV_Workflow/tools/sync_donor_genome_map.py

# Run molecular graft tool against DNK-Ecom donor worktrees
shopify-graft *args:
    @cd ../DNKEcom/DNK-Ecom_git_mirrow && ./graft.sh {{args}}

# Run offline sub-millisecond local-storefront Liquid runtime check
shopify-lsf-check theme="":
    @uv run python3 -c "from services.dnk_shopify.runtime.local_storefront import LocalStorefrontManager; from services.dnk_shopify.src.service import DNKShopifyService; from pathlib import Path; s = DNKShopifyService(default_theme_path=Path('{{theme}}') if '{{theme}}' else None); m = LocalStorefrontManager(); res = m.run_check(s.default_theme_path); print(res.get('stdout') or res.get('stderr')); exit(res['returncode'])"

# Run Spatial Canvas per-node isolation and context surgery tests
test-canvas:
    @uv run pytest tests/core/test_spatial_canvas.py -v

# -----------------------------------------------------------------------------
# ⚙️ WORKSTATION RUNTIME (APFS 4-ZONE)
# -----------------------------------------------------------------------------

# Bootstrap the zero-waste runtime directory in ~/.dnk_runtime/
bootstrap-runtime:
    @echo "⚙️ Ініціалізація 4-зонального рантайму ~/.dnk_runtime/..."
    mkdir -p ~/.dnk_runtime/{uv-cache,pnpm-store/v10,venvs,worktrees,tools,run,logs}
    touch ~/.dnk_runtime/.metadata_never_index
    @echo "✅ Рантайм готовий. Spotlight заблоковано (.metadata_never_index)."

# Check workspace hygiene and status
status:
    @echo "🛡️ Перевірка стану системи..."
    @python3 -c "import os; print('Canonical 8 Roots Check: ' + ('PASS' if all(os.path.exists(d) for d in ['core','services','packages','apps','docs','tests','scripts','infra']) else 'FAIL'))"
    @just --version

# -----------------------------------------------------------------------------
# 🧱 SOVEREIGN BRICK SCAFFOLDING (1-CLICK CREATION)
# -----------------------------------------------------------------------------

# Scaffold a new sovereign brick with 5 standard elements
new-brick name:
    @python3 scripts/system/new_brick.py {{name}}

# -----------------------------------------------------------------------------
# 🔍 REPO INTELLIGENCE & SOTA PATTERN SEARCH (1,663 REPOSITORIES)
# -----------------------------------------------------------------------------

# Search repository catalog using bilingual FTS5 expansion
repo-search query domain="":
    @uv run python3 -c "from core.registry.repo_catalog import search_repos; [print(f'★ {r[\"id\"]} [{r.get(\"maturity_tier\",\"-\")}]: {r.get(\"title\",\"\")[:60]}') for r in search_repos('{{query}}', domain='{{domain}}' or None, limit=10)]"

# Generate JIT prior-art reuse brief before writing code
repo-brief task:
    @uv run python3 -c "from services.dnk_git_research.src.reuse_brief import ReuseBriefService, format_brief_text; print(format_brief_text(ReuseBriefService(live=False).build('{{task}}', force=True)))"

# Audit documentation for dead or stale code file references (SOTA Staleness Eviction)
audit-knowledge dir="docs":
    @uv run python3 -c "from core.sentinel.knowledge_staleness_guard import KnowledgeStalenessGuard; g = KnowledgeStalenessGuard(); r = g.audit_directory(g.root / '{{dir}}'); print(f'🛡️ Knowledge Staleness Audit: {r.scanned_docs_count} docs scanned, {r.valid_count} valid refs, {r.stale_count} stale refs.'); [print(f'  - [{s.doc_path}:{s.line_number}] -> {s.referenced_path}') for s in r.stale_items[:10]]"

# Run interactive live verification test across all 5 core subsystems
live-test:
    @uv run python3 scripts/system/live_system_test.py

# -----------------------------------------------------------------------------
# 🌌 SPATIAL CANVAS & VIBE ORCHESTRATION
# -----------------------------------------------------------------------------

# Inspect the Shopify Vibe pipeline canvas DAG and node contexts
canvas-pipeline:
    @uv run python3 -c "from core.canvas.session_router import SpatialCanvasSessionRouter; from pathlib import Path; r = SpatialCanvasSessionRouter(); print('🌌 Shopify Vibe Pipeline:'); [print(f'  - {n}') for n in ['node_competitors', 'node_cro_audit', 'node_brand_dna', 'node_liquid_blocks']]"

# Execute a single canvas node through Sovereign Quad Runner
run-node canvas node_id summary="":
    @uv run python3 core/orchestrator/quad_runner.py {{canvas}} {{node_id}} {{summary}}

# Compile node session context with L2 Project DNA and upstream contracts
node-context canvas node_id:
    @uv run python3 core/kernel.py --cli node context {{canvas}} {{node_id}}

# Post message to an isolated node chat session
node-post canvas_id node_id role message:
    @uv run python3 core/kernel.py --cli node post {{canvas_id}} {{node_id}} {{role}} "{{message}}"

# Read discussion messages for an isolated node chat session
node-messages canvas_id node_id limit="50":
    @uv run python3 core/kernel.py --cli node messages {{canvas_id}} {{node_id}} {{limit}}

# Crystallize node output contract into .canvas and SQLite WAL
node-crystallize canvas node_id summary artifacts_json="[]":
    @uv run python3 core/kernel.py --cli node crystallize {{canvas}} {{node_id}} "{{summary}}" '{{artifacts_json}}'

# -----------------------------------------------------------------------------
# 🌐 API SERVER & FASTMCP
# -----------------------------------------------------------------------------

# Start the DNK OS Microkernel FastAPI server on port 8000
api:
    @uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run the Microkernel FastMCP server over STDIO (for Antigravity/Hermes/Claude)
mcp-stdio:
    @uv run python3 core/kernel.py

# Launch Denchik Sovereign Master Developer (Hermes Agent Runtime)
denchik *args:
    @bash scripts/system/denchik.sh {{args}}
