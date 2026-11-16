# --- DNK-MRH-HEADER ---
# mrh_id: "references/shopify_staging_lab_worktree_sandbox_workflow.md"
# purpose: "Operational standard for Shopify Git bare worktree fleet, staging-lab test sandbox, and 7-module Fumadocs Section Specification Template."
# canonical_source: true
# author: "DNK-e.com Maksym & Denchik"
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-10-30"
# --- END DNK-MRH-HEADER ---

# 🧪 Shopify Git Bare Worktree Fleet, Staging-Lab Sandbox & Section Spec Standard

## 1. Architectural Fleet Topology

DNK E-Commerce theme development utilizes a high-velocity Git Bare Worktree topology (`DNK-Ecom_git_mirrow/.bare`) rather than multiple disconnected clones or frequent branch switching on a single working directory. This ensures zero cache invalidation, instant context switching, and strict isolation between experimental R&D, donor assimilation, and release candidates.

```
DNK-Ecom_git_mirrow/
├── .bare/                     # Central Git bare repository database (fetch = +refs/heads/*:refs/remotes/origin/*)
├── graft.sh                   # Root molecular/section grafting CLI dispatcher (auto-pulls staging-lab before grafting)
├── dnk-sections/              # Dual-rail component hub (section-2.0 + theme-blocks-2.0 + scripts/graft_section.sh)
├── staging-lab/               # 🧪 TEST & PREVIEW SANDBOX (Tinker 4.3.0 Horizon + ScrollCraft + CRO Bridge; live-linked to Shopify DEV Store)
├── staging/                   # 🚀 CLEAN CANDIDATE CORE (Tinker 4.3.0 Horizon baseline, 46 sections, 102 blocks, 59 locales)
├── donor-lab/                 # Molecular registry (.agents/donor-lab/: 2,538 molecules, 10 blueprints, 15 categories, 10 passports)
├── main/                      # Empty root baseline (0 files, awaiting production promotion)
└── <9 read-only orphan donors>/ # tinker, ks-origin, casaio, story, ella, shrine-pro, ascendify, dnk-ecom-sections, sections-vault
```

> **Note on Surrounding `DNKEcom/` Root Directory & Explicit User Preferences**:
> - **`_Theme_Block_2.0_Architecture/` is Strictly Local**: The `../SHOPIFY/DNKShopify/DNKEcom/_Theme_Block_2.0_Architecture/` folder is a private local audit staging area managed manually by the founder. **NEVER** diff, compare, or flag discrepancies between `_Theme_Block_2.0_Architecture/` and the GitHub repository (`donor-lab`).
> - **Keep Full Workspace Intact (`DNK-Ecom_Theme_Dev.code-workspace`)**: Do NOT remove or prune folders from `DNK-Ecom_Theme_Dev.code-workspace`. The user prefers keeping the complete workspace tree mounted.
> - **Auto-Sync in `graft.sh`**: Both `DNK-Ecom_git_mirrow/graft.sh` and `dnk-sections/scripts/graft_section.sh` automatically execute `git -C <staging-lab> pull --rebase origin staging-lab` whenever grafting into `staging-lab` so `shopify[bot]` Customizer commits are never overwritten.

---

## 2. The Role of `staging-lab`

`staging-lab` is the designated **live execution and preview sandbox**:
- **Baseline Engine**: Built on Shopify Horizon / Tinker 4.3.0 (`{% content_for 'blocks' %}`).
- **Purpose**: Live testing, Shopify CLI theme preview (`shopify theme dev`), customizer schema validation, and interactive JS/CSS debugging.
- **Invariant**: Experimental components (VTON, interactive games, new CRO widgets) MUST be tested in `staging-lab` first. They are NEVER directly injected into `staging` without passing the validation gate in `staging-lab`.

---

## 3. Grafting & Testing Workflow

### Step 1: Graft Component to `staging-lab`
When a new section or theme block is built in `dnk-sections`:
```bash
cd ../SHOPIFY/DNKShopify/DNKEcom/DNK-Ecom_git_mirrow
./graft.sh <section-name> --auto ./staging-lab
```
This script:
1. Automatically runs `git -C ./staging-lab pull --rebase origin staging-lab` to ingest any live `shopify[bot]` Customizer commits.
2. Detects the target theme rail (`theme-blocks-2.0` vs `section-2.0`) and copies:
   - `theme-blocks-2.0/sections/*.liquid` ➔ `staging-lab/sections/`
   - `theme-blocks-2.0/blocks/*.liquid` ➔ `staging-lab/blocks/`
   - `shared/assets/*` & `shared/snippets/*` ➔ `staging-lab/`

### Step 2: Live Local Validation via Shopify CLI
```bash
cd ../SHOPIFY/DNKShopify/DNKEcom/DNK-Ecom_git_mirrow/staging-lab
shopify theme dev --store <test-store.myshopify.com>
```
Verify:
1. Theme Editor Customizer displays all block schemas, presets, and localized settings (UK/EN).
2. Zero console errors, zero layout shifts (CLS < 0.1), zero horizontal scrollbar on mobile (320px–430px).
3. Web Components lifecycle binds cleanly on both initial load and Section Rendering API mutations.

