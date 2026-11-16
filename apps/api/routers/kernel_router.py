# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/kernel_router.py"
# purpose: "FastAPI Router for DNK OS Microkernel v2.0: Thought-to-Plan structuring, Action Bus dispatch, and SCONES memory."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from core.kernel import (
    CANONICAL_ROLE_CAPSULES,
    FastMCPKernel,
    ThoughtCompanionRequest,
    ThoughtCompanionResponse,
    get_thought_companion,
)
from core.domain.thought_dsl import parse_thought_dsl
from core.obsidian.json_canvas_builder import (
    JSONCanvasDocument,
    TextNode,
    CanvasEdge,
    CanvasColor,
    CanvasEnd,
    generate_canvas_id,
)

logger = logging.getLogger("dnk.api.kernel")

router = APIRouter(prefix="/api/v1/kernel", tags=["Microkernel v2.0 (Action Bus & Thought Engine)"])

# Shared singleton kernel instance for the API process
_kernel_instance: Optional[FastMCPKernel] = None


def get_kernel() -> FastMCPKernel:
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = FastMCPKernel()
    return _kernel_instance


# -----------------------------------------------------------------------------
# DTO Models
# -----------------------------------------------------------------------------
class IdeaStructureRequest(BaseModel):
    raw_input: str = Field(..., description="Raw thought text or voice transcription from founder")
    title: Optional[str] = Field("Нова Ідея", description="Title or topic for the idea")
    source: str = Field("vibe_coder", description="Source of input (e.g. founder_voice, chat, notes)")
    output_format: str = Field("both", description="'obsidian_canvas', 'thought_dag', or 'both'")


class ActionDispatchRequest(BaseModel):
    action_type: str = Field(..., description="Action identifier (e.g. git.commit, task.create, file.mutate)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Action payload parameters")
    requester: str = Field("vibe_coder", description="Requester identifier")


class ObservationRecordRequest(BaseModel):
    topic: str = Field(..., description="Topic of the learned observation")
    observation: str = Field(..., description="Observation body text")
    source: str = Field("agent", description="Source of observation")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")


