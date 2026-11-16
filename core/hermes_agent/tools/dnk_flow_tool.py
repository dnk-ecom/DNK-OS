# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_flow_tool.py"
# purpose: "Native Hermes tool for executing autonomous LangGraph workflows (Research-Write-Validate flow)."
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

logger = logging.getLogger("DNKFlowTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

from uuid import uuid4
import asyncio

try:
    from core.flows.research_write_validate import run_flow
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except ImportError:
    run_flow = None
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_run_research_flow(
    query: str,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Executes the autonomous Research -> Write -> Validate LangGraph pipeline on a given topic.

    Args:
        query: Research question or topic (e.g. 'Optimizing Shopify Liquid rendering').
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the final validated artifact and flow execution trace.
    """
    if run_flow is None:
        return json.dumps({"status": "error", "message": "LangGraph research flow unavailable"})

    try:
        run_id = uuid4()
        canvas_id = uuid4()
        
        # Execute async flow
        artifact = asyncio.run(run_flow(run_id=run_id, canvas_id=canvas_id, query=query))

        return json.dumps({
            "status": "success",
            "run_id": str(run_id),
            "canvas_id": str(canvas_id),
            "query": query,
            "workspace_id": workspace_id,
            "artifact_length": len(artifact),
            "artifact_snippet": artifact[:300] + ("..." if len(artifact) > 300 else "")
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_flow_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_run_research_flow",
            "description": "Runs the autonomous Research -> Write -> Validate LangGraph workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research inquiry or architecture topic."},
                    "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                },
                "required": ["query"]
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_run_research_flow",
        toolset="flows",
        schema=get_flow_schema(),
        handler=dnk_run_research_flow,
    )
except Exception:
    pass
