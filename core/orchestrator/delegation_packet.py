# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/delegation_packet.py"
# purpose: "Canonical PSOD Delegation Packet, Whitelist Containment, and Deterministic Completion Oracle Engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.orchestrator.delegation")


class DelegationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED_SUCCESS = "verified_success"
    ORACLE_FAILED = "oracle_failed"
    WHITELIST_VIOLATION = "whitelist_violation"
    MAX_REVISIONS_EXCEEDED = "max_revisions_exceeded"
    BLOCKED = "blocked"


class DelegationPacket(BaseModel):
    """
    PSOD (Problem, Substrate, Oracle, Deliverable) Canonical Delegation Contract.
    Enforces 100% first-pass completion with zero phantom 'Done' claims.
    """
    packet_id: str = Field(..., description="Unique packet identifier, e.g. 'DEL-20261116-01'")
    title: str = Field(..., description="Short task title")
    problem: str = Field(..., description="Explicit description of problem and functional requirements")
    target_whitelist: List[str] = Field(
        default_factory=list,
        description="Strict whitelist of relative file paths permitted for modification"
    )
    substrate: str = Field(
        default="Shared ~/.dnk_runtime/venv, pnpm APFS hardlink store, GEMINI.md compliance",
        description="Environment constraints and runtime rules"
    )
    oracle_command: str = Field(..., description="Deterministic verification command (must return exit code 0)")
    expected_exit_code: int = Field(default=0, description="Required exit code for passing verification")
    deliverable_summary: str = Field(
        default="Raw execution log + git diff summary",
        description="Expected format of deliverable output"
    )
    assigned_agent: str = Field(default="subagent", description="Worker role: 'subagent', 'gerych', 'denchik'")
    max_revisions: int = Field(default=3, description="Maximum bounded self-repair attempts upon test failure")
    timeout_seconds: int = Field(default=300, description="Maximum execution timeout in seconds")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of packet creation"
    )

    def render_prompt_brief(self) -> str:
        """Render a concise markdown delegation brief for LLM subagents."""
        whitelist_md = "\n".join(f"  - `{p}`" for p in self.target_whitelist) if self.target_whitelist else "  - (Any within repository scope)"
        return (
            f"# 📋 DELEGATION CONTRACT [{self.packet_id}]: {self.title}\n\n"
            f"### 1. Problem & Requirements (P):\n{self.problem}\n\n"
            f"### 2. Permitted Files Whitelist (Target Whitelist):\n{whitelist_md}\n"
            f"> ⚠️ MODIFICATIONS OUTSIDE THIS WHITELIST ARE STRICTLY BLOCKED.\n\n"
            f"### 3. Substrate & Rules (S):\n{self.substrate}\n\n"
            f"### 4. Deterministic Verification Oracle (O):\n"
            f"You MUST execute and verify this command before reporting completion:\n"
            f"```bash\n{self.oracle_command}\n```\n"
            f"> 🚨 EXIT CODE MUST BE `{self.expected_exit_code}`. NO EVIDENCE LOG = NO ACCEPTANCE.\n\n"
            f"### 5. Deliverable Format (D):\n{self.deliverable_summary}\n"
        )


class VerificationVerdict(BaseModel):
    """Result of validating an agent's execution against the PSOD contract."""
    passed: bool
    status: DelegationStatus
    exit_code: Optional[int] = None
    oracle_executed: bool = False
    whitelist_ok: bool = True
    disallowed_files: List[str] = Field(default_factory=list)
    failure_reason: Optional[str] = None
    evidence_log: Optional[str] = None


