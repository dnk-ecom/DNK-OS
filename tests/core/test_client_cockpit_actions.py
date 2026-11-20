# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_client_cockpit_actions.py"
# purpose: "Unit tests for Client Cockpit Engine, Dual-Surface Actions, and Scope Guard triage."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

import pytest
from pathlib import Path

from core.client_cockpit.engine import ClientCockpitEngine, CANONICAL_6_STAGES
from core.action_bus.dual_surface_registry import (
    ActionExecutionContext,
    DualSurfaceActionRegistry,
)
from core.action_bus.actions.client_cockpit_actions import (
    handle_init_deal,
    handle_submit_ticket,
    handle_advance_stage,
    register_client_cockpit_actions,
)


@pytest.fixture
def temp_engine(tmp_path: Path):
    db_file = tmp_path / "test_client_cockpit.db"
    return ClientCockpitEngine(db_path=db_file)


def test_engine_init_deal(temp_engine: ClientCockpitEngine):
    deal_id = "test_noku_deal"
    state = temp_engine.init_deal(
        deal_id=deal_id,
        client_name="Андрій Ніколаєв",
        brand="NOKU",
        tier="scale_1500",
        total_amount=1500.0,
    )

    assert state["deal"]["deal_id"] == deal_id
    assert state["deal"]["total_amount"] == 1500.0
    assert state["deal"]["prepay_amount"] == 750.0
    assert state["deal"]["revision_quota"] == 3
    assert state["deal"]["revisions_used"] == 0

    assert len(state["stages"]) == 6
    assert state["stages"][0]["status"] == "completed"
    assert state["stages"][1]["status"] == "in_progress"
    assert state["stages"][2]["status"] == "pending"

    assert len(state["artifacts"]) >= 2
    artifact_names = [a["name"] for a in state["artifacts"]]
    assert "Жива комерційна пропозиція" in artifact_names


def test_engine_scope_guard_triage(temp_engine: ClientCockpitEngine):
    deal_id = "test_scope_deal"
    temp_engine.init_deal(deal_id=deal_id)

    # 1. Question triage
    t1 = temp_engine.submit_ticket(
        deal_id=deal_id,
        title="Питання щодо термінів",
        comment="Чи можна додати ще один колір пізніше?",
        category="auto",
    )
    assert t1.category == "question"

    # Quota shouldn't decrease for questions
    state1 = temp_engine.get_cockpit_state(deal_id)
    assert state1["deal"]["revisions_used"] == 0

    # 2. Out of scope upsell triage
    t2 = temp_engine.submit_ticket(
        deal_id=deal_id,
        title="Інтеграція з обліком",
        comment="Потрібна інтеграція з бас або 1С",
        category="auto",
    )
    assert t2.category == "out_of_scope_upsell"

    state2 = temp_engine.get_cockpit_state(deal_id)
    assert state2["deal"]["revisions_used"] == 0

    # 3. In-scope revision triage (default)
    t3 = temp_engine.submit_ticket(
        deal_id=deal_id,
        title="Шрифт заголовка",
        comment="Зробіть відступ між літерами трохи ширшим",
        category="auto",
    )
    assert t3.category == "in_scope_revision"

    # Quota increases by 1
    state3 = temp_engine.get_cockpit_state(deal_id)
    assert state3["deal"]["revisions_used"] == 1


def test_engine_stage_progression_and_artifacts(temp_engine: ClientCockpitEngine):
    deal_id = "test_progress_deal"
    temp_engine.init_deal(deal_id=deal_id)

    # Advance stage 2 to completed
    temp_engine.update_stage_status(deal_id, stage_num=2, new_status="completed")
    state = temp_engine.get_cockpit_state(deal_id)
    stage_2 = next(s for s in state["stages"] if s["stage_num"] == 2)
    assert stage_2["status"] == "completed"
    assert stage_2["completed_at"] is not None

    # Add custom artifact
    temp_engine.add_artifact(
        deal_id=deal_id,
        name="Figma Prototype Review",
        artifact_type="figma",
        url="https://figma.com/file/xyz",
    )
    state = temp_engine.get_cockpit_state(deal_id)
    assert any(a["name"] == "Figma Prototype Review" for a in state["artifacts"])


