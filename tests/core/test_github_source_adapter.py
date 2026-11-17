# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_github_source_adapter.py"
# purpose: "Unit tests for GitHub Event Ingestion Adapter with Gate & Outbox integration (DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import pytest
from core.domain.mandate_contracts import AdmissionGate, Strength, TicketStage
from core.outbox.service import TransactionalOutbox
from core.adapters.github_source_adapter import GithubSourceAdapter


@pytest.fixture
def adapter():
    gate = AdmissionGate(
        allowed_actors={"maxim", "lead_maintainer"},
        banned_actors={"spammer_99"},
        known_bots={"dependabot"},
        allow_inferred_candidates=True
    )
    outbox = TransactionalOutbox(":memory:")
    return GithubSourceAdapter(gate=gate, outbox=outbox, bot_handle="@dnk-agent")


def test_allowed_human_explicit_issue(adapter):
    payload = {
        "repository": {"full_name": "dnk-ecom/DNK_OS"},
        "issue": {
            "number": 142,
            "title": "Refactor media silence detector",
            "body": "Hey @dnk-agent please optimize 9:16 reframing",
            "user": {"login": "maxim", "type": "User"}
        }
    }

    ticket = adapter.ingest_event("issues", payload)
    assert ticket is not None
    assert ticket.mandate.strength == Strength.EXPLICIT
    assert ticket.mandate.actor_id == "maxim"
    assert "github:dnk-ecom/DNK_OS:142" in ticket.channels
    assert ticket.stage == TicketStage.QUEUED

    # Check Outbox receipt
    messages = adapter.outbox.list_messages()
    assert len(messages) == 1
    assert messages[0].destination_channel == "github:dnk-ecom/DNK_OS:142"
    assert messages[0].payload["type"] == "ack"
    assert "explicit mandate" in messages[0].payload["message"]


def test_unlisted_human_inferred_comment(adapter):
    payload = {
        "repository": {"full_name": "dnk-ecom/DNK_OS"},
        "issue": {"number": 142, "title": "Existing thread"},
        "comment": {
            "body": "@dnk-agent can you look at this edge case?",
            "user": {"login": "community_contributor", "type": "User"}
        }
    }

    ticket = adapter.ingest_event("issue_comment", payload)
    assert ticket is not None
    assert ticket.mandate.strength == Strength.INFERRED
    assert ticket.mandate.actor_id == "community_contributor"


def test_banned_actor_dropped(adapter):
    payload = {
        "repository": {"full_name": "dnk-ecom/DNK_OS"},
        "issue": {
            "number": 999,
            "title": "Spam attack",
            "body": "@dnk-agent do something bad",
            "user": {"login": "spammer_99", "type": "User"}
        }
    }

    ticket = adapter.ingest_event("issues", payload)
    assert ticket is None

    # Zero Outbox messages
    messages = adapter.outbox.list_messages()
    assert len(messages) == 0


def test_unknown_bot_dropped(adapter):
    payload = {
        "repository": {"full_name": "dnk-ecom/DNK_OS"},
        "issue": {
            "number": 500,
            "title": "Automated scan",
            "body": "@dnk-agent automated trigger",
            "user": {"login": "random-scanner[bot]", "type": "Bot"}
        }
    }

    ticket = adapter.ingest_event("issues", payload)
    assert ticket is None
    assert len(adapter.outbox.list_messages()) == 0


def test_known_bot_inferred(adapter):
    payload = {
        "repository": {"full_name": "dnk-ecom/DNK_OS"},
        "pull_request": {
            "number": 210,
            "title": "Bump pydantic from 2.10 to 2.11",
            "body": "@dnk-agent verify dependencies",
            "user": {"login": "dependabot", "type": "Bot"}
        }
    }

    ticket = adapter.ingest_event("pull_request", payload)
    assert ticket is not None
    assert ticket.mandate.strength == Strength.INFERRED
