# Frame 0 Audio Latency Elimination & Dynamic Punch-In Zoom Protocol

## 1. Frame 0 Hard Attack Trim
In short-form retention engineering, viewers decide whether to swipe within the first 0.3s–0.5s. If there is dead air (>0.15s) between the video start and the speaker's first word, drop-off spikes by up to 25%.

### Protocol:
- **Max Lead Latency**: 0.10s (<=100ms).
- **Implementation**: `ClipFactory.apply_hard_attack_trim(candidate, max_lead_sec=0.10)`
- Snaps candidate start time directly to `first_word_start - max_lead_sec`, eliminating pre-speech pause.
- Automatically adjusts candidate duration and shifts all subtitle word timestamps so audio, video, and text remain strictly aligned.

## 2. Dynamic Punch-In Zoom (0.8s – 1.4s)
Subconscious pattern adaptation happens between 0.8s and 1.2s. A subtle 1.20x zoom pulse breaks visual monotony right before the viewer's thumb initiates a scroll.

### Protocol:
- **Time Window**: 0.8s to 1.4s (peak at ~1.1s).
- **Scale Range**: Base 1.00x -> Peak 1.20x -> Return 1.00x.
- **Easing**: `EasingType.EASE_OUT` on rise, `EasingType.EASE_IN` on recovery.
- **Implementation**: Generates `Keyframe` timeline on background video track in `ShortsPipeline.generate_shorts_composition(..., punch_in_zoom=True, punch_in_scale=1.20)`.

## 3. Kinetic Trigger Word Highlighting
- Scanning word tokens against high-impact hook dictionaries (`HOOK_POWER_WORDS_UK`, `HOOK_POWER_WORDS_EN`).
- Triggers: *stop, never, hack, secret, viral, гроші, бізнес, помилка, фатальна*.
- Highlighting: High-contrast yellow (`#fef08a`), 52px font size, and 4px shadow stroke.
