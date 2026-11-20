# --- DNK-MRH-HEADER ---
# mrh_id: "packages/swarm_simulation/models.py"
# purpose: "Domain Contracts and Pydantic v2 Models for Synthetic Customer Swarm and Funnel Simulation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "Gerych Prime & Antigravity"
# --- END DNK-MRH-HEADER ---

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class BuyerMindset(str, Enum):
    """Core behavioral archetype of a synthetic customer."""
    IMPULSE = "impulse"
    ANALYTICAL = "analytical"
    PRICE_SENSITIVE = "price_sensitive"
    SKEPTIC = "skeptic"
    PREMIUM = "premium"


class ObjectionType(str, Enum):
    """Primary friction points preventing conversion in a sales funnel."""
    PRICE_TOO_HIGH = "price_too_high"
    LACK_OF_TRUST = "lack_of_trust"
    SHIPPING_DELAY = "shipping_delay"
    UNCLEAR_VALUE = "unclear_value"
    COMPETITOR_PREFERRED = "competitor_preferred"


class FunnelStepType(str, Enum):
    """Standard eCommerce and SaaS funnel stages."""
    LANDING = "landing"
    PRODUCT_PAGE = "product_page"
    CART_DRAWER = "cart_drawer"
    CHECKOUT = "checkout"
    POST_PURCHASE_UPSELL = "post_purchase_upsell"


class PsychographicProfile(BaseModel):
    """Psychological and behavioral traits shaping customer decision-making."""
    model_config = ConfigDict(extra="ignore")

    mbti: Optional[str] = Field(default="INTJ", description="Myers-Briggs personality indicator")
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk appetite (0=risk averse, 1=risk seeking)")
    decision_speed: float = Field(default=0.5, ge=0.0, le=1.0, description="Speed of action (0=deliberate, 1=impulsive)")
    social_proof_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0, description="Responsiveness to reviews and social consensus")
    brand_loyalty: float = Field(default=0.5, ge=0.0, le=1.0, description="Propensity to stick with known brands")
    core_values: List[str] = Field(default_factory=list, description="Guiding personal or business values")
    buying_motivations: List[str] = Field(default_factory=list, description="Primary drivers for purchasing")


class CustomerPersona(BaseModel):
    """High-fidelity synthetic buyer agent representation."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Unique persona identifier")
    name: str = Field(description="Synthetic persona full name")
    mindset: BuyerMindset = Field(description="Dominant decision-making archetype")
    age: Optional[int] = Field(default=30, ge=18, le=99, description="Customer age")
    occupation: Optional[str] = Field(default="Professional", description="Customer occupation or domain role")
    budget_usd: float = Field(ge=0.0, description="Disposable budget allocated for this purchase")
    skepticism_score: float = Field(ge=0.0, le=1.0, description="Inherent resistance/doubt (0=trusting, 1=highly skeptical)")
    urgency_score: float = Field(ge=0.0, le=1.0, description="Current need or time sensitivity (0=browsing, 1=critical need)")
    primary_objections: List[ObjectionType] = Field(default_factory=list, description="Inherent friction triggers for this persona")
    psychographics: PsychographicProfile = Field(default_factory=PsychographicProfile, description="Detailed psychological traits")
    bio: Optional[str] = Field(default=None, description="Short narrative persona background")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extension parameters")


class FunnelStep(BaseModel):
    """Definition of a single checkpoint in the customer acquisition journey."""
    model_config = ConfigDict(extra="ignore")

    step_id: str = Field(description="Unique step slug (e.g. hero_landing, checkout_page)")
    step_type: FunnelStepType = Field(description="Category of the step")
    name: str = Field(description="Human-readable title")
    description: Optional[str] = Field(default="", description="Detailed step context or copy")
    required_trust_threshold: float = Field(default=0.4, ge=0.0, le=1.0, description="Trust minimum needed to pass without dropping off")
    price_point_usd: float = Field(default=0.0, ge=0.0, description="Financial commitment at this step")
    friction_factors: List[ObjectionType] = Field(default_factory=list, description="Objections actively challenged at this step")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters or design tags")


class StepResult(BaseModel):
    """Result of an individual synthetic persona evaluating a single funnel step."""
    model_config = ConfigDict(extra="ignore")

    persona_id: str = Field(description="Evaluating persona identifier")
    step_id: str = Field(description="Funnel step identifier")
    proceeded: bool = Field(description="Whether persona passed this step towards conversion")
    triggered_objection: Optional[ObjectionType] = Field(default=None, description="Primary objection causing drop-off")
    hesitation_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Level of doubt experienced during evaluation")
    feedback_comment: Optional[str] = Field(default=None, description="Synthetic self-reported thought or hesitation reason")


class ProductSeed(BaseModel):
    """Seed data provided to instantiate customer cohorts and storefront steps."""
    model_config = ConfigDict(extra="ignore")

    title: str = Field(description="Product or service title")
    description: str = Field(description="Core value proposition and feature summary")
    price_usd: float = Field(ge=0.0, description="Target retail price in USD")
    category: str = Field(default="general", description="Industry or niche category")
    target_audience: Optional[str] = Field(default="general consumers", description="Demographic definition")
    key_benefits: List[str] = Field(default_factory=list, description="Bullet points of major value propositions")
    social_proof_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Strength of visible reviews, testimonials, or brand equity")


class CohortReport(BaseModel):
    """Consolidated intelligence and analytics report from a swarm simulation run."""
    model_config = ConfigDict(extra="ignore")

    cohort_id: str = Field(description="Simulation batch identifier")
    product_title: str = Field(description="Evaluated product name")
    total_personas: int = Field(ge=0, description="Total synthetic agents simulated")
    completed_count: int = Field(ge=0, description="Number of agents reaching full checkout conversion")
    completion_rate: float = Field(ge=0.0, le=1.0, description="Overall conversion rate (completed / total)")
    step_dropoffs: Dict[str, int] = Field(default_factory=dict, description="Drop-off count per step_id")
    step_conversion_rates: Dict[str, float] = Field(default_factory=dict, description="Conversion percentage entering each step")
    top_objections: Dict[str, int] = Field(default_factory=dict, description="Objection frequency mapping")
    average_order_value: float = Field(default=0.0, ge=0.0, description="Average revenue generated per converted customer")
    estimated_revenue_usd: float = Field(default=0.0, ge=0.0, description="Total projected revenue from converted cohort")
    actionable_recommendations: List[str] = Field(default_factory=list, description="Prescriptive advice to boost funnel conversion")
