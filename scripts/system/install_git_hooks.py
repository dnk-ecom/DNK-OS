#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/install_git_hooks.py"
# purpose: "Installs non-bypassable local git pre-commit hook enforcing all 8/8 checks via auto_precommit_guard.py."
# canonical_source: true
# alters_files: [".git/hooks/pre-commit"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import stat
import sys
from pathlib import Path

HOOK_CONTENT = """#!/bin/bash
# --- DNK-MRH-HEADER ---
# mrh_id: ".git/hooks/pre-commit"
# purpose: "Non-bypassable local pre-commit hook enforcing all 8/8 checks via auto_precommit_guard.py."
# --- END DNK-MRH-HEADER ---

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

echo "🛡️  [DNK OS PRE-COMMIT HOOK] Enforcing Deterministic Invariants (8/8 Checks)..."

# Detect Python virtual environment
PYTHON_BIN="python3"
if [ -f "$REPO_ROOT/.venv/bin/python3" ]; then
    PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
elif [ -f "$HOME/.dnk_runtime/venv/bin/python3" ]; then
    PYTHON_BIN="$HOME/.dnk_runtime/venv/bin/python3"
fi

"$PYTHON_BIN" scripts/system/auto_precommit_guard.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ [PRE-COMMIT HOOK FAILED] Commit rejected. Fix violations before committing."
    exit 1
fi

echo "✅ [PRE-COMMIT HOOK PASSED] All 8/8 checks passed. Proceeding with commit."
exit 0
"""


def install_hook() -> bool:
    repo_root = Path(__file__).resolve().parent.parent.parent
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        print(f"❌ .git directory not found at {repo_root}")
        return False

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    pre_commit_path = hooks_dir / "pre-commit"
    pre_commit_path.write_text(HOOK_CONTENT, encoding="utf-8")

    # Make executable (chmod +x)
    current_mode = pre_commit_path.stat().st_mode
    pre_commit_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"✅ Git pre-commit hook successfully installed at: {pre_commit_path}")
    return True


if __name__ == "__main__":
    success = install_hook()
    sys.exit(0 if success else 1)
