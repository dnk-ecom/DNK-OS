# --- DNK-MRH-HEADER ---
# mrh_id: "core/design_system/schemas.py"
# purpose: "Pydantic data contracts for W3C DTCG Design Tokens, Brand Specs, and Multi-Target Emitters."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TargetPlatform(str, Enum):
    SHOPIFY = "shopify"
    TAILWIND_V4 = "tailwind_v4"
    MEDIA_MOTION = "media_motion"
    BRAND_MARKDOWN = "brand_markdown"
    ALL = "all"


class DTCGToken(BaseModel):
    value: Union[str, int, float, List[Any], Dict[str, Any]] = Field(..., alias="$value")
    type: str = Field(..., alias="$type")
    description: Optional[str] = Field(default=None, alias="$description")

    model_config = {"populate_by_name": True}


class BrandMeta(BaseModel):
    brand_name: str = Field(default="DNK Brand")
    archetype: str = Field(default="ecommerce_conversion")
    cro_allocation_rule: str = Field(default="60-30-10")
    typography_ratio_name: str = Field(default="Major Third")
    typography_ratio: float = Field(default=1.25)
    base_font_size_px: int = Field(default=16)
    spacing_grid_base_px: int = Field(default=8)
    font_family_display: Optional[str] = Field(default=None)
    font_family_body: Optional[str] = Field(default=None)
    brand_tagline: Optional[str] = Field(default=None)
    extracted_quotes: List[str] = Field(default_factory=list)


class TypographyStep(BaseModel):
    rem: float
    px: float
    line_height: float = 1.3
    weight: int = 400
    letter_spacing: str = "0em"


class MotionSpec(BaseModel):
    dur_fast_ms: int = 150
    dur_base_ms: int = 250
    dur_slow_ms: int = 400
    ease_default: str = "cubic-bezier(0.16, 1, 0.3, 1)"
    ease_spring: str = "cubic-bezier(0.34, 1.56, 0.64, 1)"
    ease_in_out: str = "cubic-bezier(0.65, 0, 0.35, 1)"


class ElevationSpec(BaseModel):
    shadow_xs: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    shadow_sm: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
    shadow_md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
    shadow_lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"


class BrandTokensSpec(BaseModel):
    schema_version: str = Field(default="dtcg-2025.10")
    meta: BrandMeta = Field(default_factory=BrandMeta)
    primitives: Dict[str, Any] = Field(default_factory=dict)
    semantic: Dict[str, Any] = Field(default_factory=dict)
    typography: Dict[str, Any] = Field(default_factory=dict)
    spacing: Dict[str, Any] = Field(default_factory=dict)
    motion: MotionSpec = Field(default_factory=MotionSpec)
    elevation: ElevationSpec = Field(default_factory=ElevationSpec)


class LintViolation(BaseModel):
    code: str
    severity: str = "error"  # "error", "warning"
    message: str
    token_name: Optional[str] = None
    suggestion: Optional[str] = None


class LintReport(BaseModel):
    valid: bool
    violations: List[LintViolation] = Field(default_factory=list)
    wcag_contrast_checked: int = 0
    contrast_pass_rate: float = 100.0
    cro_allocation_check: Dict[str, Any] = Field(default_factory=dict)


class MultiTargetCompilationResult(BaseModel):
    brand_name: str
    shopify_css: str
    shopify_settings_schema: Dict[str, Any]
    tailwind_v4_css: str
    media_motion_tokens: Dict[str, Any]
    brand_markdown: str
    astryx_theme_css: Optional[str] = None
    figma_variables_json: Optional[Dict[str, Any]] = None
    social_creative_matrix: Optional[Dict[str, Any]] = None
    shopify_theme_block_liquid: Optional[str] = None
    google_design_md: Optional[str] = None
    brand_voice_md: Optional[str] = None
    agent_skill_md: Optional[str] = None
    fix_first_report: Optional[str] = None
