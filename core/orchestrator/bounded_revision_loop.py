# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/bounded_revision_loop.py"
# purpose: "Bounded Revision Loop (Builder <-> Auditor): Finite State Machine for up to 3 automatic code revisions upon Fan-In 4-Gate rejection."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from core.canvas.session_router import SpatialCanvasSessionRouter
from core.orchestrator.fan_in_aggregator import (
    AgentOutput,
    AggregationResult,
    FanInAggregator,
    ValidationFinding,
)
from core.sentinel.agent_quarantine import (
    AgentQuarantineGuard,
    QuarantineReason,
)

logger = logging.getLogger("dnk.orchestrator.revision_loop")


class RevisionLoopState(str, Enum):
    INITIAL = "initial"
    BUILDING = "building"
    AUDITING = "auditing"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"
    QUARANTINED_FAILED = "quarantined_failed"


class RevisionAttempt(BaseModel):
    """Record of a single execution and verification attempt in the revision loop."""
    attempt_number: int
    outputs: List[AgentOutput]
    passed: bool
    remediation_findings: Dict[str, List[ValidationFinding]] = Field(default_factory=dict)
    feedback_message: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RevisionLoopResult(BaseModel):
    """Terminal outcome of the Bounded Revision Loop."""
    status: RevisionLoopState
    passed: bool
    total_revisions: int
    max_revisions: int = 3
    attempts: List[RevisionAttempt] = Field(default_factory=list)
    final_aggregation: Optional[AggregationResult] = None
    quarantined_agents: List[str] = Field(default_factory=list)
    receipt_sha256: str = ""


class BoundedRevisionLoop:
    """
    Finite State Machine driving the Builder <-> Auditor Bounded Revision Loop (DEC-120).
    Allows up to MAX_REVISIONS (default 3) automatic iterations.
    Upon each rejection by FanInAggregator:
    - Increments revision count.
    - Formulates structured feedback for the builder.
    - If session_router is provided, posts feedback into the node chat session.
    - Re-dispatches builder_fn with remediation packet.
    - If failures reach MAX_REVISIONS, trips TC-10 AgentQuarantineGuard and fails the node.
    """

    MAX_REVISIONS: int = 3

    def __init__(
        self,
        aggregator: Optional[FanInAggregator] = None,
        quarantine_guard: Optional[AgentQuarantineGuard] = None,
        session_router: Optional[SpatialCanvasSessionRouter] = None,
        max_revisions: int = MAX_REVISIONS,
    ) -> None:
        self.aggregator = aggregator or FanInAggregator()
        self.quarantine_guard = quarantine_guard or AgentQuarantineGuard()
        self.session_router = session_router
        self.max_revisions = max_revisions

    def execute_loop(
        self,
        canvas_path: Path,
        node_id: str,
        builder_fn: Callable[[int, Optional[Dict[str, List[ValidationFinding]]]], List[AgentOutput]],
        context: Optional[Dict[str, Any]] = None,
    ) -> RevisionLoopResult:
        ctx = context or {}
        attempts: List[RevisionAttempt] = []
        canvas_id = canvas_path.stem
        session_id = f"node:{canvas_id}:{node_id}"

        if self.session_router:
            self.session_router.get_or_create_session(canvas_id, node_id)

        remediation_packet: Optional[Dict[str, List[ValidationFinding]]] = None
        final_agg: Optional[AggregationResult] = None
        quarantined: List[str] = []

        for attempt_idx in range(1, self.max_revisions + 1):
            # 1. Builder phase
            outputs = builder_fn(attempt_idx, remediation_packet)

            # Ensure all builders can execute (not in quarantine)
            for out in outputs:
                self.quarantine_guard.assert_can_execute(out.agent_id)

            # 2. Auditor / Fan-In Gate phase
            agg_result = self.aggregator.aggregate_and_validate(outputs, ctx)
            final_agg = agg_result

            if agg_result.passed:
                # Success! Record success in quarantine guard to reset counters
                for out in outputs:
                    self.quarantine_guard.record_success(out.agent_id)

                feedback = f"✅ Fan-In 4-Gate APPROVED on attempt {attempt_idx}/{self.max_revisions}."
                if self.session_router:
                    self.session_router.post_message(
                        session_id=session_id,
                        role="system",
                        content=feedback,
                        meta={"receipt_sha256": agg_result.receipt_sha256, "attempt": attempt_idx},
                    )

                attempts.append(
                    RevisionAttempt(
                        attempt_number=attempt_idx,
                        outputs=outputs,
                        passed=True,
                        feedback_message=feedback,
                    )
                )

                return RevisionLoopResult(
                    status=RevisionLoopState.APPROVED,
                    passed=True,
                    total_revisions=attempt_idx,
                    max_revisions=self.max_revisions,
                    attempts=attempts,
                    final_aggregation=agg_result,
                    quarantined_agents=[],
                    receipt_sha256=agg_result.receipt_sha256,
                )

            # Validation rejected!
            defects_summary = []
            for agent_id, findings in agg_result.remediation_packets.items():
                self.quarantine_guard.record_validation_failure(
                    agent_id,
                    f"Fan-In gate failure on attempt {attempt_idx}: {findings[0].message if findings else 'unknown defect'}",
                )
                for f in findings:
                    defects_summary.append(f"- [{f.validator_name}] {agent_id}: {f.message}")

            feedback = (
                f"⚔️ Fan-In Gate REJECTED (Attempt {attempt_idx}/{self.max_revisions}):\n"
                + "\n".join(defects_summary)
            )

            if self.session_router:
                self.session_router.post_message(
                    session_id=session_id,
                    role="system",
                    content=feedback,
                    meta={"remediation": [f.model_dump() for fl in agg_result.remediation_packets.values() for f in fl]},
                )

            attempts.append(
                RevisionAttempt(
                    attempt_number=attempt_idx,
                    outputs=outputs,
                    passed=False,
                    remediation_findings=agg_result.remediation_packets,
                    feedback_message=feedback,
                )
            )

            # Check if we have attempts left
            if attempt_idx < self.max_revisions:
                remediation_packet = agg_result.remediation_packets
                logger.warning(
                    "Revision %d/%d failed for node %s. Re-dispatching builder.",
                    attempt_idx,
                    self.max_revisions,
                    node_id,
                )
            else:
                # 3 Strikes reached! Trip quarantine
                for agent_id in agg_result.remediation_packets.keys():
                    self.quarantine_guard.trip_quarantine(
                        agent_id=agent_id,
                        reason=QuarantineReason.MAX_FAILURES_EXCEEDED,
                        details=f"Agent '{agent_id}' exceeded {self.max_revisions} bounded revision attempts in node '{node_id}'.",
                    )
                    quarantined.append(agent_id)

        return RevisionLoopResult(
            status=RevisionLoopState.QUARANTINED_FAILED,
            passed=False,
            total_revisions=self.max_revisions,
            max_revisions=self.max_revisions,
            attempts=attempts,
            final_aggregation=final_agg,
            quarantined_agents=quarantined,
            receipt_sha256=final_agg.receipt_sha256 if final_agg else "",
        )
