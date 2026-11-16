# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/health_store.py"
# purpose: "Separate SQLite store for repo health signals and the reversible quarantine of removed catalog rows (the catalog itself is untouched until apply)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from services.dnk_git_research.src.brief_store import default_store_path
from services.dnk_git_research.src.repo_signals import RepoSignals


def default_health_path() -> Path:
    return default_store_path().with_name("health.db")


class HealthStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else default_health_path()

    @property
    def backups_dir(self) -> Path:
        return self.path.parent / "backups"

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self.path))
        con.execute(
            "CREATE TABLE IF NOT EXISTS signals (repo_id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL, "
            "etag TEXT, signals_json TEXT NOT NULL)"
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS quarantine (repo_id TEXT PRIMARY KEY, removed_at TEXT NOT NULL, "
            "tier TEXT NOT NULL, reasons_json TEXT NOT NULL, row_json TEXT NOT NULL)"
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS content (repo_id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL, content_json TEXT NOT NULL)"
        )
        return con

    # ---- content (file-tree facts for niche repositories)
    def put_content(self, c: Any) -> None:
        con = self._connect()
        try:
            con.execute("INSERT OR REPLACE INTO content (repo_id, fetched_at, content_json) VALUES (?,?,?)",
                        (c.repo_id.lower(), c.fetched_at, c.model_dump_json()))
            con.commit()
        finally:
            con.close()

    def content_fetched_map(self) -> Dict[str, str]:
        con = self._connect()
        try:
            return {r[0]: r[1] for r in con.execute("SELECT repo_id, fetched_at FROM content")}
        finally:
            con.close()

    def all_content(self) -> Dict[str, Any]:
        from services.dnk_git_research.src.niche_profiles import ContentSignals
        con = self._connect()
        try:
            return {r[0]: ContentSignals.model_validate_json(r[1])
                    for r in con.execute("SELECT repo_id, content_json FROM content")}
        finally:
            con.close()

    # ---- signals
    def get_signals(self, repo_id: str) -> Optional[Tuple[RepoSignals, Optional[str]]]:
        con = self._connect()
        try:
            r = con.execute("SELECT signals_json, etag FROM signals WHERE repo_id = ?", (repo_id.lower(),)).fetchone()
        finally:
            con.close()
        return (RepoSignals.model_validate_json(r[0]), r[1]) if r else None

    def put_signals(self, sig: RepoSignals, etag: Optional[str]) -> None:
        con = self._connect()
        try:
            con.execute(
                "INSERT OR REPLACE INTO signals (repo_id, fetched_at, etag, signals_json) VALUES (?,?,?,?)",
                (sig.repo_id.lower(), sig.fetched_at, etag, sig.model_dump_json()),
            )
            con.commit()
        finally:
            con.close()

    def touch_signals(self, repo_id: str) -> None:
        con = self._connect()
        try:
            con.execute("UPDATE signals SET fetched_at = ? WHERE repo_id = ?",
                        (datetime.now(timezone.utc).isoformat(), repo_id.lower()))
            con.commit()
        finally:
            con.close()

    def fetched_map(self) -> Dict[str, str]:
        con = self._connect()
        try:
            return {r[0]: r[1] for r in con.execute("SELECT repo_id, fetched_at FROM signals")}
        finally:
            con.close()

    def all_signals(self) -> Dict[str, RepoSignals]:
        con = self._connect()
        try:
            return {r[0]: RepoSignals.model_validate_json(r[1])
                    for r in con.execute("SELECT repo_id, signals_json FROM signals")}
        finally:
            con.close()

    # ---- quarantine
    def quarantine_add(self, con: sqlite3.Connection, repo_id: str, tier: str, reasons: List[str], row: Dict[str, Any]) -> None:
        con.execute(
            "INSERT OR REPLACE INTO quarantine (repo_id, removed_at, tier, reasons_json, row_json) VALUES (?,?,?,?,?)",
            (repo_id, datetime.now(timezone.utc).isoformat(), tier,
             json.dumps(reasons, ensure_ascii=False), json.dumps(row, ensure_ascii=False)),
        )

    def quarantine_get(self, repo_id: str) -> Optional[Dict[str, Any]]:
        con = self._connect()
        try:
            r = con.execute("SELECT tier, reasons_json, row_json, removed_at FROM quarantine WHERE lower(repo_id) = ?",
                            (repo_id.lower(),)).fetchone()
        finally:
            con.close()
        if not r:
            return None
        return {"tier": r[0], "reasons": json.loads(r[1]), "row": json.loads(r[2]), "removed_at": r[3]}

    def quarantine_list(self) -> List[Dict[str, Any]]:
        con = self._connect()
        try:
            return [{"repo_id": r[0], "tier": r[1], "removed_at": r[2], "reasons": json.loads(r[3])}
                    for r in con.execute("SELECT repo_id, tier, removed_at, reasons_json FROM quarantine ORDER BY removed_at")]
        finally:
            con.close()

    def quarantine_remove(self, con: sqlite3.Connection, repo_id: str) -> None:
        con.execute("DELETE FROM quarantine WHERE lower(repo_id) = ?", (repo_id.lower(),))

    def connect(self) -> sqlite3.Connection:
        return self._connect()
