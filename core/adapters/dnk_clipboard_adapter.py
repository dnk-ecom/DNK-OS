# --- DNK-MRH-HEADER ---
# mrh_id: "core/adapters/dnk_clipboard_adapter.py"
# purpose: "Hexagonal Read-Only Adapter for ClipBoardLine (macOS native SQLite + Vision OCR + FTS5)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "DNK OS Architecture & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKClipboardAdapter")


class DNKClipboardAdapter:
    """
    Hexagonal read-only adapter interfacing with ClipBoardLine's local SQLite database.
    Provides zero-overhead, non-blocking ingestion of project clips, links, notes,
    and Apple Vision OCR screenshots for DNK OS agents.
    """

    DEFAULT_PATHS = [
        Path.home() / "Library/Application Support/ClipboardLine Review/Screenshots/Library/library.sqlite",
        Path.home() / "Library/Application Support/ClipBoardLine/Screenshots/Library/library.sqlite",
    ]

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path).expanduser() if db_path else self._resolve_default_db()

    def _resolve_default_db(self) -> Path:
        for candidate in self.DEFAULT_PATHS:
            if candidate.exists():
                return candidate
        return self.DEFAULT_PATHS[0]

    def is_available(self) -> bool:
        return self.db_path.exists()

    def _get_connection(self) -> sqlite3.Connection:
        if not self.is_available():
            raise FileNotFoundError(f"ClipBoardLine database not found at {self.db_path}")
        uri = f"file:{self.db_path.resolve()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def get_database_status(self) -> Dict[str, Any]:
        """Returns database availability, path, and aggregate metrics."""
        if not self.is_available():
            return {
                "available": False,
                "path": str(self.db_path),
                "total_items": 0,
                "collections_count": 0,
                "tags_count": 0,
                "screenshots_count": 0,
            }

        with self._get_connection() as conn:
            c = conn.cursor()
            total_items = c.execute("SELECT count(*) FROM items WHERE deleted IS NULL").fetchone()[0]
            collections_count = c.execute("SELECT count(*) FROM collections").fetchone()[0]
            tags_count = c.execute("SELECT count(*) FROM tags").fetchone()[0]
            screenshots_count = c.execute(
                "SELECT count(*) FROM items WHERE kind='image' AND deleted IS NULL"
            ).fetchone()[0]

            return {
                "available": True,
                "path": str(self.db_path),
                "total_items": total_items,
                "collections_count": collections_count,
                "tags_count": tags_count,
                "screenshots_count": screenshots_count,
            }

    def list_collections(self) -> List[Dict[str, Any]]:
        """Lists all project collections (virtual folders) with their assigned item counts."""
        if not self.is_available():
            return []

        query = """
        SELECT c.id, c.name, c.parent, count(ic.item) as item_count
        FROM collections c
        LEFT JOIN item_collections ic ON c.id = ic.collection
        GROUP BY c.id
        ORDER BY c.name COLLATE NOCASE ASC
        """
        with self._get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "parent": r["parent"],
                    "item_count": r["item_count"],
                }
                for r in rows
            ]

    def list_tags(self) -> List[Dict[str, Any]]:
        """Lists all tags with their assigned item counts."""
        if not self.is_available():
            return []

        query = """
        SELECT t.id, t.name, count(it.item) as item_count
        FROM tags t
        LEFT JOIN item_tags it ON t.id = it.tag
        GROUP BY t.id
        ORDER BY t.name COLLATE NOCASE ASC
        """
        with self._get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "item_count": r["item_count"],
                }
                for r in rows
            ]

    def search_items(
        self,
        query: Optional[str] = None,
        kind: Optional[str] = None,
        collection: Optional[str] = None,
        tag: Optional[str] = None,
        favorite_only: bool = False,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Searches items across text, links, and images.
        Filters by collection (project folder), tag, kind, or favorite (pinned).
        """
        if not self.is_available():
            return []

        clauses = ["i.deleted IS NULL"]
        params: List[Any] = []

        if kind:
            clauses.append("i.kind = ?")
            params.append(kind)

        if favorite_only:
            clauses.append("i.favorite = 1")

        if collection:
            clauses.append(
                "EXISTS (SELECT 1 FROM item_collections ic JOIN collections col ON ic.collection = col.id "
                "WHERE ic.item = i.id AND col.name LIKE ?)"
            )
            params.append(f"%{collection}%")

        if tag:
            clauses.append(
                "EXISTS (SELECT 1 FROM item_tags it JOIN tags tg ON it.tag = tg.id "
                "WHERE it.item = i.id AND tg.name LIKE ?)"
            )
            params.append(f"%{tag}%")

        if query:
            clauses.append(
                "(i.search LIKE ? OR i.sort_title LIKE ? OR i.domain LIKE ? OR "
                "EXISTS (SELECT 1 FROM search_fts s WHERE s.id = i.id AND search_fts MATCH ?))"
            )
            clean_term = f"%{query}%"
            sanitized_query = query.replace('"', ' ')
            fts_term = f'"{sanitized_query}"*'
            params.extend([clean_term, clean_term, clean_term, fts_term])

        where_sql = " AND ".join(clauses)
        sql = f"""
        SELECT i.id, i.kind, i.created, i.updated, i.favorite, i.domain, i.sort_title, i.payload,
               (SELECT group_concat(col.name, ', ') FROM item_collections ic JOIN collections col ON ic.collection = col.id WHERE ic.item = i.id) as collections,
               (SELECT group_concat(tg.name, ', ') FROM item_tags it JOIN tags tg ON it.tag = tg.id WHERE it.item = i.id) as tags
        FROM items i
        WHERE {where_sql}
        ORDER BY i.created DESC
        LIMIT ?
        """
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            results = []
            for r in rows:
                payload_data = {}
                if r["payload"]:
                    try:
                        payload_data = json.loads(r["payload"].decode("utf-8"))
                    except Exception:
                        pass

                results.append({
                    "id": r["id"],
                    "kind": r["kind"],
                    "created": r["created"],
                    "updated": r["updated"],
                    "favorite": bool(r["favorite"]),
                    "domain": r["domain"],
                    "title": r["sort_title"] or payload_data.get("title", ""),
                    "note": payload_data.get("note", ""),
                    "text": payload_data.get("text"),
                    "url": payload_data.get("originalURL") or payload_data.get("normalizedURL"),
                    "path": payload_data.get("path") or payload_data.get("originalPath"),
                    "metadata_title": payload_data.get("metadataTitle"),
                    "collections": [c.strip() for c in r["collections"].split(",")] if r["collections"] else [],
                    "tags": [t.strip() for t in r["tags"].split(",")] if r["tags"] else [],
                })
            return results

    def get_recent_screenshots(
        self, limit: int = 10, ocr_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves recent screenshots along with Apple Vision OCR recognized text.
        """
        if not self.is_available():
            return []

        clauses = ["i.kind = 'image'", "i.deleted IS NULL"]
        params: List[Any] = []

        if ocr_filter:
            clauses.append("ia.ocr LIKE ?")
            params.append(f"%{ocr_filter}%")

        where_sql = " AND ".join(clauses)
        sql = f"""
        SELECT i.id, i.created, i.updated, i.favorite, i.sort_title, i.payload,
               ia.path as image_path, ia.ocr as ocr_text, ia.fingerprint
        FROM items i
        LEFT JOIN image_analysis ia ON i.id = ia.item
        WHERE {where_sql}
        ORDER BY i.created DESC
        LIMIT ?
        """
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            results = []
            for r in rows:
                payload_data = {}
                if r["payload"]:
                    try:
                        payload_data = json.loads(r["payload"].decode("utf-8"))
                    except Exception:
                        pass

                results.append({
                    "id": r["id"],
                    "created": r["created"],
                    "favorite": bool(r["favorite"]),
                    "title": r["sort_title"] or payload_data.get("title", ""),
                    "note": payload_data.get("note", ""),
                    "image_path": r["image_path"] or payload_data.get("path"),
                    "ocr_text": r["ocr_text"] or "",
                    "fingerprint": r["fingerprint"] or "",
                })
            return results

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Fetches complete item details by UUID."""
        if not self.is_available():
            return None

        sql = """
        SELECT i.*, ia.ocr as ocr_text, ia.path as image_path
        FROM items i
        LEFT JOIN image_analysis ia ON i.id = ia.item
        WHERE i.id = ? AND i.deleted IS NULL
        """
        with self._get_connection() as conn:
            r = conn.execute(sql, (item_id,)).fetchone()
            if not r:
                return None

            payload_data = {}
            if r["payload"]:
                try:
                    payload_data = json.loads(r["payload"].decode("utf-8"))
                except Exception:
                    pass

            return {
                "id": r["id"],
                "kind": r["kind"],
                "created": r["created"],
                "updated": r["updated"],
                "favorite": bool(r["favorite"]),
                "domain": r["domain"],
                "title": r["sort_title"] or payload_data.get("title", ""),
                "note": payload_data.get("note", ""),
                "text": payload_data.get("text"),
                "url": payload_data.get("originalURL"),
                "image_path": r["image_path"] or payload_data.get("path"),
                "ocr_text": r["ocr_text"] or "",
                "payload": payload_data,
            }

    def execute_action(self, sub: str, payload: Dict[str, Any]) -> Any:
        """Unified action execution facade for kernel and CLI."""
        if sub == "status":
            return self.get_database_status()
        elif sub == "projects":
            return {"collections": self.list_collections(), "tags": self.list_tags(), "status": self.get_database_status()}
        elif sub == "screenshots":
            limit = int(payload.get("limit", 10))
            ocr = payload.get("ocr_filter")
            return self.get_recent_screenshots(limit=limit, ocr_filter=ocr)
        elif sub in ("search", "query"):
            query = payload.get("query")
            kind = payload.get("kind")
            collection = payload.get("collection")
            tag = payload.get("tag")
            fav = bool(payload.get("favorite_only", False))
            limit = int(payload.get("limit", 10))
            return self.search_items(query=query, kind=kind, collection=collection, tag=tag, favorite_only=fav, limit=limit)
        else:
            return {"error": f"Unknown clipboard action sub-type: {sub}"}
