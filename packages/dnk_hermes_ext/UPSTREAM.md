<!-- --- DNK-MRH-HEADER ---
mrh_id: "packages/dnk_hermes_ext/UPSTREAM.md"
purpose: "Upstream identification and triage list for the hermes-agent snapshot (pin target, local modifications to review)."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Draft"
version: "0.2.0"
updated_at: "2026-11-06"
author: "DNK-e.com Maksym & Claude"
--- END DNK-MRH-HEADER -->

> **Оновлення 2026-11-06 (переважає над текстом нижче).** Пін перенесено на `2bd378ed` (upstream від 2026-11-05, Hermes 0.23). Власні зміни DNK до upstream це 5 патчів у `patches/` (Vertex ADC і ротація токена, префікс `google/` для Gemini на Vertex, 3 патчі банера); вони накладаються на чистий `2bd378ed` (перевірено `git apply`). Список "108 кодових файлів" нижче стосувався старої бази `12bba22dc` і більше не актуальний. Інструменти `dnk_*` і плагіни лишаються в `overlay/` і підключаються окремо (крок T4, MCP-сервер `dnk-tools`).

# Upstream: ідентифікація і список для перегляду

**Вердикт:** найближчий upstream-коміт до вашої копії це `12bba22dc` (2026-09-02, "docs(telemetry): state the consent containment rule on operator surfaces") у `github.com/NousResearch/hermes-agent`. З ~2 374 локальних файлів 1 840 збігаються з ним байт у байт. Збіг не повний, тож це **найближчий** коміт, а не доведена база: різниця в 485 файлах це суміш ваших правок і розбіжності з реальною базою.

Теги для довідки: `v2026.8.27` (0.20.6) збігається у 1 828 файлах, `v2026.8.31` (0.21.0) у 1 538. На PyPI опубліковано лише версії до 0.19.0, тож пін робиться за git-комітом або тегом.

## Підсумок порівняння з 12bba22dc

| | файлів |
|---|---:|
| збігаються з upstream | 1 840 |
| відрізняються: 346 у `skills/`, 17 у `locales/`, 108 кодових (нижче), решта документи | 485 |
| лише локально (232): 180 у `skills/`, 52 інші, з них 33 вже в `overlay/` | 232 |

## Кодові файли, що відрізняються (108) — для перегляду

Це кандидати на ваші патчі. Найімовірніші ваші (за змістом): `agent/title_generator.py` (евристика моделей Gemini, `max_tokens`), `agent/vertex_adapter.py`, `plugins/model-providers/nvidia/__init__.py`, `plugins/model-providers/vertex/__init__.py`. Для решти не встановлено, чи це ваша правка, чи різниця версій; потрібен diff проти точної бази.

- `agent/agent_init.py`
- `agent/agent_runtime_helpers.py`
- `agent/auxiliary_client.py`
- `agent/background_review.py`
- `agent/chat_completion_helpers.py`
- `agent/codex_responses_adapter.py`
- `agent/context_compressor.py`
- `agent/conversation_compression.py`
- `agent/conversation_loop.py`
- `agent/copilot_acp_client.py`
- `agent/deadline.py`
- `agent/file_safety.py`
- `agent/gemini_native_adapter.py`
- `agent/markdown_tables.py`
- `agent/message_sanitization.py`
- `agent/monitoring/cron_health.py`
- `agent/prompt_builder.py`
- `agent/skill_utils.py`
- `agent/ssl_guard.py`
- `agent/system_prompt.py`
- `agent/title_generator.py`
- `agent/tool_dispatch_helpers.py`
- `agent/tool_guardrails.py`
- `agent/transports/chat_completions.py`
- `agent/transports/codex.py`
- `agent/vertex_adapter.py`
- `cli.py`
- `cron/scheduler.py`
- `gateway/control_socket.py`
- `gateway/delivery_ledger.py`
- `gateway/kanban_watchers.py`
- `gateway/platforms/base.py`
- `gateway/run.py`
- `gateway/scale_to_zero.py`
- `gateway/slash_commands.py`
- `gateway/status.py`
- `hermes_cli/__init__.py`
- `hermes_cli/backup.py`
- `hermes_cli/banner.py`
- `hermes_cli/browser_connect.py`
- `hermes_cli/cli_commands_mixin.py`
- `hermes_cli/config.py`
- `hermes_cli/config_defaults.py`
- `hermes_cli/cron.py`
- `hermes_cli/dashboard_procs.py`
- `hermes_cli/doctor.py`
- `hermes_cli/gateway.py`
- `hermes_cli/gitlock.py`
- `hermes_cli/main.py`
- `hermes_cli/managed_uv.py`
- `hermes_cli/memory_setup.py`
- `hermes_cli/models.py`
- `hermes_cli/observability/relay_shared_metrics.py`
- `hermes_cli/observability/shared_metrics.py`
- `hermes_cli/process_identity.py`
- `hermes_cli/setup.py`
- `hermes_cli/skin_engine.py`
- `hermes_cli/subcommands/cron.py`
- `hermes_cli/subcommands/gui.py`
- `hermes_cli/tools_config.py`
- `hermes_cli/update_cmd.py`
- `hermes_cli/update_inventory.py`
- `hermes_cli/update_receipt.py`
- `hermes_cli/web_models.py`
- `hermes_cli/web_routers/mcp.py`
- `hermes_cli/web_routers/profiles.py`
- `hermes_cli/web_routers/sessions.py`
- `hermes_cli/web_routers/tools.py`
- `hermes_cli/web_server.py`
- `hermes_logging.py`
- `hermes_state.py`
- `optional-mcps/atlassian/manifest.yaml`
- `plugins/model-providers/nvidia/__init__.py`
- `plugins/model-providers/vertex/__init__.py`
- `plugins/platforms/slack/adapter.py`
- `plugins/video_gen/fal/__init__.py`
- `pyproject.toml`
- `run_agent.py`
- `tools/approval.py`
- `tools/browser_tool.py`
- `tools/browser_use_cli.py`
- `tools/checkpoint_manager.py`
- `tools/clarify_tool.py`
- `tools/code_execution_tool.py`
- `tools/computer_use/__init__.py`
- `tools/computer_use/backend.py`
- `tools/computer_use/cua_backend.py`
- `tools/computer_use/schema.py`
- `tools/computer_use/tool.py`
- `tools/cronjob_tools.py`
- `tools/env_passthrough.py`
- `tools/environments/base.py`
- `tools/environments/local.py`
- `tools/file_operations.py`
- `tools/file_tools.py`
- `tools/mcp_tool.py`
- `tools/microsoft_graph_client.py`
- `tools/process_registry.py`
- `tools/registry.py`
- `tools/session_search_tool.py`
- `tools/skill_manager_tool.py`
- `tools/skills_tool.py`
- `tools/terminal_tool.py`
- `tools/tool_search.py`
- `toolsets.py`
- `tui_gateway/methods_profiles.py`
- `tui_gateway/server.py`
- `uv.lock`

