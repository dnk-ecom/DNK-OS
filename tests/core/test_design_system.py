# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_design_system.py"
# purpose: "Unit tests for DNK OS Sovereign Multi-Channel Design System Engine, Compiler, Linter & Extractor."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from core.design_system import (
    BrandTokensSpec,
    BrandMeta,
    DesignTokenCompiler,
    DesignTokenLinter,
    DesignTokenExtractor,
)


@pytest.fixture
def valid_brand_spec() -> BrandTokensSpec:
    return BrandTokensSpec(
        meta=BrandMeta(
            brand_name="Aura Wellness",
            archetype="wellness_luxury",
            cro_allocation_rule="60-30-10",
            typography_ratio=1.25,
            base_font_size_px=16,
            spacing_grid_base_px=8,
        ),
        semantic={
            "color": {
                "surface-primary": {"$value": "#FFFFFF", "$type": "color"},
                "text-primary": {"$value": "#0F172A", "$type": "color"},
                "action-primary": {"$value": "#0D9488", "$type": "color"},
                "action-primary-text": {"$value": "#FFFFFF", "$type": "color"},
                "action-secondary": {"$value": "#14B8A6", "$type": "color"},
            }
        },
        spacing={
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
        },
    )


def test_compiler_emits_all_targets(valid_brand_spec: BrandTokensSpec):
    res = DesignTokenCompiler.compile_all(valid_brand_spec)
    assert res.brand_name == "Aura Wellness"

    # 1. Shopify CSS checks
    assert ":root {" in res.shopify_css
    assert "--color-surface-primary: #FFFFFF;" in res.shopify_css
    assert "--color-surface-primary-rgb: 255 255 255;" in res.shopify_css
    assert "--font-size-base: 16px;" in res.shopify_css
    assert "--motion-spring:" in res.shopify_css

    # 2. Shopify Schema checks
    assert res.shopify_settings_schema["name"] == "DNK DS: Aura Wellness"
    assert len(res.shopify_settings_schema["settings"]) > 1

    # 3. Tailwind v4 checks
    assert "@theme {" in res.tailwind_v4_css
    assert "--color-surface-primary: #FFFFFF;" in res.tailwind_v4_css
    assert "--ease-spring:" in res.tailwind_v4_css

    # 4. Media Motion checks
    assert res.media_motion_tokens["brand_name"] == "Aura Wellness"
    assert res.media_motion_tokens["motion"]["fps_target"] == 60
    assert res.media_motion_tokens["colors"]["focal_cta"] == "#0D9488"
    assert "9:16" in res.media_motion_tokens["aspect_ratios"]["meta_tiktok_reels"]

    # 5. Brand Markdown checks
    assert "# 🎨 Brand Design System: Aura Wellness" in res.brand_markdown
    assert "60-30-10" in res.brand_markdown

    # 6. Astryx Layer checks
    assert res.astryx_theme_css is not None
    assert "@layer astryx-theme {" in res.astryx_theme_css
    assert "--astryx-surface-canvas:" in res.astryx_theme_css
    assert "--astryx-agent-shopify:" in res.astryx_theme_css

    # 7. Figma Variables checks
    assert res.figma_variables_json is not None
    assert res.figma_variables_json["version"] == "1.0.0"
    assert len(res.figma_variables_json["collections"][0]["variables"]) > 0

    # 8. Social Creative Matrix checks
    assert res.social_creative_matrix is not None
    assert "reels_tiktok_9_16" in res.social_creative_matrix["viewport_formats"]
    assert res.social_creative_matrix["viewport_formats"]["reels_tiktok_9_16"]["safe_zones"]["top_margin_px"] == 120
    assert "spring_snappy" in res.social_creative_matrix["motion_physics"]

    # 9. Shopify Theme Block 2.0 checks
    assert res.shopify_theme_block_liquid is not None
    assert "{% schema %}" in res.shopify_theme_block_liquid
    assert "dnk-theme-block" in res.shopify_theme_block_liquid
    assert "Aura Wellness Block" in res.shopify_theme_block_liquid

    # 10. Google Labs DESIGN.md checks
    assert res.google_design_md is not None
    assert 'title: "DESIGN.md: Aura Wellness"' in res.google_design_md
    assert "surface_primary:" in res.google_design_md

    # 11. BRAND.md checks
    assert res.brand_voice_md is not None
    assert 'title: "BRAND.md: Aura Wellness"' in res.brand_voice_md
    assert "Zero-Hallucination Verified Quotes" in res.brand_voice_md

    # 12. SKILL.md checks
    assert res.agent_skill_md is not None
    assert 'name: "aura-wellness-brand-guard"' in res.agent_skill_md
    assert "Strict Token Colors Only" in res.agent_skill_md

    # 13. What We'd Fix First checks
    assert res.fix_first_report is not None
    assert "What We'd Fix First: Aura Wellness Diagnostic Audit" in res.fix_first_report
    assert "Contrast Ratio" in res.fix_first_report


