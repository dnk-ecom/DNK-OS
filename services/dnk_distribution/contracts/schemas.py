# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/contracts/schemas.py"
# purpose: "Strict Pydantic v2 schemas for dnk_distribution Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from services.dnk_distribution.src.brand_compliance import ComplianceReport, BrandProfile
from services.dnk_distribution.src.social_feedback import SocialMetrics, ContentFeedbackReport
from services.dnk_distribution.src.theme_miner import CommentItem, ThemeMiningResult


class ServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    query: str


class ServiceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    result: str


class BrandComplianceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    text: str = Field(..., min_length=1, description="Marketing copy or script to validate")
    is_promotional: bool = Field(default=False, description="Whether content is paid/promotional requiring FTC tags")
    profile: Optional[BrandProfile] = None


class BrandComplianceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    report: ComplianceReport


class SocialFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    metrics: SocialMetrics
    hook_type: Optional[str] = None


class SocialFeedbackResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    report: ContentFeedbackReport


class ThemeMiningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    comments: List[CommentItem]


class ThemeMiningResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    result: ThemeMiningResult
