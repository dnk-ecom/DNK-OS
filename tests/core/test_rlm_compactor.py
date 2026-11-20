# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_rlm_compactor.py"
# purpose: "Unit test suite for Prime Agent RLM Dynamic Context Compactor & Safe-Cut Trajectory Pruning."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from core.orchestrator.rlm_compactor import PrimeRLMCompactor
from core.canvas.session_router import SpatialCanvasSessionRouter


@pytest.fixture
def compactor():
    return PrimeRLMCompactor(default_max_tokens=500, target_retain_tokens=150)


def test_estimate_tokens():
    assert PrimeRLMCompactor.estimate_tokens("") == 0
    assert PrimeRLMCompactor.estimate_tokens("hello world") >= 2
    assert PrimeRLMCompactor.estimate_tokens("a" * 400) == 100


def test_safe_cut_index_avoids_tool_splitting(compactor):
    # Trajectory with tool call and result
    messages = [
        {"role": "user", "content": "Analyze the codebase for DEC-132"},
        {"role": "assistant", "content": "I will run git status", "tool_call_id": "call_01"},
        {"role": "tool", "content": "apps/web/page.tsx modified", "tool_call_id": "call_01"},
        {"role": "assistant", "content": "Now I will compile the blueprint"},
        {"role": "user", "content": "Check the verification command"},
        {"role": "assistant", "content": "Running verify_all.sh exit code 0"},
    ]

    # Cutting point should not land on index 2 (role="tool")
    cut_idx = compactor.find_safe_cut_index(messages, target_retain_tokens=15)
    assert cut_idx > 0
    assert messages[cut_idx]["role"] in ("user", "assistant")
    assert messages[cut_idx].get("role") != "tool"


def test_compaction_digest_extraction(compactor):
    discarded = [
        {"role": "user", "content": "We need to lock DEC-132 and DEC-133 in docs/architecture/DECISION_REGISTRY_ADHD.md"},
        {"role": "assistant", "content": "Fixed: Resolved translation mismatch on uk.json with exit code 0. Modified services/dnk_shopify/DNK_Sovereign_Apex/templates/customers/account.json."},
    ]
    digest = compactor.extract_compaction_digest(discarded)
    assert "DEC-132" in digest["locked_decisions"]
    assert "DEC-133" in digest["locked_decisions"]
    assert any("DECISION_REGISTRY_ADHD.md" in f for f in digest["touched_files"])
    assert digest["discarded_turns_count"] == 2


def test_compact_trajectory_under_threshold(compactor):
    messages = [
        {"role": "user", "content": "Short question"},
        {"role": "assistant", "content": "Short answer"},
    ]
    compacted, was_compacted, tel = compactor.compact_trajectory(messages, max_tokens=1000)
    assert was_compacted is False
    assert len(compacted) == 2


def test_compact_trajectory_over_threshold(compactor):
    # Generate long conversation
    long_msg = "Detailed technical explanation with many lines of code. " * 30
    messages = [
        {"role": "user", "content": f"First step: {long_msg} and DEC-120 was approved"},
        {"role": "assistant", "content": f"Second step: {long_msg} touching core/kernel.py"},
        {"role": "user", "content": f"Third step: {long_msg}"},
        {"role": "assistant", "content": "Recent short question"},
        {"role": "user", "content": "Recent short response"},
    ]
    compacted, was_compacted, tel = compactor.compact_trajectory(
        messages, max_tokens=200, target_retain_tokens=50, session_id="test_sess"
    )
    assert was_compacted is True
    assert tel["compacted"] is True
    assert tel["tokens_saved"] > 0
    assert compacted[0]["role"] == "system"
    assert "PRIME RLM COMPACTED CONTEXT" in compacted[0]["content"]
    assert "DEC-120" in compacted[0]["content"]


def test_session_router_compact_thread_integration(tmp_path: Path):
    db_file = tmp_path / "test_canvas_sessions.db"
    router = SpatialCanvasSessionRouter(db_path=db_file)
    session = router.get_or_create_session("canvas_test", "node_01", "builder")
    session_id = session.id

    # Add messages
    for i in range(10):
        router.post_message(
            session_id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Turn {i}: Technical analysis for DEC-13{i} touching core/adapters/bridge.py. " + "Lots of words. " * 20,
        )

    # Initial count
    msgs_before = router.get_messages(session_id)
    assert len(msgs_before) == 10

    # Execute compaction with small threshold
    tel = router.compact_thread(session_id, max_tokens=200)
    assert tel.get("compacted") is True
    assert tel.get("tokens_saved", 0) > 0

    # Pruned count in SQLite
    msgs_after = router.get_messages(session_id)
    assert len(msgs_after) < 10
    assert msgs_after[0].role == "system"
    assert "PRIME RLM COMPACTED CONTEXT" in msgs_after[0].content
