# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_video_tool.py"
# purpose: "Native Hermes tool for programmatic video generation, Remotion composition synthesis, and media rendering."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKVideoTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except ImportError:
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_video_generate_composition(
    title: str,
    props: Optional[Dict[str, Any]] = None,
    duration_seconds: int = 15,
    format_type: str = "story_9_16",
    workspace_id: str = "ws-video-studio"
) -> str:
    """
    Synthesizes a programmatic Remotion/FrameCN video composition for product marketing or social reels.

    Args:
        title: Composition headline / product name.
        props: Parameterized visual elements (price, discount, cta, image_urls).
        duration_seconds: Video duration in seconds (default 15).
        format_type: 'story_9_16' (1080x1920) or 'landscape_16_9' (1920x1080) or 'square_1_1' (1080x1080).
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the generated composition metadata, timeline keyframes, and output spec.
    """
    props = props or {}
    composition_id = f"comp_{format_type}_{abs(hash(title)) % 100000}"

    timeline = [
        {"timestamp": 0.0, "scene": "IntroHook", "animation": "fadeInScale", "text": title},
        {"timestamp": 3.0, "scene": "ProductShowcase", "animation": "slideRight", "props": props},
        {"timestamp": 10.0, "scene": "SpecialOffer", "animation": "pulseBadge", "discount": props.get("discount", "20% OFF")},
        {"timestamp": 13.0, "scene": "CallToAction", "animation": "bounceCTA", "cta": props.get("cta", "Shop Now")}
    ]

    # Emit live event to Visual Cabinet
    if RuntimeEvent and RuntimeEventBus:
        try:
            bus = RuntimeEventBus.get_instance()
            bus.publish(RuntimeEvent(
                tenant_id="tenant-alpha-001",
                workspace_id=workspace_id,
                canvas_id="canvas-main-001",
                graph_id="graph-swarm-001",
                thread_id=f"thread-video-{composition_id}",
                execution_id=f"exec-video-{composition_id}",
                node_id="dnk_video_ai_creator",
                event_type="artifact.generated",
                sequence_number=1,
                payload={
                    "composition_id": composition_id,
                    "title": title,
                    "duration": duration_seconds,
                    "format": format_type
                }
            ))
        except Exception:
            pass

    return json.dumps({
        "status": "success",
        "composition_id": composition_id,
        "title": title,
        "format": format_type,
        "fps": 60,
        "duration_seconds": duration_seconds,
        "timeline_scenes": timeline,
        "message": f"Successfully synthesized Remotion video composition '{composition_id}'."
    }, indent=2, ensure_ascii=False)


def get_dnk_video_schema() -> Dict[str, Any]:
    """Returns OpenAI/Hermes tool schema for dnk_video_generate_composition."""
    return {
        "type": "function",
        "function": {
            "name": "dnk_video_generate_composition",
            "description": "Synthesizes a programmatic Remotion / FrameCN video composition for product marketing, stories, and reels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Video headline or product title."
                    },
                    "props": {
                        "type": "object",
                        "description": "Visual parameters (price, discount, cta, image_urls)."
                    },
                    "duration_seconds": {
                        "type": "integer",
                        "description": "Duration in seconds (default: 15)."
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["story_9_16", "landscape_16_9", "square_1_1"],
                        "description": "Aspect ratio and layout format."
                    },
                    "workspace_id": {
                        "type": "string",
                        "description": "Target workspace identifier (default: ws-video-studio)."
                    }
                },
                "required": ["title"]
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_video_generate_composition",
        toolset="video",
        schema=get_dnk_video_schema(),
        handler=dnk_video_generate_composition,
    )
except Exception:
    pass
