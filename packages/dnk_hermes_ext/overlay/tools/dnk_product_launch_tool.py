# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_product_launch_tool.py"
# purpose: "Native Hermes tool bridge for triggering One-Click Multi-Agent Product Launch flow."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MVP_PATH = HUB_ROOT
if str(MVP_PATH) not in sys.path:
    sys.path.insert(0, str(MVP_PATH))

from core.flows.product_launch_flow import (
    product_launch_pipeline,
    ProductLaunchInput,
)


def dnk_one_click_product_launch(
    product_name: str,
    target_audience: str,
    price_usd: float,
    cost_usd: float,
    key_features_csv: str = "Premium Quality, Ergonomic Design, 2-Year Warranty",
    workspace_id: str = "ws-alpha-001",
) -> str:
    """
    Trigger end-to-end One-Click Product Launch pipeline coordinating:
      - dnk_marketing_cmo: Marketing Angles & Copywriting
      - dnk_shopify: Shopify PDP Liquid Section
      - dnk_video_ai_creator: Remotion 9:16 Video Reel
      - dnk_finance_cfo: Unit Economics & Break-Even ROAS
    """
    try:
        features = [f.strip() for f in key_features_csv.split(",") if f.strip()]
        payload = ProductLaunchInput(
            product_name=product_name,
            target_audience=target_audience,
            price_usd=float(price_usd),
            cost_usd=float(cost_usd),
            key_features=features,
            workspace_id=workspace_id,
        )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(asyncio.run, product_launch_pipeline.execute(payload)).result()
        else:
            res = asyncio.run(product_launch_pipeline.execute(payload))

        return json.dumps(res.model_dump(), indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)}, indent=2)


def get_product_launch_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "dnk_one_click_product_launch",
                "description": "Execute autonomous multi-agent One-Click Product Launch pipeline (CMO + Shopify + Video AI + CFO).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "Product name"},
                        "target_audience": {"type": "string", "description": "Target customer demographic"},
                        "price_usd": {"type": "number", "description": "Retail price in USD"},
                        "cost_usd": {"type": "number", "description": "COGS cost in USD"},
                        "key_features_csv": {"type": "string", "description": "Comma-separated list of product features"},
                        "workspace_id": {"type": "string", "description": "Target workspace ID", "default": "ws-alpha-001"},
                    },
                    "required": ["product_name", "target_audience", "price_usd", "cost_usd"],
                },
            },
        }
    ]


try:
    from tools import registry
    registry.register(
        name="dnk_one_click_product_launch",
        toolset="dnk_swarm",
        schema=get_product_launch_schemas()[0],
        handler=dnk_one_click_product_launch,
    )
except Exception:
    pass

