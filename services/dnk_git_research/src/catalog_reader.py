# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/catalog_reader.py"
# purpose: "Read-only FTS5 reader over the DNK repository catalog (no import from core/, per services DOMAIN_RULES)"
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
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dnk.git_research.catalog")

HUB_ROOT = Path(__file__).resolve().parents[3]
CATALOG_ENV = "DNK_REPO_CATALOG_DB"

_COLUMNS = (
    "r.id, r.url, r.title, r.description, r.what_it_gives, r.tech_stack, r.category, "
    "r.maturity_tier, r.assimilation_status, r.sota_doc_path, r.license_track, "
    "r.architectural_pattern, r.dnk_module_target"
)


def default_catalog_path() -> Path:
    env = os.environ.get(CATALOG_ENV)
    return Path(env) if env else HUB_ROOT / ".data" / "repo_catalog" / "catalog.db"


def _fts_term(term: str) -> str:
    safe = term.replace('"', "")
    if re.fullmatch(r"[A-Za-z0-9]+", safe):
        return f'"{safe}"*'
    return f'"{safe}"'


class CatalogReader:
    """Read-only access; never writes to the catalog."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else default_catalog_path()

    def available(self) -> bool:
        return self.db_path.exists() and self.db_path.stat().st_size > 0

    def search(self, terms: List[str], limit: int = 12) -> List[Dict[str, Any]]:
        """bm25-ranked rows matching ANY term (the caller re-checks term coverage)."""
        if not terms or not self.available():
            return []
        query = " OR ".join(_fts_term(t) for t in terms)
        sql = (
            f"SELECT {_COLUMNS}, "
            "-bm25(repositories_fts, 0, 6, 3, 1, 1, 3, 0.5, 1, 0, 0.5, 3) AS score "
            "FROM repositories_fts f JOIN repositories r ON r.id = f.id "
            "WHERE repositories_fts MATCH ? ORDER BY score DESC LIMIT ?"
        )
        try:
            con = sqlite3.connect(self.db_path.resolve().as_uri() + "?mode=ro", uri=True)
            con.row_factory = sqlite3.Row
            try:
                return [dict(r) for r in con.execute(sql, (query, limit)).fetchall()]
            finally:
                con.close()
        except sqlite3.Error as exc:
            logger.warning("catalog search failed: %s", exc)
            return []
