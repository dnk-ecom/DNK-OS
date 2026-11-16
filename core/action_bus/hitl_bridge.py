# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/hitl_bridge.py"
# purpose: "Human-in-the-Loop (HITL) Approval Bridge connecting ActionBus, SwarmRouter, and Canvas ApprovalEngine (CANVAS-004)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

"""
Human-in-the-Loop (HITL) Approval Bridge.

Bridges critical ActionBus operations and Canvas state mutations with
the persistent ApprovalManager (CANVAS-004). Transitions tasks to WAITING_APPROVAL
and broadcasts approval lifecycle events to SSE/WebSocket subscribers.
"""

import logging
from typing import Any, Dict, List, Optional
import uuid

from core.action_bus.models import ActionTaskStatus, BusEvent, BusEventType
from core.canvas.approval import (
    ApprovalHistoryEntry,
    ApprovalManager,
    ApprovalRequest,
    ApprovalStatus,
    Decision,
    is_critical_operation,
)

logger = logging.getLogger("mvr_core.hitl_bridge")


class HitlApprovalBridge:
    """Manages HITL approval gates for ActionBus tasks and Canvas mutations."""

    def __init__(
        self,
        approval_manager: Optional[ApprovalManager] = None,
        bus: Optional[Any] = None,
        pending_file: Optional[str] = None,
        history_file: Optional[str] = None,
    ):
        if approval_manager is not None:
            self.manager = approval_manager
        else:
            kwargs: Dict[str, Any] = {}
            if pending_file:
                kwargs["pending_file"] = pending_file
            if history_file:
                kwargs["history_file"] = history_file
            self.manager = ApprovalManager(**kwargs)

        self.bus = bus
        self._request_to_task: Dict[str, str] = {}
        self._decision_events: Dict[str, Any] = {}
        self._decision_results: Dict[str, ApprovalHistoryEntry] = {}

    def is_critical(
        self,
        operation_type: str,
        operation_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Determines if the operation requires explicit human approval."""
        return is_critical_operation(operation_type, operation_payload or {})

    async def request_approval(
        self,
        canvas_id: str,
        operation_type: str,
        operation_payload: Optional[Dict[str, Any]] = None,
        requester_id: str = "gerych_prime",
        approver_id: str = "maksym",
        reason: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> ApprovalRequest:
        """Creates a pending approval request and notifies the event stream."""
        payload = operation_payload or {}
        req = self.manager.create_request(
            canvas_id=canvas_id,
            operation_type=operation_type,
            operation_payload=payload,
            requester_id=requester_id,
            approver_id=approver_id,
            reason=reason,
        )

        if task_id:
            self._request_to_task[req.request_id] = task_id

        # Broadcast approval requested event
        if self.bus is not None:
            event = BusEvent(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                event_type=BusEventType.APPROVAL_REQUESTED,
                task_id=task_id or f"canvas_{canvas_id}",
                payload={
                    "request_id": req.request_id,
                    "canvas_id": canvas_id,
                    "operation_type": operation_type,
                    "operation_payload": payload,
                    "requester_id": requester_id,
                    "approver_id": approver_id,
                    "reason": reason,
                    "status": ApprovalStatus.PENDING.value,
                    "created_at": req.created_at,
                },
            )
            await self.bus.publish_event(event)

        logger.info(
            f"Approval requested: {req.request_id} for operation {operation_type} (task: {task_id})"
        )
        return req

    async def resolve_approval(
        self,
        request_id: str,
        decision: str,
        approver_id: str = "maksym",
        reason: Optional[str] = None,
    ) -> ApprovalHistoryEntry:
        """Records human decision, notifies event stream, and resolves task gating."""
        dec_lower = decision.lower().strip()
        if dec_lower not in {Decision.APPROVED.value, Decision.REJECTED.value}:
            raise ValueError(
                f"Invalid decision '{decision}'. Must be 'approved' or 'rejected'"
            )

        updated_req, history_entry = self.manager.decide(
            request_id=request_id,
            decision=dec_lower,
            approver_id=approver_id,
            reason=reason,
        )

        task_id = self._request_to_task.get(request_id)

        # Broadcast approval resolved event
        if self.bus is not None:
            event = BusEvent(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                event_type=BusEventType.APPROVAL_RESOLVED,
                task_id=task_id or f"req_{request_id}",
                payload={
                    "request_id": request_id,
                    "decision": dec_lower,
                    "approver_id": approver_id,
                    "reason": reason,
                    "decided_at": history_entry.decided_at,
                    "canvas_id": history_entry.canvas_id,
                    "operation_type": history_entry.operation_type,
                },
            )
            await self.bus.publish_event(event)

        logger.info(
            f"Approval resolved: {request_id} -> {dec_lower} by {approver_id} (reason: {reason})"
        )
        self._decision_results[request_id] = history_entry
        ev = self._decision_events.get(request_id)
        if ev is not None:
            ev.set()

        return history_entry

    async def wait_for_decision(
        self,
        request_id: str,
        timeout_seconds: float = 30.0,
    ) -> Optional[ApprovalHistoryEntry]:
        """
        Asynchronously waits until the given approval request is decided (approved/rejected)
        or until timeout_seconds elapses. Returns None on timeout.
        """
        import asyncio
        if request_id in self._decision_results:
            return self._decision_results[request_id]

        if request_id not in self._decision_events:
            self._decision_events[request_id] = asyncio.Event()

        ev = self._decision_events[request_id]
        try:
            await asyncio.wait_for(ev.wait(), timeout=timeout_seconds)
            return self._decision_results.get(request_id)
        except asyncio.TimeoutError:
            return None

    def list_pending(self, canvas_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Lists pending approvals, optionally filtered by canvas_id."""
        return self.manager.list_pending(canvas_id=canvas_id)

    def get_history(
        self,
        canvas_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[ApprovalHistoryEntry]:
        """Returns approval history, optionally filtered by canvas_id."""
        entries = self.manager.get_history(canvas_id=canvas_id)
        return entries[-limit:]
