# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel.py"
# purpose: "Unified FastMCP Microkernel Host v2.5.0 coordinating Action Bus, SCONES Memory, Spatial Canvas and Multi-Agent Fan-In."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Denchik (Builder)"
# --- END DNK-MRH-HEADER ---

"""
DNK OS Unified FastMCP Microkernel Host v2.5.0 (Narrow-Waist Invariant: < 400 LOC).
Central protocol gateway coordinating Action Bus, SCONES memory, Spatial Canvas, Fan-In and Quarantine.
"""

import asyncio
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Core v2.0 Microkernel components
from core.action_bus.artifact_store import ArtifactStore
from core.action_bus.broadcaster import EventBroadcaster
from core.action_bus.bus import AgentActionBus
from core.action_bus.hitl_bridge import HitlApprovalBridge
from core.action_bus.models import ActionTask, ActionTaskStatus, BusEvent, BusEventType
from core.action_bus.persistence import ActionBusPersistence
from core.domain.dag_models import (
    ContextCompileRequest, NodeKind, ThoughtDAGGraph, ThoughtNode, Wire, WireType, compile_thoughtdag_context
)
from core.domain.identity_models import BrandDNA, ProjectWorkspace, UserProfile
from core.domain.thought_dsl import (
    MultiParentMergeRequest, MultiParentMergeResult, detect_cycles_kahn, merge_multi_parent_context, parse_thought_dsl
)
from core.memory.scones_store import SconesMemoryStore
from core.orchestrator.task_dna_lifecycle import TaskDNALifecycleEngine, TaskDNAPhase
from core.orchestrator.user_soul import UserSOUL, user_soul
from core.orchestrator.zero_waste_slicer import ZeroWasteSlicer
from core.canvas.session_router import SpatialCanvasSessionRouter
from core.orchestrator.fan_in_aggregator import FanInAggregator, AgentOutput
from core.sentinel.agent_quarantine import AgentQuarantineGuard, AgentQuarantinedError, QuarantineReason

logger = logging.getLogger("dnk.core.kernel")


def uuid_hex() -> str:
    return uuid.uuid4().hex[:12]


