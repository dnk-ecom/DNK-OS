# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_mandate_contracts.py"
# purpose: "Unit tests for DSH Mandate, AdmissionGate, and Ticket contracts (DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import pytest
from core.domain.mandate_contracts import (
    AdmissionGate,
    DecisionKind,
    Mandate,
    MandateScope,
    MandateViolationError,
    ReportStatus,
    Strength,
    Ticket,
    TicketStage,
)


def test_mandate_scope_path_allowance():
    scope = MandateScope(
        allowed_paths=["services/dnk_distribution/**", "tests/services/**"],
        negative_scope=["**/.env*", "**/credentials.json", "core/kernel.py"],
        allowed_tools=["read_file", "edit_file", "run_test"],
    )

    # Allowed paths
    assert scope.is_path_allowed("services/dnk_distribution/src/brand_compliance.py")
    assert scope.is_path_allowed("tests/services/test_dist.py")

    # Outside allowed paths
    assert not scope.is_path_allowed("services/dnk_shopify/src/service.py")
    with pytest.raises(MandateViolationError):
        scope.assert_path_allowed("services/dnk_shopify/src/service.py")

    # Negative scope overrides allowed paths
    assert not scope.is_path_allowed("services/dnk_distribution/.env")
    with pytest.raises(MandateViolationError):
        scope.assert_path_allowed("services/dnk_distribution/.env")

    assert not scope.is_path_allowed("core/kernel.py")
    with pytest.raises(MandateViolationError):
        scope.assert_path_allowed("core/kernel.py")


def test_mandate_tool_whitelist():
    scope = MandateScope(
        allowed_paths=["services/**"],
        allowed_tools=["read_file", "write_file"]
    )
    mandate = Mandate(
        policy_version="pol-2026-v1",
        scope=scope,
        strength=Strength.EXPLICIT,
        matched_rules=["rule-brand-review"],
        actor_id="maxim_admin",
        source_id="github"
    )

    assert mandate.check_tool_allowed("read_file")
    assert mandate.check_tool_allowed("write_file")
    assert not mandate.check_tool_allowed("delete_database")

    with pytest.raises(MandateViolationError):
        mandate.assert_tool_allowed("delete_database")


def test_admission_gate():
    gate = AdmissionGate(
        allowed_actors={"maxim", "lead_dev"},
        banned_actors={"malicious_actor"},
        known_bots={"dependabot", "dnk_auto_sync"},
        allow_inferred_candidates=True
    )

    # Allowed actor explicit
    assert gate.admit("maxim", is_bot=False, is_direct_or_mention=True) == Strength.EXPLICIT

    # Banned actor
    assert gate.admit("malicious_actor", is_bot=False, is_direct_or_mention=True) == Strength.NOT_ADMITTED

    # Unknown human
    assert gate.admit("stranger_1", is_bot=False, is_direct_or_mention=True) == Strength.INFERRED
    assert gate.admit("stranger_1", is_bot=False, is_direct_or_mention=False) == Strength.NOT_ADMITTED

    # Known bot
    assert gate.admit("dependabot", is_bot=True, is_direct_or_mention=True) == Strength.INFERRED

    # Unknown bot
    assert gate.admit("unknown_bot", is_bot=True, is_direct_or_mention=True) == Strength.NOT_ADMITTED


def test_ticket_lifecycle_and_attention_state():
    scope = MandateScope(allowed_paths=["services/**"])
    mandate = Mandate(
        policy_version="pol-v1",
        scope=scope,
        strength=Strength.EXPLICIT,
        actor_id="maxim",
        source_id="github"
    )

    ticket = Ticket(
        short_name="dist-fix-001",
        mandate=mandate,
        channels=["github:issues:42"]
    )

    assert ticket.stage == TicketStage.QUEUED

    # 1. Assign to executor
    asg_id = ticket.assign("denchik")
    assert "denchik" in asg_id
    assert ticket.stage == TicketStage.WORKING
    assert ticket.active_assignment_id == asg_id

    # 2. Progress report (stays working)
    ticket.post_report(ReportStatus.PROGRESS, summary="Analyzing AST")
    assert ticket.stage == TicketStage.WORKING

    # 3. Attention question (transitions to PERSON_ATTENTION)
    ticket.post_report(
        ReportStatus.WAITING,
        summary="Need decision on threshold",
        question="Should threshold be 0.8 or 0.9?"
    )
    assert ticket.stage == TicketStage.PERSON_ATTENTION
    assert ticket.attention_question == "Should threshold be 0.8 or 0.9?"

    # 4. Answer attention
    ticket.answer_attention("Use 0.85")
    assert ticket.stage == TicketStage.WORKING
    assert ticket.attention_question is None

    # 5. Ready report (transitions to PERSON_REVIEW)
    ticket.post_report(ReportStatus.READY, summary="PR #105 opened with clean AST")
    assert ticket.stage == TicketStage.PERSON_REVIEW

    # 6. Stop ticket
    ticket.stop("Merged and resolved")
    assert ticket.stage == TicketStage.ENDED
    assert ticket.ended_at_epoch is not None

    # 7. Resume
    ticket.resume()
    assert ticket.stage == TicketStage.WORKING
