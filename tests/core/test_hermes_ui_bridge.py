# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_hermes_ui_bridge.py"
# purpose: "Unit verification suite for HermesUIBridge and Astryx real-time streaming integration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import asyncio
import pytest
from core.adapters.hermes_ui_bridge import HermesUIBridge
from core.action_bus.broadcaster import EventBroadcaster
from core.action_bus.models import BusEventType


@pytest.fixture
def bridge():
    """Isolated HermesUIBridge with dedicated broadcaster."""
    broadcaster = EventBroadcaster()
    return HermesUIBridge(broadcaster=broadcaster)


@pytest.mark.asyncio
async def test_publish_agent_thought_broadcast(bridge):
    """Verifies thought stream broadcasting to subscribed clients."""
    sub = await bridge.broadcaster.subscribe()

    env = bridge.publish_agent_thought(
        session_id="sess_001",
        agent="denchik",
        thought="Compiling FastMCP AST tree...",
        step=1,
    )
    assert env.agent == "denchik"
    assert env.task_id == "sess_001"

    received = await sub.queue.get()
    assert received.event_id == env.event_id
    assert received.payload["kind"] == "thought_stream"
    assert received.payload["content"] == "Compiling FastMCP AST tree..."
    assert received.payload["step"] == 1


@pytest.mark.asyncio
async def test_tool_start_and_complete_lifecycle(bridge):
    """Verifies tool start and completion envelopes with exit codes."""
    sub = await bridge.broadcaster.subscribe()

    # Tool start
    start_env = bridge.publish_tool_start(
        session_id="sess_002",
        agent="denchik",
        tool_name="patch_file",
        tool_args={"path": "core/kernel.py", "diff": "+# test"},
        tool_call_id="call_abc123",
    )
    assert start_env.payload["kind"] == "tool_start"
    assert start_env.payload["tool_call_id"] == "call_abc123"

    # Tool complete
    comp_env = bridge.publish_tool_complete(
        session_id="sess_002",
        agent="denchik",
        tool_name="patch_file",
        result="File patched successfully",
        tool_call_id="call_abc123",
        exit_code=0,
        duration_ms=45.2,
    )
    assert comp_env.event_type == BusEventType.TASK_COMPLETED
    assert comp_env.payload["success"] is True
    assert comp_env.payload["exit_code"] == 0

    # Pop both from subscriber queue
    q_start = await sub.queue.get()
    q_comp = await sub.queue.get()
    assert q_start.payload["tool_call_id"] == "call_abc123"
    assert q_comp.payload["tool_call_id"] == "call_abc123"


@pytest.mark.asyncio
async def test_plan_update_broadcast(bridge):
    """Verifies plan DAG mutations broadcast to living canvas."""
    sub = await bridge.broadcaster.subscribe()

    plan_items = [
        {"id": "step_1", "title": "Analyze contracts", "status": "completed"},
        {"id": "step_2", "title": "Implement adapter", "status": "in_progress"},
    ]
    env = bridge.publish_plan_update(
        session_id="sess_003",
        agent="gerych_prime",
        plan_entries=plan_items,
        title="Sovereign Migration Plan",
    )
    assert env.event_type == BusEventType.CANVAS_BATCH_MUTATION
    assert env.payload["entry_count"] == 2

    received = await sub.queue.get()
    assert received.payload["title"] == "Sovereign Migration Plan"
    assert len(received.payload["entries"]) == 2


@pytest.mark.asyncio
async def test_non_blocking_hitl_approval_flow(bridge):
    """Verifies asynchronous HITL request and 1-Click resolution."""
    sub = await bridge.broadcaster.subscribe()

    async def _simulate_agent():
        approved, res = await bridge.request_hitl_approval_async(
            session_id="sess_004",
            agent="denchik",
            action_type="delete_legacy_route",
            details={"route": "/api/v1/deprecated"},
            timeout=5.0,
        )
        return approved, res

    agent_task = asyncio.create_task(_simulate_agent())

    # Wait for approval request on stream
    req_env = await sub.queue.get()
    assert req_env.event_type == BusEventType.APPROVAL_REQUESTED
    ticket_id = req_env.payload["ticket_id"]
    assert ticket_id.startswith("hitl_")

    # Simulate UI clicking 1-Click Approve with modifications
    success = await bridge.resolve_hitl_ticket(
        ticket_id=ticket_id,
        approved=True,
        author="Maksym",
        reason="Approved for Astryx UI migration",
        modifications={"backup": True},
    )
    assert success is True

    # Await agent resolution
    approved, resolution = await agent_task
    assert approved is True
    assert resolution["author"] == "Maksym"
    assert resolution["modifications"] == {"backup": True}

    # Verify resolution event was also broadcasted to UI
    res_env = await sub.queue.get()
    assert res_env.event_type == BusEventType.APPROVAL_RESOLVED
    assert res_env.payload["ticket_id"] == ticket_id


@pytest.mark.asyncio
async def test_acp_bridge_callbacks_integration(bridge):
    """Verifies factory callbacks properly map to Hermes execution hooks."""
    sub = await bridge.broadcaster.subscribe()

    callbacks = bridge.create_acp_bridge_callbacks("sess_005", "antigravity")
    assert "on_thought" in callbacks
    assert "on_tool_start" in callbacks
    assert "on_tool_complete" in callbacks
    assert "on_plan_update" in callbacks
    assert "on_status_change" in callbacks

    # Trigger thought callback
    callbacks["on_thought"]("Reviewing architecture decisions...", 2)

    received = await sub.queue.get()
    assert received.agent == "antigravity"
    assert received.payload["content"] == "Reviewing architecture decisions..."
    assert received.payload["step"] == 2


@pytest.mark.asyncio
async def test_publish_taskboard_mutation(bridge):
    """Verifies taskboard status change event broadcasts to living canvas."""
    sub = await bridge.broadcaster.subscribe()

    env = bridge.publish_taskboard_mutation(
        task_id="task-999",
        new_status="in_progress",
        agent="denchik",
        execution_logs="Started atomic slice #1",
    )
    assert env.event_type == BusEventType.CANVAS_BATCH_MUTATION

    received = await sub.queue.get()
    assert received.payload["kind"] == "taskboard_mutation"
    assert received.payload["task_id"] == "task-999"
    assert received.payload["new_status"] == "in_progress"
    assert received.payload["execution_logs"] == "Started atomic slice #1"
