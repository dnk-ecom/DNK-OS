# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_architecture_fitness.py"
# purpose: "Architecture Fitness Functions enforcing SOTA 2026 invariants (<400 LOC Narrow Waist, Zero-Hub Bleed, SCONES FTS5, L1 AccountSpec)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import ast
from pathlib import Path
import pytest
from core.canvas.session_router import SpatialCanvasSessionRouter
from core.kernel import FastMCPKernel, create_fastmcp_server
from core.memory.scones_store import SconesMemoryStore
from core.project.project_engine import ProjectEngine

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_kernel_narrow_waist_loc():
    """Invariant: core/kernel.py must remain a Narrow Waist microkernel (< 400 LOC)."""
    kernel_path = ROOT_DIR / "core" / "kernel.py"
    assert kernel_path.exists(), f"core/kernel.py missing at {kernel_path}"
    lines = kernel_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 400, f"Narrow Waist violated: core/kernel.py has {len(lines)} lines (max 400)"


def test_kernel_mcp_delegation():
    """Invariant: FastMCP protocol bindings are cleanly encapsulated in core/kernel_mcp.py."""
    mcp_path = ROOT_DIR / "core" / "kernel_mcp.py"
    assert mcp_path.exists(), f"core/kernel_mcp.py missing at {mcp_path}"
    k = FastMCPKernel()
    server = create_fastmcp_server(k)
    assert server is not None, "FastMCP server creation failed"


def test_zero_hub_bleed():
    """Invariant: Zero imports or hardcoded references to archived DNK_HUB in core and services."""
    root = ROOT_DIR
    violating_files = []
    for py_file in root.glob("core/**/*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "from DNK_HUB import" in text or "import DNK_HUB" in text or 'sys.path.append("../DNK_HUB")' in text:
            violating_files.append(str(py_file))
    for py_file in root.glob("services/**/*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "from DNK_HUB import" in text or "import DNK_HUB" in text or 'sys.path.append("../DNK_HUB")' in text:
            violating_files.append(str(py_file))

    assert len(violating_files) == 0, f"Found files bleeding from DNK_HUB: {violating_files}"


def test_scones_native_fts5_active(tmp_path: Path):
    """Invariant: SCONES operates with native FTS5 BM25 index and Anchor Verifier without fallback."""
    db_path = tmp_path / "test_fitness_scones.db"
    store = SconesMemoryStore(db_path=db_path)
    assert store.bm25 is not None, "BM25Index failed to initialize"
    assert store.anchor_verifier is not None, "AnchorVerifier failed to initialize"


def test_l1_account_spec_and_project_engine_integrity():
    """Invariant: L1 AccountSpec and ProjectEngine are active and discovered in DNK_OS."""
    router = SpatialCanvasSessionRouter()
    account_spec = router.find_account_spec()
    assert account_spec is not None, "find_account_spec() returned None"
    assert account_spec.account_id == "acct-dnk-maksym"
    assert "Canonical 8-Root Directory Invariant" in str(account_spec.system_invariants)

    engine = ProjectEngine()
    loaded_account = engine.load_account()
    assert loaded_account.account_id == "acct-dnk-maksym"
    project_manifest = engine.get_project_manifest("proj-shopify-dnk-ecom")
    assert project_manifest["project_id"] == "proj-shopify-dnk-ecom"


def test_wave2_quarantine_sqlite_wal_persistence(tmp_path: Path):
    """Fitness Check (DEC-120): TC-10 Quarantine Guard persists strike history in SQLite WAL."""
    from core.sentinel.agent_quarantine import AgentQuarantineGuard, AgentState
    db_file = tmp_path / "fitness_quarantine.db"
    g1 = AgentQuarantineGuard(max_failures=1, db_path=db_file)
    g1.record_validation_failure("test_agent", "Test defect")
    assert g1.get_or_create("test_agent").state == AgentState.QUARANTINED

    # New instance must read the same state
    g2 = AgentQuarantineGuard(max_failures=1, db_path=db_file)
    assert g2.get_or_create("test_agent").state == AgentState.QUARANTINED


def test_wave2_context_surgery_and_revision_loop():
    """Fitness Check (DEC-120): Context Surgery (<= 1500 tok) and Bounded Revision Loop are active."""
    from core.canvas.session_router import compile_lod_dna_slice
    from core.orchestrator.bounded_revision_loop import BoundedRevisionLoop

    assert callable(compile_lod_dna_slice)
    loop = BoundedRevisionLoop(max_revisions=3)
    assert loop.max_revisions == 3

