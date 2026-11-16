---
name: outlier-post-finder
description: Identify statistical outlier posts that exceed creator baseline engagement.
category: social-media
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/outlier-post-finder/SKILL.md"
# purpose: "Identify statistical outlier posts that exceed creator baseline engagement."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (ScrapeCreators Assimilated)"
# --- END DNK-MRH-HEADER ---

# Outlier Post Finder Skill

Find breakthrough viral posts that significantly outperform a creator's historical median/average baseline.

## When to Use
- Reverse-engineering viral topics, sound trends, and hook mechanics.
- Filtering out vanity accounts by calculating true multiplier over author baseline.
- Sourcing high-converting script formats for vertical video generation (Shorts/Reels/TikTok).

## Multiplier Standard
- **Baseline**: Average/median views across recent 30 posts.
- **Outlier Threshold**: Posts exceeding ≥ 2.5x the baseline.
- **Mega-Viral**: Posts exceeding ≥ 10.0x the baseline.

## Python Execution
```python
from services.dnk_content_intelligence.engine import ContentIntelligenceEngine
from services.dnk_content_intelligence.models import OutlierPostRequest, SocialPlatform

engine = ContentIntelligenceEngine()
res = engine.find_outliers(OutlierPostRequest(
    creator_handle_or_topic="ecom_growth",
    platform=SocialPlatform.TIKTOK,
    min_multiplier=2.5,
    limit=15
))

for item in res.items:
    print(f"{item.multiplier}x Outlier: {item.post_url} - {item.hook_text}")
```
