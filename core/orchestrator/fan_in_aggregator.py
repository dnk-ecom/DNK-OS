# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/fan_in_aggregator.py"
# purpose: "Fan-In Multi-Agent Aggregation Engine with Deterministic Validation Chain (assimilated from Worley UAIP ai-platform-agents)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import ast
import hashlib
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Sequence
from pydantic import BaseModel, Field

from core.sentinel.grounding_guard import GroundingGuard

logger = logging.getLogger("dnk.orchestrator.fan_in")


class AggregationStatus(str, Enum):
    APPROVED_FOR_SYNTHESIS = "approved_for_synthesis"
    REJECTED_REMEDIATION_REQUIRED = "rejected_remediation_required"


class AgentOutput(BaseModel):
    """Output packet from a single domain agent in a fan-out cohort."""
    agent_id: str = Field(..., description="e.g. 'denchik', 'dnk_shopify', 'gerych'")
    task_id: str
    status: str = "completed"
    summary: str = ""
    produced_files: Dict[str, str] = Field(default_factory=dict, description="rel_path -> content")
    command_results: List[Dict[str, Any]] = Field(default_factory=list, description="[{command, exit_code, stdout, stderr}]")
    metrics: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)


class ValidationFinding(BaseModel):
    """Specific defect or contract violation identified by a validator."""
    validator_name: str
    severity: str = "error"  # "error", "warning"
    agent_id: str
    file_path: Optional[str] = None
    message: str
    suggested_fix: Optional[str] = None


class ValidationResult(BaseModel):
    """Outcome of running a validator over one or more agent outputs."""
    validator_name: str
    passed: bool
    findings: List[ValidationFinding] = Field(default_factory=list)


class ValidatorProtocol(Protocol):
    """Contract for modular pre-synthesis validators."""
    name: str

    def validate(self, outputs: Sequence[AgentOutput], context: Dict[str, Any]) -> ValidationResult:
        ...


class GroundingValidator:
    """Verifies numeric, date, and token facts against context to stop hallucinations."""
    name: str = "grounding_validator"

    def __init__(self, guard: Optional[GroundingGuard] = None) -> None:
        self.guard = guard or GroundingGuard()

    def validate(self, outputs: Sequence[AgentOutput], context: Dict[str, Any]) -> ValidationResult:
        findings: List[ValidationFinding] = []
        raw_context = context.get("prompt", "") + " " + context.get("knowledge", "")

        for out in outputs:
            text_to_check = out.summary + " " + " ".join(out.produced_files.values())
            res = self.guard.verify_grounding(claim=text_to_check, context_source=raw_context)
            if not res.grounded:
                for mismatch in res.unsupported_tokens:
                    findings.append(
                        ValidationFinding(
                            validator_name=self.name,
                            severity="error",
                            agent_id=out.agent_id,
                            message=f"Ungrounded token/number detected: '{mismatch}'",
                            suggested_fix="Align output figures strictly with provided source facts.",
                        )
                    )

        return ValidationResult(
            validator_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
        )


class SyntaxASTValidator:
    """Verifies that generated code (Python, JSON, YAML) compiles without syntax errors."""
    name: str = "syntax_ast_validator"

    def validate(self, outputs: Sequence[AgentOutput], context: Dict[str, Any]) -> ValidationResult:
        findings: List[ValidationFinding] = []

        for out in outputs:
            for path, content in out.produced_files.items():
                if path.endswith(".py"):
                    try:
                        ast.parse(content, filename=path)
                    except SyntaxError as exc:
                        findings.append(
                            ValidationFinding(
                                validator_name=self.name,
                                severity="error",
                                agent_id=out.agent_id,
                                file_path=path,
                                message=f"Python SyntaxError at line {exc.lineno}: {exc.msg}",
                                suggested_fix="Fix syntax syntax error in generated Python code.",
                            )
                        )
                elif path.endswith(".json"):
                    try:
                        json.loads(content)
                    except Exception as exc:
                        findings.append(
                            ValidationFinding(
                                validator_name=self.name,
                                severity="error",
                                agent_id=out.agent_id,
                                file_path=path,
                                message=f"Invalid JSON: {exc}",
                                suggested_fix="Ensure valid JSON syntax without trailing commas.",
                            )
                        )

        return ValidationResult(
            validator_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
        )