@pytest.mark.asyncio
async def test_dual_surface_cockpit_actions(monkeypatch, tmp_path: Path):
    db_file = tmp_path / "action_test.db"
    monkeypatch.setattr("core.client_cockpit.engine.DB_PATH", db_file)

    deal_id = "action_noku_deal"

    # 1. Test handle_init_deal
    ctx_init = ActionExecutionContext(
        action_id="cockpit.init_deal",
        payload={"deal_id": deal_id, "client_name": "Андрій", "brand": "NOKU"},
    )
    res_init = await handle_init_deal(ctx_init)
    assert res_init.success is True
    assert res_init.broadcast_events[0]["event"] == "cockpit_deal_initialized"

    # 2. Test handle_submit_ticket
    ctx_ticket = ActionExecutionContext(
        action_id="cockpit.submit_ticket",
        payload={
            "deal_id": deal_id,
            "title": "Зміна кольору плашки",
            "comment": "Змініть бекграунд на матовий графіт",
            "category": "in_scope_revision",
        },
    )
    res_ticket = await handle_submit_ticket(ctx_ticket)
    assert res_ticket.success is True
    assert res_ticket.result["ticket"]["category"] == "in_scope_revision"
    assert res_ticket.broadcast_events[0]["event"] == "cockpit_ticket_submitted"

    # 3. Test handle_advance_stage
    ctx_stage = ActionExecutionContext(
        action_id="cockpit.advance_stage",
        payload={"deal_id": deal_id, "stage_num": 3, "status": "completed"},
    )
    res_stage = await handle_advance_stage(ctx_stage)
    assert res_stage.success is True
    assert res_stage.result["stage_num"] == 3
    assert res_stage.broadcast_events[0]["event"] == "cockpit_stage_advanced"


def test_registration_in_action_registry():
    registry = DualSurfaceActionRegistry.get_shared_instance()
    register_client_cockpit_actions()

    assert registry.get_action_spec("cockpit.init_deal") is not None
    assert registry.get_action_spec("cockpit.submit_ticket") is not None
    assert registry.get_action_spec("cockpit.advance_stage") is not None


def test_engine_ticket_lifecycle_and_resolution(temp_engine: ClientCockpitEngine):
    deal_id = "test_lifecycle_deal"
    temp_engine.init_deal(deal_id=deal_id)

    # 1. Submit ticket
    t = temp_engine.submit_ticket(
        deal_id=deal_id,
        title="Змінити розмір шрифту ціни",
        comment="На мобільному ціна занадто велика",
        category="in_scope_revision",
        selector=".price-item--regular",
        section_id="main-product",
        block_id="price",
    )
    assert t.status == "open"

    # 2. Query open tickets
    open_tickets = temp_engine.get_tickets(deal_id=deal_id, status="open")
    assert len(open_tickets) == 1
    assert open_tickets[0]["ticket_id"] == t.ticket_id
    assert open_tickets[0]["section_id"] == "main-product"

    # 3. Resolve ticket
    resolved = temp_engine.resolve_ticket(
        deal_id=deal_id,
        ticket_id=t.ticket_id,
        resolution_note="Зменшено font-size до 18px у block-price.css (commit 4b8d21)",
        status="resolved",
    )
    assert resolved["status"] == "resolved"
    assert "4b8d21" in resolved["resolution_note"]
    assert resolved["resolved_at"] is not None

    # 4. Verify filtered queries
    assert len(temp_engine.get_tickets(deal_id=deal_id, status="open")) == 0
    resolved_list = temp_engine.get_tickets(deal_id=deal_id, status="resolved")
    assert len(resolved_list) == 1
    assert resolved_list[0]["ticket_id"] == t.ticket_id


