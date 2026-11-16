# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/mirofish_swarm_prediction_and_synthetic_customer_sandbox.md"
# purpose: "Assimilation patterns, Clean-Room Reverse Engineering & Synthetic Customer Focus Group Sandbox from 666ghj/MiroFish."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# MiroFish Swarm Simulation & Synthetic Customer Focus Group Architecture

## 1. Upstream Archetype & Technical Profile
- **Repository**: `666ghj/MiroFish` (72.4k+ ⭐)
- **License**: `AGPL-3.0` (Strong Copyleft) ➔ **Track 2 Clean-Room Reverse Engineering Required**.
- **Core Technology Stack**: Python (Flask / CAMEL-OASIS multi-agent social network engine, Zep Cloud temporal memory, Pydantic, PyMuPDF) + Vue 3 (Vite, Pinia, G6 Graph visualization).

## 2. 5-Stage Swarm Simulation Lifecycle
1. **Graph Building (Source -> Semantic Entity Graph)**:
   - Ingestion of seed product descriptions, PRDs, landing page URLs, or market analyses.
   - Entity & relation extraction compiled into GraphRAG representation.
2. **Environment & Persona Synthesis (OASIS Profiles)**:
   - Generation of rich, diverse agent profiles: demographics, MBTI, price sensitivity, technical literacy, skepticism level, and domain interest distributions.
3. **Dual-Platform Social Sandbox Simulation**:
   - **Twitter/X Channel**: Micro-reactions, fast sentiment shifts, virality hooks, short critiques, shares/retweets.
   - **Reddit Channel**: In-depth threaded discussions, technical teardowns, deep skepticism, alternative comparisons, upvote/downvote consensus.
4. **Interactive Deep Probing (1:1 & Batch Agent Interviews)**:
   - Dynamic conversational probing of individual agents mid-run or post-simulation:
     - *"What exact objection prevented you from converting?"*
     - *"What would be the threshold price point for your team?"*
5. **Analytical Report Synthesis (InsightForge / ReACT Report Agent)**:
   - Aggregation of thread telemetry, sentiment heatmaps, consensus clustering, and high-confidence behavioral predictions.

## 3. Clean-Room Canonical Implementation (`packages/swarm_simulation/`)
To strictly respect AGPL-3.0 boundaries, zero code is copied verbatim. We implement a clean MIT package ground-up:

### 3.1. Verified Domain Models (`packages/swarm_simulation/models.py`)
```python
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class BuyerMindset(str, Enum):
    IMPULSE = "impulse"
    ANALYTICAL = "analytical"
    PRICE_SENSITIVE = "price_sensitive"
    SKEPTIC = "skeptic"
    PREMIUM = "premium"

class ObjectionType(str, Enum):
    PRICE_TOO_HIGH = "price_too_high"
    LACK_OF_TRUST = "lack_of_trust"
    SHIPPING_DELAY = "shipping_delay"
    UNCLEAR_VALUE = "unclear_value"
    COMPETITOR_PREFERRED = "competitor_preferred"

class PsychographicProfile(BaseModel):
    mbti: str = "INTJ"
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    decision_speed: float = Field(default=0.5, ge=0.0, le=1.0)
    social_proof_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    brand_loyalty: float = Field(default=0.5, ge=0.0, le=1.0)
    core_values: List[str] = Field(default_factory=list)
    primary_motivator: str = "efficiency"

class CustomerPersona(BaseModel):
    id: str
    name: str
    mindset: BuyerMindset
    age: int = Field(ge=18, le=99)
    occupation: str
    budget_usd: float = Field(ge=0.0)
    skepticism_score: float = Field(ge=0.0, le=1.0)
    urgency_score: float = Field(ge=0.0, le=1.0)
    primary_objections: List[ObjectionType] = Field(default_factory=list)
    psychographics: PsychographicProfile = Field(default_factory=PsychographicProfile)
    background_bio: str = ""

class FunnelStepType(str, Enum):
    LANDING = "landing"
    PRODUCT_PAGE = "product_page"
    CART_DRAWER = "cart_drawer"
    CHECKOUT = "checkout"
    POST_PURCHASE_UPSELL = "post_purchase_upsell"

class FunnelStep(BaseModel):
    step_id: str
    step_type: FunnelStepType
    title: str
    required_trust_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    price_point_usd: float = Field(default=0.0, ge=0.0)
    friction_factors: List[str] = Field(default_factory=list)

class StepResult(BaseModel):
    step_type: FunnelStepType
    proceeded: bool
    triggered_objection: Optional[ObjectionType] = None
    hesitation_score: float = Field(ge=0.0, le=1.0)
    persona_feedback: str = ""

class ProductSeed(BaseModel):
    product_name: str
    price_usd: float = Field(ge=0.0)
    category: str
    value_propositions: List[str] = Field(default_factory=list)
    trust_elements: List[str] = Field(default_factory=list)

class CohortReport(BaseModel):
    total_personas: int
    converted_personas: int
    overall_conversion_rate: float
    dropoff_by_step: dict[str, int]
    top_objections: list[tuple[str, int]]
    average_order_value_usd: float
    estimated_revenue_usd: float
```

### 3.2. Clean-Room Customer Generator (`packages/swarm_simulation/generator.py`)
- **Seeded Determinism**: Uses `random.Random(seed)` instance to guarantee reproducible persona cohort generation across test runs.
- **Dynamic Price-Weighted Distribution**: Automatically shifts cohort mindset distribution:
  - High price ($100+): Elevates `BuyerMindset.SKEPTIC` (35%) and `BuyerMindset.ANALYTICAL` (35%), suppressing `BuyerMindset.IMPULSE` (5%).
  - Budget/Low price (<$30): Elevates `BuyerMindset.IMPULSE` (40%) and `BuyerMindset.PRICE_SENSITIVE` (30%).
- **Archetype-Correlated Objections**:
  - `PRICE_SENSITIVE` -> `PRICE_TOO_HIGH`
  - `SKEPTIC` -> `LACK_OF_TRUST`, `UNCLEAR_VALUE`
  - `ANALYTICAL` -> `COMPETITOR_PREFERRED`, `UNCLEAR_VALUE`

## 4. Swarm Service Integrations in DNK OS
| DNK OS Service | Integration Mode | Tangible Business Value |
|---|---|---|
| `dnk_shopify` & `dnk_one_click_product_launch` | Virtual Focus Group before Ad Spend | Test headline copy, cart drawer upsells, and price thresholds ($29 vs $49) across 100 simulated buyers. |
| `dnk_video_ai_creator` & `dnk_youtube_auditor` | Hook & Retention Pre-Testing | Simulate initial 5-second viewer churn, comment virality, and engagement ratio across demographic segments. |
| `gerych_prime` | SaaS Feature & ICP Validation | Cold outreach and value proposition stress-testing on virtual CTO / Founder personas before building. |
| `packages/swarm_simulation/funnel_simulator.py` | Headless Funnel Execution Engine | Monte Carlo simulation of simulated cohort against discrete funnel steps with objections telemetry. |
