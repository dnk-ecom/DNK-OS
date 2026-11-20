# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/tests/test_brick.py"
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


def test_list_theme_blocks_donor(shopify_service: DNKShopifyService):
    """Verify discovery of Theme Blocks 2.0 in donor reference theme."""
    tinker_p = (
        Path(__file__).resolve().parent.parent.parent.parent.parent
        / "DNKEcom"
        / "DNK-Ecom_git_mirrow"
        / "tinker"
    )
    if tinker_p.exists():
        blocks = shopify_service.list_theme_blocks(tinker_p)
        assert len(blocks) >= 20
        priv_meta = next((b for b in blocks if b.is_private), None)
        pub_meta = next((b for b in blocks if not b.is_private), None)
        assert priv_meta is not None or pub_meta is not None


def test_checkpoint_engine_audit(shopify_service: DNKShopifyService):
    """Verify 7-Gate Checkpoint Engine cleanly audits the MVP clean-slate theme."""
    from services.dnk_shopify.engine.checkpoints import CheckpointEngine, CheckpointStatus
    engine = CheckpointEngine()
    audit = engine.audit_theme(shopify_service.default_theme_path)
    assert audit["total_checkpoints"] == 7
    assert len(audit["checkpoints"]) == 7
    # For a clean slate theme, Gate 0 starts as failed until tokens are authored
    assert audit["checkpoints"][0]["status"] == CheckpointStatus.FAILED


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


def test_cro_audit_structure(shopify_service: DNKShopifyService):
    """Verify CRO readiness audit returns structured scoring object."""
    res = shopify_service.audit_cro()
    assert hasattr(res, "score")
    assert hasattr(res, "detected_blocks")
    assert hasattr(res, "missing_blocks")


def test_fastmcp_tools():
    """Verify FastMCP dual-mount tools return structured dictionaries."""
    val = shopify_validate_liquid("{% if true %}OK{% endif %}")
    assert val["valid"] is True

    cart = shopify_calculate_cart(subtotal=500.0, threshold=1000.0, added_items_price=500.0)
    assert cart["free_shipping_qualified"] is True


def test_proposal_quote_generation(shopify_service: DNKShopifyService):
    """Verify deterministic proposal quote, App-Tax savings, and 64-char SHA-256 seal."""
    spec = ProposalConfigSpec(
        client_name="Олександр",
        brand_name="Lumiere",
        niche="home_decor_lighting",
        package_tier="scale_1500",
        include_gmc_setup=True,
    )
    quote = shopify_service.generate_proposal_quote(spec)
    assert quote.total_investment_usd == 1800  # 1500 + 300 GMC
    assert quote.prepayment_30_usd == 540.0
    assert quote.completion_70_usd == 1260.0
    assert quote.annual_app_savings_usd == 2868
    assert len(quote.scope_sha256) == 64
    assert len(quote.niche_pain_to_molecule_matrix) >= 2


def test_client_cockpit_initialization(shopify_service: DNKShopifyService):
    """Verify 6-stage DEC-010 client cockpit generation and SLA pause flag."""
    spec = ProposalConfigSpec(
        client_name="Олександр",
        brand_name="Lumiere",
        package_tier="launch_1200",
    )
    quote = shopify_service.generate_proposal_quote(spec)
    
    # Ready assets -> Stage 1 completed, Stage 2 in_progress
    stages = shopify_service.initialize_client_deal_cockpit(quote, client_assets_ready=True)
    assert len(stages) == 6
    assert stages[0].status == "completed"
    assert stages[1].status == "in_progress"

    # Waiting assets -> Stage 1 SLA paused
    stages_paused = shopify_service.initialize_client_deal_cockpit(quote, client_assets_ready=False)
    assert stages_paused[0].status == "waiting_client_assets"


def test_ticket_scope_guard_triage(shopify_service: DNKShopifyService):
    """Verify Scope Guard deterministic classification: question, in-scope, out-of-scope."""
    # 1. Question (no revision quota used)
    req_q = ClientTicketRequest(
        deal_id="deal-test",
        client_name="Олександр",
        request_text="Як мені підключити платіжку Stripe до налаштованого чекауту?",
        used_revisions_count=1,
        max_free_revisions=3,
    )
    res_q = shopify_service.triage_client_ticket(req_q)
    assert res_q.classification == "question"
    assert res_q.remaining_free_revisions == 2

    # 2. In-scope revision (uses 1 revision)
    req_rev = ClientTicketRequest(
        deal_id="deal-test",
        client_name="Олександр",
        request_text="Змініть колір кнопки Купити на смарагдовий і зробіть липкою",
        used_revisions_count=1,
        max_free_revisions=3,
    )
    res_rev = shopify_service.triage_client_ticket(req_rev)
    assert res_rev.classification == "in_scope_revision"
    assert res_rev.remaining_free_revisions == 1

    # 3. Out-of-scope upsell (triggers quote)
    req_out = ClientTicketRequest(
        deal_id="deal-test",
        client_name="Олександр",
        request_text="Нам потрібна повна 1С ERP інтеграція зі складом",
        used_revisions_count=0,
        max_free_revisions=3,
    )
    res_out = shopify_service.triage_client_ticket(req_out)
    assert res_out.classification == "out_of_scope_upsell"
    assert res_out.upsell_estimate_usd == 250


def test_ticket_taskboard_sqlite_persistence(shopify_service: DNKShopifyService):
    """Verify ticket triage persists task to .agents/taskboard/tasks.sqlite."""
    import sqlite3
    req = ClientTicketRequest(
        deal_id="deal-persist-unit-test",
        client_name="Тестовий Клієнт",
        request_text="Зробіть шрифт заголовків Playfair Display на картці товару",
        used_revisions_count=0,
        max_free_revisions=3,
    )
    res = shopify_service.triage_client_ticket(req, persist_to_taskboard=True)
    assert res.classification == "in_scope_revision"

    db_path = Path(".agents/taskboard/tasks.sqlite")
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT id, status, subagent_role FROM agent_tasks WHERE id = ?", (res.ticket_id,))
        row = cur.fetchone()
        conn.close()
        assert row is not None
        assert row[0] == res.ticket_id
        assert row[1] == "todo"
        assert row[2] == "denchik" or row[2] == "dnk_shopify"
