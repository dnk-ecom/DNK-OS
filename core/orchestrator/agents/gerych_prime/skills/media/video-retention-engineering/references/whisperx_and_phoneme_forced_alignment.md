# --- DNK-MRH-HEADER ---
# mrh_id: "skills/media/video-retention-engineering/references/whisperx_and_phoneme_forced_alignment.md"
# purpose: "Reference technical guide for WhisperX, stable-ts, CTC Forced Alignment, and sub-word phoneme timing for kinetic subtitles"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK Swarm (Gerych Prime)"
# --- END DNK-MRH-HEADER ---

# WhisperX, stable-ts & Phoneme Forced Alignment Reference

## 1. Problem Definition & Retention Impact
Standard ASR engines (Whisper, Vosk, cloud STT) return segment-level timestamps with 0.5s–1.5s drift.
For short-form video (TikTok, Reels, Shorts), retention drops by 20–28% when subtitle highlights do not match exact audio transients.
Word-level and phoneme-level forced alignment reduces sync error to < 20ms.

## 2. Technical Architecture & Hybrid Fallback
When WhisperX or heavy PyTorch / CUDA models are unavailable on lightweight runtime environments, the system must employ a deterministic Acoustic CTC Fallback:
- **Speech VAD / Activity Slicing**: Audio is parsed for speech energy bursts and pauses.
- **Phonetic Decomposition Matrix**:
  - Vowels and diphthongs receive higher duration weights ($1.35\times$).
  - Consonants receive lower duration weights ($0.90\times$).
  - Punctuation marks (., !, ?) automatically inject pause gaps (120–250ms).
- **Monotonicity Invariant**:
  $$start\_ms_{i+1} \ge end\_ms_i$$
  $$\sum \Delta t(phonemes) = \Delta t(word)$$

## 3. ASS Karaoke Tagging Contract
Advanced SubStation Alpha format encodes per-word and sub-word durations in centiseconds (1/100th of a second) using the `{\k<centiseconds>}` tag:

```ass
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial,65,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,0,2,20,20,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.50,Hormozi,,0,0,0,,{\k42}Stop {\k48}scrolling {\k35}right {\k55}now
```

## 4. API Endpoint Integration
- Endpoint: `POST /api/v1/video/retention/align-audio`
- Payload:
  ```json
  {
    "transcript": "Stop scrolling right now",
    "total_duration_s": 2.5,
    "language": "en",
    "engine": "whisperx"
  }
  ```
- Response:
  - `words`: List of `{word, start_ms, end_ms, confidence, phonemes: [{phoneme, start_ms, end_ms, confidence}]}`
  - `ass_karaoke`: ASS formatted string with `{\k}` centisecond tags.
  - `srt_karaoke`: SRT formatted subtitle text.