### Step 3: Promotion to Clean `staging`
Once verified with 100% pass:
```bash
cd ../SHOPIFY/DNKShopify/DNKEcom/DNK-Ecom_git_mirrow/staging
git checkout staging-lab -- sections/<file>.liquid blocks/<file>.liquid assets/<file>.*
git commit -m "feat(staging): promote validated <feature> from staging-lab"
```

---

## 4. Canonical 7-Module Section Specification Standard (Fumadocs + Merchant + Agent SSOT)

Every section in `dnk-sections/sections/<slug>/` MUST have a matching specification in `../SHOPIFY/DNKShopify/DNKEcom/docs/specs/DNK_SPEC_<SECTION_NAME>.md` cloned from the golden template `../SHOPIFY/DNKShopify/DNKEcom/docs/templates/DNK_SECTION_SPEC_TEMPLATE.md` (exemplar: `docs/specs/DNK_SPEC_BEAT_THE_DEALER_BLACKJACK.md` `v2.1.0`):

1. **Fumadocs YAML Frontmatter + `DNK-MRH-HEADER`**: Includes `title`, `description`, `icon`, `category`, `slug` (`/docs/sections/<category>/<slug>`), `toc: true`, and `alters_files` listing both rails.
2. **Module 1 — Executive Summary & CRO Triggers**: Business goal, psychological triggers (e.g., *Endowed Progress*, *IKEA Effect*), and target KPI table.
3. **Module 2 — Dual-Rail Architecture (`section-2.0` & `theme-blocks-2.0`)**: File tree inside `dnk-sections/sections/<slug>/` and architectural comparison between the monolithic OS 2.0 rail and the modular Horizon Theme Blocks 2.0 rail (`{% content_for 'blocks' %}`).
4. **Module 3 — State Machine & Business Logic**: ASCII state flow, mathematical/algorithmic rules, and zero-dependency guarantees.
5. **Module 4 — Full Schema Contracts (`{% schema %}`)**: Complete parameter tables (`ID`, `Type`, `Default`, `Description`) for the section container and every atomic block in `theme-blocks-2.0/blocks/*.liquid`, plus `section-2.0` parity differences.
6. **Module 5 — Merchant Guide (Shopify Customizer Documentation)**: Step-by-step installation, Shopify Admin discount/metafield setup, display mode switching (`testing` vs `popup` vs `inline`), Klaviyo/Shopify Email customer tag automation, and troubleshooting FAQ.
7. **Module 6 — AI Agent & Developer Playbook**: Grafting CLI commands, CSS/JS scoping invariants (`#btd-root-{{ section.id }}`, IIFE), `shopify:section:select` / `shopify:section:deselect` Customizer hooks, DOM `data-*` contracts, and automated JSON schema validation recipe.
8. **Module 7 — Per-Component SemVer Changelog**: Separate version tracking table for the section container and each individual block (`blocks/<prefix>-*.liquid`), plus dated release notes and a copy-paste template for future changes.

---

## 5. Anti-Pattern & Hygiene Pitfalls

| Pitfall | Consequence | Correct Pattern |
| :--- | :--- | :--- |
| **Comparing `_Theme_Block_2.0_Architecture/` to GitHub** | False-positive drift warnings on local manual audit files | Never compare `_Theme_Block_2.0_Architecture/` against `donor-lab` or GitHub; treat it strictly as the user's private local folder. |
| **Pruning `DNK-Ecom_Theme_Dev.code-workspace`** | Removes folders the user actively uses in VS Code | Leave `DNK-Ecom_Theme_Dev.code-workspace` untouched with all workspace folders preserved. |
| **Scattered Untracked Files** | Leaving experimental files in submodules (`services/dnk_shopify/DNK-e.com`) | Always commit or work directly within the designated worktree (`staging-lab` or `dnk-sections`). |
| **Direct Staging Edits** | Breaking clean theme baseline while debugging JavaScript or CSS | Build and break in `staging-lab`; promote only deterministic, audited artifacts. |
| **Absolute Path Leaks** | Hardcoding `/Users/kuzmenko.top/...` in shell commands or configs | Always resolve paths relative to repository root (`../SHOPIFY/...`). |
| **Local Commit Isolation (Unpushed to GitHub)** | Shopify GitHub integration never syncs; merchant opens theme and sees "nothing changed" | Always run `git push origin <branch>` immediately after committing. Shopify only pulls pushed commits. |
| **Two-Way Sync Race with `shopify[bot]`** | Shopify Customizer auto-commits (`Update from Shopify for theme DNKShopify-DEV-Store`) push directly to `origin/staging-lab` (`templates/*.json`). Grafting or pushing locally without pulling first causes merge conflicts | Use `./graft.sh` (which auto-runs `git pull --rebase origin staging-lab`) and ensure all 14 worktree branches in `.bare/config` have upstream tracking (`git branch -u origin/<branch>`). |
| **Read-Only Donor Worktree Pollution (`.DS_Store` & Stray Files)** | macOS `.DS_Store` files or stray test sections dirty read-only orphan worktrees | Keep `.DS_Store` in `.bare/info/exclude` and keep all 9 donor worktrees 100% clean (`git status --short` empty, matching their `<theme-slug>-vX.Y.Z` tag). |
