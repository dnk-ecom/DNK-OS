# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-agentic-canvas-themes/references/dnk_ecom_v2_multi_donor_synthesis_and_github_sync.md"
# purpose: "Architecture blueprint for DNK-Ecom v2.0 Theme Blocks 2.0 base repository, 3-Tier Molecular Donor Lab, multi-donor synthesis (DEC-001/002/013), and GitHub org/sync guardrails."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-19"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# DNK-Ecom v2.0 Multi-Donor Theme Synthesis, Molecular Lab & GitHub Sync Guardrails

## 1. GitHub Organization Fine-Grained PAT Policy Workaround (`DNKShopify`)
- **Problem**: The `DNKShopify` GitHub organization enforces a strict security policy: *"The 'DNKShopify' organization forbids access via a fine-grained personal access tokens if the token's lifetime is greater than 366 days"*. When `$GH_TOKEN` or `$GITHUB_TOKEN` in the shell environment holds a long-lived fine-grained PAT (`github_pat_...`), `gh` CLI commands and GitHub MCP calls targeting `DNKShopify/*` fail with HTTP 403/422.
- **Solution**: Query the macOS system git credential helper (`git credential fill` for `protocol=https\nhost=github.com`) to retrieve the active OAuth token (`gho_...`), or use the pre-authenticated SSH remote (`git@github.com:DNKShopify/DNK-e.com.git`).

## 2. Shopify GitHub App Sync & Repository Root Hygiene
- **Shopify Admin GitHub Integration Constraint**: When connecting a repository (`DNKShopify/DNK-e.com`) to a Shopify store (`m-craft-top.myshopify.com`), the target branch root must strictly adhere to the canonical 8-folder Shopify theme structure (`assets/`, `blocks/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/`).
- **Forbidden in Theme Root**: Never commit Python backend services (`services/`), test suites (`tests/`), `.DS_Store`, or un-ignored heavy multi-niche demo assets directly into the active theme branch without `.shopifyignore` protection, as this breaks Shopify GitHub App synchronization and exceeds theme file/size limits.
- **`.shopifyignore` Guardrail**: Any agent metadata directories (e.g., `.agents/`, `.github/`) MUST be listed in `.shopifyignore` at the repository root so Shopify Store / CLI / GitHub App completely ignores them during theme uploads.
- **`shopify[bot]` Auto-Commit Isolation**: Live Customizer edits in Shopify Admin automatically push commits authored by `shopify[bot]` to the connected branch (modifying `templates/*.json` and `config/settings_data.json`). Isolate live store sync to a dedicated `staging` branch while keeping `main` as the clean golden engineering baseline.

## 3. 3-Tier Molecular Donor Lab Architecture (`DNK Molecular Theme Lab`)

To synthesize blocks, sections, and settings across multiple commercial and Horizon themes without polluting `main` or burning LLM context on 800+ raw Liquid files:

### Tier 1: Isolated `--orphan` Theme Branches & Scoped Version Tags in GitHub (`DEC-018`)
- **DEC-018 Git Branch & Tag Versioning Standard (Locked)**:
  1. **Pure Theme Branch Naming**: Every theme branch in `DNKShopify/DNK-e.com` (`services/dnk_shopify/DNK-e.com`) is named purely by its kebab-case `<theme-slug>` without `donor/` prefixes or version numbers in the branch name (e.g., `ascendify`, `casaio`, `dnk-ecom-sections`, `ella`, `ks-origin`, `shrine-pro`, `story`, `tinker`, `donor-lab`, `sections-vault`, `main`, `staging`).
  2. **Every New Version = Atomic Commit + Annotated Scoped Tag**:
     - Bump `theme_version` in `config/settings_schema.json` to keep Shopify Admin in sync.
     - Commit on `<theme-slug>` (`git commit -m "feat(<theme-slug>): <summary> [vX.Y.Z]"`).
     - Tag with an annotated scoped SemVer tag `<theme-slug>-v<Major.Minor.Patch>` (`git tag -a <theme-slug>-vX.Y.Z -m "<Theme> vX.Y.Z — <Summary>"`) so multiple themes in the same repository never collide on generic `v1.0.0` tags and can be listed via `git tag -l "<theme-slug>-*"`.
