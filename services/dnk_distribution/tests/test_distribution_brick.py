# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/tests/test_distribution_brick.py"
# purpose: "Comprehensive Unit Tests for dnk_distribution Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from services.dnk_distribution.src.service import (
    check_compliance,
    evaluate_social_metrics,
    mine_audience_themes,
    process_data,
)
from services.dnk_distribution.src.brand_compliance import (
    BrandComplianceEngine,
    BrandProfile,
    ViolationSeverity,
)
from services.dnk_distribution.src.social_feedback import (
    SocialFeedbackRLSFEngine,
    SocialMetrics,
    PerformanceTier,
)
from services.dnk_distribution.src.theme_miner import (
    AudienceThemeMiner,
    CommentItem,
)


def test_process_data_fallback():
    assert process_data("ping") == "Processed: ping"


def test_brand_compliance_detects_blockers():
    dirty_text = "This secret miracle cure is guaranteed 100% wealth while you sleep! Shady rival is a scam!"
    report = check_compliance(dirty_text, is_promotional=True)

    assert report.is_compliant is False
    assert report.score < 0.60
    assert report.has_blockers is True
    assert report.total_violations >= 3

    categories = [v.category.value for v in report.violations]
    assert "legal_claims" in categories
    assert "competitor_slander" in categories
    assert "ftc_disclosure" in categories

    # Verify auto-sanitization cleans the text
    assert report.sanitized_text is not None
    assert "miracle cure" not in report.sanitized_text


def test_brand_compliance_passes_clean_promotional_copy():
    clean_text = "Discover our newly engineered ergonomic workspace setup designed for high-focus builders. #ad"
    report = check_compliance(clean_text, is_promotional=True)

    assert report.is_compliant is True
    assert report.score >= 0.95
    assert report.has_blockers is False
    assert report.total_violations == 0


def test_social_feedback_rlsf_viral_and_underperforming_tiers():
    # 1. High-performing / Viral test
    viral_metrics = SocialMetrics(
        publication_id="pub_viral_01",
        views=25000,
        retention_rate_3s=0.78,
        retention_rate_15s=0.55,
        completion_rate=0.40,
        likes=2200,
        comments=350,
        shares=1200,
        saves=800,
    )
    viral_report = evaluate_social_metrics(viral_metrics, hook_type="bold_claim")

    assert viral_report.reward.performance_tier in (PerformanceTier.VIRAL_TIER, PerformanceTier.HIGH_PERFORMING)
    assert viral_report.reward.hook_reward >= 0.85
    assert viral_report.reward.virality_reward >= 0.75
    assert len(viral_report.distilled_insights) > 0

    # 2. Underperforming test
    poor_metrics = SocialMetrics(
        publication_id="pub_poor_01",
        views=500,
        retention_rate_3s=0.20,
        retention_rate_15s=0.10,
        completion_rate=0.05,
        likes=5,
        comments=1,
        shares=0,
        saves=1,
    )
    poor_report = evaluate_social_metrics(poor_metrics)
    assert poor_report.reward.performance_tier == PerformanceTier.UNDERPERFORMING
    assert poor_report.reward.overall_reward < 0.35


def test_theme_miner_clusters_objections_and_intent():
    comments = [
        CommentItem(text="This is way too expensive for what it is", likes=15),
        CommentItem(text="Costs too much, I can get similar on Amazon", likes=8),
        CommentItem(text="How long is shipping to Germany? Does it have tracking?", likes=4),
        CommentItem(text="Is this legit? Looks like a fake scam", likes=2),
        CommentItem(text="I need this right now! Where is the link to buy?", likes=25),
        CommentItem(text="Buying for my husband as a gift!", likes=10),
    ]

    result = mine_audience_themes(comments)

    assert result.total_comments_analyzed == 6
    assert len(result.dominant_themes) >= 3

    theme_names = [t.theme for t in result.dominant_themes]
    assert "Pricing & Perceived Value" in theme_names
    assert "Shipping Time & Tracking" in theme_names
    assert "Direct Buying Intent" in theme_names

    # Check actionable angles
    assert len(result.suggested_copy_angles) >= 2
    assert any("Buy Box" in a or "money-back" in a for a in result.suggested_copy_angles)


def test_fastmcp_distribution_tools():
    from services.dnk_distribution.mcp_server import (
        distribution_check_compliance,
        distribution_evaluate_rlsf,
        distribution_mine_themes,
    )

    # 1. Compliance tool
    res_comp = distribution_check_compliance("Clean text with #ad", is_promotional=True)
    assert res_comp["is_compliant"] is True

    # 2. RLSF tool
    res_rlsf = distribution_evaluate_rlsf(
        publication_id="pub_test",
        views=5000,
        retention_rate_3s=0.70,
        completion_rate=0.30,
        shares=150
    )
    assert "reward" in res_rlsf
    assert "performance_tier" in res_rlsf["reward"]

    # 3. Theme miner tool
    res_themes = distribution_mine_themes([
        {"text": "Too expensive for me", "likes": 5}
    ])
    assert res_themes["total_comments_analyzed"] == 1
    assert len(res_themes["dominant_themes"]) == 1