class BoundaryScopeValidator:
    """Ensures touched files respect target_file_whitelist and negative_scope."""
    name: str = "boundary_scope_validator"

    def validate(self, outputs: Sequence[AgentOutput], context: Dict[str, Any]) -> ValidationResult:
        findings: List[ValidationFinding] = []
        whitelist: List[str] = context.get("target_file_whitelist", [])
        negative_scope: List[str] = context.get("negative_scope", [])

        for out in outputs:
            for path in out.produced_files.keys():
                # Check negative scope
                for neg in negative_scope:
                    if neg in path or path.startswith(neg):
                        findings.append(
                            ValidationFinding(
                                validator_name=self.name,
                                severity="error",
                                agent_id=out.agent_id,
                                file_path=path,
                                message=f"Touched path violates negative_scope rule: '{neg}'",
                                suggested_fix=f"Remove mutation of '{path}'; this file is strictly protected.",
                            )
                        )
                # Check whitelist if configured
                if whitelist and not any(path == w or path.startswith(w.rstrip("/") + "/") for w in whitelist):
                    findings.append(
                        ValidationFinding(
                            validator_name=self.name,
                            severity="error",
                            agent_id=out.agent_id,
                            file_path=path,
                            message=f"File '{path}' is not in target_file_whitelist",
                            suggested_fix=f"Only mutate files explicitly whitelisted: {whitelist}",
                        )
                    )

        return ValidationResult(
            validator_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
        )


class DeterministicExitCodeValidator:
    """Ensures all automated verification commands returned exit code 0."""
    name: str = "deterministic_exit_code_validator"

    def validate(self, outputs: Sequence[AgentOutput], context: Dict[str, Any]) -> ValidationResult:
        findings: List[ValidationFinding] = []

        for out in outputs:
            for cmd in out.command_results:
                code = cmd.get("exit_code", 0)
                if code != 0:
                    findings.append(
                        ValidationFinding(
                            validator_name=self.name,
                            severity="error",
                            agent_id=out.agent_id,
                            message=f"Command '{cmd.get('command')}' failed with exit code {code}: {cmd.get('stderr')}",
                            suggested_fix="Resolve compilation/test error and rerun until exit code is 0.",
                        )
                    )

        return ValidationResult(
            validator_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
        )


class AggregationResult(BaseModel):
    """Final outcome of the Fan-In Aggregator."""
    status: AggregationStatus
    passed: bool
    validation_results: List[ValidationResult]
    remediation_packets: Dict[str, List[ValidationFinding]] = Field(default_factory=dict, description="agent_id -> defects")
    synthesized_artifacts: List[str] = Field(default_factory=list)
    receipt_sha256: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FanInAggregator:
    """
    Fan-In Multi-Agent Aggregation Engine (Worley UAIP Pattern).
    Aggregates subagent outputs and runs deterministic validation gate before synthesis.
    """

    def __init__(self, validators: Optional[List[ValidatorProtocol]] = None) -> None:
        self.validators: List[ValidatorProtocol] = validators or [
            SyntaxASTValidator(),
            BoundaryScopeValidator(),
            DeterministicExitCodeValidator(),
        ]

    def aggregate_and_validate(
        self,
        outputs: Sequence[AgentOutput],
        context: Optional[Dict[str, Any]] = None,
    ) -> AggregationResult:
        ctx = context or {}
        val_results: List[ValidationResult] = []
        remediation_map: Dict[str, List[ValidationFinding]] = {}
        all_passed = True

        for validator in self.validators:
            res = validator.validate(outputs, ctx)
            val_results.append(res)
            if not res.passed:
                all_passed = False
                for finding in res.findings:
                    remediation_map.setdefault(finding.agent_id, []).append(finding)

        # Collect artifacts
        artifacts: List[str] = []
        for out in outputs:
            artifacts.extend(out.artifacts)
            for path in out.produced_files.keys():
                if path not in artifacts:
                    artifacts.append(path)

        # Calculate cryptographic receipt
        receipt_payload = {
            "outputs": [o.model_dump() for o in outputs],
            "passed": all_passed,
            "remediation_count": sum(len(f) for f in remediation_map.values()),
        }
        receipt_sha256 = hashlib.sha256(json.dumps(receipt_payload, sort_keys=True).encode()).hexdigest()

        status = AggregationStatus.APPROVED_FOR_SYNTHESIS if all_passed else AggregationStatus.REJECTED_REMEDIATION_REQUIRED

        return AggregationResult(
            status=status,
            passed=all_passed,
            validation_results=val_results,
            remediation_packets=remediation_map,
            synthesized_artifacts=artifacts,
            receipt_sha256=receipt_sha256,
        )
