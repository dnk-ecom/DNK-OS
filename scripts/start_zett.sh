#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/start_zett.sh"
# purpose: "Launch Zettelekasten with validated Google Cloud OAuth2 token and environment."
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
python3 "$SCRIPT_DIR/sync_gcp_tokens.py"

echo "🧠 Запуск Zett (Zettelekasten) на http://127.0.0.1:6280..."
zett start
zett status
