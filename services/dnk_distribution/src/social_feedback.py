# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/src/social_feedback.py"
# purpose: "Reinforcement Learning from Social Feedback (RLSF) Engine for dnk_distribution Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.distribution.rlsf")


class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class PerformanceTier(str, Enum):
    VIRAL_TIER = "viral_tier"
    HIGH_PERFORMING = "high_performing"
    AVERAGE = "average"
    UNDERPERFORMING = "underperforming"


class SocialMetrics(BaseModel):
    publication_id: str
    platform: SocialPlatform = SocialPlatform.TIKTOK
    views: int = Field(default=0, ge=0)
    retention_rate_3s: float = Field(default=0.0, ge=0.0, le=1.0)
    retention_rate_15s: float = Field(default=0.0, ge=0.0, le=1.0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)


class SocialRewardBreakdown(BaseModel):
    hook_reward: float
    retention_reward: float
    engagement_reward: float
    virality_reward: float
    overall_reward: float
    performance_tier: PerformanceTier


class ContentFeedbackReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"rlsf_{uuid.uuid4().hex[:12]}")
    publication_id: str
    platform: SocialPlatform
    metrics: SocialMetrics
    reward: SocialRewardBreakdown
    hook_type: Optional[str] = None
    distilled_insights: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SocialFeedbackRLSFEngine:
    """
    Reinforcement Learning from Social Feedback (RLSF) Engine.
    Evaluates published content performance, computes multi-objective social reward signals,
    and produces actionable script and offer recommendations.
    """

    BENCHMARK_RETENTION_3S = 0.65
    BENCHMARK_RETENTION_15S = 0.40
    BENCHMARK_COMPLETION = 0.25
    BENCHMARK_ENGAGEMENT_RATE = 0.05
    BENCHMARK_VIRALITY_RATE = 0.02

    def __init__(self) -> None:
        self._reports: Dict[str, ContentFeedbackReport] = {}

    def compute_reward(self, metrics: SocialMetrics) -> SocialRewardBreakdown:
        # 1. Hook Reward (3s retention)
        hook_reward = min(1.0, metrics.retention_rate_3s / max(self.BENCHMARK_RETENTION_3S, 0.01))

        # 2. Retention Reward (15s retention and completion)
        r15_score = min(1.0, metrics.retention_rate_15s / max(self.BENCHMARK_RETENTION_15S, 0.01))
        comp_score = min(1.0, metrics.completion_rate / max(self.BENCHMARK_COMPLETION, 0.01))
        retention_reward = 0.5 * r15_score + 0.5 * comp_score

        # 3. Engagement Reward
        views = max(metrics.views, 1)
        eng_rate = (metrics.likes + 2.0 * metrics.comments) / views
        engagement_reward = min(1.0, eng_rate / max(self.BENCHMARK_ENGAGEMENT_RATE, 0.001))

        # 4. Virality Reward (Shares count 3x, Saves count 2x)
        vir_rate = (3.0 * metrics.shares + 2.0 * metrics.saves) / views
        virality_reward = min(1.0, vir_rate / max(self.BENCHMARK_VIRALITY_RATE, 0.001))

        overall_reward = (
            0.30 * hook_reward
            + 0.30 * retention_reward
            + 0.20 * engagement_reward
            + 0.20 * virality_reward
        )
        overall_reward = round(max(0.0, min(1.0, overall_reward)), 4)

        if overall_reward >= 0.80:
            tier = PerformanceTier.VIRAL_TIER
        elif overall_reward >= 0.65:
            tier = PerformanceTier.HIGH_PERFORMING
        elif overall_reward >= 0.45:
            tier = PerformanceTier.AVERAGE
        else:
            tier = PerformanceTier.UNDERPERFORMING

        return SocialRewardBreakdown(
            hook_reward=round(hook_reward, 4),
            retention_reward=round(retention_reward, 4),
            engagement_reward=round(engagement_reward, 4),
            virality_reward=round(virality_reward, 4),
            overall_reward=overall_reward,
            performance_tier=tier,
        )

    def evaluate_publication(
        self,
        metrics: SocialMetrics,
        hook_type: Optional[str] = None
    ) -> ContentFeedbackReport:
        reward = self.compute_reward(metrics)

        insights: List[str] = []
        if reward.hook_reward >= 0.85:
            insights.append("Hook outperformed 3s retention benchmark: strong curiosity gap.")
        else:
            insights.append("Hook underperformed 3s retention: test faster pacing, bolder visual motion or immediate problem statement.")

        if reward.virality_reward >= 0.70:
            insights.append("High share-to-view ratio: content triggered high social currency / relational sharing.")

        if reward.performance_tier == PerformanceTier.UNDERPERFORMING:
            insights.append("Overall retention low: apply aggressive silence-cutting and kinetic captions on next generation.")

        report = ContentFeedbackReport(
            publication_id=metrics.publication_id,
            platform=metrics.platform,
            metrics=metrics,
            reward=reward,
            hook_type=hook_type,
            distilled_insights=insights,
        )
        self._reports[report.report_id] = report
        return report


social_feedback_engine = SocialFeedbackRLSFEngine()
