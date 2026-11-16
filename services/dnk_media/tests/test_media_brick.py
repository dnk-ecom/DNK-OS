# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/tests/test_media_brick.py"
# purpose: "Comprehensive Unit Tests for dnk_media Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from services.dnk_media.src.service import (
    cut_silence,
    reframe_smart,
    generate_kinetic_subtitles,
    compose_sound_design,
    process_data,
)
from services.dnk_media.src.silence_cutting import SilenceCuttingEngine
from services.dnk_media.src.smart_reframing import SmartReframingEngine, SpeakerTrackingPoint, BoundingBox
from services.dnk_media.src.kinetic_subtitles import KineticSubtitlesEngine
from services.dnk_media.src.sound_design import SoundDesignEngine, DuckingSettings


def test_process_data_fallback():
    assert process_data("ping") == "Processed: ping"


def test_silence_cutting_detects_dead_air():
    words = [
        {"start_ms": 600, "end_ms": 1100, "word": "Stop"},
        {"start_ms": 2200, "end_ms": 2800, "word": "wasting"},
        {"start_ms": 2900, "end_ms": 3400, "word": "money"},
    ]
    total_duration_ms = 4500
    plan = cut_silence(words, total_duration_ms, min_silence_ms=400, padding_ms=70)

    assert plan.original_duration_ms == 4500
    assert plan.saved_duration_ms > 0
    assert plan.cut_duration_ms < plan.original_duration_ms
    assert plan.silence_count >= 2  # Leading silence + inter-word gap
    assert "between(t," in plan.ffmpeg_select_filter
    assert plan.retention_boost_estimate_pct > 0.0


def test_smart_reframing_9_16_smoothing():
    tracking = [
        SpeakerTrackingPoint(
            timestamp_ms=0,
            speaker_bbox=BoundingBox(x=0.2, y=0.1, width=0.2, height=0.3),
            is_speaking=True
        ),
        SpeakerTrackingPoint(
            timestamp_ms=500,
            speaker_bbox=BoundingBox(x=0.7, y=0.1, width=0.2, height=0.3),
            is_speaking=True
        ),
    ]
    plan = reframe_smart(1920, 1080, tracking_points=tracking, duration_ms=2000)

    assert plan.original_width == 1920
    assert plan.original_height == 1080
    assert plan.target_width == 1080
    assert plan.target_height == 1920
    assert len(plan.keyframes) == 2
    assert "crop=" in plan.ffmpeg_filter
    assert "scale=1080:1920" in plan.ffmpeg_filter


def test_kinetic_subtitles_hormozi_formatting():
    transcript = "Stop making this huge mistake with your money right now"
    track = generate_kinetic_subtitles(transcript, total_duration_ms=4000, style_preset="hormozi_bold")

    assert track.words_count == 10
    assert track.duration_ms == 4000
    assert len(track.phrases) > 0
    assert len(track.words) == 10

    # Strong keywords detection
    strong_words = [w for w in track.words if w.emphasis == "STRONG"]
    assert len(strong_words) >= 3  # stop, huge, mistake, money

    # Emoji trigger detection
    emojis = [w.emoji for w in track.words if w.emoji is not None]
    assert any("🛑" in e or "💰" in e or "💵" in e for e in emojis)

    # Valid export verification
    assert "-->" in track.srt_content
    assert "[Script Info]" in track.ass_content
    assert "Style: Hormozi" in track.ass_content


def test_sound_design_ducking_and_sfx():
    speech = [
        {"start_ms": 500, "end_ms": 2500, "text": "Hook line"},
        {"start_ms": 4000, "end_ms": 7000, "text": "Explanation"},
    ]
    plan = compose_sound_design(video_duration_s=10.0, speech_segments=speech)

    assert plan.video_duration_s == 10.0
    assert len(plan.ducking_keyframes) >= 6
    assert len(plan.sfx_timeline) >= 2
    # Verify intro hook SFX placed
    assert plan.sfx_timeline[0].trigger_source == "hook"
    assert plan.speech_clarity_score >= 90.0
    assert plan.audio_energy_score >= 70.0


def test_fastmcp_media_tools():
    from services.dnk_media.mcp_server import (
        media_cut_silence,
        media_smart_reframe,
        media_kinetic_subtitles,
        media_sound_design,
    )

    # Test silence cut tool
    res_silence = media_cut_silence(
        words=[{"start_ms": 500, "end_ms": 1500, "word": "Hi"}],
        total_duration_ms=3000
    )
    assert "saved_duration_ms" in res_silence

    # Test reframe tool
    res_reframe = media_smart_reframe(1920, 1080, 2000)
    assert res_reframe["target_width"] == 1080

    # Test kinetic subtitles tool
    res_subtitles = media_kinetic_subtitles("Viral hook test")
    assert "srt_content" in res_subtitles

    # Test sound design tool
    res_sound = media_sound_design(video_duration_s=12.0)
    assert "sfx_timeline" in res_sound
