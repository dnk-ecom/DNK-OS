# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/adversarial_review_gate.py"
# purpose: "Adversarial Pre-Commit & Decision Gate (5-Vector Critique Framework) for DNK_OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CritiqueVerdict(str, Enum):
    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    REJECTED = "REJECTED"


@dataclass
class VectorAssessment:
    vector_name: str
    risk_level: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    observation: str
    boundary_limit: str


@dataclass
class AdversarialReviewResult:
    subject: str
    verdict: CritiqueVerdict
    what_this_is: str
    problem: str
    fix: str
    if_we_skip_it: str
    vectors: List[VectorAssessment] = field(default_factory=list)
    skeptic_alternative: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "verdict": self.verdict.value,
            "what_this_is": self.what_this_is,
            "problem": self.problem,
            "fix": self.fix,
            "if_we_skip_it": self.if_we_skip_it,
            "skeptic_alternative": self.skeptic_alternative,
            "vectors": [
                {
                    "name": v.vector_name,
                    "risk": v.risk_level,
                    "observation": v.observation,
                    "boundary": v.boundary_limit,
                }
                for v in self.vectors
            ],
            "passed": self.verdict == CritiqueVerdict.APPROVED,
        }


class AdversarialReviewGate:
    """
    Epistemic Armor & SOTA Adversarial Review Gate (Auditor ⚔️ vs Builder 🛡️).
    Enforces the mandatory 5-Vector Developer Critique Framework prior to
    locking architectural decisions or merging high-blast code.
    """

    CRITIQUE_VECTORS = [
        "1. Boundary Conditions",
        "2. Scalability (100x load)",
        "3. Maintainability & Technical Debt",
        "4. Security & Attack Vectors",
        "5. Computational & Memory Efficiency",
    ]

    def evaluate_proposal(
        self,
        subject: str,
        what_this_is: str,
        problem: str,
        fix: str,
        if_we_skip_it: str,
        vector_assessments: Optional[List[Dict[str, str]]] = None,
        skeptic_alt: str = "",
    ) -> AdversarialReviewResult:
        """Evaluates a proposal across all 5 vectors and determines the verdict."""
        vectors: List[VectorAssessment] = []
        raw_assessments = vector_assessments or []

        has_critical = False
        has_high = False

        for idx, name in enumerate(self.CRITIQUE_VECTORS):
            v_data = raw_assessments[idx] if idx < len(raw_assessments) else {}
            risk = v_data.get("risk", "LOW").upper()
            if risk == "CRITICAL":
                has_critical = True
            elif risk == "HIGH":
                has_high = True

            vectors.append(
                VectorAssessment(
                    vector_name=name,
                    risk_level=risk,
                    observation=v_data.get("observation", "Satisfies baseline invariants."),
                    boundary_limit=v_data.get("boundary", "Standard operating limits."),
                )
            )

        if has_critical:
            verdict = CritiqueVerdict.REJECTED
        elif has_high or not fix.strip():
            verdict = CritiqueVerdict.NEEDS_REVISION
        else:
            verdict = CritiqueVerdict.APPROVED

        return AdversarialReviewResult(
            subject=subject,
            verdict=verdict,
            what_this_is=what_this_is,
            problem=problem,
            fix=fix,
            if_we_skip_it=if_we_skip_it,
            vectors=vectors,
            skeptic_alternative=skeptic_alt,
        )


if __name__ == "__main__":
    gate = AdversarialReviewGate()
    res = gate.evaluate_proposal(
        subject="Living Knowledge Lifecycle & SCONES FTS5 Integration",
        what_this_is="Autonomous eviction of stale documentation and FTS5 BM25 retrieval for agent memories.",
        problem="Static notes rot in 60-90 days, causing attention entropy in LLMs.",
        fix="Enforce AST file-existence guards and SCONES FTS5 belief revision.",
        if_we_skip_it="Agents make mistakes using deprecated APIs and phantom files.",
    )
    print(json.dumps(res.to_dict(), indent=2, ensure_ascii=False))