class NodeMessagePostRequest(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or domain agent name")
    content: str = Field(..., description="Message text content")
    artifact_refs: List[str] = Field(default_factory=list, description="Associated file or artifact paths")


class NodeCrystallizeRequest(BaseModel):
    summary: str = Field(..., description="Crystallized summary contract of the node output")
    artifact_refs: List[str] = Field(default_factory=list, description="Referenced artifact paths")
    canvas_path: Optional[str] = Field(None, description="Path to .canvas file if updating in place")


class FanInAggregationRequest(BaseModel):
    outputs: List[Dict[str, Any]] = Field(..., description="Subagent branch outputs to validate and merge")
    synthesis_instructions: str = Field("", description="Guidance for final synthesis")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context and invariants")


class QuarantineReleaseRequest(BaseModel):
    approver: str = Field("founder", description="Approving authority identifier")


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/status", status_code=status.HTTP_200_OK)
def get_kernel_status() -> Dict[str, Any]:
    """Returns the live status, soul profile, and active subsystems of Microkernel v2.0."""
    kernel = get_kernel()
    return kernel.get_system_status()


@router.post("/ideas/structure", status_code=status.HTTP_200_OK)
def structure_ideas(req: IdeaStructureRequest) -> Dict[str, Any]:
    """
    Thought-to-Plan Engine:
    Ingests raw founder thoughts (voice or text), validates ThoughtDSL / graphs,
    and materializes them as structured JSON Canvas 1.0 nodes and Task Forest units.
    """
    kernel = get_kernel()
    text = req.raw_input.strip()
    if not text:
        raise HTTPException(status_code=400, detail="raw_input cannot be empty")

    response_data: Dict[str, Any] = {
        "success": True,
        "title": req.title,
        "source": req.source,
    }

    # 1. Check if input is ThoughtDSL or has explicit DSL markers
    is_dsl = "[" in text and "]" in text and ":" in text
    if is_dsl or req.output_format in ("thought_dag", "both"):
        dsl_res = parse_thought_dsl(text)
        response_data["thought_dag"] = {
            "has_cycles": dsl_res.has_cycles,
            "cycle_nodes": dsl_res.cycle_nodes,
            "nodes_count": len(dsl_res.graph.nodes),
            "wires_count": len(dsl_res.graph.wires),
            "nodes": [n.model_dump() for n in dsl_res.graph.nodes.values()],
        }

    # 2. Materialize JSON Canvas 1.0 document (Kepano spec for Obsidian)
    if req.output_format in ("obsidian_canvas", "both"):
        doc = JSONCanvasDocument()

        # Root idea card (Cyan)
        root_id = generate_canvas_id("root_" + req.title)
        root_node = TextNode(
            id=root_id,
            x=0,
            y=0,
            width=360,
            height=160,
            text=f"### 💡 {req.title}\n\n{text[:200]}..." if len(text) > 200 else f"### 💡 {req.title}\n\n{text}",
            color=CanvasColor.CYAN,
        )
        doc.nodes.append(root_node)

        # Split sentences / thoughts into sub-nodes (Emerald Green)
        lines = [line.strip("- •*\t ") for line in text.split("\n") if line.strip()]
        if len(lines) <= 1 and "." in text:
            lines = [s.strip() for s in text.split(".") if len(s.strip()) > 10]

        sub_lines = [l for l in lines if l and l != req.title][:6]
        for idx, sub_line in enumerate(sub_lines):
            sub_id = generate_canvas_id(f"sub_{idx}_{sub_line[:10]}")
            x_pos = 440
            y_pos = (idx - len(sub_lines) // 2) * 140
            sub_node = TextNode(
                id=sub_id,
                x=x_pos,
                y=y_pos,
                width=320,
                height=110,
                text=f"**Крок {idx + 1}**\n\n{sub_line}",
                color=CanvasColor.GREEN,
            )
            doc.nodes.append(sub_node)

            # Connect root to sub-node with directed arrow
            edge = CanvasEdge(
                id=generate_canvas_id(f"edge_{root_id}_{sub_id}"),
                from_node=root_id,
                to_node=sub_id,
                to_end=CanvasEnd.ARROW,
                color=CanvasColor.GREEN,
            )
            doc.edges.append(edge)

        response_data["canvas_document"] = doc.to_dict()

    return response_data


@router.post("/actions/dispatch", status_code=status.HTTP_200_OK)
async def dispatch_action(req: ActionDispatchRequest) -> Dict[str, Any]:
    """Dispatches a mutation task through the Agent Action Bus with strict HITL approval gate."""
    kernel = get_kernel()
    res = await kernel.dispatch_action(req.action_type, req.payload, requester=req.requester)
    return res


@router.get("/memory", status_code=status.HTTP_200_OK)
async def query_memory(
    topic: str = Query(..., description="Search topic substring"),
    limit: int = Query(5, ge=1, le=50, description="Max memory items to return"),
) -> List[Dict[str, Any]]:
    """Queries SCONES cognitive memory for verified past observations and solutions."""
    kernel = get_kernel()
    return await kernel.query_memory(topic, limit=limit)


@router.post("/memory", status_code=status.HTTP_201_CREATED)
async def record_observation(req: ObservationRecordRequest) -> Dict[str, Any]:
    """Records a new learned observation or skill calibration into SCONES memory."""
    kernel = get_kernel()
    obs_id = await kernel.record_observation(
        topic=req.topic,
        observation=req.observation,
        source=req.source,
        confidence=req.confidence,
    )
    return {"recorded": True, "observation_id": obs_id, "topic": req.topic}


@router.get("/companion/capsules", status_code=status.HTTP_200_OK)
def list_companion_capsules() -> Dict[str, Any]:
    """Returns the canonical Role Capsules (<=8 tools, <=6000 tokens) and assimilated SOTA patterns."""
    companion = get_thought_companion()
    return {
        "capsules": {k: v.model_dump() for k, v in CANONICAL_ROLE_CAPSULES.items()},
        "assimilated_patterns": companion.get_assimilated_patterns(),
    }


@router.post("/companion/structure", response_model=ThoughtCompanionResponse, status_code=status.HTTP_200_OK)
def companion_structure_thoughts(req: ThoughtCompanionRequest) -> ThoughtCompanionResponse:
    """
    First Thought Companion & Architect Agent (Gerych Thought Companion):
    Transforms raw founder thoughts or ThoughtDSL into an acyclic ThoughtDAG,
    Obsidian JSON Canvas 1.0 document, Role Capsule bindings, SHA-256 fingerprint,
    and Mandatory Dissent (3 Flaws Rule) critique.
    """
    if not req.raw_thought or not req.raw_thought.strip():
        raise HTTPException(status_code=400, detail="raw_thought cannot be empty")
    companion = get_thought_companion()
    return companion.structure_thoughts(req)


# -----------------------------------------------------------------------------
# Spatial Canvas Node-Session & Context Surgery Endpoints (ADR-092 / DEC-110)
# -----------------------------------------------------------------------------
@router.get("/canvas/nodes/{canvas_id}/{node_id}/context", status_code=status.HTTP_200_OK)
def get_node_session_context(
    canvas_id: str,
    node_id: str,
    canvas_path: Optional[str] = Query(None, description="Optional path to .canvas file"),
    max_tokens: int = Query(1500, ge=100, le=8000, description="Max tokens for context wire"),
) -> Dict[str, Any]:
    """Compiles upstream ancestor wires + L2 DNA + L1 User Soul for an isolated node session."""
    kernel = get_kernel()
    return kernel.compile_node_session_context(
        canvas_id=canvas_id, node_id=node_id, canvas_path=canvas_path, max_tokens=max_tokens
    )


@router.get("/canvas/nodes/{canvas_id}/{node_id}/messages", status_code=status.HTTP_200_OK)
def get_node_session_messages(
    canvas_id: str,
    node_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max messages to fetch"),
) -> List[Dict[str, Any]]:
    """Retrieves conversation thread for an isolated node session from SQLite WAL."""
    kernel = get_kernel()
    return kernel.get_node_messages(canvas_id=canvas_id, node_id=node_id, limit=limit)


@router.post("/canvas/nodes/{canvas_id}/{node_id}/messages", status_code=status.HTTP_201_CREATED)
def post_node_session_message(
    canvas_id: str,
    node_id: str,
    req: NodeMessagePostRequest,
) -> Dict[str, Any]:
    """Appends a message to the isolated node session thread in SQLite WAL."""
    kernel = get_kernel()
    return kernel.post_node_message(
        canvas_id=canvas_id,
        node_id=node_id,
        role=req.role,
        content=req.content,
        artifact_refs=req.artifact_refs,
    )


@router.post("/canvas/nodes/{canvas_id}/{node_id}/crystallize", status_code=status.HTTP_200_OK)
def crystallize_node_session_output(
    canvas_id: str,
    node_id: str,
    req: NodeCrystallizeRequest,
) -> Dict[str, Any]:
    """Crystallizes completed node output into summary contract, preventing context rot."""
    kernel = get_kernel()
    return kernel.crystallize_node_session(
        canvas_id=canvas_id,
        node_id=node_id,
        summary=req.summary,
        artifact_refs=req.artifact_refs,
        canvas_path=req.canvas_path,
    )


# -----------------------------------------------------------------------------
# Multi-Agent Fan-In Aggregation & Governance (UAIP / DEC-116)
# -----------------------------------------------------------------------------
@router.post("/canvas/aggregate", status_code=status.HTTP_200_OK)
def aggregate_fan_in(req: FanInAggregationRequest) -> Dict[str, Any]:
    """
    Executes FanInAggregator with 4-phase deterministic gate
    (SyntaxAST, BoundaryScope, DeterministicExitCode, Grounding) before merging outputs.
    """
    kernel = get_kernel()
    return kernel.aggregate_branch_results(
        outputs=req.outputs,
        context=req.context,
        synthesis_instructions=req.synthesis_instructions,
    )


@router.get("/governance/quarantine/{agent_id}", status_code=status.HTTP_200_OK)
def get_agent_quarantine_status(agent_id: str) -> Dict[str, Any]:
    """Retrieves live circuit-breaker and health status for an agent."""
    kernel = get_kernel()
    return kernel.get_quarantine_record(agent_id)


@router.post("/governance/quarantine/{agent_id}/release", status_code=status.HTTP_200_OK)
def release_agent_quarantine(agent_id: str, req: QuarantineReleaseRequest) -> Dict[str, Any]:
    """Releases a quarantined agent upon founder approval."""
    kernel = get_kernel()
    kernel.quarantine.release_agent(agent_id, approver=req.approver)
    return {"agent_id": agent_id, "status": "released", "approver": req.approver}


