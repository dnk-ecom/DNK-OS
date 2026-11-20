# --- DNK-MRH-HEADER ---
# mrh_id: "core/client_success/agent.py"
# purpose: "DNK Client Success Agent: In-Context Visual Area Review Ingestion & Builder Translation Engine."
# canonical_source: true
# alters_files: ["data/client_cockpit.db"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from core.client_cockpit.engine import ClientCockpitEngine

logger = logging.getLogger("dnk.client_success")


class RelativeAnchor(BaseModel):
    selector: Optional[str] = Field(None, description="CSS selector of closest anchor element")
    rel_x_pct: float = Field(0.0, description="Percentage offset X (0-100%) inside anchor element")
    rel_y_pct: float = Field(0.0, description="Percentage offset Y (0-100%) inside anchor element")
    parent_tag: Optional[str] = Field(None, description="Tag name of parent element")


class BoundingBox(BaseModel):
    x: float = Field(0.0, description="X coordinate in px relative to viewport")
    y: float = Field(0.0, description="Y coordinate in px relative to viewport")
    width: float = Field(0.0, description="Width in px of selected area")
    height: float = Field(0.0, description="Height in px of selected area")
    page_x: float = Field(0.0, description="X coordinate relative to full document")
    page_y: float = Field(0.0, description="Y coordinate relative to full document")
    scroll_x: float = Field(0.0, description="Window scrollX at selection time")
    scroll_y: float = Field(0.0, description="Window scrollY at selection time")
    viewport_w: float = Field(1280.0, description="Viewport width")
    viewport_h: float = Field(800.0, description="Viewport height")
    relative_anchor: Optional[RelativeAnchor] = Field(None, description="Responsive anchor for viewport resize")


class VisualReviewPayload(BaseModel):
    deal_id: str = "deal_noku_2026"
    title: str
    comment: str
    category: str = "auto"
    selector: Optional[str] = None
    section_id: Optional[str] = None
    block_id: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    page_url: Optional[str] = None
    screenshot_url: Optional[str] = None
    client_name: Optional[str] = None


class ClientSuccessResponse(BaseModel):
    ticket_id: str
    deal_id: str
    category: str
    client_acknowledgment: str
    quota_used: int
    quota_remaining: int
    builder_task: Dict[str, Any]


class ClientSuccessAgent:
    """
    Client Success Agent / Account Concierge for in-context visual reviews.
    Translates visual rectangular coordinates into builder-ready TaskDNA and produces
    empathetic real-time feedback for clients on preview links.
    """

    def __init__(self, engine: Optional[ClientCockpitEngine] = None) -> None:
        self.engine = engine or ClientCockpitEngine()

    def process_visual_review(self, payload: VisualReviewPayload) -> ClientSuccessResponse:
        """
        Ingests a visual area review from a preview site, performs Scope Guard triage,
        persists the ticket with bounding box metadata, and synthesizes both a client
        acknowledgment and an engineering builder task.
        """
        box_dict = payload.bounding_box.model_dump() if payload.bounding_box else None

        # 1. Persist ticket in SQLite Cockpit repository
        ticket = self.engine.submit_ticket(
            deal_id=payload.deal_id,
            title=payload.title,
            comment=payload.comment,
            category=payload.category,
            selector=payload.selector,
            section_id=payload.section_id,
            block_id=payload.block_id,
            screenshot_url=payload.screenshot_url,
            bounding_box=box_dict,
        )

        # 2. Query quota state
        state = self.engine.get_cockpit_state(payload.deal_id)
        deal = state.get("deal", {})
        quota_total = deal.get("revision_quota", 3)
        quota_used = deal.get("revisions_used", 0)
        quota_rem = max(0, quota_total - quota_used)

        # 3. Synthesize Empathetic Client Acknowledgment
        target_name = payload.block_id or payload.section_id or payload.selector or "виділеної області"
        if ticket.category == "question":
            ack = (
                f"Дякуємо за запитання! Ми детально роз'яснимо логіку роботи для зони '{target_name}'. "
                "Ваш ліміт правок не використовується."
            )
        elif ticket.category == "out_of_scope_upsell":
            ack = (
                f"Дякуємо за побажання! Запит по зоні '{target_name}' передбачає новий розширений функціонал. "
                "Ми прорахуємо орієнтовну вартість і повернемося з рішенням."
            )
        else:
            ack = (
                f"Дякуємо! Вашу правку по зоні '{target_name}' зафіксовано та передано в чергу розробки. "
                f"Залишок раундів правок: {quota_rem} з {quota_total}. Статус виконання доступний у Cockpit."
            )

        # 4. Synthesize Builder Task for Denchik
        builder_task = {
            "task_id": f"BLD-{ticket.ticket_id}",
            "deal_id": payload.deal_id,
            "target_element": {
                "section": payload.section_id or "global",
                "block": payload.block_id,
                "selector": payload.selector,
                "bounding_box": box_dict,
                "relative_anchor": box_dict.get("relative_anchor") if box_dict else None,
            },
            "page_context": {
                "url": payload.page_url or "/",
            },
            "client_instruction": payload.comment,
            "category": ticket.category,
            "suggested_file": self._infer_suggested_file(payload.section_id, payload.block_id),
        }

        # 5. Update ticket with agent response
        self.engine.update_ticket_agent_response(payload.deal_id, ticket.ticket_id, ack)

        return ClientSuccessResponse(
            ticket_id=ticket.ticket_id,
            deal_id=payload.deal_id,
            category=ticket.category,
            client_acknowledgment=ack,
            quota_used=quota_used,
            quota_remaining=quota_rem,
            builder_task=builder_task,
        )

    def _infer_suggested_file(self, section_id: Optional[str], block_id: Optional[str]) -> str:
        """Determines best hypothesis for Shopify Liquid or CSS file location."""
        if block_id:
            return f"blocks/{block_id}.liquid"
        if section_id and section_id not in ("global", "main"):
            return f"sections/{section_id}.liquid"
        return "sections/main-product.liquid"

    @staticmethod
    def generate_preview_review_link(base_url: str, deal_id: str, client_name: str = "Client") -> str:
        """
        Constructs a direct preview link with review sensor parameters auto-activated.
        """
        clean_url = base_url.rstrip("/")
        separator = "&" if "?" in clean_url else "?"
        return f"{clean_url}{separator}dnk_review=1&deal_id={deal_id}&client={client_name}"
