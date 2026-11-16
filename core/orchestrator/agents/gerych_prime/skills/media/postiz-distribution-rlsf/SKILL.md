---
name: postiz-distribution-rlsf
description: Use when publishing content via Postiz, collecting social metrics, and running RLSF feedback loops into SCONES memory.
category: media
---

# Multi-Platform Postiz Auto-Distribution & Closed-Loop Social Feedback (RLSF)

## Overview
This skill operationalizes **Phase 4** of the 2026 Autonomous Content Intelligence Engine. It connects approved content from Phase 3 (`ContentApprovalStatus.APPROVED`) with:
1. **Self-Hosted Postiz Publishing Stack** (`infra/compose/docker-compose.postiz.yml` & `services/dnk_content_intelligence/postiz_publisher.py`):
   - Multi-platform post dispatch and scheduling across TikTok, YouTube Shorts, Instagram Reels, X (Twitter), LinkedIn, Threads, Pinterest, and Reddit.
   - Platform-tailored payload formatting (X 280-char boundaries, hashtag normalization, platform video tags).
   - Mock/deterministic execution mode for offline testing and live HTTP client mode.
2. **Reinforcement Learning from Social Feedback (RLSF)** (`services/dnk_content_intelligence/social_feedback_rlsf.py`):
   - Inspired by **ZJU-REAL/Easel (⭐ 880+)** social feedback alignment.
   - Multi-objective reward modeling combining 3s Hook Retention ($w=0.30$), Video Retention ($w=0.30$), Engagement ($w=0.20$), and Virality ($w=0.20$).
   - Automated heuristic distillation (generating actionable rules for hooks and visual presets).
   - Direct closed-loop memory writes into **SCONES Memory** (`scones_add_memory`), updating future creative generation in Phase 1 & 2.

## Fast Architecture Reference
- **Docker Compose**: `infra/compose/docker-compose.postiz.yml`
- **Publisher Client**: `services/dnk_content_intelligence/postiz_publisher.py`
- **RLSF Feedback Engine**: `services/dnk_content_intelligence/social_feedback_rlsf.py`
- **REST Endpoints**: `apps/api/routers/distribution_router.py`
  - `POST /api/v1/content/distribution/publish`
  - `GET /api/v1/content/distribution/publications`
  - `POST /api/v1/content/distribution/feedback/metrics`
  - `GET /api/v1/content/distribution/feedback/reports`
  - `GET /api/v1/content/distribution/feedback/patterns`
- **Swarm Actions**: `publish_draft`, `record_social_metrics`, `get_content_patterns`

## Python Usage Recipe

```python
from services.dnk_content_intelligence.hitl_gate import ContentHITLGate, ContentDraftCreate, ContentType
from services.dnk_content_intelligence.postiz_publisher import PostizPublisher, DistributionPlatform
from services.dnk_content_intelligence.social_feedback_rlsf import SocialFeedbackRLSFEngine, SocialMetrics

gate = ContentHITLGate()
publisher = PostizPublisher()
rlsf = SocialFeedbackRLSFEngine()

# 1. Prepare and approve draft in Gate
draft = gate.submit_draft(ContentDraftCreate(
    title="Hydration Energy Hack",
    caption="The electrolyte secret high-performers use daily. #ad",
    content_type=ContentType.VIDEO_SHORT,
    target_platforms=["tiktok", "youtube_shorts", "instagram_reels"],
    is_promotional=True,
))
approved_draft = gate.approve(draft.request_id, reviewer="Maxim")

# 2. Publish via Postiz across target channels
pub_record = publisher.publish_draft(approved_draft)
print(f"Publication status: {pub_record.status.value}")

# 3. Later (24h/48h): Ingest social feedback metrics
metrics = SocialMetrics(
    publication_id=pub_record.publication_id,
    platform=DistributionPlatform.TIKTOK,
    post_id="tt_video_982734",
    views=54200,
    retention_rate_3s=0.74,
    retention_rate_15s=0.48,
    completion_rate=0.32,
    likes=4800,
    comments=310,
    shares=1250,
    saves=890,
)

# 4. RLSF Reward Computation & SCONES memory ingestion
feedback_report = rlsf.record_feedback(
    metrics=metrics,
    hook_type="curiosity_gap",
    preset_name="hormozi_bold",
    sync_to_scones=True,
)

print(f"Social Reward Score: {feedback_report.reward.overall_reward:.3f}")
print(f"Tier: {feedback_report.reward.performance_tier}")
for insight in feedback_report.distilled_insights:
    print(f"- {insight}")
```
