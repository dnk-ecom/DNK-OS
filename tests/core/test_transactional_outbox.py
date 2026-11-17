# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_transactional_outbox.py"
# purpose: "Unit tests for Transactional Outbox Service and Receipts (DEC-151)."
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
from core.outbox.service import TransactionalOutbox


@pytest.mark.asyncio
async def test_outbox_enqueue_and_receipt():
    outbox = TransactionalOutbox(":memory:")

    msg = outbox.enqueue(
        destination_channel="github:issues:105",
        payload={"event": "pr_ready", "pr_url": "https://github.com/org/repo/pull/1"},
        idempotency_key="idemp_key_001"
    )

    assert msg.receipt_id.startswith("rcpt_")
    assert msg.status == "pending"
    assert msg.attempt_count == 0

    # Retrieve by receipt
    fetched = outbox.get_receipt(msg.receipt_id)
    assert fetched is not None
    assert fetched.message_id == msg.message_id
    assert fetched.payload == {"event": "pr_ready", "pr_url": "https://github.com/org/repo/pull/1"}


@pytest.mark.asyncio
async def test_outbox_idempotent_deduplication():
    outbox = TransactionalOutbox(":memory:")

    msg1 = outbox.enqueue(
        destination_channel="telegram:channel:dev",
        payload="Alert: Build finished",
        idempotency_key="unique_evt_123"
    )

    # Second enqueue with same idempotency key
    msg2 = outbox.enqueue(
        destination_channel="telegram:channel:dev",
        payload="Alert: Build finished (duplicate)",
        idempotency_key="unique_evt_123"
    )

    # Must return exact same message and receipt
    assert msg1.message_id == msg2.message_id
    assert msg1.receipt_id == msg2.receipt_id

    # Total stored messages must be 1
    all_msgs = outbox.list_messages()
    assert len(all_msgs) == 1


@pytest.mark.asyncio
async def test_outbox_successful_dispatch():
    outbox = TransactionalOutbox(":memory:")

    msg = outbox.enqueue(
        destination_channel="feishu:group:ops",
        payload={"status": "ok"}
    )

    delivered_payloads = []

    async def mock_sender(m):
        delivered_payloads.append(m.payload)
        return True

    dispatched = await outbox.dispatch_pending(mock_sender)
    assert len(dispatched) == 1
    assert dispatched[0].status == "delivered"
    assert len(delivered_payloads) == 1

    # Check database state
    stored = outbox.get_receipt(msg.receipt_id)
    assert stored.status == "delivered"
    assert stored.delivered_at_epoch is not None


@pytest.mark.asyncio
async def test_outbox_exponential_backoff_and_failure():
    outbox = TransactionalOutbox(":memory:")

    msg = outbox.enqueue(
        destination_channel="github:pulls:2",
        payload="Comment text",
        max_attempts=2
    )

    async def failing_sender(m):
        raise ConnectionResetError("GitHub API timeout")

    # Attempt 1: Should fail and schedule retry
    res1 = await outbox.dispatch_pending(failing_sender, base_backoff_s=0.2)
    assert len(res1) == 1
    assert res1[0].status == "pending"
    assert res1[0].attempt_count == 1
    assert "GitHub API timeout" in res1[0].last_error

    # Wait for backoff delay (0.2s)
    await asyncio.sleep(0.25)

    # Attempt 2: Exceeds max_attempts=2 -> status becomes 'failed'
    res2 = await outbox.dispatch_pending(failing_sender, base_backoff_s=0.2)
    assert len(res2) == 1
    assert res2[0].status == "failed"
    assert res2[0].attempt_count == 2
