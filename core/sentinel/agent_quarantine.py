# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/agent_quarantine.py"
# purpose: "Automated Agent Quarantine & Circuit Breaker with Persistent SQLite WAL Ledger (assimilated from Worley UAIP TC-10 agent_suspension)."
# canonical_source: true
# alters_files: ["~/.dnk_runtime/agents_state/agent_quarantine.db", ".data/agent_quarantine.db"]
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.sentinel.quarantine")

DEFAULT_QUARANTINE_DB = Path(os.path.expanduser("~/.dnk_runtime/agents_state/agent_quarantine.db"))
FALLBACK_QUARANTINE_DB = Path(".data/agent_quarantine.db")


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
    Persists strike history and quarantine states across sessions via SQLite WAL ledger.
    """

    MAX_CONSECUTIVE_FAILURES: int = 3
    MAX_TOOL_CALLS_PER_SLICE: int = 25

    def __init__(
        self,
        max_failures: int = MAX_CONSECUTIVE_FAILURES,
        max_slice_calls: int = MAX_TOOL_CALLS_PER_SLICE,
        db_path: Optional[Path | str] = None,
    ) -> None:
        self.max_failures = max_failures
        self.max_slice_calls = max_slice_calls
        if db_path is not None:
            self.db_path = Path(db_path) if db_path != ":memory:" else db_path
        elif os.environ.get("PYTEST_CURRENT_TEST"):
            self.db_path = ":memory:"
        elif DEFAULT_QUARANTINE_DB.parent.exists():
            self.db_path = DEFAULT_QUARANTINE_DB
        else:
            self.db_path = FALLBACK_QUARANTINE_DB

        self._registry: Dict[str, AgentHealthRecord] = {}
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if not hasattr(self, "_mem_conn") or self._mem_conn is None:
                self._mem_conn = sqlite3.connect(":memory:", timeout=15.0)
                self._mem_conn.row_factory = sqlite3.Row
            return self._mem_conn

        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_quarantine_ledger (
                    agent_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL DEFAULT 'active',
                    consecutive_failures INTEGER NOT NULL DEFAULT 0,
                    tool_calls_in_slice INTEGER NOT NULL DEFAULT 0,
                    total_tool_calls INTEGER NOT NULL DEFAULT 0,
                    last_tripped_reason TEXT,
                    last_incident_sha256 TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS agent_quarantine_incidents (
                    incident_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    details TEXT NOT NULL,
                    receipt_sha256 TEXT NOT NULL,
                    tripped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(agent_id) REFERENCES agent_quarantine_ledger(agent_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_incidents_agent ON agent_quarantine_incidents(agent_id);
            """)

    def _save_record(self, rec: AgentHealthRecord, incident: Optional[QuarantineIncident] = None) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO agent_quarantine_ledger
                (agent_id, state, consecutive_failures, tool_calls_in_slice, total_tool_calls, last_tripped_reason, last_incident_sha256, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id) DO UPDATE SET
                    state = excluded.state,
                    consecutive_failures = excluded.consecutive_failures,
                    tool_calls_in_slice = excluded.tool_calls_in_slice,
                    total_tool_calls = excluded.total_tool_calls,
                    last_tripped_reason = excluded.last_tripped_reason,
                    last_incident_sha256 = excluded.last_incident_sha256,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    rec.agent_id,
                    rec.state.value if hasattr(rec.state, "value") else str(rec.state),
                    rec.consecutive_failures,
                    rec.tool_calls_in_slice,
                    rec.total_tool_calls,
                    rec.last_tripped_reason.value if rec.last_tripped_reason and hasattr(rec.last_tripped_reason, "value") else (str(rec.last_tripped_reason) if rec.last_tripped_reason else None),
                    rec.last_incident_sha256,
                ),
            )
            if incident:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO agent_quarantine_incidents
                    (incident_id, agent_id, reason, details, receipt_sha256, tripped_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        incident.incident_id,
                        incident.agent_id,
                        incident.reason.value if hasattr(incident.reason, "value") else str(incident.reason),
                        incident.details,
                        incident.receipt_sha256,
                        incident.tripped_at,
                    ),
                )

    def get_or_create(self, agent_id: str) -> AgentHealthRecord:
        if agent_id in self._registry:
            return self._registry[agent_id]

        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agent_quarantine_ledger WHERE agent_id = ?", (agent_id,)
            ).fetchone()

            if row:
                inc_rows = conn.execute(
                    "SELECT * FROM agent_quarantine_incidents WHERE agent_id = ? ORDER BY tripped_at ASC",
                    (agent_id,),
                ).fetchall()
                incidents = [
                    QuarantineIncident(
                        incident_id=r["incident_id"],
                        agent_id=r["agent_id"],
                        reason=QuarantineReason(r["reason"]),
                        details=r["details"],
                        receipt_sha256=r["receipt_sha256"],
                        tripped_at=str(r["tripped_at"]),
                    )
                    for r in inc_rows
                ]
                rec = AgentHealthRecord(
                    agent_id=row["agent_id"],
                    state=AgentState(row["state"]),
                    consecutive_failures=row["consecutive_failures"],
                    tool_calls_in_slice=row["tool_calls_in_slice"],
                    total_tool_calls=row["total_tool_calls"],
                    last_tripped_reason=QuarantineReason(row["last_tripped_reason"]) if row["last_tripped_reason"] else None,
                    last_incident_sha256=row["last_incident_sha256"],
                    incidents=incidents,
                )
                self._registry[agent_id] = rec
                return rec
            else:
                rec = AgentHealthRecord(agent_id=agent_id)
                conn.execute(
                    """
                    INSERT INTO agent_quarantine_ledger
                    (agent_id, state, consecutive_failures, tool_calls_in_slice, total_tool_calls)
                    VALUES (?, ?, 0, 0, 0)
                    """,
                    (agent_id, rec.state.value),
                )
                self._registry[agent_id] = rec
                return rec

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

        self._save_record(rec)

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
            self._save_record(rec)

    def record_success(self, agent_id: str) -> None:
        """Resets failure counter and slice tool-calls upon checkpoint/verified milestone."""
        rec = self.get_or_create(agent_id)
        if rec.state != AgentState.QUARANTINED:
            rec.consecutive_failures = 0
            rec.tool_calls_in_slice = 0
            rec.state = AgentState.ACTIVE
            self._save_record(rec)

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

        self._save_record(rec, incident)

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
        self._save_record(rec)
        logger.info("Agent '%s' released from quarantine by approver '%s'", agent_id, approver)
