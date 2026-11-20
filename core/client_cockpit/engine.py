# --- DNK-MRH-HEADER ---
# mrh_id: "core/client_cockpit/engine.py"
# purpose: "DNK Agentic Client Interaction Engine (ACIE) core manager & SQLite repository."
# canonical_source: true
# alters_files: ["data/client_cockpit.db"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

DB_PATH = Path("data/client_cockpit.db")

CANONICAL_6_STAGES = [
    {"stage_num": 1, "title": "Архітектура, стиль (Polaris Snow) та прототип картки", "status": "completed"},
    {"stage_num": 2, "title": "Верстка головної сторінки та нативних Theme Blocks", "status": "in_progress"},
    {"stage_num": 3, "title": "Синхронізація відгуків Etsy та розмітка Google Shopping", "status": "pending"},
    {"stage_num": 4, "title": "Оптова B2B сторінка та висувний кошик (Slide Drawer)", "status": "pending"},
    {"stage_num": 5, "title": "QA, оптимізація швидкості (Core Web Vitals 90+) та чекаут", "status": "pending"},
    {"stage_num": 6, "title": "Фінальний реліз на noku.store та передача прав на тему", "status": "pending"},
]


class ClientTicket(BaseModel):
    ticket_id: str
    deal_id: str
    title: str
    comment: str
    category: str = "in_scope_revision"  # question | in_scope_revision | out_of_scope_upsell
    status: str = "open"  # open | in_review | applied | resolved
    selector: Optional[str] = None
    section_id: Optional[str] = None
    block_id: Optional[str] = None
    screenshot_url: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None
    agent_response: Optional[str] = None
    resolution_note: Optional[str] = None
    resolved_at: Optional[float] = None
    created_at: float = Field(default_factory=time.time)


