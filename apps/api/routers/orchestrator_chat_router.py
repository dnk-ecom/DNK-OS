# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/orchestrator_chat_router.py"
# purpose: "Living Conversational Orchestrator Chat API connecting ThoughtDAG Canvas with Gerych Prime Swarm."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import time
import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from apps.api.services.orchestrator_llm_service import orchestrator_llm

logger = logging.getLogger("apps.api.routers.orchestrator_chat")

router = APIRouter(prefix="/api/v1/orchestrator", tags=["Gerych Orchestrator Chat & Canvas Bridge"])

# Models
class CanvasAction(BaseModel):
    action_type: str = Field(..., description="Action type: 'add_note' | 'add_agent_task' | 'connect_wire' | 'compile_context' | 'run_agent'")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Action parameters and data")

class OrchestratorChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt or directive for Gerych Prime")
    session_id: Optional[str] = Field(default="session-main", description="Chat session identifier")
    target_agent: Optional[str] = Field(default="gerych_prime", description="Direct target swarm worker")
    canvas_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Snapshot of current canvas nodes and wires")
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Recent conversation turns")
    selected_node: Optional[Dict[str, Any]] = Field(default=None, description="Currently focused canvas node and context")

class OrchestratorChatResponse(BaseModel):
    reply: str
    agent: str = "gerych_prime"
    session_id: str
    timestamp: float
    canvas_actions: List[CanvasAction] = Field(default_factory=list)
    active_agents: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    provider: Optional[str] = None


AVAILABLE_SWARM_AGENTS = [
    "gerych_prime",
    "gerych_builder",
    "dnk_shopify",
    "dnk_dev_fullstack",
    "gerych_auditor",
    "dnk_video_ai_creator",
    "dnk_scones_memory",
    "herich_librarian",
]


