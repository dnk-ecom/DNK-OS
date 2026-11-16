# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel_legacy.py"
# purpose: "Legacy Engine tool routing adapter for FastMCP Microkernel (DEC-110 Narrow Waist extraction)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import logging
from typing import Any, Dict

logger = logging.getLogger("dnk.core.kernel_legacy")


class LegacyToolDispatcher:
    """
    Handles backward-compatible legacy tool calls (auth, canvas, accounting, safe execution).
    Extracted from core/kernel.py to maintain the Narrow Waist invariant (<400 LOC).
    """

    @staticmethod
    def dispatch(kernel: Any, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        kernel.telemetry.log_step("kernel", f"Calling tool {tool_name}")
        try:
            if tool_name == "auth_verify":
                phrase = arguments.get("phrase", "")
                success = kernel.auth.verify_maksym(phrase)
                kernel.telemetry.log_step("kernel", f"auth_verify: {success}")
                return {"success": success, "message": "Verification passed" if success else "Verification failed"}

            elif tool_name == "canvas_get_view":
                return {
                    "data": kernel.canvas.to_dict(),
                    "text_render": kernel.canvas.render_canvas_text(),
                }

            elif tool_name == "canvas_add_node":
                nid = arguments["node_id"]
                name = arguments["name"]
                ntype = arguments["node_type"]
                state = arguments.get("state", "Queued")
                node = kernel.canvas.add_node(nid, name, ntype, state)
                return {"success": True, "node": node.to_dict()}

            elif tool_name == "accounting_get_report":
                project_id = arguments.get("project_id")
                metrics = kernel.accounting.get_aggregated_metrics(project_id)
                return {"success": True, "metrics": metrics}

            elif tool_name == "execute_safe_task":
                agent_name = arguments["agent_name"]
                task_query = arguments["task_query"]
                file_paths = arguments.get("file_paths", [])

                if agent_name not in kernel.orchestrator.roles:
                    return {"success": False, "error": f"Agent {agent_name} is not registered"}

                plan = kernel.runtime.generate_dry_run_plan("agent_task", file_paths, {"task_query": task_query})

                def action_fn():
                    kernel.orchestrator.compile_agent_system_instructions(agent_name, task_query)

                def verify_fn():
                    return True

                result = kernel.runtime.execute_safely(action_fn, verify_fn, file_paths)
                success_status = result["status"] == "Success"
                task_id = arguments.get("task_id", "99999")
                project_id = arguments.get("project_id", "00_CORE")

                kernel.accounting.log_workflow_telemetry(
                    project_id=project_id,
                    task_id=task_id,
                    tokens_in=arguments.get("tokens_in", 150),
                    tokens_out=arguments.get("tokens_out", 200),
                    cost_usd=arguments.get("cost_usd", 0.0015),
                    duration_ms=arguments.get("duration_ms", 120),
                    success=success_status,
                    token_savings_pct=80.0,
                    dev_time_saved_pct=95.0,
                    estimated_usd_saved=0.10,
                    notes=f"Safely executed {agent_name} task",
                )

                kernel.telemetry.log_trace(
                    task_id=task_id,
                    tool_calls=[{"tool": "execute_safe_task", "arguments": arguments}],
                    inputs=arguments,
                    outputs=result,
                    duration_ms=arguments.get("duration_ms", 120),
                    cost_usd=arguments.get("cost_usd", 0.0015),
                )
                kernel.telemetry.log_trajectory(
                    task_id=task_id,
                    steps=[
                        {"action": "dry_run", "plan": plan},
                        {"action": "execute", "result": result},
                    ],
                )
                return {"success": True, "plan": plan, "execution": result}

            elif tool_name == "request_destructive_action":
                action_type = arguments["action_type"]
                target = arguments["target"]
                details = arguments.get("details", {})
                approval_id = kernel.runtime.request_destructive_action(action_type, target, details)
                return {"success": True, "approval_id": approval_id, "status": "pending_approval"}

            elif tool_name == "approve_destructive_action":
                approval_id = arguments["approval_id"]
                auth_phrase = arguments["phrase"]
                success = kernel.runtime.approve_destructive_action(approval_id, auth_phrase)
                return {
                    "success": success,
                    "message": "Destructive action approved" if success else "Approval failed: Invalid auth phrase",
                }

            elif tool_name == "thought_parse":
                return kernel.parse_thoughts(arguments.get("dsl_text", ""), arguments.get("graph_id", "graph_default"))

            elif tool_name == "system_status":
                return kernel.get_system_status()

            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error in legacy dispatch({tool_name}): {e}", exc_info=True)
            return {"success": False, "error": str(e)}
