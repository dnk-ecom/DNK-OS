# --- DNK-MRH-HEADER ---
# mrh_id: "skills/media/video-retention-engineering/references/audio_ducking_and_sound_design.md"
# purpose: "Technical specifications, envelopes, and preset guide for Auto Sound Design & Audio Ducking"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (Gerych Prime)"
# --- END DNK-MRH-HEADER ---

# Audio Ducking Dynamics & Sound Design Architecture

## Multitrack Audio Structure
1. **Primary Voice Anchor (0 dB / Gain 1.0)**:
   - Voice-over or spoken dialogue is the anchor layer.
   - Speech energy must never be masked by music. Target Speech Clarity: >90%.
2. **Dynamic Background Music Bed (-16 dB to -4 dB)**:
   - Auto-ducked during active speech intervals.
   - Dynamic rebound during pauses (>400ms) to prevent cognitive dead zones and keep pacing alive.
3. **SFX Accent Layer (-1 dB / Gain 0.9)**:
   - Micro-audio triggers synchronized with 3s hooks and visual pattern interrupts.

## Recommended Envelope Settings

| Parameter | Recommended Value | Typical Range | Rationale |
| :--- | :--- | :--- | :--- |
| `ducking_depth_db` | `-16.0 dB` | `-24.0 .. -6.0 dB` | Sufficient attenuation to keep voice crystal clear without muting music completely. |
| `attack_ms` | `60 ms` | `20 .. 150 ms` | Quick drop so the first syllable isn't masked by loud music. |
| `release_ms` | `280 ms` | `100 .. 500 ms` | Smooth musical ramp up during natural pauses between thoughts. |
| `pause_threshold_ms` | `400 ms` | `300 .. 800 ms` | Minimum pause duration before music begins to rebound. |

## Music Preset Profiles

- **`electronic_pulse`** (128 BPM, Hi-Tech / Cyberpunk): Ideal for developer tools, SaaS demos, fast tutorials, tech reviews.
- **`lofi_chill`** (85 BPM, Lo-Fi Chill / Tutorial): Ideal for deep walk-throughs, coding tutorials, calm explainer reels.
- **`cinematic_suspense`** (95 BPM, Cinematic Mystery): Ideal for mystery hooks, shocking statistics, case study investigations.
- **`upbeat_commercial`** (120 BPM, Upbeat Commercial): Ideal for TikTok product showcases, e-commerce ads, lifehacks.
- **`trap_hype`** (140 BPM, Trap / Youth Trend): Ideal for streetwear, high-energy gaming, viral challenges.

## Sound Effect (SFX) Mapping

- **Hook Launch (0.0s)**: `sub_impact.mp3` or `bass_drop.mp3` (establishes gravity).
- **Zoom Punch (Stressed word)**: `whoosh_fast.mp3` (sharp air cut).
- **Key Insight / Stat Reveal**: `ding_accent.mp3` or `chime.mp3` (registers value delivery).
- **B-Roll Transition**: `glitch_rise.mp3` or `camera_shutter.mp3` (signals context switch).
