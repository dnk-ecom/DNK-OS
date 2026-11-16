# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/agent_quarantine.py"
# purpose: "Automated Agent Quarantine & Circuit Breaker (assimilated from Worley UAIP TC-10 agent_suspension)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.sentinel.quarantine")


class QuarantineReason(str, Enum):
    MAX_FAILURES_EXCEEDED = "max_failures_exceeded"
    TOOL_CALL_LIMIT_EXCEEDED = "tool_call_limit_exceeded"
    NEGATIVE_SCOPE_VIOLATION = "negative_scope_violation"
    UNHANDLED_TIMEOUT = "unhandled_timeout"
    MANUAL_OPERATOR_TRIP = "manual_operator_trip"


class AgentState(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"


class AgentQuarantinedError(RuntimeError):
    """Raised when an attempt is made to execute an agent in quarantined state."""
    def __init__(self, agent_id: str, reason: str, incident_sha256: str) -> None:
        super().__init__(f"Agent '{agent_id}' is QUARANTINED ({reason}). Incident SHA: {incident_sha256[:12]}")
        self.agent_id = agent_id
        self.reason = reason
        self.incident_sha256 = incident_sha256


class QuarantineIncident(BaseModel):
    """Tamper-evident audit record of a triggered agent circuit breaker."""
    incident_id: str
    agent_id: str
    reason: QuarantineReason
    details: str
    tripped_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    receipt_sha256: str = ""


class AgentHealthRecord(BaseModel):
    """Live health and circuit breaker metrics for a domain agent."""
    agent_id: str
    state: AgentState = AgentState.ACTIVE
    consecutive_failures: int = 0
    tool_calls_in_slice: int = 0
    total_tool_calls: int = 0
    last_tripped_reason: Optional[QuarantineReason] = None
    last_incident_sha256: Optional[str] = None
    incidents: List[QuarantineIncident] = Field(default_factory=list)


class AgentQuarantineGuard:
    """
    Automated Agent Circuit Breaker & Quarantine Gate (UAIP TC-10).
    Guarantees strict adherence to MASE bounds (<=25 calls) and stops runaway failure loops.
    """

    MAX_CONSECUTIVE_FAILURES: int = 3
    MAX_TOOL_CALLS_PER_SLICE: int = 25

    def __init__(
        self,
        max_failures: int = MAX_CONSECUTIVE_FAILURES,
        max_slice_calls: int = MAX_TOOL_CALLS_PER_SLICE,
    ) -> None:
        self.max_failures = max_failures
        self.max_slice_calls = max_slice_calls
        self._registry: Dict[str, AgentHealthRecord] = {}

    def get_or_create(self, agent_id: str) -> AgentHealthRecord:
        if agent_id not in self._registry:
            self._registry[agent_id] = AgentHealthRecord(agent_id=agent_id)
        return self._registry[agent_id]

    def assert_can_execute(self, agent_id: str) -> None:
        """Throws AgentQuarantinedError if the agent is currently locked in quarantine."""
        rec = self.get_or_create(agent_id)
        if rec.state == AgentState.QUARANTINED:
            raise AgentQuarantinedError(
                agent_id=agent_id,
                reason=rec.last_tripped_reason.value if rec.last_tripped_reason else "quarantined",
                incident_sha256=rec.last_incident_sha256 or "unknown",
            )

    def record_step(
        self,
        agent_id: str,
        tool_name: str,
        target_path: Optional[str] = None,
        negative_scope: Optional[List[str]] = None,
    ) -> None:
        """Records an execution step and evaluates boundary invariants."""
        self.assert_can_execute(agent_id)
        rec = self.get_or_create(agent_id)

        rec.tool_calls_in_slice += 1
        rec.total_tool_calls += 1

        # 1. Negative Scope Invariant
        if target_path and negative_scope:
            for neg in negative_scope:
                if neg in target_path or target_path.startswith(neg):
                    self.trip_quarantine(
                        agent_id=agent_id,
                        reason=QuarantineReason.NEGATIVE_SCOPE_VIOLATION,
                        details=f"Agent attempted mutation on protected negative_scope path: '{target_path}' (rule '{neg}')",
                    )
                    raise AgentQuarantinedError(
                        agent_id=agent_id,
                        reason=QuarantineReason.NEGATIVE_SCOPE_VIOLATION.value,
                        incident_sha256=rec.last_incident_sha256 or "",
                    )

        # 2. MASE <= 25 Tool Calls Limit
        if rec.tool_calls_in_slice > self.max_slice_calls:
            self.trip_quarantine(
                agent_id=agent_id,
                reason=QuarantineReason.TOOL_CALL_LIMIT_EXCEEDED,
                details=f"Agent exceeded atomic slice ceiling of {self.max_slice_calls} tool calls ({rec.tool_calls_in_slice}). Checkpoint required.",
            )
            raise AgentQuarantinedError(
                agent_id=agent_id,
                reason=QuarantineReason.TOOL_CALL_LIMIT_EXCEEDED.value,
                incident_sha256=rec.last_incident_sha256 or "",
            )

    def record_validation_failure(self, agent_id: str, defect_summary: str) -> None:
        """Tracks consecutive validation failures and trips circuit breaker after 3 failures."""
        rec = self.get_or_create(agent_id)
        rec.consecutive_failures += 1

        if rec.consecutive_failures >= self.max_failures:
            self.trip_quarantine(
                agent_id=agent_id,
                reason=QuarantineReason.MAX_FAILURES_EXCEEDED,
                details=f"Agent reached {rec.consecutive_failures} consecutive validation failures. Last defect: {defect_summary}",
            )
        else:
            rec.state = AgentState.DEGRADED

    def record_success(self, agent_id: str) -> None:
        """Resets failure counter and slice tool-calls upon checkpoint/verified milestone."""
        rec = self.get_or_create(agent_id)
        if rec.state != AgentState.QUARANTINED:
            rec.consecutive_failures = 0
            rec.tool_calls_in_slice = 0
            rec.state = AgentState.ACTIVE

    def trip_quarantine(self, agent_id: str, reason: QuarantineReason, details: str) -> QuarantineIncident:
        """Directly trips the agent circuit breaker and creates an unforgeable incident receipt."""
        rec = self.get_or_create(agent_id)
        rec.state = AgentState.QUARANTINED
        rec.last_tripped_reason = reason

        inc_payload = {
            "agent_id": agent_id,
            "reason": reason.value,
            "details": details,
            "total_calls": rec.total_tool_calls,
            "slice_calls": rec.tool_calls_in_slice,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        receipt_sha256 = hashlib.sha256(json.dumps(inc_payload, sort_keys=True).encode()).hexdigest()
        incident_id = f"inc_{receipt_sha256[:12]}"

        incident = QuarantineIncident(
            incident_id=incident_id,
            agent_id=agent_id,
            reason=reason,
            details=details,
            receipt_sha256=receipt_sha256,
        )
        rec.last_incident_sha256 = receipt_sha256
        rec.incidents.append(incident)

        logger.critical(
            "CIRCUIT BREAKER TRIPPED for agent '%s' (%s). Incident: %s",
            agent_id,
            reason.value,
            incident_id,
        )
        return incident

    def release_agent(self, agent_id: str, approver: str = "founder") -> None:
        """Manually unlocks an agent from quarantine following human or supervisor review."""
        rec = self.get_or_create(agent_id)
        rec.state = AgentState.ACTIVE
        rec.consecutive_failures = 0
        rec.tool_calls_in_slice = 0
        rec.last_tripped_reason = None
        logger.info("Agent '%s' released from quarantine by approver '%s'", agent_id, approver)
