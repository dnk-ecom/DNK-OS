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

# Run comprehensive 7-vector SOTA 2026 Design System Benchmark audit
audit-sota:
    @~/.dnk_runtime/venv/bin/python3 scripts/system/audit_design_system_sota_2026.py

# Run SVAE v2.0 Autonomous YouTube Video Audit & Cross-Video Memory Synthesis
audit-video url:
    @~/.dnk_runtime/venv/bin/python3 scripts/system/audit_youtube_video.py "{{url}}"

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

# Run DSH Superagent assimilation test suite (DEC-151)
test-dsh:
    @uv run pytest tests/core/test_mandate_contracts.py tests/core/test_command_runner.py tests/core/test_transactional_outbox.py tests/core/test_github_source_adapter.py tests/core/test_denchik_builder_guard.py tests/core/test_outbox_worker.py -v

# Drain pending Transactional Outbox messages once (DEC-151)
outbox-drain:
    @uv run python3 -m core.outbox.worker --drain

# Run background Transactional Outbox Worker Daemon (DEC-151)
outbox-daemon:
    @uv run python3 -m core.outbox.worker --daemon

# -----------------------------------------------------------------------------
# 🛍️ SHOPIFY THEME DEV & MOLECULAR GRAFTING
# -----------------------------------------------------------------------------

# Run 7-Gate Anti-Regression Theme Integrity Gate on DNK Ecom theme or donor
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

# Install non-bypassable local git pre-commit hook enforcing all 8/8 checks (DEC-147)
install-hooks:
    @python3 scripts/system/install_git_hooks.py

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

# Run autonomous SOTA open-source assimilation pipeline (Spec + EGM + TaskDNA + Catalog)
sota-assimilate repo target="core":
    @uv run python3 services/dnk_git_research/cli.py sota-assimilate {{repo}} --target {{target}}

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

# Run live interactive demonstration of Dual-Surface Action Engine (Human <-> Agent <-> HITL)
demo-actions:
    @uv run python3 scripts/demo_dual_surface_live.py

# Hydrate and bootstrap quarantined external GPL services (AperiSolve etc.) in ../DNK_Vibe
hydrate-vibe:
    @uv run python3 scripts/system/hydrate_quarantined_services.py

# Check status of quarantined services without downloading
check-vibe:
    @uv run python3 scripts/system/hydrate_quarantined_services.py --check-only

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

# Check Google Cloud Vertex AI & Gemini authentication and model availability
agent-status:
    @uv run python3 scripts/system/google_agent_gateway.py --status

# Start local Universal Google Cloud Agent Gateway (OpenAI/Anthropic compatible bridge)
agent-gateway port="11436":
    @uv run python3 scripts/system/google_agent_gateway.py --server --port {{port}}

# Run any terminal agent through Google Cloud Vertex AI proxy environment
agent-run *args:
    @uv run python3 scripts/system/google_agent_gateway.py --run {{args}}

# Launch Denchik Sovereign Master Developer (Hermes Agent Runtime)
denchik *args:
    @bash scripts/system/denchik.sh {{args}}

# -----------------------------------------------------------------------------
# 🚀 DEPLOYMENT & PREVIEWS (Cloudflare Pages & GitOps)
# -----------------------------------------------------------------------------

# Safely publish all design systems and showcases to isolated dnk-preview branch & Cloudflare Pages
publish-preview:
    @bash scripts/system/publish_preview_branch.sh

# Deploy NOKU Commercial Proposal to Cloudflare Pages (https://noku-proposal.pages.dev)
deploy-noku-proposal:
    @pnpm dlx wrangler pages deploy docs/projects/dnk_ecom/proposals/noku_white --project-name=noku-proposal --branch=main --commit-dirty=true

# Scaffold a new secure, isolated client portal with Edge Password Gate
create-client-portal client_name:
    @uv run python3 scripts/system/create_client_portal.py --client {{client_name}}

# -----------------------------------------------------------------------------
# 🛍️ SHOPIFY INTELLIGENCE & CONTINUOUS SCOUT
# -----------------------------------------------------------------------------

# Fetch daily Shopify developer platform changelog and generate pulse report
daily-pulse limit="10":
    @uv run python3 scripts/shopify/shopify_daily_pulse.py --limit {{limit}} --save

# Parse and synthesize Shopify Chrome bookmarks into index & query DB
parse-bookmarks *args:
    @uv run python3 scripts/shopify/parse_shopify_bookmarks.py {{args}}

# -----------------------------------------------------------------------------
# 🌐 GEO, AI-SEARCH & SOCIAL COMMERCE (DEC-159 & DEC-160)
# -----------------------------------------------------------------------------

# Generate standard e-commerce llms.txt & Google Merchant XML feeds
geo-bundle out_dir="public":
    @uv run python3 -m services.dnk_distribution.cli llms-txt {{out_dir}}
    @uv run python3 -m services.dnk_distribution.cli merchant-feed {{out_dir}}/google_merchant_feed.xml

# Generate luxury 1200x630 social preview card (SVG) for chat apps
social-card title price currency="UAH" brand="DNK" usp="" out_path="assets/og_preview.svg":
    @uv run python3 -m services.dnk_media.cli social-card "{{title}}" "{{price}}" "{{currency}}" "{{brand}}" "{{usp}}" "{{out_path}}"

# Sign media asset with C2PA manifest & pure Python PNG metadata steganography
media-sign image author="DNK-e.com" alt_uk="" alt_en="":
    @uv run python3 -m services.dnk_media.cli sign "{{image}}" "{{author}}" "{{alt_uk}}" "{{alt_en}}"


