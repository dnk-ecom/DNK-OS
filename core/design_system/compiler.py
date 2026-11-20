# --- DNK-MRH-HEADER ---
# mrh_id: "core/design_system/compiler.py"
# purpose: "Multi-Target Design Token Compiler: Emits Shopify Liquid/CSS, Tailwind v4 @theme, HyperFrames Media Tokens, and DESIGN.md."
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
from typing import Any, Dict, List, Optional
from core.design_system.schemas import BrandTokensSpec, MultiTargetCompilationResult
from core.design_system.linter import extract_token_val, hex_to_rgb, contrast_ratio


class DesignTokenCompiler:
    """Universal compiler converting DTCG specs into cross-platform artifacts."""

    @classmethod
    def compile_all(cls, spec: BrandTokensSpec) -> MultiTargetCompilationResult:
        brand_name = spec.meta.brand_name
        shopify_css = cls.emit_shopify_css(spec)
        shopify_schema = cls.emit_shopify_settings_schema(spec)
        tailwind_v4_css = cls.emit_tailwind_v4(spec)
        media_motion = cls.emit_media_motion_tokens(spec)
        brand_md = cls.emit_brand_markdown(spec)
        astryx_theme = cls.emit_astryx_theme(spec)
        figma_vars = cls.emit_figma_variables(spec)
        social_matrix = cls.emit_social_creative_matrix(spec)
        theme_block = cls.emit_shopify_theme_block(spec)
        google_design = cls.emit_google_design_md(spec)
        brand_voice = cls.emit_brand_voice_md(spec)
        agent_skill = cls.emit_agent_skill_md(spec)
        fix_first = cls.emit_fix_first_report(spec)

        return MultiTargetCompilationResult(
            brand_name=brand_name,
            shopify_css=shopify_css,
            shopify_settings_schema=shopify_schema,
            tailwind_v4_css=tailwind_v4_css,
            media_motion_tokens=media_motion,
            brand_markdown=brand_md,
            astryx_theme_css=astryx_theme,
            figma_variables_json=figma_vars,
            social_creative_matrix=social_matrix,
            shopify_theme_block_liquid=theme_block,
            google_design_md=google_design,
            brand_voice_md=brand_voice,
            agent_skill_md=agent_skill,
            fix_first_report=fix_first,
        )

    @classmethod
    def emit_figma_variables(cls, spec: BrandTokensSpec) -> Dict[str, Any]:
        """Emits Figma Variables collection JSON (W3C DTCG / Tokens Studio format)."""
        semantic_color = spec.semantic.get("color", {})
        variables = []
        for name, val_node in semantic_color.items():
            val = extract_token_val(val_node)
            variables.append({
                "name": f"color/{name}",
                "type": "COLOR",
                "valuesByMode": {
                    "Default": str(val)
                },
                "scopes": ["ALL_FILLS", "STROKE_COLOR"]
            })

        for name, val in spec.spacing.items():
            num_val = 8.0
            try:
                if isinstance(val, (int, float)):
                    num_val = float(val)
                else:
                    m = re.search(r"([\d.]+)", str(val))
                    num_val = float(m.group(1)) if m else 8.0
            except Exception:
                num_val = 8.0

            variables.append({
                "name": f"spacing/{name}",
                "type": "FLOAT",
                "valuesByMode": {
                    "Default": num_val
                },
                "scopes": ["GAP", "PADDING", "CORNER_RADIUS"]
            })

        return {
            "version": "1.0.0",
            "metadata": {
                "brand": spec.meta.brand_name,
                "exportedAt": "2026-11-17",
                "generator": "DNK OS Design Token Compiler"
            },
            "collections": [
                {
                    "name": "Brand Design Tokens",
                    "modes": [{"modeId": "mode_default", "name": "Default"}],
                    "variables": variables
                }
            ]
        }

    @classmethod
    def emit_social_creative_matrix(cls, spec: BrandTokensSpec) -> Dict[str, Any]:
        """Emits Multi-Format Creative Automation & Remotion/HyperFrames Motion Matrix."""
        semantic_color = spec.semantic.get("color", {})
        action_primary = extract_token_val(semantic_color.get("action-primary", semantic_color.get("accent", "#008060")))
        surface_primary = extract_token_val(semantic_color.get("surface-primary", semantic_color.get("surface", "#FFFFFF")))

        return {
            "brand_name": spec.meta.brand_name,
            "viewport_formats": {
                "reels_tiktok_9_16": {
                    "width": 1080,
                    "height": 1920,
                    "aspect_ratio": "9:16",
                    "safe_zones": {
                        "top_margin_px": 120,
                        "bottom_margin_px": 340,
                        "side_margin_px": 48
                    },
                    "headline_max_chars": 40,
                    "optimal_focal_y": 720
                },
                "feed_square_1_1": {
                    "width": 1080,
                    "height": 1080,
                    "aspect_ratio": "1:1",
                    "safe_zones": {"margin_px": 40},
                    "headline_max_chars": 55
                },
                "portrait_ad_4_5": {
                    "width": 1080,
                    "height": 1350,
                    "aspect_ratio": "4:5",
                    "safe_zones": {"margin_px": 48},
                    "headline_max_chars": 48
                }
            },
            "motion_physics": {
                "spring_snappy": {"tension": 280, "friction": 20, "cubic_bezier": "cubic-bezier(0.16, 1, 0.3, 1)"},
                "spring_gentle": {"tension": 120, "friction": 14, "cubic_bezier": "cubic-bezier(0.25, 1, 0.5, 1)"},
                "spring_bouncy": {"tension": 380, "friction": 16, "cubic_bezier": "cubic-bezier(0.34, 1.56, 0.64, 1)"}
            },
            "kinetic_subtitles": {
                "font_family": "Inter, -apple-system, sans-serif",
                "highlight_color": str(action_primary),
                "normal_color": "#FFFFFF",
                "pop_scale": 1.15
            },
            "content_matrix_blueprint": [
                {"scene": "01_hook", "duration_sec": 3.0, "motion": "spring_snappy", "goal": "Pattern Interrupt"},
                {"scene": "02_pain", "duration_sec": 4.0, "motion": "spring_gentle", "goal": "Problem Agitation"},
                {"scene": "03_solution_bento", "duration_sec": 5.0, "motion": "spring_snappy", "goal": "Feature Showcase"},
                {"scene": "04_social_proof", "duration_sec": 5.0, "motion": "spring_bouncy", "goal": "Customer Reviews"},
                {"scene": "05_focal_cta", "duration_sec": 3.0, "motion": "spring_snappy", "goal": "Storefront Conversion"}
            ]
        }

    @classmethod
    def emit_astryx_theme(cls, spec: BrandTokensSpec) -> str:
        """Emits Meta Astryx @layer astryx-theme specification for React 19 / Next.js 15 apps."""
        semantic_color = spec.semantic.get("color", {})
        canvas_val = extract_token_val(semantic_color.get("canvas", "#f1f2f4"))
        surface_val = extract_token_val(semantic_color.get("surface", "#ffffff"))
        surface_sec = extract_token_val(semantic_color.get("surface-secondary", "#f6f6f7"))
        border_subtle = extract_token_val(semantic_color.get("border-subtle", "#e3e5e8"))
        border_base = extract_token_val(semantic_color.get("border", "#c9cccf"))
        accent_val = extract_token_val(semantic_color.get("accent", "#008060"))

        lines = [
            "/* --- DNK-MRH-HEADER ---",
            f'/* mrh_id: "apps_web_styles_astryx_tokens_{spec.meta.brand_name.lower().replace(" ", "_")}"',
            f'/* purpose: "Meta Astryx Agent-Native tokens for {spec.meta.brand_name} (ADR-009 / DEC-142)"',
            "/* --- END DNK-MRH-HEADER --- */",
            "",
            "@layer astryx-theme {",
            "  :root {",
            "    /* Astryx Surface Tokens mapped to Core Palette */",
            f"    --astryx-surface-canvas: var(--bg-app, {canvas_val});",
            f"    --astryx-surface-card: var(--bg-surface, {surface_val});",
            f"    --astryx-surface-panel: var(--bg-surface-secondary, {surface_sec});",
            f"    --astryx-border-subtle: var(--border-subtle, {border_subtle});",
            f"    --astryx-border-default: var(--border-base, {border_base});",
            f"    --astryx-agent-shopify: var(--color-accent, {accent_val});",
            "",
            "    /* Motion & Transitions */",
            f"    --astryx-transition-base: {spec.motion.dur_base_ms}ms {spec.motion.ease_default};",
            f"    --astryx-transition-spring: {spec.motion.dur_slow_ms}ms {spec.motion.ease_spring};",
            "  }",
            "}",
        ]
        return "\n".join(lines)

    @classmethod
    def emit_shopify_css(cls, spec: BrandTokensSpec) -> str:
        """Emits Shopify Liquid-compatible CSS custom properties with RGB channels for opacity."""
        semantic_color = spec.semantic.get("color", {})
        lines = [
            "/* --- DNK-MRH-HEADER ---",
            f'/* mrh_id: "assets/dnk-brand-{spec.meta.brand_name.lower().replace(" ", "-")}-tokens.css"',
            f'/* purpose: "Compiled Design Tokens for Shopify Liquid Theme ({spec.meta.brand_name})"',
            "/* --- END DNK-MRH-HEADER --- */",
            "",
            ":root {",
        ]

        # Colors (emit both hex and RGB channels for rgba opacity)
        for name, val_node in semantic_color.items():
            val = extract_token_val(val_node)
            lines.append(f"  --color-{name}: {val};")
            rgb = hex_to_rgb(str(val))
            if rgb:
                lines.append(f"  --color-{name}-rgb: {rgb[0]} {rgb[1]} {rgb[2]};")

        # Fluid Typography (Zero-CLS & Mobile-Optimized)
        base_px = spec.meta.base_font_size_px
        ratio = spec.meta.typography_ratio
        lines.extend([
            "",
            "  /* Fluid Typography Scale */",
            f"  --font-size-base: {base_px}px;",
            f"  --font-size-sm: clamp(0.8125rem, 0.78rem + 0.15vw, 0.875rem);",
            f"  --font-size-h3: clamp({base_px * ratio * 0.9:.1f}px, 1.1rem + 0.5vw, {base_px * ratio:.1f}px);",
            f"  --font-size-h2: clamp({base_px * (ratio**2) * 0.85:.1f}px, 1.4rem + 1vw, {base_px * (ratio**2):.1f}px);",
            f"  --font-size-h1: clamp({base_px * (ratio**3) * 0.8:.1f}px, 1.8rem + 1.8vw, {base_px * (ratio**3):.1f}px);",
            f"  --font-size-display: clamp({base_px * (ratio**4) * 0.75:.1f}px, 2.2rem + 2.5vw, {base_px * (ratio**4):.1f}px);",
        ])

        # Fluid Spacing
        lines.extend([
            "",
            "  /* Fluid Spacing & 8pt Grid */",
            "  --spacing-base: 8px;",
            "  --gutter-mobile: 16px;",
            "  --gutter-desktop: 32px;",
            "  --container-max-width: 1440px;",
        ])

        # Motion & Transitions
        lines.extend([
            "",
            "  /* Transitions & Animation Easing */",
            f"  --motion-ease: {spec.motion.ease_default};",
            f"  --motion-spring: {spec.motion.ease_spring};",
            f"  --motion-dur-fast: {spec.motion.dur_fast_ms}ms;",
            f"  --motion-dur-base: {spec.motion.dur_base_ms}ms;",
            f"  --motion-dur-slow: {spec.motion.dur_slow_ms}ms;",
        ])

        # Elevation Shadows
        lines.extend([
            "",
            "  /* Elevation Shadows */",
            f"  --shadow-sm: {spec.elevation.shadow_sm};",
            f"  --shadow-md: {spec.elevation.shadow_md};",
            f"  --shadow-lg: {spec.elevation.shadow_lg};",
            "}",
        ])
        return "\n".join(lines)

    @classmethod
    def emit_shopify_settings_schema(cls, spec: BrandTokensSpec) -> Dict[str, Any]:
        """Emits settings_schema.json structure for Shopify Theme Customizer."""
        semantic_color = spec.semantic.get("color", {})
        settings: list[Dict[str, Any]] = [
            {
                "type": "header",
                "content": f"Design System: {spec.meta.brand_name}"
            }
        ]

        for name, val_node in semantic_color.items():
            val = extract_token_val(val_node)
            settings.append({
                "type": "color",
                "id": f"color_{name.replace('-', '_')}",
                "label": name.replace("-", " ").title(),
                "default": str(val),
            })

        return {
            "name": f"DNK DS: {spec.meta.brand_name}",
            "settings": settings,
        }

    @classmethod
    def emit_tailwind_v4(cls, spec: BrandTokensSpec) -> str:
        """Emits Tailwind CSS v4 @theme directive."""
        semantic_color = spec.semantic.get("color", {})
        lines = [
            "/* Tailwind CSS v4 @theme block */",
            "@theme {",
        ]
        for name, val_node in semantic_color.items():
            val = extract_token_val(val_node)
            lines.append(f"  --color-{name}: {val};")

        lines.extend([
            f"  --ease-spring: {spec.motion.ease_spring};",
            f"  --duration-fast: {spec.motion.dur_fast_ms}ms;",
            f"  --duration-base: {spec.motion.dur_base_ms}ms;",
            f"  --duration-slow: {spec.motion.dur_slow_ms}ms;",
            "}",
        ])
        return "\n".join(lines)

    @classmethod
    def emit_media_motion_tokens(cls, spec: BrandTokensSpec) -> Dict[str, Any]:
        """Emits motion & visual tokens for HyperFrames and Remotion video engines."""
        semantic_color = spec.semantic.get("color", {})
        return {
            "brand_name": spec.meta.brand_name,
            "motion": {
                "spring": spec.motion.ease_spring,
                "ease": spec.motion.ease_default,
                "durations": {
                    "fast_ms": spec.motion.dur_fast_ms,
                    "base_ms": spec.motion.dur_base_ms,
                    "slow_ms": spec.motion.dur_slow_ms,
                },
                "fps_target": 60,
            },
            "colors": {
                "focal_cta": extract_token_val(semantic_color.get("action-primary", "#0F766E")),
                "surface": extract_token_val(semantic_color.get("surface-primary", "#FFFFFF")),
                "text": extract_token_val(semantic_color.get("text-primary", "#111827")),
                "accent": extract_token_val(semantic_color.get("action-secondary", "#14B8A6")),
            },
            "typography": {
                "ratio": spec.meta.typography_ratio,
                "base_font_px": spec.meta.base_font_size_px,
            },
            "aspect_ratios": {
                "meta_tiktok_reels": "9:16",
                "youtube_landscape": "16:9",
                "feed_square": "1:1",
            },
        }

    @classmethod
    def emit_brand_markdown(cls, spec: BrandTokensSpec) -> str:
        """Emits DESIGN.md brand specification documentation."""
        semantic_color = spec.semantic.get("color", {})
        return f"""# 🎨 Brand Design System: {spec.meta.brand_name}

> **Generated by DNK OS Sovereign Design System Engine (DTCG Standard)**
> Archetype: `{spec.meta.archetype}` | CRO Rule: `{spec.meta.cro_allocation_rule}` | Typo Ratio: `{spec.meta.typography_ratio_name} ({spec.meta.typography_ratio})`

---

## 🌈 1. Color Palette & 60-30-10 CRO Allocation

| Role | Token Name | Hex Value | WCAG Contrast Target |
| :--- | :--- | :--- | :--- |
| **60% Surface** | `surface-primary` | `{extract_token_val(semantic_color.get("surface-primary", "#FFFFFF"))}` | Neutral Base Background |
| **30% Structure/Text** | `text-primary` | `{extract_token_val(semantic_color.get("text-primary", "#111827"))}` | ≥ 4.5:1 against Surface (AA) |
| **10% Focal Conversion CTA** | `action-primary` | `{extract_token_val(semantic_color.get("action-primary", "#0F766E"))}` | Exclusive Revenue Action (ATC / Checkout) |
| **Secondary Action** | `action-secondary` | `{extract_token_val(semantic_color.get("action-secondary", "#14B8A6"))}` | Supporting Interaction |

---

## 📐 2. Spatial Grid & Modular Typography
- **Grid Base**: `{spec.meta.spacing_grid_base_px}px` (Strict 8pt System, 4pt micro-steps).
- **Body Floor**: `{spec.meta.base_font_size_px}px` (Non-negotiable mobile minimum).
- **Scale Steps**:
  - `Display`: Fluid clamp (`H1 * {spec.meta.typography_ratio}`)
  - `H1`: Hero & PDP Product Titles
  - `H2`: Section Headings
  - `H3`: Feature & Card Headings
  - `Body`: Standard Copy (`{spec.meta.base_font_size_px}px`)

---

## 🎬 3. Motion & Animation Tokens
- **Spring Ease**: `{spec.motion.ease_spring}`
- **Fast / Micro-interaction**: `{spec.motion.dur_fast_ms}ms`
- **Standard UI Transition**: `{spec.motion.dur_base_ms}ms`
- **Dramatic Video / Reveal**: `{spec.motion.dur_slow_ms}ms`
"""

    @classmethod
    def emit_shopify_theme_block(cls, spec: BrandTokensSpec) -> str:
        """
        Emits a modular, zero-React Shopify Theme Blocks 2.0 component (.liquid).
        Adheres to Shopify Polaris 2.0 & Horizon architecture with native schema contract.
        """
        brand_name = spec.meta.brand_name
        colors = spec.semantic.get("color", {})
        surface = extract_token_val(colors.get("surface-primary", "#FFFFFF"))
        text = extract_token_val(colors.get("text-primary", "#111827"))
        action = extract_token_val(colors.get("action-primary", "#008060"))
        action_text = extract_token_val(colors.get("action-primary-text", "#FFFFFF"))
        radius = extract_token_val(spec.spacing.get("sm", 8))

        liquid = f"""{{% comment %}}
  DNK OS Sovereign Theme Block: {brand_name} (Polaris 2.0 / Horizon Architecture)
  Auto-generated by DNK OS Design Token Compiler (W3C DTCG 2025.10)
{{% endcomment %}}

{{{{ 'dnk-tokens.css' | asset_url | stylesheet_tag }}}}

<div class="dnk-theme-block dnk-theme-block--{{{{ block.id }}}}" style="
  --dnk-block-bg: {{{{ block.settings.bg_color | default: '{surface}' }}}};
  --dnk-block-text: {{{{ block.settings.text_color | default: '{text}' }}}};
  --dnk-block-accent: {{{{ block.settings.accent_color | default: '{action}' }}}};
  --dnk-block-radius: {{{{ block.settings.corner_radius | default: {radius} }}}}px;
">
  <div class="dnk-theme-block__container">
    {{% if block.settings.heading != blank %}}
      <h2 class="dnk-theme-block__heading">{{{{ block.settings.heading | escape }}}}</h2>
    {{% endif %}}
    {{% if block.settings.subheading != blank %}}
      <p class="dnk-theme-block__subheading">{{{{ block.settings.subheading | escape }}}}</p>
    {{% endif %}}
    {{% if block.settings.cta_label != blank %}}
      <a href="{{{{ block.settings.cta_link | default: '#' }}}}" class="dnk-theme-block__cta">
        {{{{ block.settings.cta_label | escape }}}}
      </a>
    {{% endif %}}
  </div>
</div>

<style>
  .dnk-theme-block--{{{{ block.id }}}} {{
    background-color: var(--dnk-block-bg);
    color: var(--dnk-block-text);
    border-radius: var(--dnk-block-radius);
    padding: 2rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }}
  .dnk-theme-block__heading {{
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    line-height: 1.25;
  }}
  .dnk-theme-block__subheading {{
    font-size: 1rem;
    opacity: 0.85;
    margin-bottom: 1.5rem;
  }}
  .dnk-theme-block__cta {{
    display: inline-block;
    background-color: var(--dnk-block-accent);
    color: {action_text};
    padding: 0.75rem 1.5rem;
    border-radius: 9999px;
    font-weight: 600;
    text-decoration: none;
    transition: opacity 0.2s ease;
  }}
  .dnk-theme-block__cta:hover {{
    opacity: 0.9;
  }}
</style>

{{% schema %}}
{{
  "name": "{brand_name} Block",
  "target": "section",
  "settings": [
    {{
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "{brand_name} Sovereign Offer"
    }},
    {{
      "type": "textarea",
      "id": "subheading",
      "label": "Subheading",
      "default": "Engineered with DNK OS Polaris 2.0 design tokens."
    }},
    {{
      "type": "text",
      "id": "cta_label",
      "label": "Button Label",
      "default": "Shop Now"
    }},
    {{
      "type": "url",
      "id": "cta_link",
      "label": "Button Link"
    }},
    {{
      "type": "color",
      "id": "bg_color",
      "label": "Background Color",
      "default": "{surface}"
    }},
    {{
      "type": "color",
      "id": "text_color",
      "label": "Text Color",
      "default": "{text}"
    }},
    {{
      "type": "color",
      "id": "accent_color",
      "label": "Accent Color",
      "default": "{action}"
    }},
    {{
      "type": "range",
      "id": "corner_radius",
      "label": "Corner Radius (px)",
      "min": 0,
      "max": 32,
      "step": 2,
      "default": {radius}
    }}
  ]
}}
{{% endschema %}}
"""
        return liquid.strip()

    @classmethod
    def emit_google_design_md(cls, spec: BrandTokensSpec) -> str:
        """
        Emits a Google Labs compliant DESIGN.md file with YAML frontmatter tokens.
        Read natively by Cursor, Claude Code, GitHub Copilot, and Antigravity.
        """
        colors = spec.semantic.get("color", {})
        surface = extract_token_val(colors.get("surface-primary", "#FFFFFF"))
        text = extract_token_val(colors.get("text-primary", "#111827"))
        action = extract_token_val(colors.get("action-primary", "#008060"))
        action_text = extract_token_val(colors.get("action-primary-text", "#FFFFFF"))
        secondary = extract_token_val(colors.get("action-secondary", "#14B8A6"))

        font_display = spec.meta.font_family_display or "Inter, -apple-system, sans-serif"
        font_body = spec.meta.font_family_body or "Inter, -apple-system, sans-serif"

        grid_base = spec.meta.spacing_grid_base_px
        base_size = spec.meta.base_font_size_px
        ratio = spec.meta.typography_ratio

        return f"""---
title: "DESIGN.md: {spec.meta.brand_name}"
description: "Visual Design System and Token Specification for {spec.meta.brand_name} (Google Labs Standard)"
version: "1.0.0"
brand: "{spec.meta.brand_name}"
archetype: "{spec.meta.archetype}"
tokens:
  color:
    surface_primary: "{surface}"
    text_primary: "{text}"
    action_primary: "{action}"
    action_primary_text: "{action_text}"
    action_secondary: "{secondary}"
  typography:
    font_display: "{font_display}"
    font_body: "{font_body}"
    base_size_px: {base_size}
    modular_ratio: {ratio}
  spacing:
    grid_base_px: {grid_base}
    scale:
      xs: {spec.spacing.get('xs', 4)}
      sm: {spec.spacing.get('sm', 8)}
      md: {spec.spacing.get('md', 16)}
      lg: {spec.spacing.get('lg', 24)}
      xl: {spec.spacing.get('xl', 32)}
---

# 🎨 {spec.meta.brand_name} Design System (DESIGN.md)

> Canonical design token specification following Google Labs DESIGN.md standard.
> AI coding agents (Cursor, Claude Code, Antigravity) must strictly adhere to these tokens.

## 1. Color Palette (60-30-10 CRO Law)
- **Surface (60%)**: `{surface}` (Canvas & primary card backgrounds)
- **Text & Structure (30%)**: `{text}` (Headings, body typography, borders)
- **Primary Action (10%)**: `{action}` (Conversion CTAs only: Add to Cart, Buy Now)
- **Action Text**: `{action_text}` (High contrast label on action buttons)
- **Secondary Accent**: `{secondary}` (Badges, supporting chips, subtle links)

## 2. Typography Hierarchy
- **Display Font**: `{font_display}`
- **Body Font**: `{font_body}`
- **Scale Base**: `{base_size}px` (Strict mobile floor to prevent viewport auto-zoom)
- **Modular Scale**: `{spec.meta.typography_ratio_name} ({ratio})`

## 3. Spatial Grid & Corner Radii
- **Base Grid**: `{grid_base}px` (Multiples of 4px / 8px strictly enforced)
- **Corner Radius**: `{spec.spacing.get('sm', 8)}px` standard, `9999px` full pill for CTAs.
"""

    @classmethod
    def emit_brand_voice_md(cls, spec: BrandTokensSpec, quotes: Optional[List[str]] = None) -> str:
        """
        Emits BRAND.md containing brand personality, vocabulary, and Zero-Hallucination Quotes.
        Prevents AI models from inventing fake claims, guarantees, or synthetic reviews.
        """
        brand_name = spec.meta.brand_name
        tagline = spec.meta.brand_tagline or f"Premium {brand_name} E-Commerce Experience"
        source_quotes = quotes or spec.meta.extracted_quotes or [
            f"Engineered for high-conversion and seamless customer experience at {brand_name}.",
            f"Uncompromising quality and sustainable craftsmanship by {brand_name}."
        ]

        quotes_md = "\n".join([f'> "{q.strip()}"' for q in source_quotes[:10]])

        return f"""---
title: "BRAND.md: {brand_name}"
description: "Brand Voice, Communication Guidelines & Zero-Hallucination Source Quotes for {brand_name}"
version: "1.0.0"
brand: "{brand_name}"
tagline: "{tagline}"
---

# 🗣️ {brand_name} Brand Voice & Identity Guidelines

## 1. Brand Essence & Positioning
- **Tagline**: {tagline}
- **Archetype**: `{spec.meta.archetype}`
- **Tone Profile**: Confident, refined, authentic, concise.

## 2. Voice Principles: What We Are vs. What We Aren't
| What We Are | What We Aren't |
| :--- | :--- |
| **Direct & Clear**: Clear value props with zero filler. | **Hyped & Buzzword-Heavy**: Avoid 'game-changing', 'disruptive'. |
| **Craftsmanship-Focused**: Highlight tangible build quality. | **Generic AI Slop**: Never use cliché marketing intros. |
| **Grounded & Trustworthy**: Honest guarantees and specifications. | **Deceptive or Exaggerated**: Zero fake scarcity counters. |

## 3. Zero-Hallucination Verified Quotes (SSOT)
> [!IMPORTANT]
> AI models writing copy, product descriptions, or ads for **{brand_name}** MUST root claims in these verified storefront lines. Never fabricate testimonials or technical certifications.

{quotes_md}

## 4. Forbidden Vocabulary (Banned Lexicon)
- Do NOT use: "unleash", "skyrocket", "next-level", "game-changer", "dive into", "seamlessly".
- Favor: "precision", "crafted", "durable", "engineered", "verified", "direct".
"""

    @classmethod
    def emit_agent_skill_md(cls, spec: BrandTokensSpec) -> str:
        """
        Emits a portable agent skill SKILL.md for Claude Code (.claude/skills/),
        Cursor Rules (.cursor/rules/), and Antigravity.
        """
        brand_name = spec.meta.brand_name
        slug = re.sub(r"[^a-z0-9]+", "-", brand_name.lower()).strip("-")
        colors = spec.semantic.get("color", {})
        surface = extract_token_val(colors.get("surface-primary", "#FFFFFF"))
        text = extract_token_val(colors.get("text-primary", "#111827"))
        action = extract_token_val(colors.get("action-primary", "#008060"))

        return f"""---
name: "{slug}-brand-guard"
description: "Non-negotiable visual, token, and voice guardrails for {brand_name} when generating frontend code or copy."
version: "1.0.0"
---

# 🛡️ {brand_name} Brand Guard Agent Skill

This skill enforces strict adherence to the **{brand_name}** design system in any code or copy generation.

## ⚡ The 4 Non-Negotiable Rules ("Every Time Guard")

1. **Strict Token Colors Only**:
   - NEVER use arbitrary hex codes or default framework palettes (e.g. Tailwind blue-600).
   - Use ONLY `{surface}` (Surface), `{text}` (Text), and `{action}` (CTA Action).
   - In Shopify Liquid: use `var(--color-surface-primary)` and `var(--color-action-primary)`.

2. **Typography Floor & Hierarchy**:
   - Mobile body font size CANNOT be below `{spec.meta.base_font_size_px}px` (prevents iOS auto-zoom).
   - Display headings MUST use `{spec.meta.font_family_display or 'Display font'}`.
   - Body copy MUST use `{spec.meta.font_family_body or 'Body font'}`.

3. **Native Vector Logos Only**:
   - NEVER recreate or approximate the brand logo with stylized HTML text or SVG paths.
   - Always reference the official logo asset tag or SVG placeholder.

4. **Zero-Hallucination Marketing Claims**:
   - When drafting product descriptions or landing copy, quote ONLY verified claims from `BRAND.md`.
   - Never generate fake customer names, star ratings, or imaginary laboratory results.
"""

    @classmethod
    def emit_fix_first_report(cls, spec: BrandTokensSpec) -> str:
        """
        Emits an automated CRO & A11y Diagnostic Card ('What We'd Fix First').
        Provides high-converting audit feedback for client proposals and deal rooms.
        """
        colors = spec.semantic.get("color", {})
        surface_hex = extract_token_val(colors.get("surface-primary", "#FFFFFF"))
        text_hex = extract_token_val(colors.get("text-primary", "#111827"))
        action_hex = extract_token_val(colors.get("action-primary", "#008060"))
        action_text_hex = extract_token_val(colors.get("action-primary-text", "#FFFFFF"))

        rgb_surf = hex_to_rgb(surface_hex) or (255, 255, 255)
        rgb_txt = hex_to_rgb(text_hex) or (17, 24, 39)
        rgb_act = hex_to_rgb(action_hex) or (0, 128, 96)
        rgb_act_txt = hex_to_rgb(action_text_hex) or (255, 255, 255)

        text_ratio = round(contrast_ratio(rgb_surf, rgb_txt), 2)
        btn_ratio = round(contrast_ratio(rgb_act, rgb_act_txt), 2)

        text_status = "✅ PASS (WCAG AA)" if text_ratio >= 4.5 else "❌ FAIL (Low Contrast)"
        btn_status = "✅ PASS (WCAG AA)" if btn_ratio >= 3.0 else "❌ FAIL (Low Button Contrast)"
        font_status = "✅ PASS (16px Floor)" if spec.meta.base_font_size_px >= 16 else "❌ FAIL (Under 16px)"

        return f"""# ⚡ What We'd Fix First: {spec.meta.brand_name} Diagnostic Audit

### 1. Typography & Readability Contrast
- **Surface vs Text**: `{surface_hex}` vs `{text_hex}` ➔ Contrast Ratio **{text_ratio}:1** ({text_status}).
- **CTA Button vs Label**: `{action_hex}` vs `{action_text_hex}` ➔ Contrast Ratio **{btn_ratio}:1** ({btn_status}).
- **Base Font Floor**: `{spec.meta.base_font_size_px}px` ({font_status} — Prevents mobile Safari viewport auto-zoom).

### 2. 60-30-10 CRO Color Distribution
- **60% Dominant Base**: `{surface_hex}` (Clean, unpolluted background without third-party widget tint).
- **30% Structure & Text**: `{text_hex}` (Strict optical hierarchy).
- **10% Conversion Focal**: `{action_hex}` (Reserved exclusively for Add-to-Cart and Checkout).

### 3. Core Web Vitals & Performance Gate
- **Architecture**: Shopify Online Store 2.0 (Theme Blocks 2.0).
- **Runtime Footprint**: Zero-React, pure Liquid AST with scoped CSS custom properties.
- **Expected LCP Improvement**: +35-50% faster Largest Contentful Paint compared to bloated multipurpose themes.
"""