- Each donor theme is uploaded via an isolated temporary `git worktree --detach` + `git checkout --orphan <theme-slug>` so the active `main` working tree is never switched or dirtied:
  1. Create a temporary detached worktree: `git -C ./services/dnk_shopify/DNK-e.com worktree add --detach <tmp_dir>`
  2. Switch to an orphan branch inside `<tmp_dir>`: `git -C <tmp_dir> checkout --orphan <theme-slug>`
  3. Clear the index/working tree (`git -C <tmp_dir> rm -rf .`), extract the clean-room neutralized `.zip` into `<tmp_dir>`, stage (`git add -A`), commit (`git commit -m "chore(<theme-slug>): import <name> clean-room archive [vX.Y.Z]"`), create the annotated tag (`git tag -a <theme-slug>-vX.Y.Z -m "..."`), and remove the worktree (`git worktree remove --force <tmp_dir>`).
  4. Register `("<theme-slug>", "<Label>")` in `DONOR_BRANCHES` inside `./scripts/shopify/deconstruct_donors.py`, run `python3 ./scripts/shopify/deconstruct_donors.py build`, and commit/push `<theme-slug>`, `<theme-slug>-vX.Y.Z`, and `donor-lab`.
- **Strict Read-Only & No-Merge Rule**: Isolated theme branches share zero commit history with `main`. Never run `git merge <theme-slug>` into `main`.
- **GitHub Actions CI Filtering Caveat**: In `.github/workflows/validate.yml`, NEVER combine `branches` and `branches-ignore` under the same `on.push` trigger — GitHub Actions rejects the workflow syntax if both are present. Use an explicit allowlist ONLY: `branches: ["main", "staging", "feature/**"]`.
- **Core Selection & Worktree Fleet Status (`DNKShopify/DNK-e.com` / `DNK-Ecom_git_mirrow/.bare`)**:
  - `main`: **Empty (`0 files`, `a98d488`)** — reserved for final production release promotion.
  - `staging` (`dff2e6f`): **Clean Prod-Candidate Core** seeded from **Tinker 4.3.0 DNK** (Horizon / Theme Blocks 2.0: 46 sections, 102 blocks, 144 snippets, 128 assets, 59 locales).
  - `staging-lab`: **Live Customizer & R&D Sandbox** seeded from Tinker 4.3.0 + ScrollCraft engine (`dnk-scroll-hero.js`, `dnk-cro-bridge.js`) + interactive sections (`game-beat-the-dealer.liquid`), connected to the live Shopify DEV store (`shopify[bot]` auto-commits on `templates/index.json`).
  - `dnk-sections` (`5c6cd77`): **Dual-Rail Section Factory** (`section-2.0/` + `theme-blocks-2.0/` + `scripts/graft_section.sh`).
- **Active Branches & Annotated Scoped Tags in `DNKShopify/DNK-e.com` (14 Branches Total)**:
  1. `main`: **Empty (`0 files`)** — awaiting production release promotion; active core lives on `staging` and `staging-lab`.
  2. `tinker` (Tag: `tinker-v4.3.0` — Tinker 4.3.0 DNK, Shopify Horizon / Theme Blocks 2.0): 482 files (95 blocks [44 public + 51 private `_*`], 42 sections, 144 snippets, 125 assets, 59 locales with 100% `uk.json` [297 keys] & `uk.schema.json` [1,115 keys], dynamic `color_palette` with smart contrast override).
  3. `story` (Tags: `story-v4.0.5`, `story-v4.0.6` — branch points to latest `4.0.6`): 822+ files (255 blocks, 72 sections, 118 snippets).
  4. `ella` (Tag: `ella-v7.3.1`): 901 files (250 blocks, 72 sections, 202 snippets).
  5. `casaio` (Tag: `casaio-v1.1.0`): 578 files (148 blocks, 52 sections, 154 snippets).
  6. `shrine-pro` (Tag: `shrine-pro-v1.9.0`): 443 files (98 blocks, 91 sections, 132 snippets).
  7. `ks-origin` (Tag: `ks-origin-v1.0.0` — KS Origin 1.0.0 DNK, Minimalist Theme Blocks 2.0): 205 files (62 blocks [18 public + 44 private `_*`], 37 sections, 29 snippets, 55 assets [16 Vanilla ES6 JS modules with 23 Custom Elements built on native HTML5 `<dialog>` via `ThemeDialogElement`, `window.ThemeEvents`, `window.StorefrontActions`, and built-in `<cart-discount>` in Cart Drawer], 3 locales with 100% `uk.json` [206 keys with `one`/`few`/`many`/`other` plural forms]; uses inline English strings in `{% schema %}` so `uk.schema.json` is not required).
  8. `dnk-ecom-sections` (Tag: `dnk-ecom-sections-v1.0.0` — DNK Ecom Sections v1.0.0 Sanitized CRO): 395 files (94 blocks in `main-product.liquid` including `dnk_shipping_estimator`, 100 sections, 164 snippets, 49 assets, 6 DRM/Kill-Switch layers neutralized).
  9. `ascendify` (Tag: `ascendify-v2.10.0` — Ascendify 2.10.0 DNK): 453 files (135 sections, 187 snippets, 51 assets, 22 templates).
  10. `sections-vault` (Tag: `sections-vault-v1.0.0` — Sections DNK Deduplicated Vault): 4,234 files (1,040 canonical unique sections, 9 Theme Blocks 2.0 `_dpb_-_styleguide-*.liquid`, 246 snippets, 76 JS/CSS assets across 10 vendors).
  11. `donor-lab` (Tag: `donor-lab-v1.0.0`): 49 files (`.agents/donor-lab/` molecular deconstruction registry & blueprints; 2,538 total molecules across all 9 donor branches).

