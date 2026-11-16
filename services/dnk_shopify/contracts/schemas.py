# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/contracts/schemas.py"
# purpose: "Strict Pydantic v2 schemas for dnk_shopify Sovereign Brick."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ThemeBlockMeta(BaseModel):
    """Metadata representing a Theme Block 2.0 component."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    block_name: str = Field(..., description="Filename of the block (e.g. _card.liquid, accordion.liquid)")
    is_private: bool = Field(..., description="True if block starts with '_' (internal private block)")
    file_path: str = Field(..., description="Relative path within the theme")
    has_schema: bool = Field(False, description="Whether the block contains a {% schema %} JSON definition")
    schema_name: Optional[str] = Field(None, description="Human-readable schema name")
    target_presets: List[str] = Field(default_factory=list, description="Target presets declared in schema")


class ThemeCheckViolation(BaseModel):
    """Static analysis warning or error from theme check."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    file_path: str = Field(..., description="Path to offending file")
    line: int = Field(0, description="Line number if known")
    severity: Literal["error", "warning", "info"] = Field("warning", description="Severity level")
    rule_id: str = Field(..., description="Static analysis rule ID")
    message: str = Field(..., description="Description of the issue")


class ThemeCheckResult(BaseModel):
    """Outcome of static theme validation."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    theme_path: str = Field(..., description="Root directory of theme audited")
    total_files: int = Field(0, description="Count of evaluated liquid and json files")
    errors_count: int = Field(0, description="Count of fatal theme check errors")
    warnings_count: int = Field(0, description="Count of non-fatal warnings")
    violations: List[ThemeCheckViolation] = Field(default_factory=list, description="List of detected violations")
    is_compliant: bool = Field(True, description="True if errors_count == 0 and required structure present")


class CartMutation(BaseModel):
    """Atomic change to line items in the Shopify cart."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: Literal["add", "update", "remove", "clear"] = Field("add", description="Cart mutation verb")
    variant_id: str = Field(..., description="Target Shopify variant ID")
    quantity: int = Field(1, description="Quantity delta or target quantity")
    properties: Dict[str, str] = Field(default_factory=dict, description="Custom line-item attributes")


class CartMutationQueueSpec(BaseModel):
    """Specification for processing queued cart mutations and free shipping bar."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    mutations: List[CartMutation] = Field(default_factory=list, description="Ordered mutation sequence")
    free_shipping_threshold: float = Field(1000.0, description="Monetary threshold for free shipping")
    current_subtotal: float = Field(0.0, description="Current cart subtotal before queued mutations")
    currency: str = Field("USD", description="ISO 4217 currency code")


class CartCalculationResult(BaseModel):
    """Outcome of applying cart mutations."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    new_subtotal: float = Field(0.0, description="Updated cart subtotal after mutations")
    remaining_for_free_shipping: float = Field(0.0, description="Remaining amount needed for free shipping")
    progress_percentage: float = Field(0.0, description="Progress towards free shipping (0.0 to 100.0)")
    free_shipping_qualified: bool = Field(False, description="True if new_subtotal >= free_shipping_threshold")
    item_count: int = Field(0, description="Total physical units in cart")


class CROBlockSpec(BaseModel):
    """Conversion Rate Optimization block requirement."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    block_id: str = Field(..., description="Unique CRO component identifier")
    title: str = Field(..., description="Human name of CRO mechanism")
    category: str = Field(..., description="CRO pillar: urgency, trust, social_proof, average_order_value")
    canonical_filename: str = Field(..., description="Expected block or section liquid filename")


class CROAuditResult(BaseModel):
    """Audit of theme's conversion-readiness."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    theme_path: str = Field(..., description="Audited theme path")
    score: int = Field(0, description="CRO Score from 0 to 100")
    detected_blocks: List[str] = Field(default_factory=list, description="Found CRO components")
    missing_blocks: List[str] = Field(default_factory=list, description="Missing recommended CRO components")
    recommendations: List[str] = Field(default_factory=list, description="Actionable optimization steps")


class LiquidValidationResult(BaseModel):
    """Liquid syntax AST validation report."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    valid: bool = Field(True, description="True if liquid structure has balanced tags")
    errors: List[str] = Field(default_factory=list, description="Validation failure details")
    tags_count: int = Field(0, description="Number of parsed {% ... %} control tags")
    variables_count: int = Field(0, description="Number of parsed {{ ... }} output tags")


class ProposalConfigSpec(BaseModel):
    """Input configuration for generating an intelligent personalized Shopify proposal."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    client_name: str = Field(..., min_length=1, description="Decision-maker name")
    brand_name: str = Field(..., min_length=1, description="Client brand or store name")
    niche: Literal[
        "fashion_apparel",
        "beauty_cosmetics",
        "home_decor_lighting",
        "electronics_accessories",
        "kids_educational",
        "custom_dtc",
    ] = Field("custom_dtc", description="Store vertical for tailored CRO molecule mapping")
    package_tier: Literal["launch_1200", "scale_1500"] = Field(
        "scale_1500", description="Selected base package ($1200 Launch Core or $1500 Scale CRO)"
    )
    extra_products_batches: int = Field(
        0, ge=0, le=50, description="Number of extra 10-product batches ($50 per 10 items)"
    )
    include_gmc_setup: bool = Field(
        False, description="Include Google Merchant Center setup & compliance ($300)"
    )
    include_seo_semantics: bool = Field(
        False, description="Include semantic SEO structure & collection mapping ($200)"
    )
    monthly_orders_estimate: int = Field(150, ge=1, description="Estimated monthly orders")
    average_order_value_usd: float = Field(65.0, ge=1.0, description="Estimated AOV in USD")


