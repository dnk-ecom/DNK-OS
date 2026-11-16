# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/brief_store.py"
# purpose: "Small SQLite cache of Reuse Briefs keyed by task-mechanics fingerprint, so a repeated specific task never triggers a second search"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("dnk.git_research.store")

HUB_ROOT = Path(__file__).resolve().parents[3]
STATE_ENV = "DNK_GIT_RESEARCH_STATE_DIR"


def default_store_path() -> Path:
    env = os.environ.get(STATE_ENV)
    base = Path(env) if env else HUB_ROOT / ".data" / "dnk_git_research"
    return base / "briefs.db"


class BriefStore:
    """Best effort: any SQLite problem degrades to 'no cache', never to a crash."""

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else default_store_path()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self.path))
        con.execute(
            "CREATE TABLE IF NOT EXISTS briefs ("
            "fingerprint TEXT PRIMARY KEY, created_at TEXT NOT NULL, brief_json TEXT NOT NULL)"
        )
        return con

    def get(self, fingerprint: str, max_age_days: int = 30) -> Optional[str]:
        try:
            con = self._connect()
            try:
                row = con.execute(
                    "SELECT created_at, brief_json FROM briefs WHERE fingerprint = ?", (fingerprint,)
                ).fetchone()
            finally:
                con.close()
        except (sqlite3.Error, OSError) as exc:
            logger.warning("brief cache read failed: %s", exc)
            return None
        if not row:
            return None
        try:
            created = datetime.fromisoformat(row[0])
        except ValueError:
            return None
        if datetime.now(timezone.utc) - created > timedelta(days=max_age_days):
            return None
        return row[1]

    def put(self, fingerprint: str, brief_json: str) -> bool:
        try:
            con = self._connect()
            try:
                con.execute(
                    "INSERT OR REPLACE INTO briefs (fingerprint, created_at, brief_json) VALUES (?, ?, ?)",
                    (fingerprint, datetime.now(timezone.utc).isoformat(), brief_json),
                )
                con.commit()
            finally:
                con.close()
            return True
        except (sqlite3.Error, OSError) as exc:
            logger.warning("brief cache write failed: %s", exc)
            return False
