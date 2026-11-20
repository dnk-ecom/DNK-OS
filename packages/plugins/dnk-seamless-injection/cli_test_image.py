# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk-seamless-injection/cli_test_image.py"
# purpose: "Interactive & CLI visual test runner for Zero-Trace Seamless Visual Injection Engine on real or synthetic donor images."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-22"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""CLI Runner & Visual Comparison Sheet Generator for dnk-seamless-injection."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def _load_plugin_server():
    plugin_root = Path(__file__).resolve().parent
    init_file = plugin_root / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "dnk_seamless_injection_pkg",
        str(init_file),
        submodule_search_locations=[str(plugin_root)],
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["dnk_seamless_injection_pkg"] = mod
        spec.loader.exec_module(mod)
    return importlib.import_module("dnk_seamless_injection_pkg.mcp.server")


def generate_sample_donor_leggings(path: Path, width: int = 640, height: int = 480) -> Tuple[int, int, int, int]:
    """Generate a high-detail 3D ribbed compression leggings test photo with a donor logo."""
    rng = random.Random(42)
    img = Image.new("RGB", (width, height))
    pixels = []
    for y in range(height):
        for x in range(width):
            rib = math.sin(x * 0.35 + math.sin(y * 0.05) * 2.2) * 14.0
            fold = math.cos((x * 0.025) + (y * 0.04)) * 24.0
            cyl = -((x - width * 0.5) / (width * 0.5)) ** 2 * 38.0
            base = 64.0 + rib + fold + cyl
            n_r = rng.gauss(0.0, 2.6)
            n_g = rng.gauss(0.0, 2.6)
            n_b = rng.gauss(0.0, 2.6)
            r = max(12, min(235, int(round(base + n_r))))
            g = max(12, min(235, int(round(base * 1.02 + n_g))))
            b = max(15, min(240, int(round(base * 1.06 + n_b))))
            pixels.append((r, g, b))
    img.putdata(pixels)

    roi_box = (int(width * 0.28), int(height * 0.36), int(width * 0.72), int(height * 0.58))
    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = roi_box
    # Draw harsh flat donor watermark/brand inside ROI
    draw.rectangle([x1 + 24, y1 + 22, x2 - 24, y2 - 22], outline=(242, 242, 242), width=3)
    draw.line([x1 + 36, (y1 + y2) // 2, x2 - 36, (y1 + y2) // 2], fill=(246, 246, 246), width=6)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), format="PNG")
    return roi_box


def build_side_by_side_comparison(
    donor_path: Path,
    injected_path: Path,
    comparison_path: Path,
    metrics: dict,
) -> Path:
    """Create a side-by-side BEFORE vs AFTER visual inspection sheet with metrics footer."""
    donor = Image.open(donor_path).convert("RGB")
    injected = Image.open(injected_path).convert("RGB")
    w, h = donor.size
    footer_h = 64
    canvas = Image.new("RGB", (w * 2 + 12, h + footer_h), (18, 22, 24))
    canvas.paste(donor, (0, 0))
    canvas.paste(injected, (w + 12, 0))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.rectangle([8, 8, 220, 32], fill=(17, 34, 36))
    draw.text((16, 14), "BEFORE (Donor Image)", fill=(212, 216, 219), font=font)

    draw.rectangle([w + 20, 8, w + 250, 32], fill=(17, 34, 36))
    draw.text((w + 28, 14), "AFTER (Monte 5-Layer Injection)", fill=(53, 213, 213), font=font)

    summary = (
        f"Quality Gates: {'PASSED' if metrics.get('passed_all_gates') else 'FAILED'}  |  "
        f"LPIPS: {metrics.get('lpips_score')} (<0.04)  |  "
        f"Edge Consistency: {metrics.get('edge_gradient_consistency')} (>0.98)  |  "
        f"Zero-OCR Residual: {metrics.get('donor_ocr_matches')} (0)"
    )
    draw.text((16, h + 22), summary, fill=(34, 197, 94), font=font)
    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(comparison_path), format="PNG")
    return comparison_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Zero-Trace Seamless Visual Injection on images.")
    parser.add_argument("--input", type=str, default="", help="Path to input donor photo (leave empty for demo leggings)")
    parser.add_argument("--output-dir", type=str, default="./tests/.tmp/seamless_injection_test", help="Output directory")
    parser.add_argument("--brand-text", type=str, default="MONTE", help="Brand text to inject")
    parser.add_argument("--logo", type=str, default="", help="Optional path to transparent PNG brand logo")
    parser.add_argument(
        "--roi",
        type=str,
        default="",
        help="Optional ROI box 'x1,y1,x2,y2' where donor logo sits (auto-centered if omitted)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    roi_box: Optional[Tuple[int, int, int, int]] = None
    if args.input:
        donor_path = Path(args.input)
        if not donor_path.exists():
            print(f"❌ Input file not found: {donor_path}", file=sys.stderr)
            return 1
        if args.roi:
            parts = [int(p.strip()) for p in args.roi.split(",")]
            if len(parts) == 4:
                roi_box = (parts[0], parts[1], parts[2], parts[3])
    else:
        donor_path = out_dir / "01_donor_input.png"
        roi_box = generate_sample_donor_leggings(donor_path)

    injected_path = out_dir / "02_monte_injected.png"
    comparison_path = out_dir / "03_before_after_comparison.png"

    server = _load_plugin_server()
    result = server.inject_brand_photo(
        image_path=str(donor_path),
        output_path=str(injected_path),
        brand_text=args.brand_text,
        target_prompt="donor logo",
        hint_bbox=roi_box,
        sync_to_shopify=False,
    )

    build_side_by_side_comparison(donor_path, injected_path, comparison_path, result)

    report_path = out_dir / "04_quality_report.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": result.get("status"),
        "donor_image": str(donor_path),
        "injected_image": str(injected_path),
        "comparison_sheet": str(comparison_path),
        "quality_report": str(report_path),
        "lpips_score": result.get("lpips_score"),
        "edge_gradient_consistency": result.get("edge_gradient_consistency"),
        "donor_ocr_matches": result.get("donor_ocr_matches"),
        "passed_all_gates": result.get("passed_all_gates"),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
