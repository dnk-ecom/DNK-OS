# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/goldfish_tool_worker.py"
# purpose: "Dual-Circuit Goldfish Tool Worker Bridge implementing pattern 04-as-tool.md (DEC-058)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym, Antigravity & Denchik"
# --- END DNK-MRH-HEADER ---

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger("dnk.orchestrator.goldfish")


class GoldfishReceipt(BaseModel):
    """
    Standardized immutable receipt returned by ephemeral Goldfish Tool-Workers.
    Eliminates conversation leakage and enforces strict structured evidence (DEC-058).
    """

    status: Literal["SUCCESS", "FAILED", "BLOCKED"] = Field(
        description="Deterministic status of worker execution"
    )
    worker_domain: str = Field(description="Domain of the worker (e.g. shopify, media, auditor)")
    conclusion: str = Field(description="Actionable conclusion derived by the worker")
    evidence: Dict[str, Any] = Field(
        default_factory=dict, description="Concrete data points or AST metrics produced"
    )
    actions_taken: List[str] = Field(
        default_factory=list, description="Specific mutations or checks performed"
    )
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score of the verdict"
    )
    caveats: List[str] = Field(
        default_factory=list, description="Uncertainties, skipped checks, or boundary limits"
    )
    execution_ms: int = Field(default=0, description="Execution wall-clock time in milliseconds")


