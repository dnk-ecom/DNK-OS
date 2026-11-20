# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk-seamless-injection/tests/test_grain_matching.py"
# purpose: "Unit and Quality Gate tests for 5-Layer Photo Injection, RGB Sensor Grain Matching, LPIPS < 0.04, Edge Consistency > 0.98, and Shopify Sync."
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
import os
import random
import sys
from pathlib import Path
from typing import Tuple
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
_inp_mod = importlib.import_module("dnk_seamless_injection_pkg.core.inpainter")
_seg_mod = importlib.import_module("dnk_seamless_injection_pkg.core.segmenter")
_sync_mod = importlib.import_module("dnk_seamless_injection_pkg.core.shopify_syncer")
_blend_mod = importlib.import_module("dnk_seamless_injection_pkg.core.surface_blender")
_mcp_mod = importlib.import_module("dnk_seamless_injection_pkg.mcp.server")

TextureInpainter = _inp_mod.TextureInpainter
SubpixelSegmenter = _seg_mod.SubpixelSegmenter
ShopifyMediaSyncer = _sync_mod.ShopifyMediaSyncer
BlendMetrics = _blend_mod.BlendMetrics
SurfaceBlender = _blend_mod.SurfaceBlender
inject_brand_photo = _mcp_mod.inject_brand_photo
inspect_photorealism_metrics = _mcp_mod.inspect_photorealism_metrics


def _synthesize_3d_compression_leggings_donor(
    size: Tuple[int, int] = (240, 180),
    with_donor_logo: bool = True,
    iso_sigma: float = 3.2,
) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """
    Generates a photorealistic synthetic 3D ribbed compression leggings swatch
    with directional cylindrical shading, vertical weave periodicity, ISO camera grain,
    and an optional bright 'DONOR' watermark in the center.
    """
    w, h = size
    rng = random.Random(101)
    raw = bytearray(w * h * 3)

    for y in range(h):
        # Periodic horizontal compression fold + micro-rib
        fold_wave = math.sin((y / 12.0) * 2.0 * math.pi) * 14.0
        for x in range(w):
            # Cylindrical leg lighting gradient (brighter center-left, darker edges)
            nx = (x - w * 0.42) / (w * 0.5)
            cyl_shade = max(0.35, 1.0 - 0.55 * (nx * nx))
            rib_x = math.cos((x / 4.0) * 2.0 * math.pi) * 6.0

            base_l = (68.0 + fold_wave + rib_x) * cyl_shade
            nr = base_l + rng.gauss(0.0, iso_sigma)
            ng = base_l * 1.03 + rng.gauss(0.0, iso_sigma * 0.95)
            nb = base_l * 1.08 + rng.gauss(0.0, iso_sigma * 1.05)

            idx = (y * w + x) * 3
            raw[idx] = max(0, min(255, int(round(nr))))
            raw[idx + 1] = max(0, min(255, int(round(ng))))
            raw[idx + 2] = max(0, min(255, int(round(nb))))

    img = Image.frombytes("RGB", (w, h), bytes(raw))
    bbox = (70, 62, 170, 114)
    if with_donor_logo:
        draw = ImageDraw.Draw(img)
        draw.rectangle((82, 74, 158, 100), fill=(245, 245, 245))
    return img, bbox


def test_subpixel_segmenter_feathering_and_bounds():
    donor_img, hint_bbox = _synthesize_3d_compression_leggings_donor()
    segmenter = SubpixelSegmenter(feather_radius_px=1.75)
    res = segmenter.segment(donor_img, prompt="donor logo", hint_bbox=hint_bbox)

    assert res.feather_radius_px == 1.75
    assert res.mask.mode == "L"
    assert res.mask.size == donor_img.size
    assert res.confidence > 0.95
    assert res.metadata["anatomical_seams_preserved"] is True

    # Verify subpixel feathering creates intermediate alpha values (not just 0 and 255)
    hist = res.mask.histogram()
    intermediate_pixels = sum(hist[10:245])
    assert intermediate_pixels > 25


