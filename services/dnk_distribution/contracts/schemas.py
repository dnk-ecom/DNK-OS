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
from services.dnk_distribution.src.llms_txt import StoreProfile, CatalogItem, PolicyItem
from services.dnk_distribution.src.social_scanner import SocialScanResult


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


class LlmsTxtRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    profile: StoreProfile = Field(default_factory=StoreProfile)
    products: List[CatalogItem] = Field(default_factory=list)
    policies: Optional[List[PolicyItem]] = None
    output_dir: Optional[str] = None


class LlmsTxtResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    llms_txt: str
    llms_full_txt: str
    exported_files: Optional[Dict[str, str]] = None


class MerchantFeedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    profile: StoreProfile = Field(default_factory=StoreProfile)
    products: List[CatalogItem] = Field(default_factory=list)
    image_base_url: Optional[str] = None
    output_path: Optional[str] = None


class MerchantFeedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    xml_content: str
    output_path: Optional[str] = None
    total_items: int = 0


class SocialScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    url: str = Field(..., min_length=5, description="Social media post URL to scan")


class SocialScanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    data: SocialScanResult