def test_fastmcp_cockpit_tools(monkeypatch, tmp_path: Path):
    import json
    from core.kernel_mcp import create_fastmcp_server

    db_file = tmp_path / "mcp_test.db"
    monkeypatch.setattr("core.client_cockpit.engine.DB_PATH", db_file)

    server = create_fastmcp_server()
    deal_id = "test_mcp_deal"

    engine = ClientCockpitEngine(db_path=db_file)
    engine.init_deal(deal_id=deal_id)
    t = engine.submit_ticket(
        deal_id=deal_id,
        title="Кнопка Купити",
        comment="Зробіть радіус заокруглення 8px",
        selector=".btn-atc",
    )

    # FastMCP tools
    tools = {tool.name: tool.fn for tool in server._tool_manager.list_tools()}
    assert "get_client_tickets" in tools
    assert "resolve_client_ticket" in tools
    assert "get_cockpit_status" in tools

    # 1. Test get_client_tickets
    res_str = tools["get_client_tickets"](deal_id=deal_id, status="all")
    res_data = json.loads(res_str)
    assert res_data["deal_id"] == deal_id
    assert res_data["count"] == 1
    assert res_data["tickets"][0]["ticket_id"] == t.ticket_id

    # 2. Test resolve_client_ticket
    res_resolve = tools["resolve_client_ticket"](
        deal_id=deal_id,
        ticket_id=t.ticket_id,
        resolution_note="Застосовано border-radius: 8px",
        status="resolved",
    )
    res_resolve_data = json.loads(res_resolve)
    assert res_resolve_data["success"] is True
    assert res_resolve_data["ticket"]["status"] == "resolved"

    # 3. Test get_cockpit_status
    status_str = tools["get_cockpit_status"](deal_id=deal_id)
    status_data = json.loads(status_str)
    assert status_data["deal_id"] == deal_id
    assert len(status_data["state"]["stages"]) == 6

    # 4. Test client_success_get_inbox
    inbox_str = tools["client_success_get_inbox"](deal_id=deal_id)
    inbox_data = json.loads(inbox_str)
    assert inbox_data["deal_id"] == deal_id
    assert "open_tickets_count" in inbox_data

    # 5. Test client_success_dispatch_to_builder
    dispatch_str = tools["client_success_dispatch_to_builder"](
        deal_id=deal_id, ticket_id=t.ticket_id, builder="denchik"
    )
    dispatch_data = json.loads(dispatch_str)
    assert dispatch_data["success"] is True
    assert dispatch_data["task_dna"]["builder"] == "denchik"


def test_client_success_agent_visual_area_review(tmp_path: Path):
    from core.client_success.agent import ClientSuccessAgent, VisualReviewPayload, BoundingBox

    db_file = tmp_path / "cs_agent_test.db"
    engine = ClientCockpitEngine(db_path=db_file)
    deal_id = "test_cs_deal"
    engine.init_deal(deal_id=deal_id)

    agent = ClientSuccessAgent(engine=engine)
    bbox = BoundingBox(
        x=120.0,
        y=340.0,
        width=450.0,
        height=220.0,
        page_x=120.0,
        page_y=540.0,
        scroll_x=0.0,
        scroll_y=200.0,
    )
    payload = VisualReviewPayload(
        deal_id=deal_id,
        title="Збільшити міжрядковий інтервал в описі",
        comment="Текст зливається, зробіть line-height 1.6",
        category="auto",
        section_id="main-product",
        block_id="description",
        selector=".product__description",
        bounding_box=bbox,
        page_url="/products/magnetic-menu-board?preview=1",
        client_name="Андрій",
    )

    res = agent.process_visual_review(payload)

    assert res.category == "in_scope_revision"
    assert "description" in res.client_acknowledgment
    assert res.quota_remaining == 2
    assert res.builder_task["target_element"]["bounding_box"]["width"] == 450.0
    assert res.builder_task["suggested_file"] == "blocks/description.liquid"

    # Verify preview link generator
    link = ClientSuccessAgent.generate_preview_review_link(
        "https://noku.store/products/menu-board", deal_id="deal_noku_2026", client_name="Andrii"
    )
    assert "dnk_review=1" in link
    assert "deal_id=deal_noku_2026" in link


def test_client_success_agent_responsive_relative_anchor(tmp_path: Path):
    from core.client_success.agent import ClientSuccessAgent, VisualReviewPayload, BoundingBox, RelativeAnchor

    db_file = tmp_path / "cs_anchor_test.db"
    engine = ClientCockpitEngine(db_path=db_file)
    deal_id = "test_anchor_deal"
    engine.init_deal(deal_id=deal_id)

    agent = ClientSuccessAgent(engine=engine)
    anchor = RelativeAnchor(
        selector="[data-section-id='header']",
        rel_x_pct=45.5,
        rel_y_pct=12.2,
        parent_tag="header"
    )
    bbox = BoundingBox(
        x=200.0,
        y=50.0,
        width=300.0,
        height=80.0,
        page_x=200.0,
        page_y=50.0,
        relative_anchor=anchor
    )
    payload = VisualReviewPayload(
        deal_id=deal_id,
        title="Змінити логотип на білий",
        comment="Потрібно замінити логотип у шапці на білий варіант",
        section_id="header",
        selector="header .logo-img",
        bounding_box=bbox,
    )

    res = agent.process_visual_review(payload)
    assert res.category == "in_scope_revision"
    assert res.builder_task["target_element"]["relative_anchor"] is not None
    assert res.builder_task["target_element"]["relative_anchor"]["rel_x_pct"] == 45.5
    assert res.builder_task["target_element"]["relative_anchor"]["parent_tag"] == "header"


