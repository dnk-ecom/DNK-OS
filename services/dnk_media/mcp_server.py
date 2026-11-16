# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/mcp_server.py"
# purpose: "FastMCP Server for dnk_media Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from services.dnk_media.src.service import (
    cut_silence,
    reframe_smart,
    generate_kinetic_subtitles,
    compose_sound_design,
    process_data,
)

mcp = FastMCP("dnk_media")


@mcp.tool()
def media_cut_silence(
    words: List[Dict[str, Any]],
    total_duration_ms: int,
    min_silence_ms: int = 400,
    padding_ms: int = 70
) -> Dict[str, Any]:
    """Detect dead air gaps and return jump-cut interval plan and FFmpeg select filters."""
    plan = cut_silence(words, total_duration_ms, min_silence_ms, padding_ms)
    return plan.model_dump()


@mcp.tool()
def media_smart_reframe(
    original_width: int = 1920,
    original_height: int = 1080,
    duration_ms: int = 5000
) -> Dict[str, Any]:
    """Calculate 9:16 vertical crop with smooth speaker face centering."""
    plan = reframe_smart(original_width, original_height, None, duration_ms)
    return plan.model_dump()


@mcp.tool()
def media_kinetic_subtitles(
    transcript: str,
    total_duration_ms: Optional[int] = None,
    style_preset: str = "hormozi_bold",
    words_per_phrase: int = 2
) -> Dict[str, Any]:
    """Generate word-level kinetic subtitles in Hormozi style (ASS and SRT)."""
    track = generate_kinetic_subtitles(transcript, total_duration_ms, style_preset, words_per_phrase)
    return track.model_dump()


@mcp.tool()
def media_sound_design(
    video_duration_s: float,
    music_preset: str = "electronic_pulse"
) -> Dict[str, Any]:
    """Compose audio ducking keyframes and synchronous SFX timeline."""
    from services.dnk_media.src.sound_design import DuckingSettings
    plan = compose_sound_design(video_duration_s, custom_settings=DuckingSettings(music_preset=music_preset))
    return plan.model_dump()


@mcp.tool()
def execute(query: str) -> str:
    """Fallback query execution."""
    return process_data(query)


if __name__ == "__main__":
    mcp.run()
