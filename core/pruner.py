"""
# --- DNK-MRH-HEADER ---
# mrh_id: "core/pruner.py"
# purpose: "Deterministic Context and Output Pruner to prevent LLM attention entropy and token bloat."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-25"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
"""

import re
from typing import List


def prune_terminal_output(raw_output: str, max_lines: int = 120, max_chars: int = 8000) -> str:
    """
    Intelligently compresses terminal or test outputs.
    Preserves:
      1. First 25 lines (command kickoff and initial status)
      2. Any error markers (Traceback, FAILED, ERROR, AssertionError, Exception)
      3. Last 45 lines (summary and root cause lines)
    Eliminates redundant ballast in the middle.
    """
    if not raw_output:
        return ""

    lines = raw_output.splitlines()
    if len(lines) <= max_lines and len(raw_output) <= max_chars:
        return raw_output

    error_patterns = [
        re.compile(r"traceback\s*\(most recent call last\)", re.IGNORECASE),
        re.compile(r"FAILED\s+tests/", re.IGNORECASE),
        re.compile(r"AssertionError", re.IGNORECASE),
        re.compile(r"Exception:", re.IGNORECASE),
        re.compile(r"Error:", re.IGNORECASE),
        re.compile(r"=== FAILURES ===", re.IGNORECASE),
        re.compile(r"short test summary info", re.IGNORECASE),
    ]

    # Find error line indices
    error_indices = set()
    for idx, line in enumerate(lines):
        for pattern in error_patterns:
            if pattern.search(line):
                # Capture a context window around the error line
                start_win = max(0, idx - 5)
                end_win = min(len(lines), idx + 20)
                for w in range(start_win, end_win):
                    error_indices.add(w)
                break

    # Build head, error window, and tail
    head_count = 25
    tail_count = 45

    retained_indices = set(range(min(head_count, len(lines))))
    retained_indices.update(error_indices)
    retained_indices.update(range(max(0, len(lines) - tail_count), len(lines)))

    sorted_indices = sorted(list(retained_indices))

    pruned_lines: List[str] = []
    last_idx = -1
    for idx in sorted_indices:
        if last_idx != -1 and idx > last_idx + 1:
            omitted = idx - last_idx - 1
            pruned_lines.append(f"... [PRUNER: {omitted} lines of verbose output omitted] ...")
        pruned_lines.append(lines[idx])
        last_idx = idx

    result = "\n".join(pruned_lines)
    if len(result) > max_chars:
        # Emergency string truncate
        return result[: max_chars - 500] + "\n\n... [PRUNER: Char limit reached, tail truncated] ...\n" + result[-500:]

    return result


def prune_diff(diff_text: str, max_lines: int = 150) -> str:
    """
    Trims large git diff outputs by keeping diff headers and hunk summaries,
    avoiding massive token dumps for large generated files.
    """
    if not diff_text:
        return ""

    lines = diff_text.splitlines()
    if len(lines) <= max_lines:
        return diff_text

    # Keep header and first chunk of diff
    head = lines[:60]
    tail = lines[-40:]
    omitted = len(lines) - 100

    return (
        "\n".join(head)
        + f"\n\n... [PRUNER: {omitted} lines of diff omitted to preserve context window] ...\n\n"
        + "\n".join(tail)
    )
