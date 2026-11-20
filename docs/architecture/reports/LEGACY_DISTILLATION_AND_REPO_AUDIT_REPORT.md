---
title: "Ecosystem Repository Audit & Distillation Master Plan"
description: "Ecosystem Repository Audit & Knowledge Distillation Master Plan for 10-Day Sunsetting into DNK-Ecom_OS."
mrh_id: "docs/architecture/reports/LEGACY_DISTILLATION_AND_REPO_AUDIT_REPORT.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/reports/LEGACY_DISTILLATION_AND_REPO_AUDIT_REPORT.md"
> purpose: "Ecosystem Repository Audit & Knowledge Distillation Master Plan for 10-Day Sunsetting into DNK-Ecom_OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📊 Ecosystem Repository Audit & Distillation Master Plan

**Generated At:** `2026-10-27T17:08:15Z`  
**Total Scanned Size:** `11015.96 MB` | **Total Files:** `97120`  
**Governance:** `DEC-031` (10-Day Sunsetting), `DEC-033` (Zero-Bloat), `DEC-035` (Tri-Surface Mesh)

---

## ⚡ ADHD Action Summary

| Action Disposition | Count | Strategy | Action Engine |
|---|---|---|---|
| 🟢 **KEEP_AND_DISTILL** | `7` | Essential core architectures & locked decisions | Distill into `content/human/` & `content/agent/` |
| 🔷 **APP_PLUGIN_KNOWLEDGE** | `4` | Distilled passports for each target application | Written directly to `content/apps/<app_id>/` |
| 🗄️ **ARCHIVE_SANDBOX** | `25` | Quarantined in `DNK_Vibe` (Zero impact on production) | Preserve in cold sandbox, 0 token spend |
| 🔴 **DEAD_BLOAT_PURGE** | `1` | Obsolete caches, dead duplicates, dormant clones | Purge via `scripts/system/cleanup_dead_bloat.sh` |

---

## 📦 App & Plugin Knowledge Library (`DNK-Ecom_OS/content/apps/`)
Target application passports created with machine-readable `spec.md`, `invariants.md`, `audit_context.md`, and `llms.txt`:

- **`content/apps/shopify-theme-blocks/`**: Shopify Theme Blocks 2.0 & Liquid Engine
- **`content/apps/video-ai-creator/`**: Video AI Creator & Gemini Omni Pipeline
- **`content/apps/spatial-canvas-dag/`**: Spatial Canvas DAG & Task Forest
- **`content/apps/sovereign-agent-microkernel/`**: Sovereign Agent Microkernel (Denchik / FastMCP)
- **`content/apps/chrome-extension-runner/`**: Chrome Extension Standard & DevTools Automation

---

## 🗂️ Audit Breakdown: `DNK_Vibe` (29 Repositories Scanned)