def test_linter_passes_on_valid_spec(valid_brand_spec: BrandTokensSpec):
    report = DesignTokenLinter.lint_spec(valid_brand_spec)
    assert report.valid is True
    assert report.wcag_contrast_checked >= 2
    assert report.contrast_pass_rate == 100.0
    assert report.cro_allocation_check["cta_distinct_from_surface"] is True


def test_linter_catches_wcag_failure():
    # Low contrast text on light background
    bad_spec = BrandTokensSpec(
        meta=BrandMeta(base_font_size_px=16),
        semantic={
            "color": {
                "surface-primary": {"$value": "#FFFFFF", "$type": "color"},
                "text-primary": {"$value": "#E2E8F0", "$type": "color"},  # very light gray!
                "action-primary": {"$value": "#0D9488", "$type": "color"},
                "action-primary-text": {"$value": "#FFFFFF", "$type": "color"},
            }
        },
    )
    report = DesignTokenLinter.lint_spec(bad_spec)
    assert report.valid is False
    assert any(v.code == "WCAG_CONTRAST_FAIL_BODY" for v in report.violations)


def test_linter_catches_font_floor_violation():
    bad_spec = BrandTokensSpec(
        meta=BrandMeta(base_font_size_px=14),  # breaks 16px floor
        semantic={
            "color": {
                "surface-primary": {"$value": "#FFFFFF", "$type": "color"},
                "text-primary": {"$value": "#0F172A", "$type": "color"},
            }
        },
    )
    report = DesignTokenLinter.lint_spec(bad_spec)
    assert report.valid is False
    assert any(v.code == "TYPO_BODY_FLOOR_TOO_SMALL" for v in report.violations)


def test_extractor_from_shopify_settings():
    settings = {
        "current": {
            "color_background": "#FDFBF7",
            "color_text": "#1A1A1A",
            "color_primary": "#E11D48",
        }
    }
    spec = DesignTokenExtractor.from_shopify_settings(settings, brand_name="Client Velvet")
    assert spec.meta.brand_name == "Client Velvet"
    assert spec.semantic["color"]["surface-primary"]["$value"] == "#FDFBF7"
    assert spec.semantic["color"]["text-primary"]["$value"] == "#1A1A1A"
    assert spec.semantic["color"]["action-primary"]["$value"] == "#E11D48"

    # Lint the extracted spec
    report = DesignTokenLinter.lint_spec(spec)
    assert report.valid is True


def test_kernel_tools_design_system_integration(tmp_path):
    import json
    from core.kernel import FastMCPKernel, create_fastmcp_server

    db_path = str(tmp_path / "action_bus.db")
    artifacts_dir = str(tmp_path / "artifacts")
    k = FastMCPKernel(db_path=db_path, artifacts_dir=artifacts_dir, workspace_id="test_ds")
    server = create_fastmcp_server(k, name="dnk-ds-test")

    tool_names = [t.name for t in server._tool_manager.list_tools()]
    assert "compile_brand_design_tokens" in tool_names
    assert "lint_brand_design_tokens" in tool_names
    assert "extract_brand_design_tokens" in tool_names

    sample_yaml = """
schema_version: "dtcg-2025.10"
meta:
  brand_name: "Test FastMCP Brand"
  base_font_size_px: 16
semantic:
  color:
    surface-primary:
      $value: "#FFFFFF"
      $type: "color"
    text-primary:
      $value: "#111827"
      $type: "color"
    action-primary:
      $value: "#0F766E"
      $type: "color"
    action-primary-text:
      $value: "#FFFFFF"
      $type: "color"
"""
    # 1. Lint via FastMCP tool function
    lint_tool = server._tool_manager.get_tool("lint_brand_design_tokens")
    lint_raw = lint_tool.fn(spec_json_or_yaml=sample_yaml)
    lint_res = json.loads(lint_raw)
    assert lint_res["success"] is True
    assert lint_res["report"]["valid"] is True

    # 2. Compile via FastMCP tool function
    compile_tool = server._tool_manager.get_tool("compile_brand_design_tokens")
    compile_raw = compile_tool.fn(spec_json_or_yaml=sample_yaml)
    compile_res = json.loads(compile_raw)
    assert compile_res["success"] is True
    assert compile_res["result"]["brand_name"] == "Test FastMCP Brand"
    assert ":root {" in compile_res["result"]["shopify_css"]
    assert "@theme {" in compile_res["result"]["tailwind_v4_css"]


def test_extractor_from_figma_variables_roundtrip(valid_brand_spec: BrandTokensSpec):
    # 1. Compile Figma variables
    figma_vars = DesignTokenCompiler.emit_figma_variables(valid_brand_spec)
    assert figma_vars["collections"][0]["name"] == "Brand Design Tokens"

    # 2. Extract tokens back from Figma variables JSON
    extracted_spec = DesignTokenExtractor.from_figma_variables(figma_vars, brand_name="Figma Roundtrip")
    assert extracted_spec.meta.brand_name == "Figma Roundtrip"
    assert "surface-primary" in extracted_spec.semantic["color"]
    assert extracted_spec.semantic["color"]["surface-primary"]["$value"] == "#FFFFFF"
    assert extracted_spec.spacing["sm"] == 8


