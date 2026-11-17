# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/brand_compliance.py"
# purpose: "Brand Compliance Gate & Tone of Voice Engine for dnk_distribution Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import re
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ComplianceCategory(str, Enum):
    TONE_OF_VOICE = "tone_of_voice"
    BANNED_WORDS = "banned_words"
    LEGAL_CLAIMS = "legal_claims"
    FTC_DISCLOSURE = "ftc_disclosure"
    COMPETITOR_SLANDER = "competitor_slander"
    PROFANITY = "profanity"


class ViolationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


class ComplianceViolation(BaseModel):
    category: ComplianceCategory
    severity: ViolationSeverity
    rule_id: str
    message: str
    matched_text: Optional[str] = None
    suggestion: Optional[str] = None


class ComplianceReport(BaseModel):
    is_compliant: bool
    score: float = Field(default=1.0, description="Compliance score from 0.0 to 1.0")
    total_violations: int = 0
    violations: List[ComplianceViolation] = Field(default_factory=list)
    has_blockers: bool = False
    sanitized_text: Optional[str] = None
    brand_name: str = "DNK OS"


class BrandProfile(BaseModel):
    brand_name: str = "DNK OS"
    target_audience: str = "Founders, Creators, E-commerce Operators"
    allowed_tones: List[str] = Field(
        default_factory=lambda: ["professional", "authoritative", "inspiring", "dynamic", "educational"]
    )
    banned_words: List[str] = Field(
        default_factory=lambda: [
            "guaranteed millions",
            "get rich quick",
            "100% risk free",
            "miracle cure",
            "secret hack they don't want you to know",
            "cheat the algorithm",
        ]
    )
    competitors_blacklist: List[str] = Field(
        default_factory=lambda: ["scam competitor", "shady rival"]
    )
    require_ftc_if_promotional: bool = True
    ftc_valid_tags: List[str] = Field(
        default_factory=lambda: ["#ad", "#sponsored", "#partner", "#advertisement", "#affiliate"]
    )
    max_exclamation_marks: int = 4


