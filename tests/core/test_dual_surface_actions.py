# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_dual_surface_actions.py"
# purpose: "Unit & Integration test suite verifying DualSurfaceActionRegistry, FastMCP tool export, and HITL gate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

import asyncio
import pytest

from core.action_bus.broadcaster import EventBroadcaster
from core.action_bus.dual_surface_registry import (
    ActionDispatchResult,
    DualSurfaceActionRegistry,
)
from core.action_bus.models import BusEventType
from core.adapters.hermes_ui_bridge import HermesUIBridge
from core.domain.vibe_core_contracts import (
    ActionSurfaceMode,
    DualSurfaceActionSpec,
    NodeLifecycleState,
)


@pytest.fixture
def isolated_registry():
    """Provides an isolated DualSurfaceActionRegistry connected to an isolated bridge."""
    broadcaster = EventBroadcaster()
    bridge = HermesUIBridge(broadcaster=broadcaster)
    registry = DualSurfaceActionRegistry(ui_bridge=bridge)
    return registry, bridge, broadcaster


@pytest.mark.asyncio
async def test_action_registration_and_mcp_export(isolated_registry):
    """Verifies action registration via method and decorator, plus FastMCP schema generation."""
    registry, bridge, broadcaster = isolated_registry

    # 1. Register simple dual action
    spec1 = DualSurfaceActionSpec(
        action_id="canvas.move_node",
        label_uk="Перемістити вузол",
        description_en="Moves a canvas node to new coordinates",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_canvas",
        mcp_tool_name="canvas_move_node",
        input_json_schema={
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "x": {"type": "number"},
                "y": {"type": "number"},
            },
            "required": ["node_id", "x", "y"],
        },
        ui_widget="button",
        ui_tone="primary",
    )

    async def move_handler(payload, actor="human", origin="ui"):
        return {"status": "moved", "node_id": payload["node_id"], "x": payload["x"], "y": payload["y"]}

    registry.register_action(spec1, move_handler)

    # 2. Register human-only action via decorator
    spec2 = DualSurfaceActionSpec(
        action_id="billing.release_payment",
        label_uk="Підтвердити оплату",
        description_en="Final authorization of supplier invoice",
        surface_mode=ActionSurfaceMode.HUMAN_ONLY,
        mcp_brick="dnk_finance",
        mcp_tool_name="finance_release_payment",
        input_json_schema={"type": "object", "properties": {"invoice_id": {"type": "string"}}},
        requires_human_confirmation=True,
    )

    @registry.action(spec2)
    def payment_handler(payload, actor="human", origin="ui"):
        return {"authorized": True, "invoice_id": payload.get("invoice_id")}

    # Verify retrieval
    assert registry.get_action_spec("canvas.move_node") == spec1
    assert registry.get_action_spec("billing.release_payment") == spec2

    # Verify filter
    dual_actions = registry.list_actions(ActionSurfaceMode.DUAL)
    assert len(dual_actions) == 1
    assert dual_actions[0].action_id == "canvas.move_node"

    # Verify FastMCP export: Only DUAL and AGENT_ONLY actions should be exported, NOT HUMAN_ONLY
    tools = registry.export_mcp_tools()
    assert len(tools) == 1
    tool = tools[0]
    assert tool["name"] == "canvas_move_node"
    assert tool["metadata"]["action_id"] == "canvas.move_node"
    assert "node_id" in tool["inputSchema"]["properties"]


