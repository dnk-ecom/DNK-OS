---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_theme_blocks_importer_pitfalls.md"
purpose: "Reference guide for troubleshooting 'No templates found for products' and Theme Blocks importer drop in Shopify OS 2.0."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-08"
author: "DNK-e.com Maksym & Gerych"
---

# Shopify OS 2.0: "No templates found for products" & Theme Blocks Importer Pitfall

## 1. Symptom & Failure Signature
- **Symptom**: When uploading a theme ZIP (e.g. Shrine Pro 1.9.0 or custom builds) into Shopify Admin, the theme customizer displays:
  `"No templates found for products"`
  even though all `templates/product*.json` files exist locally in the ZIP.
- **Side Effect**: The customizer hides the entire "Products" dropdown section, preventing merchants from viewing, editing, or assigning custom product templates.

## 2. Root Cause Analysis
1. **Silent Importer Dropping**: Shopify's cloud ZIP ingestion pipeline strictly validates template schemas before mounting files. If a JSON template fails schema validation against the theme's Liquid sections, the importer silently discards the template without halting the entire ZIP upload.
2. **Missing Anchor Template (`templates/product.json`)**:
   Shopify Online Store 2.0 requires the base default template (`product.json`) to register the resource type in the Customizer. If `templates/product.json` is dropped or omitted (even if suffix templates `product.suffix.json` exist), Shopify flags the theme as having zero product templates.
3. **Experimental Theme Blocks Schema Mismatch**:
   - In modern themes exploring Theme Blocks (with a top-level `blocks/` directory), sections like `sections/main-product.liquid` declare `"blocks": []` in their schema and render blocks dynamically via:
     `{% content_for 'block', id: 'Details', type: 'main-product_details' %}`
   - Consequently, `templates/product*.json` contains nested blocks (`sections.main.blocks.Details.blocks`) and lacks a top-level `sections.main.block_order`.
   - On production Shopify stores where the Theme Blocks Developer Preview is disabled, Shopify's validator parses `templates/product.json` against the standard OS 2.0 schema, triggers a validation fault due to the missing `block_order` and `"blocks": []` definition in `main-product.liquid`, and silently drops `templates/product.json`.

## 3. Resolution Playbook

### Method A: Fast In-Admin Recovery (Immediate Hotfix)
1. In Shopify Admin, navigate to **Online Store > Themes**.
2. Click **... > Edit code**.
3. Under **Templates**, click **Add a new template**:
   - Template type: `Product`
   - File type: `JSON`
   - File name: `product`
4. Save the generated default OS 2.0 template.
5. Reopen **Customize**. The "Products" category and all suffix templates immediately unlock.

### Method B: Deterministic Monolithic OS 2.0 Standardization (DNK Invariant)
To permanently avoid silent drops across all store environments without relying on experimental store flags:
1. Re-inline block definitions into `sections/main-product.liquid` schema (flat blocks architecture).
2. Ensure every section in `templates/product*.json` provides:
   - A valid `"blocks"` map.
   - An explicit `"block_order"` array of block keys matching the schema.
3. Do not ship nested `blocks/` directories with `content_for 'block'` unless the target store is confirmed to have the Theme Blocks runtime flag enabled.
