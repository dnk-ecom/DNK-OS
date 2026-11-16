#!/usr/bin/env bash
# ==============================================================================
# DNK OS :: Hermes Agent Enhancement Installer & Migration Script
# ==============================================================================
# Purpose: Applies all DNK OS adaptations (Vertex AI ADC, adaptive responsive
#          banner, dynamic capabilities showcase, Gemini model auto-prefixing,
#          and Zero-Local-Env symlink hygiene) to any Hermes Agent release in 1 command.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$(pwd)}"

cd "$TARGET_DIR"

echo "=================================================================="
echo "⚡ [DNK OS] Installing Hermes Agent Enhancements in: $TARGET_DIR"
echo "=================================================================="

# 1. Verification
if [ ! -f "$TARGET_DIR/cli.py" ] || [ ! -d "$TARGET_DIR/hermes_cli" ]; then
    echo "❌ Помилка: Директорія $TARGET_DIR не схожа на hermes-agent (не знайдено cli.py або hermes_cli)."
    exit 1
fi

# 2. Runtime Environment Hygiene (Zero Local Environments)
RUNTIME_VENV="${HOME}/.dnk_runtime/venvs/hermes-agent"
if [ ! -d "$RUNTIME_VENV" ]; then
    RUNTIME_VENV="${HOME}/.dnk_runtime/venv"
fi

if [ -d "$RUNTIME_VENV" ]; then
    if [ ! -L "$TARGET_DIR/.venv" ]; then
        if [ -d "$TARGET_DIR/.venv" ]; then
            echo "⚠️  Знайдено фізичний .venv у репозиторії. Видаляємо дублікат згідно з DNK_Vibe/GEMINI.md..."
            rm -rf "$TARGET_DIR/.venv"
        fi
        echo "🔗 Створюємо симлінк: .venv -> $RUNTIME_VENV"
        ln -s "$RUNTIME_VENV" "$TARGET_DIR/.venv"
    else
        echo "✅ Симлінк .venv вже налаштовано на: $(readlink "$TARGET_DIR/.venv")"
    fi
else
    echo "⚠️  Увага: Центральне середовище $RUNTIME_VENV не знайдено."
fi

# 2.1 Node.js Environment Hygiene (Centralized node_modules)
NODE_CENTRAL="${HOME}/.dnk_runtime/node_environments/hermes-agent"
mkdir -p "$NODE_CENTRAL"

for mod_pair in "node_modules:node_modules" "ui-tui/node_modules:ui-tui_node_modules" "web/node_modules:web_node_modules" "apps/desktop/node_modules:desktop_node_modules"; do
    local_path="${mod_pair%%:*}"
    central_name="${mod_pair##*:}"
    target_mod="$TARGET_DIR/$local_path"
    central_mod="$NODE_CENTRAL/$central_name"

    if [ -d "$target_mod" ] && [ ! -L "$target_mod" ]; then
        echo "⚠️  Знайдено фізичну папку $local_path. Переносимо до $central_mod..."
        mkdir -p "$(dirname "$central_mod")"
        mv "$target_mod" "$central_mod"
        ln -s "$central_mod" "$target_mod"
        echo "🔗 Створено симлінк: $local_path -> $central_mod"
    elif [ ! -e "$target_mod" ] && [ -d "$central_mod" ]; then
        ln -s "$central_mod" "$target_mod"
        echo "🔗 Відновлено симлінк: $local_path -> $central_mod"
    fi
done

# 3. Apply DNK Patches
PATCH_FILE="$SCRIPT_DIR/dnk_os_full_hermes_v0230.patch"

if [ -f "$PATCH_FILE" ]; then
    echo "📦 Перевірка та застосування патча DNK OS..."
    if git apply --check "$PATCH_FILE" 2>/dev/null; then
        git apply "$PATCH_FILE"
        echo "✅ Патч успішно застосовано через git apply!"
    elif git apply --check -3 "$PATCH_FILE" 2>/dev/null; then
        git apply -3 "$PATCH_FILE"
        echo "✅ Патч застосовано з 3-way merge!"
    else
        echo "ℹ️  Файли вже містять зміни або мають конфлікти. Перевіряємо окремі маркери..."
        # Fallback check if changes already exist
        if grep -q "_TOKEN_BEARER_MAX_AGE_SEC" "$TARGET_DIR/agent/vertex_adapter.py" 2>/dev/null && \
           grep -q "_is_dnk" "$TARGET_DIR/hermes_cli/banner.py" 2>/dev/null && \
           grep -q "provider == \"vertex\"" "$TARGET_DIR/hermes_cli/model_normalize.py" 2>/dev/null; then
            echo "✅ Всі доопрацювання DNK OS вже присутні в коді."
        else
            echo "⚠️  Спроба пофайлового накатування окремих патчів..."
            for p in "$SCRIPT_DIR"/00*.patch; do
                if [ -f "$p" ]; then
                    pname=$(basename "$p")
                    if git apply --check "$p" 2>/dev/null; then
                        git apply "$p"
                        echo "  + Застосовано: $pname"
                    else
                        echo "  - Пропущено або вже в коді: $pname"
                    fi
                fi
            done
        fi
    fi
else
    echo "❌ Помилка: Файл патча $PATCH_FILE не знайдено!"
    exit 1
fi

# 4. Skin & Config Sync
HERMES_DIR="${HOME}/.hermes"
mkdir -p "$HERMES_DIR/skins"

if [ -f "$SCRIPT_DIR/dnk-os.yaml" ]; then
    cp "$SCRIPT_DIR/dnk-os.yaml" "$HERMES_DIR/skins/dnk-os.yaml"
    echo "🎨 Оновлено фірмовий скін: ~/.hermes/skins/dnk-os.yaml"
fi

# 5. Quick Health Test
echo "🧪 Виконання перевірки цілісності рантайму..."
PYTHON_EXEC="$TARGET_DIR/.venv/bin/python"
if [ ! -x "$PYTHON_EXEC" ]; then
    PYTHON_EXEC="python3"
fi

if "$PYTHON_EXEC" -c "
import sys
sys.path.insert(0, '$TARGET_DIR')
from agent.vertex_adapter import has_vertex_credentials
from hermes_cli.model_normalize import normalize_model_for_provider
assert normalize_model_for_provider('gemini-4-argon', 'vertex') == 'google/gemini-4-argon'
print('  ✅ Model Normalization Test: OK')
print('  ✅ Vertex Adapter Import Test: OK')
" 2>/dev/null; then
    echo "✅ Всі внутрішні тести DNK OS пройдено успішно!"
else
    echo "⚠️  Тест рантайму видав зауваження (перевірте наявність необхідних залежностей у рантаймі)."
fi

echo "=================================================================="
echo "🎉 Встановлення завершено! Hermes Agent готовий до роботи в DNK OS."
echo "   Запуск: ./.venv/bin/python cli.py --provider vertex --model gemini-4-argon"
echo "=================================================================="

