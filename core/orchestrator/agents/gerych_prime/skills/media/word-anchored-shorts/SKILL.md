---
name: word-anchored-shorts
description: "Generate 9:16 word-anchored kinetic typography Shorts using Remotion and FFmpeg with zero rendering costs."
---

# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/media/word-anchored-shorts/SKILL.md"
# purpose: "Operational Guide for synthesizing SOTA Word-Anchored 9:16 Shorts with Kinetic Typography inspired by hypit & AI-Youtube-Shorts-Generator"
# author: "DNK-e.com Maksym"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# --- END DNK-MRH-HEADER ---

# 🎬 Word-Anchored 9:16 Kinetic Shorts Synthesis

## Overview
Synthesize high-retention 9:16 vertical video compositions for TikTok, Reels, and YouTube Shorts using word-anchored micro-animations, dynamic karaoke highlight, and hook visual pacing inspired by `hypit` and `AI-Youtube-Shorts-Generator` at **$0 compute cost**.

## Core Kinetic Presets
1. **`hormozi_punch`**: High-contrast yellow (`#facc15`) & green (`#4ade80`), bold uppercase sans-serif with 4px black shadow stroke, 1.25x scale pop on active word.
2. **`beast_high_energy`**: Red (`#ef4444`) & amber (`#f59e0b`), rapid rhythm, animated top retention bar.
3. **`neon_cyber`**: Cyan (`#06b6d4`) & magenta (`#ec4899`), glowing shadow blur with translucent dark pill container.
4. **`minimal_editorial`**: Clean off-white (`#f8fafc`) typography with subtle animated underline highlight.

## Workflow

### 1. Direct Python Execution
```python
from services.dnk_video_ai_creator.word_anchored_timeline import (
    WordAnchoredTimelineEngine,
    KineticPreset
)

engine = WordAnchoredTimelineEngine()

# Option A: From text script
timeline = engine.from_text_script(
    script="STOP SCROLLING! This secret changes everything about automated ecommerce.",
    total_duration=12.0,
    preset=KineticPreset.HORMOZI_PUNCH
)

# Option B: Bridge from Phase 1 Content Intelligence Transcript Report
# timeline = engine.from_transcript_report(transcript_report, preset=KineticPreset.BEAST_HIGH_ENERGY)

# Export Remotion React TSX component (zero-cost headless rendering)
remotion_artifact = engine.export_remotion_tsx(
    timeline=timeline,
    bg_media="assets/ugc/product_background.mp4",
    username="@reburn_brand",
    cta_text="CLAIM OFFER IN BIO ➔"
)
print("Generated TSX:", remotion_artifact.entry_file)

# Export FFmpeg filter_complex command for instant 100% local rendering
ffmpeg_artifact = engine.export_ffmpeg_command(
    timeline=timeline,
    input_media="raw_camera_clip.mp4",
    output_media="final_reel_9x16.mp4"
)
print("FFmpeg command:", ffmpeg_artifact.command)
```

### 2. Swarm Parallel Dispatch
To dispatch via Gerych Swarm Coordinator:
```python
from core.orchestrator.swarm_coordinator import GerychSwarmCoordinator

coordinator = GerychSwarmCoordinator()

# Single Dispatch
result = coordinator.dispatch(
    agent="dnk_video_ai_creator",
    action="bridge_transcript_to_video",
    payload={
        "transcript_report": transcript_data,
        "preset": "hormozi_punch",
        "bg_media": "assets/ugc/clip1.mp4"
    }
)

# Parallel Batch with Research & Fullstack
batch_results = coordinator.dispatch_parallel([
    {
        "agent": "gerych_researcher",
        "action": "transcript_intelligence",
        "payload": {"video_url": "https://tiktok.com/@competitor/video/987"}
    },
    {
        "agent": "dnk_video_ai_creator",
        "action": "generate_remotion_tsx",
        "payload": {
            "script": "Stop wasting budget on broken ad sets. Watch this 10-second fix.",
            "preset": "beast_high_energy"
        }
    }
])
```

## Verification & Pitfalls
- **Audio drift prevention**: Word timestamps are absolute seconds from track start.
- **Hook pacing (0–3s)**: Always ensure the first 90 frames (at 30fps) contain hook zoom-punch to eliminate drop-off.
- **Line length constraint**: Phrases are automatically clamped to 3–5 words per frame group to prevent visual clutter on vertical screens.
