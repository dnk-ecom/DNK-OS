#!/bin/bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/denchik.sh"
# purpose: "Canonical launcher for Denchik (Денчік) Sovereign Master Developer with Super-Builder Protocol v3."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-29"
# author: "Antigravity & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HUB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Super-Builder Protocol v3 Environment Flags
export DENCHIK_MODE=1
export DENCHIK_SUPER_BUILDER_V3=1
export HERMES_AGENT_NAME="denchik"
export FAST_MCP_IN_RAM=1
export STANDING_CONTEXT_LIMIT=6000
export BROWSER_DISABLED=1
# Single shared venv (~/.dnk_runtime/venv): forbid `uv run` from auto-syncing/installing packages.
export UV_NO_SYNC=1

# Ensure sovereign agent profile directory exists
if [ ! -d "$HUB_ROOT/core/orchestrator/agents/denchik" ]; then
    mkdir -p "$HUB_ROOT/core/orchestrator/agents/denchik" 2>/dev/null || true
fi

exec bash "${SCRIPT_DIR}/denchik_engine.sh" --agent denchik "$@"
