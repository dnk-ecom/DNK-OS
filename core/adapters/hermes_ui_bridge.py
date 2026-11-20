# --- DNK-MRH-HEADER ---
# mrh_id: "core/adapters/hermes_ui_bridge.py"
# purpose: "Bidirectional bridge connecting Hermes terminal agent/orchestrator execution events to ActionBus & Astryx UI."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Hermes UI Bridge (Terminal Agent ➔ Astryx UI Streamer).

Translates autonomous Hermes / Gerych execution lifecycle events
(thoughts, tool calls, plan updates, status shifts) into ActionBus
events broadcasted via WebSockets/SSE to Meta Astryx frontend components.
Provides non-blocking asynchronous Human-in-the-Loop (HITL) ticket resolution.
"""

import asyncio
from datetime import datetime, timezone
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid

from core.action_bus.broadcaster import EventBroadcaster, StreamEnvelope
from core.action_bus.models import BusEvent, BusEventType

logger = logging.getLogger("dnk_core.hermes_ui_bridge")


class HermesUIBridge:
    """Coordinates real-time bi-directional streaming between Hermes and Astryx UI."""

    _instance: Optional["HermesUIBridge"] = None

    def __init__(self, broadcaster: Optional[EventBroadcaster] = None):
        self.broadcaster = broadcaster or EventBroadcaster()
        self._active_hitl_tickets: Dict[str, asyncio.Event] = {}
        self._ticket_resolutions: Dict[str, Dict[str, Any]] = {}
        self._session_agents: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def get_shared_instance(cls) -> "HermesUIBridge":
        """Get or initialize singleton instance for system-wide streaming."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def publish_agent_thought(
        self,
        session_id: str,
        agent: str,
        thought: str,
        step: int = 0,
        thought_type: str = "reasoning",
    ) -> StreamEnvelope:
        """Broadcasts agent internal reasoning / thought chunk to Astryx HUD."""
        event = BusEvent(
            event_id=f"evt_th_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.TASK_ROUTED,
            task_id=session_id,
            payload={
                "kind": "thought_stream",
                "session_id": session_id,
                "agent": agent,
                "step": step,
                "thought_type": thought_type,
                "content": thought,
                "timestamp_epoch": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    def publish_tool_start(
        self,
        session_id: str,
        agent: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_call_id: Optional[str] = None,
    ) -> StreamEnvelope:
        """Broadcasts tool execution commencement for live Astryx Tool Cards."""
        call_id = tool_call_id or f"call_{uuid.uuid4().hex[:8]}"
        event = BusEvent(
            event_id=f"evt_ts_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.TASK_STARTED,
            task_id=session_id,
            payload={
                "kind": "tool_start",
                "session_id": session_id,
                "agent": agent,
                "tool_call_id": call_id,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "status": "executing",
                "started_at": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    def publish_tool_complete(
        self,
        session_id: str,
        agent: str,
        tool_name: str,
        result: Any,
        tool_call_id: Optional[str] = None,
        exit_code: int = 0,
        duration_ms: float = 0.0,
    ) -> StreamEnvelope:
        """Broadcasts tool result / output for Astryx Tool Cards and Diff Viewers."""
        call_id = tool_call_id or f"call_{uuid.uuid4().hex[:8]}"
        is_success = exit_code == 0
        event = BusEvent(
            event_id=f"evt_tc_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.TASK_COMPLETED if is_success else BusEventType.TASK_FAILED,
            task_id=session_id,
            payload={
                "kind": "tool_complete",
                "session_id": session_id,
                "agent": agent,
                "tool_call_id": call_id,
                "tool_name": tool_name,
                "result": result,
                "exit_code": exit_code,
                "success": is_success,
                "duration_ms": duration_ms,
                "completed_at": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    def publish_plan_update(
        self,
        session_id: str,
        agent: str,
        plan_entries: List[Dict[str, Any]],
        title: Optional[str] = None,
    ) -> StreamEnvelope:
        """Broadcasts agent plan / todo DAG update to living Spatial Canvas."""
        event = BusEvent(
            event_id=f"evt_plan_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.CANVAS_BATCH_MUTATION,
            task_id=session_id,
            payload={
                "kind": "plan_update",
                "session_id": session_id,
                "agent": agent,
                "title": title or f"Plan update for {agent}",
                "entries": plan_entries,
                "entry_count": len(plan_entries),
                "updated_at": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    def publish_agent_status(
        self,
        session_id: str,
        agent: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> StreamEnvelope:
        """Broadcasts agent overall status (idle, thinking, executing, waiting_hitl, completed, failed)."""
        event = BusEvent(
            event_id=f"evt_st_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.TASK_QUEUED if status == "idle" else BusEventType.TASK_STARTED,
            task_id=session_id,
            payload={
                "kind": "agent_status",
                "session_id": session_id,
                "agent": agent,
                "status": status,
                "message": message,
                "details": details or {},
                "timestamp_epoch": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    def publish_taskboard_mutation(
        self,
        task_id: str,
        new_status: str,
        agent: str = "taskboard",
        execution_logs: Optional[str] = None,
    ) -> StreamEnvelope:
        """Broadcasts taskboard status shift to trigger real-time living canvas updates."""
        event = BusEvent(
            event_id=f"evt_tb_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.CANVAS_BATCH_MUTATION,
            task_id=task_id,
            payload={
                "kind": "taskboard_mutation",
                "task_id": task_id,
                "new_status": new_status,
                "agent": agent,
                "execution_logs": execution_logs,
                "timestamp_epoch": time.time(),
            },
        )
        return self.broadcaster.broadcast(event, agent=agent)

    async def request_hitl_approval_async(
        self,
        session_id: str,
        agent: str,
        action_type: str,
        details: Dict[str, Any],
        timeout: float = 300.0,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Asynchronously requests Human-in-the-Loop approval from the Astryx UI.
        Non-blocking: sets up an asyncio.Event and waits without locking the loop.
        """
        ticket_id = f"hitl_{uuid.uuid4().hex[:10]}"
        event_obj = asyncio.Event()

        async with self._lock:
            self._active_hitl_tickets[ticket_id] = event_obj

        # Broadcast approval request to Astryx UI
        bus_event = BusEvent(
            event_id=f"evt_apr_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.APPROVAL_REQUESTED,
            task_id=session_id,
            payload={
                "kind": "hitl_approval_request",
                "ticket_id": ticket_id,
                "session_id": session_id,
                "agent": agent,
                "action_type": action_type,
                "details": details,
                "options": ["approve", "reject", "modify"],
                "timeout_seconds": timeout,
                "created_at": time.time(),
            },
        )
        self.broadcaster.broadcast(bus_event, agent=agent)
        logger.info(f"HITL approval ticket created: {ticket_id} for agent: {agent}")

        try:
            # Asynchronous non-blocking wait
            await asyncio.wait_for(event_obj.wait(), timeout=timeout)
            resolution = self._ticket_resolutions.pop(ticket_id, {})
            approved = resolution.get("approved", False)
            return approved, resolution
        except asyncio.TimeoutError:
            logger.warning(f"HITL approval ticket timed out: {ticket_id}")
            return False, {"approved": False, "reason": "timeout", "ticket_id": ticket_id}
        finally:
            async with self._lock:
                self._active_hitl_tickets.pop(ticket_id, None)

    async def resolve_hitl_ticket(
        self,
        ticket_id: str,
        approved: bool,
        author: str = "Maksym (Human-in-the-Loop)",
        reason: str = "",
        modifications: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Resolves a pending HITL ticket from an Astryx UI button click or WebSocket message."""
        async with self._lock:
            event_obj = self._active_hitl_tickets.get(ticket_id)
            if not event_obj:
                logger.warning(f"Attempted to resolve nonexistent or expired ticket: {ticket_id}")
                return False

            resolution = {
                "ticket_id": ticket_id,
                "approved": approved,
                "author": author,
                "reason": reason,
                "modifications": modifications or {},
                "resolved_at": time.time(),
            }
            self._ticket_resolutions[ticket_id] = resolution
            event_obj.set()

        # Broadcast resolution to UI subscribers
        bus_event = BusEvent(
            event_id=f"evt_res_{uuid.uuid4().hex[:8]}",
            event_type=BusEventType.APPROVAL_RESOLVED,
            task_id=ticket_id,
            payload={
                "kind": "hitl_approval_resolved",
                "ticket_id": ticket_id,
                "approved": approved,
                "author": author,
                "reason": reason,
                "modifications": modifications or {},
                "resolved_at": time.time(),
            },
        )
        self.broadcaster.broadcast(bus_event)
        logger.info(f"HITL ticket {ticket_id} resolved: approved={approved} by {author}")
        return True

    def create_acp_bridge_callbacks(
        self,
        session_id: str,
        agent_name: str,
    ) -> Dict[str, Callable[..., Any]]:
        """
        Creates factory callbacks matching Hermes / ACP execution hooks.
        Can be passed directly into AIAgent or Hermes task loops.
        """
        bridge = self

        def on_thought(thought_text: str, step_idx: int = 0):
            bridge.publish_agent_thought(session_id, agent_name, thought_text, step=step_idx)

        def on_tool_start(tool_name: str, tool_args: Dict[str, Any], tool_id: Optional[str] = None):
            bridge.publish_tool_start(session_id, agent_name, tool_name, tool_args, tool_call_id=tool_id)

        def on_tool_complete(tool_name: str, output: Any, tool_id: Optional[str] = None, exit_code: int = 0):
            bridge.publish_tool_complete(session_id, agent_name, tool_name, output, tool_call_id=tool_id, exit_code=exit_code)

        def on_plan_update(plan_items: List[Dict[str, Any]]):
            bridge.publish_plan_update(session_id, agent_name, plan_items)

        def on_status_change(new_status: str, msg: str = ""):
            bridge.publish_agent_status(session_id, agent_name, new_status, message=msg)

        return {
            "on_thought": on_thought,
            "on_tool_start": on_tool_start,
            "on_tool_complete": on_tool_complete,
            "on_plan_update": on_plan_update,
            "on_status_change": on_status_change,
        }

    def get_recent_history(self) -> List[Dict[str, Any]]:
        """Returns snapshot of recent stream envelopes for initial Astryx UI hydration."""
        return [env.model_dump() for env in self.broadcaster._recent_events]
