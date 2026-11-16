# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_swarm_tool.py"
# purpose: "Native Hermes tool suite bridging Gerych Prime with DNK OS SwarmCoordinator, SwarmEngine, and Runtime Events."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-02"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("DNKSwarmTool")

# Ensure DNK OS root and core are importable
HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(HUB_ROOT))

if "core" in sys.modules and hasattr(sys.modules["core"], "__path__"):
    core_path = str(HUB_ROOT / "core")
    if core_path not in sys.modules["core"].__path__:
        sys.modules["core"].__path__.insert(0, core_path)

try:
    from core.orchestrator.swarm_coordinator import swarm_coordinator
except Exception as e:
    try:
        import importlib.util
        coord_file = HUB_ROOT / "core" / "orchestrator" / "swarm_coordinator.py"
        if coord_file.exists():
            spec = importlib.util.spec_from_file_location("swarm_coordinator_dyn", str(coord_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            swarm_coordinator = mod.swarm_coordinator
        else:
            swarm_coordinator = None
    except Exception as err:
        logger.error("Failed to load SwarmCoordinator: %s", err)
        swarm_coordinator = None

try:
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except Exception:
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_swarm_dispatch(
    agent: str,
    task_description: str,
    workspace_id: str = "ws-alpha-001",
    tenant_id: str = "tenant-alpha-001",
    parameters: Optional[Dict[str, Any]] = None,
    mode: str = "direct"
) -> str:
    """
    Dispatches a task to a specialized DNK OS Swarm Worker (gerych_builder, gerych_researcher, dnk_shopify, dnk_dev_fullstack, gerych_auditor).
    """
    if swarm_coordinator is None:
        return json.dumps({
            "status": "error",
            "message": "DNK OS SwarmCoordinator not available in current runtime environment."
        })

    try:
        # Publish start event to RuntimeEventBus for Visual Canvas
        if RuntimeEvent and RuntimeEventBus:
            try:
                bus = RuntimeEventBus.get_instance()
                bus.publish(RuntimeEvent(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    canvas_id="canvas-main-001",
                    graph_id="graph-swarm-001",
                    thread_id=f"thread-{agent}",
                    execution_id=f"exec-{agent}-{os.getpid()}",
                    node_id=agent,
                    event_type="node.started",
                    sequence_number=1,
                    payload={"role": agent, "task": task_description}
                ))
            except Exception:
                pass

        # Execute subtask through SwarmCoordinator
        task_action = (parameters or {}).get("action", "execute")
        task_dict = {
            "agent": agent,
            "action": task_action,
            "mode": mode,
            "timeout_seconds": (parameters or {}).get("timeout_seconds", 120),
            "payload": {
                "task_description": task_description,
                "workspace_id": workspace_id,
                "parameters": parameters or {},
                "target_files": (parameters or {}).get("target_files", [])
            }
        }
        res = swarm_coordinator.dispatch_parallel([task_dict])
        completed = res.get("completed_tasks", [{}])[0]

        # Publish completion event
        if RuntimeEvent and RuntimeEventBus:
            try:
                bus = RuntimeEventBus.get_instance()
                bus.publish(RuntimeEvent(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    canvas_id="canvas-main-001",
                    graph_id="graph-swarm-001",
                    thread_id=f"thread-{agent}",
                    execution_id=f"exec-{agent}-{os.getpid()}",
                    node_id=agent,
                    event_type="node.completed",
                    sequence_number=2,
                    payload={"role": agent, "status": "completed", "outcome": completed.get("outcome")}
                ))
            except Exception:
                pass

        return json.dumps({
            "status": "success",
            "agent": agent,
            "task_description": task_description,
            "duration_seconds": completed.get("duration_seconds", 0.0),
            "model_routing": completed.get("model_routing", {}),
            "outcome": completed.get("outcome", {}),
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.exception("Failed to dispatch swarm task: %s", e)
        return json.dumps({
            "status": "failed",
            "error": str(e),
            "agent": agent
        })


# ---------------------------------------------------------------------------
# dnk_triage_task — Autonomous Swarm Triage (Step 0: Complexity Classification)
# ---------------------------------------------------------------------------
try:
    from core.orchestrator.task_triage import dnk_triage_task_json as _triage_json
except Exception:
    _triage_json = None


def dnk_triage_task(goal_or_prompt: str) -> str:
    """
    Step 0 classifier for Gerych Prime.
    Evaluates task complexity and returns a structured routing decision:
      - SOLO (C <= 3): Gerych executes directly within 15 tool calls
      - SWARM_PARALLEL: Independent domain workers run simultaneously (fastest)
      - SWARM_SEQUENTIAL: Phased sequential handoffs across specialist agents

    Formula: C = F_files + (2 * D_domains) + (3 * S_stages)

    Returns a JSON TriageResult with mode, complexity_score, rationale,
    domains_detected, and execution_plan (agent assignments per slice/group).

    Usage:
        triage = dnk_triage_task(user_prompt)
        # If mode == "SOLO": execute directly
        # If mode == "SWARM_*": route via dnk_swarm_parallel / dnk_swarm_dispatch
    """
    if _triage_json is None:
        return json.dumps({
            "mode": "SOLO",
            "complexity_score": 0,
            "rationale": "TaskTriageEngine not loaded — defaulting to SOLO execution.",
            "execution_plan": []
        })
    try:
        return _triage_json(goal_or_prompt)
    except Exception as e:
        return json.dumps({"mode": "SOLO", "error": str(e)})


def dnk_swarm_pipeline(goal: str, target_module: Optional[str] = "core") -> str:
    """
    Executes the autonomous 4-stage Gerych Swarm pipeline:
    Prime (Planning) -> Researcher (Analysis) -> Builder (Implementation) -> Auditor (Verification Gate).
    """
    if swarm_coordinator is None:
        return json.dumps({"status": "error", "message": "SwarmCoordinator not available"})

    try:
        res = swarm_coordinator.run_pipeline(goal=goal, target_module=target_module)
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def dnk_swarm_parallel(
    tasks_json: Optional[Union[str, List[Any]]] = None,
    tasks: Optional[List[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> str:
    """
    Executes a batch of subagent tasks concurrently in parallel.
    tasks_json should be a JSON array of dicts: [{'agent': 'gerych_builder', 'action': '...', 'payload': {...}}]
    """
    global swarm_coordinator
    if swarm_coordinator is None:
        try:
            import importlib.util
            coord_file = HUB_ROOT / "core" / "orchestrator" / "swarm_coordinator.py"
            if coord_file.exists():
                spec = importlib.util.spec_from_file_location("swarm_coordinator_dyn", str(coord_file))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    swarm_coordinator = getattr(mod, "swarm_coordinator", None)
        except Exception:
            pass

    if swarm_coordinator is None:
        return json.dumps({"status": "error", "message": "SwarmCoordinator not available"})

    try:
        raw_tasks = tasks
        if raw_tasks is None and tasks_json is not None:
            if isinstance(tasks_json, str):
                raw_tasks = json.loads(tasks_json)
            elif isinstance(tasks_json, list):
                raw_tasks = tasks_json
        if raw_tasks is None:
            raw_tasks = kwargs.get("tasks")

        if not isinstance(raw_tasks, list):
            return json.dumps({"status": "error", "message": "tasks_json or tasks must be a JSON array of task objects"})
        res = swarm_coordinator.dispatch_parallel(raw_tasks)
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def dnk_swarm_status(
    swarm_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **kwargs: Any
) -> str:
    """
    Returns live status, capabilities, and registered profiles of all 14 DNK OS Swarm Workers.
    Gracefully accepts swarm_id, task_id, and arbitrary telemetry kwargs.
    """
    global swarm_coordinator
    s_id = swarm_id or kwargs.get("swarm_id")
    t_id = task_id or kwargs.get("task_id")
    if swarm_coordinator is None:
        try:
            import importlib.util
            coord_file = HUB_ROOT / "core" / "orchestrator" / "swarm_coordinator.py"
            if coord_file.exists():
                spec = importlib.util.spec_from_file_location("swarm_coordinator_dyn", str(coord_file))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    swarm_coordinator = getattr(mod, "swarm_coordinator", None)
        except Exception:
            pass

    if swarm_coordinator is None:
        return json.dumps({"status": "error", "message": "SwarmCoordinator not available"})

    try:
        agents = swarm_coordinator.list_agents()
        resp: Dict[str, Any] = {
            "status": "success",
            "total_agents": len(agents),
            "agents": agents
        }
        if s_id:
            resp["swarm_id"] = s_id
        if t_id:
            resp["task_id"] = t_id
        return json.dumps(resp, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


def get_dnk_swarm_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "dnk_swarm_dispatch",
                "description": "Dispatches a subtask to specialized DNK OS Swarm Workers (gerych_builder, gerych_researcher, dnk_shopify, dnk_dev_fullstack, gerych_auditor, dnk_video_ai_creator, etc.) with real model routing and visual canvas event streaming.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "string",
                            "description": "Target worker role: 'gerych_builder' (Code/UI), 'gerych_researcher' (AST & SOTA Retrieval), 'dnk_shopify' (Liquid/Checkout/Vite), 'dnk_dev_fullstack' (FastAPI/ORM), 'gerych_auditor' (Adversarial Security & Test Gate), 'dnk_video_ai_creator', 'dnk_scones_memory', 'dnk_analytics', 'dnk_finance_cfo', etc."
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Clear description of the work to be performed."
                        },
                        "mode": {
                            "type": "string",
                            "description": "'direct' (fast domain engine) or 'autonomous_subagent' (isolated worker process)",
                            "enum": ["direct", "autonomous_subagent"]
                        },
                        "workspace_id": {
                            "type": "string",
                            "description": "Target workspace identifier (default: ws-alpha-001)."
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Optional parameters dictionary."
                        }
                    },
                    "required": ["agent", "task_description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dnk_swarm_pipeline",
                "description": "Executes the 4-stage autonomous Gerych Swarm pipeline: Prime (Plan) -> Researcher (AST patterns) -> Builder (Code) -> Auditor (Adversarial review gate).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string", "description": "High-level goal specification"},
                        "target_module": {"type": "string", "description": "Target module or domain (default: core)"}
                    },
                    "required": ["goal"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dnk_swarm_parallel",
                "description": "Executes multiple subagent tasks concurrently in parallel threads with automatic model tier routing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tasks_json": {
                            "type": "string",
                            "description": "JSON array of task specifications: [{'agent': 'dnk_shopify', 'action': '...', 'payload': {...}}, ...]"
                        }
                    },
                    "required": ["tasks_json"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dnk_swarm_status",
                "description": "Queries the live status, capabilities, and availability of all 14 DNK OS Swarm Workers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "swarm_id": {
                            "type": "string",
                            "description": "Optional swarm identifier."
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Optional task telemetry identifier."
                        }
                    }
                }
            }
        }
    ]


