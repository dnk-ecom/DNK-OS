# --- DNK-MRH-HEADER ---
# mrh_id: "packages/swarm_simulation/generator.py"
# purpose: "Clean-Room MIT Synthetic Customer Persona Generator Engine."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "Gerych Prime & Antigravity"
# --- END DNK-MRH-HEADER ---

"""Clean-Room Synthetic Customer Generator.

Produces diverse, statistically grounded customer persona cohorts from a ProductSeed.
Adheres strictly to Clean-Room reverse engineering invariants (zero MiroFish AGPL code).
"""

import random
from typing import List, Optional

from packages.swarm_simulation.models import (
    BuyerMindset,
    CustomerPersona,
    ObjectionType,
    ProductSeed,
    PsychographicProfile,
)

_FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley",
    "Elena", "Marcus", "Sophia", "Liam", "Maya", "Noah", "Olivia", "Lucas",
    "Emma", "Dmitry", "Aria", "Kai", "Chloe", "Zack", "Hanna", "Taras"
]

_LAST_NAMES = [
    "Vance", "Kovacs", "Sterling", "Chen", "Novak", "Dubois", "Smith", "Miller",
    "Petrenko", "Larsen", "Mendoza", "Kim", "Tanaka", "Ivanov", "Shevchenko", "Weber"
]

_OCCUPATIONS_BY_MINDSET = {
    BuyerMindset.ANALYTICAL: [
        "Data Scientist", "Software Architect", "Financial Analyst", "Research Engineer",
        "Systems Administrator", "Biochemist", "Actuary"
    ],
    BuyerMindset.PRICE_SENSITIVE: [
        "Freelance Designer", "Graduate Student", "Junior Support Specialist", "Retail Associate",
        "Elementary Teacher", "Administrative Assistant"
    ],
    BuyerMindset.SKEPTIC: [
        "Security Consultant", "Investigative Journalist", "Compliance Auditor", "Legal Counsel",
        "Procurement Manager", "Cybersecurity Analyst"
    ],
    BuyerMindset.IMPULSE: [
        "Creative Director", "Growth Marketer", "Social Media Influencer", "Event Producer",
        "Sales Executive", "Content Creator"
    ],
    BuyerMindset.PREMIUM: [
        "Managing Director", "Venture Partner", "Chief Technology Officer", "Product VP",
        "Enterprise Consultant", "Architectural Lead"
    ],
}

_MBTI_BY_MINDSET = {
    BuyerMindset.ANALYTICAL: ["INTJ", "INTP", "ISTJ", "ENTP"],
    BuyerMindset.PRICE_SENSITIVE: ["ISFJ", "ISTP", "ESFJ", "ISFP"],
    BuyerMindset.SKEPTIC: ["INTJ", "ISTJ", "INFJ", "INTP"],
    BuyerMindset.IMPULSE: ["ENFP", "ESFP", "ESTP", "ENTP"],
    BuyerMindset.PREMIUM: ["ENTJ", "ESTJ", "INTJ", "ENFJ"],
}


