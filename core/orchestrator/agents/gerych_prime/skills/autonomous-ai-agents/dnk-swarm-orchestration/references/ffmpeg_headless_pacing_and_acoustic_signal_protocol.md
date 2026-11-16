# --- DNK-MRH-HEADER ---
# mrh_id: "references/ffmpeg_headless_pacing_and_acoustic_signal_protocol.md"
# purpose: "Protocol & Reference for Headless FFmpeg Scene Detection, Pacing Scorer, and Acoustic Signals."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🎬 Headless FFmpeg Visual Pacing & Prosody Acoustic Signal Protocol

This protocol standardizes the deterministic signal extraction pipeline for video retention analysis in DNK OS.

---

## 1. Headless C-Level FFmpeg Command Patterns

### A. Scene Cut Detection
Extract frame cut timestamps without decoding complete video streams to disk:
```bash
ffmpeg -hide_banner -nostats -i <video_path> -filter:v "select='gt(scene,0.3)',showinfo" -f null -
```
- **Parsing**: Scan stderr for `pts_time:(\d+\.?\d*)`.
- **Deduplication**: Filter out duplicate cut timestamps occurring within `< 0.1s`.

### B. Silence & Dead Air Detection
Extract pause boundaries and durations:
```bash
ffmpeg -hide_banner -nostats -i <media_path> -af "silencedetect=noise=-35dB:d=0.35" -f null -
```
- **Parsing**: Match `silence_start: (\d+\.?\d*)` and `silence_end: (\d+\.?\d*) \| silence_duration: (\d+\.?\d*)`.

### C. Volume & RMS Dynamics
Calculate energy distribution:
```bash
ffmpeg -hide_banner -nostats -i <media_path> -af "volumedetect" -f null -
```
- **Parsing**: Match `mean_volume: ([-0-9.]+) dB` and `max_volume: ([-0-9.]+) dB`.

---

## 2. Retention Pacing & Non-Linear Static Hold Penalties

A linear penalty for scene hold duration underestimates viewer churn. Retention drop-off increases exponentially when a single shot exceeds the human attention span threshold.

### Standards & Thresholds:
- **Optimal Scene Duration**: 1.5s – 3.2s.
- **Static Hold Threshold**: `> 3.5s` flags `is_static_hold_risk = True`.
- **Severity Tiers**:
  - `3.5s - 5.0s`: `MEDIUM` risk (-12 pts).
  - `5.0s - 7.0s`: `HIGH` risk (-20 pts).
  - `> 7.0s`: `CRITICAL` risk (-27 pts). Viewer drop-off rate reaches 30–50%.
- **Actionable Remediation**:
  - Always pair every detected static hold with concrete video editing instructions:
    *"Insert 1.2x punch-in zoom, b-roll footage, motion graphics, or pattern interrupt."*

---

## 3. Acoustic & Prosody Retention Rules

- **Zero-Latency Hook Rule**: Speech start latency must be `≤ 0.2s`. Any silence `> 0.2s` at the start of a short-form video results in immediate hook abandonment.
- **Pacing Cadence (WPM)**:
  - Fast/Engaging: 165 – 195 WPM.
  - Slow/Drifting: < 140 WPM (triggers pacing penalty).
- **Acoustic Energy Delta**:
  - `rms_energy_delta_db = hook_rms_db - mean_rms_db`.
  - A positive delta (+2dB to +5dB) in the first 3 seconds signals authority and command of audience attention.

---

## 4. Deterministic Synthetic Media Testing in CI/CD

To test FFmpeg pipelines without committing binary media files to git repositories, generate deterministic synthetic test media in pytest:

```python
test_media = tmp_path / "test_synth.wav"
cmd = [
    ffmpeg_bin,
    "-y",
    "-f", "lavfi",
    "-i", "sine=frequency=1000:duration=2",
    "-af", "volume=enable='between(t,0,0.5)':volume=0",
    str(test_media),
]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
```
Generates 0.5s of dead air followed by 1.5s of audio tone, allowing deterministic verification of silence detection and speech start latency.
