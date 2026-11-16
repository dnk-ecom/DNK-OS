# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_bounded_revision_loop.py"
# purpose: "Senior Unit Tests for Bounded Revision Loop FSM (Builder <-> Auditor 3-strike cycle)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from core.canvas.session_router import SpatialCanvasSessionRouter
from core.orchestrator.bounded_revision_loop import BoundedRevisionLoop, RevisionLoopState
from core.orchestrator.fan_in_aggregator import (
    AgentOutput,
    FanInAggregator,
    SyntaxASTValidator,
    DeterministicExitCodeValidator,
)
from core.sentinel.agent_quarantine import (
    AgentQuarantineGuard,
    AgentQuarantinedError,
)


@pytest.fixture
def revision_test_env(tmp_path: Path):
    db_path = tmp_path / "rev_sessions.db"
    canvas_path = tmp_path / "rev_pipeline.canvas"

    canvas_data = {
        "nodes": [
            {
                "id": "node_builder_task",
                "type": "text",
                "text": "### Task 1: Build Module\n**Agent**: `denchik`\nSynthesize clean python module.",
                "x": 0,
                "y": 0,
                "width": 300,
                "height": 200,
            }
        ],
        "edges": [],
    }
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")

    router = SpatialCanvasSessionRouter(db_path=db_path)
    quarantine = AgentQuarantineGuard(max_failures=3, db_path=tmp_path / "quarantine.db")
    aggregator = FanInAggregator([
        SyntaxASTValidator(),
        DeterministicExitCodeValidator(),
    ])

    loop = BoundedRevisionLoop(
        aggregator=aggregator,
        quarantine_guard=quarantine,
        session_router=router,
        max_revisions=3,
    )

    return loop, canvas_path, router, quarantine


def test_revision_loop_first_attempt_pass(revision_test_env):
    """Verify clean single-pass approval on first attempt."""
    loop, canvas_path, router, quarantine = revision_test_env

    def builder_pass(attempt: int, remediation):
        return [
            AgentOutput(
                agent_id="denchik",
                task_id="t1",
                summary="Clean module",
                produced_files={"module.py": "def clean():\n    return 42\n"},
                command_results=[{"command": "pytest", "exit_code": 0}],
            )
        ]

    result = loop.execute_loop(canvas_path, "node_builder_task", builder_pass)
    assert result.passed is True
    assert result.status == RevisionLoopState.APPROVED
    assert result.total_revisions == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].passed is True

    # Check that session received approval feedback
    session_id = router.format_session_id(canvas_path.stem, "node_builder_task")
    msgs = router.get_messages(session_id)
    assert any("APPROVED on attempt 1/3" in m.content for m in msgs)


def test_revision_loop_self_healing_on_second_attempt(revision_test_env):
    """Verify Bounded Revision Loop heals on second attempt with remediation feedback."""
    loop, canvas_path, router, quarantine = revision_test_env

    def builder_healing(attempt: int, remediation):
        if attempt == 1:
            # First attempt has syntax error
            return [
                AgentOutput(
                    agent_id="denchik",
                    task_id="t1",
                    summary="Broken syntax",
                    produced_files={"broken.py": "def broken(:\n    pass"},
                    command_results=[],
                )
            ]
        else:
            # Second attempt receives remediation and fixes syntax error
            assert remediation is not None
            assert "denchik" in remediation
            return [
                AgentOutput(
                    agent_id="denchik",
                    task_id="t1",
                    summary="Fixed syntax",
                    produced_files={"broken.py": "def broken():\n    pass"},
                    command_results=[{"command": "pytest", "exit_code": 0}],
                )
            ]

    result = loop.execute_loop(canvas_path, "node_builder_task", builder_healing)
    assert result.passed is True
    assert result.status == RevisionLoopState.APPROVED
    assert result.total_revisions == 2
    assert len(result.attempts) == 2
    assert result.attempts[0].passed is False
    assert result.attempts[1].passed is True

    # Check chat history in node session
    session_id = router.format_session_id(canvas_path.stem, "node_builder_task")
    msgs = router.get_messages(session_id)
    assert any("REJECTED (Attempt 1/3)" in m.content for m in msgs)
    assert any("APPROVED on attempt 2/3" in m.content for m in msgs)


def test_revision_loop_three_strikes_trips_quarantine(revision_test_env):
    """Verify that failing all 3 attempts trips TC-10 AgentQuarantineGuard."""
    loop, canvas_path, router, quarantine = revision_test_env

    def stubborn_builder(attempt: int, remediation):
        return [
            AgentOutput(
                agent_id="stubborn_agent",
                task_id="t_fail",
                summary=f"Failing attempt {attempt}",
                produced_files={"bad.py": "def fail(:\n    pass"},
            )
        ]

    result = loop.execute_loop(canvas_path, "node_builder_task", stubborn_builder)
    assert result.passed is False
    assert result.status == RevisionLoopState.QUARANTINED_FAILED
    assert result.total_revisions == 3
    assert len(result.attempts) == 3
    assert "stubborn_agent" in result.quarantined_agents

    # Verify agent is locked in quarantine
    with pytest.raises(AgentQuarantinedError) as exc_info:
        quarantine.assert_can_execute("stubborn_agent")
    assert "QUARANTINED" in str(exc_info.value)
