# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel_tools.py"
# purpose: "FastMCP Tool Registry and Dynamic Decoupled Tool Definitions for DNK OS Microkernel Host."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import logging
from typing import Any

logger = logging.getLogger("dnk.core.kernel_tools")


def register_kernel_tools(mcp: Any, k: Any) -> None:
    """
    Registers the canonical 19 FastMCP tools onto the FastMCP server instance,
    binding them to the underlying FastMCPKernel (k).
    """

    @mcp.tool()
    def dispatch_thought(dsl_text: str, graph_id: str = "graph_default") -> str:
        """Parses ThoughtDSL into a validated ThoughtDAG graph."""
        res = k.parse_thoughts(dsl_text, graph_id=graph_id)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    async def execute_action(action_type: str, payload_json: str = "{}", requester: str = "vibe_coder") -> str:
        """Dispatches an action through the Agent Action Bus with HITL safety gate."""
        payload = json.loads(payload_json) if isinstance(payload_json, str) else payload_json
        res = await k.dispatch_action(action_type, payload, requester=requester)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    async def query_memory(topic: str, limit: int = 5) -> str:
        """Queries SCONES cognitive memory for past observations and solutions."""
        res = await k.query_memory(topic, limit=limit)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    async def record_observation(topic: str, observation: str, source: str = "agent") -> str:
        """Records a new learned observation or calibration into SCONES memory."""
        res = await k.record_observation(topic, observation, source=source)
        return json.dumps({"recorded": True, "id": res}, ensure_ascii=False)

    @mcp.tool()
    async def request_approval(task_id: str, approved: bool, note: str = "") -> str:
        """Resolves a Human-in-the-Loop approval gate for a critical action."""
        task = await k.bus.resolve_approval(task_id, approved=approved, approved_by="Maxim", note=note)
        status_val = task.status.value if hasattr(task.status, "value") else str(task.status)
        return json.dumps({"task_id": task_id, "status": status_val, "note": note}, ensure_ascii=False)

    @mcp.tool()
    def get_system_status() -> str:
        """Returns the real-time telemetry and health status of the DNK OS Microkernel."""
        return json.dumps(k.get_system_status(), ensure_ascii=False)

    @mcp.tool()
    def inspect_code_map(file_path: str) -> str:
        """Returns an AST symbol map of classes, functions, and line numbers for a Python file."""
        from core.code_map import generate_code_map_from_file

        code_map = generate_code_map_from_file(file_path)
        return code_map.to_compact_summary()

    @mcp.tool()
    def prune_output(raw_output: str, max_lines: int = 120) -> str:
        """Prunes verbose terminal or test output to prevent token window overflow."""
        from core.pruner import prune_terminal_output

        return prune_terminal_output(raw_output, max_lines=max_lines)

    @mcp.tool()
    def search_clipboard(
        query: str = "", kind: str = "", collection: str = "", tag: str = "", favorite_only: bool = False, limit: int = 10
    ) -> str:
        """Searches native ClipBoardLine SQLite library for project clips, notes, URLs, or texts."""
        from core.adapters.dnk_clipboard_adapter import DNKClipboardAdapter
        items = DNKClipboardAdapter().search_items(
            query=query or None, kind=kind or None, collection=collection or None, tag=tag or None, favorite_only=favorite_only, limit=limit
        )
        return json.dumps(items, ensure_ascii=False)

    @mcp.tool()
    def get_clipboard_projects() -> str:
        """Lists all project collections (folders) and tags stored in ClipBoardLine."""
        from core.adapters.dnk_clipboard_adapter import DNKClipboardAdapter
        ad = DNKClipboardAdapter()
        return json.dumps({"status": ad.get_database_status(), "collections": ad.list_collections(), "tags": ad.list_tags()}, ensure_ascii=False)

    @mcp.tool()
    def get_clipboard_screenshots(limit: int = 5, ocr_filter: str = "") -> str:
        """Retrieves recent macOS screenshots from ClipBoardLine with Apple Vision OCR recognized text."""
        from core.adapters.dnk_clipboard_adapter import DNKClipboardAdapter
        return json.dumps(DNKClipboardAdapter().get_recent_screenshots(limit=limit, ocr_filter=ocr_filter or None), ensure_ascii=False)

    @mcp.tool()
    def node_session_get_context(canvas_id: str, node_id: str, canvas_path: str = "") -> str:
        """Retrieves compiled upstream context wire and ancestor contracts for an isolated node session."""
        res = k.compile_node_session_context(canvas_id, node_id, canvas_path=canvas_path or None)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def node_session_post_message(canvas_id: str, node_id: str, role: str, content: str) -> str:
        """Posts a message to the isolated node session thread in SQLite WAL."""
        res = k.post_node_message(canvas_id, node_id, role, content)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def node_session_crystallize(canvas_id: str, node_id: str, summary: str, artifact_refs_json: str = "[]") -> str:
        """Crystallizes a completed node output into summary contract, preventing context rot."""
        refs = json.loads(artifact_refs_json) if isinstance(artifact_refs_json, str) else artifact_refs_json
        res = k.crystallize_node_session(canvas_id, node_id, summary=summary, artifact_refs=refs)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def fan_in_validate_and_aggregate(outputs_json: str, synthesis_instructions: str = "") -> str:
        """Validates parallel subagent outputs across 4 gates (SyntaxAST, BoundaryScope, ExitCode, Grounding) and merges."""
        outputs = json.loads(outputs_json) if isinstance(outputs_json, str) else outputs_json
        res = k.aggregate_branch_results(outputs, synthesis_instructions=synthesis_instructions)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def quarantine_get_status(agent_id: str) -> str:
        """Checks circuit breaker and quarantine status of an agent."""
        res = k.get_quarantine_record(agent_id)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def quarantine_release_agent(agent_id: str, approver: str = "founder") -> str:
        """Manually releases a quarantined agent after review."""
        k.quarantine.release_agent(agent_id, approver=approver)
        return json.dumps({"agent_id": agent_id, "status": "released", "approver": approver}, ensure_ascii=False)

    @mcp.tool()
    def search_repo_catalog(query: str, domain: str = "", limit: int = 10) -> str:
        """Searches 1,663 vetted SOTA repositories in catalog.db using bilingual (UA/EN) FTS5 expansion and Tier ranking."""
        from core.registry.repo_catalog import search_repos
        results = search_repos(query=query, domain=domain or None, limit=limit)
        return json.dumps(results, ensure_ascii=False)

    @mcp.tool()
    def get_repo_progressive_index(domain: str = "") -> str:
        """
        Two-Level Progressive Disclosure Index (LOD Navigation) for 1,663 repositories:
        - domain='' or 'all': Returns Level 0 overview of 3 sovereign pillars (Shopify, Media, Core) <= 1,000 tokens.
        - domain='shopify'|'media'|'core': Returns Level 1 category slice with Tier 1/2 blueprints <= 1,500 tokens.
        Eliminates context rot and preserves prompt diet.
        """
        from core.registry.repo_catalog import get_repo_progressive_index as get_index
        res = get_index(domain=domain or None)
        return json.dumps(res, ensure_ascii=False, indent=2)

    @mcp.tool()
    def get_repo_reuse_brief(task_description: str, force_research: bool = False, live: bool = False) -> str:
        """Gated JIT prior-art search before writing code: returns ADOPT / ADAPT / CLEAN_ROOM / BUILD recommendations."""
        from services.dnk_git_research.src.reuse_brief import ReuseBriefService, format_brief_text
        svc = ReuseBriefService(live=live)
        brief = svc.build(text=task_description, force=force_research)
        return json.dumps({
            "mode": brief.mode.value,
            "summary": brief.summary,
            "formatted_text": format_brief_text(brief),
            "fingerprint": brief.fingerprint,
            "needs": [n.model_dump() for n in brief.needs]
        }, ensure_ascii=False)

    @mcp.tool()
    async def record_error_reflexion(
        tool_or_command: str, symptom: str, root_cause: str, solution: str, source: str = "agent"
    ) -> str:
        """Records a structured error reflexion into SCONES memory to prevent repeating mistakes."""
        topic = f"error_solution:{tool_or_command.lower().strip()}"
        payload = {
            "tool_or_command": tool_or_command,
            "symptom": symptom,
            "root_cause": root_cause,
            "solution": solution,
            "source": source,
        }
        res_id = await k.record_observation(topic, json.dumps(payload, ensure_ascii=False), source=source)
        return json.dumps({"recorded": True, "id": res_id, "topic": topic}, ensure_ascii=False)

    @mcp.tool()
    async def query_error_solutions(query: str, limit: int = 3) -> str:
        """Queries past reflexions and known solutions from SCONES memory for an error or tool failure."""
        topic = f"error_solution:{query.lower().strip()}" if not query.startswith("error_solution:") else query.lower().strip()
        memories = await k.query_memory(topic, limit=limit)
        return json.dumps(memories, ensure_ascii=False)

    @mcp.tool()
    def execute_code_mode(code: str, timeout_sec: int = 30) -> str:
        """
        Executes a self-contained Python script in-memory with access to the DNK OS Microkernel (k)
        and standard libraries (CE-MCP / Anthropic Code Mode). Eliminates multi-turn LLM latency.
        """
        import io
        import sys
        import traceback

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        local_env = {
            "kernel": k,
            "k": k,
            "json": json,
            "result": None,
        }

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            exec(code, local_env, local_env)
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            res_val = local_env.get("result")
            return json.dumps(
                {
                    "success": True,
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                    "result": res_val,
                    "exit_code": 0,
                },
                ensure_ascii=False,
            )
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return json.dumps(
                {
                    "success": False,
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue() + "\n" + traceback.format_exc(),
                    "error": str(e),
                    "exit_code": 1,
                },
                ensure_ascii=False,
            )

    @mcp.tool()
    def compact_session_context(session_id: str, max_tokens: int = 15000) -> str:
        """
        Applies Prime Agent RLM Smart Compaction to an active node or agent session.
        Synthesizes older dialogue into an immutable state contract, pruning context bloat.
        """
        router = getattr(k, "session_router", None)
        if router is None:
            from core.canvas.session_router import SpatialCanvasSessionRouter
            router = SpatialCanvasSessionRouter()

        res = router.compact_thread(session_id, max_tokens=max_tokens)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    async def video_extract_insights(
        video_url: str,
        focus_query: str = "Key ideas, architectural insights, and actionable thoughts",
    ) -> str:
        """
        Extracts high-signal ideas, architectural concepts, semantic chapters,
        and timestamped moments from a video (YouTube or URI) using Agentic Exploration.
        """
        from core.adapters.dnk_agentic_video_adapter import DNKAgenticVideoAdapter
        adapter = DNKAgenticVideoAdapter()
        res = await adapter.extract_actionable_insights(video_url, focus_query=focus_query)
        return json.dumps(res, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def video_benchmark_sota(
        topic: str,
        video_diamond: str,
        video_source_url: str = "",
    ) -> str:
        """
        Coordinates background agent research to benchmark a video-extracted diamond against
        active SOTA corporate leaders (Stripe, Shopify, Figma, Linear, Cursor, Cognition)
        as of today's date, generating an actionable DNK OS physical adaptation spec.
        """
        from core.orchestrator.video_sota_research_bridge import VideoSotaResearchBridge
        bridge = VideoSotaResearchBridge()
        res = await bridge.benchmark_video_diamond(
            topic=topic,
            video_diamond=video_diamond,
            video_source_url=video_source_url,
        )
        return json.dumps(res.model_dump(), ensure_ascii=False, indent=2)

    @mcp.tool()
    def compile_brand_design_tokens(spec_json_or_yaml: str) -> str:
        """
        Compiles a W3C DTCG Design Token specification into multi-target outputs:
        Shopify Theme CSS (:root & RGB channels), settings_schema.json, Tailwind v4 @theme,
        HyperFrames Media/Motion tokens, and DESIGN.md brand documentation.
        """
        import yaml
        from core.design_system import BrandTokensSpec, DesignTokenCompiler

        try:
            data = yaml.safe_load(spec_json_or_yaml)
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Spec must be a valid YAML/JSON mapping"}, ensure_ascii=False)
            spec = BrandTokensSpec.model_validate(data)
            res = DesignTokenCompiler.compile_all(spec)
            return json.dumps({"success": True, "result": res.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def lint_brand_design_tokens(spec_json_or_yaml: str) -> str:
        """
        Deterministically lints a Brand Token specification against WCAG 2.2 AA / APCA
        contrast minimums, 8pt spatial grid, 16px body font floor, and 60-30-10 CRO color allocation.
        """
        import yaml
        from core.design_system import BrandTokensSpec, DesignTokenLinter

        try:
            data = yaml.safe_load(spec_json_or_yaml)
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Spec must be a valid YAML/JSON mapping"}, ensure_ascii=False)
            spec = BrandTokensSpec.model_validate(data)
            report = DesignTokenLinter.lint_spec(spec)
            return json.dumps({"success": True, "report": report.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def extract_brand_design_tokens(source_type: str, raw_content: str, brand_name: str = "Client Brand") -> str:
        """
        Extracts structured DTCG Brand Tokens from raw sources ('shopify_settings' or 'css').
        """
        import json as pyjson
        from core.design_system import DesignTokenExtractor

        try:
            if source_type == "shopify_settings":
                settings_dict = pyjson.loads(raw_content)
                spec = DesignTokenExtractor.from_shopify_settings(settings_dict, brand_name=brand_name)
            else:
                spec = DesignTokenExtractor.from_css_string(raw_content, brand_name=brand_name)

            return json.dumps({"success": True, "spec": spec.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_client_tickets(deal_id: str = "deal_noku_2026", status: str = "all") -> str:
        """
        Retrieves real-time in-context review tickets and comments left by the client
        directly on the Shopify storefront via the In-Context Sensor (DOM elements, sections, selectors).
        """
        from core.client_cockpit.engine import ClientCockpitEngine
        try:
            engine = ClientCockpitEngine()
            tickets = engine.get_tickets(deal_id=deal_id, status=None if status == "all" else status)
            return json.dumps({"deal_id": deal_id, "tickets": tickets, "count": len(tickets)}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def resolve_client_ticket(deal_id: str, ticket_id: str, resolution_note: str = "", status: str = "resolved") -> str:
        """
        Resolves or updates an in-context client ticket from the Shopify storefront,
        recording the agent's code fix and notifying the client cockpit.
        """
        from core.client_cockpit.engine import ClientCockpitEngine
        try:
            engine = ClientCockpitEngine()
            ticket = engine.resolve_ticket(deal_id=deal_id, ticket_id=ticket_id, resolution_note=resolution_note, status=status)
            return json.dumps({"success": True, "ticket": ticket}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_cockpit_status(deal_id: str = "deal_noku_2026") -> str:
        """
        Returns full client cockpit status: 6-stage roadmap progress, revision quota usage,
        active tickets, and deliverable artifacts for an e-commerce client deal.
        """
        from core.client_cockpit.engine import ClientCockpitEngine
        try:
            engine = ClientCockpitEngine()
            state = engine.get_cockpit_state(deal_id=deal_id)
            return json.dumps({"deal_id": deal_id, "state": state}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def client_success_get_inbox(deal_id: str = "deal_noku_2026") -> str:
        """
        Queries the Client Success Agent inbox for incoming visual area review tickets,
        bounding box coordinates, client instructions, and automated Scope Guard triage.
        """
        from core.client_cockpit.engine import ClientCockpitEngine
        try:
            engine = ClientCockpitEngine()
            tickets = engine.get_tickets(deal_id=deal_id, status="open")
            return json.dumps({
                "deal_id": deal_id,
                "open_tickets_count": len(tickets),
                "inbox": tickets,
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def client_success_dispatch_to_builder(deal_id: str, ticket_id: str, builder: str = "denchik") -> str:
        """
        Packages an in-context visual review ticket into an atomic builder task for Denchik / Shopify Theme Craftsman.
        """
        from core.client_cockpit.engine import ClientCockpitEngine
        try:
            engine = ClientCockpitEngine()
            state = engine.get_cockpit_state(deal_id=deal_id)
            ticket = next((t for t in state.get("tickets", []) if t["ticket_id"] == ticket_id), None)
            if not ticket:
                return json.dumps({"success": False, "error": f"Ticket {ticket_id} not found"}, ensure_ascii=False)

            task_dna = {
                "builder": builder,
                "deal_id": deal_id,
                "ticket_id": ticket_id,
                "instruction": ticket["comment"],
                "target_selector": ticket.get("selector"),
                "section_id": ticket.get("section_id"),
                "block_id": ticket.get("block_id"),
                "bounding_box": ticket.get("bounding_box"),
                "status": "dispatched",
            }
            engine.resolve_ticket(deal_id, ticket_id, resolution_note=f"Dispatched to {builder}", status="in_progress")
            return json.dumps({"success": True, "task_dna": task_dna}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def client_success_generate_remediation(
        deal_id: str,
        ticket_id: str,
        target_file: str,
        new_content: str,
        explanation_uk: str = ""
    ) -> str:
        """
        Denchik generates a unified git diff remediation proposal for an in-context visual review ticket,
        ready for Maxim's 1-click Human-in-the-Loop approval.
        """
        from core.client_success.remediation_engine import RemediationEngine
        try:
            rem_engine = RemediationEngine()
            proposal = rem_engine.synthesize_remediation(
                deal_id=deal_id,
                ticket_id=ticket_id,
                target_file=target_file,
                new_content=new_content,
                explanation_uk=explanation_uk,
            )
            return json.dumps({"success": True, "proposal": proposal.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def client_success_apply_remediation(
        proposal_id: str,
        new_content: str,
        approver: str = "maksym"
    ) -> str:
        """
        Applies an approved visual review remediation patch to disk and resolves the ticket in Cockpit DB.
        """
        from core.client_success.remediation_engine import RemediationEngine
        try:
            rem_engine = RemediationEngine()
            res = rem_engine.apply_remediation(
                proposal_id=proposal_id,
                new_content=new_content,
                approver=approver,
            )
            return json.dumps(res, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
