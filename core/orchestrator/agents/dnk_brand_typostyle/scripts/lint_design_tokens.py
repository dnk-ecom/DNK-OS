#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/dnk_brand_typostyle/scripts/lint_design_tokens.py"
# purpose: "Deterministic CLI validator for W3C DTCG & Google DESIGN.md tokens: WCAG 2.2 contrast checking, 8pt spacing grid verification, 60-30-10 CRO allocation, and modular typography scale validation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Deterministic Design Token Linter for dnk_brand_typostyle."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import yaml

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
PIXEL_VALUE_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*(?:px)?$")

CANONICAL_SCALE_125: dict[str, float] = {
    "display": 2.441,
    "h1": 1.953,
    "h2": 1.563,
    "h3": 1.250,
    "body-lg": 1.125,
    "body-md": 1.000,
    "body-sm": 0.875,
    "caption": 0.750,
}

CANONICAL_SCALE_120: dict[str, float] = {
    "display": 2.074,
    "h1": 1.728,
    "h2": 1.440,
    "h3": 1.200,
    "body-lg": 1.125,
    "body-md": 1.000,
    "body-sm": 0.875,
    "caption": 0.750,
}

CANONICAL_SPACING_PX: dict[str, int] = {
    "none": 0,
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
    "3xl": 64,
}


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert #RGB or #RRGGBB hex string to (R, G, B) integers in 0..255."""
    cleaned = hex_str.strip()
    if not HEX_COLOR_RE.match(cleaned):
        raise ValueError(f"Invalid hex color format: {hex_str!r}")
    raw = cleaned.lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def relative_luminance(hex_str: str) -> float:
    """Compute WCAG 2.2 relative luminance L in [0.0, 1.0] for a hex color."""
    r_int, g_int, b_int = hex_to_rgb(hex_str)
    channels = []
    for channel in (r_int, g_int, b_int):
        s_rgb = channel / 255.0
        if s_rgb <= 0.04045:
            channels.append(s_rgb / 12.92)
        else:
            channels.append(((s_rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def calculate_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG 2.2 contrast ratio (L1 + 0.05) / (L2 + 0.05) rounded to 2 decimals."""
    lum1 = relative_luminance(fg_hex)
    lum2 = relative_luminance(bg_hex)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    ratio = (lighter + 0.05) / (darker + 0.05)
    return round(ratio, 2)


def _extract_token_hex(token_obj: Any) -> str:
    """Extract hex string from either a raw string or DTCG token dict."""
    if isinstance(token_obj, str):
        return token_obj
    if isinstance(token_obj, dict) and "$value" in token_obj:
        return str(token_obj["$value"])
    if isinstance(token_obj, dict) and "value" in token_obj:
        return str(token_obj["value"])
    raise ValueError(f"Cannot extract hex value from token: {token_obj!r}")


def _extract_spacing_px(token_obj: Any) -> float:
    """Extract numeric pixel value from spacing token entry."""
    if isinstance(token_obj, (int, float)):
        return float(token_obj)
    if isinstance(token_obj, str):
        match = PIXEL_VALUE_RE.match(token_obj.strip())
        if not match:
            raise ValueError(f"Invalid pixel dimension: {token_obj!r}")
        return float(match.group(1))
    if isinstance(token_obj, dict):
        if "px" in token_obj:
            return float(token_obj["px"])
        raw = token_obj.get("$value", token_obj.get("value"))
        if raw is not None:
            return _extract_spacing_px(raw)
    raise ValueError(f"Cannot extract pixel dimension from spacing token: {token_obj!r}")


def validate_contrast_section(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate WCAG 2.2 contrast ratios across semantic color pairs."""
    errors: list[str] = []
    results: list[dict[str, Any]] = []

    semantic = spec.get("semantic", {})
    colors = semantic.get("color", {})
    if not colors:
        errors.append("Missing 'semantic.color' token dictionary.")
        return results, errors

    proportion = semantic.get("proportion_allocation", {})
    if proportion:
        dom = proportion.get("dominant_surface_pct", 0)
        struc = proportion.get("structural_typography_pct", 0)
        acc = proportion.get("focal_accent_pct", 0)
        if (dom, struc, acc) != (60, 30, 10):
            errors.append(
                f"CRO 60-30-10 allocation violated: got {dom}-{struc}-{acc} (expected 60-30-10)."
            )

    for token_name, token_data in colors.items():
        if not isinstance(token_data, dict):
            continue
        bg_target = token_data.get("contrast_against")
        if not bg_target:
            continue

        if bg_target not in colors:
            errors.append(
                f"Token '{token_name}' references unknown background token '{bg_target}'."
            )
            continue

        try:
            fg_hex = _extract_token_hex(token_data)
            bg_hex = _extract_token_hex(colors[bg_target])
            ratio = calculate_contrast_ratio(fg_hex, bg_hex)
        except ValueError as exc:
            errors.append(f"Color parse error for '{token_name}' vs '{bg_target}': {exc}")
            continue

        category = token_data.get("category", "text")
        is_large = bool(token_data.get("is_large_text", False))
        default_threshold = 3.0 if (category == "ui_component" or is_large) else 4.5
        min_required = float(token_data.get("min_contrast", default_threshold))

        passed = ratio >= min_required
        results.append(
            {
                "pair": f"{token_name} on {bg_target}",
                "foreground": fg_hex,
                "background": bg_hex,
                "ratio": ratio,
                "required": min_required,
                "passed": passed,
            }
        )
        if not passed:
            errors.append(
                f"WCAG 2.2 contrast failure on '{token_name}' vs '{bg_target}': "
                f"{ratio}:1 < required {min_required}:1"
            )

    return results, errors


def validate_spacing_section(spec: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    """Validate that spacing tokens strictly obey the 4px / 8pt spatial grid."""
    errors: list[str] = []
    parsed_spacing: dict[str, float] = {}

    spacing = spec.get("spacing", {})
    if not spacing:
        errors.append("Missing 'spacing' section in design token specification.")
        return parsed_spacing, errors

    for key, expected_px in CANONICAL_SPACING_PX.items():
        if key not in spacing:
            errors.append(f"Missing required canonical spacing token '{key}' ({expected_px}px).")

    for key, val in spacing.items():
        try:
            px_val = _extract_spacing_px(val)
            parsed_spacing[key] = px_val
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if px_val < 0:
            errors.append(f"Spacing token '{key}' cannot be negative ({px_val}px).")
            continue

        if px_val != 0 and (px_val % 4 != 0):
            errors.append(
                f"Spacing token '{key}' ({px_val}px) violates the 4px/8pt spatial grid."
            )

        if key in CANONICAL_SPACING_PX and not math.isclose(
            px_val, CANONICAL_SPACING_PX[key], abs_tol=0.01
        ):
            errors.append(
                f"Spacing token '{key}' is {px_val}px, expected canonical {CANONICAL_SPACING_PX[key]}px."
            )

    return parsed_spacing, errors


def validate_typography_section(spec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Validate base font size (16px), modular scale ratios (1.25/1.20), and line heights."""
    errors: list[str] = []
    meta = spec.get("meta", {})
    ratio = float(meta.get("typography_ratio", 1.25))
    base_px = float(meta.get("base_font_size_px", 16))

    if not math.isclose(base_px, 16.0, abs_tol=0.01):
        errors.append(f"Base font size must be 16px (1rem), got {base_px}px.")

    if not (math.isclose(ratio, 1.25, abs_tol=0.005) or math.isclose(ratio, 1.20, abs_tol=0.005)):
        errors.append(
            f"Modular scale ratio must be Major Third (1.25) or Minor Third (1.20), got {ratio}."
        )

    typography = spec.get("typography", {})
    scale = typography.get("scale", {})
    if not scale:
        errors.append("Missing 'typography.scale' section.")
        return {"ratio": ratio, "base_px": base_px, "steps_checked": 0}, errors

    reference_scale = CANONICAL_SCALE_125 if math.isclose(ratio, 1.25, abs_tol=0.01) else CANONICAL_SCALE_120

    for step_name, expected_rem in reference_scale.items():
        if step_name not in scale:
            errors.append(f"Missing required typography scale step '{step_name}'.")
            continue
        step_data = scale[step_name]
        actual_rem = float(step_data.get("rem", 0.0))
        actual_px = float(step_data.get("px", actual_rem * 16.0))
        line_height = float(step_data.get("line_height", 0.0))
        role = step_data.get("role", "heading" if step_name in ("display", "h1", "h2", "h3") else "body")

        if not math.isclose(actual_rem, expected_rem, abs_tol=0.01):
            errors.append(
                f"Typography step '{step_name}' rem={actual_rem} does not match expected {expected_rem}rem."
            )

        if step_name == "body-md" and not math.isclose(actual_px, 16.0, abs_tol=0.1):
            errors.append(f"Typography 'body-md' must be 16px, got {actual_px}px.")

        if role == "heading":
            if not (1.10 <= line_height <= 1.25):
                errors.append(
                    f"Heading '{step_name}' line_height={line_height} outside allowed range [1.10, 1.25]."
                )
        else:
            if not (1.40 <= line_height <= 1.60):
                errors.append(
                    f"Body step '{step_name}' line_height={line_height} outside allowed range [1.40, 1.60]."
                )

    return {
        "ratio": ratio,
        "base_px": base_px,
        "steps_checked": len(scale),
    }, errors


def lint_token_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Run full deterministic lint suite on a parsed design token specification."""
    contrast_results, contrast_errors = validate_contrast_section(spec)
    spacing_results, spacing_errors = validate_spacing_section(spec)
    typo_summary, typo_errors = validate_typography_section(spec)

    all_errors = contrast_errors + spacing_errors + typo_errors
    status = "PASS" if not all_errors else "FAIL"

    return {
        "status": status,
        "schema_version": spec.get("schema_version", "unknown"),
        "brand_name": spec.get("meta", {}).get("brand_name", "unnamed"),
        "contrast": {
            "pairs_checked": len(contrast_results),
            "all_passed": len(contrast_errors) == 0 and len(contrast_results) > 0,
            "results": contrast_results,
        },
        "spacing": {
            "grid_base_px": 8,
            "tokens_checked": len(spacing_results),
            "valid": len(spacing_errors) == 0,
        },
        "typography": {
            **typo_summary,
            "valid": len(typo_errors) == 0,
        },
        "errors": all_errors,
    }


def load_spec_file(spec_path: Path) -> dict[str, Any]:
    """Load YAML or JSON design token specification from disk."""
    content = spec_path.read_text(encoding="utf-8")
    if spec_path.suffix.lower() == ".json":
        return json.loads(content)
    return yaml.safe_load(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic WCAG 2.2, 8pt Grid & Modular Typography Linter."
    )
    parser.add_argument(
        "--spec",
        required=True,
        type=Path,
        help="Relative path to YAML or JSON token specification file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Emit machine-readable JSON output (default: True).",
    )
    args = parser.parse_args(argv)

    if not args.spec.exists():
        error_payload = {
            "status": "FAIL",
            "errors": [f"Specification file not found: {args.spec}"],
        }
        print(json.dumps(error_payload, indent=2))
        return 1

    spec_data = load_spec_file(args.spec)
    report = lint_token_spec(spec_data)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
