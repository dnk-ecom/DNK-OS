# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/actions/canvas_actions.py"
# purpose: "Canonical Dual-Surface Actions for Living Canvas & Taskboard manipulation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""
Standard Dual-Surface Canvas Actions.
Callable identically by Astryx UI (buttons/drags) and Agents (FastMCP tools).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core.action_bus.dual_surface_registry import DualSurfaceActionRegistry
from core.adapters.taskboard_canvas_bridge import TaskboardCanvasBridge
from core.adapters.hermes_ui_bridge import HermesUIBridge
from core.domain.vibe_core_contracts import ActionSurfaceMode, DualSurfaceActionSpec

logger = logging.getLogger("dnk.action_bus.canvas_actions")


def _get_taskboard_bridge() -> TaskboardCanvasBridge:
    db_path = Path(".agents/taskboard/tasks.sqlite")
    if not db_path.exists():
        db_path = Path("../../.agents/taskboard/tasks.sqlite")
    return TaskboardCanvasBridge(db_path=db_path)


def register_canvas_actions(registry: Optional[DualSurfaceActionRegistry] = None) -> None:
    """Registers standard canvas actions into the specified or shared registry."""
    reg = registry or DualSurfaceActionRegistry.get_shared_instance()

    # 1. canvas.move_node
    spec_move = DualSurfaceActionSpec(
        action_id="canvas.move_node",
        label_uk="Перемістити вузол",
        description_en="Moves a canvas node to new spatial coordinates (x, y)",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_canvas",
        mcp_tool_name="canvas_move_node",
        input_json_schema={
            "type": "object",
            "properties": {
                "node_id": {"type": "string", "description": "ID of node to reposition"},
                "x": {"type": "number", "description": "Target X coordinate"},
                "y": {"type": "number", "description": "Target Y coordinate"},
            },
            "required": ["node_id", "x", "y"],
        },
        ui_widget="button",
        ui_tone="primary",
    )

    async def handle_move_node(payload: Dict[str, Any], actor: str = "human", origin: str = "ui") -> Dict[str, Any]:
        node_id = payload["node_id"]
        x = float(payload["x"])
        y = float(payload["y"])
        logger.info("Executed canvas.move_node for %s to (%f, %f) by %s (%s)", node_id, x, y, actor, origin)
        return {"status": "moved", "node_id": node_id, "x": x, "y": y, "actor": actor}

    reg.register_action(spec_move, handle_move_node)

    # 2. canvas.update_task_status
    spec_update_status = DualSurfaceActionSpec(
        action_id="canvas.update_task_status",
        label_uk="Оновити статус задачі",
        description_en="Updates Kanban task status (todo, planned, in_progress, verification, done, failed) and syncs canvas",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_taskboard",
        mcp_tool_name="update_task_status",
        input_json_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "ID of task to update"},
                "new_status": {
                    "type": "string",
                    "enum": ["todo", "planned", "in_progress", "verification", "done", "failed"],
                    "description": "Target workflow status",
                },
                "execution_logs": {"type": "string", "description": "Optional logs or reasoning"},
            },
            "required": ["task_id", "new_status"],
        },
        ui_widget="button",
        ui_tone="secondary",
    )

    async def handle_update_task_status(payload: Dict[str, Any], actor: str = "human", origin: str = "ui") -> Dict[str, Any]:
        task_id = payload["task_id"]
        new_status = payload["new_status"]
        execution_logs = payload.get("execution_logs")

        bridge = _get_taskboard_bridge()
        updated = False
        try:
            updated = bridge.update_task_status(task_id, new_status, execution_logs)
        except Exception as e:
            logger.warning("Could not persist to SQLite taskboard: %s (fallback in-memory)", e)

        # Broadcast mutation via HermesUIBridge
        ui_bridge = HermesUIBridge.get_shared_instance()
        ui_bridge.publish_taskboard_mutation(
            task_id=task_id,
            new_status=new_status,
            agent=actor,
            execution_logs=execution_logs,
        )

        return {
            "success": True,
            "task_id": task_id,
            "new_status": new_status,
            "persisted_db": updated,
            "actor": actor,
        }

    reg.register_action(spec_update_status, handle_update_task_status)

    # 3. canvas.delete_node (High Risk -> requires_human_confirmation=True)
    spec_delete = DualSurfaceActionSpec(
        action_id="canvas.delete_node",
        label_uk="Видалити вузол канвасу",
        description_en="Permanently removes a node and its incoming/outgoing edges from canvas",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_canvas",
        mcp_tool_name="canvas_delete_node",
        input_json_schema={
            "type": "object",
            "properties": {
                "node_id": {"type": "string", "description": "ID of node to delete"},
                "reason": {"type": "string", "description": "Justification for deletion"},
            },
            "required": ["node_id"],
        },
        ui_widget="approve_reject",
        ui_tone="danger",
        requires_human_confirmation=True,
    )

    async def handle_delete_node(payload: Dict[str, Any], actor: str = "human", origin: str = "ui") -> Dict[str, Any]:
        node_id = payload["node_id"]
        reason = payload.get("reason", "No reason provided")
        logger.warning("Deleted canvas node %s by %s. Reason: %s", node_id, actor, reason)
        return {"deleted": True, "node_id": node_id, "actor": actor, "reason": reason}

    reg.register_action(spec_delete, handle_delete_node)
