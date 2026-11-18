# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/tests/test_shopify_brick.py"
# purpose: "Senior Test Suite for dnk_shopify Sovereign Brick Contract (executes in < 1s)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
from pathlib import Path
import pytest

from services.dnk_shopify.src.service import DNKShopifyService
from services.dnk_shopify.contracts.schemas import (
    CartMutation,
    CartMutationQueueSpec,
    ProposalConfigSpec,
    ClientTicketRequest,
)
from services.dnk_shopify.mcp_server import (
    shopify_validate_liquid,
    shopify_list_theme_blocks,
    shopify_check_theme,
    shopify_cro_audit,
    shopify_calculate_cart,
    shopify_verify_7gates,
    shopify_generate_proposal_quote,
    shopify_triage_client_ticket,
)


@pytest.fixture
def shopify_service() -> DNKShopifyService:
    return DNKShopifyService()


def test_liquid_validation_balanced(shopify_service: DNKShopifyService):
    """Verify valid Liquid code with matched tags and valid schema."""
    valid_snippet = """
    {% if customer %}
      <div class="welcome">Hello {{ customer.name }}</div>
    {% else %}
      <a href="/login">Sign in</a>
    {% endif %}

    {% schema %}
    {
      "name": "Custom Banner",
      "settings": []
    }
    {% endschema %}
    """
    res = shopify_service.validate_liquid(valid_snippet)
    assert res.valid is True
    assert len(res.errors) == 0
    assert res.variables_count == 1
    assert res.tags_count >= 4


def test_liquid_validation_unclosed_tags(shopify_service: DNKShopifyService):
    """Verify detection of unclosed block tags."""
    invalid_snippet = """
    {% if product.available %}
      <span>In Stock</span>
    {% for tag in product.tags %}
      <span class="tag">{{ tag }}</span>
    """
    res = shopify_service.validate_liquid(invalid_snippet)
    assert res.valid is False
    assert any("Unclosed tag" in e for e in res.errors)


def test_liquid_validation_malformed_schema_json(shopify_service: DNKShopifyService):
    """Verify detection of broken JSON inside {% schema %}."""
    invalid_schema = """
    {% schema %}
    { "name": "Broken" "settings": [] }
    {% endschema %}
    """
    res = shopify_service.validate_liquid(invalid_schema)
    assert res.valid is False
    assert any("Invalid JSON inside {% schema %}" in e for e in res.errors)


def test_list_theme_blocks(shopify_service: DNKShopifyService):
    """Verify discovery of Theme Blocks 2.0 in DNK Sovereign 1.0.0 Apex."""
    blocks = shopify_service.list_theme_blocks()
    assert len(blocks) >= 70

    block_names = {b.block_name for b in blocks}
    assert "_product-main-buy-buttons.liquid" in block_names
    assert "button.liquid" in block_names
    assert "product_quantity-breaks-v2.liquid" in block_names
    assert "cart-drawer_body.liquid" in block_names

    priv_meta = next(b for b in blocks if b.block_name == "_product-main-buy-buttons.liquid")
    assert priv_meta.is_private is True

    pub_meta = next(b for b in blocks if b.block_name == "button.liquid")
    assert pub_meta.is_private is False


def test_theme_check_pass(shopify_service: DNKShopifyService):
    """Verify static structure check passes for DNK Sovereign 1.0.0 Apex."""
    res = shopify_service.check_theme()
    assert res.is_compliant is True
    assert res.errors_count == 0
    assert res.total_files >= 250


def test_theme_7gate_integrity(shopify_service: DNKShopifyService):
    """Verify 7-Gate Anti-Regression Theme Integrity passes with 100% CLEAN & PROTECTED."""
    res = shopify_service.run_7gate_integrity()
    assert res["success"] is True
    assert res["all_gates_passed"] is True
    assert "100% CLEAN & PROTECTED" in res["stdout"]


def test_theme_check_missing_dir(shopify_service: DNKShopifyService, tmp_path: Path):
    """Verify static check fails gracefully on missing mandatory folders."""
    res = shopify_service.check_theme(tmp_path / "non_existent_theme")
    assert res.is_compliant is False
    assert res.errors_count >= 1


def test_cart_calculation(shopify_service: DNKShopifyService):
    """Verify deterministic CartMutationQueue calculations."""
    spec = CartMutationQueueSpec(
        current_subtotal=400.0,
        free_shipping_threshold=1000.0,
        mutations=[
            CartMutation(
                action="add",
                variant_id="var_1",
                quantity=2,
                properties={"price": "150.0"},
            )
        ],
    )
    res = shopify_service.calculate_cart(spec)
    assert res.new_subtotal == 700.0
    assert res.remaining_for_free_shipping == 300.0
    assert res.progress_percentage == 70.0
    assert res.free_shipping_qualified is False
    assert res.item_count == 2

    # Now add enough to qualify
    spec_qual = CartMutationQueueSpec(
        current_subtotal=700.0,
        free_shipping_threshold=1000.0,
        mutations=[
            CartMutation(
                action="add",
                variant_id="var_2",
                quantity=1,
                properties={"price": "350.0"},
            )
        ],
    )
    res_qual = shopify_service.calculate_cart(spec_qual)
    assert res_qual.new_subtotal == 1050.0
    assert res_qual.remaining_for_free_shipping == 0.0
    assert res_qual.progress_percentage == 100.0
    assert res_qual.free_shipping_qualified is True


