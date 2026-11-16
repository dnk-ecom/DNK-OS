# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/src/sound_design.py"
# purpose: "Auto Sound Design, SFX timeline composition, and Voice-to-Background Audio Ducking Engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SpeechSegment(BaseModel):
    start_ms: int = Field(..., description="Start time in milliseconds")
    end_ms: int = Field(..., description="End time in milliseconds")
    text_snippet: Optional[str] = Field(None, description="Spoken text in this segment")


class VolumeKeyframe(BaseModel):
    time_ms: int = Field(..., description="Timestamp in milliseconds")
    volume: float = Field(..., ge=0.0, le=1.0, description="Target volume coefficient (0.0 to 1.0)")
    db_level: float = Field(..., description="Target level in dB")


class SFXPlacement(BaseModel):
    id: str
    time_s: float = Field(..., description="Timestamp in seconds")
    time_ms: int = Field(..., description="Timestamp in milliseconds")
    sfx_type: str = Field(..., description="SFX identifier, e.g. whoosh, ding, sub_impact, glitch")
    sfx_file: str = Field(..., description="Audio file reference or mock path")
    volume: float = Field(default=0.8, ge=0.0, le=1.0)
    pan: float = Field(default=0.0, ge=-1.0, le=1.0, description="Stereo panning: -1.0 Left to +1.0 Right")
    trigger_source: str = Field(..., description="hook, pattern_interrupt, punch_zoom, cta")
    label: str = Field(..., description="Human-readable title")


class MusicTrackPreset(BaseModel):
    preset_id: str
    title: str
    genre: str
    tempo_bpm: int
    mood: str
    base_volume: float = 0.75
    ducked_volume: float = 0.20
    preview_url: Optional[str] = None


class DuckingSettings(BaseModel):
    attack_ms: int = Field(default=60, description="Fade down duration upon speech onset")
    release_ms: int = Field(default=280, description="Fade up duration upon speech pause")
    ducking_depth_db: float = Field(default=-16.0, description="Attenuation during voice")
    normal_level_db: float = Field(default=-4.0, description="Level during voice pause")
    music_preset: str = Field(default="electronic_pulse", description="Ambient genre preset")
    master_voice_gain: float = Field(default=1.0, ge=0.0, le=2.0)
    master_music_gain: float = Field(default=0.8, ge=0.0, le=2.0)
    master_sfx_gain: float = Field(default=0.9, ge=0.0, le=2.0)


class SoundDesignPlan(BaseModel):
    video_duration_s: float
    music_preset: MusicTrackPreset
    ducking_settings: DuckingSettings
    speech_segments: List[SpeechSegment]
    ducking_keyframes: List[VolumeKeyframe]
    sfx_timeline: List[SFXPlacement]
    speech_clarity_score: float = Field(..., description="Predicted voice intelligibility (0-100%)")
    total_ducking_points: int
    audio_energy_score: float = Field(..., description="Audio dynamism and engagement score (0-100%)")
    production_mix_notes: List[str]


MUSIC_PRESETS: Dict[str, MusicTrackPreset] = {
    "electronic_pulse": MusicTrackPreset(
        preset_id="electronic_pulse",
        title="Cyber Pulse (128 BPM)",
        genre="Synthwave / EDM",
        tempo_bpm=128,
        mood="Energetic, Hi-Tech, High Retention",
        base_volume=0.75,
        ducked_volume=0.18,
    ),
    "lofi_chill": MusicTrackPreset(
        preset_id="lofi_chill",
        title="Focus Café (85 BPM)",
        genre="Lo-Fi Chillhop",
        tempo_bpm=85,
        mood="Relaxed, Intimate, Educational",
        base_volume=0.70,
        ducked_volume=0.22,
    ),
    "cinematic_suspense": MusicTrackPreset(
        preset_id="cinematic_suspense",
        title="Shadow Riser (105 BPM)",
        genre="Cinematic Trailer",
        tempo_bpm=105,
        mood="Mysterious, Curiosity-Gap, Dramatic",
        base_volume=0.80,
        ducked_volume=0.15,
    ),
    "upbeat_commercial": MusicTrackPreset(
        preset_id="upbeat_commercial",
        title="Modern Groove (120 BPM)",
        genre="Funk Pop",
        tempo_bpm=120,
        mood="Optimistic, E-commerce, Friendly",
        base_volume=0.75,
        ducked_volume=0.20,
    ),
    "trap_hype": MusicTrackPreset(
        preset_id="trap_hype",
        title="Bass Rush (140 BPM)",
        genre="Urban Trap",
        tempo_bpm=140,
        mood="Aggressive, Viral Hooks, Bold",
        base_volume=0.85,
        ducked_volume=0.16,
    ),
}


