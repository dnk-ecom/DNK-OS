# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/rlm_compactor.py"
# purpose: "Prime Agent RLM Dynamic Context Compactor, Semantic Turn Slicing & Attention Preserving Engine."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

"""
Prime Agent RLM Dynamic Context Compactor.
Implements Recursive Language Model (RLM) Smart Compaction, Safe-Cut Trajectory Slicing,
and Attention Guardrails based on Prime Agent SOTA standards.

Prevents attention entropy during long-running multi-turn agent sessions (>25k tokens)
by synthesizing older dialogue turns into an immutable SCONES state contract while
preserving complete tool-call/result pairs and active recent turns.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("dnk.core.orchestrator.rlm_compactor")


class PrimeRLMCompactor:
    """
    Recursive Language Model (RLM) Dynamic Compactor.
    Evaluates message trajectories, detects context window bloat,
    finds safe non-severing cut points, and crystallizes older turns.
    """

    def __init__(self, default_max_tokens: int = 15000, target_retain_tokens: int = 4000):
        self.default_max_tokens = default_max_tokens
        self.target_retain_tokens = target_retain_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation of token count (~4 chars per token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def calculate_trajectory_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Sums total token count across messages in the trajectory."""
        total = 0
        for m in messages:
            content = m.get("content", "")
            meta = m.get("meta_json") or m.get("meta") or ""
            if isinstance(meta, dict):
                meta = json.dumps(meta)
            total += self.estimate_tokens(str(content)) + self.estimate_tokens(str(meta))
        return total

    def find_safe_cut_index(
        self,
        messages: List[Dict[str, Any]],
        target_retain_tokens: Optional[int] = None,
    ) -> int:
        """
        Traverses trajectory backward to locate a clean turn boundary that:
        1. Preserves at least target_retain_tokens of the newest context.
        2. Never slices between a tool call and its corresponding tool result.
        3. Lands strictly on a User or Assistant turn boundary.

        Returns index cut_idx where messages[cut_idx:] is preserved.
        """
        retain_target = target_retain_tokens or self.target_retain_tokens
        if len(messages) <= 3:
            return 0

        running_tokens = 0
        safe_idx = 0

        # Traverse backward from the newest message
        for i in range(len(messages) - 1, 0, -1):
            msg = messages[i]
            msg_tokens = self.estimate_tokens(str(msg.get("content", "")))
            running_tokens += msg_tokens

            # Check if message is a tool result or bound to a tool call
            is_tool_bound = (
                msg.get("role") == "tool"
                or "tool_call_id" in msg
                or (msg.get("meta") and "tool" in str(msg.get("meta")))
            )

            # We can only cut if we accumulated enough retain tokens AND we're on a clean boundary
            if running_tokens >= retain_target and not is_tool_bound:
                role = msg.get("role")
                if role in ("user", "assistant"):
                    safe_idx = i
                    break

        # Fallback to nearest clean user/assistant turn if retain_target was too strict
        if safe_idx == 0 and len(messages) > 3:
            for i in range(len(messages) - 2, 0, -1):
                msg = messages[i]
                is_bound = msg.get("role") == "tool" or "tool_call_id" in msg
                if msg.get("role") in ("user", "assistant") and not is_bound:
                    safe_idx = i
                    break

        return safe_idx

    def extract_compaction_digest(self, discarded_slice: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the discarded slice and distills critical durable invariants:
        - Locked decisions (DEC-*)
        - Touched / modified file paths
        - Encountered and resolved errors
        - Milestones completed
        """
        combined_text = "\n".join(str(m.get("content", "")) for m in discarded_slice)

        # 1. Extract DEC references
        decisions = sorted(list(set(re.findall(r"DEC-\d+", combined_text))))

        # 2. Extract file paths (e.g. apps/..., core/..., services/..., docs/...)
        file_patterns = re.findall(
            r"(?:[\w\.-]+/(?:[\w\.-]+/)+[\w\.-]+\.(?:py|tsx|ts|json|liquid|md|css|yaml|yml))",
            combined_text,
        )
        touched_files = sorted(list(set(file_patterns)))[:15]

        # 3. Extract errors resolved
        errors_resolved = []
        for line in combined_text.splitlines():
            if any(kw in line.lower() for kw in ("fixed:", "resolved:", "exit code 0", "passed in")):
                clean_line = line.strip()[:120]
                if clean_line and clean_line not in errors_resolved:
                    errors_resolved.append(clean_line)
                    if len(errors_resolved) >= 5:
                        break

        # 4. Turn statistics
        roles_count = {}
        for m in discarded_slice:
            r = m.get("role", "unknown")
            roles_count[r] = roles_count.get(r, 0) + 1

        return {
            "discarded_turns_count": len(discarded_slice),
            "roles_breakdown": roles_count,
            "locked_decisions": decisions,
            "touched_files": touched_files,
            "errors_resolved": errors_resolved,
            "timestamp": time.time(),
        }

    def synthesize_compaction_contract(self, digest: Dict[str, Any], session_id: str = "") -> str:
        """
        Compiles the distilled digest into an immutable, highly compressed
        Markdown system prompt contract that anchors the LLM's attention.
        """
        lines = [
            f"### 🧬 [PRIME RLM COMPACTED CONTEXT] (Session: {session_id or 'active'})",
            f"> **Smart Compaction**: {digest['discarded_turns_count']} turns safely distilled into state invariants to preserve context budget.",
        ]

        if digest.get("locked_decisions"):
            lines.append(f"- **Locked Architectural Decisions**: {', '.join(digest['locked_decisions'])}")

        if digest.get("touched_files"):
            lines.append(f"- **Active Workspace Artifacts**: {', '.join(digest['touched_files'])}")

        if digest.get("errors_resolved"):
            lines.append("- **Resolved System Verifications**:")
            for err in digest["errors_resolved"]:
                lines.append(f"  * {err}")

        lines.append(
            "- **Invariant**: Continue execution adhering strictly to locked decisions above with zero drift."
        )
        return "\n".join(lines)

    def compact_trajectory(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        target_retain_tokens: Optional[int] = None,
        session_id: str = "",
    ) -> Tuple[List[Dict[str, Any]], bool, Dict[str, Any]]:
        """
        Evaluates message trajectory. If total tokens exceed max_tokens:
        Compacts older slice into a single synthesis turn, returning the pruned trajectory.
        """
        ceiling = max_tokens or self.default_max_tokens
        total_tokens = self.calculate_trajectory_tokens(messages)

        if total_tokens <= ceiling or len(messages) <= 4:
            return (
                messages,
                False,
                {
                    "compacted": False,
                    "total_tokens": total_tokens,
                    "ceiling": ceiling,
                    "turns_count": len(messages),
                },
            )

        cut_idx = self.find_safe_cut_index(messages, target_retain_tokens=target_retain_tokens)
        if cut_idx <= 0:
            # Cannot find safe cut point, retain all
            return messages, False, {"compacted": False, "reason": "no_safe_cut_found"}

        discarded_slice = messages[:cut_idx]
        retained_slice = messages[cut_idx:]

        digest = self.extract_compaction_digest(discarded_slice)
        contract_text = self.synthesize_compaction_contract(digest, session_id=session_id)

        # Inject synthesized contract as Turn 0 System Contract
        contract_message = {
            "id": f"cpt_{int(time.time())}",
            "session_id": session_id,
            "role": "system",
            "content": contract_text,
            "meta_json": json.dumps({"is_rlm_compaction": True, "digest": digest}, ensure_ascii=False),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        compacted_trajectory = [contract_message] + retained_slice
        new_total_tokens = self.calculate_trajectory_tokens(compacted_trajectory)

        telemetry = {
            "compacted": True,
            "original_tokens": total_tokens,
            "new_tokens": new_total_tokens,
            "tokens_saved": total_tokens - new_total_tokens,
            "discarded_turns": len(discarded_slice),
            "retained_turns": len(retained_slice),
            "digest": digest,
        }
        logger.info(
            f"RLM Smart Compaction executed for {session_id}: "
            f"{total_tokens} -> {new_total_tokens} tokens (saved {telemetry['tokens_saved']})."
        )
        return compacted_trajectory, True, telemetry
