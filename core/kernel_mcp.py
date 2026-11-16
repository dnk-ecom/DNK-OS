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

    return mcp