try:
    from tools.registry import registry
    schemas = get_dnk_swarm_schemas()
    registry.register(
        name="dnk_swarm_dispatch",
        toolset="dnk_swarm",
        schema=schemas[0],
        handler=dnk_swarm_dispatch,
    )
    registry.register(
        name="dnk_swarm_pipeline",
        toolset="dnk_swarm",
        schema=schemas[1],
        handler=dnk_swarm_pipeline,
    )
    registry.register(
        name="dnk_swarm_parallel",
        toolset="dnk_swarm",
        schema=schemas[2],
        handler=dnk_swarm_parallel,
    )
    registry.register(
        name="dnk_swarm_status",
        toolset="dnk_swarm",
        schema=schemas[3],
        handler=dnk_swarm_status,
    )
    registry.register(
        name="dnk_triage_task",
        toolset="dnk_swarm",
        schema={
            "name": "dnk_triage_task",
            "description": (
                "Step 0 Autonomous Complexity Classifier for Gerych Prime. "
                "ALWAYS CALL THIS FIRST before starting any multi-file or multi-step task. "
                "Evaluates task complexity (C = F_files + 2*D_domains + 3*S_stages) and returns "
                "a structured routing decision: SOLO (execute directly), SWARM_PARALLEL (launch "
                "independent domain workers simultaneously), or SWARM_SEQUENTIAL (phased handoffs). "
                "Provides execution_plan with assigned agents per slice and parallel_group batching."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_or_prompt": {
                        "type": "string",
                        "description": "The full task prompt, markdown specification, or user request to classify."
                    }
                },
                "required": ["goal_or_prompt"]
            }
        },
        handler=dnk_triage_task,
    )
except Exception:
    pass


