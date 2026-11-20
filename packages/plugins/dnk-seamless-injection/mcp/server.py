# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk-seamless-injection/mcp/server.py"
# purpose: "FastMCP server exposing inject_brand_photo, inject_brand_video, and inspect_photorealism_metrics for swarm agents."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-22"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import os
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

import importlib

try:
    _fastmcp_mod = importlib.import_module("mcp.server.fastmcp")
    mcp = _fastmcp_mod.FastMCP("dnk-seamless-injection")
except Exception:  # pragma: no cover

    class _FallbackMCP:
        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(fn):
                return fn

            return decorator

    mcp = _FallbackMCP("dnk-seamless-injection")

from ..core.inpainter import TextureInpainter
from ..core.segmenter import SubpixelSegmenter
from ..core.shopify_syncer import ShopifyMediaSyncer
from ..core.surface_blender import SurfaceBlender
from ..core.video_tracker import DeformableVideoTracker


@mcp.tool()
def inject_brand_photo(
    image_path: str,
    output_path: str,
    brand_text: str = "Monte",
    target_prompt: str = "donor logo",
    hint_bbox: Optional[Tuple[int, int, int, int]] = None,
    sync_to_shopify: bool = False,
) -> Dict[str, Any]:
    """
    Executes the 5-layer Zero-Trace Seamless Visual Injection pipeline on a photo:
    1. SAM 2 + Grounding DINO subpixel segmentation (1.5-2px feathering)
    2. LaMa periodic texture-preserving inpainting
    3. Luminance displacement + shading map extraction
    4. Deformable surface warp of the new brand ('Monte')
    5. Photometric blending + RGB camera sensor grain harmonization
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Donor image not found: {image_path}")

    donor_img = Image.open(image_path).convert("RGB")
    segmenter = SubpixelSegmenter(feather_radius_px=1.75)
    inpainter = TextureInpainter()
    blender = SurfaceBlender()

    seg = segmenter.segment(donor_img, prompt=target_prompt, hint_bbox=hint_bbox)
    inp = inpainter.inpaint(donor_img, seg.mask, seg.bbox)
    surface_maps = blender.extract_surface_maps(inp.clean_image, seg.bbox)

    bw = seg.bbox[2] - seg.bbox[0]
    bh = seg.bbox[3] - seg.bbox[1]
    overlay = blender.render_brand_overlay((bw, bh), brand_text=brand_text)
    warped = blender.warp_and_shade_overlay(overlay, surface_maps)

    final_img, donor_sigma, inj_sigma = blender.blend_and_harmonize_grain(
        inp.clean_image, warped, seg.bbox
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final_img.save(output_path)

    metrics = blender.evaluate_quality_gates(
        inp.clean_image,
        final_img,
        seg.bbox,
        donor_text=target_prompt,
        target_brand=brand_text,
    )

    sync_info: Optional[Dict[str, Any]] = None
    if sync_to_shopify:
        syncer = ShopifyMediaSyncer()
        sr = syncer.sync_asset(output_path, metrics)
        sync_info = {
            "success": sr.success,
            "cdn_url": sr.cdn_url,
            "rejection_reason": sr.rejection_reason,
        }

    return {
        "status": "completed",
        "output_path": output_path,
        "bbox": seg.bbox,
        "feather_radius_px": seg.feather_radius_px,
        "lpips_score": metrics.lpips_score,
        "edge_gradient_consistency": metrics.edge_gradient_consistency,
        "donor_ocr_matches": metrics.donor_ocr_matches,
        "target_brand_readable": metrics.target_brand_readable,
        "grain_rgb_sigma_donor": metrics.grain_rgb_sigma_donor,
        "grain_rgb_sigma_injected": metrics.grain_rgb_sigma_injected,
        "passed_all_gates": metrics.passed_all_gates,
        "shopify_sync": sync_info,
    }


@mcp.tool()
def inject_brand_video(
    frame_paths: List[str],
    output_dir: str,
    brand_text: str = "Monte",
    fps: int = 60,
    hint_bboxes: Optional[List[Tuple[int, int, int, int]]] = None,
) -> Dict[str, Any]:
    """
    Executes the CoTracker3 500+ point deformable surface tracking + ProPainter + 5-layer
    injection pipeline across a sequence of video frames at 60fps.
    """
    if not frame_paths:
        raise ValueError("frame_paths cannot be empty")

    frames = [Image.open(p).convert("RGB") for p in frame_paths]
    tracker = DeformableVideoTracker(fps=fps)
    result = tracker.process_video_frames(
        frames, brand_text=brand_text, hint_bboxes=hint_bboxes
    )

    os.makedirs(output_dir, exist_ok=True)
    saved_paths: List[str] = []
    for idx, frame in enumerate(result.frames):
        out_p = os.path.join(output_dir, f"frame_{idx:04d}.png")
        frame.save(out_p)
        saved_paths.append(out_p)

    mean_lpips = sum(m.lpips_score for m in result.frame_metrics) / float(
        len(result.frame_metrics)
    )
    mean_edge = sum(
        m.edge_gradient_consistency for m in result.frame_metrics
    ) / float(len(result.frame_metrics))

    return {
        "status": "completed",
        "output_frames": saved_paths,
        "fps": result.fps,
        "num_tracked_points": result.num_tracked_points,
        "raw_trajectory_jitter": result.raw_trajectory_jitter,
        "stabilized_trajectory_jitter": result.stabilized_trajectory_jitter,
        "temporal_consistency_score": result.temporal_consistency_score,
        "mean_lpips_score": round(mean_lpips, 5),
        "mean_edge_gradient_consistency": round(mean_edge, 5),
        "passed_quality_gates": result.passed_quality_gates,
    }


@mcp.tool()
def inspect_photorealism_metrics(
    clean_image_path: str,
    injected_image_path: str,
    mask_bbox: Tuple[int, int, int, int],
    donor_text: str = "DONOR",
    target_brand: str = "Monte",
) -> Dict[str, Any]:
    """
    Evaluates Section 6 Quality Gates (LPIPS < 0.04, Edge Gradient Consistency > 0.98,
    Zero-Residual OCR, and RGB Sensor Grain Sigma match) on an injected image.
    """
    clean_img = Image.open(clean_image_path).convert("RGB")
    inj_img = Image.open(injected_image_path).convert("RGB")
    blender = SurfaceBlender()
    metrics = blender.evaluate_quality_gates(
        clean_img,
        inj_img,
        mask_bbox,
        donor_text=donor_text,
        target_brand=target_brand,
    )
    return {
        "lpips_score": metrics.lpips_score,
        "edge_gradient_consistency": metrics.edge_gradient_consistency,
        "donor_ocr_matches": metrics.donor_ocr_matches,
        "target_brand_readable": metrics.target_brand_readable,
        "grain_rgb_sigma_donor": metrics.grain_rgb_sigma_donor,
        "grain_rgb_sigma_injected": metrics.grain_rgb_sigma_injected,
        "passed_all_gates": metrics.passed_all_gates,
        "details": metrics.details,
    }
