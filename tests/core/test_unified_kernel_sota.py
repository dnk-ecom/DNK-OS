# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_unified_kernel_sota.py"
# purpose: "Comprehensive test suite for Unified SOTA Microkernel v2.5 (Canvas Router, Fan-In, Quarantine, SCONES, FastMCP)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from pathlib import Path
from core.kernel import FastMCPKernel, create_fastmcp_server
from core.sentinel.agent_quarantine import QuarantineReason


@pytest.fixture
def kernel(tmp_path):
    db_path = str(tmp_path / "action_bus.db")
    artifacts_dir = str(tmp_path / "artifacts")
    k = FastMCPKernel(
        db_path=db_path,
        artifacts_dir=artifacts_dir,
        workspace_id="test_ws",
    )
    return k


def test_kernel_initialization_with_sota_subsystems(kernel):
    status = kernel.get_system_status()
    assert status["kernel_version"] == "2.5.0"
    assert status["status"] == "ACTIVE"
    assert "sota_subsystems" in status
    assert status["sota_subsystems"]["spatial_canvas_session_router"] == "ACTIVE"
    assert status["sota_subsystems"]["fan_in_aggregator"] == "ACTIVE"
    assert status["sota_subsystems"]["agent_quarantine_guard"] == "ACTIVE"
    assert status["sota_subsystems"]["scones_memory_fts5"] == "ACTIVE"


def test_node_session_messaging_and_crystallization(kernel, tmp_path):
    canvas_id = "test_canvas_001"
    node_id = "node_step_1"
    canvas_file = str(tmp_path / "test_canvas.canvas")

    # 1. Post messages to isolated node session
    res1 = kernel.post_node_message(canvas_id, node_id, role="user", content="Реалізуй Liquid блок")
    assert res1["status"] == "recorded"
    assert res1["session_id"] == f"node:{canvas_id}:{node_id}"

    res2 = kernel.post_node_message(canvas_id, node_id, role="assistant", content="Liquid блок готовий", artifact_refs=["snippets/block.liquid"])
    assert res2["status"] == "recorded"

    # 2. Retrieve messages
    messages = kernel.get_node_messages(canvas_id, node_id)
    assert len(messages) >= 2
    assert messages[0]["content"] == "Реалізуй Liquid блок"
    assert messages[1]["content"] == "Liquid блок готовий"

    # 3. Crystallize output summary
    c_res = kernel.crystallize_node_session(
        canvas_id,
        node_id,
        summary="Liquid блок успішно згенеровано та перевірено",
        artifact_refs=["snippets/block.liquid"],
        canvas_path=canvas_file,
    )
    assert c_res["status"] == "crystallized"
    assert c_res["crystallized_summary"] == "Liquid блок успішно згенеровано та перевірено"


def test_fan_in_aggregation_with_4_phase_validation(kernel):
    outputs = [
        {
            "agent_id": "dnk_shopify",
            "branch_name": "feature/theme",
            "content": "Theme Block updated and passed AST check",
            "exit_code": 0,
            "files_mutated": ["sections/announcement.liquid"],
            "claims": ["AST check exit code 0"],
            "code_snippets": ["def test_func():\n    return 42\n"],
        },
        {
            "agent_id": "dnk_dev_fullstack",
            "branch_name": "feature/api",
            "content": "FastAPI router mounted and verified",
            "exit_code": 0,
            "files_mutated": ["apps/api/routers/sample.py"],
            "claims": ["Router mounts cleanly"],
            "code_snippets": ["class SampleRouter:\n    pass\n"],
        },
    ]

    context = {
        "negative_scope": ["core/security/"],
        "grounding_evidence": ["AST check exit code 0", "Router mounts cleanly"],
    }

    synthesis = kernel.aggregate_branch_results(outputs, context=context, synthesis_instructions="Merge features cleanly")
    assert synthesis["passed"] is True
    assert synthesis["status"] == "approved_for_synthesis"
    assert len(synthesis["validation_results"]) >= 3
    assert len(synthesis["receipt_sha256"]) == 64


@pytest.mark.asyncio
async def test_agent_quarantine_circuit_breaker(kernel):
    agent_id = "rogue_agent_99"

    # Initially healthy
    rec = kernel.get_quarantine_record(agent_id)
    assert rec["state"] == "active"

    # Trip quarantine manually or via violation
    kernel.quarantine.trip_quarantine(
        agent_id,
        reason=QuarantineReason.NEGATIVE_SCOPE_VIOLATION,
        details="Attempted unauthorized mutation of core/security/",
    )

    rec_tripped = kernel.get_quarantine_record(agent_id)
    assert rec_tripped["state"] == "quarantined"

    # Dispatching an action as this agent should now be blocked
    res = await kernel.dispatch_action("test.mutation", {"file": "core/security/auth.py"}, requester=agent_id)
    assert res["status"] == "BLOCKED_BY_QUARANTINE"
    assert "QUARANTINED" in res["message"]

    # Release agent
    kernel.quarantine.release_agent(agent_id, approver="founder_maxim")
    rec_released = kernel.get_quarantine_record(agent_id)
    assert rec_released["state"] == "active"


def test_fastmcp_server_exposes_all_sota_tools(kernel):
    server = create_fastmcp_server(kernel, name="dnk-kernel-test")
    assert server is not None
    # FastMCP tools are registered via decorator
    tool_names = [t.name for t in server._tool_manager.list_tools()]
    expected_tools = [
        "dispatch_thought",
        "execute_action",
        "query_memory",
        "record_observation",
        "request_approval",
        "get_system_status",
        "node_session_get_context",
        "node_session_post_message",
        "node_session_crystallize",
        "fan_in_validate_and_aggregate",
        "quarantine_get_status",
        "quarantine_release_agent",
        "inspect_code_map",
        "prune_output",
        "search_clipboard",
        "get_clipboard_projects",
        "get_clipboard_screenshots",
    ]
    for exp in expected_tools:
        assert exp in tool_names, f"Expected FastMCP tool '{exp}' not found in server tools: {tool_names}"
