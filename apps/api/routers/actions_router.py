# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/actions_router.py"
# purpose: "FastAPI REST Router exposing Dual-Surface Action Catalog and Dispatch Gateway to Astryx UI."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from core.action_bus.dual_surface_registry import (
    ActionDispatchResult,
    DualSurfaceActionRegistry,
)
from core.action_bus.actions import register_all_standard_actions
from core.domain.vibe_core_contracts import ActionSurfaceMode, DualSurfaceActionSpec

logger = logging.getLogger("dnk.api.actions")
router = APIRouter(prefix="/api/v1/actions", tags=["Dual-Surface Actions Gateway"])

# Ensure standard actions are bootstrapped
register_all_standard_actions()


class DispatchActionRequest(BaseModel):
    action_id: str = Field(..., description="Action ID to execute (e.g. 'canvas.move_node')")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input parameters matching action JSON schema")
    actor: str = Field(default="Maksym (Human UI)", description="Identity of caller")
    session_id: str = Field(default="sess_default", description="Active session ID")
    timeout: float = Field(default=30.0, ge=1.0, le=120.0, description="HITL timeout in seconds")


@router.get("", response_model=List[DualSurfaceActionSpec])
async def list_actions(
    surface_mode: Optional[ActionSurfaceMode] = Query(None, description="Filter by surface mode: dual, agent, human"),
) -> List[DualSurfaceActionSpec]:
    """
    Catalog of all registered actions.
    Used by Astryx UI to dynamically render action buttons, form drawers, and toolbars.
    """
    registry = DualSurfaceActionRegistry.get_shared_instance()
    return registry.list_actions(surface_filter=surface_mode)


@router.get("/mcp-tools")
async def list_mcp_tools() -> List[Dict[str, Any]]:
    """
    Returns FastMCP-compatible tool definitions for all agent-accessible actions.
    """
    registry = DualSurfaceActionRegistry.get_shared_instance()
    return registry.export_mcp_tools()


@router.post("/dispatch", response_model=ActionDispatchResult)
async def dispatch_action(req: DispatchActionRequest) -> ActionDispatchResult:
    """
    Dispatches a Dual-Surface action from the UI.
    Executes the shared handler and broadcasts mutation events to living canvas.
    """
    registry = DualSurfaceActionRegistry.get_shared_instance()
    result = await registry.dispatch(
        action_id=req.action_id,
        payload=req.payload,
        actor=req.actor,
        origin="ui",
        session_id=req.session_id,
        timeout=req.timeout,
    )

    if not result.success and not result.requires_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error or "Action execution failed",
        )

    return result
