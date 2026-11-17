# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/theme_miner.py"
# purpose: "Audience Theme & Comment Objection Mining Engine for dnk_distribution Sovereign Brick"
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
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CommentItem(BaseModel):
    id: Optional[str] = None
    author: Optional[str] = None
    text: str = Field(..., description="Raw text of the comment")
    likes: int = Field(default=0, description="Upvote or like count")
    category: Optional[str] = Field(
        default="general",
        description="question, objection, pain_point, praise, buying_intent, feature_request"
    )


class AudienceTheme(BaseModel):
    theme: str = Field(..., description="Identified semantic theme or pattern")
    theme_type: str = Field(..., description="pain_point, objection, buying_intent, question, praise")
    frequency: int = Field(default=1, description="Number of occurrences")
    intensity: str = Field(default="medium", description="high, medium, low")
    representative_quotes: List[str] = Field(default_factory=list)
    actionable_angle: Optional[str] = Field(default=None, description="Suggested copy angle or counter-objection")


class ThemeMiningResult(BaseModel):
    total_comments_analyzed: int
    dominant_themes: List[AudienceTheme]
    top_objections: List[str]
    suggested_copy_angles: List[str]
    overall_sentiment_summary: Dict[str, int]


class AudienceThemeMiner:
    """
    Mines raw customer comments, reviews, and questions to extract
    high-leverage conversion objections and psychological pain points.
    """

    OBJECTION_PATTERNS = [
        (r"\b(too expensive|overpriced|costs too much|pricey|waste of money)\b", "Pricing & Perceived Value", "Anchor with daily cost comparison and 30-day money-back guarantee"),
        (r"\b(shipping|delivery|took so long|customs|how long to ship)\b", "Shipping Time & Tracking", "Display guaranteed delivery estimator block above the Buy Box"),
        (r"\b(size|sizing|fits?|small|large|tight|too big)\b", "Sizing Uncertainty", "Implement Interactive Size Recommender modal with 1-click exchange"),
        (r"\b(does it work|fake|scam|legit|skeptical|proof)\b", "Credibility & Trust", "Feature customer video reviews and clinical/lab test badges directly on ATC bar"),
        (r"\b(return|refund|warranty|guarantee)\b", "Risk Reversal", "Emphasize zero-hassle instant refunds and prepaid return labels"),
    ]

    INTENT_PATTERNS = [
        (r"\b(need this|buying|take my money|ordered|where to buy|link)\b", "Direct Buying Intent", "Add sticky ATC bar for immediate checkout conversion"),
        (r"\b(gift for|buying for my|christmas|birthday)\b", "Gifting Intent", "Offer 1-click Gift Box bundle tier with customized greeting card"),
    ]

    def __init__(self) -> None:
        pass

    def mine_comments(self, comments: List[CommentItem]) -> ThemeMiningResult:
        if not comments:
            return ThemeMiningResult(
                total_comments_analyzed=0,
                dominant_themes=[],
                top_objections=[],
                suggested_copy_angles=[],
                overall_sentiment_summary={"positive": 0, "neutral": 0, "negative": 0}
            )

        theme_buckets: Dict[str, AudienceTheme] = {}
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        top_objections: List[str] = []
        copy_angles: List[str] = []

        for c in comments:
            lowered = c.text.lower()
            matched = False

            # 1. Match Objections
            for regex, theme_name, angle in self.OBJECTION_PATTERNS:
                if re.search(regex, lowered):
                    matched = True
                    sentiment_counts["negative"] += 1
                    if theme_name not in theme_buckets:
                        theme_buckets[theme_name] = AudienceTheme(
                            theme=theme_name,
                            theme_type="objection",
                            frequency=1,
                            intensity="high" if c.likes > 5 else "medium",
                            representative_quotes=[c.text[:120]],
                            actionable_angle=angle
                        )
                        if theme_name not in top_objections:
                            top_objections.append(theme_name)
                        if angle not in copy_angles:
                            copy_angles.append(angle)
                    else:
                        theme_buckets[theme_name].frequency += 1
                        if len(theme_buckets[theme_name].representative_quotes) < 3:
                            theme_buckets[theme_name].representative_quotes.append(c.text[:120])
                    break

            # 2. Match Buying Intent
            if not matched:
                for regex, theme_name, angle in self.INTENT_PATTERNS:
                    if re.search(regex, lowered):
                        matched = True
                        sentiment_counts["positive"] += 1
                        if theme_name not in theme_buckets:
                            theme_buckets[theme_name] = AudienceTheme(
                                theme=theme_name,
                                theme_type="buying_intent",
                                frequency=1,
                                intensity="high",
                                representative_quotes=[c.text[:120]],
                                actionable_angle=angle
                            )
                            if angle not in copy_angles:
                                copy_angles.append(angle)
                        else:
                            theme_buckets[theme_name].frequency += 1
                            if len(theme_buckets[theme_name].representative_quotes) < 3:
                                theme_buckets[theme_name].representative_quotes.append(c.text[:120])
                        break

            if not matched:
                sentiment_counts["neutral"] += 1

        sorted_themes = sorted(theme_buckets.values(), key=lambda t: t.frequency, reverse=True)

        return ThemeMiningResult(
            total_comments_analyzed=len(comments),
            dominant_themes=sorted_themes,
            top_objections=top_objections,
            suggested_copy_angles=copy_angles,
            overall_sentiment_summary=sentiment_counts
        )


audience_theme_miner = AudienceThemeMiner()
