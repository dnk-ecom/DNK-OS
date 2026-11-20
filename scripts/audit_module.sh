#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/audit_module.sh"
# purpose: "Run focused ZettCode audit against a specific DNK_HUB module without context bloat."
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
DNK_HUB_DIR="$(cd "$SCRIPT_DIR/../../DNK_HUB" && pwd)"

TARGET_MODULE="${1:-apps/api}"
TARGET_PATH="$DNK_HUB_DIR/$TARGET_MODULE"

if [ ! -d "$TARGET_PATH" ]; then
    echo "❌ Помилка: Модуль $TARGET_PATH не знайдено."
    echo "Використання: $0 [apps/api | apps/canvas | services/dnk_shopify]"
    exit 1
fi

echo "🔍 Перевірка та оновлення токенів Google Cloud..."
python3 "$SCRIPT_DIR/sync_gcp_tokens.py"

echo "🔍 Запуск ZettCode аудиту для модуля: $TARGET_MODULE"
echo "📂 Шлях: $TARGET_PATH"

zettcode -w "$TARGET_PATH"
