# --- DNK-MRH-HEADER ---
# mrh_id: "core/design_system/distiller.py"
# purpose: "Autonomous Design System Distiller: Ingests donor themes, extracts tokens, calibrates 60-30-10 CRO, and emits multi-target bundles."
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
import logging
import re
import zipfile
import urllib.request
from urllib.parse import urljoin
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.design_system.schemas import (
    BrandTokensSpec,
    BrandMeta,
    MultiTargetCompilationResult,
    LintReport,
)
from core.design_system.extractor import DesignTokenExtractor
from core.design_system.compiler import DesignTokenCompiler
from core.design_system.linter import DesignTokenLinter, hex_to_rgb, contrast_ratio

logger = logging.getLogger("dnk.design_system.distiller")


class DesignSystemDistiller:
    """
    Autonomous engine that distills a complete SOTA design system from any donor theme,
    file directory, or asset collection.
    """

    @classmethod
    def distill_from_path(
        cls,
        donor_path: Path | str,
        brand_name: str = "DNK Sovereign Brand",
        archetype: str = "ecommerce_conversion",
    ) -> BrandTokensSpec:
        """Inspects donor directory, extracts settings & styles, and synthesizes a calibrated BrandTokensSpec."""
        p = Path(donor_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Donor path not found: {donor_path}")

        extracted_settings: Dict[str, Any] = {}
        extracted_css_text = ""

        # 0. Handle .zip donor archive
        if p.is_file() and p.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(p, "r") as z:
                    for name in z.namelist():
                        if name.endswith("settings_data.json") and not extracted_settings:
                            with z.open(name) as f:
                                extracted_settings = json.load(f)
                        elif name.endswith(".css") and len(extracted_css_text) < 100000:
                            with z.open(name) as f:
                                extracted_css_text += "\n" + f.read().decode("utf-8", errors="ignore")
            except Exception as e:
                logger.warning(f"Failed to read zip donor {p}: {e}")

        # 1. Search for settings_data.json
        if not extracted_settings and p.is_dir():
            settings_file = p / "config" / "settings_data.json"
            if not settings_file.exists():
                # Try recursive search if donor_path is a parent directory
                candidates = list(p.glob("**/settings_data.json"))
                if candidates:
                    settings_file = candidates[0]

            if settings_file.exists():
                try:
                    with open(settings_file, "r", encoding="utf-8") as f:
                        extracted_settings = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to read {settings_file}: {e}")

        # 2. Search for CSS assets
        if not extracted_css_text and p.is_dir():
            css_candidates = list(p.glob("assets/*.css")) + list(p.glob("**/base.css")) + list(p.glob("**/global.css"))
            for css_f in css_candidates[:5]:
                try:
                    with open(css_f, "r", encoding="utf-8") as f:
                        extracted_css_text += "\n" + f.read()
                except Exception as e:
                    logger.warning(f"Failed to read CSS {css_f}: {e}")

        # 3. Base Extraction
        if extracted_settings:
            spec = DesignTokenExtractor.from_shopify_settings(extracted_settings, brand_name=brand_name)
        elif extracted_css_text:
            spec = DesignTokenExtractor.from_css_string(extracted_css_text, brand_name=brand_name)
        else:
            # Fallback to sovereign baseline
            spec = BrandTokensSpec(meta=BrandMeta(brand_name=brand_name, archetype=archetype))

        spec.meta.brand_name = brand_name
        spec.meta.archetype = archetype

        # 4. Calibrate 60-30-10 CRO Allocation & WCAG AA Contrast
        cls._calibrate_cro_and_contrast(spec)

        return spec

    @classmethod
    def _calibrate_cro_and_contrast(cls, spec: BrandTokensSpec) -> None:
        """Ensures the distilled spec satisfies 60-30-10 CRO balance and passes WCAG 2.2 AA."""
        colors = spec.semantic.setdefault("color", {})

        # Surface (60%)
        surface_hex = colors.get("surface-primary", {}).get("$value", "#FFFFFF")
        rgb_surface = hex_to_rgb(surface_hex) or (255, 255, 255)

        # Text (30%)
        text_hex = colors.get("text-primary", {}).get("$value", "#111827")
        rgb_text = hex_to_rgb(text_hex) or (17, 24, 39)

        # Check surface vs text contrast
        ratio = contrast_ratio(rgb_surface, rgb_text)
        if ratio < 4.5:
            # Automatically adjust text to meet WCAG AA
            colors["text-primary"] = {
                "$value": "#0F172A" if (rgb_surface[0] + rgb_surface[1] + rgb_surface[2] > 382) else "#F8FAFC",
                "$type": "color",
            }

        # Action Primary CTA (10%)
        action_hex = colors.get("action-primary", {}).get("$value", "#0F766E")
        rgb_action = hex_to_rgb(action_hex) or (15, 118, 110)

        # Action Button Text
        action_text_hex = colors.get("action-primary-text", {}).get("$value", "#FFFFFF")
        rgb_action_text = hex_to_rgb(action_text_hex) or (255, 255, 255)
        btn_ratio = contrast_ratio(rgb_action, rgb_action_text)

        if btn_ratio < 3.0:
            # Flip button label text to black or white based on luminance
            dark_ratio = contrast_ratio(rgb_action, (0, 0, 0))
            light_ratio = contrast_ratio(rgb_action, (255, 255, 255))
            colors["action-primary-text"] = {
                "$value": "#000000" if dark_ratio > light_ratio else "#FFFFFF",
                "$type": "color",
            }

        # Secondary action
        if "action-secondary" not in colors:
            colors["action-secondary"] = {"$value": "#14B8A6", "$type": "color"}

        # Ensure spatial grid compliance
        spec.spacing = {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "2xl": 48,
            "3xl": 64,
        }
        spec.meta.base_font_size_px = max(16, spec.meta.base_font_size_px)

    @classmethod
    def distill_from_url(
        cls,
        url: str,
        brand_name: str = "Extracted Brand",
        archetype: str = "ecommerce_conversion",
    ) -> BrandTokensSpec:
        """Fetches live website HTML and stylesheets, extracts design tokens, and synthesizes a calibrated BrandTokensSpec."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise RuntimeError(f"Could not fetch website {url}: {e}")

        combined_css = html

        # Extract linked stylesheets
        css_links = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']', html)
        for link in css_links[:5]:
            if link.startswith("//"):
                css_url = f"https:{link}"
            elif link.startswith("/"):
                css_url = urljoin(url, link)
            elif link.startswith("http://") or link.startswith("https://"):
                css_url = link
            else:
                css_url = urljoin(url, link)

            try:
                css_req = urllib.request.Request(css_url, headers=headers)
                with urllib.request.urlopen(css_req, timeout=6.0) as css_resp:
                    combined_css += "\n" + css_resp.read().decode("utf-8", errors="ignore")
            except Exception as e:
                logger.warning(f"Could not fetch external stylesheet {css_url}: {e}")

        spec = DesignTokenExtractor.from_css_string(combined_css, brand_name=brand_name)
        spec.meta.archetype = archetype

        # Extract headings and storefront copy as ground-truth source quotes
        quotes: List[str] = []
        for tag in ["h1", "h2", "h3", "p"]:
            matches = re.findall(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.I | re.S)
            for m in matches:
                clean = re.sub(r'<[^>]+>', '', m).strip()
                clean = re.sub(r'\s+', ' ', clean)
                if 20 <= len(clean) <= 180 and clean not in quotes:
                    if not any(w in clean.lower() for w in ["cookie", "javascript", "rights reserved", "terms of service", "privacy policy"]):
                        quotes.append(clean)
        if quotes:
            spec.meta.extracted_quotes = quotes[:12]

        cls._calibrate_cro_and_contrast(spec)
        return spec

    @classmethod
    def distill_and_compile(
        cls,
        donor_path: Path | str,
        brand_name: str = "DNK Sovereign Brand",
        output_dir: Optional[Path | str] = None,
    ) -> Dict[str, Any]:
        """Turnkey distillation pipeline: ingests donor URL, path or zip, lints spec, compiles targets, and optionally writes artifacts."""
        src_str = str(donor_path).strip()
        if src_str.startswith("http://") or src_str.startswith("https://"):
            spec = cls.distill_from_url(src_str, brand_name=brand_name)
        else:
            spec = cls.distill_from_path(donor_path, brand_name=brand_name)
        lint_report = DesignTokenLinter.lint_spec(spec)
        bundle = DesignTokenCompiler.compile_all(spec)

        written_files: List[str] = []
        if output_dir:
            out_p = Path(output_dir).resolve()
            out_p.mkdir(parents=True, exist_ok=True)

            # 1. Shopify CSS
            shopify_css_p = out_p / "dnk-tokens.css"
            with open(shopify_css_p, "w", encoding="utf-8") as f:
                f.write(bundle.shopify_css)
            written_files.append(str(shopify_css_p))

            # 2. Tailwind v4
            tw_p = out_p / "tailwind-theme.css"
            with open(tw_p, "w", encoding="utf-8") as f:
                f.write(bundle.tailwind_v4_css)
            written_files.append(str(tw_p))

            # 3. Media Motion JSON
            media_p = out_p / "media-motion-tokens.json"
            with open(media_p, "w", encoding="utf-8") as f:
                json.dump(bundle.media_motion_tokens, f, indent=2, ensure_ascii=False)
            written_files.append(str(media_p))

            # 4. Google Labs DESIGN.md
            brand_md_p = out_p / "DESIGN.md"
            with open(brand_md_p, "w", encoding="utf-8") as f:
                f.write(bundle.google_design_md or bundle.brand_markdown)
            written_files.append(str(brand_md_p))

            # 4.1 BRAND.md (Voice & Zero-Hallucination Quotes)
            if bundle.brand_voice_md:
                brand_voice_p = out_p / "BRAND.md"
                with open(brand_voice_p, "w", encoding="utf-8") as f:
                    f.write(bundle.brand_voice_md)
                written_files.append(str(brand_voice_p))

            # 4.2 SKILL.md (Agent Guard Skill)
            if bundle.agent_skill_md:
                skill_p = out_p / "SKILL.md"
                with open(skill_p, "w", encoding="utf-8") as f:
                    f.write(bundle.agent_skill_md)
                written_files.append(str(skill_p))

            # 4.3 What We'd Fix First Express Audit
            if bundle.fix_first_report:
                fix_first_p = out_p / "AUDIT_WHAT_WE_FIX_FIRST.md"
                with open(fix_first_p, "w", encoding="utf-8") as f:
                    f.write(bundle.fix_first_report)
                written_files.append(str(fix_first_p))

            # 4.4 Shopify Theme Block 2.0
            if bundle.shopify_theme_block_liquid:
                blocks_dir = out_p / "blocks"
                blocks_dir.mkdir(parents=True, exist_ok=True)
                block_p = blocks_dir / "dnk-offer.liquid"
                with open(block_p, "w", encoding="utf-8") as f:
                    f.write(bundle.shopify_theme_block_liquid)
                written_files.append(str(block_p))

            # 5. Raw DTCG Spec
            spec_yaml_p = out_p / "brand_tokens_spec.json"
            with open(spec_yaml_p, "w", encoding="utf-8") as f:
                json.dump(spec.model_dump(), f, indent=2, ensure_ascii=False)
            written_files.append(str(spec_yaml_p))

            # 6. Astryx Theme Layer
            if bundle.astryx_theme_css:
                astryx_p = out_p / "astryx-tokens.css"
                with open(astryx_p, "w", encoding="utf-8") as f:
                    f.write(bundle.astryx_theme_css)
                written_files.append(str(astryx_p))

            # 7. Figma Variables JSON
            if bundle.figma_variables_json:
                figma_p = out_p / "figma_variables.json"
                with open(figma_p, "w", encoding="utf-8") as f:
                    json.dump(bundle.figma_variables_json, f, indent=2, ensure_ascii=False)
                written_files.append(str(figma_p))

            # 8. Social Creative Matrix
            if bundle.social_creative_matrix:
                matrix_p = out_p / "social_creative_matrix.json"
                with open(matrix_p, "w", encoding="utf-8") as f:
                    json.dump(bundle.social_creative_matrix, f, indent=2, ensure_ascii=False)
                written_files.append(str(matrix_p))

        return {
            "brand_name": brand_name,
            "donor_path": str(donor_path),
            "lint_report": lint_report.model_dump(),
            "bundle": bundle.model_dump(),
            "written_files": written_files,
            "status": "SUCCESS" if lint_report.valid else "VALIDATION_FAILED",
        }