class BrandComplianceEngine:
    """
    Evaluates marketing copy, scripts, and video captions against
    legal requirements, brand guidelines, and FTC compliance.
    """

    MEDICAL_CLAIM_PATTERNS = [
        (r"\b(cures?|prevents?|treats?)\s+(cancer|diabetes|depression|insomnia|covid|disease)\b", "Unsubstantiated medical cure claim (FDA/FTC violation)"),
        (r"\b(miracle\s+(cure|drug|pill|supplement))\b", "Deceptive health miracle claim"),
        (r"\blost\s+\d+\s*(lbs|kg|pounds)\s+in\s+\d+\s*(days|hours)\b", "Unsubstantiated rapid weight loss claim"),
    ]

    FINANCIAL_CLAIM_PATTERNS = [
        (r"\b(guaranteed\s+(100%|return|income|profit|wealth|millions))\b", "FTC violation: Unsubstantiated financial/income guarantee"),
        (r"\b(risk-free\s+(investment|passive income|wealth))\b", "FTC violation: Deceptive risk-free wealth claim"),
        (r"\b(make\s+\$\d+k?\s+(overnight|while you sleep|in\s+\d+\s*minutes))\b", "Misleading income promise"),
    ]

    PROFANITY_LIST = [
        "scam", "bullshit", "idiots", "morons", "fraudulent", "fucking", "shit", "bastards"
    ]

    def __init__(self, default_profile: Optional[BrandProfile] = None):
        self.profile = default_profile or BrandProfile()

    def validate(
        self,
        text: str,
        profile: Optional[BrandProfile] = None,
        is_promotional: bool = False,
    ) -> ComplianceReport:
        active_profile = profile or self.profile
        violations: List[ComplianceViolation] = []
        lowered = text.lower()

        # 1. Banned words inspection
        for word in active_profile.banned_words:
            if word.lower() in lowered:
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.BANNED_WORDS,
                        severity=ViolationSeverity.ERROR,
                        rule_id="BAN-001",
                        message=f"Banned brand keyword or overpromise: '{word}'",
                        matched_text=word,
                        suggestion="Rephrase with grounded, value-focused terminology.",
                    )
                )

        # 2. Competitor slander check
        for competitor in active_profile.competitors_blacklist:
            if competitor.lower() in lowered:
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.COMPETITOR_SLANDER,
                        severity=ViolationSeverity.BLOCKER,
                        rule_id="SLAND-001",
                        message=f"Direct competitor attack detected: '{competitor}'",
                        matched_text=competitor,
                        suggestion="Focus on your unique product merits rather than direct naming.",
                    )
                )

        # 3. Medical Claims (Regulatory blocker)
        for pattern, desc in self.MEDICAL_CLAIM_PATTERNS:
            match = re.search(pattern, lowered)
            if match:
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.LEGAL_CLAIMS,
                        severity=ViolationSeverity.BLOCKER,
                        rule_id="MED-001",
                        message=desc,
                        matched_text=match.group(0),
                        suggestion="Do not make diagnostic or therapeutic promises without regulatory proof.",
                    )
                )

        # 4. Financial / E-commerce Guarantees (FTC blocker)
        for pattern, desc in self.FINANCIAL_CLAIM_PATTERNS:
            match = re.search(pattern, lowered)
            if match:
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.LEGAL_CLAIMS,
                        severity=ViolationSeverity.BLOCKER,
                        rule_id="FIN-001",
                        message=desc,
                        matched_text=match.group(0),
                        suggestion="Add disclaimers like 'Results may vary' or remove specific guarantees.",
                    )
                )

        # 5. Profanity & Aggressive Language
        for bad_word in self.PROFANITY_LIST:
            if re.search(rf"\b{re.escape(bad_word)}\b", lowered):
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.PROFANITY,
                        severity=ViolationSeverity.BLOCKER,
                        rule_id="PROF-001",
                        message=f"Inappropriate or hostile language detected: '{bad_word}'",
                        matched_text=bad_word,
                        suggestion="Use clean, professional vocabulary.",
                    )
                )

        # 6. FTC Disclosure inspection
        if is_promotional and active_profile.require_ftc_if_promotional:
            has_tag = any(tag.lower() in lowered for tag in active_profile.ftc_valid_tags)
            if not has_tag:
                violations.append(
                    ComplianceViolation(
                        category=ComplianceCategory.FTC_DISCLOSURE,
                        severity=ViolationSeverity.ERROR,
                        rule_id="FTC-001",
                        message="Missing mandatory FTC sponsorship tag for promotional content (#ad, #sponsored, etc.)",
                        matched_text=None,
                        suggestion=f"Append {active_profile.ftc_valid_tags[0]} to the caption/script.",
                    )
                )

        # 7. Tone & Formatting
        exclamation_count = text.count("!")
        if exclamation_count > active_profile.max_exclamation_marks:
            violations.append(
                ComplianceViolation(
                    category=ComplianceCategory.TONE_OF_VOICE,
                    severity=ViolationSeverity.WARNING,
                    rule_id="TOV-001",
                    message=f"Excessive excitement punctuation: {exclamation_count} exclamation marks (max allowed: {active_profile.max_exclamation_marks})",
                    matched_text="!" * exclamation_count,
                    suggestion="Tone down punctuation to avoid appearing spammy or breathless.",
                )
            )

        has_blockers = any(v.severity == ViolationSeverity.BLOCKER for v in violations)
        has_errors = any(v.severity == ViolationSeverity.ERROR for v in violations)
        is_compliant = not (has_blockers or has_errors)

        penalty = 0.0
        for v in violations:
            if v.severity == ViolationSeverity.BLOCKER:
                penalty += 0.55
            elif v.severity == ViolationSeverity.ERROR:
                penalty += 0.2
            elif v.severity == ViolationSeverity.WARNING:
                penalty += 0.05
            elif v.severity == ViolationSeverity.INFO:
                penalty += 0.01

        score = max(0.0, round(1.0 - penalty, 2))
        sanitized = self.auto_sanitize(text, violations) if not is_compliant else text

        return ComplianceReport(
            is_compliant=is_compliant,
            score=score,
            total_violations=len(violations),
            violations=violations,
            has_blockers=has_blockers,
            sanitized_text=sanitized,
            brand_name=active_profile.brand_name,
        )

    def auto_sanitize(self, text: str, violations: Union[List[ComplianceViolation], ComplianceReport]) -> str:
        violation_list = violations.violations if isinstance(violations, ComplianceReport) else violations
        cleaned = text
        for v in violation_list:
            if v.matched_text and v.matched_text in cleaned:
                if v.category == ComplianceCategory.PROFANITY:
                    cleaned = re.sub(rf"\b{re.escape(v.matched_text)}\b", "[redacted]", cleaned, flags=re.IGNORECASE)
                elif v.category == ComplianceCategory.BANNED_WORDS:
                    cleaned = cleaned.replace(v.matched_text, "[verified strategy]")
                elif v.category == ComplianceCategory.LEGAL_CLAIMS:
                    cleaned = cleaned.replace(v.matched_text, "[disclosed result]")
        return cleaned


brand_compliance_engine = BrandComplianceEngine()
