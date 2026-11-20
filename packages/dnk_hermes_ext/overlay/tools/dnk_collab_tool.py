# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_collab_tool.py"
# purpose: "Native Hermes tool for Multi-Workspace Collaboration, RBAC queries, and OCC 3-way graph merging."
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

logger = logging.getLogger("DNKCollabTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from services.dnk_workspace.occ_engine import OCCConcurrencyEngine
except ImportError:
    OCCConcurrencyEngine = None


def dnk_workspace_occ_merge(
    base_state_json: str,
    current_state_json: str,
    incoming_state_json: str
) -> str:
    """
    Executes a 3-way structural diff and optimistic merge between base snapshot, server state, and client mutation.

    Args:
        base_state_json: JSON string of common ancestor graph state (version V).
        current_state_json: JSON string of canonical server graph state (version V+k).
        incoming_state_json: JSON string of client mutation patch (originated from V).

    Returns:
        JSON string containing the merge status, merged graph state, or detected conflict details.
    """
    if OCCConcurrencyEngine is None:
        return json.dumps({"status": "error", "message": "OCCConcurrencyEngine unavailable"})

    try:
        base = json.loads(base_state_json) if isinstance(base_state_json, str) else base_state_json
        curr = json.loads(current_state_json) if isinstance(current_state_json, str) else current_state_json
        inc = json.loads(incoming_state_json) if isinstance(incoming_state_json, str) else incoming_state_json

        res = OCCConcurrencyEngine.merge_graph_state(base_state=base, current_state=curr, incoming_state=inc)
        return json.dumps(res.to_dict(), indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_collab_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "dnk_workspace_occ_merge",
                "description": "Performs an OCC 3-way structural merge on multi-user Canvas graph mutations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_state_json": {"type": "string", "description": "Base graph snapshot."},
                        "current_state_json": {"type": "string", "description": "Current server graph state."},
                        "incoming_state_json": {"type": "string", "description": "Incoming client graph mutation."}
                    },
                    "required": ["base_state_json", "current_state_json", "incoming_state_json"]
                }
            }
        }
    ]


try:
    from tools import registry
    for schema in get_collab_schemas():
        registry.register(
            name=schema["function"]["name"],
            toolset="collab",
            schema=schema,
            handler=dnk_workspace_occ_merge,
        )
except Exception:
    pass
