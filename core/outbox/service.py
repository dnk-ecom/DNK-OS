# --- DNK-MRH-HEADER ---
# mrh_id: "core/outbox/service.py"
# purpose: "Transactional Outbox Service providing persistent receipts and exponential backoff dispatch (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from core.outbox.models import OutboxMessage

logger = logging.getLogger("dnk.outbox.service")


class TransactionalOutbox:
    """
    Transactional Outbox Service implementing SOTA DSH Reliability (DEC-151).
    Stores message and receipt in SQLite transaction before external transmission.
    Guarantees FIFO channel delivery, exponential backoff, and idempotent deduplication.
    """

    def __init__(self, db_path: Union[str, Path] = ":memory:") -> None:
        self.db_path = str(db_path)
        self._shared_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
        else:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outbox_messages (
                    message_id TEXT PRIMARY KEY,
                    receipt_id TEXT UNIQUE NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    destination_channel TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempt_count INTEGER NOT NULL,
                    max_attempts INTEGER NOT NULL,
                    created_at_epoch REAL NOT NULL,
                    last_attempt_epoch REAL,
                    delivered_at_epoch REAL,
                    next_retry_epoch REAL NOT NULL,
                    last_error TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_status_retry ON outbox_messages(status, next_retry_epoch)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outbox_channel ON outbox_messages(destination_channel)")
            conn.commit()

    def enqueue(
        self,
        destination_channel: str,
        payload: Union[Dict[str, Any], str],
        idempotency_key: Optional[str] = None,
        max_attempts: int = 5
    ) -> OutboxMessage:
        """
        Atomically enqueue message and generate receipt before external write.
        If idempotency_key is already present, returns existing message (no duplication).
        """
        key = idempotency_key or f"auto_{uuid.uuid4().hex}"
        now = time.time()

        with self._get_connection() as conn:
            # Check existing idempotency key
            cursor = conn.execute(
                "SELECT * FROM outbox_messages WHERE idempotency_key = ?",
                (key,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_model(row)

            # Insert new record
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            receipt_id = f"rcpt_{uuid.uuid4().hex[:10]}"
            payload_json = json.dumps(payload) if isinstance(payload, dict) else payload

            conn.execute("""
                INSERT INTO outbox_messages (
                    message_id, receipt_id, idempotency_key, destination_channel,
                    payload, status, attempt_count, max_attempts, created_at_epoch,
                    last_attempt_epoch, delivered_at_epoch, next_retry_epoch, last_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id, receipt_id, key, destination_channel,
                payload_json, "pending", 0, max_attempts, now,
                None, None, now, None
            ))
            conn.commit()

            return OutboxMessage(
                message_id=message_id,
                receipt_id=receipt_id,
                idempotency_key=key,
                destination_channel=destination_channel,
                payload=payload,
                status="pending",
                attempt_count=0,
                max_attempts=max_attempts,
                created_at_epoch=now,
                next_retry_epoch=now
            )

    def get_receipt(self, receipt_id: str) -> Optional[OutboxMessage]:
        """Fetch message by receipt ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM outbox_messages WHERE receipt_id = ?",
                (receipt_id,)
            )
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def list_messages(self, status: Optional[str] = None, limit: int = 50) -> List[OutboxMessage]:
        """List messages, optionally filtered by status."""
        with self._get_connection() as conn:
            if status:
                cursor = conn.execute(
                    "SELECT * FROM outbox_messages WHERE status = ? ORDER BY created_at_epoch DESC LIMIT ?",
                    (status, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM outbox_messages ORDER BY created_at_epoch DESC LIMIT ?",
                    (limit,)
                )
            return [self._row_to_model(row) for row in cursor.fetchall()]

    async def dispatch_pending(
        self,
        sender_fn: Callable[[OutboxMessage], Awaitable[bool]],
        base_backoff_s: float = 2.0,
        max_backoff_s: float = 300.0
    ) -> List[OutboxMessage]:
        """
        Process pending messages whose next_retry_epoch has arrived.
        Calls sender_fn(message) -> bool.
        On success: transitions to 'delivered'.
        On failure: applies exponential backoff: base * (2 ** attempts), up to max_backoff_s.
        """
        now = time.time()
        dispatched: List[OutboxMessage] = []

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM outbox_messages WHERE status = 'pending' AND next_retry_epoch <= ? ORDER BY created_at_epoch ASC",
                (now,)
            )
            rows = cursor.fetchall()

        for row in rows:
            msg = self._row_to_model(row)
            attempt = msg.attempt_count + 1
            attempt_time = time.time()

            try:
                success = await sender_fn(msg)
                if success:
                    self._update_status(
                        msg.message_id,
                        status="delivered",
                        attempt_count=attempt,
                        last_attempt_epoch=attempt_time,
                        delivered_at_epoch=attempt_time,
                        last_error=None
                    )
                    msg.status = "delivered"
                    msg.delivered_at_epoch = attempt_time
                else:
                    self._handle_failure(msg, attempt, attempt_time, base_backoff_s, max_backoff_s, "Sender returned False")
            except Exception as ex:
                self._handle_failure(msg, attempt, attempt_time, base_backoff_s, max_backoff_s, str(ex))

            dispatched.append(msg)

        return dispatched

    def _handle_failure(
        self,
        msg: OutboxMessage,
        attempt: int,
        attempt_time: float,
        base_backoff: float,
        max_backoff: float,
        error_msg: str
    ) -> None:
        if attempt >= msg.max_attempts:
            new_status = "failed"
            next_retry = attempt_time + 999999.0
        else:
            new_status = "pending"
            delay = min(max_backoff, base_backoff * (2 ** (attempt - 1)))
            next_retry = attempt_time + delay

        self._update_status(
            msg.message_id,
            status=new_status,
            attempt_count=attempt,
            last_attempt_epoch=attempt_time,
            next_retry_epoch=next_retry,
            last_error=error_msg
        )
        msg.status = new_status
        msg.attempt_count = attempt
        msg.last_error = error_msg
        msg.next_retry_epoch = next_retry

    def _update_status(
        self,
        message_id: str,
        status: str,
        attempt_count: int,
        last_attempt_epoch: float,
        delivered_at_epoch: Optional[float] = None,
        next_retry_epoch: Optional[float] = None,
        last_error: Optional[str] = None
    ) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE outbox_messages SET
                    status = ?,
                    attempt_count = ?,
                    last_attempt_epoch = ?,
                    delivered_at_epoch = COALESCE(?, delivered_at_epoch),
                    next_retry_epoch = COALESCE(?, next_retry_epoch),
                    last_error = ?
                WHERE message_id = ?
            """, (
                status, attempt_count, last_attempt_epoch,
                delivered_at_epoch, next_retry_epoch, last_error, message_id
            ))
            conn.commit()

    def _row_to_model(self, row: sqlite3.Row) -> OutboxMessage:
        raw_payload = row["payload"]
        try:
            payload = json.loads(raw_payload)
        except Exception:
            payload = raw_payload

        return OutboxMessage(
            message_id=row["message_id"],
            receipt_id=row["receipt_id"],
            idempotency_key=row["idempotency_key"],
            destination_channel=row["destination_channel"],
            payload=payload,
            status=row["status"],
            attempt_count=row["attempt_count"],
            max_attempts=row["max_attempts"],
            created_at_epoch=row["created_at_epoch"],
            last_attempt_epoch=row["last_attempt_epoch"],
            delivered_at_epoch=row["delivered_at_epoch"],
            next_retry_epoch=row["next_retry_epoch"],
            last_error=row["last_error"]
        )