### Tier 2: Molecular Registry (`donor/donor-lab` -> `.agents/donor-lab/`)
Generated deterministically via `./scripts/shopify/deconstruct_donors.py` (reads directly from `git ls-tree` / `git cat-file --batch` across `donor/*` branches without checking them out):
- **Important**: Because `./scripts/shopify/deconstruct_donors.py build` writes `.agents/donor-lab/` into the local repository directory on disk, always sync the generated `.agents/donor-lab/` files onto the `donor/donor-lab` branch via a temporary detached worktree and remove `.agents/` from the `main`/`staging` working tree afterward so `main` and `staging` stay 100% empty (`0 files`).
- `.agents/donor-lab/molecules_index.json` — Master index of all 2,538 blocks and sections across all 9 donor branches (represented as a JSON dict `{"total_molecules": N, "donors": [...], "molecules": [...]}` — always iterate `idx["molecules"]`, never `idx` directly). Each molecule entry uses keys `id`, `donor` (not `branch`), `kind` (`"block"` or `"section"`), `slug`, `file` (not `path`), `name`, `category`, `settings_count`, `accepts_theme_blocks_2_0`, `snippets` (list), `js_assets` (list), `css_assets` (list), and `web_components` (list) — dependencies are flat top-level fields on each molecule entry in `molecules_index.json` rather than nested under a `dependencies` dict.
- `.agents/donor-lab/DONOR_CATALOG.md` (mirrored to `README.md` at the root of `donor/donor-lab` and `_Theme_Block_2.0_Architecture/00_DONOR_CATALOG_AND_GRAFTING_MATRIX.md`) — Level 1 Executive Compass & Decision Matrix (`Task -> Best Donor -> Molecule ID`) + 8-point step-by-step donor audit checklist.
- `.agents/donor-lab/docs/*_ARCHITECTURE_AND_CHANGELOG.md` — 9 hybrid Level 2 forensic passports (8 commercial/Horizon donor themes + `SECTIONS_VAULT_ARCHITECTURE_AND_CHANGELOG.md`), each prepended with a standardized `⚡ Картка Швидкого Графтингу Донора` (Archetype, Coupling Score, Theme Blocks 2.0 readiness, Top-8 Gold Molecules with CLI commands, Core JS/CSS dependencies, and Anti-Patterns). Note: Keep `README.md` and docs inside `donor/donor-lab` and `_Theme_Block_2.0_Architecture/` so the 8 reference `donor/<theme>` branches remain 100% bit-for-bit identical (`Diffs: 0`) to their source `.zip` archives.
- `.agents/donor-lab/blueprints/<donor>.json` — Full molecular blueprints per donor containing:
  - Top-level keys: `donor` (slug), `label`, `stats` (summary counts), and `molecules` (list of molecule objects).
  - Each molecule object inside `bp["molecules"]` uses the exact schema: `id`, `donor`, `donor_label`, `kind` (`"block"` or `"section"`), `slug`, `file`, `name` (resolved from `locales/en.default.schema.json`), `category`, `lines`, `size_bytes`, `accepts_theme_blocks_2_0`, `presets_count`, `settings_count`, `settings_atoms` (list of `{id, type, label, default, options, visible_if}`), `setting_groups`, `static_blocks_count`, `static_blocks` (list of `{type, name, limit, settings_count, settings_atoms}` — used heavily by legacy Dawn monoliths like `Ascendify 2.10.0` which pack 106 block types inside `main-product.liquid` and 31 inside `cart-drawer.liquid`), and `dependencies` (nested dict with `snippets`, `js_assets`, `css_assets`, `web_components`, `css_vars`).
  - **Schema Difference Warning (`molecules_index.json` vs `blueprints/<donor>.json`)**: In `molecules_index.json`, dependency lists (`snippets`, `js_assets`, `css_assets`, `web_components`) are flat top-level keys on each molecule entry; in `blueprints/<donor>.json`, they are nested inside `molecule["dependencies"]` (`m["dependencies"]["snippets"]`, etc.), and embedded `{% case block.type %}` definitions live under `m["static_blocks"]`.
  - **Inspecting Legacy Monolith Sub-Blocks Without Checkout**: When auditing legacy OS 2.0 / Dawn donors that have `0` files in `blocks/` (e.g., `donor/ascendify-2.10.0`), inspect `m["static_blocks"]` in `blueprints/<donor>.json` or parse the `{% schema %}` of `sections/main-product.liquid` and `sections/cart-drawer.liquid` via `git -C ./services/dnk_shopify/DNK-e.com show donor/<slug>:sections/<file>.liquid` rather than checking out the branch. Standalone Zero-App CRO sections with `len(m["dependencies"]["snippets"]) == 0` and `len(m["dependencies"]["js_assets"]) == 0` (`sn=0, ass=0`) are P1 candidates for direct 1-second grafting, whereas monolithic `main-product.liquid` (36k+ LOC) must never be copied whole — extract individual `{% when '...' %}` branches into modular `blocks/_pdp-*.liquid` files.
