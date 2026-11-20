# --- DNK-MRH-HEADER ---
# mrh_id: "packages/swarm_simulation/funnel_simulator.py"
# purpose: "Clean-Room MIT Funnel Simulation Engine and Conversion Analytics."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "Gerych Prime & Antigravity"
# --- END DNK-MRH-HEADER ---

"""Clean-Room MIT Funnel Simulation Engine and Conversion Analytics.

This engine executes synthetic customer persona swarms through multi-step
sales and marketing funnels (e.g. Shopify storefronts, video hooks, checkout).
Calculates drop-off rates, identifies friction points, and synthesizes
actionable conversion optimization recommendations.
"""

import random
import uuid
from typing import Dict, List, Optional

from packages.swarm_simulation.models import (
    BuyerMindset,
    CohortReport,
    CustomerPersona,
    FunnelStep,
    FunnelStepType,
    ObjectionType,
    ProductSeed,
    StepResult,
)


class FunnelSimulationEngine:
    """Simulates synthetic customer journeys across multi-step conversion funnels."""

    @staticmethod
    def create_default_shopify_funnel(product: ProductSeed) -> List[FunnelStep]:
        """Generate a canonical 4-step e-commerce Shopify funnel."""
        return [
            FunnelStep(
                step_id="step_landing",
                step_type=FunnelStepType.LANDING,
                name="Landing Page & Hero",
                description="Initial hook, store impression, and value proposition.",
                required_trust_threshold=0.20,
                price_point_usd=0.0,
                friction_factors=[
                    ObjectionType.UNCLEAR_VALUE,
                    ObjectionType.LACK_OF_TRUST,
                ],
            ),
            FunnelStep(
                step_id="step_pdp",
                step_type=FunnelStepType.PRODUCT_PAGE,
                name="Product Detail Page (PDP)",
                description="Detailed specs, gallery, customer reviews, and pricing.",
                required_trust_threshold=0.40,
                price_point_usd=product.price_usd,
                friction_factors=[
                    ObjectionType.PRICE_TOO_HIGH,
                    ObjectionType.UNCLEAR_VALUE,
                    ObjectionType.COMPETITOR_PREFERRED,
                ],
            ),
            FunnelStep(
                step_id="step_cart",
                step_type=FunnelStepType.CART_DRAWER,
                name="Cart Drawer & Review",
                description="Order review, shipping estimates, and cart bumps.",
                required_trust_threshold=0.55,
                price_point_usd=product.price_usd,
                friction_factors=[
                    ObjectionType.SHIPPING_DELAY,
                    ObjectionType.PRICE_TOO_HIGH,
                ],
            ),
            FunnelStep(
                step_id="step_checkout",
                step_type=FunnelStepType.CHECKOUT,
                name="Checkout & Payment Gateway",
                description="Payment method entry, taxes, and final purchase authorization.",
                required_trust_threshold=0.70,
                price_point_usd=product.price_usd,
                friction_factors=[
                    ObjectionType.PRICE_TOO_HIGH,
                    ObjectionType.LACK_OF_TRUST,
                ],
            ),
        ]

    def run_simulation(
        self,
        product: ProductSeed,
        steps: List[FunnelStep],
        personas: List[CustomerPersona],
        seed: Optional[int] = 42,
    ) -> CohortReport:
        """Run the full cohort through the funnel steps and compile a comprehensive report."""
        if not steps:
            raise ValueError("Funnel must contain at least one step.")
        if not personas:
            raise ValueError("Personas cohort cannot be empty.")

        rng = random.Random(seed)
        total_personas = len(personas)
        step_dropoffs: Dict[str, int] = {step.step_id: 0 for step in steps}
        step_entered_counts: Dict[str, int] = {step.step_id: 0 for step in steps}
        step_passed_counts: Dict[str, int] = {step.step_id: 0 for step in steps}
        top_objections: Dict[str, int] = {}

        completed_count = 0
        total_revenue_usd = 0.0

        for persona in personas:
            # Accumulated trust grows as persona progresses successfully
            accumulated_trust = 0.3 * (1.0 - persona.skepticism_score) + 0.3 * product.social_proof_level
            persona_completed_all = True

            for step_idx, step in enumerate(steps):
                step_entered_counts[step.step_id] += 1
                result = self._evaluate_step(
                    step=step,
                    persona=persona,
                    accumulated_trust=accumulated_trust,
                    product=product,
                    rng=rng,
                )

                if result.proceeded:
                    step_passed_counts[step.step_id] += 1
                    # Successful step reinforces trust for the next step
                    trust_gain = 0.15 * (1.0 - result.hesitation_score)
                    accumulated_trust = min(1.0, accumulated_trust + trust_gain)
                else:
                    step_dropoffs[step.step_id] += 1
                    if result.triggered_objection:
                        obj_key = result.triggered_objection.value
                        top_objections[obj_key] = top_objections.get(obj_key, 0) + 1
                    persona_completed_all = False
                    break

            if persona_completed_all:
                completed_count += 1
                # Final purchase value
                total_revenue_usd += product.price_usd

        completion_rate = round(completed_count / total_personas, 4)
        step_conversion_rates: Dict[str, float] = {}
        for step in steps:
            entered = step_entered_counts[step.step_id]
            passed = step_passed_counts[step.step_id]
            rate = round(passed / entered, 4) if entered > 0 else 0.0
            step_conversion_rates[step.step_id] = rate

        aov = round(total_revenue_usd / completed_count, 2) if completed_count > 0 else 0.0
        recommendations = self._generate_recommendations(
            step_dropoffs=step_dropoffs,
            top_objections=top_objections,
            total_personas=total_personas,
            product=product,
        )

        return CohortReport(
            cohort_id=f"cohort_{uuid.uuid4().hex[:12]}",
            product_title=product.title,
            total_personas=total_personas,
            completed_count=completed_count,
            completion_rate=completion_rate,
            step_dropoffs=step_dropoffs,
            step_conversion_rates=step_conversion_rates,
            top_objections=top_objections,
            average_order_value=aov,
            estimated_revenue_usd=round(total_revenue_usd, 2),
            actionable_recommendations=recommendations,
        )

    def _evaluate_step(
        self,
        step: FunnelStep,
        persona: CustomerPersona,
        accumulated_trust: float,
        product: ProductSeed,
        rng: random.Random,
    ) -> StepResult:
        """Evaluate whether a persona passes or drops off at a given funnel step."""
        # 1. Hard Budget Gate
        if step.price_point_usd and step.price_point_usd > 0:
            if step.price_point_usd > persona.budget_usd:
                return StepResult(
                    persona_id=persona.id,
                    step_id=step.step_id,
                    proceeded=False,
                    triggered_objection=ObjectionType.PRICE_TOO_HIGH,
                    hesitation_score=0.95,
                    feedback_comment=f"Price ${step.price_point_usd:.2f} exceeds available budget of ${persona.budget_usd:.2f}.",
                )

        # 2. Trust vs Required Threshold Gate
        trust_deficit = step.required_trust_threshold - accumulated_trust
        if trust_deficit > 0:
            # Chance to drop off depends on trust deficit and risk tolerance
            drop_chance = min(0.95, trust_deficit * (1.5 - persona.psychographics.risk_tolerance))
            if rng.random() < drop_chance:
                # Persona drops due to lack of trust or unclear value
                objection = (
                    ObjectionType.LACK_OF_TRUST
                    if ObjectionType.LACK_OF_TRUST in step.friction_factors
                    else ObjectionType.UNCLEAR_VALUE
                )
                return StepResult(
                    persona_id=persona.id,
                    step_id=step.step_id,
                    proceeded=False,
                    triggered_objection=objection,
                    hesitation_score=min(1.0, 0.5 + trust_deficit),
                    feedback_comment=f"Trust threshold not met at {step.name}. Need more verified proof or clearer guarantee.",
                )

        # 3. Step Friction vs Primary Objections Alignment
        matching_objections = [
            obj for obj in persona.primary_objections if obj in step.friction_factors
        ]

        if matching_objections:
            # Check if urgency or impulse overcomes the friction
            friction_severity = len(matching_objections) * 0.25
            resistance_score = friction_severity * persona.skepticism_score
            overcome_power = (
                persona.urgency_score * 0.5
                + persona.psychographics.decision_speed * 0.3
                + (0.3 if persona.mindset == BuyerMindset.IMPULSE else 0.0)
            )

            if resistance_score > overcome_power + rng.uniform(-0.15, 0.15):
                triggered_obj = rng.choice(matching_objections)
                return StepResult(
                    persona_id=persona.id,
                    step_id=step.step_id,
                    proceeded=False,
                    triggered_objection=triggered_obj,
                    hesitation_score=min(1.0, resistance_score),
                    feedback_comment=f"Abandoned at {step.name} due to concerns regarding {triggered_obj.value.replace('_', ' ')}.",
                )

        # 4. Success / Progression
        hesitation = max(
            0.0,
            min(
                1.0,
                0.2 * persona.skepticism_score
                + 0.2 * (1.0 - persona.psychographics.decision_speed)
                + (0.2 if step.price_point_usd and step.price_point_usd > 0 else 0.0),
            ),
        )

        return StepResult(
            persona_id=persona.id,
            step_id=step.step_id,
            proceeded=True,
            triggered_objection=None,
            hesitation_score=round(hesitation, 3),
            feedback_comment="Progressed through stage smoothly.",
        )

    def _generate_recommendations(
        self,
        step_dropoffs: Dict[str, int],
        top_objections: Dict[str, int],
        total_personas: int,
        product: ProductSeed,
    ) -> List[str]:
        """Synthesize concrete, actionable CRO (Conversion Rate Optimization) insights."""
        recommendations: List[str] = []

        # Find worst bottleneck step
        if step_dropoffs:
            worst_step = max(step_dropoffs.items(), key=lambda x: x[1])
            worst_step_id, worst_drop_count = worst_step
            drop_percentage = (worst_drop_count / total_personas) * 100
            if drop_percentage > 20:
                recommendations.append(
                    f"CRITICAL BOTTLENECK: Funnel step '{worst_step_id}' experienced {worst_drop_count} "
                    f"drop-offs ({drop_percentage:.1f}% of cohort). Prioritize redesign and friction audit here."
                )

        # Objection-driven recommendations
        price_drops = top_objections.get(ObjectionType.PRICE_TOO_HIGH.value, 0)
        if price_drops > 0 and (price_drops / total_personas) > 0.15:
            recommendations.append(
                f"PRICING ELASTICITY: {price_drops} personas triggered '{ObjectionType.PRICE_TOO_HIGH.value}'. "
                f"Introduce BNPL (Klarna/Affirm), a 3-pay installment option, or offer an entry-level tier below ${product.price_usd:.2f}."
            )

        trust_drops = top_objections.get(ObjectionType.LACK_OF_TRUST.value, 0)
        if trust_drops > 0 and (trust_drops / total_personas) > 0.12:
            recommendations.append(
                f"TRUST DEFICIT: {trust_drops} personas dropped due to '{ObjectionType.LACK_OF_TRUST.value}'. "
                "Add verified social proof badges, video testimonials, and an explicit 30-day money-back guarantee above the fold."
            )

        shipping_drops = top_objections.get(ObjectionType.SHIPPING_DELAY.value, 0)
        if shipping_drops > 0:
            recommendations.append(
                f"LOGISTICS FRICTION: {shipping_drops} personas hesitated on '{ObjectionType.SHIPPING_DELAY.value}'. "
                "Highlight 'Free 2-day delivery on orders over $50' and provide real-time postal tracking estimates in cart drawer."
            )

        value_drops = top_objections.get(ObjectionType.UNCLEAR_VALUE.value, 0)
        if value_drops > 0:
            recommendations.append(
                f"VALUE PROPOSITION: {value_drops} personas dropped over '{ObjectionType.UNCLEAR_VALUE.value}'. "
                "Sharpen headline messaging: replace generic features with quantifiable outcome bullets and before/after comparisons."
            )

        competitor_drops = top_objections.get(ObjectionType.COMPETITOR_PREFERRED.value, 0)
        if competitor_drops > 0:
            recommendations.append(
                f"COMPETITIVE DEFENSE: {competitor_drops} personas preferred alternatives. "
                "Add a side-by-side comparison table showing unique differentiators against market incumbents."
            )

        if not recommendations:
            recommendations.append("High funnel efficiency across all tested archetypes. Ready for ad traffic scale.")

        return recommendations
