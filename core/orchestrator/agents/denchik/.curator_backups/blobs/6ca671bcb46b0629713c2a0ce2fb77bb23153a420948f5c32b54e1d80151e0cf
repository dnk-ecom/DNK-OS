# --- DNK-MRH-HEADER ---
# mrh_id: "references/canonical_theme_refactor_pipeline.md"
# purpose: "Canonical Reference for Dual-Directory Sync, Sanitization, Registry Generation, and Release Packaging."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🚀 Canonical Shopify Theme Refactor & Packaging Pipeline

## Architecture Overview
The canonical theme refactor pipeline (`scripts/system/theme_refactor_pipeline.py`) standardizes theme management between the canonical upstream Git submodule (`services/dnk_shopify/DNK-e.com`) and the decoupled working/release copy (`services/dnk_shopify/DNK_Horizon_Tinker`).

```
                ┌─────────────────────────────────┐
                │   services/dnk_shopify/         │
                │        DNK-e.com                │
                │  (Upstream Submodule / SSOT)    │
                └───────────────┬─────────────────┘
                                │
                      `sync`    │ (Zero-Diff Mirroring)
                                ▼
                ┌─────────────────────────────────┐
                │   services/dnk_shopify/         │
                │     DNK_Horizon_Tinker          │
                │  (Decoupled Working Copy)       │
                └───────┬───────────────┬─────────┘
                        │               │
        `sanitize` &    │               │ `validate`
     `registry` Audit   │               │ (Packets 1-4 Gate)
                        ▼               ▼
          mega_component_registry.json  0 Blocking Violations
                        │               │
                        └───────┬───────┘
                                │ `package`
                                ▼
                ┌─────────────────────────────────┐
                │ DNK_Horizon_Tinker_Theme_v1.0.0 │
                │             .zip                │
                │    (Production Clean Release)   │
                └─────────────────────────────────┘
```

## CLI Operations
The CLI driver provides individual targeted subcommands and a full end-to-end execution mode (always invoke via project virtualenv `./.venv/bin/python3` due to `pydantic` dependency in AST compiler):

| Command | Action | Key Verification |
|---|---|---|
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py sync` | Mirrors all 8 theme directories and config files from `DNK-e.com` to `DNK_Horizon_Tinker` | Zero diffs across all tracked directories |
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py sanitize` | Audits JS assets (`assets/main.js`) for domain locks (`window.stop()`) and verifies security snippets | Confirm license bypass stubs and `country-blocker.liquid` |
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py registry` | Extracts metadata for all blocks, sections, and snippets via `ThemeAdapter` | Generates `services/dnk_shopify/mega_component_registry.json` (549 components) |
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py validate` | Runs validation gates for Packets 1 through 4 across both directories | 0 blocking violations |
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py package` | Builds clean production ZIP without `.git`, `.DS_Store`, or `.py` files | Computes SHA256 and verifies internal ZIP directory structure (819 files, 2.81 MB) |
| `./.venv/bin/python3 scripts/system/theme_refactor_pipeline.py all` | Runs all 5 phases sequentially | End-to-end certification |

## Operational Invariants & Pitfalls
- **Virtualenv Interpreter SSOT**: Running with system `python3` fails with `ModuleNotFoundError: No module named 'pydantic'`. Always execute via `./.venv/bin/python3`.
- **Single Canonical SSOT & Deduplication**: All theme assets, submodules, and working copies are unified strictly in `services/dnk_shopify/` (`DNK-e.com` as submodule SSOT, `DNK_Horizon_Tinker` as working copy). Duplicate directories under `services/dnk_store_studio/themes/` are completely removed. Engine adapters (`ThemeAdapter`, `ThemeExporter`, `ThemeMigrationOrchestrator`) and validators prioritize `services/dnk_shopify/`.
- **Packet Validator Import & Path Standard**: Validator scripts (`scripts/validate_shopify_packet*.py`) must default to `services/dnk_shopify/DNK-e.com` and explicitly import standard library dependencies (`import os`, `import sys`, `import re`) to prevent `NameError: name 'os' is not defined`.
- **Liquid Compiler Tag Pair & Whitespace Standard**: When compiling and pairing Liquid tags, syntax parsers must recognize whitespace-suppressing tags (`{%-` and `-%}` via regex `r"\{%-?\s*([a-zA-Z0-9_]+)"`) and maintain paired sets including `capture`/`endcapture` and `raw`/`endraw`.
- **Monorepo Root Hygiene Standard**: Any test persistence or temporary databases must strictly use hidden directories (`./.data/`) rather than creating naked root folders like `./data/`, preserving 100% compliance with `scripts/system/root_hygiene_guard.py`.

## Verification Suite
Regression tests are maintained under `tests/shopify/test_theme_refactor_pipeline.py`:
- `test_pipeline_security_sanitization`
- `test_pipeline_dual_directory_sync`
- `test_pipeline_os2_packet_validation_gates`
- `test_pipeline_mega_registry_integrity`
- `test_pipeline_release_zip_packaging`
- `test_pipeline_end_to_end_execution`
