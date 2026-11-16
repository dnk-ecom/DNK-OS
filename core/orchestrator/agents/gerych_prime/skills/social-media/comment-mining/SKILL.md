---
name: comment-mining
description: Extract customer objections, pain points, and buying intent from social comments.
category: social-media
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/comment-mining/SKILL.md"
# purpose: "Extract customer objections, pain points, and buying intent from social comments."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (ScrapeCreators Assimilated)"
# --- END DNK-MRH-HEADER ---

# Comment Mining Skill

Extract high-signal customer intelligence from comments on TikTok, YouTube, Instagram, and Reddit posts.

## When to Use
- Researching customer objections before launching or optimizing a Shopify product page.
- Finding exact customer language and phrases for ad copy and landing page headlines.
- Generating FAQ sections and risk-reversal offers based on real customer hesitations.
- Discovering unmet product needs and feature requests from competitor audiences.

## Core Capabilities
- Linguistic analysis of raw comments across 11+ platforms.
- Automatic clustering into:
  - **Objections**: Friction points, trust issues, price resistance.
  - **Questions**: Confusion about usage, compatibility, or shipping.
  - **Buying Intent**: Urgency signals ("where to buy", "link in bio").
  - **Praise & Proof**: Specific outcomes praised by real users.

## Python Execution
```python
from services.dnk_content_intelligence.engine import ContentIntelligenceEngine
from services.dnk_content_intelligence.models import CommentMiningRequest

engine = ContentIntelligenceEngine()
report = engine.mine_comments(CommentMiningRequest(
    post_url="https://tiktok.com/@competitor/video/73918237192",
    max_comments=100
))

print(report.markdown_report)
```

## Swarm Dispatch (SwarmCoordinator)
```python
task = {
    "agent": "gerych_researcher",
    "action": "comment_mining",
    "payload": {
        "post_url": "https://tiktok.com/@competitor/video/73918237192",
        "max_comments": 100
    }
}
```