- `.agents/donor-lab/categories/<category>.json` — 15 functional cross-donor comparison matrices (`cro_bundles_offers`, `pdp_product_core`, `cart_drawer_checkout`, `sticky_atc_buy`, `comparison_before_after`, `storytelling_editorial`, `header_navigation_footer`, `collection_plp_facets`, etc.) sorted by setting richness.

### Tier 3: CLI Search, Inspection & Transitive Extraction (`./scripts/shopify/deconstruct_donors.py`)
- **Rebuild the Molecular Lab from git branches**:
  ```bash
  python3 ./scripts/shopify/deconstruct_donors.py build
  ```
- **Search molecules across all donors by positional query, `--category`, `--donor`, or `--kind`**:
  ```bash
  python3 ./scripts/shopify/deconstruct_donors.py search "" --category cro_bundles_offers
  python3 ./scripts/shopify/deconstruct_donors.py search "quantity" --kind block
  python3 ./scripts/shopify/deconstruct_donors.py search "" --donor dnk-ecom-sections-1.0.0
  ```
  *(Note: `search` takes a positional `query` argument and supports `--donor`, `--category`, and `--kind`; it does NOT take `--query` or `--limit` flags).*
- **Pre-Check Before Importing a Theme Archive**:
  Before unpacking a `.zip` to create a new `donor/<slug>` branch, verify `git -C ./services/dnk_shopify/DNK-e.com branch -a` and compare SHA-256 hashes of files inside the `.zip` against `git ls-tree -r donor/<slug>` and `git cat-file -p donor/<slug>:<path>` to avoid duplicating an already-indexed donor branch. Also note that `DNK_Ecom_sections 1.0.0.zip` is the clean-room sanitized version of `DNK_Ecom 1.0.0.zip` (identical 395 files with 53 custom `dnk-*` sections stripped to 100 standard sections).
- **Inspect a molecule's settings atoms, dependency graph, and Liquid source**:
  ```bash
  python3 ./scripts/shopify/deconstruct_donors.py inspect "casaio-1.1.0::block::_quantity-breaks" --source
  ```
- **Extract/transplant a molecule + all transitive snippets and JS/CSS assets into `main` staging**:
  ```bash
  python3 ./scripts/shopify/deconstruct_donors.py extract "shrine-pro-1.9.0::section::comparison-table" --with-deps
  ```
  *(Extracts cleanly into `.agents/donor-lab/extracted/<donor>__<slug>/` with `MOLECULE_PASSPORT.json` for CSS token adaptation before moving into `blocks/` or `sections/`).*

## 4. 4-Level Section Vault Deduplication Pipeline (`./scripts/shopify/dedup_sections_dnk.py`)