## Файли лише локально, крім `skills/`

- `.web_ui_build.lock`
- `DNK-VIDEO-AUDIT-AND-PLAN.md`
- `__init__.py`
- `acp_registry/DIRECTORY.md`
- `acp_registry/agent.json`
- `acp_registry/icon.svg`
- `check_mrh.py`
- `debug.py`
- `docs/architecture/GERYCH_PRIME_UNIFIED_ORCHESTRATION_AND_SOTA_SPEC.md`
- `excalidraw_elements.json`
- `hermes_runtime.py`
- `index.html`
- `plugins/memory/scones/__init__.py`
- `plugins/memory/scones/plugin.yaml`
- `plugins/model-providers/groq/__init__.py`
- `scaler.sh`
- `script.js`
- `services/enqueue_test.py`
- `services/worker/README.md`
- `services/worker/health.py`
- `services/worker/logrotate.conf`
- `services/worker/monitor.sh`
- `services/worker/rotate_log.sh`
- `services/worker/worker.sh`
- `style.css`
- `telemetry/metrics/task_cost_usd_metrics.jsonl`
- `test.txt`
- `test_dir.py`
- `test_guard.txt`
- `test_in_web_ui.txt`
- `test_report.md`
- `tools/computer_use/browser_route.py`
- `tools/dnk_accounting_tool.py`
- `tools/dnk_adversarial_review_tool.py`
- `tools/dnk_assimilate_tool.py`
- `tools/dnk_collab_tool.py`
- `tools/dnk_distiller_tool.py`
- `tools/dnk_flow_tool.py`
- `tools/dnk_product_launch_tool.py`
- `tools/dnk_rag_tool.py`
- `tools/dnk_repo_map_tool.py`
- `tools/dnk_scones_tool.py`
- `tools/dnk_shopify_tool.py`
- `tools/dnk_swarm_tool.py`
- `tools/dnk_taskdna_tool.py`
- `tools/dnk_vault_tool.py`
- `tools/dnk_video_tool.py`
- `tools/dnk_visual_context_tool.py`
- `update_mrh.py`

`plugins/web/tavily/*`, `plugins/model-providers/groq/*` та `acp_registry/*` схожі на пізніші версії upstream, а не на ваші; вирішити після піна.

## Статус піна

Пін зафіксовано у `UPSTREAM.lock` (повний SHA `12bba22dc95b5fbbdc0a26461d8aed5a65ea9ce0`, підтверджено користувачем 2026-11-06). Локальна копія `core/hermes_agent` ще НЕ видалена.

**Важливе спостереження для кроку 4:** upstream має плоский layout (топ-рівневі пакети `agent`, `tools`, `hermes_cli`, ...), і локальна копія всередині використовує саме такі імпорти (`from tools.registry`, `from agent.redact`). Лише 20 файлів поза копією імпортують `core.hermes_agent.*`. Тому DNK-інструменти (`tools/dnk_*`, 16 файлів) не можна просто залишити у `tools/` встановленого пакета: їх треба винести у `packages/dnk_hermes_ext` як окремий пакет і зареєструвати через `tools.registry` (або застосувати overlay до встановленого пакета). Це потребує перевірки на Mac у єдиному venv, тому крок виконується окремо.

## План піну (S1b, частково виконано: п.1)

1. Закріпити upstream за комітом (початково `12bba22dc`).
2. Накласти `overlay/` поверх.
3. Переглянути 108 файлів зі списку; справжні патчі перенести в `overlay/patches/` як `.patch`.
4. Замінити імпорти `core.hermes_agent.*` на встановлений пакет; прибрати локальну копію.
