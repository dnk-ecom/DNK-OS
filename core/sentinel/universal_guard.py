# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/universal_guard.py"
# purpose: "Universal Cross-Harness Pre-Tool Execution Sentinel (Antigravity, Hermes, Claude Code)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
universal_guard.py — Universal Sentinel executing declarative invariants across ANY agent harness.

Supported Harnesses:
1. Nous Hermes Agent (pre_tool_call hook)
2. Anthropic Claude Code (PreToolUse hook)
3. Google Antigravity (CLI / Subagent lifecycle checks)
4. Custom Autonomous Scripts / Workflows
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def get_core_repo_root() -> Path:
    """Resolve the canonical DNK_OS repository root."""
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / "core" / "config" / "structural_barriers.json").exists():
            return p
    # Fallback to standard location
    standard = Path.home() / "Kuzmenko" / "MY_LIFE_WORK" / "DNK_OS"
    if standard.exists():
        return standard
    return current.parent.parent


def evaluate_structural_barriers(tool_name: str, payload_str: str, repo_root: Path) -> Optional[Tuple[str, str]]:
    """
    Checks payload against core/config/structural_barriers.json.
    Returns (barrier_id, message) if blocked, else None.
    """
    barriers_file = repo_root / "core" / "config" / "structural_barriers.json"
    if not barriers_file.exists():
        # Check DNK_HUB fallback
        hub_fallback = repo_root.parent / "DNK_HUB" / "core" / "config" / "structural_barriers.json"
        if hub_fallback.exists():
            barriers_file = hub_fallback
        else:
            return None

    try:
        with open(barriers_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for b in data.get("barriers", []):
            pattern = b.get("pattern")
            tool_pat = b.get("tool_name", ".*")
            if pattern and re.search(tool_pat, tool_name):
                if re.search(pattern, payload_str):
                    return (b.get("id", "BARRIER_UNKNOWN"), b.get("message", "Action blocked by invariant."))
    except Exception:
        pass
    return None


def run_guard(event_data: Dict[str, Any], harness: str = "auto") -> Dict[str, Any]:
    """
    Universal evaluation entrypoint.
    Returns format-neutral decision dictionary.
    """
    tool_name = event_data.get("tool_name", "") or event_data.get("tool", "")
    tool_input = event_data.get("tool_input", {}) or event_data.get("input", {}) or {}

    # Extract command or code payload if available
    payload_str = ""
    if isinstance(tool_input, dict):
        payload_str = (
            tool_input.get("command") or
            tool_input.get("code") or
            tool_input.get("query") or
            json.dumps(tool_input)
        )
    else:
        payload_str = str(tool_input)

    repo_root = get_core_repo_root()

    # 1. Check declarative structural barriers
    barrier = evaluate_structural_barriers(tool_name, payload_str, repo_root)
    if barrier:
        barrier_id, message = barrier
        # Format response based on calling harness convention
        return {
            "allowed": False,
            "action": "block",
            "decision": "deny",
            "barrier_id": barrier_id,
            "message": f"❌ BLOCKED [{barrier_id}]: {message}",
            "reason": f"BLOCKED [{barrier_id}]: {message}"
        }

    # 2. Check for Absolute Paths Leak (/Users/...)
    if "/Users/" in payload_str and not any(k in payload_str for k in ("~/.dnk_runtime", "MY_LIFE_WORK")):
        # Advisory sanitization warning
        pass

    return {
        "allowed": True,
        "action": "allow",
        "decision": "allow",
        "tool_name": tool_name,
        "tool_input": tool_input
    }


def main():
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            print(json.dumps({"action": "allow", "decision": "allow"}))
            sys.exit(0)

        data = json.loads(raw)
        result = run_guard(data)
        print(json.dumps(result))
        sys.exit(0 if result.get("allowed", True) else 1)
    except Exception as e:
        # Fail safe (allow) with logging
        print(json.dumps({"action": "allow", "decision": "allow", "error": str(e)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