class SoundDesignEngine:
    """
    Auto Sound Design and Voice-to-Background Audio Ducking Engine.
    Computes smooth volume keyframes for background music (ducking) and
    places synchronous SFX accents across the timeline.
    """

    def __init__(self):
        pass

    def compose_soundtrack(
        self,
        video_duration_s: float,
        speech_segments: Optional[List[Dict[str, Any]]] = None,
        hook_variant: Optional[Dict[str, Any]] = None,
        pattern_interrupts: Optional[List[Dict[str, Any]]] = None,
        custom_settings: Optional[DuckingSettings] = None
    ) -> SoundDesignPlan:
        settings = custom_settings or DuckingSettings()
        preset = MUSIC_PRESETS.get(settings.music_preset, MUSIC_PRESETS["electronic_pulse"])

        speech_segs: List[SpeechSegment] = []
        if speech_segments:
            for seg in speech_segments:
                speech_segs.append(
                    SpeechSegment(
                        start_ms=int(seg.get("start_ms", seg.get("start", 0) * 1000)),
                        end_ms=int(seg.get("end_ms", seg.get("end", 0) * 1000)),
                        text_snippet=seg.get("text", "")
                    )
                )

        keyframes: List[VolumeKeyframe] = []
        normal_vol = max(0.0, min(1.0, 10 ** (settings.normal_level_db / 20.0)))
        ducked_vol = max(0.0, min(1.0, 10 ** (settings.ducking_depth_db / 20.0)))

        video_ms = int(video_duration_s * 1000)

        # Baseline start
        keyframes.append(VolumeKeyframe(time_ms=0, volume=normal_vol, db_level=settings.normal_level_db))

        for seg in speech_segs:
            att_start = max(0, seg.start_ms - settings.attack_ms)
            keyframes.append(VolumeKeyframe(time_ms=att_start, volume=normal_vol, db_level=settings.normal_level_db))
            keyframes.append(VolumeKeyframe(time_ms=seg.start_ms, volume=ducked_vol, db_level=settings.ducking_depth_db))
            keyframes.append(VolumeKeyframe(time_ms=seg.end_ms, volume=ducked_vol, db_level=settings.ducking_depth_db))

            rel_end = min(video_ms, seg.end_ms + settings.release_ms)
            keyframes.append(VolumeKeyframe(time_ms=rel_end, volume=normal_vol, db_level=settings.normal_level_db))

        keyframes.append(VolumeKeyframe(time_ms=video_ms, volume=normal_vol, db_level=settings.normal_level_db))

        sorted_keyframes = sorted(keyframes, key=lambda k: k.time_ms)
        unique_keyframes: List[VolumeKeyframe] = []
        last_t = -1
        for kf in sorted_keyframes:
            if kf.time_ms != last_t:
                unique_keyframes.append(kf)
                last_t = kf.time_ms

        sfx_list: List[SFXPlacement] = []
        sfx_idx = 1

        hook_sfx = "whoosh_impact.mp3"
        hook_label = "3-Second Hook Audio Impact"
        if hook_variant:
            rec_sfx = hook_variant.get("recommended_sfx", "whoosh_fast.mp3")
            hook_sfx = rec_sfx
            hook_label = f"Hook Impact ({hook_variant.get('title', 'Intro')})"

        sfx_list.append(SFXPlacement(
            id=f"sfx_{sfx_idx}",
            time_s=0.15,
            time_ms=150,
            sfx_type="sub_impact",
            sfx_file=hook_sfx,
            volume=0.9 * settings.master_sfx_gain,
            pan=0.0,
            trigger_source="hook",
            label=hook_label
        ))
        sfx_idx += 1

        if pattern_interrupts:
            for item in pattern_interrupts:
                t_sec = float(item.get("timestamp_s", item.get("time_s", 0.0)))
                if t_sec < 0.6:
                    continue
                itype = item.get("interrupt_type", "whoosh")
                audio_cue = item.get("audio_cue", f"{itype}.mp3")
                sfx_list.append(SFXPlacement(
                    id=f"sfx_{sfx_idx}",
                    time_s=round(t_sec, 2),
                    time_ms=int(t_sec * 1000),
                    sfx_type=itype,
                    sfx_file=audio_cue,
                    volume=0.75 * settings.master_sfx_gain,
                    pan=0.1 if sfx_idx % 2 == 0 else -0.1,
                    trigger_source="pattern_interrupt",
                    label=item.get("action_label", f"Pattern Interrupt: {itype}")
                ))
                sfx_idx += 1

        if len(sfx_list) == 1 and video_duration_s >= 6.0:
            default_cadence = [
                (2.8, "whoosh", "whoosh_soft.mp3", "Attention Reset Whoosh"),
                (5.5, "ding", "bell_ding.mp3", "Key Takeaway Chime"),
            ]
            if video_duration_s >= 10.0:
                default_cadence.append((8.5, "glitch", "glitch_short.mp3", "Visual Transition Glitch"))

            for ts, stype, sfile, slabel in default_cadence:
                if ts < video_duration_s - 0.5:
                    sfx_list.append(SFXPlacement(
                        id=f"sfx_{sfx_idx}",
                        time_s=ts,
                        time_ms=int(ts * 1000),
                        sfx_type=stype,
                        sfx_file=sfile,
                        volume=0.70 * settings.master_sfx_gain,
                        pan=0.0,
                        trigger_source="cadence",
                        label=slabel
                    ))
                    sfx_idx += 1

        speech_clarity_score = 94.5 if settings.ducking_depth_db <= -14.0 else 86.0
        audio_energy_score = min(98.0, 75.0 + len(sfx_list) * 4.0)

        mix_notes = [
            f"Active ambient preset '{preset.title}' at -4dB baseline.",
            f"Auto-ducked to {settings.ducking_depth_db}dB across {len(speech_segs)} speech phrases.",
            f"Dynamic attack ({settings.attack_ms}ms) and release ({settings.release_ms}ms) prevent pumping artifacts.",
            f"Arranged {len(sfx_list)} synchronized SFX cues for cognitive retention reinforcement."
        ]

        return SoundDesignPlan(
            video_duration_s=video_duration_s,
            music_preset=preset,
            ducking_settings=settings,
            speech_segments=speech_segs,
            ducking_keyframes=unique_keyframes,
            sfx_timeline=sfx_list,
            speech_clarity_score=speech_clarity_score,
            total_ducking_points=len(unique_keyframes),
            audio_energy_score=audio_energy_score,
            production_mix_notes=mix_notes
        )


sound_design_engine = SoundDesignEngine()
