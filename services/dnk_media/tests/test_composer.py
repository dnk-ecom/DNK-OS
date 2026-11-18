# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/tests/test_composer.py"
# purpose: "Unit and integration tests for Unified 9:16 Video Composition Pipeline"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import os
from pathlib import Path
import pytest
from services.dnk_media.contracts.schemas import VideoCompositionRequest
from services.dnk_media.src.composer import VideoComposer, video_composer
from services.dnk_media.src.service import compose_video_9_16
from services.dnk_media.mcp_server import media_compose_video_9_16


def test_composer_dry_run_composition(tmp_path):
    transcript = "Stop making this huge mistake with your Shopify store. Watch your profit explode fast with this secret strategy."
    out_mp4 = str(tmp_path / "test_output.mp4")

    req = VideoCompositionRequest(
        transcript=transcript,
        duration_ms=4500,
        style_preset="hormozi_bold",
        output_path=out_mp4
    )

    composer = VideoComposer()
    res = composer.compose(req, dry_run=True)

    assert res.success is True
    assert res.target_dimensions == "1080x1920 (9:16)"
    assert res.estimated_duration_ms == 4500
    assert res.subtitles_track is not None
    assert len(res.subtitles_track.words) > 0
    assert res.reframe_plan is not None
    assert res.silence_cut_plan is not None
    assert res.sound_design_plan is not None

    # Verify FFmpeg recipe synthesis
    assert "1080x1920" in res.ffmpeg_recipe
    assert "-c:s mov_text" in res.ffmpeg_recipe

    # Verify sidecar .ass and .srt files were generated
    assert res.ass_subtitle_path is not None
    assert Path(res.ass_subtitle_path).exists()
    srt_path = Path(res.ass_subtitle_path).with_suffix(".srt")
    assert srt_path.exists()
    assert "00:00:00" in srt_path.read_text(encoding="utf-8")
    ass_text = Path(res.ass_subtitle_path).read_text(encoding="utf-8")
    assert "[Script Info]" in ass_text
    assert "Dialogue:" in ass_text


def test_composer_with_source_video_path(tmp_path):
    mock_src = tmp_path / "mock_cam_recording.mp4"
    mock_src.write_bytes(b"dummy_mp4_bytes")

    out_mp4 = str(tmp_path / "final_reel.mp4")
    req = VideoCompositionRequest(
        source_video_path=str(mock_src),
        transcript="Boost your e-commerce growth with sovereign themes.",
        duration_ms=3000,
        output_path=out_mp4
    )

    res = video_composer.compose(req, dry_run=True)
    assert res.success is True
    assert f'-i "{str(mock_src)}"' in res.ffmpeg_recipe
    assert "scale=1080:1920" in res.ffmpeg_recipe


def test_facade_and_mcp_tool(tmp_path):
    out_mp4 = str(tmp_path / "facade_reel.mp4")

    # 1. Test In-RAM Facade
    res_facade = compose_video_9_16(
        transcript="Test fast revenue growth.",
        duration_ms=2000,
        output_path=out_mp4,
        dry_run=True
    )
    assert res_facade.success is True
    assert "1080x1920" in res_facade.target_dimensions

    # 2. Test FastMCP tool
    mcp_res = media_compose_video_9_16(
        transcript="Test fast revenue growth.",
        duration_ms=2000,
        output_path=out_mp4,
        dry_run=True
    )
    assert mcp_res["success"] is True
    assert "cmp_" in mcp_res["composition_id"]


def test_real_ffmpeg_rendering_sample(tmp_path):
    """Executes a real 1-second 9:16 vertical render using local FFmpeg."""
    out_mp4 = str(tmp_path / "rendered_9x16_reel.mp4")

    req = VideoCompositionRequest(
        transcript="Fast viral reel test.",
        duration_ms=1000,
        style_preset="minimal_clean",
        output_path=out_mp4,
        enable_silence_cut=False  # simple render for speed
    )

    res = video_composer.compose(req, dry_run=False)
    assert res.success is True
    assert res.is_rendered is True

    # Verify physical MP4 exists and has valid size
    out_file = Path(out_mp4)
    assert out_file.exists()
    assert out_file.stat().st_size > 1000

    # Verify MP4 magic header
    data = out_file.read_bytes()
    assert b"ftyp" in data[:32]
