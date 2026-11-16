# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_kernel_cli.py"
# purpose: "Unit tests for Microkernel CLI commands (node context, post, messages, crystallize)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from core.kernel import FastMCPKernel
from core.kernel_cli import run_cli_command


@pytest.fixture
def cli_test_env(tmp_path: Path):
    db_path = str(tmp_path / "cli_action_bus.db")
    canvas_path = tmp_path / "cli_test.canvas"
    canvas_data = {
        "nodes": [
            {
                "id": "node_audit",
                "type": "text",
                "text": "### Audit Node\n**Agent**: `gerych`\nAnalyze donor theme.",
                "x": 0,
                "y": 0,
                "width": 300,
                "height": 200,
            }
        ],
        "edges": [],
    }
    canvas_path.write_text(json.dumps(canvas_data), encoding="utf-8")
    from core.canvas.session_router import SpatialCanvasSessionRouter
    kernel = FastMCPKernel(db_path=db_path)
    kernel.session_router = SpatialCanvasSessionRouter(db_path=tmp_path / "sessions.db")
    return kernel, canvas_path


@pytest.mark.asyncio
async def test_cli_status(cli_test_env):
    kernel, _ = cli_test_env
    code = await run_cli_command(kernel, ["status"])
    assert code == 0


@pytest.mark.asyncio
async def test_cli_node_flow(cli_test_env, capsys):
    kernel, canvas_path = cli_test_env

    # 1. Compile context
    code = await run_cli_command(kernel, ["node", "context", str(canvas_path), "node_audit"])
    assert code == 0
    captured = capsys.readouterr().out
    ctx = json.loads(captured)
    assert ctx["node_id"] == "node_audit"
    assert ctx["agent_role"] == "gerych"

    # 2. Post message
    code = await run_cli_command(
        kernel, ["node", "post", "cli_test", "node_audit", "gerych", "Sugar audit started."]
    )
    assert code == 0
    captured = capsys.readouterr().out
    post_res = json.loads(captured)
    assert post_res["status"] == "recorded"

    # 3. Read messages
    code = await run_cli_command(kernel, ["node", "messages", "cli_test", "node_audit"])
    assert code == 0
    captured = capsys.readouterr().out
    msgs = json.loads(captured)
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Sugar audit started."

    # 4. Crystallize node
    code = await run_cli_command(
        kernel,
        [
            "node",
            "crystallize",
            str(canvas_path),
            "node_audit",
            "Completed Sugar cart audit.",
            json.dumps(["docs/notes/audit.md"]),
        ],
    )
    assert code == 0
    captured = capsys.readouterr().out
    cryst_res = json.loads(captured)
    assert cryst_res["status"] == "crystallized"

    # Verify canvas file was updated
    canvas_data = json.loads(canvas_path.read_text(encoding="utf-8"))
    node = canvas_data["nodes"][0]
    assert "CRYSTALLIZED" in node["text"]
    assert node["color"] == "4"
