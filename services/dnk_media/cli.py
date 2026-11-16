# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/cli.py"
# purpose: "Standalone CLI for dnk_media Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import sys
import json
from services.dnk_media.src.service import (
    cut_silence,
    reframe_smart,
    generate_kinetic_subtitles,
    compose_sound_design,
    process_data,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m services.dnk_media.cli [subtitles|reframe|silence|sound|process] <args>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "subtitles":
        text = sys.argv[2] if len(sys.argv) > 2 else "Stop making this huge mistake right now"
        track = generate_kinetic_subtitles(text)
        print(f"Generated {track.words_count} kinetic words in {track.duration_ms}ms ({track.wpm} WPM)")
        print("\n--- SRT Preview ---")
        print("\n".join(track.srt_content.splitlines()[:12]))
    elif cmd == "reframe":
        plan = reframe_smart(1920, 1080, duration_ms=5000)
        print(f"Reframed 1920x1080 -> {plan.target_width}x{plan.target_height}")
        print(f"FFmpeg filter: {plan.ffmpeg_filter}")
    elif cmd == "silence":
        sample_words = [
            {"start_ms": 500, "end_ms": 1200, "word": "Hello"},
            {"start_ms": 2500, "end_ms": 3200, "word": "World"},
        ]
        plan = cut_silence(sample_words, total_duration_ms=4000)
        print(f"Saved {plan.saved_duration_ms}ms ({plan.retention_boost_estimate_pct}% retention boost)")
        print(f"Kept segments: {len(plan.keep_segments)}")
    elif cmd == "sound":
        plan = compose_sound_design(video_duration_s=15.0)
        print(f"Soundtrack preset: {plan.music_preset.title} | SFX Cues: {len(plan.sfx_timeline)}")
    else:
        query = sys.argv[2] if len(sys.argv) > 2 else "default"
        print(process_data(query))


if __name__ == "__main__":
    main()