class ProposalQuoteResult(BaseModel):
    """Deterministic quote, ROI projection, and cryptographic scope seal for a client deal."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., description="Deterministic deal room identifier")
    client_name: str = Field(..., description="Client name")
    brand_name: str = Field(..., description="Brand name")
    niche: str = Field(..., description="Target vertical")
    package_tier: Literal["launch_1200", "scale_1500"] = Field(..., description="Selected tier")
    base_price_usd: int = Field(..., description="Base package investment in USD")
    addons_total_usd: int = Field(..., description="Total add-ons cost in USD")
    total_investment_usd: int = Field(..., description="Total contract value in USD")
    prepayment_30_usd: float = Field(..., description="30% upfront deposit required to ignite pipeline")
    completion_70_usd: float = Field(..., description="70% final payment upon QA gate approval")
    delivery_business_days: int = Field(14, description="Contract SLA in business days")
    included_products_count: int = Field(..., description="Total SKU upload quota included")
    included_languages_count: int = Field(..., description="Number of storefront languages")
    included_revision_rounds: int = Field(..., description="Hard cap on free revision cycles")
    annual_app_savings_usd: int = Field(
        ..., description="Annual savings from native DNK Sovereign Apex blocks vs paid Shopify apps"
    )
    estimated_payback_months: float = Field(
        ..., description="Months to recoup total store investment from app savings + CRO lift"
    )
    recommended_molecules: List[str] = Field(
        default_factory=list, description="Activated DNK Sovereign Apex Theme Blocks 2.0"
    )
    niche_pain_to_molecule_matrix: List[Dict[str, str]] = Field(
        default_factory=list, description="Traceable mapping: buyer objection -> DNK molecule -> KPI lift"
    )
    scope_sha256: str = Field(..., min_length=64, max_length=64, description="64-char SHA-256 contract scope hash")


class ClientArtifactRecord(BaseModel):
    """Verifiable artifact crystallized at a pipeline stage for client inspection."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    artifact_id: str = Field(..., description="Unique artifact identifier")
    stage_number: int = Field(..., ge=1, le=6, description="Pipeline stage 1..6")
    canvas_node_id: str = Field(..., description="Source node in shopify_vibe_pipeline.canvas")
    title: str = Field(..., description="Client-facing deliverable name")
    relative_path: str = Field(..., description="Relative artifact path inside workspace")
    sha256_receipt: str = Field(..., min_length=64, max_length=64, description="64-char SHA-256 artifact hash")
    status: Literal["locked", "in_progress", "ready_for_review", "approved"] = Field(
        "locked", description="Lifecycle state of the deliverable"
    )


class ClientStageSpec(BaseModel):
    """Single stage in the 6-Stage Client Execution Dashboard (DEC-010)."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    stage_number: int = Field(..., ge=1, le=6)
    stage_id: str
    title_uk: str
    canvas_node_id: str
    assigned_agent: str
    status: Literal["completed", "in_progress", "waiting_client_assets", "pending"]
    sla_days: str
    deliverables: List[str] = Field(default_factory=list)
    artifacts: List[ClientArtifactRecord] = Field(default_factory=list)


class ClientTicketRequest(BaseModel):
    """Client question or revision submitted via the Client Portal Task Manager."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1)
    request_text: str = Field(..., min_length=3)
    preferred_node_id: Optional[str] = Field(None, description="Optional explicit canvas node target")
    used_revisions_count: int = Field(0, ge=0)
    max_free_revisions: int = Field(3, ge=1)


class ClientTicketTriageResult(BaseModel):
    """Deterministic Scope Guard classification and DNK OS Spatial Canvas routing outcome."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_id: str
    deal_id: str
    classification: Literal["question", "in_scope_revision", "out_of_scope_upsell"]
    target_canvas_node_id: str
    assigned_agent: str
    session_id: str = Field(..., description="Isolated SQLite WAL thread: node:{canvas_id}:{node_id}")
    gate_state: Literal["awaiting_founder_triage", "auto_answered", "upsell_quote_required"]
    remaining_free_revisions: int
    upsell_estimate_usd: int = Field(0, ge=0)
    action_summary_uk: str
    audit_hash: str = Field(..., min_length=64, max_length=64, description="64-char JCS SHA-256 audit hash")

