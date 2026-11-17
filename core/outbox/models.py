# --- DNK-MRH-HEADER ---
# mrh_id: "core/outbox/models.py"
# purpose: "Unified Outbox Pydantic SSOT machine models for transactional messaging & receipts (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import time
import uuid
from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class OutboxMessage(BaseModel):
    """
    Transactional Outbox Message entity with persistent receipt.
    Guarantees zero lost messages across network drops or host restarts.
    """
    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    receipt_id: str = Field(default_factory=lambda: f"rcpt_{uuid.uuid4().hex[:10]}")
    idempotency_key: str = Field(..., description="Unique key for deduplication and replay prevention")
    destination_channel: str = Field(..., description="Target channel (e.g. github:issue:12, telegram:chat:1)")
    payload: Union[Dict[str, Any], str] = Field(..., description="Message content or event dictionary")
    status: Literal["pending", "in_flight", "delivered", "failed", "dropped"] = "pending"
    attempt_count: int = 0
    max_attempts: int = 5
    created_at_epoch: float = Field(default_factory=time.time)
    last_attempt_epoch: Optional[float] = None
    delivered_at_epoch: Optional[float] = None
    next_retry_epoch: float = Field(default_factory=time.time)
    last_error: Optional[str] = None
