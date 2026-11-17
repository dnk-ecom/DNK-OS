# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/taskboard_canvas_router.py"
# purpose: "FastAPI Router exposing Taskboard-to-Living-Canvas Bi-directional Bridge endpoints."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.adapters.taskboard_canvas_bridge import (
    TaskboardCanvasBridge,
    TaskboardCanvasPayload,
)
from core.adapters.hermes_ui_bridge import HermesUIBridge

router = APIRouter(prefix="/api/v1/taskboard", tags=["Taskboard Canvas Bridge"])


class UpdateTaskStatusRequest(BaseModel):
    task_id: str = Field(..., description="Task ID in SQLite (e.g. task-mwkfe23b-vbmc)")
    new_status: str = Field(..., description="Target status: todo, planned, in_progress, verification, done, failed")
    execution_logs: Optional[str] = Field(None, description="Optional logs or reasoning")


class UpdateTaskStatusResponse(BaseModel):
    success: bool
    task_id: str
    new_status: str
    message: str


def get_bridge() -> TaskboardCanvasBridge:
    # Resolve sqlite path relative to repo root
    db_path = Path(".agents/taskboard/tasks.sqlite")
    if not db_path.exists():
        # Fallback to parent path if running from apps/api
        db_path = Path("../../.agents/taskboard/tasks.sqlite")
    return TaskboardCanvasBridge(db_path=db_path)


@router.get("/canvas", response_model=TaskboardCanvasPayload)
async def get_taskboard_canvas_nodes() -> TaskboardCanvasPayload:
    """
    Fetch all tasks mapped into living XYFlow v12 nodes and sequential edges.
    """
    try:
        bridge = get_bridge()
        return bridge.fetch_canvas_payload()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch taskboard canvas: {e}",
        )


@router.post("/node/status", response_model=UpdateTaskStatusResponse)
async def update_node_status(request: UpdateTaskStatusRequest) -> UpdateTaskStatusResponse:
    """
    Update a task's status in SQLite directly from a canvas node interaction.
    """
    bridge = get_bridge()
    try:
        updated = bridge.update_task_status(
            task_id=request.task_id,
            new_status=request.new_status,
            execution_logs=request.execution_logs,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {request.task_id} not found in taskboard.",
            )
        # Broadcast real-time mutation to living canvas and swarm HUD
        try:
            HermesUIBridge.get_shared_instance().publish_taskboard_mutation(
                task_id=request.task_id,
                new_status=request.new_status,
                agent="canvas_user",
                execution_logs=request.execution_logs,
            )
        except Exception as broadcast_err:
            # Non-fatal broadcast logging
            pass
        return UpdateTaskStatusResponse(
            success=True,
            task_id=request.task_id,
            new_status=request.new_status,
            message=f"Task {request.task_id} status updated to {request.new_status}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {e}",
        )