def _synthesize_orchestrator_response(
    message: str,
    target_agent: str,
    canvas_context: Optional[Dict[str, Any]] = None
) -> tuple[str, List[CanvasAction], List[str]]:
    """
    Synthesizes Gerych Prime's decision, response, and canvas mutation actions.
    Understands Ukrainian and English directives for living canvas interaction.
    """
    msg_lower = message.lower().strip()
    actions: List[CanvasAction] = []
    active = ["gerych_prime"]

    # Current context extraction
    nodes = (canvas_context or {}).get("nodes", [])
    has_notes = any(n.get("type") in ("thoughtDagNote", "StrategyMarkdownNode", "ShopifySpecNoteNode") for n in nodes)
    has_agents = any(n.get("type") in ("agentTaskNode", "AgentTaskNode", "mindMapAgent") for n in nodes)

    # 1. Intent: Create Note / Living Note
    if any(k in msg_lower for k in ["нотатк", "note", "вимог", "інструкці", "контекст", "промпт"]):
        note_title = "Living ThoughtDAG Note"
        note_content = message
        if "liquid" in msg_lower or "shopify" in msg_lower:
            note_title = "Shopify Liquid Requirements"
            note_content = "### Liquid Rules\n1. Use secure AST-friendly syntax\n2. Follow OS 2.0 schema invariants\n3. Zero inline style pollution"
            active.append("dnk_shopify")
        elif "архітектур" in msg_lower or "arch" in msg_lower:
            note_title = "System Architecture Note"
            note_content = "### Invariants\n- Relative paths only\n- Deterministic proof over verbal claims\n- 100% test pass gate"
        
        actions.append(CanvasAction(
            action_type="add_note",
            payload={
                "title": note_title,
                "content": note_content,
                "x": 100,
                "y": 150,
                "highlightMode": "all"
            }
        ))

    # 2. Intent: Add Agent / Task
    agent_target = "gerych_builder"
    agent_title = "Builder Task"
    if "аудит" in msg_lower or "тест" in msg_lower or "перевір" in msg_lower or "audit" in msg_lower:
        agent_target = "gerych_auditor"
        agent_title = "Adversarial Quality Gate"
    elif "shopify" in msg_lower or "liquid" in msg_lower or "checkout" in msg_lower or "магазин" in msg_lower:
        agent_target = "dnk_shopify"
        agent_title = "Shopify Theme & AST Engine"
    elif "бек" in msg_lower or "api" in msg_lower or "fastapi" in msg_lower or "backend" in msg_lower:
        agent_target = "dnk_dev_fullstack"
        agent_title = "FastAPI Backend Worker"
    elif "відео" in msg_lower or "video" in msg_lower or "remotion" in msg_lower:
        agent_target = "dnk_video_ai_creator"
        agent_title = "Remotion Video Creator"

    if any(k in msg_lower for k in ["агент", "agent", "задач", "task", "зроби", "виконай", "побудуй", "build", "створи"]):
        if agent_target not in active:
            active.append(agent_target)
        actions.append(CanvasAction(
            action_type="add_agent_task",
            payload={
                "title": agent_title,
                "agent": agent_target,
                "description": message,
                "status": "pending",
                "x": 500,
                "y": 150,
            }
        ))

    # 3. If both note and agent were created (or exist), trigger context wire connection
    has_note_action = any(a.action_type == "add_note" for a in actions)
    has_agent_action = any(a.action_type == "add_agent_task" for a in actions)
    
    if has_note_action and has_agent_action:
        actions.append(CanvasAction(
            action_type="connect_wire",
            payload={
                "source_role": "note",
                "target_role": "agent",
                "scope": "all"
            }
        ))

    # Build concise Ukrainian response according to Epistemic Armor rules
    if actions:
        action_names = [f"`{a.action_type}`" for a in actions]
        reply = (
            f"Прийнято. Розгортаю вузли на полотні: {', '.join(action_names)}.\n"
            f"Агенти рою у фокусі: {', '.join(f'`{a}`' for a in active)}.\n"
            f"Контекстний дріт зв'язує живу нотатку з агентом для передачі upstream SHA-256 відбитка."
        )
    else:
        # Conversational / Inquiry response
        reply = (
            f"Полотно синхронізоване з роєм DNK OS. На зв'язку Герич Prime.\n"
            f"Активних нод на полотні: {len(nodes)}. Спеціалізовані агенти рою готові до розгортання: "
            f"`gerych_builder`, `dnk_shopify`, `dnk_dev_fullstack`, `gerych_auditor`.\n"
            f"Ви можете сформулювати ціль (наприклад: 'Створи нотатку з Liquid вимогами та підключи dnk_shopify'), "
            f"і я миттєво згенерую живу топологію на полотні."
        )

    # Generative UI widget synthesis based on domain intent
    gen_ui_widget = ""
    if any(k in msg_lower for k in ["sticky", "atc", "shopify", "liquid", "cart", "товар", "магазин"]):
        gen_ui_widget = (
            '\n\n<!-- GENERATIVE_UI:shopify_block {"blockType":"sticky_atc","title":"Obsidian Titanium Case",'
            '"price":89.99,"variants":["S (Compact)","M (Standard)","L (Pro Max)"],"rating":4.9,"reviewsCount":142,'
            '"stockRemaining":7} -->'
        )
    elif any(k in msg_lower for k in ["відео", "video", "tiktok", "reels", "shorts", "сценарій", "контент"]):
        gen_ui_widget = (
            '\n\n<!-- GENERATIVE_UI:social {"platform":"tiktok","hook":"99% of Shopify stores lose 40% conversions right here!",'
            '"caption":"Here is how to optimize sticky ATC and Cart Rewards in 3 simple steps with DNK OS.",'
            '"audioTrack":"Trending Viral Phonk • High Retention Beat","scenesCount":4,'
            '"cta":"Check the link in bio for the complete SaaP theme blueprint"} -->'
        )
    elif any(k in msg_lower for k in ["аналітик", "analytics", "aov", "cvr", "roas", "конверсі", "метрики"]):
        gen_ui_widget = (
            '\n\n<!-- GENERATIVE_UI:analytics {"title":"Conversion Rate (CVR)","value":"4.82%","changePercent":18.4,'
            '"timeframe":"Останні 7 днів","metricType":"cvr","sparklineData":[32,35,38,42,40,49,54,52,61]} -->'
        )
    elif any(k in msg_lower for k in ["thoughtdag", "спека", "архітектур", "рішення", "decision", "критик"]):
        gen_ui_widget = (
            '\n\n<!-- GENERATIVE_UI:thought_dag {"nodeKind":"decision","title":"DEC-135: Astryx Generative UI & ThoughtDAG Semantic Zoom",'
            '"agent":"Antigravity & Denchik","summary":"Sovereign living cockpit with 4 macro-clusters, semantic zoom, and interactive generative UI widgets in Astryx tokens.",'
            '"lockedDecRef":"DEC-135","flaws":["Macro cluster state must synchronize with low-level Taskboard SQLite",'
            '"SSE stream backpressure on large task sets","Client-side re-renders during high-frequency mutation broadcasts"]} -->'
        )

    reply = reply + gen_ui_widget
    return reply, actions, active


