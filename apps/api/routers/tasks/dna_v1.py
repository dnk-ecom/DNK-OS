# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/tasks/dna_v1.py"
# purpose: "FastAPI REST API router for TaskDNA Anti-Poisoning Lifecycle and Live Canvas HUD synchronization"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (dnk_dev_fullstack & Gerych Prime)"
# --- END DNK-MRH-HEADER ---

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.orchestrator.task_dna_lifecycle import (
    AgentRole,
    AuditReport,
    LifecycleSecurityViolation,
    SecurityGateResult,
    TaskDNALifecycleEngine,
    TaskDNAPhase,
    TaskDNASlice,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/taskdna", tags=["TaskDNA Lifecycle"])

# Global engine instance
_lifecycle_engine = TaskDNALifecycleEngine()


def get_lifecycle_engine() -> TaskDNALifecycleEngine:
    return _lifecycle_engine


class CreateTaskRequest(BaseModel):
    title: str = Field(..., max_length=128)
    content: str = Field(..., max_length=10000)
    task_id: Optional[str] = Field(None, max_length=64)
    creator_role: str = Field(AgentRole.RESEARCHER.value, max_length=64)
    source_url: Optional[str] = None
    target_vault_path: Optional[str] = None
    target_memory_topic: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubmitAuditRequest(BaseModel):
    auditor_role: str = Field(AgentRole.AUDITOR.value, max_length=64)


class AuditVerdictRequest(BaseModel):
    auditor_role: str = Field(AgentRole.AUDITOR.value, max_length=64)
    passed: bool
    score: float = Field(1.0, ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)


class FounderDecisionRequest(BaseModel):
    founder_role: str = Field(AgentRole.FOUNDER.value, max_length=64)
    approved: bool
    feedback: str = Field("LGTM", max_length=500)


class LibrarianIngestRequest(BaseModel):
    librarian_role: str = Field(AgentRole.LIBRARIAN.value, max_length=64)
    ingested_vault_path: Optional[str] = None
    ingested_memory_key: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    phase: str
    assigned_agent: str
    content: str
    dependencies: List[str]
    has_audit_report: bool
    audit_score: Optional[float] = None
    founder_decision: Optional[str] = None
    target_vault_path: Optional[str] = None
    created_at: str
    updated_at: str


class SyncHudResponse(BaseModel):
    status: str
    canvas_path: str
    total_tasks: int
    nodes_count: int
    edges_count: int


def _to_response(task: TaskDNASlice) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        phase=task.phase.value,
        assigned_agent=task.assigned_agent,
        content=task.content,
        dependencies=task.dependencies,
        has_audit_report=task.audit_report is not None,
        audit_score=task.audit_report.score if task.audit_report else None,
        founder_decision=task.founder_decision,
        target_vault_path=task.target_vault_path,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all TaskDNA slices and their lifecycle phases",
)
def list_tasks(phase: Optional[str] = None) -> List[TaskResponse]:
    engine = get_lifecycle_engine()
    phase_enum = None
    if phase:
        try:
            phase_enum = TaskDNAPhase(phase)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phase: '{phase}'. Allowed: {[p.value for p in TaskDNAPhase]}",
            )
    tasks = engine.list_tasks(phase=phase_enum)
    return [_to_response(t) for t in tasks]


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single TaskDNA slice by id",
)
def get_task(task_id: str) -> TaskResponse:
    engine = get_lifecycle_engine()
    task = engine.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )
    return _to_response(task)


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new slice in RESEARCH_RAW phase",
)
def register_task(payload: CreateTaskRequest) -> TaskResponse:
    engine = get_lifecycle_engine()
    try:
        task = engine.register_task(
            title=payload.title,
            content=payload.content,
            task_id=payload.task_id,
            source_url=payload.source_url,
            target_vault_path=payload.target_vault_path,
            target_memory_topic=payload.target_memory_topic,
            dependencies=payload.dependencies,
            creator_role=payload.creator_role,
            metadata=payload.metadata,
        )
        return _to_response(task)
    except LifecycleSecurityViolation as sec_exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(sec_exc),
        ) from sec_exc
    except Exception as exc:
        logger.exception("Error registering task: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post(
    "/tasks/{task_id}/submit-audit",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Advance slice from RESEARCH_RAW to AUDIT_GATE",
)
def submit_for_audit(task_id: str, payload: SubmitAuditRequest) -> TaskResponse:
    engine = get_lifecycle_engine()
    try:
        task = engine.submit_for_audit(task_id=task_id, actor_role=payload.auditor_role)
        return _to_response(task)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )
    except LifecycleSecurityViolation as sec_exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(sec_exc),
        ) from sec_exc


@router.post(
    "/tasks/{task_id}/audit-verdict",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit audit result (Auditor role: PASSED or FAILED)",
)
def submit_audit_verdict(task_id: str, payload: AuditVerdictRequest) -> TaskResponse:
    engine = get_lifecycle_engine()
    status_gate = SecurityGateResult.PASSED if payload.passed else SecurityGateResult.FAILED
    try:
        task = engine.record_audit_result(
            task_id=task_id,
            auditor_role=payload.auditor_role,
            status=status_gate,
            score=payload.score,
            issues=payload.issues,
        )
        return _to_response(task)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )
    except LifecycleSecurityViolation as sec_exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(sec_exc),
        ) from sec_exc


@router.post(
    "/tasks/{task_id}/founder-decision",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Founder reviews task in FOUNDER_APPROVAL phase (HITL)",
)
def founder_decision(task_id: str, payload: FounderDecisionRequest) -> TaskResponse:
    engine = get_lifecycle_engine()
    try:
        task = engine.founder_decision(
            task_id=task_id,
            approved=payload.approved,
            feedback=payload.feedback,
            actor_role=payload.founder_role,
        )
        return _to_response(task)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )
    except LifecycleSecurityViolation as sec_exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(sec_exc),
        ) from sec_exc


@router.post(
    "/tasks/{task_id}/complete-ingest",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Librarian ingests approved slice into Obsidian / SCONES and completes task",
)
def complete_ingest(task_id: str, payload: LibrarianIngestRequest) -> TaskResponse:
    engine = get_lifecycle_engine()
    try:
        task = engine.complete_ingest(
            task_id=task_id,
            ingested_vault_path=payload.ingested_vault_path,
            ingested_memory_key=payload.ingested_memory_key,
            actor_role=payload.librarian_role,
        )
        return _to_response(task)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )
    except LifecycleSecurityViolation as sec_exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(sec_exc),
        ) from sec_exc


@router.post(
    "/sync-hud",
    response_model=SyncHudResponse,
    status_code=status.HTTP_200_OK,
    summary="Synchronize TaskDNA tasks to Obsidian JSON Canvas Swarm Live HUD",
)
def sync_hud(target_canvas_path: Optional[str] = None) -> SyncHudResponse:
    engine = get_lifecycle_engine()
    try:
        path = target_canvas_path or "docs/notes/Canvas/Swarm_Live_HUD.canvas"
        canvas_doc = engine.sync_to_canvas(canvas_rel_path=path)
        all_tasks = engine.list_tasks()
        return SyncHudResponse(
            status="synchronized",
            canvas_path=path,
            total_tasks=len(all_tasks),
            nodes_count=len(canvas_doc.nodes),
            edges_count=len(canvas_doc.edges),
        )
    except Exception as exc:
        logger.exception("Error syncing Canvas HUD: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync HUD failed: {str(exc)}",
        ) from exc
