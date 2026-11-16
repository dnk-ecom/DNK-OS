---
name: video-retention-engineering
description: Use when optimizing video retention, hooks, or captions.
category: media
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/media/video-retention-engineering/SKILL.md"
# purpose: "Class-level operational guidelines for video retention optimization, kinetic typography, pattern interrupts, and 3-second hook split-testing"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (Gerych Prime)"
# --- END DNK-MRH-HEADER ---

# Video Retention Engineering

Comprehensive playbook for diagnosing, boosting, and engineering audience retention in short-form and long-form video pipelines (TikTok, Instagram Reels, YouTube Shorts).

## When to Use
- Implementing or tuning 0–3 second hook variations (Loss Aversion, Curiosity Gap, Shocking Stat, Direct Benefit, Contrarian Stance).
- Building or updating kinetic word-level subtitle engines (Hormozi Punch, Minimal Clean, Cyberpunk Neon).
- Engineering Pattern Interrupt schedulers: detecting dead zones (>2.5s monotone speech), applying punch zooms (1.15x–1.25x), and scheduling B-roll cutaways.
- Designing and automating multitrack audio envelopes: voice-prioritized dynamic ducking (-16 dB), ambient background presets, and synchronized SFX placement.
- Connecting retention audit nodes to video synthesis nodes in DNK Canvas or Remotion render pipelines.

## Supporting References
- Deterministic video culling, mathematical quality scoring & open-source tools: `references/deterministic_video_culling_and_selects.md`
- SOTA Video understanding, montage & video knowledge graph repositories: `references/sota_video_understanding_montage_and_kg_repos.md`
- CapCut Desktop project reverse-engineering & Gemini Vision action cuts: `references/capcut_draft_reverse_engineering_and_action_cuts.md`
- Detailed hook formulas and retention metrics: `references/hook_retention_formulas.md`
- Frame 0 hard attack audio trim & dynamic punch-in zoom protocol: `references/frame_0_audio_latency_and_punch_in_zoom.md`
- Audio ducking dynamics, presets, and envelope parameters: `references/audio_ducking_and_sound_design.md`
- Neuro-retention mathematical model and attention scoring: `references/neuro_retention_and_attention_simulation.md`
- WhisperX, stable-ts & Phoneme Forced Alignment: `references/whisperx_and_phoneme_forced_alignment.md`

## Retention Optimization Pillars

### 1. 3-Second Hook Architecture
The first 90 frames (at 30fps) determine whether the platform algorithm flags the video as engaging or skippable:
- **Negative Frame (Loss Aversion)**: Focus on what the viewer stands to lose. Generates highest 3s hold (~84-88%).
- **Curiosity Gap**: Open an unresolvable cognitive loop in sentence one (~81-85%).
- **Shocking Stat**: Concrete numerical proof to establish instant authority (~78-82%).
- **Direct Benefit**: Frictionless promise for immediate problem solving (~76-80%).
- **Contrarian Stance**: Attack a widely accepted myth or common practice (~82-86%).
- **Extreme Status / Environmental Juxtaposition**: Visual or conceptual paradox (e.g. billionaire in street food RV, high-tech rig in ruins) (~85-91%).
- **Authority / Brand Anchor**: Frame 0 anchor to high-recognition brand or figure to eliminate unfamiliarity friction (~80-84%).
- **Frame 0 Zero-Water Invariant**: Never open with greetings ("Hi guys", "Welcome back", "Today we discuss") or empty landscape. Speaker face or hero object must be centered at t=0.0s, delivering the trigger word within the first 3 words.

### 2. Anti-Monotony & Pattern Interrupts
- **Dead Zone Threshold**: Speech or static camera footage lasting >2.8–3.2s without audio-visual change triggers attention drop.
- **Punch Zooms**: Scale container to 1.15x–1.25x for 0.4–0.8s on stressed words or hook punchlines.
- **B-Roll Cutaways**: Swap primary speaker feed for 1.2–2.0s with contextual stock footage, screen recording, or motion graphics.
- **Audio Anchors**: Pair every visual cutaway with micro-SFX (`whoosh_fast.mp3`, `sub_impact.mp3`, `ding_accent.mp3`).

### 3. Word-Level Kinetic Subtitles & Phoneme Forced Alignment
- Maximum 3–5 words per screen to avoid cognitive overload on mobile viewports.
- Active word scale pop (1.2x) with high-contrast highlight colors (`#facc15`, `#4ade80`, `#06b6d4`).
- **Sub-word & Phoneme Forced Alignment**: WhisperX / CTC alignment producing millisecond precision (`start_ms`, `end_ms`, `phonemes`).
- **Karaoke ASS Tagging**: Export ASS files with per-word centisecond karaoke tags (`{\k45}`) for seamless sync with Alex Hormozi style video pacing.
- Reference implementation: `services/media/forced_alignment_service.py`.