def test_lama_texture_inpainter_preserves_sharpness():
    donor_img, hint_bbox = _synthesize_3d_compression_leggings_donor()
    segmenter = SubpixelSegmenter(feather_radius_px=1.75)
    seg = segmenter.segment(donor_img, prompt="donor logo", hint_bbox=hint_bbox)

    inpainter = TextureInpainter(patch_stride_y=12)
    inp = inpainter.inpaint(donor_img, seg.mask, seg.bbox)

    assert inp.clean_image.size == donor_img.size
    assert inp.texture_periodicity_score > 0.98
    assert inp.metadata["blur_artifact_detected"] is False
    assert float(inp.metadata["patch_sharpness_std"]) > 2.0


def test_surface_blender_grain_matching_and_quality_gates(tmp_path: Path):
    donor_img, hint_bbox = _synthesize_3d_compression_leggings_donor(iso_sigma=3.5)
    donor_path = tmp_path / "donor_leggings.png"
    out_path = tmp_path / "monte_injected.png"
    donor_img.save(donor_path)

    report = inject_brand_photo(
        image_path=str(donor_path),
        output_path=str(out_path),
        brand_text="Monte",
        target_prompt="donor logo",
        hint_bbox=hint_bbox,
        sync_to_shopify=True,
    )

    assert os.path.exists(out_path)
    assert report["status"] == "completed"
    assert report["lpips_score"] < 0.04
    assert report["edge_gradient_consistency"] > 0.98
    assert report["donor_ocr_matches"] == 0
    assert report["target_brand_readable"] is True
    assert report["passed_all_gates"] is True
    assert report["shopify_sync"]["success"] is True
    assert "cdn.shopify.com" in report["shopify_sync"]["cdn_url"]

    # Verify RGB camera sensor grain harmonization (injected region is not sterile/plastic)
    donor_sig = report["grain_rgb_sigma_donor"]
    inj_sig = report["grain_rgb_sigma_injected"]
    for c in range(3):
        assert donor_sig[c] > 1.5
        assert inj_sig[c] > 1.5
        # Grain sigma in injected zone stays within realistic camera ISO band
        assert abs(inj_sig[c] - donor_sig[c]) < donor_sig[c] * 0.85


def test_shopify_syncer_blocks_failed_quality_gate(tmp_path: Path):
    dummy_file = tmp_path / "bad_inject.png"
    Image.new("RGB", (64, 64), (120, 120, 120)).save(dummy_file)

    syncer = ShopifyMediaSyncer(store_handle="test01010126")
    bad_metrics = BlendMetrics(
        lpips_score=0.065,  # Exceeds 0.04 limit!
        edge_gradient_consistency=0.99,
        donor_ocr_matches=0,
        target_brand_readable=True,
        grain_rgb_sigma_donor=(2.5, 2.5, 2.5),
        grain_rgb_sigma_injected=(2.4, 2.4, 2.4),
        passed_all_gates=False,
    )
    res = syncer.sync_asset(str(dummy_file), bad_metrics)
    assert res.success is False
    assert res.cdn_url is None
    assert res.quality_gate_passed is False
    assert "LPIPS" in (res.rejection_reason or "")


def test_inspect_photorealism_metrics_mcp_tool(tmp_path: Path):
    clean_img, bbox = _synthesize_3d_compression_leggings_donor(with_donor_logo=False)
    blender = SurfaceBlender()
    s_maps = blender.extract_surface_maps(clean_img, bbox)
    ov = blender.render_brand_overlay((bbox[2] - bbox[0], bbox[3] - bbox[1]), "Monte")
    warped = blender.warp_and_shade_overlay(ov, s_maps)
    inj_img, _, _ = blender.blend_and_harmonize_grain(clean_img, warped, bbox)

    c_path = tmp_path / "clean.png"
    i_path = tmp_path / "inj.png"
    clean_img.save(c_path)
    inj_img.save(i_path)

    metrics = inspect_photorealism_metrics(
        clean_image_path=str(c_path),
        injected_image_path=str(i_path),
        mask_bbox=bbox,
        donor_text="DONOR",
        target_brand="Monte",
    )
    assert metrics["lpips_score"] < 0.04
    assert metrics["edge_gradient_consistency"] > 0.98
    assert metrics["passed_all_gates"] is True