def test_cro_audit(shopify_service: DNKShopifyService):
    """Verify CRO readiness scoring for DNK Sovereign 1.0.0 Apex."""
    res = shopify_service.audit_cro()
    assert res.score == 100
    assert "Direct Conversion Buy Buttons" in res.detected_blocks
    assert "High-Converting AJAX Cart Drawer" in res.detected_blocks
    assert "Dual-Level Quantity Breaks v2" in res.detected_blocks


def test_fastmcp_tools():
    """Verify FastMCP dual-mount tools return structured dictionaries."""
    val = shopify_validate_liquid("{% if true %}OK{% endif %}")
    assert val["valid"] is True

    blocks = shopify_list_theme_blocks()
    assert len(blocks) >= 70

    check = shopify_check_theme()
    assert check["is_compliant"] is True

    gates = shopify_verify_7gates()
    assert gates["success"] is True

    cro = shopify_cro_audit()
    assert cro["score"] == 100

    cart = shopify_calculate_cart(subtotal=500.0, threshold=1000.0, added_items_price=500.0)
    assert cart["free_shipping_qualified"] is True


def test_personalized_proposal_and_cockpit_stages(shopify_service: DNKShopifyService):
    """Verify personalized $1200/$1500 proposal quote, ROI savings, and 6-stage cockpit."""
    spec = ProposalConfigSpec(
        client_name="Олександр Коваль",
        brand_name="Lumiere Beauty",
        niche="beauty_cosmetics",
        package_tier="scale_1500",
        extra_products_batches=2,
        include_gmc_setup=True,
        include_seo_semantics=True,
        monthly_orders_estimate=200,
        average_order_value_usd=75.0,
    )
    quote = shopify_service.generate_proposal_quote(spec)
    assert quote.base_price_usd == 1500
    assert quote.addons_total_usd == 600  # 2*50 + 300 + 200
    assert quote.total_investment_usd == 2100
    assert quote.prepayment_30_usd == 630.0
    assert quote.completion_70_usd == 1470.0
    assert quote.included_products_count == 40
    assert quote.included_languages_count == 2
    assert quote.included_revision_rounds == 3
    assert quote.annual_app_savings_usd == 2868
    assert len(quote.scope_sha256) == 64
    assert "product_quantity-breaks-v2.liquid" in quote.recommended_molecules

    stages_ready = shopify_service.initialize_client_deal_cockpit(quote, client_assets_ready=True)
    assert len(stages_ready) == 6
    assert stages_ready[0].status == "completed"
    assert stages_ready[1].status == "in_progress"
    assert len(stages_ready[0].artifacts[0].sha256_receipt) == 64

    stages_paused = shopify_service.initialize_client_deal_cockpit(quote, client_assets_ready=False)
    assert stages_paused[0].status == "waiting_client_assets"


def test_client_ticket_scope_guard_and_routing():
    """Verify Scope Guard classification (question vs in_scope_revision vs out_of_scope_upsell)."""
    prop = shopify_generate_proposal_quote(
        client_name="Ірина",
        brand_name="VibeDecor",
        niche="home_decor_lighting",
        package_tier="launch_1200",
    )
    assert prop["quote"]["total_investment_usd"] == 1200
    assert len(prop["stages"]) == 6

    # 1. In-scope design revision -> routes to node_brand_dna (denchik) and persists to SQLite WAL
    rev = shopify_triage_client_ticket(
        deal_id="deal-vibedecor-launch_1200",
        client_name="Ірина",
        request_text="Змініть основний колір кнопок на смарагдовий та оновіть шрифт заголовків",
        used_revisions_count=0,
        max_free_revisions=2,
        persist_to_canvas_session=True,
    )
    assert rev["classification"] == "in_scope_revision"
    assert rev["target_canvas_node_id"] == "node_brand_dna"
    assert rev["assigned_agent"] == "denchik"
    assert rev["remaining_free_revisions"] == 1
    assert rev["gate_state"] == "awaiting_founder_triage"
    assert len(rev["audit_hash"]) == 64

    # 2. Question -> does not consume revision quota
    q = shopify_triage_client_ticket(
        deal_id="deal-vibedecor-launch_1200",
        client_name="Ірина",
        request_text="Підкажіть, коли буде готовий другий етап воронки?",
        used_revisions_count=1,
        max_free_revisions=2,
    )
    assert q["classification"] == "question"
    assert q["remaining_free_revisions"] == 1
    assert q["upsell_estimate_usd"] == 0

    # 3. Out-of-scope ERP request -> blocked by Scope Guard with upsell estimate
    oos = shopify_triage_client_ticket(
        deal_id="deal-vibedecor-launch_1200",
        client_name="Ірина",
        request_text="Нам потрібна двостороння інтеграція з 1С та кастомний ERP модуль складу",
        used_revisions_count=1,
        max_free_revisions=2,
    )
    assert oos["classification"] == "out_of_scope_upsell"
    assert oos["gate_state"] == "upsell_quote_required"
    assert oos["upsell_estimate_usd"] == 250

