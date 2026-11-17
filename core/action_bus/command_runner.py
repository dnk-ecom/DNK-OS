# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/command_runner.py"
# purpose: "Adaptive Command Runner with 5-Second Foreground Shift and Background Job Tracking (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import asyncio
import logging
import os
import time
import uuid
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("dnk.action_bus.command_runner")


class CommandRunResult(BaseModel):
    """Result of running a command via CommandRunner."""
    model_config = ConfigDict(extra="forbid")

    command: str
    is_background: bool
    job_id: Optional[str] = None
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    duration_s: float = 0.0
    status: Literal["completed", "running", "failed", "killed", "timeout"] = "completed"
    message: Optional[str] = None


class BackgroundJob(BaseModel):
    """Metadata and state of a backgrounded command."""
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:8]}")
    command: str
    cwd: Optional[str] = None
    started_at_epoch: float = Field(default_factory=time.time)
    completed_at_epoch: Optional[float] = None
    max_duration_s: float = 1800.0  # 30 minutes DSH standard
    status: Literal["running", "completed", "failed", "killed", "timeout"] = "running"
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""


class CommandRunner:
    """
    Adaptive Command Runner implementing DSH 5-Second Foreground Shift (DEC-151).
    Commands completing within timeout_foreground (5.0s) return synchronously.
    Commands exceeding 5.0s are seamlessly shifted to background jobs.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, BackgroundJob] = {}
        self._processes: Dict[str, asyncio.subprocess.Process] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        """Retrieve background job state by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, status: Optional[str] = None) -> List[BackgroundJob]:
        """List tracked background jobs, optionally filtered by status."""
        if status:
            return [j for j in self._jobs.values() if j.status == status]
        return list(self._jobs.values())

    async def kill_job(self, job_id: str) -> bool:
        """Terminate a running background job."""
        job = self._jobs.get(job_id)
        if not job or job.status != "running":
            return False

        proc = self._processes.get(job_id)
        if proc:
            try:
                proc.terminate()
            except ProcessLookupError:
                pass

        task = self._tasks.get(job_id)
        if task and not task.done():
            task.cancel()

        job.status = "killed"
        job.completed_at_epoch = time.time()
        logger.info(f"Background job {job_id} killed by operator.")
        return True

    async def run_command_adaptive(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout_foreground: float = 5.0,
        max_duration: float = 1800.0
    ) -> CommandRunResult:
        """
        Execute command with adaptive 5-second foreground shift.
        If command completes in <= timeout_foreground, returns synchronous result.
        If command runs > timeout_foreground, shifts to background job and returns immediately.
        """
        start_time = time.time()
        job_id = f"job_{uuid.uuid4().hex[:8]}"

        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        job = BackgroundJob(
            job_id=job_id,
            command=command,
            cwd=cwd,
            started_at_epoch=start_time,
            max_duration_s=max_duration
        )
        self._jobs[job_id] = job
        self._processes[job_id] = proc

        # Define background collector task
        async def _collect_output():
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=max_duration
                )
                job.stdout = stdout_data.decode("utf-8", errors="replace")
                job.stderr = stderr_data.decode("utf-8", errors="replace")
                job.exit_code = proc.returncode
                job.status = "completed" if proc.returncode == 0 else "failed"
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                job.status = "timeout"
                job.stderr += f"\nCommand exceeded maximum duration of {max_duration}s."
            except asyncio.CancelledError:
                job.status = "killed"
            finally:
                job.completed_at_epoch = time.time()

        task = asyncio.create_task(_collect_output())
        self._tasks[job_id] = task

        # Wait up to timeout_foreground
        done, _ = await asyncio.wait([task], timeout=timeout_foreground)

        if task in done:
            # Finished in foreground
            duration = time.time() - start_time
            return CommandRunResult(
                command=command,
                is_background=False,
                job_id=job_id,
                exit_code=job.exit_code,
                stdout=job.stdout,
                stderr=job.stderr,
                duration_s=duration,
                status=job.status,
                message="Completed in foreground."
            )
        else:
            # Shifted to background
            duration = time.time() - start_time
            logger.info(f"Command '{command}' exceeded {timeout_foreground}s; shifted to background job {job_id}.")
            return CommandRunResult(
                command=command,
                is_background=True,
                job_id=job_id,
                exit_code=None,
                stdout="",
                stderr="",
                duration_s=duration,
                status="running",
                message=f"Command exceeded {timeout_foreground}s foreground limit; shifted to background job {job_id}."
            )