@pytest.mark.asyncio
async def test_ui_and_agent_dispatch_execution(isolated_registry):
    """Verifies that human in UI and Agent in FastMCP execute the exact same action."""
    registry, bridge, broadcaster = isolated_registry
    sub = await broadcaster.subscribe()

    spec = DualSurfaceActionSpec(
        action_id="task.update_status",
        label_uk="Змінити статус задачі",
        description_en="Updates Kanban task status",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_taskboard",
        mcp_tool_name="update_task_status",
        input_json_schema={"type": "object", "properties": {"task_id": {"type": "string"}, "status": {"type": "string"}}},
    )

    state = {}

    async def update_status_handler(payload, actor="human", origin="ui"):
        state[payload["task_id"]] = payload["status"]
        return {"updated": True, "task_id": payload["task_id"], "new_status": payload["status"], "by": actor}

    registry.register_action(spec, update_status_handler)

    # 1. Dispatch by Human (UI)
    res_ui = await registry.dispatch(
        action_id="task.update_status",
        payload={"task_id": "task-01", "status": "in_progress"},
        actor="Maksym",
        origin="ui",
    )
    assert res_ui.success is True
    assert res_ui.result["new_status"] == "in_progress"
    assert state["task-01"] == "in_progress"

    # Verify broadcast
    evt_ui = await sub.queue.get()
    assert evt_ui.event_type == BusEventType.CANVAS_BATCH_MUTATION
    assert evt_ui.payload["origin"] == "ui"
    assert evt_ui.payload["actor"] == "Maksym"

    # 2. Dispatch by Agent (FastMCP)
    res_agent = await registry.dispatch(
        action_id="task.update_status",
        payload={"task_id": "task-01", "status": "done"},
        actor="denchik",
        origin="agent",
    )
    assert res_agent.success is True
    assert res_agent.result["new_status"] == "done"
    assert state["task-01"] == "done"

    # Verify broadcast
    evt_agent = await sub.queue.get()
    assert evt_agent.payload["origin"] == "agent"
    assert evt_agent.payload["actor"] == "denchik"


@pytest.mark.asyncio
async def test_surface_mode_restrictions(isolated_registry):
    """Verifies that surface mode boundaries (HUMAN_ONLY and AGENT_ONLY) are strictly enforced."""
    registry, bridge, broadcaster = isolated_registry

    # Human-only action
    registry.register_action(
        DualSurfaceActionSpec(
            action_id="admin.wipe_database",
            label_uk="Очистити БД",
            description_en="Purges all local caches",
            surface_mode=ActionSurfaceMode.HUMAN_ONLY,
            mcp_brick="core_admin",
            mcp_tool_name="wipe_db",
        ),
        lambda p, actor="human", origin="ui": {"wiped": True},
    )

    # Agent attempts to execute HUMAN_ONLY action -> Must be rejected
    res_agent = await registry.dispatch(
        action_id="admin.wipe_database",
        payload={},
        actor="denchik",
        origin="agent",
    )
    assert res_agent.success is False
    assert "HUMAN_ONLY" in str(res_agent.error)

    # Agent-only action
    registry.register_action(
        DualSurfaceActionSpec(
            action_id="internal.sync_weights",
            label_uk="Синхронізація ваг",
            description_en="Syncs neural weights",
            surface_mode=ActionSurfaceMode.AGENT_ONLY,
            mcp_brick="core_ai",
            mcp_tool_name="sync_weights",
        ),
        lambda p, actor="agent", origin="agent": {"synced": True},
    )

    # UI attempts to execute AGENT_ONLY action -> Must be rejected
    res_ui = await registry.dispatch(
        action_id="internal.sync_weights",
        payload={},
        actor="Maksym",
        origin="ui",
    )
    assert res_ui.success is False
    assert "AGENT_ONLY" in str(res_ui.error)


