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
