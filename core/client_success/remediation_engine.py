# --- DNK-MRH-HEADER ---
# mrh_id: "core/client_success/remediation_engine.py"
# purpose: "Automated Visual Review Remediation Engine: Synthesize Git Diffs & 1-Click HITL Approval for Denchik."
# canonical_source: true
# alters_files: ["data/client_cockpit.db"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from core.client_cockpit.engine import ClientCockpitEngine
from core.orchestrator.agents.denchik.builder_guard import DenchikMandateGuard

logger = logging.getLogger("dnk.client_success.remediation")


class RemediationProposal(BaseModel):
    proposal_id: str = Field(..., description="Unique ID of proposal (e.g. PROP-TKT-101)")
    ticket_id: str = Field(..., description="Referenced client review ticket ID")
    deal_id: str = Field(..., description="Deal identifier")
    target_file: str = Field(..., description="Relative file path being modified")
    client_instruction: str = Field(..., description="Original client feedback")
    unified_diff: str = Field(..., description="Standard Unified Git Diff showing code changes")
    explanation_uk: str = Field(..., description="4-part senior dev explanation formatted for Maxim")
    status: str = Field("pending_approval", description="pending_approval | approved | applied | rejected")
    proposed_by: str = Field("denchik", description="Agent author")
    approved_by: Optional[str] = Field(None, description="Human approver (e.g. maksym)")


class RemediationEngine:
    """
    Automates the feedback loop between client in-context visual reviews and Denchik.
    Generates unified git diff patches and coordinates Human-In-The-Loop approval for Maxim.
    """

    def __init__(self, engine: Optional[ClientCockpitEngine] = None, repo_root: Optional[Path] = None) -> None:
        self.engine = engine or ClientCockpitEngine()
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self._proposals: Dict[str, RemediationProposal] = {}

    def synthesize_remediation(
        self,
        deal_id: str,
        ticket_id: str,
        target_file: str,
        new_content: str,
        explanation_uk: str = "",
    ) -> RemediationProposal:
        """
        Takes Denchik's proposed content for a target file, compares with current file,
        generates unified diff, and packages into a pending approval proposal.
        """
        # Relative path invariant
        norm_file = target_file.lstrip("./")
        abs_target = (self.repo_root / norm_file).resolve()

        if not abs_target.exists():
            original_content = ""
        else:
            original_content = abs_target.read_text(encoding="utf-8")

        # Generate Unified Diff
        diff_lines = list(
            difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{norm_file}",
                tofile=f"b/{norm_file}",
            )
        )
        diff_str = "".join(diff_lines) if diff_lines else "# No textual difference detected."

        # Fetch ticket details
        state = self.engine.get_cockpit_state(deal_id=deal_id)
        ticket = next((t for t in state.get("tickets", []) if t["ticket_id"] == ticket_id), None)
        client_instr = ticket["comment"] if ticket else "Правка клієнта з прев'ю-посилання"

        proposal_id = f"PROP-{ticket_id}"

        # 4-Part Senior Dev Rubric in Ukrainian if not supplied
        if not explanation_uk:
            selector = ticket.get("selector") if ticket else norm_file
            explanation_uk = (
                f"### 🎯 Рішення Денчіка для тікета {ticket_id}\n\n"
                f"1. **Що це**: Візуальна правка клієнта для зони `{selector}` у файлі `{norm_file}`.\n"
                f"2. **Проблема**: Клієнт просить: «_{client_instr}_».\n"
                f"3. **Рішення (Diff)**: Внесено точкову зміну без зайвих сторонніх залежностей.\n"
                f"4. **Якщо пропустимо**: Клієнт побачить невідповідність затвердженому дизайну на прев'ю.\n"
            )

        proposal = RemediationProposal(
            proposal_id=proposal_id,
            ticket_id=ticket_id,
            deal_id=deal_id,
            target_file=norm_file,
            client_instruction=client_instr,
            unified_diff=diff_str,
            explanation_uk=explanation_uk,
            status="pending_approval",
            proposed_by="denchik",
        )

        self._proposals[proposal_id] = proposal

        # Update ticket status in Cockpit Engine to 'in_review'
        self.engine.resolve_ticket(
            deal_id=deal_id,
            ticket_id=ticket_id,
            resolution_note=f"Denchik generated remediation diff {proposal_id}. Awaiting Maxim's 1-click approval.",
            status="in_review",
        )

        logger.info(f"Generated RemediationProposal {proposal_id} for {norm_file}")
        return proposal

    def apply_remediation(
        self,
        proposal_id: str,
        new_content: str,
        approver: str = "maksym",
    ) -> Dict[str, Any]:
        """
        Applies an approved patch to disk safely via DenchikMandateGuard and closes the ticket.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found.")

        norm_file = proposal.target_file.lstrip("./")
        abs_target = (self.repo_root / norm_file).resolve()

        # Safe file write with relative path assertion and mandate guard
        DenchikMandateGuard.validate_mutation(
            path=norm_file,
            tool_name="remediation_apply",
        )
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        abs_target.write_text(new_content, encoding="utf-8")
        logger.info(f"Denchik successfully applied remediation to '{norm_file}'.")

        proposal.status = "applied"
        proposal.approved_by = approver

        # Mark ticket as resolved in Cockpit DB
        self.engine.resolve_ticket(
            deal_id=proposal.deal_id,
            ticket_id=proposal.ticket_id,
            resolution_note=f"Approved by {approver}. Patch applied to {norm_file} by Denchik.",
            status="resolved",
        )

        return {
            "success": True,
            "proposal_id": proposal_id,
            "ticket_id": proposal.ticket_id,
            "target_file": norm_file,
            "status": "resolved",
            "applied_by": "denchik",
            "approved_by": approver,
        }

    def get_pending_proposals(self, deal_id: Optional[str] = None) -> List[RemediationProposal]:
        """Lists proposals awaiting Maxim's 1-click approval."""
        props = list(self._proposals.values())
        if deal_id:
            props = [p for p in props if p.deal_id == deal_id]
        return [p for p in props if p.status == "pending_approval"]
