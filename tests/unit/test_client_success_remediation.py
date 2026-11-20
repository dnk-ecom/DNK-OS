# --- DNK-MRH-HEADER ---
# mrh_id: "tests/unit/test_client_success_remediation.py"
# purpose: "Unit & Integration test for In-Context Visual Review Remediation Loop to Denchik."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import pytest
from pathlib import Path

from core.client_cockpit.engine import ClientCockpitEngine
from core.client_success.agent import ClientSuccessAgent, VisualReviewPayload, BoundingBox, RelativeAnchor
from core.client_success.remediation_engine import RemediationEngine


def test_visual_review_to_denchik_loop(tmp_path: Path):
    # Setup test sqlite db in tmp_path
    db_file = tmp_path / "test_cockpit.db"
    engine = ClientCockpitEngine(db_path=str(db_file))
    deal_id = "deal_test_m_kraft"
    engine.init_deal(deal_id=deal_id, client_name="M-Kraft Test", brand="M-Kraft")

    # 1. Simulate client submitting visual area review from m-kraft.kuzmenko.top
    cs_agent = ClientSuccessAgent(engine=engine)
    payload = VisualReviewPayload(
        deal_id=deal_id,
        title="Зміна кольору кнопки 'Купити'",
        comment="Зробіть кнопку оформлення смарагдово-зеленою, щоб вона краще виділялася",
        category="in_scope_revision",
        selector=".btn-cart",
        section_id="main-product",
        block_id="buy_buttons",
        page_url="https://m-kraft.kuzmenko.top/demo.html",
        bounding_box=BoundingBox(
            x=150, y=320, width=280, height=52,
            relative_anchor=RelativeAnchor(selector=".btn-cart", rel_x_pct=50, rel_y_pct=50)
        )
    )
    res = cs_agent.process_visual_review(payload)
    assert res.ticket_id.startswith("TKT-")
    assert "зафіксовано" in res.client_acknowledgment
    assert res.builder_task["deal_id"] == deal_id
    assert res.builder_task["target_element"]["selector"] == ".btn-cart"

    # 2. Denchik Remediation Engine synthesizes a git diff patch
    sample_file = tmp_path / "mock_component.liquid"
    original_code = (
        '<div class="product-form">\n'
        '  <button class="btn-cart" style="background:#2563eb;">Купити зараз</button>\n'
        '</div>\n'
    )
    sample_file.write_text(original_code, encoding="utf-8")

    proposed_code = (
        '<div class="product-form">\n'
        '  <button class="btn-cart" style="background:#10b981;">Купити зараз</button>\n'
        '</div>\n'
    )

    rem_engine = RemediationEngine(engine=engine, repo_root=tmp_path)
    proposal = rem_engine.synthesize_remediation(
        deal_id=deal_id,
        ticket_id=res.ticket_id,
        target_file="mock_component.liquid",
        new_content=proposed_code,
    )

    assert proposal.proposal_id == f"PROP-{res.ticket_id}"
    assert proposal.status == "pending_approval"
    assert "-  <button class=\"btn-cart\" style=\"background:#2563eb;\">" in proposal.unified_diff
    assert "+  <button class=\"btn-cart\" style=\"background:#10b981;\">" in proposal.unified_diff
    assert "Що це" in proposal.explanation_uk

    # 3. Maxim's 1-Click Approval applies the patch
    apply_res = rem_engine.apply_remediation(
        proposal_id=proposal.proposal_id,
        new_content=proposed_code,
        approver="maksym",
    )

    assert apply_res["success"] is True
    assert apply_res["status"] == "resolved"
    assert apply_res["approved_by"] == "maksym"

    # Verify physical file on disk updated
    updated_file_content = sample_file.read_text(encoding="utf-8")
    assert 'background:#10b981;' in updated_file_content

    # Verify ticket resolved in database
    tickets = engine.get_tickets(deal_id=deal_id, status="resolved")
    assert len(tickets) == 1
    assert "Approved by maksym" in tickets[0]["resolution_note"]