| Repository Name | Size | Files | Git Status | Bloat Markers | Disposition | Action Rationale |
|---|---|---|---|---|---|---|
| **Agents Room** | 135.89 MB | 21 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **Comfy UI** | 68.63 MB | 1548 | Branch: `HEAD` (1 commits) | .git, .venv, .git | 🔷 `APP_PLUGIN_KNOWLEDGE` | Knowledge source for dedicated application/plugin passport |
| **DNK_Chrome_Plugins** | 34.06 MB | 298 | Non-Git | Clean | 🔷 `APP_PLUGIN_KNOWLEDGE` | Knowledge source for dedicated application/plugin passport |
| **DeepSeek HArness** | 405.85 MB | 24360 | Branch: `master` (16511 commits) | node_modules, node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **Done_DNK_Projects** | 290.72 MB | 5 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **ECC** | 52.11 MB | 3735 | Branch: `main` (2703 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **ERPNEXT ReBurn** | 15.94 MB | 330 | Branch: `main` (5 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **GSD** | 64.66 MB | 3948 | Branch: `next` (5917 commits) | node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **Hermes Agent** | 616.84 MB | 21007 | Branch: `main` (50 commits) | __pycache__, node_modules, .pytest_cache, node_modules, __pycache__, .venv, .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **M-kraft.top_Vibe** | 0.0 MB | 0 | Non-Git | Clean | 🔴 `DEAD_BLOAT_PURGE` | Legacy dormant repository; candidate for cold archive |
| **Macbook Utilits** | 321.82 MB | 2456 | Branch: `main` (1939 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Legacy dormant repository; candidate for cold archive |
| **ODS** | 10.99 MB | 1048 | Branch: `main` (3266 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Legacy dormant repository; candidate for cold archive |
| **Octop** | 48.27 MB | 1984 | Branch: `main` (481 commits) | node_modules, .venv, .git | 🗄️ `ARCHIVE_SANDBOX` | Legacy dormant repository; candidate for cold archive |
| **OnePersonCompany** | 34.93 MB | 1729 | Branch: `main` (1 commits) | node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Legacy dormant repository; candidate for cold archive |
| **Open Design Local** | 300.14 MB | 16017 | Branch: `main` (1 commits) | node_modules, node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **Usefull_Repos** | 142.5 MB | 861 | Non-Git | .next, node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **VirtualFittingRoom** | 2.32 MB | 137 | Branch: `feature/initial-setup` (1 commits) | .git, node_modules | 🗄️ `ARCHIVE_SANDBOX` | Legacy dormant repository; candidate for cold archive |
| **_ Архітектура агентної OS** | 0.01 MB | 7 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **chief-of-staff-2** | 1.14 MB | 88 | Branch: `main` (1 commits) | .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **codegraph** | 143.91 MB | 1068 | Branch: `main` (1046 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **craftile_editor** | 1.93 MB | 256 | Branch: `main` (1 commits) | .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **creator-os-starter** | 11.59 MB | 723 | Branch: `main` (2 commits) | node_modules, .next, .venv, .git | 🔷 `APP_PLUGIN_KNOWLEDGE` | Knowledge source for dedicated application/plugin passport |
| **elephant-goldfish-model** | 4.56 MB | 304 | Branch: `main` (1 commits) | .venv, .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **fumadocs** | 42.08 MB | 2102 | Branch: `dev` (1 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **pmx-canvas** | 23.57 MB | 1021 | Branch: `main` (465 commits) | node_modules, .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **roast-room** | 4.24 MB | 184 | Branch: `main` (1 commits) | .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |
| **scriptwriter** | 2370.94 MB | 2423 | Branch: `main` (35 commits) | node_modules, .git | 🔷 `APP_PLUGIN_KNOWLEDGE` | Knowledge source for dedicated application/plugin passport |
| **thoughtdag** | 172.55 MB | 2861 | Branch: `main` (684 commits) | node_modules, .git | 🟢 `KEEP_AND_DISTILL` | High architectural relevance; core foundation for DEC-030..DEC-043 |
| **tributary** | 12.28 MB | 518 | Branch: `feature/i18n-multilingual-support` (48 commits) | node_modules, .git | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |

---

## 🗂️ Audit Breakdown: Sibling Workspaces (`..`)

| Workspace Name | Size | Files | Git Status | Bloat Markers | Disposition | Action Rationale |
|---|---|---|---|---|---|---|
| **AI YouTube** | 306.51 MB | 29 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **DNK-e.com** | 2.01 MB | 102 | Branch: `main` | __pycache__, .git | 🟢 `KEEP_AND_DISTILL` | Active e-commerce production domain |
| **Digital Dropshiping** | 8.13 MB | 9 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **ReBurn** | 0.02 MB | 7 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **SHOPIFY** | 5103.6 MB | 5830 | Non-Git | __pycache__, .git, node_modules | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **SMM materials** | 119.68 MB | 7 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **WEB Builder** | 76.84 MB | 94 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Pre-DNK legacy folder; candidate for cold compression archive |
| **Реклама** | 64.7 MB | 3 | Non-Git | Clean | 🗄️ `ARCHIVE_SANDBOX` | Reference sandbox library |

---

## 🚀 Execution Runbook for Swarm Agents (Antigravity + Denchik + Gerych)

1. **Step 1 (Denchik - AST Code Mode):**
   - Execute `python3 scripts/system/distill_knowledge_to_ecom_os.py` to refresh all `DEC-*` decisions and invariants in `DNK-Ecom_OS/content/`.
2. **Step 2 (Antigravity - Quality Gate):**
   - Verify `DNK-Ecom_OS` repository size remains `< 2,000 KB` (`du -sh ../DNK-Ecom_OS`).
3. **Step 3 (Gerych - Safe Bloat Cleanup):**
   - Review dry-run: `bash scripts/system/cleanup_dead_bloat.sh --dry-run`.
   - Execute deletion: `bash scripts/system/cleanup_dead_bloat.sh --execute`.
4. **Step 4 (Knowledge Index Verification):**
   - Launch FastMCP server or test Fumadocs: `pnpm --prefix ../DNK-Ecom_OS dev`.
