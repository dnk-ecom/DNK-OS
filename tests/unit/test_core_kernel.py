# --- DNK-MRH-HEADER ---
# mrh_id: "tests/unit/test_core_kernel.py"
# purpose: "Deterministic unit test suite for DNK OS FastMCPKernel, Action Bus, ThoughtDSL, and HITL gate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-24"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import asyncio
import pytest
from core.kernel import FastMCPKernel
from core.domain.identity_models import BrandDNA, VisualStyle, UserProfile


@pytest.fixture
def kernel(tmp_path):
    db_file = str(tmp_path / "test_action_bus.db")
    artifacts = str(tmp_path / "artifacts")
    return FastMCPKernel(db_path=db_file, artifacts_dir=artifacts)


def test_kernel_initialization(kernel):
    status = kernel.get_system_status()
    assert status["kernel_version"] in ("2.0.0", "2.5.0")
    assert status["status"] == "ACTIVE"
    assert status["user_soul"] == "Maxim (Architect / Owner)"


def test_thought_dsl_cycle_free_pipeline(kernel):
    dsl = """
    [hypothesis] H1: Clean Room Microkernel
    [critique] C1: Risk of excessive abstraction
    [synthesis] S1: Single Action Bus with SQLite WAL
    H1 -> C1
    C1 -> S1
    """
    res = kernel.parse_thoughts(dsl, graph_id="g_test")
    assert res["success"] is True
    assert res["has_cycles"] is False
    assert res["nodes_count"] == 3
    assert res["wires_count"] == 2

    # Verify context compiling along wires
    wire_res = kernel.compile_node_context_wire("g_test", "S1", max_tokens=1000)
    assert wire_res["success"] is True
    assert wire_res["target_node_id"] == "S1"
    assert wire_res["token_count"] > 0
    assert "Clean Room Microkernel" in wire_res["compiled_prompt"]
    assert "Risk of excessive abstraction" in wire_res["compiled_prompt"]


def test_thought_dsl_cycle_detection(kernel):
    cyclic_dsl = """
    [hypothesis] N1: First Node
    [hypothesis] N2: Second Node
    N1 -> N2
    N2 -> N1
    """
    res = kernel.parse_thoughts(cyclic_dsl, graph_id="g_cycle")
    assert res["success"] is False
    assert res["has_cycles"] is True
    assert set(res["cycle_nodes"]) == {"N1", "N2"}


@pytest.mark.asyncio
async def test_hitl_critical_action_gating(kernel):
    res = await kernel.dispatch_action("canvas.node.remove", {"node_id": "test_node"})
    assert res["status"] == "WAITING_APPROVAL"
    assert "Human-in-the-Loop" in res["message"]


def test_brand_dna_validation():
    style = VisualStyle(palette=["#16191c", "#34d399"], typography="Inter, Outfit")
    dna = BrandDNA(
        mission="AI-native OS for Creators",
        target_audience="Founders & Vibe Coders",
        visual_style=style,
        tone_of_voice="Direct, Technical, Elegant",
        negative_constraints=["No sycophancy", "No absolute paths"],
    )
    assert dna.visual_style.palette == ["#16191c", "#34d399"]

    # Invalid hex color raises ValueError
    with pytest.raises(Exception):
        VisualStyle(palette=["not-a-color"], typography="Inter")


@pytest.mark.asyncio
async def test_run_cli_command_status_and_thought(kernel, capsys):
    from core.kernel import run_cli_command

    code = await run_cli_command(kernel, ["status"])
    assert code == 0
    captured = capsys.readouterr()
    assert "kernel_version" in captured.out
    assert "ACTIVE" in captured.out

    dsl = """
    [hypothesis] H1: Hypothesis
    [synthesis] S1: Synthesis
    H1 -> S1
    """
    code2 = await run_cli_command(kernel, ["thought", dsl])
    assert code2 == 0
    captured2 = capsys.readouterr()
    assert "success" in captured2.out
    assert "graph_default" in captured2.out


def test_kernel_fastmcp_repo_search_and_brief(kernel):
    from core.kernel import create_fastmcp_server
    import json

    mcp = create_fastmcp_server(kernel)
    assert mcp is not None

    # Retrieve registered tool callables via list_tools or direct inspection
    # FastMCP stores tools in _tool_manager._tools or similar
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "search_repo_catalog" in tool_names
    assert "get_repo_reuse_brief" in tool_names
    assert "execute_code_mode" in tool_names
    assert "record_error_reflexion" in tool_names
    assert "query_error_solutions" in tool_names


@pytest.mark.asyncio
async def test_kernel_fastmcp_code_mode_and_reflexions(kernel):
    from core.kernel import create_fastmcp_server
    import json

    mcp = create_fastmcp_server(kernel)
    tools = {t.name: t.fn for t in mcp._tool_manager.list_tools()}

    # 1. Test execute_code_mode (Anthropic CE-MCP)
    code_snippet = """
total = 40 + 2
result = {"calculated": total, "status": "ok"}
print(f"Calculated answer: {total}")
"""
    exec_res_raw = tools["execute_code_mode"](code=code_snippet)
    exec_res = json.loads(exec_res_raw)
    assert exec_res["success"] is True
    assert exec_res["exit_code"] == 0
    assert "Calculated answer: 42" in exec_res["stdout"]
    assert exec_res["result"]["calculated"] == 42

    # 2. Test record_error_reflexion and query_error_solutions (SCONES Reflexion)
    rec_res_raw = await tools["record_error_reflexion"](
        tool_or_command="shopify theme check",
        symptom="MatchingTranslations error on uk.json",
        root_cause="Missing cart keys in secondary locale",
        solution="Merge en.default.json keys into uk.json",
    )
    rec_res = json.loads(rec_res_raw)
    assert rec_res["recorded"] is True
    assert "error_solution:shopify theme check" in rec_res["topic"]

    # Query reflexions
    query_res_raw = await tools["query_error_solutions"](query="shopify theme check")
    query_res = json.loads(query_res_raw)
    assert len(query_res) > 0
    obs_text = query_res[0]["observation"]
    assert "MatchingTranslations error" in obs_text
    assert "Merge en.default.json keys" in obs_text
