# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/dual_surface_registry.py"
# purpose: "Unified Dual-Surface Action Registry & Dispatcher bridging FastMCP LLM tools and Astryx UI mutations."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""
Unified Dual-Surface Action Registry & Dispatcher (BuilderIO/agent-native parity).

Provides a single source of mutation truth:
1. Actions are declared ONCE via DualSurfaceActionSpec.
2. Handlers are callable by humans (via REST/SSE/WS Astryx UI) and agents (FastMCP tools).
3. Automatic Human-in-the-Loop (HITL) interception for dangerous actions when triggered by agents.
4. Broadcasts resulting mutations to the Living Canvas and connected clients via EventBroadcaster.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from core.domain.vibe_core_contracts import ActionSurfaceMode, DualSurfaceActionSpec
from core.adapters.hermes_ui_bridge import HermesUIBridge
from core.action_bus.models import BusEvent, BusEventType

logger = logging.getLogger("dnk.action_bus.dual_surface")


class ActionDispatchResult(BaseModel):
    """Result of dispatching a Dual-Surface action."""
    action_id: str = Field(..., description="Action ID executed")
    success: bool = Field(..., description="Whether action finished successfully")
    result: Any = Field(default=None, description="Returned payload or data from handler")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    requires_approval: bool = Field(default=False, description="Whether action paused waiting for human approval")
    ticket_id: Optional[str] = Field(default=None, description="HITL ticket ID if approval was requested")
    actor: str = Field(..., description="Name or ID of actor invoking action")
    origin: str = Field(..., description="'ui' or 'agent'")
    timestamp_epoch: float = Field(default_factory=time.time)


