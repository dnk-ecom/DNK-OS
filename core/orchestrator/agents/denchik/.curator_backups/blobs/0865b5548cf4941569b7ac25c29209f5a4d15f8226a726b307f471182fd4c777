<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/shopify_ai_toolkit_theme_validation_and_standards.md"
purpose: "Official Shopify AI Toolkit standards for theme validation, LiquidDoc, and modular theme block architecture."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-28"
author: "DNK-e.com Maksym & Gerych"
--- END DNK-MRH-HEADER -->

# Shopify AI Toolkit: Theme Standards & Validation Reference

Extracted from official `Shopify/Shopify-AI-Toolkit` (v1.17.0+).

## 1. Modern Theme Directory Architecture

Focus generation on **modular components** (snippets, blocks, sections); merchants manage page layout templates in the Theme Editor.

```
.
├── assets     # Static assets (CSS, JS, images, fonts)
├── blocks     # Reusable, nestable, customizable theme blocks
├── config     # Global theme settings (settings_schema.json, settings_data.json)
├── layout     # Top-level wrappers (theme.liquid with content_for_header, content_for_layout)
├── locales    # Translation JSON files (en.default.json, fr.json)
├── sections   # Modular full-width components with {% schema %}
├── snippets   # Pure reusable fragments rendered via {% render %}
└── templates  # JSON or Liquid page templates
```

### Component Rules

- **`sections/*.liquid`**:
  - Modular full-width page components.
  - Must include `{% schema %}` tag.
  - Use `{{ block.shopify_attributes }}` on block wrappers for theme editor drag-and-drop.
- **`blocks/*.liquid`**:
  - Fine-grained reusable components (do not need full width).
  - Can nest child blocks via `{% content_for 'blocks' %}`.
  - Must include `{% schema %}` tag validated against `schemas/theme_block.json`.
  - Must include `{% doc %}` tag when statically rendered via `{% content_for 'block', id: '42', type: 'block_name' %}`.
- **`snippets/*.liquid`**:
  - Reusable code fragments rendered via `{% render 'snippet_name', param: value %}`.
  - Accept parameters for dynamic behavior.
  - **Mandatory LiquidDoc**: Must begin with a `{% doc %}` header block.

## 2. LiquidDoc Specification

Snippets and static blocks must include LiquidDoc:

```liquid
{% doc %}
@param {image} image - The image to render
@param {string} [url] - Optional destination URL
@example
{% render 'image', image: product.featured_image %}
{% enddoc %}
```

## 3. Encapsulated CSS & JavaScript Invariants

- Write per-component styling and scripts using `{% stylesheet %}` and `{% javascript %}` tags.
- Supported **only** inside `snippets/`, `blocks/`, and `sections/`.
- **CRITICAL INVARIANT**: Liquid is **NEVER** evaluated or rendered inside `{% stylesheet %}` or `{% javascript %}` tags. Never put `{{ settings.color }}` or Liquid loops inside these tags. Use CSS custom properties (variables) set inline on HTML wrappers instead.

## 4. Theme Check & Validation Tooling

Validation is performed via `@shopify/theme-check` engines bundled in `scripts/validate.mjs` / `_validate_theme.mjs`:

### A. Stateless Mode (Single Codeblock / Generated File)
```bash
node scripts/validate.mjs --api liquid \
  --filename <name.liquid> \
  --filetype <sections|blocks|snippets|layout|templates|locales|config|assets> \
  --context <theme|app> \
  --code '<liquid_source>'
```

- `--context app`: Use when validating Theme App Extensions (`blocks/` under extension) to allow extension schema keys (`target`, `javascript`, `stylesheet`) without triggering `Property target is not allowed` errors.

### B. Full Theme Mode (Local Theme Tree)
```bash
node scripts/validate.mjs --api liquid \
  --theme-path <absolute_or_relative_path_to_theme> \
  --files <rel_file1,rel_file2,...>
```

- Validates real filesystem tree and cross-file dependencies (locales, snippets, schemas).

## 5. Telemetry & Privacy Opt-Out

Shopify AI Toolkit scripts report telemetry to `shopify.dev/mcp/usage` by default. To disable telemetry permanently:
- Set environment variable: `OPT_OUT_INSTRUMENTATION=true` or `DO_NOT_TRACK=1`
- Or create empty opt-out file: `touch ~/.config/shopify-ai-toolkit/opt-out`
