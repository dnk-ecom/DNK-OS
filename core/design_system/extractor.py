# --- DNK-MRH-HEADER ---
# mrh_id: "core/design_system/extractor.py"
# purpose: "Extracts brand tokens from Shopify settings_data.json, raw CSS custom properties, or donor themes into DTCG specs."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
from core.design_system.schemas import BrandTokensSpec, BrandMeta

CSS_VAR_RE = re.compile(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);")


def _normalize_color_to_hex(val: str) -> Optional[str]:
    """Convert hex, rgb(), or comma-separated R,G,B to #RRGGBB."""
    val = val.strip()
    if val.startswith("#"):
        if len(val) == 4:
            return f"#{val[1]*2}{val[2]*2}{val[3]*2}".lower()
        return val.lower()
    
    # Check for rgb(r, g, b) or raw r, g, b
    nums = [int(n) for n in re.findall(r"\d+", val)[:3]]
    if len(nums) == 3 and all(0 <= n <= 255 for n in nums):
        return f"#{nums[0]:02x}{nums[1]:02x}{nums[2]:02x}"
    
    return None


class DesignTokenExtractor:
    """Extracts design tokens from Shopify theme configurations or CSS stylesheets."""

    @classmethod
    def from_shopify_settings(cls, settings_dict: Dict[str, Any], brand_name: str = "Shopify Store") -> BrandTokensSpec:
        """Parse Shopify settings_data.json into a structured BrandTokensSpec."""
        current = settings_dict.get("current", settings_dict)

        # Extract primary colors
        bg_color = current.get("color_background", current.get("color_site_background", "#FFFFFF"))
        text_color = current.get("color_text", current.get("color_foreground", "#111827"))
        accent_color = current.get("color_accent", current.get("color_primary", current.get("color_button", "#0F766E")))
        secondary_color = current.get("color_surface", "#F3F4F6")

        spec = BrandTokensSpec(
            meta=BrandMeta(brand_name=brand_name),
            semantic={
                "color": {
                    "surface-primary": {"$value": bg_color, "$type": "color"},
                    "text-primary": {"$value": text_color, "$type": "color"},
                    "action-primary": {"$value": accent_color, "$type": "color"},
                    "action-primary-text": {"$value": "#FFFFFF", "$type": "color"},
                    "action-secondary": {"$value": secondary_color, "$type": "color"},
                }
            },
            spacing={
                "base": 8,
                "sm": 8,
                "md": 16,
                "lg": 24,
                "xl": 32,
            }
        )
        return spec

    @classmethod
    def from_css_string(cls, css_text: str, brand_name: str = "Extracted Brand") -> BrandTokensSpec:
        """Parse CSS custom properties into a BrandTokensSpec."""
        matches = CSS_VAR_RE.findall(css_text)
        semantic_colors: Dict[str, Any] = {}
        spacings: Dict[str, Any] = {}
        font_display: Optional[str] = None
        font_body: Optional[str] = None

        for var_name, var_val in matches:
            var_val = var_val.strip()

            # 1. Fonts
            if "font-heading-family" in var_name or "font-display" in var_name:
                font_display = var_val.strip("'\"")
            elif "font-body-family" in var_name or "font-text" in var_name:
                font_body = var_val.strip("'\"")

            # 2. Colors
            hex_color = _normalize_color_to_hex(var_val)
            if "color" in var_name or "button-" in var_name or "bg-" in var_name or hex_color:
                clean_name = var_name.replace("color-", "").replace("color_", "")
                color_val = hex_color or var_val
                semantic_colors[clean_name] = {"$value": color_val, "$type": "color"}

                # Semantic Aliasing
                if clean_name in ("background", "bg", "surface") and "surface-primary" not in semantic_colors:
                    semantic_colors["surface-primary"] = {"$value": color_val, "$type": "color"}
                elif clean_name in ("foreground", "text") and "text-primary" not in semantic_colors:
                    semantic_colors["text-primary"] = {"$value": color_val, "$type": "color"}
                elif clean_name in ("accent", "button", "button-primary-bg", "primary") and "action-primary" not in semantic_colors:
                    semantic_colors["action-primary"] = {"$value": color_val, "$type": "color"}
                elif clean_name in ("button-text", "button-primary-text") and "action-primary-text" not in semantic_colors:
                    semantic_colors["action-primary-text"] = {"$value": color_val, "$type": "color"}
                elif clean_name in ("secondary-button", "button-secondary-bg", "accent-2") and "action-secondary" not in semantic_colors:
                    semantic_colors["action-secondary"] = {"$value": color_val, "$type": "color"}

            # 3. Spacing and Radii (exclude letter-spacing and word-spacing)
            elif (
                ("space" in var_name or "spacing" in var_name or "gap" in var_name or "corner" in var_name or "radius" in var_name)
                and "letter" not in var_name
                and "word" not in var_name
            ):
                clean_name = var_name.replace("spacing-", "").replace("space-", "").replace("corner-", "radius-")
                # Parse numeric part if present
                m = re.search(r"^([\d.]+)", var_val)
                if m:
                    try:
                        spacings[clean_name] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
                    except ValueError:
                        spacings[clean_name] = var_val
                else:
                    spacings[clean_name] = var_val

        # Provide sensible defaults if not all found
        if "surface-primary" not in semantic_colors:
            semantic_colors["surface-primary"] = {"$value": "#FFFFFF", "$type": "color"}
        if "text-primary" not in semantic_colors:
            semantic_colors["text-primary"] = {"$value": "#111827", "$type": "color"}
        if "action-primary" not in semantic_colors:
            semantic_colors["action-primary"] = {"$value": "#0F766E", "$type": "color"}
        if "action-primary-text" not in semantic_colors:
            semantic_colors["action-primary-text"] = {"$value": "#FFFFFF", "$type": "color"}

        meta = BrandMeta(brand_name=brand_name)
        if font_display:
            meta.font_family_display = font_display
        if font_body:
            meta.font_family_body = font_body

        return BrandTokensSpec(
            meta=meta,
            semantic={"color": semantic_colors},
            spacing=spacings or {"base": 8, "sm": 8, "md": 16, "lg": 24, "xl": 32},
        )

    @classmethod
    def from_figma_variables(
        cls,
        figma_json: Dict[str, Any],
        brand_name: str = "Figma Extracted Brand"
    ) -> BrandTokensSpec:
        """
        Parses Figma Variables JSON (W3C DTCG / Tokens Studio format)
        and reconstructs a valid BrandTokensSpec.
        """
        spec = BrandTokensSpec(meta=BrandMeta(brand_name=brand_name))
        collections = figma_json.get("collections", [])
        for col in collections:
            for var in col.get("variables", []):
                name = var.get("name", "")
                val = var.get("valuesByMode", {}).get("Default")
                if not val:
                    continue
                if name.startswith("color/"):
                    token_key = name.replace("color/", "")
                    spec.semantic.setdefault("color", {})[token_key] = {
                        "$value": str(val),
                        "$type": "color"
                    }
                elif name.startswith("spacing/"):
                    token_key = name.replace("spacing/", "")
                    try:
                        spec.spacing[token_key] = float(val) if "." in str(val) else int(val)
                    except (ValueError, TypeError):
                        pass
        return spec

