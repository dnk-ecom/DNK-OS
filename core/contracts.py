# --- DNK-MRH-HEADER ---
# mrh_id: "core/contracts.py"
# purpose: "Canonical Typed Machine Contracts for Inter-Agent and Inter-Repository IPC."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""Canonical Typed Machine Contracts for DNK OS IPC."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BlastRadiusRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TriageStatus(str, Enum):
    APPROVED = "APPROVED"
    TURN_DOWN_WORK = "TURN_DOWN_WORK"
    AMBIGUOUS = "AMBIGUOUS"


class CompletionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class KernelTaskRequest(BaseModel):
    """Dispatched task request between repositories or agents."""

    task_id: str = Field(..., description="Deterministic task identifier")
    source_repo: str = Field(..., description="Originating repository identifier (e.g. DNK_HUB, DNK-OS)")
    target_repo: str = Field(..., description="Target repository identifier (e.g. DNK-Shopify-AI-Builder)")
    action: str = Field(..., description="Targeted capability or action")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured task arguments")
    negative_scope: List[str] = Field(default_factory=list, description="Explicitly forbidden files or areas")
    target_file_whitelist: List[str] = Field(default_factory=list, description="Permitted files for modification")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )


class KernelTriageReceipt(BaseModel):
    """Triage verification receipt generated before task execution."""

    receipt_id: str = Field(..., description="Unique receipt identifier")
    task_id: str = Field(..., description="Linked task identifier")
    status: TriageStatus = Field(..., description="Triage verdict")
    reasoning: str = Field(..., description="Architectural justification for triage decision")
    blast_radius_risk: BlastRadiusRisk = Field(..., description="Evaluated risk level")
    execution_plan: List[str] = Field(default_factory=list, description="Ordered atomic DAG slices")
    issued_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )


class KernelDecisionReceipt(BaseModel):
    """Persisted architectural decision receipt."""

    decision_id: str = Field(..., description="Unique decision identifier")
    title: str = Field(..., description="Concise decision title")
    status: str = Field("LOCKED", description="Decision state (e.g. LOCKED, PROPOSED)")
    context: str = Field(..., description="Context and problem statement")
    verdict: str = Field(..., description="Final binding architectural verdict")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )


class KernelCompletionReceipt(BaseModel):
    """Deterministic machine completion receipt validating task execution."""

    receipt_id: str = Field(..., description="Unique completion receipt identifier")
    task_id: str = Field(..., description="Linked task identifier")
    status: CompletionStatus = Field(..., description="Execution outcome")
    exit_code: int = Field(0, description="Deterministic process exit code (0 mandatory for SUCCESS)")
    test_output_summary: str = Field(..., description="Machine test execution output summary")
    affected_files: List[str] = Field(default_factory=list, description="List of modified relative paths")
    scones_persisted: bool = Field(False, description="Whether durable lessons were saved to SCONES")
    completed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp",
    )
