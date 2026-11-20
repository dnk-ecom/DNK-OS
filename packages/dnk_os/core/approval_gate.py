# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/approval_gate.py"
# purpose: "Human-in-the-Loop (HITL) approval gate for sensitive operations"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""
Approval Gate (HITL) Module for DNK OS.

Provides Human-in-the-Loop approval workflows, interrupt handling,
audit logging, and persistence for expensive or sensitive actions.
"""

import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dnk_os.core.checkpointer import DNKCheckpointer, create_checkpointer


class ApprovalStatus(Enum):
    """Approval status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class DNKApprovalGate:
    """
    Human-in-the-Loop (HITL) approval gate for DNK OS.
    
    Blocks expensive actions until human approval.
    
    Supports:
    - Approval workflows
    - Timeout handling
    - Audit logging
    - Integration with Supervisor and Checkpointer
    """
    
    def __init__(
        self,
        checkpointer_backend: str = "memory",
        checkpointer: Optional[DNKCheckpointer] = None,
        timeout_seconds: int = 300,
        **kwargs: Any
    ):
        """
        Initialize Approval Gate.
        
        Args:
            checkpointer_backend: Backend type ("memory", "sqlite", "redis")
            checkpointer: Optional pre-configured checkpointer
            timeout_seconds: Approval timeout in seconds (default 5 minutes)
            **kwargs: Additional arguments
        """
        self.checkpointer: Optional[DNKCheckpointer] = checkpointer or create_checkpointer(backend=checkpointer_backend)
        self.timeout_seconds = timeout_seconds
        self.audit_log: List[Dict[str, Any]] = []
        self._requests: Dict[str, Dict[str, Any]] = {}

    def request_approval(
        self,
        action: str,
        context: Dict[str, Any],
        thread_id: str,
        approver_id: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Request human approval for action.
        
        Args:
            action: Action name (e.g., "delete_agent", "deploy", "sensitive_operation")
            context: Action context (e.g., {"agent_name": "Герич", "reason": "..."})
            thread_id: Thread identifier
            approver_id: Optional specific approver ID
            **kwargs: Additional request metadata
            
        Returns:
            Approval request ID
        """
        request_id = kwargs.get("request_id") or f"req_{uuid.uuid4().hex[:12]}"
        created_at = time.time()
        
        request_data = {
            "request_id": request_id,
            "action": action,
            "context": context,
            "thread_id": thread_id,
            "approver_id": approver_id,
            "status": ApprovalStatus.PENDING.value,
            "created_at": created_at,
            "updated_at": created_at,
            "comments": None,
            "reason": None,
            **kwargs
        }
        
        self._requests[request_id] = request_data
        
        # Persist request if checkpointer is available
        if self.checkpointer:
            self.checkpointer.put(
                thread_id=thread_id,
                checkpoint=request_data,
                checkpoint_ns=f"approval_{request_id}"
            )
            
        self.audit_log.append({
            "event": "approval_requested",
            "request_id": request_id,
            "thread_id": thread_id,
            "action": action,
            "timestamp": created_at
        })
        
        return request_id

    def get_approval_status(
        self,
        request_id: str,
        thread_id: str,
        **kwargs: Any
    ) -> ApprovalStatus:
        """
        Get approval status.
        
        Args:
            request_id: Approval request ID
            thread_id: Thread identifier
            **kwargs: Additional arguments
            
        Returns:
            ApprovalStatus enum
        """
        req = self._requests.get(request_id)
        if not req and self.checkpointer:
            req = self.checkpointer.get(
                thread_id=thread_id,
                checkpoint_ns=f"approval_{request_id}"
            )
            if req:
                self._requests[request_id] = req
                
        if not req:
            return ApprovalStatus.REJECTED
            
        current_status_str = req.get("status", ApprovalStatus.PENDING.value)
        
        # Check timeout if still pending
        if current_status_str == ApprovalStatus.PENDING.value:
            created_at = req.get("created_at", time.time())
            timeout_limit = kwargs.get("timeout_seconds", self.timeout_seconds)
            if time.time() - created_at > timeout_limit:
                req["status"] = ApprovalStatus.TIMEOUT.value
                req["updated_at"] = time.time()
                if self.checkpointer:
                    self.checkpointer.put(
                        thread_id=thread_id,
                        checkpoint=req,
                        checkpoint_ns=f"approval_{request_id}"
                    )
                self.audit_log.append({
                    "event": "approval_timeout",
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "timestamp": time.time()
                })
                return ApprovalStatus.TIMEOUT
                
        return ApprovalStatus(req["status"])

    def approve(
        self,
        request_id: str,
        thread_id: str,
        approver_id: str,
        comments: Optional[str] = None,
        **kwargs: Any
    ) -> bool:
        """
        Approve action.
        
        Args:
            request_id: Approval request ID
            thread_id: Thread identifier
            approver_id: Approver identifier
            comments: Optional approval comments
            **kwargs: Additional metadata
            
        Returns:
            True if approved successfully
        """
        req = self._requests.get(request_id)
        if not req and self.checkpointer:
            req = self.checkpointer.get(
                thread_id=thread_id,
                checkpoint_ns=f"approval_{request_id}"
            )
            
        if not req:
            return False
            
        now = time.time()
        req["status"] = ApprovalStatus.APPROVED.value
        req["approver_id"] = approver_id
        req["comments"] = comments
        req["updated_at"] = now
        self._requests[request_id] = req
        
        if self.checkpointer:
            self.checkpointer.put(
                thread_id=thread_id,
                checkpoint=req,
                checkpoint_ns=f"approval_{request_id}"
            )
            
        self.audit_log.append({
            "event": "approved",
            "request_id": request_id,
            "thread_id": thread_id,
            "approver_id": approver_id,
            "comments": comments,
            "timestamp": now
        })
        return True

    def reject(
        self,
        request_id: str,
        thread_id: str,
        approver_id: str,
        reason: Optional[str] = None,
        **kwargs: Any
    ) -> bool:
        """
        Reject action.
        
        Args:
            request_id: Approval request ID
            thread_id: Thread identifier
            approver_id: Approver identifier
            reason: Optional rejection reason
            **kwargs: Additional metadata
            
        Returns:
            True if rejected successfully
        """
        req = self._requests.get(request_id)
        if not req and self.checkpointer:
            req = self.checkpointer.get(
                thread_id=thread_id,
                checkpoint_ns=f"approval_{request_id}"
            )
            
        if not req:
            return False
            
        now = time.time()
        req["status"] = ApprovalStatus.REJECTED.value
        req["approver_id"] = approver_id
        req["reason"] = reason
        req["updated_at"] = now
        self._requests[request_id] = req
        
        if self.checkpointer:
            self.checkpointer.put(
                thread_id=thread_id,
                checkpoint=req,
                checkpoint_ns=f"approval_{request_id}"
            )
            
        self.audit_log.append({
            "event": "rejected",
            "request_id": request_id,
            "thread_id": thread_id,
            "approver_id": approver_id,
            "reason": reason,
            "timestamp": now
        })
        return True

    def wait_for_approval(
        self,
        request_id: str,
        thread_id: str,
        poll_interval: float = 0.1,
        **kwargs: Any
    ) -> ApprovalStatus:
        """
        Wait for approval (blocking until decision or timeout).
        
        Args:
            request_id: Approval request ID
            thread_id: Thread identifier
            poll_interval: Polling interval in seconds
            **kwargs: Additional timeout arguments
            
        Returns:
            Final ApprovalStatus
        """
        timeout_limit = kwargs.get("timeout_seconds", self.timeout_seconds)
        start_time = time.time()
        
        while True:
            status = self.get_approval_status(request_id=request_id, thread_id=thread_id)
            if status != ApprovalStatus.PENDING:
                return status
                
            if time.time() - start_time >= timeout_limit:
                # Mark as timeout
                req = self._requests.get(request_id, {})
                req["status"] = ApprovalStatus.TIMEOUT.value
                req["updated_at"] = time.time()
                self._requests[request_id] = req
                if self.checkpointer:
                    self.checkpointer.put(
                        thread_id=thread_id,
                        checkpoint=req,
                        checkpoint_ns=f"approval_{request_id}"
                    )
                return ApprovalStatus.TIMEOUT
                
            time.sleep(poll_interval)

    def get_pending_requests(
        self,
        thread_id: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get pending approval requests.
        
        Args:
            thread_id: Optional thread filter
            **kwargs: Additional filter parameters
            
        Returns:
            List of pending request dicts
        """
        pending = []
        for req in self._requests.values():
            if req.get("status") == ApprovalStatus.PENDING.value:
                if thread_id is None or req.get("thread_id") == thread_id:
                    pending.append(dict(req))
        return pending

    def get_audit_log(
        self,
        thread_id: Optional[str] = None,
        limit: int = 100,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Get audit log.
        
        Args:
            thread_id: Optional thread filter
            limit: Maximum entries to return
            **kwargs: Additional query arguments
            
        Returns:
            List of audit log entries
        """
        logs = self.audit_log
        if thread_id:
            logs = [entry for entry in logs if entry.get("thread_id") == thread_id]
        return list(logs[-limit:])

    def execute_with_approval(
        self,
        action: str,
        action_function: Callable[..., Any],
        context: Dict[str, Any],
        thread_id: str,
        auto_approve_actions: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute action with approval gate.
        
        High-level method: requests approval, checks auto-approval or waits,
        then executes or rejects.
        
        Args:
            action: Action name
            action_function: Function to execute if approved
            context: Action context
            thread_id: Thread identifier
            auto_approve_actions: List of actions that don't require manual approval
            **kwargs: Additional parameters
            
        Returns:
            Execution result with "status", "output", "approval_status"
        """
        auto_list = auto_approve_actions or []
        
        if action in auto_list:
            # Auto-approved
            request_id = self.request_approval(
                action=action,
                context=context,
                thread_id=thread_id,
                approver_id="system_auto"
            )
            self.approve(
                request_id=request_id,
                thread_id=thread_id,
                approver_id="system_auto",
                comments="Auto-approved by policy"
            )
            output = action_function()
            return {
                "status": "success",
                "output": output,
                "approval_status": ApprovalStatus.APPROVED,
                "request_id": request_id
            }
            
        # Needs human approval
        request_id = kwargs.get("request_id")
        if not request_id or request_id not in self._requests:
            request_id = self.request_approval(
                action=action,
                context=context,
                thread_id=thread_id,
                **kwargs
            )
        
        # If non-blocking / pending mode
        if kwargs.get("blocking", False):
            poll_interval = kwargs.get("poll_interval", 0.05)
            wait_kwargs = {k: v for k, v in kwargs.items() if k not in ("request_id", "thread_id", "poll_interval", "blocking")}
            final_status = self.wait_for_approval(
                request_id=request_id,
                thread_id=thread_id,
                poll_interval=poll_interval,
                **wait_kwargs
            )
            if final_status == ApprovalStatus.APPROVED:
                output = action_function()
                return {
                    "status": "success",
                    "output": output,
                    "approval_status": ApprovalStatus.APPROVED,
                    "request_id": request_id
                }
            else:
                return {
                    "status": "blocked",
                    "output": None,
                    "approval_status": final_status,
                    "request_id": request_id
                }
        else:
            return {
                "status": "pending_approval",
                "output": None,
                "approval_status": ApprovalStatus.PENDING,
                "request_id": request_id
            }
