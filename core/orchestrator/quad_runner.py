# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/quad_runner.py"
# purpose: "Sovereign Quad Node Runner linking Spatial Canvas with Hermes v0.23 Headless Personas & Grounding Guard."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
Sovereign Quad Node Runner.
Connects Canvas Nodes with the 4 sovereign agents:
1. Strategist (strategist_prime): Intent, CRO, Marketing, Strategy.
2. Architect (dnk_mentor): System architecture, ADRs, invariant checks.
3. Builder (denchik): Atomic code construction, MASE <= 25 actions.
4. Auditor (gerych): Cold knowledge, AST checks, fail-closed verification.

Executes nodes headlessly, enforces GroundingGuard against hallucinations,
and crystallizes outputs back into .canvas and SQLite WAL.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repository root is in sys.path
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from core.canvas.session_router import SpatialCanvasSessionRouter
from core.sentinel.grounding_guard import GroundingGuard, GroundingValidationError

logger = logging.getLogger("dnk.core.quad_runner")

ROLE_PERSONA_MAP = {
    "strategist": "strategist_prime",
    "strategist_prime": "strategist_prime",
    "architect": "dnk_mentor",
    "dnk_mentor": "dnk_mentor",
    "denchik": "denchik",
    "builder": "denchik",
    "gerych": "gerych_prime",
    "gerych_prime": "gerych_prime",
    "auditor": "auditor",
    "dnk_shopify": "dnk_shopify",
    "dnk_media": "dnk_media",
    "dnk_distribution": "dnk_distribution",
}


class SovereignQuadRunner:
    """Executes canvas nodes using the Sovereign Quad runtime with anti-hallucination gates."""

    def __init__(self, router: Optional[SpatialCanvasSessionRouter] = None):
        self.router = router or SpatialCanvasSessionRouter()

    def build_execution_envelope(
        self, canvas_path: Path, node_id: str
    ) -> Dict[str, Any]:
        """
        Synthesizes the complete zero-waste execution prompt for the node agent,
        incorporating L2 Project DNA and upstream crystallized contracts.
        """
        ctx = self.router.compile_node_context(canvas_path, node_id)
        persona = ROLE_PERSONA_MAP.get(ctx.agent_role.lower(), "general_agent")

        return {
            "canvas_id": ctx.canvas_id,
            "node_id": ctx.node_id,
            "node_title": ctx.node_title,
            "node_task": ctx.node_task,
            "agent_role": ctx.agent_role,
            "persona": persona,
            "system_prompt": ctx.system_prompt,
            "upstream_count": len(ctx.upstream_contracts),
            "project_dna": ctx.project_dna,
            "account_spec": ctx.account_spec,
        }

    def execute_node_mock(
        self,
        canvas_path: Path,
        node_id: str,
        simulated_output_summary: Optional[str] = None,
        simulated_numeric_payload: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Deterministic mock/sandbox execution validating GroundingGuard
        and crystallizing the node.
        """
        envelope = self.build_execution_envelope(canvas_path, node_id)
        source_text = envelope["system_prompt"]

        if simulated_output_summary is None:
            simulated_output_summary = (
                f"Autonomous crystallization of '{node_id}' executed by persona '{envelope['persona']}'."
            )

        # Validate grounding on any emitted numeric facts
        if simulated_numeric_payload:
            ungrounded = GroundingGuard.validate_grounding(simulated_numeric_payload, source_text)
            if ungrounded:
                detail = ", ".join(ungrounded)
                raise GroundingValidationError(
                    f"Node '{node_id}' failed GroundingGuard check with ungrounded values: {detail}"
                )

        # Crystallize outcome
        session = self.router.crystallize_node(
            canvas_path=canvas_path,
            node_id=node_id,
            summary=simulated_output_summary,
            artifact_refs=artifacts or [],
        )

        return {
            "status": "CRYSTALLIZED",
            "session_id": session.id,
            "node_id": node_id,
            "summary": simulated_output_summary,
            "artifacts": artifacts or [],
            "agent_role": envelope["agent_role"],
            "persona": envelope["persona"],
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 -m core.orchestrator.quad_runner <canvas_path> <node_id> [summary]")
        sys.exit(1)

    c_path = Path(sys.argv[1])
    n_id = sys.argv[2]
    summ = sys.argv[3] if len(sys.argv) > 3 else None

    runner = SovereignQuadRunner()
    res = runner.execute_node_mock(canvas_path=c_path, node_id=n_id, simulated_output_summary=summ)
    print(f"🎯 Node {n_id} Result: status={res['status']}, persona={res['persona']}")
    print(f"📝 Summary: {res['summary']}")
    print(f"🔑 Session ID: {res['session_id']}")