class DelegationVerifier:
    """Verifies agent outputs and environment state against DelegationPacket invariants."""

    @staticmethod
    def verify(
        packet: DelegationPacket,
        executed_commands: List[str],
        exit_codes: List[int],
        modified_files: List[str],
        raw_output: str = ""
    ) -> VerificationVerdict:
        """
        Validate whether the execution satisfies all Tier 2 completion gates.
        """
        # 1. Check if oracle command was actually executed
        oracle_clean = packet.oracle_command.strip()
        oracle_idx = -1
        for idx, cmd in enumerate(executed_commands):
            if oracle_clean in cmd.strip() or cmd.strip() in oracle_clean:
                oracle_idx = idx
                break

        if oracle_idx == -1:
            return VerificationVerdict(
                passed=False,
                status=DelegationStatus.ORACLE_FAILED,
                oracle_executed=False,
                failure_reason=f"Phantom Done: Oracle command '{oracle_clean}' was never executed in session."
            )

        # 2. Check exit code of oracle execution
        exit_code = exit_codes[oracle_idx] if oracle_idx < len(exit_codes) else -1
        if exit_code != packet.expected_exit_code:
            return VerificationVerdict(
                passed=False,
                status=DelegationStatus.ORACLE_FAILED,
                oracle_executed=True,
                exit_code=exit_code,
                failure_reason=f"Oracle failed with exit code {exit_code} (expected {packet.expected_exit_code}).",
                evidence_log=raw_output[-1500:] if raw_output else None
            )

        # 3. Check Whitelist Containment (Anti-Habit: Drive-By Refactor)
        if packet.target_whitelist:
            disallowed: List[str] = []
            normalized_whitelist = {os.path.normpath(p) for p in packet.target_whitelist}
            for mf in modified_files:
                norm_mf = os.path.normpath(mf)
                # Check exact or prefix match
                if not any(norm_mf == w or norm_mf.startswith(w + os.sep) for w in normalized_whitelist):
                    disallowed.append(mf)

            if disallowed:
                return VerificationVerdict(
                    passed=False,
                    status=DelegationStatus.WHITELIST_VIOLATION,
                    oracle_executed=True,
                    exit_code=exit_code,
                    whitelist_ok=False,
                    disallowed_files=disallowed,
                    failure_reason=(
                        f"Drive-By Refactor Blocked: Modified files outside whitelist: {disallowed}. "
                        f"Allowed whitelist: {packet.target_whitelist}."
                    )
                )

        # 4. All checks passed
        return VerificationVerdict(
            passed=True,
            status=DelegationStatus.VERIFIED_SUCCESS,
            oracle_executed=True,
            exit_code=exit_code,
            whitelist_ok=True,
            evidence_log=raw_output[-500:] if raw_output else None
        )

    @staticmethod
    def execute_and_verify_local(
        packet: DelegationPacket,
        cwd: Optional[Path] = None
    ) -> VerificationVerdict:
        """
        Directly execute the oracle command in a local subprocess and evaluate.
        """
        run_cwd = cwd or Path.cwd()
        cmd = packet.oracle_command
        try:
            res = subprocess.run(
                cmd,
                shell=True,
                cwd=str(run_cwd),
                capture_output=True,
                text=True,
                timeout=packet.timeout_seconds
            )
            passed = (res.returncode == packet.expected_exit_code)
            combined_log = (res.stdout + "\n" + res.stderr).strip()
            status = DelegationStatus.VERIFIED_SUCCESS if passed else DelegationStatus.ORACLE_FAILED
            return VerificationVerdict(
                passed=passed,
                status=status,
                exit_code=res.returncode,
                oracle_executed=True,
                whitelist_ok=True,
                failure_reason=None if passed else f"Command returned exit code {res.returncode}",
                evidence_log=combined_log[-1000:]
            )
        except subprocess.TimeoutExpired:
            return VerificationVerdict(
                passed=False,
                status=DelegationStatus.ORACLE_FAILED,
                exit_code=-9,
                oracle_executed=True,
                failure_reason=f"Oracle command timed out after {packet.timeout_seconds}s"
            )
        except Exception as e:
            return VerificationVerdict(
                passed=False,
                status=DelegationStatus.ORACLE_FAILED,
                failure_reason=f"Execution error: {str(e)}"
            )
