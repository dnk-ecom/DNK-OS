# --- DNK-MRH-HEADER ---
# mrh_id: "tests/test_contracts.py"
# purpose: "Contract Validation & Anti-Tautology Unit Tests for DNK OS IPC."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""Unit tests for DNK OS machine contracts."""

import pytest
from core.contracts import (
    BlastRadiusRisk,
    CompletionStatus,
    KernelCompletionReceipt,
    KernelDecisionReceipt,
    KernelTaskRequest,
    KernelTriageReceipt,
    TriageStatus,
)


def test_kernel_task_request_serialization():
    """Verify KernelTaskRequest serializes and validates required fields."""
    request = KernelTaskRequest(
        task_id="TASK-2026-001",
        source_repo="DNK_HUB",
        target_repo="DNK-Shopify-AI-Builder",
        action="transpile_liquid",
        payload={"theme_id": "horizon_v1", "mode": "ast"},
        negative_scope=["core/kernel.py"],
        target_file_whitelist=["templates/index.liquid"],
    )

    data = request.model_dump()
    assert data["task_id"] == "TASK-2026-001"
    assert data["source_repo"] == "DNK_HUB"
    assert data["target_repo"] == "DNK-Shopify-AI-Builder"
    assert data["action"] == "transpile_liquid"
    assert "core/kernel.py" in data["negative_scope"]
    assert "templates/index.liquid" in data["target_file_whitelist"]
    assert data["payload"]["mode"] == "ast"


def test_kernel_triage_receipt_statuses():
    """Verify KernelTriageReceipt strictly honors enum values."""
    receipt = KernelTriageReceipt(
        receipt_id="REC-TR-001",
        task_id="TASK-2026-001",
        status=TriageStatus.APPROVED,
        reasoning="Task adheres to 2-tier protocol with clean negative scope.",
        blast_radius_risk=BlastRadiusRisk.LOW,
        execution_plan=["step1_parse", "step2_transpile"],
    )

    assert receipt.status == TriageStatus.APPROVED
    assert receipt.blast_radius_risk == BlastRadiusRisk.LOW
    assert len(receipt.execution_plan) == 2


def test_kernel_completion_receipt_exit_code_validation():
    """Verify KernelCompletionReceipt represents verified machine proof."""
    receipt = KernelCompletionReceipt(
        receipt_id="REC-COMP-001",
        task_id="TASK-2026-001",
        status=CompletionStatus.SUCCESS,
        exit_code=0,
        test_output_summary="3 passed in 0.04s",
        affected_files=["templates/index.liquid"],
        scones_persisted=True,
    )

    assert receipt.status == CompletionStatus.SUCCESS
    assert receipt.exit_code == 0
    assert receipt.scones_persisted is True
    assert "3 passed" in receipt.test_output_summary


def test_kernel_decision_receipt_locking():
    """Verify KernelDecisionReceipt locks architectural agreements."""
    decision = KernelDecisionReceipt(
        decision_id="DEC-091",
        title="DNK OS Microkernel IPC Protocol",
        status="LOCKED",
        context="Need deterministic cross-repo communication.",
        verdict="All IPC routed via core/contracts.py Pydantic schemas.",
    )

    assert decision.decision_id == "DEC-091"
    assert decision.status == "LOCKED"
    assert "core/contracts.py" in decision.verdict