class SyntheticCustomerGenerator:
    """Generates synthetic customer cohorts with distinct cognitive and behavioral archetypes."""

    def __init__(self, seed: Optional[int] = 42):
        self.default_seed = seed

    def generate_cohort(
        self,
        product: ProductSeed,
        size: int = 50,
        seed: Optional[int] = None,
    ) -> List[CustomerPersona]:
        """Generates a list of CustomerPersonas tailored to the target product."""
        active_seed = seed if seed is not None else self.default_seed
        rng = random.Random(active_seed)

        personas: List[CustomerPersona] = []
        for idx in range(1, size + 1):
            persona_id = f"persona-{active_seed if active_seed is not None else 0}-{idx:04d}"
            mindset = self._derive_mindset(rng, product.price_usd)
            psychographics = self._assign_psychographics(mindset, rng)
            budget = self._calculate_budget(mindset, product.price_usd, rng)
            objections = self._extract_objections(mindset, rng)
            skepticism = self._calculate_skepticism(mindset, rng)
            urgency = self._calculate_urgency(mindset, rng)

            first = rng.choice(_FIRST_NAMES)
            last = rng.choice(_LAST_NAMES)
            occupation = rng.choice(_OCCUPATIONS_BY_MINDSET[mindset])
            age = rng.randint(22, 62)

            bio = (
                f"{first} {last} is a {age}-year-old {occupation}. As a {mindset.value} buyer, "
                f"their purchasing focus centers on {', '.join(psychographics.buying_motivations[:2])}."
            )

            persona = CustomerPersona(
                id=persona_id,
                name=f"{first} {last}",
                mindset=mindset,
                age=age,
                occupation=occupation,
                budget_usd=budget,
                skepticism_score=skepticism,
                urgency_score=urgency,
                primary_objections=objections,
                psychographics=psychographics,
                bio=bio,
                metadata={
                    "product_category": product.category,
                    "target_product": product.title,
                    "seed_reference": active_seed,
                },
            )
            personas.append(persona)

        return personas

    def _derive_mindset(self, rng: random.Random, price_usd: float) -> BuyerMindset:
        """Determines persona mindset with distribution biased by price point."""
        if price_usd >= 200.0:
            weights = [0.10, 0.35, 0.15, 0.25, 0.15]  # impulse, analytical, price_sensitive, skeptic, premium
        elif price_usd <= 30.0:
            weights = [0.35, 0.15, 0.30, 0.15, 0.05]
        else:
            weights = [0.20, 0.30, 0.25, 0.15, 0.10]

        mindsets = [
            BuyerMindset.IMPULSE,
            BuyerMindset.ANALYTICAL,
            BuyerMindset.PRICE_SENSITIVE,
            BuyerMindset.SKEPTIC,
            BuyerMindset.PREMIUM,
        ]
        return rng.choices(mindsets, weights=weights, k=1)[0]

    def _assign_psychographics(
        self, mindset: BuyerMindset, rng: random.Random
    ) -> PsychographicProfile:
        """Constructs psychographic attributes tuned to the specific buyer mindset."""
        mbti = rng.choice(_MBTI_BY_MINDSET[mindset])

        if mindset == BuyerMindset.IMPULSE:
            risk = rng.uniform(0.65, 0.95)
            speed = rng.uniform(0.70, 0.98)
            social_proof = rng.uniform(0.50, 0.85)
            loyalty = rng.uniform(0.20, 0.50)
            motivations = ["instant_gratification", "novelty", "social_trend", "aesthetics"]
            values = ["speed", "enjoyment", "status"]
        elif mindset == BuyerMindset.ANALYTICAL:
            risk = rng.uniform(0.15, 0.45)
            speed = rng.uniform(0.10, 0.40)
            social_proof = rng.uniform(0.60, 0.90)
            loyalty = rng.uniform(0.40, 0.70)
            motivations = ["specifications", "benchmarks", "efficiency", "durability"]
            values = ["precision", "competence", "transparency"]
        elif mindset == BuyerMindset.PRICE_SENSITIVE:
            risk = rng.uniform(0.10, 0.35)
            speed = rng.uniform(0.20, 0.50)
            social_proof = rng.uniform(0.40, 0.75)
            loyalty = rng.uniform(0.10, 0.40)
            motivations = ["discounts", "value_for_money", "cost_recovery", "affordability"]
            values = ["frugality", "practicality", "security"]
        elif mindset == BuyerMindset.SKEPTIC:
            risk = rng.uniform(0.05, 0.25)
            speed = rng.uniform(0.05, 0.30)
            social_proof = rng.uniform(0.75, 0.98)
            loyalty = rng.uniform(0.30, 0.60)
            motivations = ["risk_mitigation", "verified_guarantees", "transparent_terms"]
            values = ["skepticism", "authenticity", "reliability"]
        else:  # PREMIUM
            risk = rng.uniform(0.50, 0.80)
            speed = rng.uniform(0.40, 0.75)
            social_proof = rng.uniform(0.30, 0.60)
            loyalty = rng.uniform(0.60, 0.90)
            motivations = ["superior_craftsmanship", "vip_support", "exclusive_features"]
            values = ["excellence", "prestige", "time_saving"]

        return PsychographicProfile(
            mbti=mbti,
            risk_tolerance=round(risk, 3),
            decision_speed=round(speed, 3),
            social_proof_sensitivity=round(social_proof, 3),
            brand_loyalty=round(loyalty, 3),
            core_values=values,
            buying_motivations=motivations,
        )

    def _calculate_budget(
        self, mindset: BuyerMindset, base_price: float, rng: random.Random
    ) -> float:
        """Calculates a realistic allocated budget based on mindset and price."""
        if mindset == BuyerMindset.PRICE_SENSITIVE:
            multiplier = rng.uniform(0.65, 1.15)
        elif mindset == BuyerMindset.IMPULSE:
            multiplier = rng.uniform(0.90, 1.80)
        elif mindset == BuyerMindset.ANALYTICAL:
            multiplier = rng.uniform(1.00, 2.00)
        elif mindset == BuyerMindset.SKEPTIC:
            multiplier = rng.uniform(0.85, 1.50)
        else:  # PREMIUM
            multiplier = rng.uniform(1.80, 4.50)

        raw_budget = max(base_price * multiplier, 1.0)
        return round(raw_budget, 2)

    def _extract_objections(
        self, mindset: BuyerMindset, rng: random.Random
    ) -> List[ObjectionType]:
        """Selects likely friction triggers based on persona archetype."""
        pool: List[ObjectionType] = []
        if mindset == BuyerMindset.PRICE_SENSITIVE:
            pool = [ObjectionType.PRICE_TOO_HIGH, ObjectionType.UNCLEAR_VALUE]
        elif mindset == BuyerMindset.SKEPTIC:
            pool = [ObjectionType.LACK_OF_TRUST, ObjectionType.UNCLEAR_VALUE, ObjectionType.COMPETITOR_PREFERRED]
        elif mindset == BuyerMindset.ANALYTICAL:
            pool = [ObjectionType.UNCLEAR_VALUE, ObjectionType.COMPETITOR_PREFERRED]
        elif mindset == BuyerMindset.IMPULSE:
            pool = [ObjectionType.SHIPPING_DELAY, ObjectionType.LACK_OF_TRUST]
        else:  # PREMIUM
            pool = [ObjectionType.UNCLEAR_VALUE, ObjectionType.COMPETITOR_PREFERRED]

        count = rng.randint(1, min(len(pool), 2))
        return rng.sample(pool, count)

    def _calculate_skepticism(self, mindset: BuyerMindset, rng: random.Random) -> float:
        """Derives baseline skepticism score for the archetype."""
        if mindset == BuyerMindset.SKEPTIC:
            return round(rng.uniform(0.70, 0.98), 3)
        if mindset == BuyerMindset.ANALYTICAL:
            return round(rng.uniform(0.50, 0.75), 3)
        if mindset == BuyerMindset.PRICE_SENSITIVE:
            return round(rng.uniform(0.40, 0.70), 3)
        if mindset == BuyerMindset.IMPULSE:
            return round(rng.uniform(0.10, 0.35), 3)
        # PREMIUM
        return round(rng.uniform(0.25, 0.55), 3)

    def _calculate_urgency(self, mindset: BuyerMindset, rng: random.Random) -> float:
        """Derives urgency/need score for the archetype."""
        if mindset == BuyerMindset.IMPULSE:
            return round(rng.uniform(0.65, 0.95), 3)
        if mindset == BuyerMindset.PREMIUM:
            return round(rng.uniform(0.45, 0.80), 3)
        if mindset == BuyerMindset.ANALYTICAL:
            return round(rng.uniform(0.20, 0.55), 3)
        if mindset == BuyerMindset.PRICE_SENSITIVE:
            return round(rng.uniform(0.25, 0.60), 3)
        # SKEPTIC
        return round(rng.uniform(0.15, 0.45), 3)
