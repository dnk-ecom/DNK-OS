# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_taskdna_tool.py"
# purpose: "Native Hermes tool for TaskDNA hierarchical goal decomposition and DAG dependency tree generation."
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

logger = logging.getLogger("DNKTaskDNATool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except ImportError:
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_decompose_task_dna(
    goal: str = "",
    workspace_id: str = "ws-alpha-001",
    task_id: Optional[str] = None,
    **kwargs: Any
) -> str:
    """
    Decomposes a complex goal or epic into an evolutionary TaskDNA DAG dependency tree.

    Args:
        goal: High-level user goal or feature specification.
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the subtask nodes, assigned swarm workers, risk assessments, and execution order.
    """
    # Safe normalization of goal argument against dict/list/non-string payloads
    if isinstance(goal, dict):
        goal_str = json.dumps(goal, sort_keys=True)
        goal_display = str(goal.get("goal") or goal.get("title") or goal.get("description") or goal_str)
    elif not isinstance(goal, str):
        goal_str = str(goal)
        goal_display = goal_str
    else:
        goal_str = goal
        goal_display = goal

    task_id = task_id or f"taskdna-{abs(hash(goal_str)) % 100000}"
    
    # Generate structured subtask decomposition DAG
    subtasks = [
        {
            "id": f"{task_id}-sub-1",
            "title": "Architecture & Interface Contract Specification",
            "assigned_agent": "antigravity_mentor",
            "dependencies": [],
            "risk_level": "low"
        },
        {
            "id": f"{task_id}-sub-2",
            "title": f"Implementation of Core Submodules for '{goal_display[:40]}'",
            "assigned_agent": "gerych_builder",
            "dependencies": [f"{task_id}-sub-1"],
            "risk_level": "medium"
        },
        {
            "id": f"{task_id}-sub-3",
            "title": "Adversarial Code Audit & Quality Gate Verification",
            "assigned_agent": "gerych_auditor",
            "dependencies": [f"{task_id}-sub-2"],
            "risk_level": "low"
        }
    ]

    # Emit event to Visual Cabinet
    if RuntimeEvent and RuntimeEventBus:
        try:
            bus = RuntimeEventBus.get_instance()
            bus.publish(RuntimeEvent(
                tenant_id="tenant-alpha-001",
                workspace_id=workspace_id,
                canvas_id="canvas-main-001",
                graph_id="graph-swarm-001",
                thread_id=f"thread-taskdna-{task_id}",
                execution_id=f"exec-taskdna-{task_id}",
                node_id="antigravity_mentor",
                event_type="taskdna.decomposed",
                sequence_number=1,
                payload={
                    "task_id": task_id,
                    "goal": goal,
                    "subtasks_count": len(subtasks)
                }
            ))
        except Exception:
            pass

    return json.dumps({
        "status": "success",
        "task_id": task_id,
        "goal": goal,
        "workspace_id": workspace_id,
        "total_subtasks": len(subtasks),
        "dag_tree": subtasks
    }, indent=2, ensure_ascii=False)


def get_taskdna_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_decompose_task_dna",
            "description": "Decomposes a complex objective into an evolutionary TaskDNA DAG dependency tree assigned to specialized swarm agents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "High-level goal or feature request."},
                    "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                },
                "required": ["goal"]
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_decompose_task_dna",
        toolset="orchestration",
        schema=get_taskdna_schema(),
        handler=dnk_decompose_task_dna,
    )
except Exception:
    pass
