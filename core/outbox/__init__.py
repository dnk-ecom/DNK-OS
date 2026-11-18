# --- DNK-MRH-HEADER ---
# mrh_id: "core/outbox/__init__.py"
# purpose: "Package entry point for DNK OS Transactional Outbox (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from core.outbox.models import OutboxMessage
from core.outbox.service import TransactionalOutbox
from core.outbox.worker import OutboxWorkerDaemon, default_channel_dispatcher

__all__ = ["OutboxMessage", "TransactionalOutbox", "OutboxWorkerDaemon", "default_channel_dispatcher"]
