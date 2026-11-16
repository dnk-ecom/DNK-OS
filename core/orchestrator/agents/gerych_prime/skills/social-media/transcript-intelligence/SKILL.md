---
name: transcript-intelligence
description: Extract retention hooks and script formulas from video transcripts.
category: social-media
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/transcript-intelligence/SKILL.md"
# purpose: "Extract retention hooks and script formulas from video transcripts."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (ScrapeCreators Assimilated)"
# --- END DNK-MRH-HEADER ---

# Transcript Intelligence Skill

Analyze video audio transcripts to isolate 0-3 second retention hooks, pacing formulas, and persuasive script mechanics.

## When to Use
- Deconstructing viral Reels/Shorts to extract fill-in-the-blank script templates.
- Feeding word-anchored audio timelines into `dnk_video_ai_creator`.
- Identifying retention drop-off triggers and high-engagement language.

## Hook Taxonomy
- **Contrarian Stance**: "Everyone says X, but Y is the truth."
- **Negative Framing**: "Stop doing X if you want Y."
- **Curiosity Gap**: "This one tiny change did X."
- **Data Shock**: "We analyzed 1,000 stores and found X."

## Python Execution
```python
from services.dnk_content_intelligence.engine import ContentIntelligenceEngine
from services.dnk_content_intelligence.models import TranscriptIntelligenceRequest

engine = ContentIntelligenceEngine()
res = engine.analyze_transcript(TranscriptIntelligenceRequest(
    video_url="https://tiktok.com/@growth/video/10001",
    language="en"
))

for hook in res.atomic_hooks:
    print(f"[{hook.start_seconds}s - {hook.end_seconds}s] ({hook.hook_type}): {hook.text_snippet}")
```
