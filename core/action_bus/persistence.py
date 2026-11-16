# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/persistence.py"
# purpose: "SQLite WAL persistence layer for Action Tasks, Results, and Audit Events."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.action_bus.models import (
    ActionExecutionResponse,
    ActionTask,
    ActionTaskStatus,
    ArtifactMetadata,
    BusEvent,
    BusEventType,
)

logger = logging.getLogger("dnk.action_bus.persistence")


class ActionBusPersistence:
    """
    Lightweight, thread-safe, asyncio-friendly SQLite WAL persistence for Action Bus.
    Guarantees state durability across service restarts without external infrastructure.
    """

    def __init__(self, db_path: Union[str, Path] = ".data/mvr_action_bus.db"):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self._initialized = False

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _sync_init_db(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS action_tasks (
                        task_id TEXT PRIMARY KEY,
                        action_type TEXT NOT NULL,
                        plugin_card_path TEXT,
                        payload_json TEXT NOT NULL,
                        tenant_id TEXT NOT NULL,
                        workspace_id TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS action_results (
                        task_id TEXT PRIMARY KEY,
                        status TEXT NOT NULL,
                        exit_code INTEGER NOT NULL,
                        stdout TEXT,
                        stderr TEXT,
                        output_json TEXT,
                        error_message TEXT,
                        execution_time_ms REAL,
                        completed_at TEXT NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES action_tasks (task_id)
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS action_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS action_artifacts (
                        artifact_id TEXT PRIMARY KEY,
                        uri TEXT NOT NULL UNIQUE,
                        filename TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        created_by_agent TEXT,
                        task_id TEXT,
                        checksum_sha256 TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        storage_path TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_artifacts_uri ON action_artifacts (uri);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_artifacts_task_id ON action_artifacts (task_id);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_task_id ON action_events (task_id);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON action_tasks (tenant_id, workspace_id);"
                )
            self._initialized = True

    async def init_db(self) -> None:
        """Initialize tables in background thread."""
        await asyncio.to_thread(self._sync_init_db)

    def _sync_save_task(self, task: ActionTask) -> None:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO action_tasks (
                        task_id, action_type, plugin_card_path, payload_json,
                        tenant_id, workspace_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        task.task_id,
                        task.action_type,
                        task.plugin_card_path,
                        json.dumps(task.payload),
                        task.tenant_id,
                        task.workspace_id,
                        task.created_at,
                    ),
                )

    async def save_task(self, task: ActionTask) -> None:
        if not self._initialized:
            await self.init_db()
        await asyncio.to_thread(self._sync_save_task, task)

    def _sync_get_task(self, task_id: str) -> Optional[ActionTask]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT task_id, action_type, plugin_card_path, payload_json,
                           tenant_id, workspace_id, created_at
                    FROM action_tasks WHERE task_id = ?;
                    """,
                    (task_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return ActionTask(
                    task_id=row["task_id"],
                    action_type=row["action_type"],
                    plugin_card_path=row["plugin_card_path"],
                    payload=json.loads(row["payload_json"]),
                    tenant_id=row["tenant_id"],
                    workspace_id=row["workspace_id"],
                    created_at=row["created_at"],
                )

    async def get_task(self, task_id: str) -> Optional[ActionTask]:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_get_task, task_id)

    def _sync_save_execution_response(self, resp: ActionExecutionResponse) -> None:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO action_results (
                        task_id, status, exit_code, stdout, stderr,
                        output_json, error_message, execution_time_ms, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        resp.task_id,
                        resp.status.value,
                        resp.exit_code,
                        resp.stdout,
                        resp.stderr,
                        json.dumps(resp.output),
                        resp.error_message,
                        resp.execution_time_ms,
                        resp.completed_at,
                    ),
                )

    async def save_execution_response(self, resp: ActionExecutionResponse) -> None:
        if not self._initialized:
            await self.init_db()
        await asyncio.to_thread(self._sync_save_execution_response, resp)

    def _sync_get_execution_response(self, task_id: str) -> Optional[ActionExecutionResponse]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT task_id, status, exit_code, stdout, stderr,
                           output_json, error_message, execution_time_ms, completed_at
                    FROM action_results WHERE task_id = ?;
                    """,
                    (task_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return ActionExecutionResponse(
                    task_id=row["task_id"],
                    status=ActionTaskStatus(row["status"]),
                    exit_code=row["exit_code"],
                    stdout=row["stdout"] or "",
                    stderr=row["stderr"] or "",
                    output=json.loads(row["output_json"]) if row["output_json"] else {},
                    error_message=row["error_message"],
                    execution_time_ms=row["execution_time_ms"] or 0.0,
                    completed_at=row["completed_at"],
                )

    async def get_execution_response(self, task_id: str) -> Optional[ActionExecutionResponse]:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_get_execution_response, task_id)

    def _sync_append_event(self, event: BusEvent) -> None:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO action_events (
                        event_id, event_type, task_id, timestamp, payload_json
                    ) VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        event.event_id,
                        event.event_type.value,
                        event.task_id,
                        event.timestamp,
                        json.dumps(event.payload),
                    ),
                )

    async def append_event(self, event: BusEvent) -> None:
        if not self._initialized:
            await self.init_db()
        await asyncio.to_thread(self._sync_append_event, event)

    def _sync_get_events(
        self, task_id: Optional[str] = None, limit: int = 100
    ) -> List[BusEvent]:
        with self._lock:
            with self._get_connection() as conn:
                if task_id:
                    cur = conn.execute(
                        """
                        SELECT event_id, event_type, task_id, timestamp, payload_json
                        FROM action_events WHERE task_id = ?
                        ORDER BY rowid ASC LIMIT ?;
                        """,
                        (task_id, limit),
                    )
                else:
                    cur = conn.execute(
                        """
                        SELECT event_id, event_type, task_id, timestamp, payload_json
                        FROM action_events
                        ORDER BY rowid ASC LIMIT ?;
                        """,
                        (limit,),
                    )
                rows = cur.fetchall()
                events = []
                for row in rows:
                    events.append(
                        BusEvent(
                            event_id=row["event_id"],
                            event_type=BusEventType(row["event_type"]),
                            task_id=row["task_id"],
                            timestamp=row["timestamp"],
                            payload=json.loads(row["payload_json"]),
                        )
                    )
                return events

    async def get_events(
        self, task_id: Optional[str] = None, limit: int = 100
    ) -> List[BusEvent]:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_get_events, task_id, limit)

    def _sync_save_artifact(self, meta: ArtifactMetadata) -> None:
        if not self._initialized:
            self._sync_init_db()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO action_artifacts (
                        artifact_id, uri, filename, content_type, size_bytes,
                        created_by_agent, task_id, checksum_sha256, created_at, storage_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        meta.artifact_id,
                        meta.uri,
                        meta.filename,
                        meta.content_type,
                        meta.size_bytes,
                        meta.created_by_agent,
                        meta.task_id,
                        meta.checksum_sha256,
                        meta.created_at,
                        meta.storage_path,
                    ),
                )

    async def save_artifact(self, meta: ArtifactMetadata) -> None:
        if not self._initialized:
            await self.init_db()
        await asyncio.to_thread(self._sync_save_artifact, meta)

    def _sync_get_artifact(self, artifact_id_or_uri: str) -> Optional[ArtifactMetadata]:
        if not self._initialized:
            self._sync_init_db()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT artifact_id, uri, filename, content_type, size_bytes,
                           created_by_agent, task_id, checksum_sha256, created_at, storage_path
                    FROM action_artifacts
                    WHERE artifact_id = ? OR uri = ?
                    LIMIT 1;
                    """,
                    (artifact_id_or_uri, artifact_id_or_uri),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return ArtifactMetadata(
                    artifact_id=row["artifact_id"],
                    uri=row["uri"],
                    filename=row["filename"],
                    content_type=row["content_type"],
                    size_bytes=row["size_bytes"],
                    created_by_agent=row["created_by_agent"],
                    task_id=row["task_id"],
                    checksum_sha256=row["checksum_sha256"],
                    created_at=row["created_at"],
                    storage_path=row["storage_path"],
                )

    async def get_artifact(self, artifact_id_or_uri: str) -> Optional[ArtifactMetadata]:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_get_artifact, artifact_id_or_uri)

    def _sync_list_artifacts(
        self, task_id: Optional[str] = None, agent: Optional[str] = None, limit: int = 200
    ) -> List[ArtifactMetadata]:
        if not self._initialized:
            self._sync_init_db()
        with self._lock:
            with self._get_connection() as conn:
                query = (
                    "SELECT artifact_id, uri, filename, content_type, size_bytes, "
                    "created_by_agent, task_id, checksum_sha256, created_at, storage_path "
                    "FROM action_artifacts"
                )
                params: List[Any] = []
                clauses: List[str] = []
                if task_id:
                    clauses.append("task_id = ?")
                    params.append(task_id)
                if agent:
                    clauses.append("created_by_agent = ?")
                    params.append(agent)
                if clauses:
                    query += " WHERE " + " AND ".join(clauses)
                query += " ORDER BY rowid ASC LIMIT ?;"
                params.append(limit)

                cur = conn.execute(query, tuple(params))
                rows = cur.fetchall()
                artifacts = []
                for row in rows:
                    artifacts.append(
                        ArtifactMetadata(
                            artifact_id=row["artifact_id"],
                            uri=row["uri"],
                            filename=row["filename"],
                            content_type=row["content_type"],
                            size_bytes=row["size_bytes"],
                            created_by_agent=row["created_by_agent"],
                            task_id=row["task_id"],
                            checksum_sha256=row["checksum_sha256"],
                            created_at=row["created_at"],
                            storage_path=row["storage_path"],
                        )
                    )
                return artifacts

    async def list_artifacts(
        self, task_id: Optional[str] = None, agent: Optional[str] = None, limit: int = 200
    ) -> List[ArtifactMetadata]:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_list_artifacts, task_id, agent, limit)

    def _sync_delete_artifacts(self, artifact_ids: List[str]) -> int:
        if not self._initialized:
            self._sync_init_db()
        if not artifact_ids:
            return 0
        with self._lock:
            with self._get_connection() as conn:
                placeholders = ",".join("?" for _ in artifact_ids)
                cur = conn.execute(
                    f"DELETE FROM action_artifacts WHERE artifact_id IN ({placeholders});",
                    artifact_ids,
                )
                return cur.rowcount

    async def delete_artifacts(self, artifact_ids: List[str]) -> int:
        if not self._initialized:
            await self.init_db()
        return await asyncio.to_thread(self._sync_delete_artifacts, artifact_ids)

    async def close(self) -> None:
        """Close persistence resources."""
        pass