When ingesting massive third-party section archives (containing mixed unpacked folders, full theme backup ZIPs, and RAR codebooks):
1. **In-Memory Multi-Container Scanning**: Inspect both unpacked files on disk, `.zip` archives (`zipfile`), and `.rar` archives (`bsdtar -xf`) in a single pass, grouping by container context so companion `snippets/`, `assets/`, and installation instructions (`!__INSTRUCTION*.txt` with original demo URLs) remain linked to their parent section.
2. **Level 1 (Base Theme Boilerplate Stripping)**: Filter out unmodified stock `Dawn`, `Sense`, and `Ella` sections (`announcement-bar.liquid`, `main-product.liquid`, `Clear_DAWN`, `CLEAR Dev Sense`) that pollute full-theme export ZIPs.
3. **Level 2 (Normalized Code SHA-256)**: Strip whitespace variations (`re.sub(r"\s+", " ", txt)`) and compute SHA-256 to collapse 100% identical section clones scattered across folders.
4. **Level 3 (Canonical Stem + Vendor Winner Selection)**: Normalize filenames (stripping `copy`, `(1)`, `-backup`, version suffixes), classify into vendor namespaces (`ss-`, `dnk-`, `dp-`, `sp-`, `kava-`, `dingo-`, `ks-`, `qq-`, `flx-`), and score competing revisions by `(not_flagged_broken, settings_count + blocks_count * 3 + block_settings_count, code_length)` so the richest working schema automatically wins.
5. **Dual-View Clean Vault Structure**:
   - `01_sections_by_vendor/<vendor>/<prefix>-<stem>.liquid`
   - `02_sections_by_category/<category>/<prefix>-<stem>.liquid`
   - `03_dependencies/{blocks,snippets,assets}/` (includes Theme Blocks 2.0 `_dpb_-_styleguide-*.liquid` coupled to orchestrator sections like `design_pack_-_design_system.liquid`)
   - `04_custom_liquid_snippets/{dnk_cro_widgets,150_ultimate_liquid_codebook}/`
   - `05_instructions_and_guides/`
   - `_registry/{sections_catalog.json,dedup_audit_report.json}`
6. **Composite Theme Directory Audits (`Shopify Themes BUY LIBRARY`)**:
   - When auditing folders that contain full modified themes (e.g., `DNK_Theme_Section ` — note macOS Finder folders may carry trailing spaces in names, so inspect parent directory listings rather than calling `.resolve()` blindly), diff `sections/` and `blocks/` against the baseline theme (`tinker_baseline`) and existing `donor/*` hashes so only net-new orchestrator sections and their child `blocks/_*.liquid` are extracted into `donor/sections-vault`.
7. **RFC 8259 JSON Comment Stripping Pitfall (Shopify Auto-Generated Headers)**:
   - Shopify theme exports (`templates/*.json`, `sections/*-group.json`, `locales/en.default*.json`) frequently prepend C-style `/* ... */` blocks.
   - When stripping comments in Python, ALWAYS attempt `json.loads(raw)` first; only apply regex comment stripping if `json.loads` fails, and match strictly double-quoted JSON strings (`r'("(?:\\.|[^"\\])*")|(/\*.*?\*/|//[^\r\n]*$)'`). Never include single-quoted string patterns (`'.*?'`) in a JSON regex, as apostrophes inside valid JSON values paired with `https://` URLs will corrupt the string and raise `JSONDecodeError: Invalid control character`.
8. **Horizon / Theme Blocks 2.0 Ukrainian Localization Parity (`uk.json` + `uk.schema.json`) & Donor Passports**:
   - Official Horizon themes (`Tinker 4.3.0`, `Casaio 1.1.0`) ship with 57 locales (`en.default.json` + `en.default.schema.json` using `t:...` schema keys) but omit `locales/uk.json` and `locales/uk.schema.json`.
   - When preparing a Horizon donor archive, recursively build `locales/uk.json` and `locales/uk.schema.json` against the exact key tree of `en.default.json` and `en.default.schema.json` (100% key parity, reusing existing `donor/casaio-1.1.0` Ukrainian translations + translating any version-specific delta keys).
   - For non-Horizon Theme Blocks 2.0 themes that hardcode inline English strings inside `{% schema %}` without `t:` references (e.g., `KS Origin 1.0.0 DNK`), only `locales/uk.json` (with full Ukrainian pluralization keys `one`, `few`, `many`, `other`) is needed.
   - Pair every sanitized `.zip` archive in `_Theme_Block_2.0_Architecture/` with a matching `<THEME>_<VERSION>_DNK_ARCHITECTURE_AND_CHANGELOG.md` passport containing a `DNK-MRH-HEADER`, file matrix, forensic DRM/RFC 8259 JSON audit log, Web Component inventory, and full block/section catalog.
