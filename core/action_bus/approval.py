# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/approval.py"
# purpose: "Re-export and canonical gateway for Canvas and Action Bus Human-in-the-Loop approvals"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Canonical Action Bus Human-in-the-Loop Approval Gateway.
Re-exports approval types and engine from core.canvas.approval for unified accessibility.
"""

from core.canvas.approval import (
    ApprovalHistoryEntry,
    ApprovalManager,
    ApprovalOperationType,
    ApprovalRequest,
    ApprovalStatus,
    Decision,
    is_critical_operation,
)

__all__ = [
    "ApprovalHistoryEntry",
    "ApprovalManager",
    "ApprovalOperationType",
    "ApprovalRequest",
    "ApprovalStatus",
    "Decision",
    "is_critical_operation",
]
