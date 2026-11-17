# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/swarm_live_ws.py"
# purpose: "FastAPI WebSocket and SSE Live Streaming Router connecting Hermes/Swarm execution to Astryx UI."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Swarm Live Streaming Router for Astryx UI.

Exposes WebSocket and SSE channels for streaming real-time thoughts,
tool calls, artifacts, and interactive Human-in-the-Loop approvals.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.adapters.hermes_ui_bridge import HermesUIBridge
from core.action_bus.models import BusEventType

logger = logging.getLogger("dnk_api.swarm_live_ws")
router = APIRouter(prefix="/api/v1/swarm/live", tags=["Swarm Live Astryx UI Bridge"])


class HitlResolveRequest(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier")
    approved: bool = Field(..., description="Whether action is approved")
    author: str = Field(default="Maksym (Human-in-the-Loop)", description="Reviewer name")
    reason: str = Field(default="", description="Optional feedback or rejection reason")
    modifications: Optional[Dict[str, Any]] = Field(default=None, description="Optional parameter overrides")


@router.websocket("/ws")
async def swarm_live_websocket(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None, description="Filter by specific session ID"),
    agent: Optional[str] = Query(None, description="Filter by specific agent name"),
):
    """
    Primary bi-directional WebSocket connection for Meta Astryx Command HUD.
    Pushes real-time thoughts, tool calls, and receives HITL decisions.
    """
    await websocket.accept()
    bridge = HermesUIBridge.get_shared_instance()
    sub = await bridge.broadcaster.subscribe(task_id=session_id, agent=agent)

    # Initial hydration frame
    initial_history = bridge.get_recent_history()
    await websocket.send_json({
        "type": "HYDRATION_SNAPSHOT",
        "sub_id": sub.sub_id,
        "events_count": len(initial_history),
        "history": initial_history[-30:],  # last 30 events for instant rendering
        "server_time": time.time(),
    })

    async def _send_loop():
        try:
            while True:
                envelope = await sub.queue.get()
                await websocket.send_json({
                    "type": "STREAM_EVENT",
                    "event_type": envelope.event_type.value if hasattr(envelope.event_type, "value") else str(envelope.event_type),
                    "task_id": envelope.task_id,
                    "agent": envelope.agent,
                    "payload": envelope.payload,
                    "timestamp": envelope.timestamp.isoformat() if hasattr(envelope.timestamp, "isoformat") else str(envelope.timestamp),
                })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"WebSocket send loop terminated: {e}")

    send_task = asyncio.create_task(_send_loop())

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "").upper()

            if msg_type == "PING":
                await websocket.send_json({"type": "PONG", "time": time.time()})

            elif msg_type == "HITL_RESOLVE":
                ticket_id = data.get("ticket_id")
                approved = bool(data.get("approved", False))
                author = data.get("author", "Maksym (Human-in-the-Loop)")
                reason = data.get("reason", "")
                mods = data.get("modifications")

                if ticket_id:
                    success = await bridge.resolve_hitl_ticket(
                        ticket_id=ticket_id,
                        approved=approved,
                        author=author,
                        reason=reason,
                        modifications=mods,
                    )
                    await websocket.send_json({
                        "type": "HITL_RESOLVE_ACK",
                        "ticket_id": ticket_id,
                        "success": success,
                    })

    except WebSocketDisconnect:
        logger.info(f"Astryx UI WebSocket disconnected: {sub.sub_id}")
    except Exception as e:
        logger.warning(f"Error in Astryx UI WebSocket: {e}")
    finally:
        send_task.cancel()
        await bridge.broadcaster.unsubscribe(sub.sub_id)


@router.get("/stream")
async def swarm_live_sse_stream(
    session_id: Optional[str] = Query(None),
    agent: Optional[str] = Query(None),
):
    """Server-Sent Events (SSE) fallback stream for lightweight Astryx widgets."""
    bridge = HermesUIBridge.get_shared_instance()
    sub = await bridge.broadcaster.subscribe(task_id=session_id, agent=agent)

    async def event_generator():
        try:
            # Send initial hello
            yield f"event: connected\ndata: {json.dumps({'sub_id': sub.sub_id})}\n\n"
            while True:
                envelope = await sub.queue.get()
                payload = {
                    "event_type": envelope.event_type.value if hasattr(envelope.event_type, "value") else str(envelope.event_type),
                    "task_id": envelope.task_id,
                    "agent": envelope.agent,
                    "payload": envelope.payload,
                }
                yield f"event: stream_event\ndata: {json.dumps(payload)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await bridge.broadcaster.unsubscribe(sub.sub_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/hitl/resolve")
async def resolve_hitl_endpoint(req: HitlResolveRequest):
    """1-Click HITL Resolution endpoint for Astryx action buttons."""
    bridge = HermesUIBridge.get_shared_instance()
    success = await bridge.resolve_hitl_ticket(
        ticket_id=req.ticket_id,
        approved=req.approved,
        author=req.author,
        reason=req.reason,
        modifications=req.modifications,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found or already resolved.")
    return {"status": "resolved", "ticket_id": req.ticket_id, "approved": req.approved}


@router.get("/history")
async def get_history_endpoint():
    """Returns recent stream history for instant Astryx UI hydration."""
    bridge = HermesUIBridge.get_shared_instance()
    return {"history": bridge.get_recent_history()}
