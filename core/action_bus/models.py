# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/models.py"
# purpose: "Pydantic v2 data models for Agent Action Bus, tasks, events, and responses."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ActionTaskStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class BusEventType(str, Enum):
    TASK_SUBMITTED = "TASK_SUBMITTED"
    TASK_QUEUED = "TASK_QUEUED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    TASK_REJECTED = "TASK_REJECTED"
    TASK_ROUTED = "TASK_ROUTED"
    TASK_DELEGATED = "TASK_DELEGATED"
    SWARM_PARALLEL_STARTED = "SWARM_PARALLEL_STARTED"
    SWARM_PARALLEL_COMPLETED = "SWARM_PARALLEL_COMPLETED"
    SWARM_PIPELINE_STARTED = "SWARM_PIPELINE_STARTED"
    SWARM_PIPELINE_COMPLETED = "SWARM_PIPELINE_COMPLETED"
    ARTIFACT_CREATED = "ARTIFACT_CREATED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_RESOLVED = "APPROVAL_RESOLVED"
    CANVAS_NODE_MOVED = "CANVAS_NODE_MOVED"
    CANVAS_BATCH_MUTATION = "CANVAS_BATCH_MUTATION"
    SANDBOX_EXECUTION_COMPLETED = "SANDBOX_EXECUTION_COMPLETED"
    SIMULATION_ABORTED = "SIMULATION_ABORTED"



class ActionTask(BaseModel):
    task_id: str = Field(..., description="Unique deterministic task identifier")
    action_type: str = Field(default="plugin_execution", description="Action type (e.g. 'plugin_execution', 'agent_step', 'swarm_task')")
    plugin_card_path: Optional[str] = Field(default=None, description="Relative path to plugin card if applicable")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input execution parameters")
    tenant_id: str = Field(default="default_tenant", description="Tenant isolation boundary")
    workspace_id: str = Field(default="ws-alpha-001", description="Workspace context")
    target_agent: Optional[str] = Field(default=None, description="Assigned swarm worker agent")
    delegated_by: Optional[str] = Field(default=None, description="Origin agent if delegated (A2A)")
    routing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata produced by task router")
    created_at: str = Field(default_factory=_utc_now_iso, description="ISO UTC timestamp of task creation")


class BusEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: BusEventType = Field(..., description="Type of bus event")
    task_id: str = Field(..., description="Associated task identifier")
    timestamp: str = Field(default_factory=_utc_now_iso, description="ISO UTC timestamp of event")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload or metadata")


class ActionExecutionResponse(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    status: ActionTaskStatus = Field(..., description="Final or current execution status")
    exit_code: int = Field(default=0, description="Process or runner exit code")
    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured standard error")
    output: Optional[Any] = Field(default=None, description="Structured execution result dictionary")
    error_message: Optional[str] = Field(default=None, description="Error explanation if status is FAILED or REJECTED")
    execution_time_ms: float = Field(default=0.0, description="Total execution duration in milliseconds")
    completed_at: str = Field(default_factory=_utc_now_iso, description="ISO UTC timestamp of completion")


class SwarmRouteResult(BaseModel):
    matched_agent: str = Field(..., description="Resolved target agent")
    confidence: float = Field(default=1.0, description="Confidence score between 0.0 and 1.0")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords matching the agent domain")
    reasoning: str = Field(default="", description="Explanation of routing decision")


class SwarmBatchRequest(BaseModel):
    tasks: List[ActionTask] = Field(..., description="List of subtasks for parallel execution")
    fail_fast: bool = Field(default=False, description="Abort remaining tasks on first failure")
    timeout_seconds: float = Field(default=30.0, description="Timeout for batch execution")


class SwarmBatchResponse(BaseModel):
    batch_id: str = Field(..., description="Batch execution identifier")
    total_tasks: int = Field(..., description="Number of tasks in batch")
    succeeded_tasks: int = Field(..., description="Number of successfully completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    results: List[ActionExecutionResponse] = Field(default_factory=list, description="List of individual execution responses")
    total_duration_ms: float = Field(default=0.0, description="Total wall-clock duration in ms")


class SwarmPipelineRequest(BaseModel):
    stages: List[ActionTask] = Field(..., description="Ordered list of task stages for pipeline execution")
    stop_on_failure: bool = Field(default=True, description="Halt pipeline on first failing stage")


class SwarmPipelineResponse(BaseModel):
    pipeline_id: str = Field(..., description="Pipeline execution identifier")
    total_stages: int = Field(..., description="Total number of stages in pipeline")
    completed_stages: int = Field(..., description="Number of completed stages")
    status: ActionTaskStatus = Field(..., description="Overall pipeline status")
    results: List[ActionExecutionResponse] = Field(default_factory=list, description="Ordered results per stage")
    final_output: Optional[Any] = Field(default=None, description="Output of the final pipeline stage")
    total_duration_ms: float = Field(default=0.0, description="Total pipeline execution duration in ms")


class ArtifactMetadata(BaseModel):
    artifact_id: str = Field(..., description="Unique artifact identifier")
    uri: str = Field(..., description="Deterministic URI, e.g. artifact://mvr/<cat>/<filename>")
    filename: str = Field(..., description="Name of the stored file")
    content_type: str = Field(default="text/plain", description="MIME content type")
    size_bytes: int = Field(default=0, description="Size of artifact in bytes")
    created_by_agent: Optional[str] = Field(default=None, description="Agent who generated this artifact")
    task_id: Optional[str] = Field(default=None, description="Associated task ID")
    checksum_sha256: str = Field(default="", description="SHA-256 content checksum")
    created_at: str = Field(default_factory=_utc_now_iso, description="ISO UTC timestamp")
    storage_path: str = Field(default="", description="Relative path on disk (e.g. artifacts/mvr/...)")


class ArtifactReference(BaseModel):
    artifact_id: str = Field(..., description="Unique artifact identifier")
    uri: str = Field(..., description="URI for referencing the artifact")
    summary: Optional[str] = Field(default=None, description="Brief summary or description")
    size_bytes: int = Field(default=0, description="Size of artifact in bytes")


class StreamEnvelope(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: BusEventType = Field(..., description="Type of bus event")
    task_id: str = Field(..., description="Associated task identifier")
    timestamp: str = Field(default_factory=_utc_now_iso, description="ISO UTC timestamp of event")
    agent: Optional[str] = Field(default=None, description="Target or executing agent")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload or metadata")
    artifact_uri: Optional[str] = Field(default=None, description="URI of attached artifact if any")


class CanvasNodeMoveRequest(BaseModel):
    canvas_id: str = Field(..., description="Target canvas ID")
    node_id: str = Field(..., description="Node ID being moved")
    x: float = Field(..., description="Target x coordinate")
    y: float = Field(..., description="Target y coordinate")
    delta_x: Optional[float] = Field(default=None, description="Coordinate delta X")
    delta_y: Optional[float] = Field(default=None, description="Coordinate delta Y")
    task_id: Optional[str] = Field(default=None, description="Associated task ID")


class CanvasBatchMutationRequest(BaseModel):
    canvas_id: str = Field(..., description="Target canvas ID")
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="List of node definitions or updates")
    edges: List[Dict[str, Any]] = Field(default_factory=list, description="List of edge definitions or updates")
    task_id: Optional[str] = Field(default=None, description="Associated task ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional mutation metadata")


class HitlApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="Decision: 'approved' or 'rejected'")
    approver_id: str = Field(default="maksym", description="Approver identifier")
    reason: Optional[str] = Field(default=None, description="Reason or comment for the decision")


