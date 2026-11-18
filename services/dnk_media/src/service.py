# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/src/service.py"
# purpose: "Unified In-RAM Facade for dnk_media Sovereign Brick"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from typing import List, Dict, Any, Optional
from services.dnk_media.src.silence_cutting import (
    SilenceCuttingEngine,
    SilenceCutPlan,
    silence_cutting_engine,
)
from services.dnk_media.src.smart_reframing import (
    SmartReframingEngine,
    SmartReframePlan,
    SpeakerTrackingPoint,
    smart_reframing_engine,
)
from services.dnk_media.src.kinetic_subtitles import (
    KineticSubtitlesEngine,
    KineticSubtitleTrack,
    kinetic_subtitles_engine,
)
from services.dnk_media.src.sound_design import (
    SoundDesignEngine,
    SoundDesignPlan,
    DuckingSettings,
    sound_design_engine,
)
from services.dnk_media.src.provenance import (
    ProvenanceEngine,
    provenance_engine,
)
from services.dnk_media.contracts.schemas import (
    ProvenanceSignRequest,
    ProvenanceSignResponse,
    ProvenanceVerifyRequest,
    ProvenanceVerifyResponse,
)


def cut_silence(
    words: List[Dict[str, Any]],
    total_duration_ms: int,
    min_silence_ms: Optional[int] = None,
    padding_ms: Optional[int] = None
) -> SilenceCutPlan:
    """Detects dead-air gaps and generates jump-cut interval plan."""
    return silence_cutting_engine.plan_silence_cuts_from_words(
        words=words,
        total_duration_ms=total_duration_ms,
        min_silence_ms=min_silence_ms,
        padding_ms=padding_ms
    )


def reframe_smart(
    original_width: int = 1920,
    original_height: int = 1080,
    tracking_points: Optional[List[SpeakerTrackingPoint]] = None,
    duration_ms: int = 5000
) -> SmartReframePlan:
    """Calculates 9:16 vertical crop with smooth speaker face centering."""
    return smart_reframing_engine.plan_reframe(
        original_width=original_width,
        original_height=original_height,
        tracking_points=tracking_points,
        duration_ms=duration_ms
    )


def generate_kinetic_subtitles(
    transcript: str,
    total_duration_ms: Optional[int] = None,
    style_preset: str = "hormozi_bold",
    words_per_phrase: int = 2
) -> KineticSubtitleTrack:
    """Aligns speech to word-level timestamps and exports ASS / SRT subtitles."""
    return kinetic_subtitles_engine.align_transcript(
        transcript=transcript,
        total_duration_ms=total_duration_ms,
        style_preset=style_preset,
        words_per_phrase=words_per_phrase
    )


def compose_sound_design(
    video_duration_s: float,
    speech_segments: Optional[List[Dict[str, Any]]] = None,
    hook_variant: Optional[Dict[str, Any]] = None,
    pattern_interrupts: Optional[List[Dict[str, Any]]] = None,
    custom_settings: Optional[DuckingSettings] = None
) -> SoundDesignPlan:
    """Composes audio ducking keyframes and synchronous SFX timeline."""
    return sound_design_engine.compose_soundtrack(
        video_duration_s=video_duration_s,
        speech_segments=speech_segments,
        hook_variant=hook_variant,
        pattern_interrupts=pattern_interrupts,
        custom_settings=custom_settings
    )


def process_data(query: str) -> str:
    """Generic fallback string processor for basic connectivity check."""
    return f"Processed: {query}"


def sign_provenance(
    image_path: str,
    author_name: str = "DNK-e.com",
    author_url: Optional[str] = "https://dnk-e.com",
    copyright_notice: Optional[str] = None,
    watermark_payload: Optional[str] = None,
    output_path: Optional[str] = None,
) -> ProvenanceSignResponse:
    """Signs media file with C2PA manifest & metadata steganography (DEC-143)."""
    req = ProvenanceSignRequest(
        image_path=image_path,
        author_name=author_name,
        author_url=author_url,
        copyright_notice=copyright_notice,
        watermark_payload=watermark_payload,
        output_path=output_path,
    )
    return provenance_engine.sign_asset(req)


def verify_provenance(
    image_path: str,
    expected_author: Optional[str] = None,
) -> ProvenanceVerifyResponse:
    """Verifies provenance, metadata chunks and manifest integrity (DEC-143)."""
    req = ProvenanceVerifyRequest(
        image_path=image_path,
        expected_author=expected_author,
    )
    return provenance_engine.verify_asset(req)


def compose_video_9_16(
    transcript: str,
    source_video_path: Optional[str] = None,
    duration_ms: Optional[int] = None,
    style_preset: str = "hormozi_bold",
    enable_silence_cut: bool = True,
    enable_smart_reframe: bool = True,
    enable_sound_design: bool = True,
    output_path: Optional[str] = None,
    dry_run: bool = True
) -> Any:
    """Harmonizes kinetic subtitles, smart reframing, dead-air cuts, and audio into 9:16 video."""
    from services.dnk_media.contracts.schemas import VideoCompositionRequest
    from services.dnk_media.src.composer import video_composer

    req = VideoCompositionRequest(
        transcript=transcript,
        source_video_path=source_video_path,
        duration_ms=duration_ms,
        style_preset=style_preset,
        enable_silence_cut=enable_silence_cut,
        enable_smart_reframe=enable_smart_reframe,
        enable_sound_design=enable_sound_design,
        output_path=output_path
    )
    return video_composer.compose(request=req, dry_run=dry_run)