class DualSurfaceActionRegistry:
    """
    Central registry and execution controller for Dual-Surface actions.
    Ensures identical business logic, authorization, and event logs for both UI and AI.
    """

    _instance: Optional["DualSurfaceActionRegistry"] = None

    def __init__(self, ui_bridge: Optional[HermesUIBridge] = None):
        self.ui_bridge = ui_bridge or HermesUIBridge.get_shared_instance()
        self._actions: Dict[str, DualSurfaceActionSpec] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self._lock = asyncio.Lock()

    @classmethod
    def get_shared_instance(cls) -> "DualSurfaceActionRegistry":
        """Get or initialize singleton instance for system-wide action dispatch."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_shared_instance(cls) -> None:
        """Reset singleton for isolated test suites."""
        cls._instance = None

    def register_action(
        self,
        spec: DualSurfaceActionSpec,
        handler: Callable[..., Any],
    ) -> None:
        """Register a dual-surface action specification and its executable handler."""
        if not callable(handler):
            raise ValueError(f"Handler for action '{spec.action_id}' must be callable.")
        
        self._actions[spec.action_id] = spec
        self._handlers[spec.action_id] = handler
        logger.info(
            "Registered Dual-Surface Action: %s (mode=%s, mcp_tool=%s)",
            spec.action_id,
            spec.surface_mode.value,
            spec.mcp_tool_name,
        )

    def action(self, spec: DualSurfaceActionSpec) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to declare and register an action handler in one statement."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register_action(spec, func)
            return func
        return decorator

    def get_action_spec(self, action_id: str) -> Optional[DualSurfaceActionSpec]:
        """Fetch specification by action ID."""
        return self._actions.get(action_id)

    def list_actions(
        self,
        surface_filter: Optional[ActionSurfaceMode] = None,
    ) -> List[DualSurfaceActionSpec]:
        """List registered action specifications, optionally filtered by surface mode."""
        specs = list(self._actions.values())
        if surface_filter is None:
            return specs
        return [s for s in specs if s.surface_mode == surface_filter]

    def export_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Export all actions accessible to agents (DUAL or AGENT_ONLY)
        as FastMCP-compatible tool schema definitions.
        """
        tools = []
        for spec in self._actions.values():
            if spec.surface_mode in (ActionSurfaceMode.DUAL, ActionSurfaceMode.AGENT_ONLY):
                tool_def = {
                    "name": spec.mcp_tool_name,
                    "description": f"{spec.description_en} [Action ID: {spec.action_id}]",
                    "inputSchema": spec.input_json_schema or {
                        "type": "object",
                        "properties": {},
                    },
                    "metadata": {
                        "action_id": spec.action_id,
                        "label_uk": spec.label_uk,
                        "surface_mode": spec.surface_mode.value,
                        "requires_human_confirmation": spec.requires_human_confirmation,
                        "ui_widget": spec.ui_widget,
                    },
                }
                tools.append(tool_def)
        return tools

    async def dispatch(
        self,
        action_id: str,
        payload: Dict[str, Any],
        actor: str = "human",
        origin: str = "ui",
        session_id: str = "sess_default",
        timeout: float = 30.0,
    ) -> ActionDispatchResult:
        """
        Dispatch an action invocation from either UI or an Agent.

        Enforces:
        1. Action existence and surface permission check.
        2. Automatic HITL approval pause if action requires human confirmation and origin is 'agent'.
        3. Handler execution (async or sync).
        4. Broadcasting mutation event to Astryx UI / Living Canvas.
        """
        spec = self.get_action_spec(action_id)
        if not spec:
            return ActionDispatchResult(
                action_id=action_id,
                success=False,
                error=f"Action '{action_id}' is not registered in DualSurfaceActionRegistry.",
                actor=actor,
                origin=origin,
            )

        handler = self._handlers.get(action_id)
        if not handler:
            return ActionDispatchResult(
                action_id=action_id,
                success=False,
                error=f"No executable handler registered for action '{action_id}'.",
                actor=actor,
                origin=origin,
            )

        # Enforce surface mode permissions
        if origin == "agent" and spec.surface_mode == ActionSurfaceMode.HUMAN_ONLY:
            return ActionDispatchResult(
                action_id=action_id,
                success=False,
                error=f"Action '{action_id}' is restricted to HUMAN_ONLY surface mode.",
                actor=actor,
                origin=origin,
            )
        if origin == "ui" and spec.surface_mode == ActionSurfaceMode.AGENT_ONLY:
            return ActionDispatchResult(
                action_id=action_id,
                success=False,
                error=f"Action '{action_id}' is restricted to AGENT_ONLY surface mode.",
                actor=actor,
                origin=origin,
            )

        # Enforce Human-in-the-Loop approval for risky agent actions
        ticket_id = None
        if spec.requires_human_confirmation and origin == "agent":
            logger.info("Action '%s' requires human confirmation. Requesting HITL ticket...", action_id)
            approved, resolution = await self.ui_bridge.request_hitl_approval_async(
                session_id=session_id,
                agent=actor,
                action_type=action_id,
                details={
                    "label_uk": spec.label_uk,
                    "description": spec.description_en,
                    "payload": payload,
                    "ui_widget": spec.ui_widget,
                },
                timeout=timeout,
            )
            ticket_id = resolution.get("ticket_id")
            if not approved:
                reason = resolution.get("reason", "Human rejected or ticket timed out.")
                logger.warning("HITL approval rejected for action '%s': %s", action_id, reason)
                return ActionDispatchResult(
                    action_id=action_id,
                    success=False,
                    error=f"HITL Approval Rejected: {reason}",
                    requires_approval=True,
                    ticket_id=ticket_id,
                    actor=actor,
                    origin=origin,
                )

            # Apply any parameter overrides approved by human
            if resolution.get("modifications"):
                payload = {**payload, **resolution["modifications"]}
                logger.info("Applied human parameter overrides to action '%s'", action_id)

        # Execute handler
        try:
            start_time = time.time()
            if inspect.iscoroutinefunction(handler):
                result = await handler(payload, actor=actor, origin=origin)
            else:
                result = handler(payload, actor=actor, origin=origin)
            duration_ms = (time.time() - start_time) * 1000

            # Broadcast successful mutation event to ActionBus & Astryx UI
            event = BusEvent(
                event_id=f"evt_act_{uuid.uuid4().hex[:8]}",
                event_type=BusEventType.CANVAS_BATCH_MUTATION,
                task_id=session_id,
                payload={
                    "kind": "dual_surface_action_executed",
                    "action_id": action_id,
                    "label_uk": spec.label_uk,
                    "origin": origin,
                    "actor": actor,
                    "payload": payload,
                    "result": result,
                    "duration_ms": round(duration_ms, 2),
                    "timestamp_epoch": time.time(),
                },
            )
            self.ui_bridge.broadcaster.broadcast(event, agent=actor)

            return ActionDispatchResult(
                action_id=action_id,
                success=True,
                result=result,
                requires_approval=spec.requires_human_confirmation and origin == "agent",
                ticket_id=ticket_id,
                actor=actor,
                origin=origin,
            )

        except Exception as exc:
            logger.exception("Failed to execute handler for action '%s': %s", action_id, exc)
            return ActionDispatchResult(
                action_id=action_id,
                success=False,
                error=str(exc),
                ticket_id=ticket_id,
                actor=actor,
                origin=origin,
            )