@router.post("/chat", response_model=OrchestratorChatResponse)
async def orchestrator_chat_endpoint(
    payload: OrchestratorChatRequest,
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID")
):
    """
    Direct dialogue endpoint with Gerych Prime and Swarm Orchestrator.
    Powered by live connected LLM models (Vertex AI Gemini / NVIDIA NIM / OpenRouter).
    Returns reasoning message, status, and atomic actions to execute on the canvas.
    """
    logger.info(f"Orchestrator chat received: {payload.message[:60]}... (Agent: {payload.target_agent})")

    try:
        reply_text, actions_raw, active_agents, model_used, provider_used = await orchestrator_llm.generate_response(
            message=payload.message,
            target_agent=payload.target_agent or "gerych_prime",
            canvas_context=payload.canvas_context,
            history=payload.history,
        )
        canvas_actions = [CanvasAction(**act) for act in actions_raw]
    except Exception as exc:
        logger.warning(f"Error in orchestrator_llm: {exc}. Using fallback synthesis.")
        reply_text, canvas_actions, active_agents = _synthesize_orchestrator_response(
            message=payload.message,
            target_agent=payload.target_agent or "gerych_prime",
            canvas_context=payload.canvas_context
        )
        model_used = "fallback-heuristic"
        provider_used = "local"

    return OrchestratorChatResponse(
        reply=reply_text,
        agent=payload.target_agent or "gerych_prime",
        session_id=payload.session_id or "session-main",
        timestamp=time.time(),
        canvas_actions=canvas_actions,
        active_agents=active_agents,
        model=model_used,
        provider=provider_used,
    )


@router.post("/chat/stream")
async def orchestrator_chat_stream(
    payload: OrchestratorChatRequest,
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID")
):
    """
    Streaming SSE endpoint for Gerych Prime Cockpit.
    Transmits live thought, status, tool calls/results, canvas mutations, and content chunks.
    """
    logger.info(f"Orchestrator stream initiated: {payload.message[:60]}... (Agent: {payload.target_agent})")

    async def event_generator():
        try:
            async for event in orchestrator_llm.generate_stream(
                message=payload.message,
                target_agent=payload.target_agent or "gerych_prime",
                canvas_context=payload.canvas_context,
                history=payload.history,
                selected_node=payload.selected_node,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            logger.exception("Error during orchestrator streaming: %s", exc)
            err_event = {
                "type": "error",
                "error": str(exc),
            }
            yield f"data: {json.dumps(err_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/status")
async def orchestrator_status(x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-ID")):
    """
    Returns live health, active LLM model, and available swarm worker roles.
    """
    return {
        "status": "online",
        "orchestrator": "Gerych Prime v4.5.0",
        "active_model": orchestrator_llm.hermes_model,
        "active_provider": orchestrator_llm.active_provider,
        "swarm_size": len(AVAILABLE_SWARM_AGENTS),
        "available_agents": AVAILABLE_SWARM_AGENTS,
        "capabilities": [
            "thoughtdag_contract_002",
            "canvas_graph_mutations",
            "adversarial_audit_gate",
            "context_wire_compilation",
            "live_llm_inference"
        ],
        "timestamp": time.time()
    }
