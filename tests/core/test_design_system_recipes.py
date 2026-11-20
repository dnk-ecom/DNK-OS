# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_design_system_recipes.py"
# purpose: "Deterministic Verification Suite for Design System Recipes Catalog and DTC Spec."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym, Antigravity & Denchik"
# --- END DNK-MRH-HEADER ---

from pathlib import Path
import yaml
from core.design_system import (
    BrandTokensSpec,
    DesignTokenCompiler,
    DesignTokenLinter,
)


def test_genome_recipes_catalog_structure():
    catalog_path = Path("docs/projects/dnk_ecom/audits/GENOME_DESIGN_SYSTEM_RECIPES.yaml")
    assert catalog_path.exists(), "GENOME_DESIGN_SYSTEM_RECIPES.yaml must exist"

    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "2.5.0"
    assert "shopify_molecules" in data
    assert "social_motion_molecules" in data

    # Shopify checks
    shopify = data["shopify_molecules"]
    assert "sticky_atc" in shopify
    assert "tiered_cart_rewards" in shopify
    assert "quantity_breaks" in shopify
    assert "before_after_slider" in shopify
    assert "comparison_table" in shopify

    # Social Motion checks
    social = data["social_motion_molecules"]
    assert "safe_zones_9_16" in social
    assert social["safe_zones_9_16"]["viewport"]["aspect_ratio"] == "9:16"
    assert social["safe_zones_9_16"]["top_danger_zone_px"] == 120
    assert social["safe_zones_9_16"]["bottom_danger_zone_px"] == 340
    assert "motion_spring_presets" in social
    assert "spring_snappy" in social["motion_spring_presets"]
    assert "kinetic_subtitles_preset" in social


def test_dtc_social_ecommerce_spec_compilation():
    spec_path = Path("core/design_system/templates/dnk_dtc_social_ecommerce_spec.yaml")
    assert spec_path.exists(), "dnk_dtc_social_ecommerce_spec.yaml must exist"

    raw_data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    spec = BrandTokensSpec(**raw_data)

    assert spec.meta.brand_name == "DNK DTC Sovereign Ecom"
    assert spec.meta.cro_allocation_rule == "60-30-10"
    assert spec.meta.base_font_size_px == 16

    # 1. Linter verification
    report = DesignTokenLinter.lint_spec(spec)
    assert report.valid is True
    assert report.contrast_pass_rate == 100.0
    assert report.wcag_contrast_checked >= 2
    assert report.cro_allocation_check["cta_distinct_from_surface"] is True

    # 2. Multi-Target Compiler verification
    res = DesignTokenCompiler.compile_all(spec)
    assert res.brand_name == "DNK DTC Sovereign Ecom"

    # Shopify CSS
    assert "--color-action-primary: #0F766E;" in res.shopify_css
    assert "--color-action-primary-rgb: 15 118 110;" in res.shopify_css
    assert "--font-size-base: 16px;" in res.shopify_css

    # Astryx CSS Layer
    assert res.astryx_theme_css is not None
    assert "@layer astryx-theme {" in res.astryx_theme_css
    assert "--astryx-surface-canvas:" in res.astryx_theme_css

    # Media Motion
    assert res.media_motion_tokens["motion"]["fps_target"] == 60
    assert "cubic-bezier" in res.media_motion_tokens["motion"]["spring"]

    # Markdown Brandbook
    assert "# 🎨 Brand Design System: DNK DTC Sovereign Ecom" in res.brand_markdown

    # Figma Variables
    assert res.figma_variables_json is not None
    assert res.figma_variables_json["metadata"]["brand"] == "DNK DTC Sovereign Ecom"

    # Social Creative Matrix
    assert res.social_creative_matrix is not None
    assert "reels_tiktok_9_16" in res.social_creative_matrix["viewport_formats"]
    assert res.social_creative_matrix["viewport_formats"]["reels_tiktok_9_16"]["optimal_focal_y"] == 720