### 4. Auto Sound Design & Dynamic Audio Ducking
- **Multitrack Hierarchy**: Primary Voice Anchor (0 dB) > Ambient Background Bed (Auto-Ducked to -16 dB) > SFX Layer (-1 dB).
- **Attack & Release Envelopes**: Attack = 60ms (fast dip on speech onset), Release = 280ms (smooth rebound during pauses > 400ms).
- **Speech Clarity Gate**: Target >90% clarity to prevent cognitive fatigue and premature swipe-aways.
- **Micro-SFX Synchronization**: Auto-map `sub_impact.mp3` to hook drop (0.0s), `whoosh_fast.mp3` to punch zooms, and `ding_accent.mp3` to core value propositions.

### 5. Neuro-Retention Heatmap & Attention Simulator
- **Hazard Rate Modeling**: Simulates instantaneous viewer drop-off $h(t)$ along the timeline based on cognitive fatigue vs active stimuli.
- **Synergistic Multiplier Effects**: Validated hook reduces early hazard by 55%, pattern interrupts by 60%, captions by 35%, and sound ducking by 30%.
- **Second-by-Second Attention Classification**:
  - Green (>75%): Peak Focus / Safe Retention zone.
  - Yellow (55–75%): Pacing fatigue zone.
  - Red (<55% or hazard > 0.12): Danger Drop-off Zone (requires immediate pacing intervention).
- **Composite Metrics**: 3s Retention %, Predicted Completion Rate %, Retention Lift %, Neuro Score, and Viral Index (0–100).

## Standard Execution Workflow

### Step 1: Hook Generation & Split-Testing
```python
from services.dnk_media.hook_variant_generator_service import HookVariantGeneratorEngine, HookGenerationRequest

engine = HookVariantGeneratorEngine()
response = engine.generate_variants(HookGenerationRequest(
    core_topic="Shopify Store Speed Optimization",
    target_audience="E-commerce founders",
    original_hook="Here is how to speed up your website."
))

# Best predicted retention hook
winning_hook = next(v for v in response.variants if v.variant_id == response.recommended_winning_variant_id)
print(f"Winner ({winning_hook.predicted_3s_retention_pct}% Hold): {winning_hook.script_text}")
```

### Step 2: Pattern Interrupt Schedule Generation
```python
from services.dnk_media.pattern_interrupt_service import PatternInterruptEngine, PatternInterruptRequest

engine = PatternInterruptEngine()
plan = engine.generate_interrupt_plan(PatternInterruptRequest(
    script_or_transcript="Your full video transcript text here...",
    total_duration_sec=30.0,
    target_pacing_interval_sec=3.0
))

print(f"Scheduled {plan.interrupts_count} interrupts. Boost: +{plan.retention_boost_estimate_pct}%")
```

### Step 3: Sound Design & Dynamic Audio Ducking Plan
```python
from services.dnk_media.sound_design_engine_service import SoundDesignEngine, SoundDesignRequest

sound_engine = SoundDesignEngine()
sound_plan = sound_engine.generate_sound_plan(SoundDesignRequest(
    total_duration_sec=30.0,
    script_text="Your full video transcript text here...",
    music_preset_id="electronic_pulse",
    ducking_depth_db=-16.0,
    attack_ms=60,
    release_ms=280,
    hook_variant=winning_hook.model_dump(),
    pattern_interrupt_plan=plan.model_dump()
))

print(f"Speech Clarity: {sound_plan.speech_clarity_score_pct}%, SFX Cues: {len(sound_plan.sfx_timeline)}")
```

### Step 4: Neuro-Retention Heatmap Simulation
```python
from services.dnk_media.neuro_retention_service import NeuroRetentionEngine, NeuroRetentionSimulationRequest

neuro_engine = NeuroRetentionEngine()
sim_result = neuro_engine.simulate_retention(NeuroRetentionSimulationRequest(
    video_duration_s=30.0,
    transcript_text="Your full video transcript text here...",
    active_hook=winning_hook.model_dump(),
    pattern_interrupts=plan.interrupts,
    sound_design_plan=sound_plan.model_dump(),
    kinetic_captions={"animation_preset": "hormozi_bold"}
))

print(f"3s Hold: {sim_result.predicted_retention_3s_pct}% (Lift: +{sim_result.retention_lift_pct}%), Neuro Score: {sim_result.neuro_engagement_score}")
```

### Step 5: Canvas Node Data Propagation
In DNK Canvas architecture, downstream nodes consume retention metadata through `propagateDataFlow`:
```typescript
// Inside RetentionAuditorNode
propagateDataFlow(id, {
  hook_variants: hooksData,
  selected_hook_variant: winningVariant,
  pattern_interrupts: interruptPlan,
  sound_design_plan: soundPlan,
  neuro_simulation: simResult,
});
```

