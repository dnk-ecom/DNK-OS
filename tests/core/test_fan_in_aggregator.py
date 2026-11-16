# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_fan_in_aggregator.py"
# purpose: "Unit tests for FanInAggregator with deterministic validation chain."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import pytest
from core.orchestrator.fan_in_aggregator import (
    FanInAggregator,
    AgentOutput,
    AggregationStatus,
    SyntaxASTValidator,
    BoundaryScopeValidator,
    DeterministicExitCodeValidator,
)


def test_fan_in_aggregator_all_pass():
    aggregator = FanInAggregator([
        SyntaxASTValidator(),
        BoundaryScopeValidator(),
        DeterministicExitCodeValidator(),
    ])

    outputs = [
        AgentOutput(
            agent_id="denchik",
            task_id="task_1",
            summary="Created clean helper module",
            produced_files={"core/clean_helper.py": "def test():\n    return 42\n"},
            command_results=[{"command": "pytest", "exit_code": 0}],
        ),
        AgentOutput(
            agent_id="gerych",
            task_id="task_2",
            summary="Verified AST checks",
            command_results=[{"command": "ruff check", "exit_code": 0}],
        ),
    ]

    res = aggregator.aggregate_and_validate(outputs, context={"target_file_whitelist": ["core/clean_helper.py"]})
    assert res.passed is True
    assert res.status == AggregationStatus.APPROVED_FOR_SYNTHESIS
    assert len(res.remediation_packets) == 0
    assert "core/clean_helper.py" in res.synthesized_artifacts
    assert len(res.receipt_sha256) == 64


def test_fan_in_aggregator_syntax_error_rejection():
    aggregator = FanInAggregator([SyntaxASTValidator()])

    outputs = [
        AgentOutput(
            agent_id="denchik",
            task_id="task_broken",
            summary="Broken python code",
            produced_files={"broken.py": "def foo(:\n    pass"},
        )
    ]

    res = aggregator.aggregate_and_validate(outputs)
    assert res.passed is False
    assert res.status == AggregationStatus.REJECTED_REMEDIATION_REQUIRED
    assert "denchik" in res.remediation_packets
    defects = res.remediation_packets["denchik"]
    assert len(defects) == 1
    assert "Python SyntaxError" in defects[0].message


def test_fan_in_aggregator_negative_scope_rejection():
    aggregator = FanInAggregator([BoundaryScopeValidator()])

    outputs = [
        AgentOutput(
            agent_id="rogue_agent",
            task_id="task_hack",
            produced_files={"config/master_secrets.env": "LEAK=1"},
        )
    ]

    ctx = {"negative_scope": ["config/master_secrets.env"]}
    res = aggregator.aggregate_and_validate(outputs, context=ctx)
    assert res.passed is False
    assert res.status == AggregationStatus.REJECTED_REMEDIATION_REQUIRED
    assert "rogue_agent" in res.remediation_packets
    assert "violates negative_scope" in res.remediation_packets["rogue_agent"][0].message


def test_fan_in_aggregator_command_failure_rejection():
    aggregator = FanInAggregator([DeterministicExitCodeValidator()])

    outputs = [
        AgentOutput(
            agent_id="dnk_shopify",
            task_id="task_theme_check",
            command_results=[{"command": "shopify theme check", "exit_code": 1, "stderr": "Error in block"}],
        )
    ]

    res = aggregator.aggregate_and_validate(outputs)
    assert res.passed is False
    assert res.status == AggregationStatus.REJECTED_REMEDIATION_REQUIRED
    assert "dnk_shopify" in res.remediation_packets
    assert "failed with exit code 1" in res.remediation_packets["dnk_shopify"][0].message
