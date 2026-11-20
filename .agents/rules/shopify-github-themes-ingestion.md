---
title: "Shopify GitHub Theme Ingestion Protocol"
description: "Mandatory Protocol for Ingestion, Audit, Sanitization, and Packaging of Shopify Themes from GitHub."
mrh_id: ".agents/rules/shopify-github-themes-ingestion.md"
status: Active
version: "1.0.0"
updated: 2026-11-18
globs: "**/*"
alwaysApply: true
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: ".agents/rules/shopify-github-themes-ingestion.md"
> purpose: "Mandatory Protocol for Ingestion, Audit, Sanitization, and Packaging of Shopify Themes from GitHub."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛍️ Standard Protocol: Shopify GitHub Theme Ingestion & Packaging

Whenever the user requests to download, clone, or intake a Shopify theme from `github.com` (or any external git repository), all agents MUST strictly execute the following deterministic protocol:

## 1. Canonical Destination Directory (Zero-Pollution Invariant)
- **Target Root**: STRICTLY clone or extract into:
  `../DNKEcom/GitHub_Shopify_Themes/<theme-folder>/`
- **Quarantine Invariant**: NEVER download, clone, or unzip third-party themes directly into `DNK_HUB` root or subfolders. The theme intake directory is external to `DNK_HUB` to preserve monorepo hygiene and prevent indexer latency.

## 2. Ingestion & Shallow Clone
- Perform shallow clone to minimize disk and network overhead:
  `git clone --depth 1 <github_url> ../DNKEcom/GitHub_Shopify_Themes/<theme-folder>`

## 3. Mandatory External Asset & Reference Sanitization (Zero-Error Gate)
Before packaging for the test store, inspect and purge all broken or external links to prevent Shopify block/section/template rendering errors:
1. **Broken Snippet Renders**: Scan all Liquid files for `{% render 'snippet-name' %}` and `{% include 'snippet-name' %}`. If a referenced snippet is missing, replace it with a graceful comment or provide a safe stub snippet.
2. **Missing Section References**: Verify that every section called in `templates/*.json` or via `{% section '...' %}` exists in `sections/`.
3. **Dead Asset URLs**: Check `asset_url` calls. Ensure no references point to missing asset files.
4. **Third-Party Tracker & Script Purge**:
   - Strip hardcoded tracking scripts (Facebook Pixel, TikTok Pixel, Google Analytics, GTM, Klaviyo, Yotpo, Judge.me embeds) that could fail, cause console errors, or leak telemetry in test environments.
   - Replace any dead external CDN scripts/styles with local fallbacks or remove them if non-essential.
5. **Shopify Font & SVG Invariance**: Ensure fonts utilize standard Shopify `font_face` filters or system fonts without relying on unauthenticated remote font CDNs.

## 4. Theme Audit (`AUDIT_<theme-folder>.md`)
Generate a structured audit markdown report saved directly in:
`../DNKEcom/GitHub_Shopify_Themes/AUDIT_<theme-folder>.md`
The audit MUST cover:
- **Theme Profile**: Version, author, license, architecture (OS 2.0 vs vintage), component inventory (sections, snippets, blocks, assets, templates).
- **Static Gate Results**: Results of `shopify theme check` and lint/tests if available in the repo.
- **Sanitization Log**: Detailed ledger of stripped external scripts, missing snippet stubs, and neutralized endpoints.
- **Conversion & CRO Highlights**: Notable features to inspect for inspiration (Offer cards, Sticky ATC, Cart Drawer upsells, Timelines, Tickers, Comparison tables).
- **Test Store Deployment Guide**: Specific instructions for uploading to the test store.

## 5. Compilation & Clean Upload Packaging
Package a clean zip archive for immediate upload to the Shopify Admin theme library:
- Archive name: `../DNKEcom/GitHub_Shopify_Themes/<theme-folder>-upload.zip`
- Package composition:
  - Must include: `assets/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/`, and `blocks/` (if present) placed directly at the root of the zip archive.
  - Must EXCLUDE: `.git/`, `.github/`, `docs/`, `scripts/`, `node_modules/`, `tests/`, and OS metadata (`.DS_Store`).
  - Size budget: Must stay well below Shopify's 50 MB theme limit (preferably ≤ 5 MB).

