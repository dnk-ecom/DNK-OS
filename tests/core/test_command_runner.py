# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_command_runner.py"
# purpose: "Unit tests for Adaptive Command Runner with 5-Second Foreground Shift (DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import asyncio
import pytest
from core.action_bus.command_runner import CommandRunner


@pytest.mark.asyncio
async def test_fast_command_foreground():
    runner = CommandRunner()
    res = await runner.run_command_adaptive(
        command="echo 'sovereign_dnk_ok'",
        timeout_foreground=2.0
    )

    assert not res.is_background
    assert res.exit_code == 0
    assert "sovereign_dnk_ok" in res.stdout
    assert res.status == "completed"


@pytest.mark.asyncio
async def test_fast_command_failure_foreground():
    runner = CommandRunner()
    res = await runner.run_command_adaptive(
        command="sh -c 'exit 7'",
        timeout_foreground=2.0
    )

    assert not res.is_background
    assert res.exit_code == 7
    assert res.status == "failed"


@pytest.mark.asyncio
async def test_slow_command_background_shift():
    runner = CommandRunner()
    # Run sleep 1 with a 0.2s foreground threshold
    res = await runner.run_command_adaptive(
        command="sleep 0.6 && echo 'done_in_bg'",
        timeout_foreground=0.2
    )

    # Should immediately detach into background
    assert res.is_background
    assert res.job_id is not None
    assert res.status == "running"
    assert "exceeded" in res.message

    job = runner.get_job(res.job_id)
    assert job is not None
    assert job.status == "running"

    # Wait for the background task to complete
    await asyncio.sleep(0.7)

    job_after = runner.get_job(res.job_id)
    assert job_after.status == "completed"
    assert job_after.exit_code == 0
    assert "done_in_bg" in job_after.stdout


@pytest.mark.asyncio
async def test_kill_background_job():
    runner = CommandRunner()
    res = await runner.run_command_adaptive(
        command="sleep 10",
        timeout_foreground=0.2
    )

    assert res.is_background
    job_id = res.job_id

    # Kill job
    killed = await runner.kill_job(job_id)
    assert killed is True

    job = runner.get_job(job_id)
    assert job.status == "killed"
