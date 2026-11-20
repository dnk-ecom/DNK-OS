# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk-seamless-injection/tests/test_temporal_consistency.py"
# purpose: "Unit and Quality Gate tests for Section 4 Video Pipeline: CoTracker3 500+ mesh points, optical flow stabilization, and motion blur matching."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-22"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import importlib.util
import math
import sys
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw

PLUGIN_DIR = Path(__file__).resolve().parents[1]


def _load_plugin_pkg():
    pkg_name = "dnk_seamless_injection_pkg"
    if pkg_name in sys.modules:
        return sys.modules[pkg_name]
    spec = importlib.util.spec_from_file_location(
        pkg_name,
        PLUGIN_DIR / "__init__.py",
        submodule_search_locations=[str(PLUGIN_DIR)],
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[pkg_name] = mod
    spec.loader.exec_module(mod)
    return mod


_load_plugin_pkg()
_vt_mod = importlib.import_module("dnk_seamless_injection_pkg.core.video_tracker")
_mcp_mod = importlib.import_module("dnk_seamless_injection_pkg.mcp.server")
DeformableVideoTracker = _vt_mod.DeformableVideoTracker
inject_brand_video = _mcp_mod.inject_brand_video


def test_cotracker3_mesh_has_500_plus_points_and_reduces_jitter():
    tracker = DeformableVideoTracker(grid_cols=25, grid_rows=20, fps=60)
    assert tracker.num_mesh_points == 500

    initial_bbox = (60, 50, 140, 90)
    # Simulate 16 frames of smooth walking motion contaminated with high-frequency temporal jitter
    raw_offsets: List[Tuple[float, float]] = []
    for t in range(16):
        jitter_x = 2.4 * (1 if t % 2 == 0 else -1)
        jitter_y = -1.8 * (1 if t % 2 == 0 else -1)
        smooth_x = t * 1.5
        smooth_y = math.sin(t * 0.3) * 3.0
        raw_offsets.append((smooth_x + jitter_x, smooth_y + jitter_y))

    states, raw_jitter, stabilized_jitter = tracker.track_deformable_surface(
        initial_bbox, raw_offsets
    )

    assert len(states) == 16
    assert len(states[0].points) == 500
    assert raw_jitter > 3.0
    assert stabilized_jitter < raw_jitter * 0.25


def test_video_pipeline_60fps_temporal_consistency_and_motion_blur(tmp_path: Path):
    frame_paths: List[str] = []
    hint_bboxes: List[Tuple[int, int, int, int]] = []

    for t in range(8):
        img = Image.new("RGB", (200, 150), (72, 76, 82))
        draw = ImageDraw.Draw(img)
        # Draw textured compression ribs moving horizontally
        dx = int(t * 3 + (2 if t % 2 == 0 else -2))
        for ry in range(20, 130, 8):
            draw.line([(0, ry), (200, ry)], fill=(60, 64, 70), width=2)
        bbox = (55 + dx, 50, 135 + dx, 90)
        draw.rectangle((bbox[0] + 10, bbox[1] + 8, bbox[2] - 10, bbox[3] - 8), fill=(235, 235, 235))

        fp = tmp_path / f"donor_frame_{t:02d}.png"
        img.save(fp)
        frame_paths.append(str(fp))
        hint_bboxes.append(bbox)

    out_dir = tmp_path / "monte_video_out"
    res = inject_brand_video(
        frame_paths=frame_paths,
        output_dir=str(out_dir),
        brand_text="Monte",
        fps=60,
        hint_bboxes=hint_bboxes,
    )

    assert res["status"] == "completed"
    assert res["fps"] == 60
    assert res["num_tracked_points"] >= 500
    assert len(res["output_frames"]) == 8
    assert res["stabilized_trajectory_jitter"] < res["raw_trajectory_jitter"]
    assert res["temporal_consistency_score"] > 0.98
    assert res["mean_lpips_score"] < 0.04
    assert res["mean_edge_gradient_consistency"] > 0.98
    assert res["passed_quality_gates"] is True
