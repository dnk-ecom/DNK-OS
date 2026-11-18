# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel_mcp.py"
# purpose: "FastMCP Protocol Server & Tool Registry for DNK OS Microkernel (Tier-0 Standing & Tier-1 Deferred)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
FastMCP Server Adapter for DNK OS Microkernel.
Separates MCP protocol serialization from the core FastMCPKernel logic,
preserving the Narrow-Waist invariant (< 400 LOC for core/kernel.py).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.kernel import FastMCPKernel

logger = logging.getLogger("dnk.core.kernel_mcp")


def create_fastmcp_server(kernel: Optional[FastMCPKernel] = None, name: str = "dnk-kernel") -> Any:
    """
    Creates and configures an MCP server exposing DNK OS Microkernel capabilities
    over standard MCP protocol (STDIO / SSE).
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        logger.warning("mcp package not installed, FastMCP server creation skipped.")
        return None

    if kernel is None:
        from core.kernel import FastMCPKernel
        k = FastMCPKernel()
    else:
        k = kernel

    mcp = FastMCP(name)

    # -------------------------------------------------------------------------
    # Tier-0: Standing Core Tools (Primary Agent Interaction & Navigation)
    # -------------------------------------------------------------------------

    @mcp.tool()
    def node_session_get_context(canvas_id: str, node_id: str, canvas_path: str = "") -> str:
        """Retrieves compiled upstream context wire and ancestor contracts for an isolated node session."""
        res = k.compile_node_session_context(canvas_id, node_id, canvas_path=canvas_path or None)
        return json.dumps(res, ensure_ascii=False)

    @mcp.tool()
    def node_session_crystallize(canvas_id: str, node_id: str, summary: str, artifact_refs_json: str = "[]") -> str:
        """Crystallizes a completed node output into summary contract, preventing context rot."""
        refs = json.loads(artifact_refs_json) if isinstance(artifact_refs_json, str) else artifact_refs_json
        res = k.crystallize_node_session(canvas_id, node_id, summary=summary, artifact_refs=refs)
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
    def get_system_status() -> str:
        """Returns the real-time telemetry and health status of the DNK OS Microkernel."""
        return json.dumps(k.get_system_status(), ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Tier-1: Deferred & Specialized Tools (Actions, Security, Clipboard & Repo)
    # -------------------------------------------------------------------------

    @mcp.tool()
    def dispatch_thought(dsl_text: str, graph_id: str = "graph_default") -> str:
        """Parses ThoughtDSL into a validated ThoughtDAG graph."""
        res = k.parse_thoughts(dsl_text, graph_id=graph_id)
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
    def node_session_post_message(canvas_id: str, node_id: str, role: str, content: str) -> str:
        """Posts a message to the isolated node session thread in SQLite WAL."""
        res = k.post_node_message(canvas_id, node_id, role, content)
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
        """Searches vetted SOTA repositories in catalog.db using bilingual FTS5 expansion and Tier ranking."""
        from core.registry.repo_catalog import search_repos
        results = search_repos(query=query, domain=domain or None, limit=limit)
        return json.dumps(results, ensure_ascii=False)

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
    def audit_knowledge_staleness(directory: str = "docs") -> str:
        """Audits documentation files for dead or stale code file references (Cognition/Devin SOTA)."""
        from core.sentinel.knowledge_staleness_guard import KnowledgeStalenessGuard
        guard = KnowledgeStalenessGuard()
        target = guard.root / directory if directory else None
        report = guard.audit_directory(target_dir=target)
        return json.dumps(report.to_dict(), ensure_ascii=False)

    @mcp.tool()
    def evaluate_adversarial_proposal(
        subject: str, what_this_is: str, problem: str, fix: str, if_we_skip_it: str, skeptic_alt: str = ""
    ) -> str:
        """Runs the 5-Vector Developer Critique Framework before locking an architectural decision."""
        from core.sentinel.adversarial_review_gate import AdversarialReviewGate
        gate = AdversarialReviewGate()
        res = gate.evaluate_proposal(
            subject=subject,
            what_this_is=what_this_is,
            problem=problem,
            fix=fix,
            if_we_skip_it=if_we_skip_it,
            skeptic_alt=skeptic_alt,
        )
        return json.dumps(res.to_dict(), ensure_ascii=False)

    @mcp.tool()
    def media_cut_silence(
        words_json: str, total_duration_ms: int, min_silence_ms: int = 400, padding_ms: int = 70
    ) -> str:
        """Detects dead-air pauses and generates jump-cut interval plan and FFmpeg filters for short-form retention."""
        from services.dnk_media.src.service import cut_silence
        words = json.loads(words_json) if isinstance(words_json, str) else words_json
        plan = cut_silence(words=words, total_duration_ms=total_duration_ms, min_silence_ms=min_silence_ms, padding_ms=padding_ms)
        return json.dumps(plan.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def media_smart_reframe(
        original_width: int = 1920, original_height: int = 1080, duration_ms: int = 5000
    ) -> str:
        """Calculates dynamic 9:16 vertical crop coordinates with smooth speaker face centering."""
        from services.dnk_media.src.service import reframe_smart
        plan = reframe_smart(original_width=original_width, original_height=original_height, duration_ms=duration_ms)
        return json.dumps(plan.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def media_kinetic_subtitles(
        transcript: str, total_duration_ms: int = 0, style_preset: str = "hormozi_bold"
    ) -> str:
        """Generates word-level Hormozi kinetic subtitles (ASS and SRT) with emoji triggers."""
        from services.dnk_media.src.service import generate_kinetic_subtitles
        track = generate_kinetic_subtitles(
            transcript=transcript, total_duration_ms=total_duration_ms if total_duration_ms > 0 else None, style_preset=style_preset
        )
        return json.dumps(track.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def media_sound_design(video_duration_s: float, music_preset: str = "electronic_pulse") -> str:
        """Composes automatic audio ducking keyframes and synchronous SFX cues."""
        from services.dnk_media.src.service import compose_sound_design
        from services.dnk_media.src.sound_design import DuckingSettings
        plan = compose_sound_design(
            video_duration_s=video_duration_s,
            custom_settings=DuckingSettings(music_preset=music_preset)
        )
        return json.dumps(plan.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def media_compose_video_9_16(
        transcript: str,
        source_video_path: str = "",
        duration_ms: int = 0,
        style_preset: str = "hormozi_bold",
        output_path: str = "",
        dry_run: bool = True
    ) -> str:
        """Composes 9:16 vertical video combining kinetic subtitles, smart reframing, dead-air cuts, and audio."""
        from services.dnk_media.src.service import compose_video_9_16
        res = compose_video_9_16(
            transcript=transcript,
            source_video_path=source_video_path or None,
            duration_ms=duration_ms if duration_ms > 0 else None,
            style_preset=style_preset,
            output_path=output_path or None,
            dry_run=dry_run
        )
        return json.dumps(res.model_dump(), ensure_ascii=False)

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
                return json.dumps({"success": False, "error": "Spec must be a valid JSON or YAML mapping"}, ensure_ascii=False)
            spec = BrandTokensSpec.model_validate(data)
            res = DesignTokenCompiler.compile_all(spec)
            return json.dumps({"success": True, "result": res.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception("compile_brand_design_tokens failed")
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
            logger.exception("lint_brand_design_tokens failed")
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
            logger.exception("extract_brand_design_tokens failed")
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def distill_brand_design_system(
        donor_path: str,
        brand_name: str = "DNK Sovereign Brand",
        target_output_dir: str = "",
        target_theme_dir: str = "",
    ) -> str:
        """
        Coordinates the 5-stage Design System Swarm to distill, calibrate 60-30-10 CRO,
        audit WCAG contrast, and physically emit multi-target design tokens from any donor theme or asset directory.
        """
        from core.orchestrator.design_system_runner import DesignSystemSwarmRunner, DesignSystemBrief

        try:
            runner = DesignSystemSwarmRunner()
            brief = DesignSystemBrief(
                donor_path=donor_path,
                brand_name=brand_name,
                target_output_dir=target_output_dir or None,
                target_theme_dir=target_theme_dir or None,
            )
            res = runner.execute_turnkey_distillation(brief)
            return json.dumps({"success": True, "result": res.model_dump()}, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception("distill_brand_design_system failed")
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
            logger.exception("get_client_tickets failed")
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
            logger.exception("resolve_client_ticket failed")
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
            logger.exception("get_cockpit_status failed")
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
            logger.exception("client_success_get_inbox failed")
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
            logger.exception("client_success_dispatch_to_builder failed")
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def distribution_check_compliance(text: str, is_promotional: bool = False) -> str:
        """Validates marketing copy against brand guidelines, banned words, legal claims, and FTC rules."""
        from services.dnk_distribution.src.service import check_compliance
        report = check_compliance(text=text, is_promotional=is_promotional)
        return json.dumps(report.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def distribution_evaluate_rlsf(
        publication_id: str,
        views: int,
        retention_rate_3s: float,
        completion_rate: float,
        shares: int = 0,
        likes: int = 0,
        comments: int = 0,
        hook_type: str = ""
    ) -> str:
        """Computes RLSF multi-objective social reward signals and assigns performance tier."""
        from services.dnk_distribution.src.service import evaluate_social_metrics
        from services.dnk_distribution.src.social_feedback import SocialMetrics
        metrics = SocialMetrics(
            publication_id=publication_id,
            views=views,
            retention_rate_3s=retention_rate_3s,
            completion_rate=completion_rate,
            shares=shares,
            likes=likes,
            comments=comments,
        )
        report = evaluate_social_metrics(metrics=metrics, hook_type=hook_type or None)
        return json.dumps(report.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def distribution_mine_themes(comments_json: str) -> str:
        """Mines customer comments to extract objections, buying intents, and copy angles."""
        from services.dnk_distribution.src.service import mine_audience_themes
        from services.dnk_distribution.src.theme_miner import CommentItem
        raw_items = json.loads(comments_json) if isinstance(comments_json, str) else comments_json
        parsed = [CommentItem(**c) for c in raw_items]
        res = mine_audience_themes(parsed)
        return json.dumps(res.model_dump(), ensure_ascii=False)

    # --- DSH Superagent Assimilated Tools (DEC-151) ---
    @mcp.tool()
    def mandate_validate_scope(allowed_paths_json: str, negative_scope_json: str, target_path: str) -> str:
        """Validates if a target path is allowed under Mandate scope boundaries (DSH / DEC-151)."""
        from core.domain.mandate_contracts import MandateScope
        allowed = json.loads(allowed_paths_json) if isinstance(allowed_paths_json, str) else allowed_paths_json
        neg = json.loads(negative_scope_json) if isinstance(negative_scope_json, str) else negative_scope_json
        scope = MandateScope(allowed_paths=allowed, negative_scope=neg)
        is_allowed = scope.is_path_allowed(target_path)
        return json.dumps({"target_path": target_path, "is_allowed": is_allowed}, ensure_ascii=False)

    @mcp.tool()
    def command_run_adaptive(command: str, timeout_foreground: float = 5.0) -> str:
        """Executes a command with 5-second foreground shift to background job if taking longer (DEC-151)."""
        import asyncio
        from core.action_bus.command_runner import CommandRunner
        runner = CommandRunner()
        result = asyncio.run(runner.run_command_adaptive(command=command, timeout_foreground=timeout_foreground))
        return json.dumps(result.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def outbox_enqueue_message(destination_channel: str, payload_json: str, idempotency_key: str = "") -> str:
        """Enqueues an outbox message with deterministic receipt before transmission (DSH / DEC-151)."""
        from core.outbox.service import TransactionalOutbox
        outbox = TransactionalOutbox()
        raw_payload = json.loads(payload_json) if payload_json.startswith("{") or payload_json.startswith("[") else payload_json
        msg = outbox.enqueue(
            destination_channel=destination_channel,
            payload=raw_payload,
            idempotency_key=idempotency_key or None
        )
        return json.dumps(msg.model_dump(), ensure_ascii=False)

    @mcp.tool()
    def outbox_get_receipt(receipt_id: str) -> str:
        """Retrieves outbox delivery status and receipt metadata by receipt ID (DEC-151)."""
        from core.outbox.service import TransactionalOutbox
        outbox = TransactionalOutbox()
        msg = outbox.get_receipt(receipt_id=receipt_id)
        if not msg:
            return json.dumps({"found": False, "receipt_id": receipt_id})
        return json.dumps({"found": True, "message": msg.model_dump()}, ensure_ascii=False)

    @mcp.tool()
    def google_vertex_status() -> str:
        """Returns the active Google Cloud Vertex AI account, project, ADC token health, and models."""
        from scripts.system.google_agent_gateway import GoogleAuthManager, GeminiPayloadTranslator
        token = GoogleAuthManager.get_token()
        data = {
            "active_account": GoogleAuthManager.get_active_account(),
            "active_project": GoogleAuthManager.get_active_project(),
            "adc_token_valid": bool(token and token.startswith("ya29.")),
            "supported_models": GeminiPayloadTranslator.SUPPORTED_MODELS,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @mcp.tool()
    def repo_assimilate_sota(repo_url: str, target_module: str = "core") -> str:
        """Executes the Autonomous SOTA Ingestion & Distillation Pipeline (Spec, EGM Rubric, PSOD Task)."""
        from services.dnk_git_research.src.sota_pipeline import SOTAPipelineRunner
        runner = SOTAPipelineRunner()
        output = runner.run(repo_input=repo_url, target_module=target_module)
        return json.dumps(output.model_dump(), ensure_ascii=False, indent=2)

    return mcp
