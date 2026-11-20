#!/usr/bin/env bash
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/run_sota_leaders_audit.sh"
# purpose: "Launch autonomous Hermes-core deep audit of world leaders in Agentic Core systems and architectural adjustments for DNK OS."
# canonical_source: true
# alters_files: ["docs/architecture/reports/SOTA_WORLD_LEADERS_AGENTIC_CORE_AUDIT.md"]
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPORT_FILE="${REPO_ROOT}/docs/architecture/reports/SOTA_WORLD_LEADERS_AGENTIC_CORE_AUDIT.md"
QUERY_FILE="/tmp/hermes_sota_audit_query.txt"

HERMES_DIR="${DNK_GERYCH_DIR:-$(cd "$REPO_ROOT/.." && pwd)/Gerych-Agent}"
HERMES_PYTHON="${HERMES_DIR}/.venv/bin/python"
HERMES_EXEC="${HERMES_DIR}/cli.py"

if [ ! -x "$HERMES_PYTHON" ]; then
    HERMES_PYTHON="$HOME/.dnk_runtime/venvs/hermes-agent/bin/python"
fi

if [ ! -f "$HERMES_EXEC" ]; then
    echo "❌ Error: Hermes CLI not found at $HERMES_EXEC"
    exit 1
fi

mkdir -p "${REPO_ROOT}/docs/architecture/reports"

cat << EOF > "$QUERY_FILE"
ЗАДАЧА ВІД МАКСИМА (DNK-e.com):
Здійснити ґрунтовний автономний інженерний аудит світових лідерів у розробці Agentic Core, Agent Execution Harnesses та Multi-Agent Operating Systems (SOTA 2026).
Порівняти їхні архітектурні рішення з поточною реалізацією ядра DNK OS (FastMCP Microkernel v2.5.0, Spatial Canvas Session Router, 3 Core Workhorses, SCONES FTS5 Memory, Fan-In 4-Gate, TC-10 Quarantine, Skills Curator, Google EGM Dual-System Review, Harness² Blind Tournament, Canonical PSOD Delegation, Universal Pre-Tool Sentinel) та надати конкретні рекомендації: «ЩО НАМ СЛІД ПІДКОРИГУВАТИ».

ОБ'ЄКТИ АУДИТУ (СВІТОВІ ЛІДЕРИ):
1. Anthropic (Claude Code, Subagent Execution Loops, Tool Protocols, MCP Specification).
2. LangChain / LangGraph (Pregel cyclic state graphs, checkpointing, LangGraph Store, Human-in-the-Loop approval).
3. NousResearch (Hermes Agent v0.23, trajectory compression, toolsets, WAL state management, skills lifecycle).
4. AutoGen / AG2 & CrewAI (Multi-agent conversational DAGs, hierarchical supervisor architectures, code sandboxing).
5. Builder.io (Agent-Native) & SmythOS / CopilotKit (Visual Canvas integration, Dual-Surface Actions, node execution).
6. Cognition (Devin) & Cursor (Anysphere) (Shadow workspace execution, per-task context surgery, git worktrees, AST indexing, deterministic quality gates).
7. Google Research (Harness² / arXiv:2610.14224 & Elephant-Goldfish Model / EGM dual-system review).

5 ВЕКТОРІВ ПОРІВНЯННЯ ТА КОРЕКЦІЇ ДЛЯ DNK OS:
1. Бібліотека знань проєкту (Project Knowledge & Context Architecture):
   - Як організована L1 Account -> L2 Project DNA (brand_dna.json, project.manifest.yaml) -> L3 Tasks ієрархія у порівнянні зі світовими аналогами.
   - Що нам підкоригувати для синхронізації знань між канвасом, кодом і правилами.
2. Пам'ять системи (Multi-Tier Cognitive Memory):
   - SCONES (SQLite WAL + FTS5 full-text search) + Per-Node Context Surgery (<= 1500 токенів) проти LangGraph Store, Letta (MemGPT), Mem0.
   - Чи потрібні векторні ембедінги, чи достатньо FTS5 + Kahn DAG upstream context injection?
3. Організація сервісів та інструментів (Services & Tools Architecture):
   - Правило 3-х робочих конячок (dnk_shopify, dnk_media, dnk_distribution) + Sovereign Bricks (5 елементів: manifest, service, contracts, tests, FastMCP) + Senior Dev Solution Ladder (DEC-057) проти монолітів і безконтрольних мікросервісів.
   - Що підкоригувати для standing context diet (<= 6000 токенів).
4. Оркестрація завдань і мультиагентна взаємодія (Task Orchestration & Workflows):
   - Spatial Canvas (.canvas) + Session Router + 4-Gate Fan-In Aggregator + TC-10 Quarantine Circuit Breaker проти JSON-RPC / LangGraph State.
   - Підтримка циклів зворотного зв'язку (revision loops) та живого Human-in-the-Loop через PSOD та EGM Review.
5. Відбір і селекція навичок, гачків та скриптів (Skill Curation & Invariants):
   - 4-Vector Generalisability Test, Skill Core-Size Ratchet (<= 750 рядків + LOD), Second Violation Invariant (Pre-tool hooks) проти статичних каталогів навичок.
   - Автоматичний депрекейт та прунінг застарілих навичок.

СТРУКТУРА ТА ВИМОГИ ДО ЗВІТУ:
1. Збережи повний звіт у файл:
   ${REPORT_FILE}
2. Формат:
   - Повний MRH-хедер стандарту DNK-STD-0075 (author: "DNK-e.com Maksym & Antigravity", status: "Active", version: "2.0.0").
   - Резюме для Максима (Executive Summary / ADHD Cards).
   - Детальний аналіз кожного з 5 векторів із порівняльними таблицями:
     [Компонент / Патерн світового лідера / Як реалізовано в DNK OS / Рекомендація та корекція].
   - Топ-7 конкретних архітектурних коригувань (Top Actionable Adjustments) для ядра DNK OS.
3. Мова: Українська, професійний інженерний стиль, конкретні схеми та конфігурації.
EOF

echo "🚀 [DNK OS] Запуск автономного дослідження Hermes Agent..."
echo "📄 Цільовий файл: $REPORT_FILE"

cd "$REPO_ROOT"
exec "$HERMES_PYTHON" "$HERMES_EXEC" --provider vertex --model gemini-4-argon -q "$(cat "$QUERY_FILE")" --oneshot
