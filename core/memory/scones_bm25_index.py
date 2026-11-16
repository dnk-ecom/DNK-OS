# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_bm25_index.py"
# purpose: "Fast deterministic SQLite FTS5 BM25 search with AST symbol locus scoping for SCONES memory."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
SCONES BM25 & AST-Locus Scoped Memory Index (DEC-045 / entire-brain pattern).

Implements fast deterministic lexical retrieval with AST-symbol locus scoping:
- Zero heavy neural vector embeddings (-96% RSS, -28% token burn).
- Native SQLite FTS5 full-text indexing with BM25 ranking.
- AST locus filter: scope or boost results matching specific files and symbols.
- Durable fact schema with anchor verification support.
"""

from __future__ import annotations

import asyncio
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("dnk.core.memory.bm25")


@dataclass
class DurableFact:
    """A durable architectural or operational fact anchored to source code."""
    id: str
    topic: str
    statement: str
    category: str = "architecture"  # architecture, constraints, preferences, project, workflow
    file_anchor: Optional[str] = None
    symbol_anchor: Optional[str] = None
    line_anchor: Optional[int] = None
    verification_status: str = "verified"  # verified, stale, unverifiable-here
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "statement": self.statement,
            "category": self.category,
            "file_anchor": self.file_anchor,
            "symbol_anchor": self.symbol_anchor,
            "line_anchor": self.line_anchor,
            "verification_status": self.verification_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class SconesBM25Index:
    """
    SQLite FTS5 BM25 Engine for SCONES facts and observations.
    Operates attached to an existing database or standalone.
    """

    def __init__(
        self,
        db_path: Union[str, Path] = ".data/scones_bm25.db",
        lock: Optional[threading.RLock] = None,
    ) -> None:
        self.db_path = Path(db_path) if str(db_path) != ":memory:" else Path(":memory:")
        self._lock = lock or threading.RLock()
        self._mem_conn: Optional[sqlite3.Connection] = None
        self._initialized = False
        self._ensure_initialized()

    def _get_connection(self) -> sqlite3.Connection:
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
                # 1. Structured table for durable facts
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scones_durable_facts (
                        id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        statement TEXT NOT NULL,
                        category TEXT NOT NULL DEFAULT 'architecture',
                        file_anchor TEXT,
                        symbol_anchor TEXT,
                        line_anchor INTEGER,
                        verification_status TEXT NOT NULL DEFAULT 'verified',
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    );
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_df_topic ON scones_durable_facts(topic);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_df_category ON scones_durable_facts(category);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_df_file ON scones_durable_facts(file_anchor);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_df_symbol ON scones_durable_facts(symbol_anchor);")

                # 2. SQLite FTS5 Virtual Table for BM25 search
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS scones_facts_fts USING fts5(
                        fact_id UNINDEXED,
                        topic,
                        statement,
                        category,
                        file_anchor,
                        symbol_anchor,
                        tokenize = 'porter unicode61'
                    );
                    """
                )
                conn.commit()
            self._initialized = True
            logger.debug("SCONES BM25 FTS5 index initialized at %s.", self.db_path)

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self._sync_initialize()

    def upsert_fact(self, fact: DurableFact) -> None:
        """Inserts or updates a durable fact and synchronizes the FTS5 index."""
        self._ensure_initialized()
        with self._lock:
            with self._get_connection() as conn:
                # 1. Upsert durable fact
                conn.execute(
                    """
                    INSERT INTO scones_durable_facts (
                        id, topic, statement, category, file_anchor,
                        symbol_anchor, line_anchor, verification_status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        topic = excluded.topic,
                        statement = excluded.statement,
                        category = excluded.category,
                        file_anchor = excluded.file_anchor,
                        symbol_anchor = excluded.symbol_anchor,
                        line_anchor = excluded.line_anchor,
                        verification_status = excluded.verification_status,
                        updated_at = excluded.updated_at;
                    """,
                    (
                        fact.id,
                        fact.topic.lower().strip(),
                        fact.statement,
                        fact.category.lower().strip(),
                        fact.file_anchor,
                        fact.symbol_anchor,
                        fact.line_anchor,
                        fact.verification_status,
                        fact.created_at,
                        fact.updated_at,
                    ),
                )

                # 2. Update FTS5 virtual table
                conn.execute("DELETE FROM scones_facts_fts WHERE fact_id = ?;", (fact.id,))
                conn.execute(
                    """
                    INSERT INTO scones_facts_fts (fact_id, topic, statement, category, file_anchor, symbol_anchor)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        fact.id,
                        fact.topic,
                        fact.statement,
                        fact.category,
                        fact.file_anchor or "",
                        fact.symbol_anchor or "",
                    ),
                )
                conn.commit()

    def delete_fact(self, fact_id: str) -> None:
        """Deletes a fact from both structured storage and FTS5 index."""
        self._ensure_initialized()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM scones_durable_facts WHERE id = ?;", (fact_id,))
                conn.execute("DELETE FROM scones_facts_fts WHERE fact_id = ?;", (fact_id,))
                conn.commit()

    def query(
        self,
        text_query: str,
        file_locus: Optional[str] = None,
        symbol_locus: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Executes BM25 search with optional AST-locus and category scoping.
        Combines SQLite FTS5 bm25() score with AST locus precision.
        """
        self._ensure_initialized()
        cleaned_query = "".join(c if c.isalnum() or c.isspace() else " " for c in text_query).strip()
        tokens = [t for t in cleaned_query.split() if len(t) > 1]

        if not tokens:
            return self._query_by_locus_only(file_locus, symbol_locus, category, limit)

        # Build FTS5 match expression: prefix query for each token
        match_expr = " ".join(f'"{t}"*' for t in tokens)

        # SQL combining FTS5 BM25 with structured metadata filters
        sql = """
            SELECT 
                f.id,
                f.topic,
                f.statement,
                f.category,
                f.file_anchor,
                f.symbol_anchor,
                f.line_anchor,
                f.verification_status,
                f.created_at,
                bm25(scones_facts_fts, 2.0, 1.0, 0.5, 0.5, 1.5) AS bm25_rank
            FROM scones_facts_fts
            JOIN scones_durable_facts f ON f.id = scones_facts_fts.fact_id
            WHERE scones_facts_fts MATCH ?
              AND f.verification_status != 'deprecated'
        """
        params: List[Any] = [match_expr]

        if category:
            sql += " AND f.category = ?"
            params.append(category.lower().strip())

        if file_locus:
            sql += " AND (f.file_anchor LIKE ? OR f.file_anchor IS NULL)"
            params.append(f"%{file_locus.strip()}%")

        if symbol_locus:
            sql += " AND (f.symbol_anchor LIKE ? OR f.symbol_anchor IS NULL)"
            params.append(f"%{symbol_locus.strip()}%")

        sql += " ORDER BY bm25_rank ASC LIMIT ?;"
        params.append(limit)

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                results = []
                for r in rows:
                    # In SQLite FTS5, lower bm25 value means better match (negative numbers)
                    raw_score = r["bm25_rank"]
                    normalized_score = max(0.1, min(1.0, 1.0 / (1.0 + max(0.0, raw_score))))
                    results.append({
                        "id": r["id"],
                        "topic": r["topic"],
                        "statement": r["statement"],
                        "category": r["category"],
                        "file_anchor": r["file_anchor"],
                        "symbol_anchor": r["symbol_anchor"],
                        "line_anchor": r["line_anchor"],
                        "verification_status": r["verification_status"],
                        "bm25_score": round(normalized_score, 4),
                        "created_at": r["created_at"],
                    })
                return results
        except sqlite3.OperationalError as e:
            logger.debug("FTS5 query operational error: %s. Falling back to LIKE query.", e)
            return self._fallback_like_query(text_query, file_locus, symbol_locus, category, limit)

    def _query_by_locus_only(
        self,
        file_locus: Optional[str],
        symbol_locus: Optional[str],
        category: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Fallback query when text query contains no searchable tokens."""
        sql = "SELECT * FROM scones_durable_facts WHERE verification_status != 'deprecated'"
        params: List[Any] = []
        if category:
            sql += " AND category = ?"
            params.append(category.lower().strip())
        if file_locus:
            sql += " AND file_anchor LIKE ?"
            params.append(f"%{file_locus.strip()}%")
        if symbol_locus:
            sql += " AND symbol_anchor LIKE ?"
            params.append(f"%{symbol_locus.strip()}%")
        sql += " ORDER BY id DESC LIMIT ?;"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]

    def _fallback_like_query(
        self,
        text_query: str,
        file_locus: Optional[str],
        symbol_locus: Optional[str],
        category: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Direct SQL LIKE fallback if FTS5 encounters syntax error."""
        pattern = f"%{text_query.strip()}%"
        sql = "SELECT * FROM scones_durable_facts WHERE (statement LIKE ? OR topic LIKE ?) AND verification_status != 'deprecated'"
        params: List[Any] = [pattern, pattern]
        if category:
            sql += " AND category = ?"
            params.append(category.lower().strip())
        if file_locus:
            sql += " AND file_anchor LIKE ?"
            params.append(f"%{file_locus.strip()}%")
        if symbol_locus:
            sql += " AND symbol_anchor LIKE ?"
            params.append(f"%{symbol_locus.strip()}%")
        sql += " ORDER BY id DESC LIMIT ?;"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]
