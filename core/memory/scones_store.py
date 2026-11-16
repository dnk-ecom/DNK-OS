# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_store.py"
# purpose: "SCONES Cognitive Memory Store with standard library SQLite WAL backend for working memory, episodic logs, and observations."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-24"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
SCONES Cognitive Memory Engine for DNK OS.
Provides asynchronous SQLite WAL-backed persistence for:
1. Working Memory (transient key-value state for active tasks)
2. Episodic Memory (chronological conversation and tool execution history)
3. Observation Store (learned facts, skill calibrations, error solutions)
Uses Python standard library sqlite3 with zero external dependencies.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("dnk.core.memory.scones")


class SconesMemoryStore:
    """
    Standard library SQLite WAL-backed multi-tier cognitive memory implementation.
    Thread-safe and async-compatible.
    Adheres to DNK-STD-0075 and Specs/03_MEMORY_SCONES_SPEC.md.
    """

    def __init__(
        self,
        db_path: Union[str, Path] = ".data/scones_memory.db",
        enable_vitality: bool = True,
    ):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._initialized = False
        self.enable_vitality = enable_vitality
        self._vitality: Optional[Any] = None
        self._overlay: Optional[Any] = None
        self._bm25: Optional[Any] = None
        self._anchor_verifier: Optional[Any] = None

    @property
    def vitality(self) -> Optional[Any]:
        """Provides access to the SCONES Vitality Engine (DEC-045)."""
        if not self.enable_vitality:
            return None
        if self._vitality is None:
            from core.memory.scones_vitality import SconesVitalityEngine

            self._vitality = SconesVitalityEngine(store=self)
        return self._vitality

    @property
    def overlay(self) -> Any:
        """Provides access to the SCONES Working-Tree Diff Overlay Engine."""
        if self._overlay is None:
            from core.memory.scones_overlay import SconesOverlayEngine

            self._overlay = SconesOverlayEngine(repo_root=self.db_path.parent.parent)
        return self._overlay

    @property
    def bm25(self) -> Any:
        """Provides access to the SCONES SQLite FTS5 BM25 Engine."""
        if self._bm25 is None:
            from core.memory.scones_bm25_index import SconesBM25Index

            self._bm25 = SconesBM25Index(db_path=self.db_path, lock=self._lock)
        return self._bm25

    @property
    def anchor_verifier(self) -> Any:
        """Provides access to the SCONES Anchor Verification Engine."""
        if self._anchor_verifier is None:
            from core.memory.scones_anchor_verifier import SconesAnchorVerifier

            self._anchor_verifier = SconesAnchorVerifier(repo_root=self.db_path.parent.parent)
        return self._anchor_verifier

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _sync_initialize(self) -> None:
        if self._initialized:
            return
        with self._lock:
            with self._get_connection() as conn:
                # 1. Working memory table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_working_memory (
                        session_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value_json TEXT NOT NULL,
                        updated_at REAL NOT NULL,
                        PRIMARY KEY (session_id, key)
                    );
                    """
                )
                # 2. Episodic memory table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_episodic_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata_json TEXT,
                        created_at REAL NOT NULL
                    );
                    """
                )
                # 3. Observations and knowledge store
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_observations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        observation TEXT NOT NULL,
                        source TEXT NOT NULL,
                        confidence REAL NOT NULL DEFAULT 1.0,
                        created_at REAL NOT NULL
                    );
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_obs_topic ON scones_observations(topic);"
                )
                conn.commit()
            self._initialized = True
            logger.info(f"SCONES Memory Store initialized at {self.db_path} (WAL mode).")

    async def initialize(self) -> None:
        """Initializes the database schema asynchronously."""
        await asyncio.to_thread(self._sync_initialize)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self._sync_initialize()

    # -------------------------------------------------------------------------
    # Working Memory Tier
    # -------------------------------------------------------------------------
    def _sync_set_working_memory(self, session_id: str, key: str, value: Any) -> None:
        self._ensure_initialized()
        val_str = json.dumps(value, ensure_ascii=False)
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO scones_working_memory (session_id, key, value_json, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(session_id, key) DO UPDATE SET
                        value_json = excluded.value_json,
                        updated_at = excluded.updated_at;
                    """,
                    (session_id, key, val_str, now),
                )
                conn.commit()

    async def set_working_memory(self, session_id: str, key: str, value: Any) -> None:
        """Stores a key-value pair in working memory."""
        await asyncio.to_thread(self._sync_set_working_memory, session_id, key, value)

    def _sync_get_working_memory(self, session_id: str, key: str) -> Optional[Any]:
        self._ensure_initialized()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value_json FROM scones_working_memory WHERE session_id = ? AND key = ?;",
                (session_id, key),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row["value_json"])
        return None

    async def get_working_memory(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieves a value from working memory."""
        return await asyncio.to_thread(self._sync_get_working_memory, session_id, key)

    # -------------------------------------------------------------------------
    # Episodic Memory Tier
    # -------------------------------------------------------------------------
    def _sync_append_episodic(
        self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        self._ensure_initialized()
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO scones_episodic_logs (session_id, role, content, metadata_json, created_at)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (session_id, role, content, meta_str, now),
                )
                conn.commit()
                return cursor.lastrowid or 0

    async def append_episodic(
        self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Appends a turn to the episodic trajectory log."""
        return await asyncio.to_thread(
            self._sync_append_episodic, session_id, role, content, metadata
        )

    def _sync_get_recent_episodes(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, role, content, metadata_json, created_at
                FROM scones_episodic_logs
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?;
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
            results = []
            for r in reversed(rows):
                results.append(
                    {
                        "id": r["id"],
                        "role": r["role"],
                        "content": r["content"],
                        "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {},
                        "created_at": r["created_at"],
                    }
                )
            return results

    async def get_recent_episodes(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent episodes for a given session."""
        return await asyncio.to_thread(self._sync_get_recent_episodes, session_id, limit)

    # -------------------------------------------------------------------------
    # Long-term Observations & SCONES Knowledge Tier
    # -------------------------------------------------------------------------
    def _sync_record_observation(
        self, topic: str, observation: str, source: str = "agent", confidence: float = 1.0
    ) -> int:
        self._ensure_initialized()
        now = time.time()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO scones_observations (topic, observation, source, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (topic.lower().strip(), observation, source, confidence, now),
                )
                conn.commit()
                obs_id = cursor.lastrowid or 0
                if self.enable_vitality and obs_id and self.vitality is not None:
                    try:
                        self.vitality.track_access(str(obs_id), utility_delta=1.0)
                    except Exception as e:
                        logger.warning(f"Failed to track vitality for observation {obs_id}: {e}")
                return obs_id

    async def record_observation(
        self, topic: str, observation: str, source: str = "agent", confidence: float = 1.0
    ) -> int:
        """Records a verified observation or skill adjustment."""
        return await asyncio.to_thread(
            self._sync_record_observation, topic, observation, source, confidence
        )

    def _sync_query_memories(
        self,
        topic: str,
        limit: int = 5,
        min_vitality: Optional[float] = None,
        track_access: bool = False,
        now: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        search_pattern = f"%{topic.lower().strip()}%"
        fetch_limit = limit * 2 if min_vitality is not None else limit
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, topic, observation, source, confidence, created_at
                FROM scones_observations
                WHERE topic LIKE ?
                ORDER BY id DESC LIMIT ?;
                """,
                (search_pattern, fetch_limit),
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                fact_id = str(r["id"])
                vitality_score = 1.0
                if self.enable_vitality and self.vitality is not None:
                    vitality_score = self.vitality.calculate_decay(fact_id, now=now)
                    if min_vitality is not None and vitality_score < min_vitality:
                        continue
                    if track_access:
                        self.vitality.track_access(fact_id, utility_delta=0.2, now=now)
                        vitality_score = self.vitality.calculate_decay(fact_id, now=now)
                results.append(
                    {
                        "id": r["id"],
                        "topic": r["topic"],
                        "observation": r["observation"],
                        "source": r["source"],
                        "confidence": r["confidence"],
                        "vitality_score": vitality_score,
                        "created_at": r["created_at"],
                    }
                )
                if len(results) >= limit:
                    break
            return results

    async def query_memories(
        self,
        topic: str,
        limit: int = 5,
        min_vitality: Optional[float] = None,
        track_access: bool = False,
        now: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Queries recorded observations matching a topic substring with optional vitality filtering."""
        return await asyncio.to_thread(
            self._sync_query_memories, topic, limit, min_vitality, track_access, now
        )

    def prune_dead_facts(
        self, min_vitality: float = 0.1, now: Optional[float] = None
    ) -> List[str]:
        """Prunes dead facts from vitality index and observation store."""
        if self.enable_vitality and self.vitality is not None:
            return self.vitality.prune_dead_facts(min_vitality=min_vitality, now=now)
        return []

    async def prune_dead_facts_async(
        self, min_vitality: float = 0.1, now: Optional[float] = None
    ) -> List[str]:
        """Asynchronously prunes dead facts."""
        return await asyncio.to_thread(self.prune_dead_facts, min_vitality, now)

    async def close(self) -> None:
        """No-op for connection-per-operation SQLite pattern."""
        pass