class GoldfishToolWorker:
    """
    Sovereign caller bridging Elephant Orchestrator (Denchik/Antigravity) with isolated Goldfish workers.
    Enforces pattern 04-as-tool.md (DEC-058): fresh context, subprocess isolation, zero shared RAM.
    """

    SUPPORTED_DOMAINS = {"shopify", "media", "auditor", "distribution", "cleanroom", "gerych_auditor"}

    def __init__(self, hub_root: Optional[Path] = None, default_timeout_sec: int = 45):
        self.hub_root = hub_root or Path(__file__).resolve().parent.parent.parent
        self.default_timeout_sec = default_timeout_sec

    def _find_gerych_binary(self) -> Optional[Path]:
        """Locates canonical gerych-root or gerych binary."""
        candidates = [
            Path.home() / ".local" / "bin" / "gerych-root",
            Path.home() / ".local" / "bin" / "gerych",
            Path(os.path.expanduser("~/.local/bin/gerych-root")),
            Path(os.path.expanduser("~/.local/bin/gerych")),
        ]
        for c in candidates:
            if c.exists() and os.access(c, os.X_OK):
                return c

        which_path = shutil.which("gerych-root") or shutil.which("gerych")
        if which_path:
            return Path(which_path)

        return None

    def invoke_worker(
        self,
        domain: str,
        required_brief: Dict[str, Any],
        instructions: str,
        timeout_sec: Optional[int] = None,
        runner: Literal["simulation", "gerych", "auto"] = "simulation",
    ) -> GoldfishReceipt:
        """
        Executes a domain worker in a fresh isolated subprocess with strict validation.
        """
        start_time = time.perf_counter()
        clean_domain = domain.strip().lower()

        # Step 6 of 04-as-tool: Validate required parameters before invoking worker
        if clean_domain not in self.SUPPORTED_DOMAINS:
            return GoldfishReceipt(
                status="BLOCKED",
                worker_domain=clean_domain,
                conclusion=f"Unsupported domain worker: {clean_domain}",
                caveats=[f"Domain must be one of {sorted(self.SUPPORTED_DOMAINS)}"],
                execution_ms=int((time.perf_counter() - start_time) * 1000),
            )

        if not required_brief:
            return GoldfishReceipt(
                status="BLOCKED",
                worker_domain=clean_domain,
                conclusion="Missing required brief payload for worker call",
                caveats=["Required brief dictionary cannot be empty (04-as-tool requirement)"],
                execution_ms=int((time.perf_counter() - start_time) * 1000),
            )

        default_timeout = 180 if (runner == "gerych" or clean_domain in {"auditor", "gerych_auditor"}) else self.default_timeout_sec
        timeout = timeout_sec or default_timeout

        # Route to Gerych-Root CLI runner if requested or configured
        if runner == "gerych" or (runner == "auto" and clean_domain in {"auditor", "gerych_auditor"}):
            return self._invoke_gerych_cli(
                clean_domain=clean_domain,
                required_brief=required_brief,
                instructions=instructions,
                timeout=timeout,
                start_time=start_time,
            )

        # Fallback to isolated deterministic simulation runner
        return self._invoke_simulation(
            clean_domain=clean_domain,
            required_brief=required_brief,
            instructions=instructions,
            timeout=timeout,
            start_time=start_time,
        )

    def _invoke_simulation(
        self,
        clean_domain: str,
        required_brief: Dict[str, Any],
        instructions: str,
        timeout: int,
        start_time: float,
    ) -> GoldfishReceipt:
        """Deterministic simulation runner for hermetic test suites."""
        worker_harness_code = (
            "import sys, json\n"
            "try:\n"
            "    input_data = json.loads(sys.stdin.read())\n"
            "    domain = input_data.get('domain')\n"
            "    brief = input_data.get('brief', {})\n"
            "    out = {\n"
            "        'status': 'SUCCESS',\n"
            "        'worker_domain': domain,\n"
            "        'conclusion': f'Completed {domain} slice for {brief.get(\"action\", \"task\")}',\n"
            "        'evidence': {'verified_keys': list(brief.keys()), 'items_count': len(brief)},\n"
            "        'actions_taken': [f'executed_{domain}_action'],\n"
            "        'confidence_score': 1.0,\n"
            "        'caveats': []\n"
            "    }\n"
            "    print(json.dumps(out))\n"
            "except Exception as e:\n"
            "    print(json.dumps({'status': 'FAILED', 'worker_domain': str(domain), 'conclusion': str(e), 'evidence': {}, 'actions_taken': [], 'confidence_score': 0.0, 'caveats': [repr(e)]}))\n"
        )

        input_payload = {
            "domain": clean_domain,
            "brief": required_brief,
            "instructions": instructions,
        }

        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.hub_root)
        env["GOLDFISH_ISOLATED"] = "1"

        try:
            proc = subprocess.run(
                [sys.executable, "-c", worker_harness_code],
                input=json.dumps(input_payload),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env=env,
                cwd=str(self.hub_root),
            )

            execution_ms = int((time.perf_counter() - start_time) * 1000)

            if proc.returncode != 0:
                err_text = proc.stderr.strip() or f"Process returned exit code {proc.returncode}"
                return GoldfishReceipt(
                    status="FAILED",
                    worker_domain=clean_domain,
                    conclusion=f"Worker subprocess terminated with error: {err_text}",
                    caveats=[f"Subprocess non-zero exit: {proc.returncode}"],
                    execution_ms=execution_ms,
                )

            raw_stdout = proc.stdout.strip()
            if not raw_stdout:
                return GoldfishReceipt(
                    status="FAILED",
                    worker_domain=clean_domain,
                    conclusion="Worker returned empty stdout",
                    caveats=["Zero-byte worker output"],
                    execution_ms=execution_ms,
                )

            try:
                parsed_json = json.loads(raw_stdout)
                parsed_json["execution_ms"] = execution_ms
                return GoldfishReceipt.model_validate(parsed_json)
            except (json.JSONDecodeError, ValidationError) as e:
                return GoldfishReceipt(
                    status="FAILED",
                    worker_domain=clean_domain,
                    conclusion=f"Invalid worker output schema: {str(e)}",
                    caveats=["Failed schema conformance check"],
                    execution_ms=execution_ms,
                )

        except subprocess.TimeoutExpired:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return GoldfishReceipt(
                status="FAILED",
                worker_domain=clean_domain,
                conclusion=f"Worker timed out after {timeout} seconds",
                caveats=["Subprocess timeout deadline reached"],
                execution_ms=execution_ms,
            )
        except Exception as e:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return GoldfishReceipt(
                status="FAILED",
                worker_domain=clean_domain,
                conclusion=f"Unexpected invocation error: {str(e)}",
                caveats=[repr(e)],
                execution_ms=execution_ms,
            )

    def _invoke_gerych_cli(
        self,
        clean_domain: str,
        required_brief: Dict[str, Any],
        instructions: str,
        timeout: int,
        start_time: float,
    ) -> GoldfishReceipt:
        """
        Invokes live Gerych-Root CLI (hermes-agent) in a stateless Goldfish mode.
        """
        gerych_bin = self._find_gerych_binary()
        if not gerych_bin:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return GoldfishReceipt(
                status="FAILED",
                worker_domain=clean_domain,
                conclusion="Gerych-Root binary not found in PATH or ~/.local/bin",
                caveats=["Binary missing: gerych-root"],
                execution_ms=execution_ms,
            )

        prompt = (
            f"[GOLDFISH AUDIT PROTOCOL - DEC-058 / EGM]\n"
            f"Role: Ephemeral Cold Knowledge & Architecture Auditor (Goldfish).\n"
            f"Domain: {clean_domain}\n"
            f"Brief: {json.dumps(required_brief, ensure_ascii=False, indent=2)}\n"
            f"Instructions: {instructions}\n\n"
            f"Perform an adversarial and objective audit. Output your final verdict in a strict JSON code block:\n"
            f"```json\n"
            f'{{\n'
            f'  "status": "SUCCESS",\n'
            f'  "worker_domain": "{clean_domain}",\n'
            f'  "conclusion": "<1-2 sentence decisive verdict>",\n'
            f'  "evidence": {{}},\n'
            f'  "actions_taken": [],\n'
            f'  "confidence_score": 0.95,\n'
            f'  "caveats": []\n'
            f'}}\n'
            f"```\n"
        )

        cmd = [str(gerych_bin), "-q", prompt, "--oneshot"]
        env = os.environ.copy()
        env["GOLDFISH_ISOLATED"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env=env,
                cwd=str(self.hub_root),
            )

            execution_ms = int((time.perf_counter() - start_time) * 1000)
            raw_stdout = proc.stdout.strip()

            if proc.returncode != 0 and not raw_stdout:
                err_text = proc.stderr.strip() or f"Gerych exited with code {proc.returncode}"
                return GoldfishReceipt(
                    status="FAILED",
                    worker_domain=clean_domain,
                    conclusion=f"Gerych CLI failed: {err_text}",
                    caveats=[f"Subprocess code {proc.returncode}"],
                    execution_ms=execution_ms,
                )

            # Look for JSON code fence in stdout
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_stdout, re.DOTALL)
            if json_match:
                try:
                    payload = json.loads(json_match.group(1))
                    payload["execution_ms"] = execution_ms
                    return GoldfishReceipt.model_validate(payload)
                except Exception as e:
                    logger.warning("Failed to parse matched JSON block: %s", e)

            # Fallback: extract clean text between banner lines
            lines = []
            capturing = False
            for line in raw_stdout.splitlines():
                if "⚡ Гєрич" in line:
                    capturing = True
                    continue
                if "Resume this session with:" in line or "Session:" in line:
                    break
                if capturing and not line.startswith("───"):
                    lines.append(line)

            conclusion_text = "\n".join(lines).strip()
            if not conclusion_text:
                conclusion_text = raw_stdout[:500]

            return GoldfishReceipt(
                status="SUCCESS" if proc.returncode == 0 else "FAILED",
                worker_domain=clean_domain,
                conclusion=conclusion_text,
                evidence={"raw_stdout_sample": raw_stdout[-800:]},
                actions_taken=["executed_gerych_cli_audit"],
                confidence_score=0.9,
                caveats=[],
                execution_ms=execution_ms,
            )

        except subprocess.TimeoutExpired:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return GoldfishReceipt(
                status="FAILED",
                worker_domain=clean_domain,
                conclusion=f"Gerych worker timed out after {timeout} seconds",
                caveats=["Subprocess timeout deadline reached"],
                execution_ms=execution_ms,
            )
        except Exception as e:
            execution_ms = int((time.perf_counter() - start_time) * 1000)
            return GoldfishReceipt(
                status="FAILED",
                worker_domain=clean_domain,
                conclusion=f"Unexpected Gerych CLI error: {str(e)}",
                caveats=[repr(e)],
                execution_ms=execution_ms,
            )

    def invoke_gerych_goldfish(
        self,
        required_brief: Dict[str, Any],
        instructions: str,
        domain: str = "auditor",
        timeout_sec: int = 120,
    ) -> GoldfishReceipt:
        """High-level entrypoint for Elephant-Goldfish Dual Audits."""
        return self.invoke_worker(
            domain=domain,
            required_brief=required_brief,
            instructions=instructions,
            timeout_sec=timeout_sec,
            runner="gerych",
        )
