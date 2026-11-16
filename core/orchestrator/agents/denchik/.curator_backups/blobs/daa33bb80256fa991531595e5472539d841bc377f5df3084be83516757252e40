# 🧼 Shopify Cleanroom Theme Neutralization Architecture (3 Core Workhorses Standard)

This reference defines the deterministic architecture for One-Pass AST & JSON Cleanroom Neutralization of Shopify OS 2.0 themes in DNK OS.

## 🎯 Core Objectives
1. **Zero Theme Customizer Rendering Lockups**: Eliminate all structural JSON/Liquid mismatches (`schema.blocks` vs template instances, missing `color_scheme` tokens, invalid `select` values) that cause the Customizer to break or swallow footers.
2. **Data & Asset Decoupling**: Automatically strip hardcoded `shopify://shop_images/` links, client UUIDs, non-existent collection/product handles, and third-party app embeds.
3. **3 Core Workhorses Compliance**: No standalone micro-agents or microservices. Neutralization logic must run as a deterministic CLI pipeline, a Python service tool, or a git QA hook.

---

## 🏗️ Architectural Topology

### 1. Service Engine Tool
- **Path**: `services/dnk_shopify/tools/theme_cleanroom_neutralizer.py`
- **Function**: `shopify_neutralize_cleanroom(theme_root: str, in_place: bool = True)`
- **Key Operations**:
  - `cleanroom_sanitize_json_obj()`: Recursively walks theme JSON structures (`templates/*.json`, `sections/*.json`, `config/settings_data.json`).
  - Normalizes empty `color_scheme: ""` properties to `"scheme-1"`.
  - Replaces external image links with SVG fallback placeholders (`product-1`, `collection-1`).
  - Neutralizes invalid collection/product handles to safe defaults.
  - Automatically verifies and patches Liquid parent schema block declarations (`blocks/_product-card.liquid`).

### 2. System CLI Pipeline
- **Path**: `scripts/system/shopify_theme_neutralizer.py`
- **Usage**:
  ```bash
  python3 scripts/system/shopify_theme_neutralizer.py <path_to_theme> --write --zip clean_theme.zip
  ```
- **Output**: Produces a clean production `.zip` ready for upload into Shopify Admin.

### 3. Repository-Local QA Guards & Hooks
- **CLI Script**: `scripts/cleanroom-neutralize.mjs` (`npm run theme:neutralize`)
- **Customizer Guard**: `qa/customizer-guard.mjs` (`npm run customizer:guard`)
- **Git Hook**: `.git/hooks/pre-push` — blocks pushing unneutralized theme artifacts to Git.

---

## 🛡️ Checklist for Cleanroom Neutralization
1. **Asset Sanitization**: Remove all `shopify://shop_images/` references.
2. **Handle Isolation**: Ensure collection/product links use fallback anchors or standard routes (`routes.all_products_collection_url`).
3. **Color Scheme Fallbacks**: Every section/block setting with a color scheme must have a valid value (e.g. `"scheme-1"`).
4. **Block Parent-Child Hierarchy**: All child block types used in templates MUST be declared in the parent block/section's `schema.blocks`.
5. **Footer Group Integrity**: `sections/footer-group.json` must contain a complete block chain including `footer-utilities` with copyright & policies.
