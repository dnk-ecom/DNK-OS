---
name: shopify-cleanroom-neutralization
description: Use when neutralizing, sanitizing, or packaging a cloned Shopify OS 2.0 theme for Theme Customizer preview and clean ZIP upload in 1 pass.
---
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-cleanroom-neutralization/SKILL.md"
# purpose: "One-Pass Shopify OS 2.0 Theme Clean-Room Neutralization & Footer/Customizer Integrity Skill."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Shopify Clean-Room Neutralization (One-Pass Protocol)

## Trigger Conditions
Use this skill whenever the user asks to:
- Neutralize or clean a cloned/external Shopify theme for testing in a new Shopify store.
- Fix broken templates, missing sections, or missing footers in Shopify Theme Customizer.
- Replace store-specific `shopify://shop_images/`, app embeds, handles, and URLs with safe fallbacks and SVG placeholders.
- Package a production-ready, Customizer-safe `.zip` archive in a single pass.

## Root Causes of Customizer & Footer Failures (Why Naive Image Stripping Fails)
When Shopify uploads a theme ZIP or opens a template in Theme Customizer, it validates the entire `templates/*.json` and `sections/*.json` AST against Liquid `{% schema %}` definitions. Any single violation causes Shopify to reject the template or abort rendering before `footer-group`:
1. **Unlisted Child Blocks in Parent Schema**: JSON templates referencing custom child blocks (e.g. `tp-card-color-thumbs`, `tp-card-sterne`, `tp-card-aktion`, `_tp-description-style`) that are missing from the parent block's `schema.blocks` array (`blocks/_product-card.liquid`, `blocks/_product-details.liquid`).
2. **Invalid `select` or Empty `color_scheme` Values**: Settings like `"color_scheme": ""` or legacy values like `"font": "var(--font-primary--family)"` / `"color": ""` not present in the schema's `options` list.
3. **Unknown/Removed Setting Keys**: Settings in `templates/*.json` or `config/settings_data.json` that no longer exist in `{% schema %}` or `config/settings_schema.json`.
4. **Foreign App Embeds & Resource Handles**: `shopify://apps/...` UUIDs in `config/settings_data.json`, `shopify://shop_images/...`, or hardcoded collection/product/blog handles that do not exist in the target store.
5. **Missing Footer Sections or Empty Menu Filter Loops**: `sections/footer-group.json` missing `footer-utilities` or footer menu loops filtering out all items when `main-menu` has no `/collections/` links, leaving empty columns.

## Numbered One-Pass Workflow
1. **Run the Deterministic Neutralizer CLI**:
   ```bash
   python3 scripts/system/shopify_theme_neutralizer.py <path_to_theme> --write --zip <output_zip_path>
   ```
2. **If the Theme Has Node QA Guards, Run Them**:
   ```bash
   npm run theme:neutralize
   npm run customizer:guard
   npm run liquid:guard && npm run schema:guard && npm run template:guard && npm run schrift:guard
   npm run qa:unit:test
   ```
3. **Verify Zero Findings**:
   Confirm 0 disallowed child blocks, 0 invalid select/color_scheme values, 0 foreign `shopify://` URIs, and 100% footer-group presence before delivering the `.zip`.
