# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/service.py"
# purpose: "Unified In-RAM Facade for dnk_distribution Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from typing import List, Dict, Any, Optional
from pathlib import Path
from services.dnk_distribution.src.brand_compliance import (
    BrandComplianceEngine,
    ComplianceReport,
    BrandProfile,
    brand_compliance_engine,
)
from services.dnk_distribution.src.social_feedback import (
    SocialFeedbackRLSFEngine,
    SocialMetrics,
    ContentFeedbackReport,
    social_feedback_engine,
)
from services.dnk_distribution.src.theme_miner import (
    AudienceThemeMiner,
    CommentItem,
    ThemeMiningResult,
    audience_theme_miner,
)
from services.dnk_distribution.src.llms_txt import (
    StoreProfile,
    CatalogItem,
    PolicyItem,
    llms_txt_engine,
)
from services.dnk_distribution.src.merchant_feed import (
    generate_google_merchant_xml,
    export_merchant_feed,
)
from services.dnk_distribution.contracts.schemas import (
    LlmsTxtRequest,
    LlmsTxtResponse,
    MerchantFeedRequest,
    MerchantFeedResponse,
)


def check_compliance(
    text: str,
    profile: Optional[BrandProfile] = None,
    is_promotional: bool = False
) -> ComplianceReport:
    """Validates marketing copy against brand guidelines, banned words, legal claims, and FTC rules."""
    return brand_compliance_engine.validate(
        text=text,
        profile=profile,
        is_promotional=is_promotional
    )


def evaluate_social_metrics(
    metrics: SocialMetrics,
    hook_type: Optional[str] = None
) -> ContentFeedbackReport:
    """Computes RLSF multi-objective social reward signals and assigns performance tiers."""
    return social_feedback_engine.evaluate_publication(
        metrics=metrics,
        hook_type=hook_type
    )


def mine_audience_themes(
    comments: List[CommentItem]
) -> ThemeMiningResult:
    """Mines comments and reviews to extract core customer objections, buying intents, and copy angles."""
    return audience_theme_miner.mine_comments(comments=comments)


def generate_llms_bundle(request: LlmsTxtRequest) -> LlmsTxtResponse:
    """Generates llms.txt and llms-full.txt files according to llmstxt.org e-commerce standards."""
    txt = llms_txt_engine.generate_llms_txt(
        profile=request.profile,
        products=request.products,
        policies=request.policies,
    )
    full_txt = llms_txt_engine.generate_llms_full_txt(
        profile=request.profile,
        products=request.products,
        policies=request.policies,
    )

    exported = None
    if request.output_dir:
        exported = llms_txt_engine.export_bundle(
            output_dir=Path(request.output_dir),
            profile=request.profile,
            products=request.products,
            policies=request.policies,
        )

    return LlmsTxtResponse(
        success=True,
        llms_txt=txt,
        llms_full_txt=full_txt,
        exported_files=exported,
    )


def generate_merchant_feed(request: MerchantFeedRequest) -> MerchantFeedResponse:
    """Generates Google Merchant Center RSS 2.0 XML product feed."""
    xml_content = generate_google_merchant_xml(
        profile=request.profile,
        products=request.products,
        image_base_url=request.image_base_url,
    )

    out_path = None
    if request.output_path:
        out_path = export_merchant_feed(
            output_path=Path(request.output_path),
            profile=request.profile,
            products=request.products,
            image_base_url=request.image_base_url,
        )

    return MerchantFeedResponse(
        success=True,
        xml_content=xml_content,
        output_path=out_path,
        total_items=len(request.products),
    )


def process_data(query: str) -> str:
    """Generic fallback string processor for basic connectivity check."""
    return f"Processed: {query}"