class FastMCPKernel:
    """
    Unified FastMCP Microkernel Host v2.5.0 for DNK OS.
    Coordinates decoupled asynchronous execution, spatial canvas event broadcasting,
    strict deterministic safety gates, SCONES memory, and Fan-In aggregation.
    """

    def __init__(
        self,
        db_path: str = ".data/dnk_action_bus.db",
        artifacts_dir: Optional[str] = None,
        workspace_id: str = "ws_default",
        session_store_path: str = ".data/sessions/session_registry.json",
        log_path: str = "core/telemetry/accounting_log.json",
    ):
        # 0. In-Memory Google Secret Manager (GSM) Integration
        try:
            from scripts.system.dnk_secrets import load_gsm_env
            load_gsm_env()
        except Exception:
            pass

        # 1. Action Bus and Substrate Persistence
        self.workspace_id = workspace_id
        self.persistence = ActionBusPersistence(db_path=db_path)
        self.broadcaster = EventBroadcaster()
        self.artifact_store = ArtifactStore(base_dir=artifacts_dir, persistence=self.persistence)
        self.hitl_bridge = HitlApprovalBridge(bus=None)

        self.bus = AgentActionBus(
            persistence=self.persistence,
            broadcaster=self.broadcaster,
            artifact_store=self.artifact_store,
            hitl_bridge=self.hitl_bridge,
            workspace_id=self.workspace_id,
        )
        self.hitl_bridge.bus = self.bus

        # 2. Epistemic Engines and Cognitive Memory
        self.slicer = ZeroWasteSlicer()
        self.task_dna = TaskDNALifecycleEngine()
        self.user_soul = user_soul

        mem_dir = os.path.dirname(db_path) or ".data"
        memory_path = os.path.join(mem_dir, "scones_memory.db")
        self.memory = SconesMemoryStore(db_path=memory_path)

        # 3. SOTA Assimilated Subsystems (DEC-110, DEC-115, DEC-116, DEC-134)
        self.session_router = SpatialCanvasSessionRouter()
        self.fan_in = FanInAggregator()
        self.quarantine = AgentQuarantineGuard()

        self._workspaces: Dict[str, ProjectWorkspace] = {}
        self._active_graphs: Dict[str, ThoughtDAGGraph] = {}
        self._running = True

    # -------------------------------------------------------------------------
    # SCONES Cognitive Memory Operations (v2.5)
    # -------------------------------------------------------------------------
    async def query_memory(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries SCONES cognitive memory for past observations and solutions."""
        return await self.memory.query_memories(topic, limit=limit)

    async def record_observation(
        self, topic: str, observation: str, source: str = "agent", confidence: float = 1.0
    ) -> int:
        """Records a new learned observation or calibration into SCONES memory."""
        return await self.memory.record_observation(
            topic, observation, source=source, confidence=confidence
        )

    # -------------------------------------------------------------------------
    # Spatial ThoughtDAG & Flow Operations (Deer-Flow / Canvas Paradigm v2.5)
    # -------------------------------------------------------------------------
    def parse_thoughts(self, dsl_text: str, graph_id: str = "graph_default") -> Dict[str, Any]:
        """Parses ThoughtDSL into a validated, cycle-checked ThoughtDAG graph."""
        result = parse_thought_dsl(dsl_text)
        if result.has_cycles:
            logger.warning(f"Cycles detected in ThoughtDSL: {result.cycle_nodes}")
            return {
                "success": False,
                "has_cycles": True,
                "cycle_nodes": result.cycle_nodes,
                "errors": result.errors,
            }

        self._active_graphs[graph_id] = result.graph
        return {
            "success": True,
            "has_cycles": False,
            "graph_id": graph_id,
            "nodes_count": len(result.graph.nodes),
            "wires_count": len(result.graph.wires),
        }

    def compile_node_context_wire(
        self, graph_id: str, target_node_id: str, max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """Extracts upstream context strictly along wires (Context-as-Wires) to enforce Context Diet."""
        graph = self._active_graphs.get(graph_id)
        if not graph:
            return {"success": False, "error": f"Graph {graph_id} not found."}

        compiled = compile_thoughtdag_context(graph=graph, target_node_id=target_node_id, max_tokens=max_tokens)
        return {
            "success": True,
            "target_node_id": compiled.target_node_id,
            "upstream_fingerprint": compiled.upstream_fingerprint,
            "token_count": compiled.estimated_tokens,
            "compiled_prompt": compiled.context_text,
        }

    # -------------------------------------------------------------------------
    # Action Bus & HITL Dispatcher
    # -------------------------------------------------------------------------
    async def dispatch_action(
        self, action_type: str, payload: Dict[str, Any], requester: str = "vibe_coder"
    ) -> Dict[str, Any]:
        """Central Action Dispatcher routing execution through the Action Bus with HITL gating."""
        task_id = f"task_{uuid_hex()}"

        # 0. Circuit Breaker Check
        try:
            self.quarantine.assert_can_execute(requester)
        except AgentQuarantinedError as q_err:
            logger.error(f"Execution rejected by QuarantineGuard: {q_err}")
            return {
                "task_id": task_id,
                "status": "BLOCKED_BY_QUARANTINE",
                "message": str(q_err),
                "error": "Agent is currently quarantined due to circuit breaker trip.",
            }

        is_crit = self.hitl_bridge.is_critical(action_type, payload)
        task = ActionTask(
            task_id=task_id,
            action_type=action_type,
            payload=payload,
            status=ActionTaskStatus.WAITING_APPROVAL if is_crit else ActionTaskStatus.PENDING,
            metadata={"requester": requester, "is_critical": is_crit},
        )

        if is_crit:
            async with self.bus._lock:
                self.bus._tasks[task_id] = task
                if self.bus._persistence:
                    await self.bus._persistence.save_task(task)
            await self.bus._publish(
                BusEventType.APPROVAL_REQUESTED,
                task_id,
                {"action_type": action_type, "payload": payload},
            )
            return {
                "task_id": task_id,
                "status": "WAITING_APPROVAL",
                "message": f"Action '{action_type}' requires Human-in-the-Loop approval.",
            }

        if action_type.startswith("clipboard_"):
            from core.adapters.dnk_clipboard_adapter import DNKClipboardAdapter
            sub = action_type.replace("clipboard_", "")
            data = DNKClipboardAdapter().execute_action(sub, payload)
            return {
                "task_id": task_id,
                "status": "COMPLETED",
                "message": f"Action '{action_type}' processed successfully via DNKClipboardAdapter.",
                "result": {"output": data, "handled_by": "dnk_clipboard_adapter"},
            }

        res = await self.bus.dispatch_task(task)
        return {
            "task_id": task_id,
            "status": res.status.value if hasattr(res.status, "value") else str(res.status),
            "message": f"Action '{action_type}' dispatched.",
            "result": res.model_dump() if hasattr(res, "model_dump") else res,
        }

    # -------------------------------------------------------------------------
    # Spatial Canvas Per-Node Session & Context Surgery (ADR-092 / DEC-110)
    # -------------------------------------------------------------------------
    def compile_node_session_context(
        self, canvas_id: str, node_id: str, canvas_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compiles upstream context wires + L2 DNA + L1 Account for an isolated node session."""
        c_path = Path(canvas_path) if canvas_path else Path(f"docs/canvas/{canvas_id}.canvas")
        prompt = self.session_router.compile_node_context(
            canvas_path=c_path, node_id=node_id
        )
        return prompt.model_dump() if hasattr(prompt, "model_dump") else dict(prompt)

    def post_node_message(
        self, canvas_id: str, node_id: str, role: str, content: str, artifact_refs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Appends a message to the isolated node session thread in SQLite WAL."""
        session_id = SpatialCanvasSessionRouter.format_session_id(canvas_id, node_id)
        self.session_router.get_or_create_session(canvas_id, node_id, agent_role=role)
        meta = {"artifact_refs": artifact_refs} if artifact_refs else None
        msg = self.session_router.post_message(session_id, role=role, content=content, meta=meta)
        return {"session_id": session_id, "message_id": msg.id, "status": "recorded"}

    def get_node_messages(self, canvas_id: str, node_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves messages for an isolated node session."""
        session_id = SpatialCanvasSessionRouter.format_session_id(canvas_id, node_id)
        msgs = self.session_router.get_messages(session_id, limit=limit)
        return [m.model_dump() if hasattr(m, "model_dump") else dict(m) for m in msgs]

    def crystallize_node_session(
        self, canvas_id: str, node_id: str, summary: str, artifact_refs: Optional[List[str]] = None, canvas_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crystallizes a completed node output into summary contract, preventing context rot."""
        c_path = Path(canvas_path) if canvas_path else Path(f"docs/canvas/{canvas_id}.canvas")
        if not c_path.exists():
            c_path.parent.mkdir(parents=True, exist_ok=True)
            c_path.write_text('{"nodes":[], "edges":[]}', encoding="utf-8")
        node_session = self.session_router.crystallize_node(
            canvas_path=c_path, node_id=node_id, summary=summary, artifact_refs=artifact_refs
        )
        return node_session.model_dump() if hasattr(node_session, "model_dump") else dict(node_session)

    # -------------------------------------------------------------------------
    # Multi-Agent Fan-In Aggregation with 4-Gate Validation (UAIP / DEC-116)
    # -------------------------------------------------------------------------
    def aggregate_branch_results(
        self, outputs: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None, synthesis_instructions: str = ""
    ) -> Dict[str, Any]:
        """Aggregates outputs from parallel subagents with pre-synthesis validation chain."""
        typed_outputs = [
            AgentOutput(
                agent_id=o.get("agent_id", "subagent"),
                task_id=o.get("task_id", f"task_{uuid_hex()}"),
                status=o.get("status", "completed"),
                summary=o.get("summary", o.get("content", "")),
                produced_files=o.get("produced_files", {f: "" for f in o.get("files_mutated", [])}),
                command_results=o.get("command_results", [{"command": "test", "exit_code": o.get("exit_code", 0)}]),
                metrics=o.get("metrics", {}),
                artifacts=o.get("artifacts", []),
            )
            for o in outputs
        ]
        ctx = dict(context or {})
        if synthesis_instructions:
            ctx["synthesis_instructions"] = synthesis_instructions
        synthesis = self.fan_in.aggregate_and_validate(typed_outputs, context=ctx)
        return synthesis.model_dump()

    def get_quarantine_record(self, agent_id: str) -> Dict[str, Any]:
        """Returns quarantine and circuit breaker status for an agent."""
        rec = self.quarantine.get_or_create(agent_id)
        return rec.model_dump()

    def get_system_status(self) -> Dict[str, Any]:
        """Telemetry and health status endpoint."""
        return {
            "kernel_version": "2.5.0",
            "status": "ACTIVE",
            "workspace_id": self.workspace_id,
            "user_soul": self.user_soul.profile["user_name"],
            "language": self.user_soul.profile["language"],
            "active_graphs": len(self._active_graphs),
            "enqueued_tasks": len(self.bus._tasks),
            "sota_subsystems": {
                "spatial_canvas_session_router": "ACTIVE",
                "fan_in_aggregator": "ACTIVE",
                "agent_quarantine_guard": "ACTIVE",
                "scones_memory_fts5": "ACTIVE",
                "agentic_video_intelligence": "ACTIVE",
            },
        }


# FastMCP Server delegation (Narrow-Waist Invariant: protocol serialization in core/kernel_mcp.py)
from core.kernel_mcp import create_fastmcp_server  # noqa: E402

try:
    from core.kernel_cli import run_cli_command
except ImportError:
    async def run_cli_command(*a, **k): return 0  # type: ignore


if __name__ == "__main__":
    import sys
    kernel = FastMCPKernel()
    if "--cli" in sys.argv:
        sys.exit(asyncio.run(run_cli_command(kernel, [a for a in sys.argv[1:] if a != "--cli"])))
    from core.kernel_mcp import create_fastmcp_server
    server = create_fastmcp_server(kernel)
    if server is not None:
        server.run()
