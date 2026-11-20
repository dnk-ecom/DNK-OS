# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk-seamless-injection/plugin.py"
# purpose: "DNK OS PluginBase adapter for Zero-Trace Seamless Visual Injection Engine."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-22"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import importlib
from typing import Dict, List
from fastapi import APIRouter
from pydantic import BaseModel

_plugin_base_mod = importlib.import_module("core.plugins.plugin_base")
PluginBase = getattr(_plugin_base_mod, "PluginBase")
from .mcp.server import (
    inject_brand_photo,
    inject_brand_video,
    inspect_photorealism_metrics,
)


class PhotoInjectionRequest(BaseModel):
    image_path: str
    output_path: str
    brand_text: str = "Monte"
    target_prompt: str = "donor logo"
    sync_to_shopify: bool = False


class Plugin(PluginBase):
    """DNK OS Plugin: Zero-Trace Seamless Visual Injection Engine."""

    def register_routes(self, api_router: APIRouter) -> None:
        router = APIRouter(
            prefix="/api/v1/seamless-injection",
            tags=["Plugin: Zero-Trace Seamless Visual Injection"],
        )

        @router.get("/status")
        async def get_status() -> Dict[str, object]:
            return {
                "plugin": "dnk-seamless-injection",
                "version": "1.0.0",
                "status": "active",
                "capabilities": [
                    "subpixel_segmentation",
                    "texture_preserving_inpaint",
                    "deformable_surface_tracking",
                    "photometric_grain_harmonization",
                    "shopify_admin_cloud_sync",
                ],
                "quality_gates": {
                    "lpips_max": 0.04,
                    "edge_gradient_consistency_min": 0.98,
                    "zero_residual_ocr": True,
                },
            }

        @router.post("/inject-photo")
        async def api_inject_photo(req: PhotoInjectionRequest) -> Dict[str, object]:
            return inject_brand_photo(
                image_path=req.image_path,
                output_path=req.output_path,
                brand_text=req.brand_text,
                target_prompt=req.target_prompt,
                sync_to_shopify=req.sync_to_shopify,
            )

        api_router.include_router(router)

    def get_nav_items(self) -> List[Dict[str, str]]:
        return [
            {
                "label": "Seamless Injection",
                "path": "/plugins/seamless-injection",
                "icon": "Sparkles",
            }
        ]


__all__ = [
    "Plugin",
    "inject_brand_photo",
    "inject_brand_video",
    "inspect_photorealism_metrics",
]
