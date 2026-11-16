# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_delegation_packet.py"
# purpose: "Unit tests for Canonical PSOD DelegationPacket, Whitelist Containment, and VerificationVerifier"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import pytest
from core.orchestrator.delegation_packet import (
    DelegationPacket,
    DelegationStatus,
    DelegationVerifier,
    VerificationVerdict,
)


def test_delegation_packet_render_brief():
    packet = DelegationPacket(
        packet_id="DEL-TEST-001",
        title="Implement Cart Exporter",
        problem="Create CSV exporter for cart items.",
        target_whitelist=["services/dnk_shopify/exporter.py"],
        oracle_command="pytest tests/test_exporter.py",
        expected_exit_code=0
    )
    brief = packet.render_prompt_brief()
    assert "DEL-TEST-001" in brief
    assert "services/dnk_shopify/exporter.py" in brief
    assert "pytest tests/test_exporter.py" in brief
    assert "EXIT CODE MUST BE `0`" in brief


def test_delegation_verifier_phantom_done_intercept():
    packet = DelegationPacket(
        packet_id="DEL-TEST-002",
        title="Fix Cart Bug",
        problem="Fix mutation queue",
        oracle_command="pytest tests/test_cart.py",
    )
    # Agent executed unrelated commands, never ran the oracle
    verdict = DelegationVerifier.verify(
        packet=packet,
        executed_commands=["git status", "ls -la"],
        exit_codes=[0, 0],
        modified_files=["services/dnk_shopify/cart.py"]
    )
    assert not verdict.passed
    assert verdict.status == DelegationStatus.ORACLE_FAILED
    assert not verdict.oracle_executed
    assert "Phantom Done" in verdict.failure_reason


def test_delegation_verifier_oracle_failed_exit_code():
    packet = DelegationPacket(
        packet_id="DEL-TEST-003",
        title="Refactor Session",
        problem="Refactor session",
        oracle_command="pytest tests/test_session.py",
    )
    # Agent executed the command, but exit code was 1 (tests failed)
    verdict = DelegationVerifier.verify(
        packet=packet,
        executed_commands=["pytest tests/test_session.py"],
        exit_codes=[1],
        modified_files=[],
        raw_output="FAILED (failures=1)"
    )
    assert not verdict.passed
    assert verdict.status == DelegationStatus.ORACLE_FAILED
    assert verdict.oracle_executed
    assert verdict.exit_code == 1
    assert "exit code 1" in verdict.failure_reason


def test_delegation_verifier_whitelist_violation_intercept():
    packet = DelegationPacket(
        packet_id="DEL-TEST-004",
        title="Scoped Refactor",
        problem="Only edit cart.py",
        target_whitelist=["services/dnk_shopify/cart.py"],
        oracle_command="pytest tests/test_cart.py",
    )
    # Agent edited cart.py AND also modified unrelated global.py (Drive-By Refactor)
    verdict = DelegationVerifier.verify(
        packet=packet,
        executed_commands=["pytest tests/test_cart.py"],
        exit_codes=[0],
        modified_files=["services/dnk_shopify/cart.py", "services/dnk_shopify/global.py"]
    )
    assert not verdict.passed
    assert verdict.status == DelegationStatus.WHITELIST_VIOLATION
    assert not verdict.whitelist_ok
    assert "Drive-By Refactor Blocked" in verdict.failure_reason
    assert "services/dnk_shopify/global.py" in verdict.disallowed_files


def test_delegation_verifier_clean_success():
    packet = DelegationPacket(
        packet_id="DEL-TEST-005",
        title="Clean Feature",
        problem="Add clean feature",
        target_whitelist=["services/dnk_shopify/cart.py"],
        oracle_command="pytest tests/test_cart.py",
    )
    verdict = DelegationVerifier.verify(
        packet=packet,
        executed_commands=["pytest tests/test_cart.py"],
        exit_codes=[0],
        modified_files=["services/dnk_shopify/cart.py"],
        raw_output="1 passed in 0.05s"
    )
    assert verdict.passed
    assert verdict.status == DelegationStatus.VERIFIED_SUCCESS
    assert verdict.oracle_executed
    assert verdict.whitelist_ok
    assert verdict.exit_code == 0
