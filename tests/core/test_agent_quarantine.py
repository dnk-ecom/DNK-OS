# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_agent_quarantine.py"
# purpose: "Unit tests for AgentQuarantineGuard circuit breaker."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import pytest
from core.sentinel.agent_quarantine import (
    AgentQuarantineGuard,
    AgentState,
    AgentQuarantinedError,
    QuarantineReason,
)


def test_agent_quarantine_three_strikes():
    guard = AgentQuarantineGuard(max_failures=3)
    agent = "denchik_builder"

    guard.assert_can_execute(agent)
    assert guard.get_or_create(agent).state == AgentState.ACTIVE

    # Failure 1: Degraded
    guard.record_validation_failure(agent, "Defect 1")
    assert guard.get_or_create(agent).state == AgentState.DEGRADED
    assert guard.get_or_create(agent).consecutive_failures == 1

    # Failure 2: Still degraded
    guard.record_validation_failure(agent, "Defect 2")
    assert guard.get_or_create(agent).state == AgentState.DEGRADED

    # Failure 3: Tripped!
    guard.record_validation_failure(agent, "Defect 3")
    assert guard.get_or_create(agent).state == AgentState.QUARANTINED
    assert guard.get_or_create(agent).last_tripped_reason == QuarantineReason.MAX_FAILURES_EXCEEDED

    # Subsequent execution attempt MUST be blocked
    with pytest.raises(AgentQuarantinedError) as exc_info:
        guard.assert_can_execute(agent)
    assert "QUARANTINED" in str(exc_info.value)
    assert exc_info.value.agent_id == agent


def test_agent_quarantine_mase_tool_limit():
    guard = AgentQuarantineGuard(max_slice_calls=25)
    agent = "worker_loop"

    # Execute 25 allowed steps
    for _ in range(25):
        guard.record_step(agent, "read_file")

    assert guard.get_or_create(agent).tool_calls_in_slice == 25
    assert guard.get_or_create(agent).state == AgentState.ACTIVE

    # 26th step trips circuit breaker
    with pytest.raises(AgentQuarantinedError) as exc_info:
        guard.record_step(agent, "read_file")

    assert "tool_call_limit_exceeded" in str(exc_info.value)
    assert guard.get_or_create(agent).state == AgentState.QUARANTINED


def test_agent_quarantine_negative_scope_trip():
    guard = AgentQuarantineGuard()
    agent = "intruder_agent"

    neg_scope = ["config/production.env", "docs/internal/keys.pem"]

    with pytest.raises(AgentQuarantinedError) as exc_info:
        guard.record_step(agent, "write_file", target_path="config/production.env", negative_scope=neg_scope)

    assert "negative_scope_violation" in str(exc_info.value)
    assert guard.get_or_create(agent).state == AgentState.QUARANTINED


def test_agent_quarantine_release_flow():
    guard = AgentQuarantineGuard(max_failures=1)
    agent = "worker_test"

    guard.record_validation_failure(agent, "Fatal bug")
    assert guard.get_or_create(agent).state == AgentState.QUARANTINED

    # Release
    guard.release_agent(agent, approver="Maxim")
    assert guard.get_or_create(agent).state == AgentState.ACTIVE
    guard.assert_can_execute(agent)


def test_agent_quarantine_sqlite_persistence_across_sessions(tmp_path):
    """Verify that AgentQuarantineGuard persists state across separate instances via SQLite WAL."""
    db_file = tmp_path / "quarantine_test.db"

    # Instance 1: Trip quarantine on rogue agent
    guard_1 = AgentQuarantineGuard(max_failures=2, db_path=db_file)
    agent = "rogue_coder"

    guard_1.record_validation_failure(agent, "Defect A")
    assert guard_1.get_or_create(agent).state == AgentState.DEGRADED
    assert guard_1.get_or_create(agent).consecutive_failures == 1

    guard_1.record_validation_failure(agent, "Defect B")
    assert guard_1.get_or_create(agent).state == AgentState.QUARANTINED

    # Instance 2: Brand new instance simulating a new process/session
    guard_2 = AgentQuarantineGuard(max_failures=2, db_path=db_file)

    # Must immediately know agent is quarantined from SQLite
    with pytest.raises(AgentQuarantinedError) as exc_info:
        guard_2.assert_can_execute(agent)
    assert "QUARANTINED" in str(exc_info.value)
    assert exc_info.value.agent_id == agent

    rec_2 = guard_2.get_or_create(agent)
    assert rec_2.state == AgentState.QUARANTINED
    assert rec_2.consecutive_failures == 2
    assert len(rec_2.incidents) >= 1
    assert rec_2.incidents[0].reason == QuarantineReason.MAX_FAILURES_EXCEEDED

    # Release agent in Instance 2
    guard_2.release_agent(agent, approver="Maxim")
    assert guard_2.get_or_create(agent).state == AgentState.ACTIVE

    # Instance 3: Third instance verifies release persisted to disk
    guard_3 = AgentQuarantineGuard(max_failures=2, db_path=db_file)
    rec_3 = guard_3.get_or_create(agent)
    assert rec_3.state == AgentState.ACTIVE
    assert rec_3.consecutive_failures == 0
    guard_3.assert_can_execute(agent)


def test_agent_quarantine_in_memory_mode():
    """Verify :memory: db mode works cleanly without disk I/O."""
    guard = AgentQuarantineGuard(max_failures=1, db_path=":memory:")
    agent = "mem_agent"

    guard.record_validation_failure(agent, "Memory bug")
    assert guard.get_or_create(agent).state == AgentState.QUARANTINED
    with pytest.raises(AgentQuarantinedError):
        guard.assert_can_execute(agent)

