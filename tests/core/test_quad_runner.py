# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_quad_runner.py"
# purpose: "Senior Test Suite for SovereignQuadRunner, GroundingGuard integration, and node crystallization."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import json
import shutil
from pathlib import Path
import pytest

from core.canvas.session_router import SpatialCanvasSessionRouter
from core.orchestrator.quad_runner import SovereignQuadRunner, ROLE_PERSONA_MAP
from core.sentinel.grounding_guard import GroundingValidationError


@pytest.fixture
def runner_test_env(tmp_path: Path):
    db_path = tmp_path / "runner_sessions.db"
    canvas_path = tmp_path / "runner_test.canvas"

    canvas_data = {
        "nodes": [
            {
                "id": "node_research",
                "type": "text",
                "text": "### 1. Market Research\n**Agent**: `strategist`\nAnalyze 5 stores with AOV of $75.",
                "x": 0,
                "y": 0,
                "width": 300,
                "height": 200,
            },
            {
                "id": "node_builder",
                "type": "text",
                "text": "### 2. Code Construction\n**Agent**: `denchik`\nBuild block based on 5 stores.",
                "x": 400,
                "y": 0,
                "width": 300,
                "height": 200,
            },
        ],
        "edges": [
            {
                "id": "edge_r_to_b",
                "fromNode": "node_research",
                "toNode": "node_builder",
            }
        ],
    }
    canvas_path.write_text(json.dumps(canvas_data, indent=2), encoding="utf-8")
    router = SpatialCanvasSessionRouter(db_path=db_path)
    runner = SovereignQuadRunner(router=router)
    return runner, canvas_path, router


def test_build_execution_envelope_with_l2_dna():
    """Verify envelope compilation with auto-injected L2 DNA."""
    runner = SovereignQuadRunner()
    canvas_path = Path("docs/canvas/projects/dnk_ecom/main.canvas")
    assert canvas_path.exists()

    envelope = runner.build_execution_envelope(canvas_path, "node_t1_dual_ready_blocks")
    assert envelope["node_id"] == "node_t1_dual_ready_blocks"
    assert envelope["agent_role"] == "dnk_shopify"
    assert envelope["persona"] == "dnk_shopify"
    assert envelope["project_dna"] is not None
    assert "Shopify Theme DNK-Ecom" in envelope["system_prompt"]


def test_execute_node_grounded_success(runner_test_env):
    """Verify successful execution and crystallization with grounded facts."""
    runner, canvas_path, router = runner_test_env

    result = runner.execute_node_mock(
        canvas_path=canvas_path,
        node_id="node_research",
        simulated_output_summary="Researched 5 stores with $75 AOV.",
        simulated_numeric_payload={"stores": 5, "aov": 75},
        artifacts=["artifacts/benchmarks.json"],
    )

    assert result["status"] == "CRYSTALLIZED"
    assert result["node_id"] == "node_research"
    assert result["persona"] == "strategist_prime"

    # Verify updated .canvas file
    data = json.loads(canvas_path.read_text(encoding="utf-8"))
    node_r = next(n for n in data["nodes"] if n["id"] == "node_research")
    assert "CRYSTALLIZED" in node_r["text"]
    assert node_r["color"] == "4"  # Green


def test_execute_node_hallucinated_failure(runner_test_env):
    """Verify GroundingGuard halts execution when ungrounded numbers are emitted."""
    runner, canvas_path, _ = runner_test_env

    # 9999.99 is not in the node text (only 5 and 75 exist)
    with pytest.raises(GroundingValidationError, match="failed GroundingGuard check"):
        runner.execute_node_mock(
            canvas_path=canvas_path,
            node_id="node_research",
            simulated_output_summary="Fake numbers report",
            simulated_numeric_payload={"stores": 5, "fake_budget": 9999.99},
        )


def test_role_persona_mapping():
    """Verify Sovereign Quad persona mapping."""
    assert ROLE_PERSONA_MAP["strategist"] == "strategist_prime"
    assert ROLE_PERSONA_MAP["architect"] == "dnk_mentor"
    assert ROLE_PERSONA_MAP["builder"] == "denchik"
    assert ROLE_PERSONA_MAP["denchik"] == "denchik"
    assert ROLE_PERSONA_MAP["auditor"] == "auditor"
    assert ROLE_PERSONA_MAP["gerych"] == "gerych_prime"


def test_quad_runner_execute_node_with_revision_loop(runner_test_env):
    """Verify SovereignQuadRunner integration with Bounded Revision Loop (DEC-120)."""
    runner, canvas_path, router = runner_test_env
    from core.orchestrator.fan_in_aggregator import AgentOutput
    from core.orchestrator.bounded_revision_loop import RevisionLoopState

    def builder_mock(attempt: int, remediation):
        return [
            AgentOutput(
                agent_id="denchik",
                task_id="task_runner_build",
                summary="Synthesized module via quad runner",
                produced_files={"built.py": "def foo():\n    return 'quad'\n"},
                command_results=[{"command": "pytest", "exit_code": 0}],
            )
        ]

    res = runner.execute_node_with_revision_loop(
        canvas_path=canvas_path,
        node_id="node_builder",
        builder_fn=builder_mock,
    )

    assert res.passed is True
    assert res.status == RevisionLoopState.APPROVED
    assert res.total_revisions == 1