@pytest.mark.asyncio
async def test_dangerous_action_hitl_approval_interception(isolated_registry):
    """Verifies that actions marked requires_human_confirmation=True pause and request HITL approval."""
    registry, bridge, broadcaster = isolated_registry
    sub = await broadcaster.subscribe()

    spec = DualSurfaceActionSpec(
        action_id="shopify.publish_theme",
        label_uk="Опублікувати тему на продакшн",
        description_en="Publishes current theme as active live theme on Shopify store",
        surface_mode=ActionSurfaceMode.DUAL,
        mcp_brick="dnk_shopify",
        mcp_tool_name="shopify_publish_theme",
        input_json_schema={"type": "object", "properties": {"theme_id": {"type": "string"}}},
        requires_human_confirmation=True,
    )

    async def publish_handler(payload, actor="human", origin="ui"):
        return {"published": True, "theme_id": payload["theme_id"], "backup": payload.get("backup", False)}

    registry.register_action(spec, publish_handler)

    # Case 1: Human dispatches directly from UI -> Does NOT require HITL since human is clicking it!
    res_ui = await registry.dispatch(
        action_id="shopify.publish_theme",
        payload={"theme_id": "live-theme-001"},
        actor="Maksym",
        origin="ui",
    )
    assert res_ui.success is True
    assert res_ui.requires_approval is False

    # Case 2: Agent dispatches action -> Must pause into HITL ticket queue
    async def _agent_dispatch_coro():
        return await registry.dispatch(
            action_id="shopify.publish_theme",
            payload={"theme_id": "live-theme-002"},
            actor="denchik",
            origin="agent",
            session_id="sess_deploy_01",
            timeout=5.0,
        )

    agent_task = asyncio.create_task(_agent_dispatch_coro())

    # Catch the APPROVAL_REQUESTED event on the stream
    # Note: first event on sub might be the mutation from res_ui
    evt1 = await sub.queue.get()
    if evt1.event_type != BusEventType.APPROVAL_REQUESTED:
        evt1 = await sub.queue.get()

    assert evt1.event_type == BusEventType.APPROVAL_REQUESTED
    ticket_id = evt1.payload["ticket_id"]
    assert ticket_id.startswith("hitl_")

    # Simulate Human reviewing and clicking 1-Click Approve with parameter modification
    resolved = await bridge.resolve_hitl_ticket(
        ticket_id=ticket_id,
        approved=True,
        author="Maksym (Founder)",
        reason="Approved after checking Theme Check score 100/100",
        modifications={"backup": True},
    )
    assert resolved is True

    # Await agent dispatch outcome
    agent_res = await agent_task
    assert agent_res.success is True
    assert agent_res.requires_approval is True
    assert agent_res.ticket_id == ticket_id
    assert agent_res.result["published"] is True
    assert agent_res.result["backup"] is True  # Parameter override was applied!


def test_actions_fastapi_router_endpoints():
    """Verifies FastAPI REST API for action catalog and UI dispatch."""
    from fastapi.testclient import TestClient
    from apps.api.main import app

    client = TestClient(app)

    # 1. Test GET /api/v1/actions
    resp = client.get("/api/v1/actions")
    assert resp.status_code == 200
    actions = resp.json()
    action_ids = [a["action_id"] for a in actions]
    assert "canvas.move_node" in action_ids
    assert "canvas.update_task_status" in action_ids
    assert "canvas.delete_node" in action_ids

    # 2. Test GET /api/v1/actions/mcp-tools
    resp_mcp = client.get("/api/v1/actions/mcp-tools")
    assert resp_mcp.status_code == 200
    tools = resp_mcp.json()
    tool_names = [t["name"] for t in tools]
    assert "canvas_move_node" in tool_names
    assert "update_task_status" in tool_names

    # 3. Test POST /api/v1/actions/dispatch (Valid action from UI)
    dispatch_resp = client.post(
        "/api/v1/actions/dispatch",
        json={
            "action_id": "canvas.move_node",
            "payload": {"node_id": "node_abc", "x": 120.5, "y": 340.0},
            "actor": "Maksym (Tester)",
        },
    )
    assert dispatch_resp.status_code == 200
    data = dispatch_resp.json()
    assert data["success"] is True
    assert data["action_id"] == "canvas.move_node"
    assert data["result"]["status"] == "moved"
    assert data["result"]["node_id"] == "node_abc"

    # 4. Test POST /api/v1/actions/dispatch (Invalid action ID)
    bad_resp = client.post(
        "/api/v1/actions/dispatch",
        json={"action_id": "non_existent.action", "payload": {}},
    )
    assert bad_resp.status_code == 400
    assert "not registered" in bad_resp.json()["detail"]

