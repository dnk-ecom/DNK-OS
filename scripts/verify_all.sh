#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/verify_all.sh"
# purpose: "Canonical deterministic 4-stage quality gate for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.1.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${HOME}/.dnk_runtime/venv/bin/python3"

if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "=========================================================="
echo "🛡️  DNK OS CANONICAL DETERMINISTIC QUALITY GATE (2026)"
echo "=========================================================="

echo "⚡ [1/4] Fast AST Syntax Compilation Check..."
"$PYTHON_BIN" "$REPO_ROOT/scripts/system/fast_compile_check.py"

echo "🛡️ [2/4] Anti-Tautology & Fake-Test AST Audit..."
"$PYTHON_BIN" "$REPO_ROOT/scripts/system/anti_tautology_guard.py"

echo "🔒 [3/4] Autonomous Pre-Commit Guard (Path Hygiene & Invariants)..."
"$PYTHON_BIN" "$REPO_ROOT/scripts/system/auto_precommit_guard.py"

echo "📄 [3.1/4] Unified MRH Header & Dual-Reader Gate..."
"$PYTHON_BIN" "$REPO_ROOT/scripts/system/check_mrh_headers.py" --audit "$REPO_ROOT/docs"

echo "🛡️ [3.2/4] Markdown Schema & Epistemic Armor Gate..."
"$PYTHON_BIN" "$REPO_ROOT/scripts/system/markdown_schema_gate.py" $(find "$REPO_ROOT/docs" -name "*.md" -not -path "*/archive/*" -not -path "*/templates/*" -not -path "*/decisions/*" -not -path "*/distillations/*")

echo "🧪 [4/4] Core Regression Test Suite..."
"$PYTHON_BIN" -m pytest "$REPO_ROOT/tests/core" --quiet --tb=short

echo "=========================================================="
echo "✅ ALL DETERMINISTIC QUALITY GATES PASSED (Exit Code: 0)"
echo "=========================================================="
