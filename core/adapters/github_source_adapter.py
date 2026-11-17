# --- DNK-MRH-HEADER ---
# mrh_id: "core/adapters/github_source_adapter.py"
# purpose: "SOTA GitHub Event Ingestion Adapter with Deterministic Gate and Mandate Inception (DSH / DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from core.domain.mandate_contracts import (
    AdmissionGate,
    Mandate,
    MandateScope,
    Strength,
    Ticket,
    TicketStage,
)
from core.outbox.service import TransactionalOutbox

logger = logging.getLogger("dnk.adapters.github_source")


class GithubNormalizedEvent(BaseModel):
    """Normalized GitHub event for domain ingestion."""
    model_config = ConfigDict(extra="ignore")

    repository: str
    event_type: str  # issues, pull_request, issue_comment, pull_request_review_comment
    number: int
    is_pr: bool
    title: str = ""
    body: str = ""
    actor_login: str
    is_bot: bool = False
    html_url: str = ""
    bot_mentioned: bool = False


class GithubSourceAdapter:
    """
    Translates GitHub webhooks or CLI event payloads into DNK OS Tickets and Mandates.
    Applies DSH Zero-Attention & Deterministic Gate filters (DEC-151).
    """

    def __init__(
        self,
        gate: AdmissionGate,
        outbox: TransactionalOutbox,
        bot_handle: str = "@dnk-agent",
        default_policy_version: str = "pol-2026-v1"
    ) -> None:
        self.gate = gate
        self.outbox = outbox
        self.bot_handle = bot_handle.lower()
        self.default_policy_version = default_policy_version

    def normalize_payload(self, event_type: str, payload: Dict[str, Any]) -> Optional[GithubNormalizedEvent]:
        """Parse raw GitHub event JSON into normalized domain structure."""
        repo_name = payload.get("repository", {}).get("full_name", "unknown/repo")
        
        # 1. Issue or Pull Request opened
        if event_type in ("issues", "pull_request"):
            item = payload.get("issue") or payload.get("pull_request", {})
            user = item.get("user", {})
            actor = user.get("login", "ghost")
            is_bot = user.get("type") == "Bot" or actor.endswith("[bot]")
            body = item.get("body") or ""
            title = item.get("title", "")
            bot_mentioned = self.bot_handle in body.lower() or self.bot_handle in title.lower()

            return GithubNormalizedEvent(
                repository=repo_name,
                event_type=event_type,
                number=item.get("number", 0),
                is_pr=(event_type == "pull_request" or "pull_request" in item),
                title=title,
                body=body,
                actor_login=actor,
                is_bot=is_bot,
                html_url=item.get("html_url", ""),
                bot_mentioned=bot_mentioned
            )

        # 2. Comments on Issue or PR
        elif event_type in ("issue_comment", "pull_request_review_comment"):
            comment = payload.get("comment", {})
            user = comment.get("user", {})
            actor = user.get("login", "ghost")
            is_bot = user.get("type") == "Bot" or actor.endswith("[bot]")
            body = comment.get("body") or ""
            issue = payload.get("issue") or payload.get("pull_request", {})
            number = issue.get("number") or payload.get("number", 0)
            is_pr = "pull_request" in issue or event_type == "pull_request_review_comment"
            bot_mentioned = self.bot_handle in body.lower()

            return GithubNormalizedEvent(
                repository=repo_name,
                event_type=event_type,
                number=number,
                is_pr=is_pr,
                title=issue.get("title", ""),
                body=body,
                actor_login=actor,
                is_bot=is_bot,
                html_url=comment.get("html_url", ""),
                bot_mentioned=bot_mentioned
            )

        logger.info(f"Ignoring unsupported GitHub event type: {event_type}")
        return None

    def ingest_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        allowed_paths: Optional[List[str]] = None,
        negative_scope: Optional[List[str]] = None
    ) -> Optional[Ticket]:
        """
        Process event through AdmissionGate:
        - If NOT_ADMITTED: discard immediately with 0 token waste.
        - If EXPLICIT or INFERRED: mint Mandate, spawn Ticket, enqueue Outbox receipt.
        """
        event = self.normalize_payload(event_type, payload)
        if not event:
            return None

        # Deterministic admission gate
        strength = self.gate.admit(
            actor_id=event.actor_login,
            is_bot=event.is_bot,
            is_direct_or_mention=event.bot_mentioned
        )

        if strength == Strength.NOT_ADMITTED:
            logger.info(
                f"Gate rejected event from actor '{event.actor_login}' (bot={event.is_bot}, mentioned={event.bot_mentioned})"
            )
            return None

        # Build Mandate
        scope = MandateScope(
            allowed_paths=allowed_paths or ["services/**", "tests/**"],
            negative_scope=negative_scope or ["**/.env*", "**/credentials.json", "core/kernel.py"]
        )
        mandate = Mandate(
            policy_version=self.default_policy_version,
            scope=scope,
            strength=strength,
            matched_rules=[f"github-{event.event_type}-rule"],
            actor_id=event.actor_login,
            source_id="github"
        )

        # Create Ticket
        channel = f"github:{event.repository}:{event.number}"
        short_name = f"gh-{event.number}-{event.actor_login[:8]}"
        ticket = Ticket(
            short_name=short_name,
            mandate=mandate,
            channels=[channel]
        )

        # Enqueue silent acknowledgement in Transactional Outbox (DSH Attention Economy)
        ack_payload = {
            "type": "ack",
            "ticket_id": ticket.ticket_id,
            "message": f"Confirmed. Working on ticket {ticket.short_name} under {strength.value} mandate. Staying silent until PR/ready."
        }
        self.outbox.enqueue(
            destination_channel=channel,
            payload=ack_payload,
            idempotency_key=f"ack_{ticket.ticket_id}"
        )

        logger.info(f"Accepted ticket {ticket.ticket_id} for {event.actor_login} with {strength.value} mandate.")
        return ticket
