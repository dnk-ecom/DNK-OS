# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/client_cockpit_router.py"
# purpose: "FastAPI REST Router for Ring 2 (Client Cockpit) and Ring 3 (In-Context Sensor)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.client_cockpit.engine import ClientCockpitEngine

router = APIRouter(prefix="/api/v1/cockpit", tags=["Client Cockpit & In-Context Sensor"])


class CreateTicketRequest(BaseModel):
    title: str = Field(..., description="Short summary of the ticket/revision")
    comment: str = Field(..., description="Detailed feedback or question")
    category: Optional[str] = Field("auto", description="auto | question | in_scope_revision | out_of_scope_upsell")
    selector: Optional[str] = Field(None, description="CSS selector of clicked DOM element")
    section_id: Optional[str] = Field(None, description="Shopify section ID (e.g. main-product)")
    block_id: Optional[str] = Field(None, description="Shopify block ID (e.g. buy_buttons)")
    screenshot_url: Optional[str] = Field(None, description="Captured screenshot URL")
    bounding_box: Optional[Dict[str, Any]] = Field(None, description="Coordinates of selected area {x, y, w, h}")
    page_url: Optional[str] = Field(None, description="URL of preview page where review occurred")
    client_name: Optional[str] = Field(None, description="Name or role of reviewing client")


class AdvanceStageRequest(BaseModel):
    stage_num: int = Field(..., ge=1, le=6)
    status: str = Field(..., description="completed | in_progress | pending")


class AddArtifactRequest(BaseModel):
    name: str = Field(...)
    artifact_type: str = Field(...)
    url: str = Field(...)


class ResolveTicketRequest(BaseModel):
    resolution_note: str = Field("", description="Agent developer explanation or git commit sha")
    status: str = Field("resolved", description="resolved | applied | in_review | dismissed")


@router.get("/{deal_id}")
async def get_cockpit_state(deal_id: str) -> Dict[str, Any]:
    """Returns the full SSOT state for the Client Cockpit."""
    engine = ClientCockpitEngine()
    state = engine.get_cockpit_state(deal_id)
    if not state:
        # Bootstrap default state if not found
        state = engine.init_deal(deal_id=deal_id)
    return state


@router.post("/{deal_id}/tickets")
async def submit_ticket(deal_id: str, req: CreateTicketRequest) -> Dict[str, Any]:
    """Submits a client visual area revision, triggering the Client Success Agent."""
    from core.client_success.agent import ClientSuccessAgent, VisualReviewPayload, BoundingBox

    engine = ClientCockpitEngine()
    cs_agent = ClientSuccessAgent(engine=engine)
    bbox_obj = BoundingBox(**req.bounding_box) if req.bounding_box else None

    payload = VisualReviewPayload(
        deal_id=deal_id,
        title=req.title,
        comment=req.comment,
        category=req.category or "auto",
        selector=req.selector,
        section_id=req.section_id,
        block_id=req.block_id,
        bounding_box=bbox_obj,
        page_url=req.page_url,
        screenshot_url=req.screenshot_url,
        client_name=req.client_name,
    )
    res = cs_agent.process_visual_review(payload)
    return {
        "status": "success",
        "ticket_id": res.ticket_id,
        "category": res.category,
        "client_acknowledgment": res.client_acknowledgment,
        "quota_remaining": res.quota_remaining,
        "builder_task": res.builder_task,
    }


@router.get("/{deal_id}/tickets")
async def list_tickets(deal_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    """Lists client tickets filtered by status."""
    engine = ClientCockpitEngine()
    tickets = engine.get_tickets(deal_id=deal_id, status=status)
    return {"status": "success", "deal_id": deal_id, "tickets": tickets, "count": len(tickets)}


@router.post("/{deal_id}/tickets/{ticket_id}/resolve")
async def resolve_ticket(deal_id: str, ticket_id: str, req: ResolveTicketRequest) -> Dict[str, Any]:
    """Resolves an in-context ticket with agent notes."""
    engine = ClientCockpitEngine()
    ticket = engine.resolve_ticket(
        deal_id=deal_id,
        ticket_id=ticket_id,
        resolution_note=req.resolution_note,
        status=req.status,
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "success", "ticket": ticket}


@router.post("/{deal_id}/advance-stage")
async def advance_stage(deal_id: str, req: AdvanceStageRequest) -> Dict[str, Any]:
    """Advances one of the 6 canonical stages."""
    engine = ClientCockpitEngine()
    engine.update_stage_status(deal_id, req.stage_num, req.status)
    return {"status": "success", "stage_num": req.stage_num, "new_status": req.status}


@router.post("/{deal_id}/artifacts")
async def add_artifact(deal_id: str, req: AddArtifactRequest) -> Dict[str, Any]:
    """Adds a deliverable artifact link to the vault."""
    engine = ClientCockpitEngine()
    engine.add_artifact(deal_id, req.name, req.artifact_type, req.url)
    return {"status": "success", "artifact": req.model_dump()}
