---
name: ad-library-teardown
description: Deconstruct active competitor ads from Meta, Google, and LinkedIn Ad Libraries.
category: social-media
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/ad-library-teardown/SKILL.md"
# purpose: "Deconstruct active competitor ads from Meta, Google, and LinkedIn Ad Libraries."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (ScrapeCreators Assimilated)"
# --- END DNK-MRH-HEADER ---

# Ad Library Teardown Skill

Perform competitive teardowns of active advertising campaigns across Meta Ad Library, Google Ads, and LinkedIn Ads.

## When to Use
- Auditing competitor ad strategies to find proven hooks and angles.
- Identifying evergreen winning ads (ads running for >30 days without pause).
- Extracting competitor offers, CTAs, landing page destinations, and risk-reversal guarantees.
- Planning creative iterations for `dnk_video_ai_creator` and Shopify product marketing.

## Core Metrics & Heuristics
- **Longevity Rule**: Ads running for more than 30 consecutive days are validated profit-drivers.
- **Hook Taxonomy**: Pain-first, curiosity gap, contrarian stance, or social proof.
- **Offer Structure**: Bundles, guarantees, free shipping thresholds, or trial models.

## Python Execution
```python
from services.dnk_content_intelligence.engine import ContentIntelligenceEngine
from services.dnk_content_intelligence.models import AdTeardownRequest

engine = ContentIntelligenceEngine()
res = engine.teardown_ad_library(AdTeardownRequest(
    brand_or_domain="Reburn",
    platforms=["facebook", "google", "linkedin"],
    limit=20
))

print(res.markdown_report)
```

## Swarm Dispatch (SwarmCoordinator)
```python
task = {
    "agent": "gerych_researcher",
    "action": "ad_library_teardown",
    "payload": {
        "brand": "Reburn",
        "platforms": ["facebook", "google"],
        "limit": 20
    }
}
```