Downstream `VideoCreatorNode` subscribes via `inputContext` and activates:
- Dynamic CSS container zoom on `zoom_punch` timecodes (`transform: scale(...)`).
- Live B-Roll overlay triggers on `broll_cutaway`.
- Quick-switcher tabs for A/B split-testing.
- Audio Mixer displaying multitrack levels, dynamic ducking status (`-16 dB` ducked vs `-4 dB` rebound), and live SFX popups.
- Interactive Heatmap Scrubber Bar directly above the timeline with click-to-seek and second-by-second attention coloring.
- Real-Time Neuro Attention HUD in the video viewport (`🧠 Attn: 94% • Peak Focus ⚡`).

## Common Pitfalls
1. **Over-interruption fatigue**: Triggering pattern interrupts more frequently than every 2.0s causes disorientation. Target 2.8s–3.5s cadence.
2. **Audio-visual desynchronization**: Zoom punches must snap precisely on the transient peak of the stressed word, not after it.
3. **Subtitles overlapping bottom UI**: On TikTok/Reels, keep bottom 20% safe zone clear for platform UI elements (captions, audio title, profile link).
4. **Harsh Audio Ducking ('Pumping')**: Setting release under 100ms creates an annoying volume oscillation. Keep release between 250ms–350ms for natural speech cadences.
5. **Speech Masking by High-BPM Tracks**: High-frequency synth leads in background tracks can clash with 2–4kHz speech harmonics. Always enforce minimum -16 dB ducking depth during dialogue.
6. **Corporate Greeting 'Water' in Frame 0**: Polite openers ("Hello everyone", "Welcome back", "Today we...") leak retention instantly. Apply a strict -35% hook penalty for opening fluff.
7. **Monolithic Content Creation Bottleneck**: Forcing a single agent or creator to cover script, filming, rough edit, motion graphics, and QA. Decouple into discrete roles (Source -> Rough Editor -> Producer -> Motion -> Multi-Persona Focus Group).
8. **Blind Pre-Release without Consensus Audit**: Releasing high-budget cuts without focus group simulation; always filter out isolated subjective complaints and fix only overlapping consensus drop-off points.
9. **Pre-Speech Dead Air (Frame 0 Audio Latency)**: Allowing >0.15s of silence before the speaker's first word spikes immediate swipe-away. Always apply hard attack trim (`ClipFactory.apply_hard_attack_trim`, `max_lead_sec <= 0.10s`) to snap audio attack to Frame 0.
10. **Delayed Pattern Interrupt (The 1-Second Adaptation Trap)**: Viewers form a swipe decision between 0.8s and 1.2s. Failing to deploy a punch-in zoom pulse (1.20x scale pulse at 0.8s–1.4s) forfeits the viewer's subconscious commitment to watch beyond the hook.
11. **CapCut In-Memory RAM Overwrite & Multi-Tier Desync**: Editing `draft_info.json` while CapCut Desktop is running results in CapCut silently overwriting changes upon exit. Furthermore, modern CapCut Pro uses `Timelines/<UUID>/draft_info.json`, `template.json`, and transaction cache `attachment/patch/mini_draft.json`. Never modify files with active CapCut processes, never create unregistered clone folders (causes "Cannot open this project"), and always sync internal `Timelines/` while clearing `attachment/patch`. (See `references/capcut_draft_reverse_engineering_and_action_cuts.md`).
12. **CapCut Text Overlay Clutter vs Native Timeline Markers (`time_marks`)**: Do not dump scene action descriptions as text clips (`materials.texts`) directly onto video layers unless explicitly requested as viewer captions. Users want scene and action cues as native timeline ruler markers (`time_marks.mark_items` with hex colors and titles) to keep the video viewport clean while providing navigation landmarks on the time axis.

## Verification
- Core Media & Pipeline tests: `pytest tests/media/ -v` (covers `test_shorts_pipeline.py`, `test_end_to_end_pipeline.py`, dynamic zoom keyframes, hard attack trim, and trigger subtitles)
- Retention Auditor tests: `pytest services/dnk_video_retention_auditor/tests/ -v` (covers hook scoring, anti-water filter penalties, surgical EDL)
- End-to-end CLI generation: `python3 scripts/media/process_raw_video.py --input "<script_or_quote>" --media-id "<id>" --top-k 1 --output-dir "artifacts/shorts" --no-canvas-sync`
- Backend API tests: `.venv/bin/pytest apps/api/tests/test_video_retention_router.py apps/api/tests/test_forced_alignment.py apps/api/tests/test_video_export_engine.py -v`
- Frontend type safety: `npx --prefix apps/web tsc --project apps/web/tsconfig.json --noEmit`
