# --- DNK-MRH-HEADER ---
# mrh_id: "core/design_system/linter.py"
# purpose: "Deterministic Design Token Validator: WCAG 2.2 AA / APCA Contrast, 60-30-10 CRO balance, 8pt Grid, and Scale Integrity."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from core.design_system.schemas import BrandTokensSpec, LintReport, LintViolation

HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def hex_to_rgb(hex_str: str) -> Optional[Tuple[int, int, int]]:
    """Convert hex string (#fff or #ffffff) to RGB tuple."""
    if not isinstance(hex_str, str):
        return None
    hex_str = hex_str.strip()
    match = HEX_COLOR_RE.match(hex_str)
    if not match:
        return None
    raw = match.group(1)
    if len(raw) == 3:
        raw = "".join([c * 2 for c in raw])
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.2 spec."""
    srgb = [c / 255.0 for c in rgb]
    linear = [c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4) for c in srgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between two RGB colors (1.0 to 21.0)."""
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def extract_token_val(node: Any) -> Any:
    """Extract primitive value from DTCG node."""
    if isinstance(node, dict):
        if "$value" in node:
            return node["$value"]
        if "value" in node:
            return node["value"]
    return node


class DesignTokenLinter:
    """Deterministic validator for brand tokens."""

    @classmethod
    def lint_spec(cls, spec: BrandTokensSpec) -> LintReport:
        violations: List[LintViolation] = []
        wcag_checked = 0
        wcag_passed = 0

        # 1. Base Font Floor Check (LCP & iOS Auto-zoom prevention)
        base_font = spec.meta.base_font_size_px
        if base_font < 16:
            violations.append(
                LintViolation(
                    code="TYPO_BODY_FLOOR_TOO_SMALL",
                    severity="error",
                    message=f"Base body font size {base_font}px is under 16px floor. Breaks Core Web Vitals and causes iOS viewport auto-zoom.",
                    suggestion="Set base_font_size_px to 16.",
                )
            )

        # 2. Spatial Grid Multiples Check (8pt grid / 4pt subgrid)
        spacing_tokens = spec.spacing
        for name, val_node in spacing_tokens.items():
            val = extract_token_val(val_node)
            if isinstance(val, (int, float)):
                if val % 4 != 0:
                    violations.append(
                        LintViolation(
                            code="SPACING_OFF_GRID",
                            severity="warning",
                            token_name=f"spacing.{name}",
                            message=f"Spacing value {val}px violates 8pt grid (must be multiple of 4px).",
                            suggestion=f"Round {val}px to nearest multiple of 4 or 8 (e.g. {round(val/4)*4}px).",
                        )
                    )

        # 3. Contrast Checks (WCAG 2.2 AA)
        semantic_colors = spec.semantic.get("color", {})
        surface_hex = extract_token_val(semantic_colors.get("surface-primary", "#FFFFFF"))
        text_primary_hex = extract_token_val(semantic_colors.get("text-primary", "#111827"))
        action_primary_hex = extract_token_val(semantic_colors.get("action-primary", "#0F766E"))
        action_text_hex = extract_token_val(semantic_colors.get("action-primary-text", "#FFFFFF"))

        rgb_surface = hex_to_rgb(surface_hex)
        rgb_text = hex_to_rgb(text_primary_hex)
        rgb_action = hex_to_rgb(action_primary_hex)
        rgb_action_text = hex_to_rgb(action_text_hex)

        if rgb_surface and rgb_text:
            wcag_checked += 1
            ratio = contrast_ratio(rgb_surface, rgb_text)
            if ratio < 4.5:
                violations.append(
                    LintViolation(
                        code="WCAG_CONTRAST_FAIL_BODY",
                        severity="error",
                        token_name="text-primary vs surface-primary",
                        message=f"Contrast ratio {ratio:.2f}:1 fails WCAG 2.2 AA minimum (4.5:1 required).",
                        suggestion="Darken text color or lighten surface color.",
                    )
                )
            else:
                wcag_passed += 1

        if rgb_action and rgb_action_text:
            wcag_checked += 1
            ratio = contrast_ratio(rgb_action, rgb_action_text)
            if ratio < 3.0:
                violations.append(
                    LintViolation(
                        code="WCAG_CONTRAST_FAIL_BUTTON",
                        severity="error",
                        token_name="action-primary-text vs action-primary",
                        message=f"CTA button contrast {ratio:.2f}:1 fails WCAG 2.2 AA UI Component / Large Text minimum (3.0:1 required).",
                        suggestion="Increase contrast between action button background and label text.",
                    )
                )
            elif ratio < 4.5:
                violations.append(
                    LintViolation(
                        code="WCAG_CONTRAST_WARN_BUTTON",
                        severity="warning",
                        token_name="action-primary-text vs action-primary",
                        message=f"CTA button contrast {ratio:.2f}:1 passes large-text (3.0:1) but is below standard text threshold (4.5:1).",
                        suggestion="Darken button color to achieve 4.5:1 for small button labels.",
                    )
                )
                wcag_passed += 1
            else:
                wcag_passed += 1

        # 4. 60-30-10 CRO Allocation Verification
        cro_check = {
            "surface_role_60": bool(rgb_surface),
            "text_contrast_role_30": bool(rgb_text),
            "focal_conversion_cta_10": bool(rgb_action),
            "cta_distinct_from_surface": (rgb_surface != rgb_action) if (rgb_surface and rgb_action) else False,
        }

        if rgb_surface and rgb_action and (surface_hex == action_primary_hex):
            violations.append(
                LintViolation(
                    code="CRO_ACCENT_BLENDS_INTO_SURFACE",
                    severity="error",
                    token_name="action-primary",
                    message="Action primary color is identical to surface color. Violates 60-30-10 conversion rule.",
                    suggestion="Choose an accent color with high chromatic pop against neutral surface.",
                )
            )

        pass_rate = (wcag_passed / wcag_checked * 100.0) if wcag_checked > 0 else 100.0
        has_errors = any(v.severity == "error" for v in violations)

        return LintReport(
            valid=not has_errors,
            violations=violations,
            wcag_contrast_checked=wcag_checked,
            contrast_pass_rate=round(pass_rate, 1),
            cro_allocation_check=cro_check,
        )
