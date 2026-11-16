# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/src/smart_reframing.py"
# purpose: "Smart Reframing Engine: 9:16 AI Auto-Framing & Speaker Centering with Trajectory Smoothing"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm (Gerych Prime & Antigravity)"
# --- END DNK-MRH-HEADER ---

import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized bounding box coordinates (0.0 to 1.0)."""
    x: float = Field(..., description="Top-left X coordinate normalized 0.0-1.0")
    y: float = Field(..., description="Top-left Y coordinate normalized 0.0-1.0")
    width: float = Field(..., description="Box width normalized 0.0-1.0")
    height: float = Field(..., description="Box height normalized 0.0-1.0")
    confidence: float = Field(default=0.95, description="Detection confidence 0.0-1.0")


class SpeakerTrackingPoint(BaseModel):
    """Timestamped detected speaker location in the frame."""
    timestamp_ms: int
    speaker_bbox: BoundingBox
    is_speaking: bool = True


class ReframeKeyframe(BaseModel):
    """Calculated 9:16 crop window keyframe."""
    timestamp_ms: int
    crop_x: int = Field(..., description="Pixel offset X in original video")
    crop_y: int = Field(..., description="Pixel offset Y in original video")
    crop_width: int = Field(..., description="Width of 9:16 crop window")
    crop_height: int = Field(..., description="Height of 9:16 crop window")
    focus_target: str = Field(default="speaker_face", description="speaker_face | rule_of_thirds | center")


class SmartReframePlan(BaseModel):
    """Full smart reframing plan with smoothing and FFmpeg filters."""
    original_width: int
    original_height: int
    target_width: int = 1080
    target_height: int = 1920
    crop_box_width: int
    crop_box_height: int
    keyframes: List[ReframeKeyframe]
    tracking_points_count: int
    average_pan_speed_px_per_sec: float
    ffmpeg_filter: str


class SmartReframingEngine:
    """
    Intelligent 9:16 Auto-Reframing Engine.
    Converts horizontal (16:9) or square (1:1) video to vertical (9:16)
    while dynamically tracking and centering the active speaker using
    Exponential Moving Average (EMA) and Deadband filtering.
    """

    def __init__(self, smoothing_alpha: float = 0.25, deadband_ratio: float = 0.12):
        self.smoothing_alpha = smoothing_alpha
        self.deadband_ratio = deadband_ratio

    def plan_reframe(
        self,
        original_width: int = 1920,
        original_height: int = 1080,
        tracking_points: Optional[List[SpeakerTrackingPoint]] = None,
        duration_ms: int = 5000,
        target_aspect_ratio: float = 9.0 / 16.0
    ) -> SmartReframePlan:
        """
        Calculates 9:16 crop coordinates with smooth camera panning.
        If tracking points are not provided, generates realistic synthetic speaker tracking.
        """
        crop_h = original_height
        crop_w = int(round(crop_h * target_aspect_ratio))

        if crop_w > original_width:
            crop_w = original_width
            crop_h = int(round(crop_w / target_aspect_ratio))

        crop_w = crop_w - (crop_w % 2)
        crop_h = crop_h - (crop_h % 2)

        max_x_offset = max(0, original_width - crop_w)
        default_center_x = max_x_offset // 2

        if not tracking_points or len(tracking_points) == 0:
            tracking_points = self._generate_synthetic_tracking(original_width, original_height, duration_ms)

        keyframes: List[ReframeKeyframe] = []
        smoothed_center_x = float(default_center_x + (crop_w // 2))
        deadband_px = crop_w * self.deadband_ratio
        total_pan_distance = 0.0

        for pt in tracking_points:
            bbox = pt.speaker_bbox
            face_center_x = (bbox.x + bbox.width / 2.0) * original_width

            delta = face_center_x - smoothed_center_x
            if abs(delta) > deadband_px:
                target_center = face_center_x - (math.copysign(deadband_px * 0.6, delta))
                new_center = (self.smoothing_alpha * target_center) + ((1.0 - self.smoothing_alpha) * smoothed_center_x)
                total_pan_distance += abs(new_center - smoothed_center_x)
                smoothed_center_x = new_center

            ideal_crop_x = int(round(smoothed_center_x - (crop_w / 2.0)))
            clamped_crop_x = max(0, min(max_x_offset, ideal_crop_x))
            clamped_crop_x = clamped_crop_x - (clamped_crop_x % 2)

            crop_y = 0

            keyframes.append(
                ReframeKeyframe(
                    timestamp_ms=pt.timestamp_ms,
                    crop_x=clamped_crop_x,
                    crop_y=crop_y,
                    crop_width=crop_w,
                    crop_height=crop_h,
                    focus_target="speaker_face" if pt.is_speaking else "center"
                )
            )

        duration_sec = max(1.0, duration_ms / 1000.0)
        avg_pan_speed = round(total_pan_distance / duration_sec, 2)

        median_x = int(sum(k.crop_x for k in keyframes) / max(1, len(keyframes)))
        median_x = median_x - (median_x % 2)

        ffmpeg_filter = f"crop={crop_w}:{crop_h}:{median_x}:0,scale=1080:1920:flags=lanczos"

        return SmartReframePlan(
            original_width=original_width,
            original_height=original_height,
            target_width=1080,
            target_height=1920,
            crop_box_width=crop_w,
            crop_box_height=crop_h,
            keyframes=keyframes,
            tracking_points_count=len(keyframes),
            average_pan_speed_px_per_sec=avg_pan_speed,
            ffmpeg_filter=ffmpeg_filter
        )

    def _generate_synthetic_tracking(
        self,
        orig_w: int,
        orig_h: int,
        duration_ms: int
    ) -> List[SpeakerTrackingPoint]:
        pts: List[SpeakerTrackingPoint] = []
        step_ms = 250
        steps = max(2, duration_ms // step_ms)

        for i in range(steps):
            t_ms = i * step_ms
            t_sec = t_ms / 1000.0
            drift = 0.08 * math.sin(t_sec * 0.7) + 0.03 * math.cos(t_sec * 1.5)

            norm_x = 0.45 + drift
            norm_y = 0.22
            norm_w = 0.22
            norm_h = 0.32

            pts.append(
                SpeakerTrackingPoint(
                    timestamp_ms=t_ms,
                    speaker_bbox=BoundingBox(
                        x=max(0.1, min(0.7, norm_x)),
                        y=norm_y,
                        width=norm_w,
                        height=norm_h,
                        confidence=0.98
                    ),
                    is_speaking=True
                )
            )
        return pts


smart_reframing_engine = SmartReframingEngine()
