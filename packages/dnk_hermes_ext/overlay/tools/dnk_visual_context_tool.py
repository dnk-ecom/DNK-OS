# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_visual_context_tool.py"
# purpose: "Native Hermes tool for querying and binding visual canvas contexts and UI selections to agent tasks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKVisualContextTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.canvas.visual_context import VisualContextRegistry, VisualContextDTO
except ImportError:
    VisualContextRegistry = None
    VisualContextDTO = None


def dnk_visual_context_query(
    context_id: Optional[str] = None,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Queries registered visual context selections from the Visual Working Cabinet Canvas.

    Args:
        context_id: Specific context identifier to retrieve (if omitted, queries all active contexts for the workspace).
        workspace_id: Active workspace identifier.

    Returns:
        JSON string containing the visual selection metadata, bounding box, and associated DOM element tags.
    """
    if VisualContextRegistry is None:
        return json.dumps({
            "status": "simulated",
            "workspace_id": workspace_id,
            "contexts": [
                {
                    "context_id": "vctx-canvas-001",
                    "canvas_id": "canvas-main-001",
                    "selected_nodes": ["gerych_builder", "SwarmCanvasFlow"],
                    "viewport": {"zoom": 1.0, "x": 0, "y": 0}
                }
            ]
        }, indent=2)

    try:
        registry = VisualContextRegistry()
        if context_id:
            ctx = registry.get_context_by_id(context_id=context_id, workspace_id=workspace_id)
            if not ctx:
                return json.dumps({"status": "not_found", "context_id": context_id})
            return json.dumps({"status": "success", "context": ctx.dict() if hasattr(ctx, "dict") else ctx.model_dump()}, indent=2)
        else:
            return json.dumps({
                "status": "success",
                "workspace_id": workspace_id,
                "total_contexts": len(registry.registry)
            }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_dnk_visual_context_schema() -> Dict[str, Any]:
    """Returns OpenAI/Hermes tool schema for dnk_visual_context_query."""
    return {
        "type": "function",
        "function": {
            "name": "dnk_visual_context_query",
            "description": "Queries visual context selections, bounding boxes, or active canvas nodes from the Visual Working Cabinet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "context_id": {
                        "type": "string",
                        "description": "Optional specific visual context ID to retrieve."
                    },
                    "workspace_id": {
                        "type": "string",
                        "description": "Target workspace identifier (default: ws-alpha-001)."
                    }
                }
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_visual_context_query",
        toolset="visual",
        schema=get_dnk_visual_context_schema(),
        handler=dnk_visual_context_query,
    )
except Exception:
    pass
