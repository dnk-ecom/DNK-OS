# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/swarm_router.py"
# purpose: "Dynamic routing matcher and Swarm execution engine for multi-agent coordination."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Antigravity (Mentor & Chief Architect) & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import asyncio
import logging
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from core.action_bus.models import (
    ActionExecutionResponse,
    ActionTask,
    ActionTaskStatus,
    BusEventType,
    SwarmBatchResponse,
    SwarmPipelineResponse,
    SwarmRouteResult,
)

logger = logging.getLogger("dnk.action_bus.swarm_router")


SWARM_AGENT_ROSTER: Dict[str, Dict[str, Any]] = {
    "gerych_prime": {
        "role": "Chief Swarm Manager & Orchestrator",
        "description": "High-level goal decomposition, task routing, supervisor loops, and swarm synchronization.",
        "keywords": ["orchestrate", "plan", "triage", "meta", "general", "root", "coordinate", "supervisor", "decompose"],
        "color": "#6366F1",
    },
    "gerych_builder": {
        "role": "UI & Frontend Systems Engineer",
        "description": "React, Tailwind, UI components, Visual Working Canvas, interactive frontend synthesis.",
        "keywords": ["ui", "frontend", "component", "react", "canvas", "css", "html", "tailwind", "layout", "visual"],
        "color": "#3B82F6",
    },
    "gerych_researcher": {
        "role": "Deep R&D & Repo Assimilator",
        "description": "GitHub exploration, AST signature extraction, SOTA academic paper retrieval, pattern synthesis.",
        "keywords": ["ast", "github", "research", "paper", "sota", "scrape", "search", "explore", "assimilate", "retrieve"],
        "color": "#8B5CF6",
    },
    "gerych_auditor": {
        "role": "Adversarial Security & Test Gatekeeper",
        "description": "Red-team adversary, vulnerability scans, pre-commit quality gates, test suite verification.",
        "keywords": ["security", "audit", "verify", "test", "gate", "adversarial", "lint", "vulnerability", "quality", "precommit"],
        "color": "#EF4444",
    },
    "dnk_dev_fullstack": {
        "role": "Backend & Cloud Services Architect",
        "description": "FastAPI routers, SQLite/PostgreSQL schemas, ORM models, background runners, API contracts.",
        "keywords": ["backend", "api", "fastapi", "database", "sqlalchemy", "model", "migration", "router", "endpoint", "crud"],
        "color": "#10B981",
    },
    "dnk_shopify": {
        "role": "E-Commerce & Liquid Specialist",
        "description": "Shopify Liquid templates, Storefront API, Checkout UI extensions, e-commerce catalog sync.",
        "keywords": ["shopify", "liquid", "store", "product", "cart", "checkout", "theme", "ecommerce", "storefront"],
        "color": "#14B8A6",
    },
    "dnk_video_ai_creator": {
        "role": "Media & Generative Video Producer",
        "description": "Programmatic Remotion compositions, motion design, video rendering, story clips.",
        "keywords": ["video", "remotion", "composition", "animation", "render", "media", "motion", "clip"],
        "color": "#EC4899",
    },
    "dnk_security_guard": {
        "role": "Vault & Secrets Officer",
        "description": "Credential encryption, token isolation, secret leak scanning, permission ACL enforcement.",
        "keywords": ["guard", "firewall", "secret", "vault", "auth", "token", "permission", "encrypt", "key"],
        "color": "#F59E0B",
    },
    "dnk_scones_memory": {
        "role": "Cognitive Memory & Vector Knowledge Keeper",
        "description": "SCONES long-term episodic recall, vector embeddings, contextual facts retrieval.",
        "keywords": ["scones", "memory", "recall", "store", "embedding", "vector", "retrieve", "knowledge", "facts"],
        "color": "#06B6D4",
    },
    "dnk_analytics": {
        "role": "Telemetry & Metrics Analyst",
        "description": "Execution latency, token spending, operational dashboards, Prometheus telemetry.",
        "keywords": ["analytics", "metric", "telemetry", "prometheus", "dashboard", "report", "stats", "spend"],
        "color": "#34D399",
    },
    "dnk_erp_supply": {
        "role": "ERP & Inventory Logistics Manager",
        "description": "Supply chain operations, order processing, warehouse management, shipping logistics.",
        "keywords": ["erp", "supply", "inventory", "order", "warehouse", "logistics", "stock", "fulfillment"],
        "color": "#F97316",
    },
    "dnk_finance_cfo": {
        "role": "CFO & Unit Economics Strategist",
        "description": "COGS optimization, pricing models, revenue analytics, cash flow forecasting.",
        "keywords": ["finance", "cfo", "budget", "cost", "revenue", "invoice", "pricing", "margin", "cogs"],
        "color": "#84CC16",
    },
    "dnk_marketing_cmo": {
        "role": "Growth & Marketing Strategist",
        "description": "Ad copy, landing page messaging, marketing campaigns, customer acquisition funnel.",
        "keywords": ["marketing", "cmo", "campaign", "growth", "copy", "brand", "social", "audience", "headline"],
        "color": "#E11D48",
    },
    "herich_librarian": {
        "role": "Obsidian Vault & ADR Knowledge Curator",
        "description": "Architectural decision records, Obsidian Markdown linking, documentation indexes.",
        "keywords": ["librarian", "obsidian", "vault", "notes", "markdown", "doc", "documentation", "adr", "wiki"],
        "color": "#A855F7",
    },
}


