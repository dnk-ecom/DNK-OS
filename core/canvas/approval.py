# --- DNK-MRH-HEADER ---
# mrh_id: "core/canvas/approval.py"
# purpose: "Formal Human-in-the-Loop Approval MVP Models and Engine for Canvas Critical State Changes (CANVAS-004)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-10"
# author: "DNK-e.com Maksym / Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
Canvas Human-in-the-Loop Approval MVP.

Provides data models, critical operation rules, and JSONL persistence
for human review of critical CanvasState changes.
Strictly zero-network, zero-secrets, and strictly relative path enforced.
"""

import json
import math
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

DEFAULT_PENDING_FILE = "core/templates/canvas/approvals/pending_approvals.jsonl"
DEFAULT_HISTORY_FILE = "core/templates/canvas/approvals/approval_history.jsonl"


def _enforce_relative_path(path_str: str) -> Path:
    """Ensure path is strictly relative and does not escape via root."""
    if os.path.isabs(path_str):
        raise ValueError(f"Absolute path is forbidden: {path_str}")
    p = Path(path_str)
    # Check if parts or resolved form attempts absolute root
    if str(p).startswith("/") or str(p).startswith("\\"):
        raise ValueError(f"Absolute path is forbidden: {path_str}")
    return p


class ApprovalOperationType(str, Enum):
    CANVAS_NODE_REMOVE = "canvas.node.remove"
    CANVAS_EDGE_REMOVE = "canvas.edge.remove"
    CANVAS_NODE_MOVE = "canvas.node.move"
    CANVAS_STATE_RESET = "canvas.state.reset"
    CANVAS_NODE_ADD = "canvas.node.add"
    CANVAS_EDGE_ADD = "canvas.edge.add"
    CANVAS_NODE_UPDATE = "canvas.node.update"
    CANVAS_STATE_UPDATE = "canvas.state.update"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Decision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    canvas_id: str
    operation_type: str
    operation_payload: Dict[str, Any] = Field(default_factory=dict)
    requester_id: str = "gerych_prime"
    approver_id: str = "maksym"
    status: str = ApprovalStatus.PENDING.value
    reason: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {s.value for s in ApprovalStatus}
        if v not in valid:
            raise ValueError(f"Invalid status '{v}'. Must be one of {valid}")
        return v


class ApprovalHistoryEntry(BaseModel):
    request_id: str
    decided_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    approver_id: str = "maksym"
    decision: str
    reason: Optional[str] = None
    canvas_id: Optional[str] = None
    operation_type: Optional[str] = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        valid = {d.value for d in Decision}
        if v not in valid:
            raise ValueError(f"Invalid decision '{v}'. Must be one of {valid}")
        return v


def is_critical_operation(
    operation_type: str,
    operation_payload: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Evaluates whether a given canvas operation requires human approval.

    Critical operations:
      - canvas.node.remove
      - canvas.edge.remove
      - canvas.node.move with large coordinate delta (>500px)
      - canvas.state.reset
    """
    payload = operation_payload or {}

    if operation_type in (
        ApprovalOperationType.CANVAS_NODE_REMOVE.value,
        ApprovalOperationType.CANVAS_EDGE_REMOVE.value,
        ApprovalOperationType.CANVAS_STATE_RESET.value,
    ):
        return True

    if operation_type == ApprovalOperationType.CANVAS_NODE_MOVE.value:
        # Check explicit flag
        if payload.get("critical") is True:
            return True

        # Check delta_x / delta_y
        delta_x = payload.get("delta_x")
        delta_y = payload.get("delta_y")
        if delta_x is not None or delta_y is not None:
            dx = float(delta_x or 0.0)
            dy = float(delta_y or 0.0)
            dist = math.hypot(dx, dy)
            if dist > 500.0 or abs(dx) > 500.0 or abs(dy) > 500.0:
                return True

        # Check from_position / to_position
        from_pos = payload.get("from_position") or payload.get("old_position")
        to_pos = payload.get("to_position") or payload.get("new_position")
        if isinstance(from_pos, dict) and isinstance(to_pos, dict):
            dx = float(to_pos.get("x", 0.0)) - float(from_pos.get("x", 0.0))
            dy = float(to_pos.get("y", 0.0)) - float(from_pos.get("y", 0.0))
            dist = math.hypot(dx, dy)
            if dist > 500.0 or abs(dx) > 500.0 or abs(dy) > 500.0:
                return True

        # Check raw distance field
        if "distance" in payload and float(payload["distance"]) > 500.0:
            return True

        return False

    return False


