# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_repo_catalog.py"
# purpose: "Unit test for Repo Intelligence & SOTA Pattern Assimilation Engine in DNK_OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from core.registry.repo_catalog import search_repos, BilingualQueryExpander
from services.dnk_git_research.src.reuse_brief import ReuseBriefService
from core.kernel import create_fastmcp_server, FastMCPKernel


def test_bilingual_query_expansion():
    query = "відео монтаж анімація"
    clauses, domain_clauses = BilingualQueryExpander.expand_clauses(query)
    assert len(clauses) > 0
    expanded = BilingualQueryExpander.expand(query)
    assert "video" in expanded.lower()


def test_search_repos_fused_ranking():
    results = search_repos(query="shopify cart drawer", limit=5)
    assert len(results) > 0
    for r in results:
        assert "id" in r
        assert "maturity_tier" in r


def test_reuse_brief_service():
    svc = ReuseBriefService(live=False)
    brief = svc.build("shopify cart mutation queue", force=True)
    assert brief.mode.value in ("RESEARCH", "CACHED")
    assert len(brief.needs) > 0


def test_kernel_fastmcp_repo_tools(tmp_path):
    db_file = str(tmp_path / "test_action_bus.db")
    artifacts = str(tmp_path / "artifacts")
    kernel = FastMCPKernel(db_path=db_file, artifacts_dir=artifacts)

    mcp = create_fastmcp_server(kernel)
    assert mcp is not None
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "search_repo_catalog" in tool_names
    assert "get_repo_reuse_brief" in tool_names
