# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_outbox_worker.py"
# purpose: "Unit tests for Transactional Outbox Worker Daemon & Channel Dispatcher (DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import asyncio
import pytest
from core.outbox.models import OutboxMessage
from core.outbox.service import TransactionalOutbox
from core.outbox.worker import OutboxWorkerDaemon, default_channel_dispatcher


@pytest.mark.asyncio
async def test_drain_once_delivers_pending_messages():
    outbox = TransactionalOutbox(":memory:")
    outbox.enqueue(
        destination_channel="github:dnk-ecom/DNK_OS:101",
        payload={"message": "PR ready for review"}
    )
    outbox.enqueue(
        destination_channel="telegram:dev_team",
        payload="Alert: system health optimal"
    )

    worker = OutboxWorkerDaemon(outbox=outbox)
    dispatched = await worker.drain_once()

    assert len(dispatched) == 2
    assert all(m.status == "delivered" for m in dispatched)

    # Verify persistent state in outbox
    all_msgs = outbox.list_messages()
    assert len(all_msgs) == 2
    assert all(m.status == "delivered" for m in all_msgs)


@pytest.mark.asyncio
async def test_drain_once_with_failing_dispatcher():
    outbox = TransactionalOutbox(":memory:")
    msg = outbox.enqueue(
        destination_channel="network:flaky_destination",
        payload="Telemetry packet"
    )

    async def flaky_sender(m: OutboxMessage) -> bool:
        return False

    worker = OutboxWorkerDaemon(outbox=outbox, dispatcher=flaky_sender)
    dispatched = await worker.drain_once()

    assert len(dispatched) == 1
    assert dispatched[0].status == "pending"
    assert dispatched[0].attempt_count == 1

    stored = outbox.get_receipt(msg.receipt_id)
    assert stored.status == "pending"
    assert stored.attempt_count == 1


@pytest.mark.asyncio
async def test_worker_daemon_clean_stop():
    outbox = TransactionalOutbox(":memory:")
    worker = OutboxWorkerDaemon(outbox=outbox, poll_interval_s=0.1)

    stop_event = asyncio.Event()

    async def _stopper():
        await asyncio.sleep(0.25)
        stop_event.set()

    stopper_task = asyncio.create_task(_stopper())
    daemon_task = asyncio.create_task(worker.run_daemon(stop_event))

    await asyncio.gather(stopper_task, daemon_task)
    assert not worker._is_running


@pytest.mark.asyncio
async def test_default_channel_dispatcher_mock():
    outbox = TransactionalOutbox(":memory:")
    msg_gh = outbox.enqueue("github:owner/repo:42", "Test GitHub dispatch")
    msg_tg = outbox.enqueue("telegram:chat_123", "Test Telegram dispatch")
    msg_generic = outbox.enqueue("custom:channel", {"data": 123})

    assert await default_channel_dispatcher(msg_gh) is True
    assert await default_channel_dispatcher(msg_tg) is True
    assert await default_channel_dispatcher(msg_generic) is True
