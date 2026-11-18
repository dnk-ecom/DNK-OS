# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/contracts/schemas.py"
# purpose: "Strict Pydantic v2 schemas for dnk_media sovereign brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from services.dnk_media.src.silence_cutting import SilenceCutPlan
from services.dnk_media.src.smart_reframing import SmartReframePlan, SpeakerTrackingPoint
from services.dnk_media.src.kinetic_subtitles import KineticSubtitleTrack
from services.dnk_media.src.sound_design import SoundDesignPlan, DuckingSettings


class ServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    query: str


class ServiceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    result: str


class SilenceCutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    words: List[Dict[str, Any]] = Field(..., description="List of dicts with start_ms, end_ms, word")
    total_duration_ms: int = Field(..., gt=0, description="Total video duration in ms")
    min_silence_ms: Optional[int] = Field(default=400, ge=100, description="Minimum silence gap to cut")
    padding_ms: Optional[int] = Field(default=70, ge=0, description="Safety padding around speech")


class SilenceCutResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    plan: SilenceCutPlan


class SmartReframeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    original_width: int = Field(default=1920, gt=0)
    original_height: int = Field(default=1080, gt=0)
    duration_ms: int = Field(default=5000, gt=0)
    tracking_points: Optional[List[SpeakerTrackingPoint]] = None


class SmartReframeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    plan: SmartReframePlan


class KineticSubtitlesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    transcript: str = Field(..., min_length=1, description="Spoken speech transcript")
    total_duration_ms: Optional[int] = Field(default=None, description="Audio duration in ms")
    style_preset: str = Field(default="hormozi_bold", description="hormozi_bold | minimal_clean | cyberpunk_neon")
    words_per_phrase: int = Field(default=2, ge=1, le=5)


class KineticSubtitlesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    track: KineticSubtitleTrack


class SoundDesignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    video_duration_s: float = Field(..., gt=0.0)
    speech_segments: Optional[List[Dict[str, Any]]] = None
    hook_variant: Optional[Dict[str, Any]] = None
    pattern_interrupts: Optional[List[Dict[str, Any]]] = None
    custom_settings: Optional[DuckingSettings] = None


class SoundDesignResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    plan: SoundDesignPlan


class ProvenanceSignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    image_path: str = Field(..., description="Path to media file")
    author_name: str = Field(default="DNK-e.com", description="Creator/Author identity")
    author_url: Optional[str] = Field(default="https://dnk-e.com", description="Author web portfolio or URI")
    copyright_notice: Optional[str] = Field(default="Copyright (c) 2026 DNK-e.com. All rights reserved.", description="Legal copyright declaration")
    watermark_payload: Optional[str] = Field(default=None, description="Steganographic watermark payload or ID")
    output_path: Optional[str] = Field(default=None, description="Output destination file")


class ProvenanceSignResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    asset_sha256: str
    asset_bytes: int
    format: str
    claim_generator: str
    author: str
    created_at: str
    c2pa_mode: str  # "embedded_c2pa" | "sidecar_manifest"
    signed_asset_path: str
    manifest_path: Optional[str] = None
    verification_token: str


class ProvenanceVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    image_path: str = Field(..., description="Path to media file to verify")
    expected_author: Optional[str] = Field(default=None, description="Expected author name")


class ProvenanceVerifyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    valid: bool
    asset_sha256: str
    detected_author: Optional[str] = None
    c2pa_mode: str
    embedded_metadata: Dict[str, str] = Field(default_factory=dict)
    message: str


class VideoCompositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_video_path: Optional[str] = Field(default=None, description="Path to source video or raw recording")
    transcript: str = Field(..., description="Spoken transcript text for alignment and kinetic subtitles")
    words: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional word-level timestamps")
    duration_ms: Optional[int] = Field(default=None, description="Total video duration in ms (estimated if None)")
    style_preset: str = Field(default="hormozi_bold", description="Subtitles style: hormozi_bold | minimal_clean | cyberpunk_neon")
    enable_silence_cut: bool = Field(default=True, description="Whether to generate silence jump-cuts")
    enable_smart_reframe: bool = Field(default=True, description="Whether to reframe 16:9/1:1 to 9:16 vertical crop")
    enable_sound_design: bool = Field(default=True, description="Whether to compose audio ducking and SFX cues")
    output_path: Optional[str] = Field(default=None, description="Output mp4 path")
    author_name: str = Field(default="DNK-e.com", description="Author for C2PA provenance")


class VideoCompositionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    composition_id: str
    target_dimensions: str = "1080x1920 (9:16)"
    estimated_duration_ms: int
    silence_cut_plan: Optional[SilenceCutPlan] = None
    reframe_plan: Optional[SmartReframePlan] = None
    subtitles_track: Optional[KineticSubtitleTrack] = None
    sound_design_plan: Optional[SoundDesignPlan] = None
    ass_subtitle_path: Optional[str] = None
    ffmpeg_recipe: str
    output_video_path: Optional[str] = None
    is_rendered: bool = False