class SwarmTaskRouter:
    """
    Intelligent Dynamic Task Matcher for Swarm Multi-Agent Coordination.
    Analyzes task descriptions, capabilities, and domains to route tasks to the best agent.
    """

    def __init__(self, agent_roster: Optional[Dict[str, Dict[str, Any]]] = None):
        self.roster = agent_roster or SWARM_AGENT_ROSTER

    def list_agents(self) -> List[Dict[str, Any]]:
        """Returns metadata list of all available swarm agents."""
        return [
            {
                "agent_id": agent_id,
                "role": meta.get("role", ""),
                "description": meta.get("description", ""),
                "keywords": meta.get("keywords", []),
                "color": meta.get("color", "#6B7280"),
                "status": "active",
            }
            for agent_id, meta in self.roster.items()
        ]

    def get_agent_roster(self) -> List[Dict[str, Any]]:
        """Alias for list_agents."""
        return self.list_agents()

    def route_task(
        self,
        task_or_prompt: Union[ActionTask, str],
        preferred_agent: Optional[str] = None,
    ) -> SwarmRouteResult:
        """
        Determines the most qualified agent for a given task or text prompt.
        """
        if preferred_agent and preferred_agent in self.roster:
            return SwarmRouteResult(
                matched_agent=preferred_agent,
                confidence=1.0,
                matched_keywords=["user_preferred"],
                reasoning=f"Explicitly routed to preferred agent '{preferred_agent}'.",
            )

        if isinstance(task_or_prompt, ActionTask):
            # Check explicit task agent first
            if task_or_prompt.target_agent and task_or_prompt.target_agent in self.roster:
                return SwarmRouteResult(
                    matched_agent=task_or_prompt.target_agent,
                    confidence=1.0,
                    matched_keywords=["task_explicit_target"],
                    reasoning=f"Task has pre-assigned target agent '{task_or_prompt.target_agent}'.",
                )
            # Combine payload text fields for content matching
            text_sources = [
                task_or_prompt.action_type,
                task_or_prompt.payload.get("prompt", ""),
                task_or_prompt.payload.get("task_description", ""),
                task_or_prompt.payload.get("goal", ""),
                task_or_prompt.payload.get("name", ""),
                task_or_prompt.plugin_card_path or "",
            ]
            content = " ".join(str(s) for s in text_sources if s).lower()
        else:
            content = str(task_or_prompt).lower()

        scores: Dict[str, int] = {agent: 0 for agent in self.roster}
        matched_kws: Dict[str, List[str]] = {agent: [] for agent in self.roster}

        for agent, meta in self.roster.items():
            keywords = meta.get("keywords", [])
            for kw in keywords:
                # Use word-boundary or substring match
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, content):
                    scores[agent] += 2
                    matched_kws[agent].append(kw)
                elif kw in content:
                    scores[agent] += 1
                    matched_kws[agent].append(kw)

        best_agent = max(scores, key=lambda a: scores[a])
        max_score = scores[best_agent]

        if max_score > 0:
            confidence = min(0.5 + (max_score * 0.1), 0.99)
            kws = matched_kws[best_agent]
            return SwarmRouteResult(
                matched_agent=best_agent,
                confidence=round(confidence, 2),
                matched_keywords=kws,
                reasoning=f"Matched domain keywords [{', '.join(kws)}] with score {max_score}.",
            )

        return SwarmRouteResult(
            matched_agent="gerych_prime",
            confidence=0.5,
            matched_keywords=[],
            reasoning="Defaulted to lead coordinator 'gerych_prime' (no specific domain keywords identified).",
        )