class ClientCockpitEngine:
    """Core engine for Ring 2 (Living Client Cockpit) & Ring 4 (Execution Loop)."""

    def __init__(self, db_path: Optional[Union[Path, str]] = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else DB_PATH
        self._ensure_db()

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(str(self.db_path))
        con.execute("PRAGMA journal_mode=WAL;")
        con.row_factory = sqlite3.Row
        return con

    def _ensure_db(self) -> None:
        with self._get_connection() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS deals (
                deal_id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                brand TEXT NOT NULL,
                tier TEXT NOT NULL DEFAULT 'scale_1500',
                total_amount REAL NOT NULL DEFAULT 1500.0,
                prepay_amount REAL NOT NULL DEFAULT 750.0,
                revision_quota INTEGER NOT NULL DEFAULT 3,
                revisions_used INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT NOT NULL,
                stage_num INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                completed_at REAL,
                FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                deal_id TEXT NOT NULL,
                title TEXT NOT NULL,
                comment TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'in_scope_revision',
                status TEXT NOT NULL DEFAULT 'open',
                selector TEXT,
                section_id TEXT,
                block_id TEXT,
                screenshot_url TEXT,
                bounding_box TEXT,
                agent_response TEXT,
                resolution_note TEXT,
                resolved_at REAL,
                created_at REAL NOT NULL,
                FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id TEXT NOT NULL,
                name TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (deal_id) REFERENCES deals(deal_id) ON DELETE CASCADE
            );
            """)

            # Schema migrations for existing databases
            for col in ["resolution_note TEXT", "resolved_at REAL", "bounding_box TEXT", "agent_response TEXT"]:
                try:
                    con.execute(f"ALTER TABLE tickets ADD COLUMN {col};")
                except sqlite3.OperationalError:
                    pass

    def init_deal(
        self,
        deal_id: str = "deal_noku_2026",
        client_name: str = "Андрій Ніколаєв",
        brand: str = "NOKU",
        tier: str = "scale_1500",
        total_amount: float = 1500.0,
    ) -> Dict[str, Any]:
        """Creates or loads a client deal, bootstrapping the 6 canonical stages."""
        with self._get_connection() as con:
            cur = con.cursor()
            existing = cur.execute("SELECT * FROM deals WHERE deal_id = ?", (deal_id,)).fetchone()
            if not existing:
                now = time.time()
                prepay = total_amount * 0.5
                cur.execute(
                    """
                    INSERT INTO deals (deal_id, client_name, brand, tier, total_amount, prepay_amount, revision_quota, revisions_used, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 3, 0, 'active', ?)
                    """,
                    (deal_id, client_name, brand, tier, total_amount, prepay, now),
                )
                for s in CANONICAL_6_STAGES:
                    cur.execute(
                        """
                        INSERT INTO stages (deal_id, stage_num, title, status, completed_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (deal_id, s["stage_num"], s["title"], s["status"], now if s["status"] == "completed" else None),
                    )
                # Seed initial artifacts
                cur.execute(
                    """
                    INSERT INTO artifacts (deal_id, name, artifact_type, url, created_at)
                    VALUES (?, 'Жива комерційна пропозиція', 'proposal_web', 'https://noku-proposal.pages.dev', ?)
                    """,
                    (deal_id, now),
                )
                cur.execute(
                    """
                    INSERT INTO artifacts (deal_id, name, artifact_type, url, created_at)
                    VALUES (?, 'Оригінальний магазин клієнта', 'live_store', 'https://noku.store', ?)
                    """,
                    (deal_id, now),
                )
                con.commit()

        return self.get_cockpit_state(deal_id)

    def submit_ticket(
        self,
        deal_id: str,
        title: str,
        comment: str,
        category: Optional[str] = None,
        selector: Optional[str] = None,
        section_id: Optional[str] = None,
        block_id: Optional[str] = None,
        screenshot_url: Optional[str] = None,
        bounding_box: Optional[Dict[str, Any]] = None,
        agent_response: Optional[str] = None,
    ) -> ClientTicket:
        """Submits a ticket with deterministic Scope Guard triage and visual area bounding box."""
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

        # Automatic classification if category is not provided
        if not category or category == "auto":
            text_lower = (title + " " + comment).lower()
            if any(q in text_lower for q in ["як ", "чи можна", "де подивитися", "чому", "?"]):
                category = "question"
            elif any(u in text_lower for u in ["crm", "кастомний додаток", "1с", "інтеграція з бас", "нова мова"]):
                category = "out_of_scope_upsell"
            else:
                category = "in_scope_revision"

        ticket = ClientTicket(
            ticket_id=ticket_id,
            deal_id=deal_id,
            title=title,
            comment=comment,
            category=category,
            status="open",
            selector=selector,
            section_id=section_id,
            block_id=block_id,
            screenshot_url=screenshot_url,
            bounding_box=bounding_box,
            agent_response=agent_response,
        )

        bbox_json = json.dumps(bounding_box) if bounding_box else None

        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO tickets (ticket_id, deal_id, title, comment, category, status, selector, section_id, block_id, screenshot_url, bounding_box, agent_response, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.ticket_id,
                    ticket.deal_id,
                    ticket.title,
                    ticket.comment,
                    ticket.category,
                    ticket.status,
                    ticket.selector,
                    ticket.section_id,
                    ticket.block_id,
                    ticket.screenshot_url,
                    bbox_json,
                    ticket.agent_response,
                    ticket.created_at,
                ),
            )
            # If in-scope revision, update quota
            if category == "in_scope_revision":
                cur.execute("UPDATE deals SET revisions_used = revisions_used + 1 WHERE deal_id = ?", (deal_id,))
            con.commit()

        return ticket

    def update_ticket_agent_response(self, deal_id: str, ticket_id: str, response_text: str) -> None:
        """Updates the agent's reply on a ticket."""
        with self._get_connection() as con:
            con.execute(
                "UPDATE tickets SET agent_response = ? WHERE deal_id = ? AND ticket_id = ?",
                (response_text, deal_id, ticket_id),
            )
            con.commit()

    def update_stage_status(self, deal_id: str, stage_num: int, new_status: str) -> None:
        """Updates stage progress (completed, in_progress, pending)."""
        now = time.time() if new_status == "completed" else None
        with self._get_connection() as con:
            con.execute(
                "UPDATE stages SET status = ?, completed_at = ? WHERE deal_id = ? AND stage_num = ?",
                (new_status, now, deal_id, stage_num),
            )
            con.commit()

    def add_artifact(self, deal_id: str, name: str, artifact_type: str, url: str) -> None:
        """Adds a deliverable artifact to the Client Vault."""
        with self._get_connection() as con:
            con.execute(
                "INSERT INTO artifacts (deal_id, name, artifact_type, url, created_at) VALUES (?, ?, ?, ?, ?)",
                (deal_id, name, artifact_type, url, time.time()),
            )
            con.commit()

    def _format_ticket_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        if d.get("bounding_box") and isinstance(d["bounding_box"], str):
            try:
                d["bounding_box"] = json.loads(d["bounding_box"])
            except Exception:
                pass
        return d

    def get_tickets(self, deal_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves tickets for a deal, optionally filtered by status."""
        with self._get_connection() as con:
            cur = con.cursor()
            if status:
                rows = cur.execute(
                    "SELECT * FROM tickets WHERE deal_id = ? AND status = ? ORDER BY created_at DESC",
                    (deal_id, status),
                ).fetchall()
            else:
                rows = cur.execute(
                    "SELECT * FROM tickets WHERE deal_id = ? ORDER BY created_at DESC",
                    (deal_id,),
                ).fetchall()
            return [self._format_ticket_row(r) for r in rows]

    def resolve_ticket(
        self,
        deal_id: str,
        ticket_id: str,
        resolution_note: str = "",
        status: str = "resolved",
    ) -> Dict[str, Any]:
        """Marks a ticket resolved, recording the agent's fix or notes."""
        now = time.time()
        with self._get_connection() as con:
            con.execute(
                """
                UPDATE tickets
                SET status = ?, resolution_note = ?, resolved_at = ?
                WHERE deal_id = ? AND ticket_id = ?
                """,
                (status, resolution_note, now, deal_id, ticket_id),
            )
            con.commit()
            row = con.execute(
                "SELECT * FROM tickets WHERE deal_id = ? AND ticket_id = ?",
                (deal_id, ticket_id),
            ).fetchone()
            return self._format_ticket_row(row) if row else {}

    def get_cockpit_state(self, deal_id: str = "deal_noku_2026") -> Dict[str, Any]:
        """Returns the complete SSOT state for Ring 2 (Client Cockpit)."""
        with self._get_connection() as con:
            cur = con.cursor()
            deal_row = cur.execute("SELECT * FROM deals WHERE deal_id = ?", (deal_id,)).fetchone()
            if not deal_row:
                return {}

            stages_rows = cur.execute(
                "SELECT * FROM stages WHERE deal_id = ? ORDER BY stage_num ASC", (deal_id,)
            ).fetchall()
            tickets_rows = cur.execute(
                "SELECT * FROM tickets WHERE deal_id = ? ORDER BY created_at DESC", (deal_id,)
            ).fetchall()
            artifacts_rows = cur.execute(
                "SELECT * FROM artifacts WHERE deal_id = ? ORDER BY created_at DESC", (deal_id,)
            ).fetchall()

            return {
                "deal": dict(deal_row),
                "stages": [dict(r) for r in stages_rows],
                "tickets": [self._format_ticket_row(r) for r in tickets_rows],
                "artifacts": [dict(r) for r in artifacts_rows],
            }
