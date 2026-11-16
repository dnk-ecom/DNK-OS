# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/mcp_server.py"
# purpose: "FastMCP Dual-Mount Server exposing dnk_shopify Theme Blocks 2.0 & Tinker tools."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repository root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from fastmcp import FastMCP
    except ImportError:
        class FastMCP:  # type: ignore
            def __init__(self, name: str, instructions: str = ""):
                self.name = name
                self.instructions = instructions
                self._tools = {}
            def tool(self, *args, **kwargs):
                def decorator(fn):
                    self._tools[fn.__name__] = fn
                    return fn
                return decorator
            async def call_tool(self, name: str, arguments: dict):
                fn = self._tools[name]
                return fn(**arguments)
            def run(self, *args, **kwargs):
                pass

from services.dnk_shopify.src.service import DNKShopifyService
from services.dnk_shopify.contracts.schemas import (
    CartMutation,
    CartMutationQueueSpec,
    ProposalConfigSpec,
    ClientTicketRequest,
)

mcp = FastMCP(
    "dnk_shopify",
    instructions="DNK Sovereign Shopify Workhorse: Theme Blocks 2.0, Liquid AST verification, Tinker 4.2.0 compatibility, and CartMutationQueue.",
)
_service = DNKShopifyService()


@mcp.tool()
def shopify_validate_liquid(code: str) -> Dict[str, Any]:
    """Validates Liquid template code ensuring balanced tags and valid schema JSON."""
    result = _service.validate_liquid(code)
    return result.model_dump()


@mcp.tool()
def shopify_list_theme_blocks(theme_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Discovers and parses Theme Blocks 2.0 in the theme blocks/ directory."""
    target = Path(theme_path) if theme_path else None
    blocks = _service.list_theme_blocks(target)
    return [b.model_dump() for b in blocks]


@mcp.tool()
def shopify_check_theme(theme_path: Optional[str] = None) -> Dict[str, Any]:
    """Runs static architecture integrity check on a Shopify theme directory."""
    target = Path(theme_path) if theme_path else None
    result = _service.check_theme(target)
    return result.model_dump()


@mcp.tool()
def shopify_cro_audit(theme_path: Optional[str] = None) -> Dict[str, Any]:
    """Evaluates theme conversion-rate readiness across canonical CRO components."""
    target = Path(theme_path) if theme_path else None
    result = _service.audit_cro(target)
    return result.model_dump()


@mcp.tool()
def shopify_calculate_cart(
    subtotal: float,
    threshold: float = 1000.0,
    added_items_price: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculates cart subtotal, free shipping progress, and qualified perks."""
    mutations = []
    if added_items_price is not None:
        mutations.append(
            CartMutation(
                action="add",
                variant_id="mock_item",
                quantity=1,
                properties={"price": str(added_items_price)},
            )
        )
    spec = CartMutationQueueSpec(
        current_subtotal=subtotal,
        free_shipping_threshold=threshold,
        mutations=mutations,
    )
    result = _service.calculate_cart(spec)
    return result.model_dump()


@mcp.tool()
def shopify_verify_7gates(theme_path: Optional[str] = None) -> Dict[str, Any]:
    """Executes the mandatory 7-Gate Anti-Regression Theme Integrity Gate on DNK Sovereign Apex."""
    target = Path(theme_path) if theme_path else None
    return _service.run_7gate_integrity(target)


@mcp.tool()
def shopify_generate_proposal_quote(
    client_name: str,
    brand_name: str,
    niche: str = "custom_dtc",
    package_tier: str = "scale_1500",
    extra_products_batches: int = 0,
    include_gmc_setup: bool = False,
    include_seo_semantics: bool = False,
    monthly_orders_estimate: int = 150,
    average_order_value_usd: float = 65.0,
) -> Dict[str, Any]:
    """
    Generates a personalized Shopify store development proposal ($1200 Launch or $1500 Scale),
    App-Tax savings ROI calculation, niche CRO molecule mapping, and 64-char SHA-256 contract seal.
    """
    spec = ProposalConfigSpec(
        client_name=client_name,
        brand_name=brand_name,
        niche=niche,  # type: ignore[arg-type]
        package_tier=package_tier,  # type: ignore[arg-type]
        extra_products_batches=extra_products_batches,
        include_gmc_setup=include_gmc_setup,
        include_seo_semantics=include_seo_semantics,
        monthly_orders_estimate=monthly_orders_estimate,
        average_order_value_usd=average_order_value_usd,
    )
    quote = _service.generate_proposal_quote(spec)
    stages = _service.initialize_client_deal_cockpit(quote, client_assets_ready=True)
    return {
        "quote": quote.model_dump(),
        "stages": [s.model_dump() for s in stages],
    }


@mcp.tool()
def shopify_triage_client_ticket(
    deal_id: str,
    client_name: str,
    request_text: str,
    used_revisions_count: int = 0,
    max_free_revisions: int = 3,
    preferred_node_id: Optional[str] = None,
    persist_to_canvas_session: bool = False,
) -> Dict[str, Any]:
    """
    Classifies a client revision or question via Scope Guard (question, in_scope_revision,
    or out_of_scope_upsell) and routes it to the target Spatial Canvas node and DNK OS agent.
    """
    req = ClientTicketRequest(
        deal_id=deal_id,
        client_name=client_name,
        request_text=request_text,
        preferred_node_id=preferred_node_id,
        used_revisions_count=used_revisions_count,
        max_free_revisions=max_free_revisions,
    )
    res = _service.triage_client_ticket(req, persist_to_canvas_session=persist_to_canvas_session)
    return res.model_dump()


if __name__ == "__main__":
    mcp.run()