class SwarmExecutionEngine:
    """
    Orchestration Engine executing parallel and sequential multi-agent workflows
    over the AgentActionBus.
    """

    def __init__(
        self,
        action_bus: Any,
        router: Optional[SwarmTaskRouter] = None,
        artifact_store: Optional[Any] = None,
    ):
        self.bus = action_bus
        self.router = router or SwarmTaskRouter()
        self.artifact_store = artifact_store

    async def execute_parallel(
        self,
        tasks: List[ActionTask],
        timeout_seconds: float = 30.0,
        fail_fast: bool = False,
    ) -> SwarmBatchResponse:
        """
        Executes a batch of ActionTasks concurrently across specialized agents.
        """
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        t_start = time.perf_counter()

        await self.bus._publish(
            BusEventType.SWARM_PARALLEL_STARTED,
            task_id=batch_id,
            payload={
                "batch_id": batch_id,
                "total_tasks": len(tasks),
                "fail_fast": fail_fast,
            },
        )

        async def _dispatch_one(task: ActionTask) -> ActionExecutionResponse:
            # Auto-route if target_agent is missing
            if not task.target_agent:
                routing = self.router.route_task(task)
                task.target_agent = routing.matched_agent
                task.routing_metadata = routing.model_dump()
                await self.bus._publish(
                    BusEventType.TASK_ROUTED,
                    task_id=task.task_id,
                    payload={"target_agent": task.target_agent, "routing": routing.model_dump()},
                )
            try:
                return await asyncio.wait_for(self.bus.dispatch_task(task), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                return ActionExecutionResponse(
                    task_id=task.task_id,
                    status=ActionTaskStatus.FAILED,
                    exit_code=124,
                    error_message=f"Task timed out after {timeout_seconds} seconds.",
                )
            except Exception as exc:
                return ActionExecutionResponse(
                    task_id=task.task_id,
                    status=ActionTaskStatus.FAILED,
                    exit_code=1,
                    error_message=str(exc),
                )

        if fail_fast:
            # Gather with immediate return on error
            results: List[ActionExecutionResponse] = []
            pending = [asyncio.create_task(_dispatch_one(t)) for t in tasks]
            try:
                for completed_coro in asyncio.as_completed(pending):
                    res = await completed_coro
                    results.append(res)
                    if res.status in (ActionTaskStatus.FAILED, ActionTaskStatus.REJECTED):
                        for p in pending:
                            p.cancel()
                        break
            except Exception:
                pass
        else:
            coros = [_dispatch_one(t) for t in tasks]
            results = await asyncio.gather(*coros)

        duration_ms = (time.perf_counter() - t_start) * 1000.0
        succeeded = sum(1 for r in results if r.status == ActionTaskStatus.COMPLETED)
        failed = len(results) - succeeded

        await self.bus._publish(
            BusEventType.SWARM_PARALLEL_COMPLETED,
            task_id=batch_id,
            payload={
                "batch_id": batch_id,
                "total_tasks": len(tasks),
                "succeeded": succeeded,
                "failed": failed,
                "duration_ms": duration_ms,
            },
        )

        return SwarmBatchResponse(
            batch_id=batch_id,
            total_tasks=len(tasks),
            succeeded_tasks=succeeded,
            failed_tasks=failed,
            results=list(results),
            total_duration_ms=round(duration_ms, 2),
        )

    async def execute_pipeline(
        self,
        stages: List[ActionTask],
        stop_on_failure: bool = True,
    ) -> SwarmPipelineResponse:
        """
        Executes a sequence of ActionTasks in phased order.
        Each stage receives the output of previous stages.
        """
        pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
        t_start = time.perf_counter()

        await self.bus._publish(
            BusEventType.SWARM_PIPELINE_STARTED,
            task_id=pipeline_id,
            payload={"pipeline_id": pipeline_id, "total_stages": len(stages)},
        )

        results: List[ActionExecutionResponse] = []
        last_output: Optional[Any] = None
        overall_status = ActionTaskStatus.COMPLETED

        for idx, stage in enumerate(stages):
            # Pass prior stage output if available
            if last_output is not None:
                stage.payload["prior_output"] = last_output
                stage.payload["prior_stage_output"] = last_output
                if isinstance(last_output, dict) and "artifact_uri" in last_output:
                    stage.payload["artifact_uri"] = last_output["artifact_uri"]
                    stage.payload["prior_stage_output_uri"] = last_output["artifact_uri"]

            # Auto-route if needed
            if not stage.target_agent:
                routing = self.router.route_task(stage)
                stage.target_agent = routing.matched_agent
                stage.routing_metadata = routing.model_dump()
                await self.bus._publish(
                    BusEventType.TASK_ROUTED,
                    task_id=stage.task_id,
                    payload={"target_agent": stage.target_agent, "routing": routing.model_dump()},
                )

            res = await self.bus.dispatch_task(stage)
            results.append(res)

            if res.status in (ActionTaskStatus.FAILED, ActionTaskStatus.REJECTED):
                overall_status = res.status
                if stop_on_failure:
                    break
            else:
                last_output = res.output

            # Check if artifact store is active and output should be offloaded as an artifact
            if self.artifact_store and (stage.payload.get("store_artifact") or (res.output and len(str(res.output)) > 1024)):
                try:
                    filename = f"stage_{idx}_{stage.action_type or 'artifact'}.json"
                    meta = self.artifact_store.store_json(
                        data=res.output,
                        filename=filename,
                        category="pipeline_stages",
                        task_id=stage.task_id,
                        agent=stage.target_agent,
                    )
                    if isinstance(res.output, dict):
                        res.output["artifact_uri"] = meta.uri
                    await self.bus._publish(
                        BusEventType.ARTIFACT_CREATED,
                        task_id=stage.task_id,
                        payload={
                            "artifact_id": meta.artifact_id,
                            "uri": meta.uri,
                            "filename": meta.filename,
                            "size_bytes": meta.size_bytes,
                            "stage_index": idx,
                        },
                    )
                except Exception as err:
                    logger.warning(f"Failed to offload stage output to artifact store: {err}")

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        await self.bus._publish(
            BusEventType.SWARM_PIPELINE_COMPLETED,
            task_id=pipeline_id,
            payload={
                "pipeline_id": pipeline_id,
                "completed_stages": len(results),
                "total_stages": len(stages),
                "status": overall_status.value,
                "duration_ms": duration_ms,
            },
        )

        return SwarmPipelineResponse(
            pipeline_id=pipeline_id,
            total_stages=len(stages),
            completed_stages=len(results),
            status=overall_status,
            results=results,
            final_output=last_output,
            total_duration_ms=round(duration_ms, 2),
        )

    async def delegate_task(
        self,
        from_agent: str,
        to_agent: str,
        task: ActionTask,
    ) -> ActionExecutionResponse:
        """
        Handles explicit Agent-to-Agent (A2A) task delegation.
        """
        task.delegated_by = from_agent
        task.target_agent = to_agent

        await self.bus._publish(
            BusEventType.TASK_DELEGATED,
            task_id=task.task_id,
            payload={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "delegated_by": from_agent,
                "target_agent": to_agent,
                "task_id": task.task_id,
            },
        )

        return await self.bus.dispatch_task(task)
