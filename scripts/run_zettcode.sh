#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/run_zettcode.sh"
# purpose: "Launch ZettCode with automatic Google Cloud OAuth2 token validation & refresh."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-02"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="python3"

# 1. Auto-refresh GCP Vertex AI OAuth token if older than 30 minutes
"$PYTHON_BIN" "$SCRIPT_DIR/sync_gcp_tokens.py"

# 2. Launch ZettCode passing all arguments
exec zettcode "$@"
