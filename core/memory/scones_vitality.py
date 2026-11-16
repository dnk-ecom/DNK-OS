# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_vitality.py"
# purpose: "SCONES Vitality Receipts & Knowledge Pruning Engine for long-term cognitive memory."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
SCONES Vitality Receipts & Knowledge Pruning Engine (DEC-045).
Tracks access utility, exponential time-based decay, and automated pruning
of stale facts and observations to prevent cognitive graveyards and context bloat.
"""

import asyncio
import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from core.memory.scones_store import SconesMemoryStore

logger = logging.getLogger("dnk.core.memory.vitality")


class SconesVitalityEngine:
    """
    SCONES Vitality Engine.
    Implements utility receipt tracking, exponential half-life decay, and dead-fact pruning.
    Can operate attached to a SconesMemoryStore or standalone with SQLite.
    """

    def __init__(
        self,
        store: Optional["SconesMemoryStore"] = None,
        db_path: Optional[Union[str, Path]] = None,
        half_life_days: float = 14.0,
    ) -> None:
        self.store = store
        self.half_life_days = float(half_life_days)
        self._lock = store._lock if store is not None else threading.RLock()
        self._mem_conn: Optional[sqlite3.Connection] = None
        self._initialized = False

        if store is not None:
            self.db_path = store.db_path
        elif db_path is not None:
            self.db_path = Path(db_path) if str(db_path) != ":memory:" else Path(":memory:")
        else:
            self.db_path = Path(".data/scones_vitality.db")

        self._ensure_initialized()

    def _get_connection(self) -> sqlite3.Connection:
        if self.store is not None:
            return self.store._get_connection()

        if str(self.db_path) == ":memory:":
            if self._mem_conn is None:
                self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
                self._mem_conn.row_factory = sqlite3.Row
            return self._mem_conn

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
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_vitality_receipts (
                        fact_id TEXT PRIMARY KEY,
                        vitality_score REAL NOT NULL DEFAULT 1.0,
                        access_count INTEGER NOT NULL DEFAULT 1,
                        last_accessed_at REAL NOT NULL,
                        created_at REAL NOT NULL,
                        half_life_days REAL NOT NULL DEFAULT 14.0,
                        metadata_json TEXT
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_vitality_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fact_id TEXT NOT NULL,
                        delta REAL NOT NULL,
                        resulting_vitality REAL NOT NULL,
                        task_hash TEXT,
                        timestamp REAL NOT NULL,
                        metadata_json TEXT
                    );
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_vitality_fact_id ON scones_vitality_receipts(fact_id);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_vitality_score ON scones_vitality_receipts(vitality_score);"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_vitality_logs_fact ON scones_vitality_logs(fact_id);"
                )
                conn.commit()
            self._initialized = True
            logger.info("SCONES Vitality Engine initialized.")

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self._sync_initialize()

    # -------------------------------------------------------------------------
    # Core Vitality Tracking & Decay Calculations
    # -------------------------------------------------------------------------
    def track_access(
        self,
        fact_id: str,
        utility_delta: float = 1.0,
        task_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        now: Optional[float] = None,
    ) -> None:
        """
        Records or updates access to a fact, adding utility_delta to its decayed vitality.
        Stores an immutable vitality receipt for audit and telemetry.
        """
        self._ensure_initialized()
        current_time = float(now if now is not None else time.time())
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT vitality_score, access_count, last_accessed_at, half_life_days FROM scones_vitality_receipts WHERE fact_id = ?;",
                    (str(fact_id),),
                )
                row = cursor.fetchone()

                if row:
                    last_score = float(row["vitality_score"])
                    last_accessed = float(row["last_accessed_at"])
                    h_life = float(row["half_life_days"]) or self.half_life_days
                    elapsed_days = (current_time - last_accessed) / 86400.0
                    decay_factor = (2.0 ** (-elapsed_days / h_life)) if elapsed_days > 0 else 1.0
                    decayed_score = max(0.0, last_score * decay_factor)
                    new_score = round(decayed_score + float(utility_delta), 6)
                    new_count = int(row["access_count"]) + 1

                    conn.execute(
                        """
                        UPDATE scones_vitality_receipts
                        SET vitality_score = ?,
                            access_count = ?,
                            last_accessed_at = ?,
                            metadata_json = ?
                        WHERE fact_id = ?;
                        """,
                        (new_score, new_count, current_time, meta_str, str(fact_id)),
                    )
                else:
                    new_score = round(float(utility_delta) if utility_delta > 0 else 1.0, 6)
                    new_count = 1
                    conn.execute(
                        """
                        INSERT INTO scones_vitality_receipts (
                            fact_id, vitality_score, access_count, last_accessed_at, created_at, half_life_days, metadata_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            str(fact_id),
                            new_score,
                            new_count,
                            current_time,
                            current_time,
                            self.half_life_days,
                            meta_str,
                        ),
                    )

                conn.execute(
                    """
                    INSERT INTO scones_vitality_logs (
                        fact_id, delta, resulting_vitality, task_hash, timestamp, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        str(fact_id),
                        float(utility_delta),
                        new_score,
                        task_hash,
                        current_time,
                        meta_str,
                    ),
                )
                conn.commit()

    def calculate_decay(
        self,
        fact_id: str,
        half_life_days: float = 14.0,
        now: Optional[float] = None,
    ) -> float:
        """
        Calculates the current decayed vitality score of a fact without mutating the store.
        Returns 0.0 if the fact does not exist.
        """
        self._ensure_initialized()
        current_time = float(now if now is not None else time.time())
        h_life = float(half_life_days) if half_life_days > 0 else self.half_life_days

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT vitality_score, last_accessed_at FROM scones_vitality_receipts WHERE fact_id = ?;",
                    (str(fact_id),),
                )
                row = cursor.fetchone()
                if not row:
                    return 0.0

                stored_score = float(row["vitality_score"])
                last_accessed = float(row["last_accessed_at"])
                elapsed_days = (current_time - last_accessed) / 86400.0

                if elapsed_days <= 0:
                    return stored_score

                decay_factor = 2.0 ** (-elapsed_days / h_life)
                decayed = max(0.0, stored_score * decay_factor)
                return round(decayed, 6)

    def prune_dead_facts(
        self,
        min_vitality: float = 0.1,
        now: Optional[float] = None,
    ) -> List[str]:
        """
        Evaluates all tracked facts against min_vitality threshold.
        Deletes facts below the threshold from vitality receipts and backing SCONES store (if attached).
        Returns list of pruned fact IDs.
        """
        self._ensure_initialized()
        current_time = float(now if now is not None else time.time())
        min_thresh = float(min_vitality)
        pruned: List[str] = []

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT fact_id, vitality_score, last_accessed_at, half_life_days FROM scones_vitality_receipts;"
                )
                rows = cursor.fetchall()

                for r in rows:
                    fid = str(r["fact_id"])
                    stored_score = float(r["vitality_score"])
                    last_accessed = float(r["last_accessed_at"])
                    h_life = float(r["half_life_days"]) or self.half_life_days
                    elapsed_days = (current_time - last_accessed) / 86400.0

                    decay_factor = (2.0 ** (-elapsed_days / h_life)) if elapsed_days > 0 else 1.0
                    decayed = max(0.0, stored_score * decay_factor)

                    if decayed < min_thresh:
                        pruned.append(fid)

                for fid in pruned:
                    conn.execute(
                        "DELETE FROM scones_vitality_receipts WHERE fact_id = ?;",
                        (fid,),
                    )
                    # If backing store is attached, clean up from scones_observations
                    if self.store is not None:
                        try:
                            if fid.isdigit():
                                conn.execute(
                                    "DELETE FROM scones_observations WHERE id = ?;",
                                    (int(fid),),
                                )
                            else:
                                conn.execute(
                                    "DELETE FROM scones_observations WHERE id = ?;",
                                    (fid,),
                                )
                        except sqlite3.OperationalError:
                            # In case scones_observations is not in this database
                            pass

                conn.commit()

        if pruned:
            logger.info(f"SCONES Vitality Engine pruned {len(pruned)} dead facts: {pruned}")
        return pruned

    def get_vitality_receipt(self, fact_id: str, now: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Returns full vitality details including decayed score and access receipt history.
        """
        self._ensure_initialized()
        current_time = float(now if now is not None else time.time())

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT fact_id, vitality_score, access_count, last_accessed_at, created_at, half_life_days, metadata_json
                    FROM scones_vitality_receipts
                    WHERE fact_id = ?;
                    """,
                    (str(fact_id),),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                decayed = self.calculate_decay(fact_id, half_life_days=float(row["half_life_days"]), now=current_time)
                return {
                    "fact_id": row["fact_id"],
                    "vitality_score": row["vitality_score"],
                    "decayed_vitality": decayed,
                    "access_count": row["access_count"],
                    "last_accessed_at": row["last_accessed_at"],
                    "created_at": row["created_at"],
                    "half_life_days": row["half_life_days"],
                    "metadata": json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                }

    def get_receipt_logs(self, fact_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves raw vitality receipt audit logs."""
        self._ensure_initialized()
        with self._lock:
            with self._get_connection() as conn:
                if fact_id is not None:
                    cursor = conn.execute(
                        """
                        SELECT id, fact_id, delta, resulting_vitality, task_hash, timestamp, metadata_json
                        FROM scones_vitality_logs
                        WHERE fact_id = ?
                        ORDER BY id DESC LIMIT ?;
                        """,
                        (str(fact_id), limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT id, fact_id, delta, resulting_vitality, task_hash, timestamp, metadata_json
                        FROM scones_vitality_logs
                        ORDER BY id DESC LIMIT ?;
                        """,
                        (limit,),
                    )
                rows = cursor.fetchall()
                return [
                    {
                        "id": r["id"],
                        "fact_id": r["fact_id"],
                        "delta": r["delta"],
                        "resulting_vitality": r["resulting_vitality"],
                        "task_hash": r["task_hash"],
                        "timestamp": r["timestamp"],
                        "metadata": json.loads(r["metadata_json"]) if r["metadata_json"] else {},
                    }
                    for r in rows
                ]

    # -------------------------------------------------------------------------
    # Async Wrappers
    # -------------------------------------------------------------------------
    async def track_access_async(
        self,
        fact_id: str,
        utility_delta: float = 1.0,
        task_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        now: Optional[float] = None,
    ) -> None:
        """Asynchronously tracks access to a fact."""
        await asyncio.to_thread(self.track_access, fact_id, utility_delta, task_hash, metadata, now)

    async def calculate_decay_async(
        self,
        fact_id: str,
        half_life_days: float = 14.0,
        now: Optional[float] = None,
    ) -> float:
        """Asynchronously calculates decayed vitality."""
        return await asyncio.to_thread(self.calculate_decay, fact_id, half_life_days, now)

    async def prune_dead_facts_async(
        self,
        min_vitality: float = 0.1,
        now: Optional[float] = None,
    ) -> List[str]:
        """Asynchronously prunes dead facts."""
        return await asyncio.to_thread(self.prune_dead_facts, min_vitality, now)