class ApprovalManager:
    """Manages creation, review, and recording of Canvas approvals via JSONL."""

    def __init__(
        self,
        pending_file: str = DEFAULT_PENDING_FILE,
        history_file: str = DEFAULT_HISTORY_FILE,
    ):
        self.pending_path = _enforce_relative_path(pending_file)
        self.history_path = _enforce_relative_path(history_file)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        self.pending_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.pending_path.exists():
            self.pending_path.touch()
        if not self.history_path.exists():
            self.history_path.touch()

    def create_request(
        self,
        canvas_id: str,
        operation_type: str,
        operation_payload: Dict[str, Any],
        requester_id: str = "gerych_prime",
        approver_id: str = "maksym",
        reason: Optional[str] = None,
    ) -> ApprovalRequest:
        """Create and persist a new pending approval request."""
        req = ApprovalRequest(
            canvas_id=canvas_id,
            operation_type=operation_type,
            operation_payload=operation_payload,
            requester_id=requester_id,
            approver_id=approver_id,
            status=ApprovalStatus.PENDING.value,
            reason=reason,
        )

        with open(self.pending_path, "a", encoding="utf-8") as f:
            f.write(req.model_dump_json() + "\n")

        return req

    def list_pending(
        self, canvas_id: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """List all pending approval requests, optionally filtered by canvas_id."""
        if not self.pending_path.exists():
            return []

        results: List[ApprovalRequest] = []
        with open(self.pending_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    req = ApprovalRequest.model_validate(data)
                    if req.status == ApprovalStatus.PENDING.value:
                        if canvas_id is None or req.canvas_id == canvas_id:
                            results.append(req)
                except Exception:
                    continue
        return results

    def decide(
        self,
        request_id: str,
        decision: str,
        approver_id: str = "maksym",
        reason: Optional[str] = None,
    ) -> Tuple[ApprovalRequest, ApprovalHistoryEntry]:
        """
        Record a decision (approved or rejected) for a pending request.
        Updates pending_approvals.jsonl and appends to approval_history.jsonl.
        """
        valid_decisions = {d.value for d in Decision}
        if decision not in valid_decisions:
            raise ValueError(
                f"Invalid decision '{decision}'. Must be one of {valid_decisions}"
            )

        if not self.pending_path.exists():
            raise ValueError(f"Approval request '{request_id}' not found.")

        all_requests: List[Dict[str, Any]] = []
        target_req: Optional[ApprovalRequest] = None

        with open(self.pending_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("request_id") == request_id:
                    target_req = ApprovalRequest.model_validate(data)
                    target_req.status = decision
                    target_req.approver_id = approver_id
                    if reason:
                        target_req.reason = reason
                    all_requests.append(target_req.model_dump())
                else:
                    all_requests.append(data)

        if target_req is None:
            raise ValueError(f"Approval request '{request_id}' not found.")

        # Re-write pending file with updated status
        with open(self.pending_path, "w", encoding="utf-8") as f:
            for item in all_requests:
                f.write(json.dumps(item) + "\n")

        # Create history entry
        history_entry = ApprovalHistoryEntry(
            request_id=request_id,
            approver_id=approver_id,
            decision=decision,
            reason=reason,
            canvas_id=target_req.canvas_id,
            operation_type=target_req.operation_type,
        )

        with open(self.history_path, "a", encoding="utf-8") as f:
            f.write(history_entry.model_dump_json() + "\n")

        return target_req, history_entry

    def get_history(
        self, canvas_id: Optional[str] = None
    ) -> List[ApprovalHistoryEntry]:
        """Retrieve history entries, optionally filtered by canvas_id."""
        if not self.history_path.exists():
            return []

        entries: List[ApprovalHistoryEntry] = []
        with open(self.history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = ApprovalHistoryEntry.model_validate(data)
                    if canvas_id is None or entry.canvas_id == canvas_id:
                        entries.append(entry)
                except Exception:
                    continue
        return entries
