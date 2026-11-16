<!-- --- DNK-MRH-HEADER ---
mrh_id: "packages/dnk_hermes_ext/README.md"
purpose: "DNK-owned files extracted from the untracked core/hermes_agent so they live in git; basis for pinning hermes-agent as an external dependency."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Draft"
version: "0.1.0"
updated_at: "2026-11-05"
author: "DNK-e.com Maksym & Claude"
--- END DNK-MRH-HEADER -->

# dnk_hermes_ext

**Вердикт:** `core/hermes_agent` це знімок upstream `NousResearch/hermes-agent` (версія в `pyproject.toml` 0.21.0) з вашими доповненнями. Каталог у `.gitignore`, тому ваші файли існували лише на диску. Тут лежить їхня копія в git (`overlay/`, 33 файли: 16 `tools/dnk_*.py`, `hermes_runtime.py`, `check_mrh.py`, `update_mrh.py`, плагіни `scones` і `dnk_hub_memory`, `services/worker/*`, 2 документи). Оригінали в `core/hermes_agent` **не змінено**; імпорти `core.hermes_agent.*` працюють як раніше.

Структура `overlay/` повторює структуру upstream: після встановлення upstream за закріпленою версією вміст `overlay/` накладається поверх (див. UPSTREAM.md).
