# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/agent_mesh_models.py"
# purpose: "Pydantic domain contracts and typed schemas for Agent-Native Enterprise Mesh, Approval Chains, and Ingress Security"
# author: "DNK-e.com Maksym & Denchik"
# license: "DNK-INTERNAL"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-02"
# --- END DNK-MRH-HEADER ---

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ApprovalRole(str, Enum):
    AUTHOR = "author"
    CREATOR = "creator"
    SALES = "sales"
    LEGAL = "legal"
    FINANCE = "finance"
    SECURITY = "security"
    EXECUTIVE = "executive"


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ApprovalStep(BaseModel):
    step_index: int = Field(..., ge=0, description="Zero-indexed sequence position in chain")
    role: ApprovalRole = Field(..., description="Role required for this step")
    approver_id: Optional[str] = Field(default=None, description="Identifier of the specific agent or human")
    decision: ApprovalDecision = Field(default=ApprovalDecision.PENDING, description="Current decision state")
    comment: Optional[str] = Field(default=None, description="Audit rationale or rejection notes")
    timestamp: Optional[str] = Field(default=None, description="ISO 8601 UTC timestamp of decision")
    signature_sha256: Optional[str] = Field(default=None, description="Cryptographic receipt hash of step")


class ApprovalChainSpec(BaseModel):
    chain_id: str = Field(..., description="Unique immutable UUID of the approval chain")
    document_id: str = Field(..., description="ID of the document or artifact being approved")
    document_payload_hash: str = Field(..., description="SHA-256 hash of canonical document content")
    title: str = Field(..., description="Title or human-readable summary of document")
    steps: List[ApprovalStep] = Field(..., min_length=1, description="Strict sequence of required approvals")
    strict_sequential: bool = Field(default=True, description="Enforce strict ordered progression")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: ApprovalDecision = Field(default=ApprovalDecision.PENDING, description="Aggregated chain status")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("steps")
    @classmethod
    def validate_step_order(cls, steps: List[ApprovalStep]) -> List[ApprovalStep]:
        for idx, step in enumerate(steps):
            if step.step_index != idx:
                raise ValueError(f"Step index mismatch: expected {idx}, got {step.step_index}")
        return steps


class SanitizationResult(BaseModel):
    is_safe: bool = Field(..., description="True if no high-risk injection patterns detected")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Normalized threat confidence (0.0=clean, 1.0=malicious)")
    detected_vectors: List[str] = Field(default_factory=list, description="List of triggered injection heuristics")
    clean_text: str = Field(..., description="Sanitized payload with stripped dangerous elements")
