# --- DNK-MRH-HEADER ---
# mrh_id: "Justfile"
# purpose: "Unified developer command center for DNK OS: runtime bootstrap, test runner, brick scaffolding, and verification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-16"
# author: "Antigravity & Gerych & Maxim"
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

# Run Shopify workhorse 7-gate integrity tests
test-shopify:
    @uv run pytest services/dnk_shopify/tests -v

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
# 🌌 SPATIAL CANVAS & VIBE ORCHESTRATION
# -----------------------------------------------------------------------------

# Inspect the Shopify Vibe pipeline canvas DAG and node contexts
canvas-pipeline:
    @uv run python3 -c "from core.canvas.session_router import SpatialCanvasSessionRouter; from pathlib import Path; r = SpatialCanvasSessionRouter(); print('🌌 Shopify Vibe Pipeline:'); [print(f'  - {n}') for n in ['node_competitors', 'node_cro_audit', 'node_brand_dna', 'node_liquid_blocks']]"

# Execute a single canvas node through Sovereign Quad Runner
run-node canvas node_id summary="":
    @uv run python3 core/orchestrator/quad_runner.py {{canvas}} {{node_id}} {{summary}}
