# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/audit_log.py"
# purpose: "DNK OS Plugin Audit Log MVP v0.1: append-only immutable audit trail"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator

ALLOWED_EVENT_TYPES: Set[str] = {
    "plugin.intake",
    "plugin.sandbox_run",
    "plugin.certification",
    "plugin.execution_plan_create",
    "plugin.execution_run",
    "plugin.lifecycle_transition",
    "plugin.registry_scan",
}

ALLOWED_ACTORS: Set[str] = {
    "gerych_prime",
    "maksym",
    "system",
}


def validate_relative_path(path: str) -> None:
    """Validate that the given path is strictly relative and does not traverse outside root."""
    if not path:
        raise ValueError("Audit log path cannot be empty")
    if os.path.isabs(path) or path.startswith("/") or path.startswith("\\"):
        raise ValueError(f"Absolute paths forbidden by DNK Invariant: {path}")
    norm = os.path.normpath(path)
    if norm.startswith("..") or "/../" in path or path.startswith("../") or norm == "..":
        raise ValueError(f"Path traversal forbidden by DNK Invariant: {path}")


class AuditEvent(BaseModel):
    """Represents a single immutable plugin lifecycle or execution audit event."""

    event_id: str = ""
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    event_type: str = "plugin.intake"
    plugin_id: str = ""
    actor: str = "gerych_prime"
    details: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        if v not in ALLOWED_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type '{v}'. Allowed event types: {sorted(ALLOWED_EVENT_TYPES)}"
            )
        return v

    @field_validator("actor")
    @classmethod
    def validate_actor(cls, v: str) -> str:
        if v not in ALLOWED_ACTORS:
            raise ValueError(
                f"Invalid actor '{v}'. Allowed actors: {sorted(ALLOWED_ACTORS)}"
            )
        return v


class AuditLog(BaseModel):
    """AuditLog manager model for recording and querying append-only JSONL events."""

    log_path: str = "templates/plugin/audit/audit_log.jsonl"
    events: List[AuditEvent] = Field(default_factory=list)

    @field_validator("log_path")
    @classmethod
    def validate_log_path(cls, v: str) -> str:
        validate_relative_path(v)
        return v

    def append_event(self, event: AuditEvent) -> AuditEvent:
        """Append an AuditEvent to the JSONL log file without rewriting existing history."""
        validate_relative_path(self.log_path)
        if not event.event_id:
            event.event_id = f"evt-{uuid.uuid4().hex[:12]}"

        parent_dir = os.path.dirname(self.log_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        line = json.dumps(event.model_dump())
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        self.events.append(event)
        return event

    def log(
        self,
        event_type: str,
        plugin_id: str,
        actor: str = "gerych_prime",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> AuditEvent:
        """Construct, validate, and append a new audit event."""
        if details is None:
            details = {}
        ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        eid = event_id or f"evt-{uuid.uuid4().hex[:12]}"

        event = AuditEvent(
            event_id=eid,
            timestamp=ts,
            event_type=event_type,
            plugin_id=plugin_id,
            actor=actor,
            details=details,
        )
        return self.append_event(event)

    def load_events(self) -> List[AuditEvent]:
        """Load and parse events from the JSONL log file sorted by timestamp."""
        validate_relative_path(self.log_path)
        if not os.path.exists(self.log_path):
            self.events = []
            return []

        loaded: List[AuditEvent] = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    data = json.loads(clean_line)
                    evt = AuditEvent.model_validate(data)
                    loaded.append(evt)
                except Exception:
                    continue

        # Events ordered chronologically by timestamp
        loaded.sort(key=lambda e: e.timestamp)
        self.events = loaded
        return loaded

    def get_events(self, plugin_id: Optional[str] = None) -> List[AuditEvent]:
        """Retrieve audit events, optionally filtered by plugin_id, ordered by timestamp."""
        all_events = self.load_events()
        if plugin_id is None:
            return all_events
        return [e for e in all_events if e.plugin_id == plugin_id]

    def show(self, plugin_id: str) -> List[AuditEvent]:
        """Alias to retrieve audit events for a specific plugin_id."""
        return self.get_events(plugin_id=plugin_id)

    def tail(self, limit: int = 10) -> List[AuditEvent]:
        """Retrieve the last N events ordered by timestamp."""
        all_events = self.load_events()
        if limit <= 0:
            return []
        return all_events[-limit:]


# Alias for backwards compatibility / class-based naming
PluginAuditLogger = AuditLog
