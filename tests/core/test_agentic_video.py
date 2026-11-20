# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_agentic_video.py"
# purpose: "Test suite for DNK OS Agentic Video Intelligence, YouTube transcript extraction, and insight distillation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from core.adapters.dnk_agentic_video_adapter import (
    DNKAgenticVideoAdapter,
    ProcessingMode,
    extract_youtube_video_id,
    fetch_youtube_transcript,
)
from core.kernel import FastMCPKernel


def test_extract_youtube_video_id():
    """Verify robust extraction of 11-char YouTube ID across common formats."""
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_fetch_youtube_transcript():
    """Verify structured transcript extraction with timestamps and text."""
    res = fetch_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert res.video_id == "dQw4w9WgXcQ"
    assert len(res.segments) > 0
    assert len(res.full_text) > 0
    assert len(res.timestamped_text) > 0
    assert res.segments[0].duration >= 0.0


@pytest.mark.asyncio
async def test_agentic_video_adapter_analysis():
    """Verify Gemini Agentic Video mode consumes <= 850 tokens and returns chapters and moments."""
    adapter = DNKAgenticVideoAdapter(mock_mode=True)
    res = await adapter.analyze_video(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        prompt="Analyze architectural highlights",
        mode=ProcessingMode.AGENTIC,
    )
    assert res.processing_mode == ProcessingMode.AGENTIC
    assert res.tokens_consumed <= 850
    assert len(res.chapters) >= 3
    assert len(res.moments) >= 2


@pytest.mark.asyncio
async def test_extract_actionable_insights():
    """Verify end-to-end extraction of core thesis, key ideas, and actionable takeaways."""
    adapter = DNKAgenticVideoAdapter(mock_mode=True)
    insights = await adapter.extract_actionable_insights(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        focus_query="Architectural paradigms",
    )
    assert insights["video_id"] == "dQw4w9WgXcQ"
    assert "core_thesis" in insights
    assert len(insights["key_ideas"]) >= 3
    assert len(insights["actionable_takeaways"]) >= 3
    assert len(insights["chapters"]) >= 3
    assert len(insights["moments"]) >= 2
    assert insights["tokens_consumed"] <= 850


def test_kernel_system_status_video_subsystem():
    """Verify FastMCPKernel reports agentic_video_intelligence as ACTIVE in telemetry."""
    kernel = FastMCPKernel()
    status = kernel.get_system_status()
    assert status["sota_subsystems"]["agentic_video_intelligence"] == "ACTIVE"


@pytest.mark.asyncio
async def test_video_sota_research_bridge_benchmark():
    """Verify background agent bridge benchmarks video diamonds against corporate leaders as of today."""
    from core.orchestrator.video_sota_research_bridge import VideoSotaResearchBridge
    bridge = VideoSotaResearchBridge()
    
    # 1. Date anchor check
    today = bridge.get_current_anchor_date()
    assert len(today) == 10  # YYYY-MM-DD
    
    # 2. Benchmark run
    res = await bridge.benchmark_video_diamond(
        topic="Multi-Repo Agentic Worktrees & Home Repo Routing",
        video_diamond="Home Repo as single agent entrypoint with git worktrees for parallel agents",
        video_source_url="https://youtu.be/hWe-j78vNpc",
    )
    assert res.as_of_date == today
    assert len(res.corporate_benchmarks) >= 3
    corps = [c.company_name for c in res.corporate_benchmarks]
    assert any("Cursor" in c or "Devin" in c for c in corps)
    assert any("Anthropic" in c for c in corps)
    assert "winning_synthesis" in res.model_dump()
    assert "dnk_sovereign_adaptation" in res.model_dump()
    assert res.action_spec_psod["oracle"] != ""
    assert res.triage_verdict in {"ADOPT", "ADAPT", "REJECT", "QUARANTINE"}
