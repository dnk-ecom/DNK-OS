# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/cli.py"
# purpose: "Standalone CLI for dnk_distribution Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import sys
import json
from services.dnk_distribution.src.service import (
    check_compliance,
    evaluate_social_metrics,
    mine_audience_themes,
    process_data,
)
from services.dnk_distribution.src.social_feedback import SocialMetrics
from services.dnk_distribution.src.theme_miner import CommentItem


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m services.dnk_distribution.cli [compliance|rlsf|themes|process] <args>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "compliance":
        text = sys.argv[2] if len(sys.argv) > 2 else "Check out this guaranteed miracle cure! Buy now!"
        report = check_compliance(text, is_promotional=True)
        print(f"Compliant: {report.is_compliant} | Score: {report.score} | Violations: {report.total_violations}")
        for v in report.violations:
            print(f"  - [{v.severity.value.upper()}] {v.category.value}: {v.message}")
        if report.sanitized_text != text:
            print(f"\nSanitized: {report.sanitized_text}")
    elif cmd == "rlsf":
        metrics = SocialMetrics(
            publication_id="pub_sample_01",
            views=10000,
            retention_rate_3s=0.72,
            completion_rate=0.35,
            shares=350,
            likes=850,
            comments=120,
        )
        report = evaluate_social_metrics(metrics, hook_type="curiosity_gap")
        print(f"Tier: {report.reward.performance_tier.value.upper()} | Overall Reward: {report.reward.overall_reward}")
        print(f"Hook Reward: {report.reward.hook_reward} | Virality: {report.reward.virality_reward}")
        for ins in report.distilled_insights:
            print(f"  * {ins}")
    elif cmd == "themes":
        sample = [
            CommentItem(text="This looks way too expensive for what it does", likes=8),
            CommentItem(text="How long does delivery take to California?", likes=3),
            CommentItem(text="Need this right now! Where is the link?", likes=12),
        ]
        res = mine_audience_themes(sample)
        print(f"Analyzed {res.total_comments_analyzed} comments. Dominant themes: {len(res.dominant_themes)}")
        for t in res.dominant_themes:
            print(f"  - {t.theme} ({t.theme_type}): {t.actionable_angle}")
    else:
        query = sys.argv[2] if len(sys.argv) > 2 else "default"
        print(process_data(query))


if __name__ == "__main__":
    main()
