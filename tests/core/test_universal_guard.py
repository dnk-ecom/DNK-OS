# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_universal_guard.py"
# purpose: "Unit tests for universal_guard.py cross-harness pre-tool execution sentinel"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from core.sentinel.universal_guard import run_guard


def test_universal_guard_blocks_local_venv():
    """Verify universal guard intercepts python -m venv creation."""
    event = {
        "tool_name": "terminal",
        "tool_input": {"command": "python3 -m venv .venv"}
    }
    res = run_guard(event)
    assert res["allowed"] is False
    assert res["action"] == "block"
    assert res["barrier_id"] == "BARRIER_001_LOCAL_VENV"


def test_universal_guard_blocks_npm_yarn_install():
    """Verify universal guard enforces pnpm hardlink store invariant."""
    event_npm = {
        "tool_name": "bash",
        "tool_input": {"command": "npm install express"}
    }
    res_npm = run_guard(event_npm)
    assert res_npm["allowed"] is False
    assert res_npm["barrier_id"] == "BARRIER_002_NPM_YARN_BLOCK"

    event_yarn = {
        "tool_name": "execute_code",
        "tool_input": {"command": "yarn add react"}
    }
    res_yarn = run_guard(event_yarn)
    assert res_yarn["allowed"] is False
    assert res_yarn["barrier_id"] == "BARRIER_002_NPM_YARN_BLOCK"


def test_universal_guard_blocks_destructive_git_force_push():
    """Verify universal guard prevents force pushes to main or master."""
    event = {
        "tool_name": "terminal",
        "tool_input": {"command": "git push --force origin main"}
    }
    res = run_guard(event)
    assert res["allowed"] is False
    assert res["barrier_id"] == "BARRIER_003_DESTRUCTIVE_GIT"


def test_universal_guard_blocks_system_destruction():
    """Verify universal guard blocks rm -rf / or $HOME."""
    event = {
        "tool_name": "terminal",
        "tool_input": {"command": "rm -rf /"}
    }
    res = run_guard(event)
    assert res["allowed"] is False
    assert res["barrier_id"] == "BARRIER_004_SYSTEM_DESTRUCTION"


def test_universal_guard_allows_safe_commands():
    """Verify universal guard permits canonical safe workflows (uv, pnpm, git)."""
    safe_commands = [
        "uv run pytest tests/",
        "pnpm install",
        "pnpm run build",
        "git status",
        "git add .",
        "git commit -m 'feat: add feature'",
        "python3 scripts/system/preflight_sync.py",
    ]
    for cmd in safe_commands:
        event = {
            "tool_name": "terminal",
            "tool_input": {"command": cmd}
        }
        res = run_guard(event)
        assert res["allowed"] is True, f"Command should be allowed: {cmd}"
        assert res["action"] == "allow"
