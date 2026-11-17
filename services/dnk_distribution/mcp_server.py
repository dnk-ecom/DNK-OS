# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/mcp_server.py"
# purpose: "FastMCP Server for dnk_distribution Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from services.dnk_distribution.src.service import (
    check_compliance,
    evaluate_social_metrics,
    mine_audience_themes,
    process_data,
)
from services.dnk_distribution.src.social_feedback import SocialMetrics
from services.dnk_distribution.src.theme_miner import CommentItem

mcp = FastMCP("dnk_distribution")


@mcp.tool()
def distribution_check_compliance(
    text: str,
    is_promotional: bool = False
) -> Dict[str, Any]:
    """Validate marketing copy against brand guidelines, banned words, legal claims, and FTC rules."""
    report = check_compliance(text=text, is_promotional=is_promotional)
    return report.model_dump()


@mcp.tool()
def distribution_evaluate_rlsf(
    publication_id: str,
    views: int,
    retention_rate_3s: float,
    completion_rate: float,
    shares: int = 0,
    likes: int = 0,
    comments: int = 0,
    hook_type: Optional[str] = None
) -> Dict[str, Any]:
    """Compute RLSF multi-objective social reward signals and assign performance tier."""
    metrics = SocialMetrics(
        publication_id=publication_id,
        views=views,
        retention_rate_3s=retention_rate_3s,
        completion_rate=completion_rate,
        shares=shares,
        likes=likes,
        comments=comments,
    )
    report = evaluate_social_metrics(metrics=metrics, hook_type=hook_type)
    return report.model_dump()


@mcp.tool()
def distribution_mine_themes(
    comments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Mine customer comments to extract objections, buying intents, and copy angles."""
    parsed = [CommentItem(**c) for c in comments]
    res = mine_audience_themes(parsed)
    return res.model_dump()


@mcp.tool()
def execute(query: str) -> str:
    """Fallback query execution."""
    return process_data(query)


if __name__ == "__main__":
    mcp.run()
