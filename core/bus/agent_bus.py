# --- DNK-MRH-HEADER ---
# mrh_id: "core/bus/agent_bus.py"
# purpose: "Inter-Agent Action Bus & TaskDNA Event Dispatcher for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class DNKAgentBus:
    """
    Sovereign Inter-Agent Communication Bus.
    Supports in-process pub/sub, SQLite WAL event log, and task delegation.
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            self.db_path = Path(__file__).resolve().parent.parent.parent / "data" / "agent_bus.sqlite"
        else:
            self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_events (
                    id TEXT PRIMARY KEY,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def subscribe(self, event_type: str, handler: Callable[[AgentMessage], None]) -> None:
        """Registers a callback handler for an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, sender: str, recipient: str, event_type: str, payload: Dict[str, Any]) -> AgentMessage:
        """Publishes an event to subscribers and records to SQLite WAL."""
        msg = AgentMessage(
            sender=sender,
            recipient=recipient,
            event_type=event_type,
            payload=payload,
        )
        with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
            conn.execute(
                "INSERT INTO agent_events (id, sender, recipient, event_type, payload, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (msg.id, msg.sender, msg.recipient, msg.event_type, json.dumps(msg.payload), msg.timestamp)
            )
            conn.commit()

        # Trigger in-process handlers
        handlers = self._subscribers.get(event_type, []) + self._subscribers.get("*", [])
        for h in handlers:
            try:
                h(msg)
            except Exception as e:
                print(f"⚠️ Error in event handler for {event_type}: {e}")

        return msg

    def get_recent_events(self, limit: int = 50) -> List[AgentMessage]:
        """Fetches the latest events from the WAL event log."""
        messages = []
        with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, sender, recipient, event_type, payload, timestamp FROM agent_events ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            for row in cursor.fetchall():
                messages.append(AgentMessage(
                    id=row[0],
                    sender=row[1],
                    recipient=row[2],
                    event_type=row[3],
                    payload=json.loads(row[4]),
                    timestamp=row[5],
                ))
        return messages


# Singleton instance
agent_bus = DNKAgentBus()
