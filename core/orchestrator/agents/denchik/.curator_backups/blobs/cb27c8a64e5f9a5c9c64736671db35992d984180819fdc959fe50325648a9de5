# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/packet4_snippets_and_visual_assets_playbook.md"
# purpose: "Playbook for Packet 4: Snippets, CSS Tokens Harmonization & PDP Widget Isolation in Shopify OS 2.0."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🎨 Packet 4 Playbook: Snippets, CSS Tokens Harmonization & PDP Widget Isolation

## Overview
Packet 4 standardizes theme snippets, global styling tokens, and core Product Detail Page (PDP) widgets (`snippets/price.liquid`, `snippets/product-variant-picker.liquid`, `snippets/buy-buttons.liquid`, and `snippets/product-media-gallery.liquid`), migrating from Vintage/Tinker 1.0 conventions to Horizon Tinker 4.3.1.

---

## 1. Syntax Fix: Nested Selector Churn
A common defect when refactoring legacy Shopify Liquid templates is repeated selector access caused by copy-pasting section context into block context:
```liquid
{% comment %} BAD: Duplicated selector {% endcomment %}
{% if section.settings.section.settings.product_images == 'one' %}

{% comment %} GOOD: Direct valid accessor {% endcomment %}
{% if section.settings.product_images == 'one' %}
```
### Detection Recipe
Search for duplicated path fragments across snippets and sections:
```python
re.findall(r"\b([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\.\1\.\2\b", liquid_content)
```

---

## 2. Dynamic CSS Token Harmonization (Tinker 4.3.1 Palette Standard)
Vintage themes rely on flat color keys (`settings.colors_text`, `settings.colors_background_1`). Modern Tinker 4.3.1 utilizes dynamic nested palette schemas (`settings.color_palette.foreground`, `settings.color_palette.background`).

Direct references to legacy keys without fallback cause:
- Empty CSS variables: `--color-base-text: ;`
- Malformed RGB color functions: `rgba(, , , 0.5)`
- Theme preview render failures.

### Mandatory Multi-Tier Fallback Cascade
Define global theme variables in `layout/theme.liquid` before injecting into `:root`:
```liquid
{%- liquid
  assign theme_text_color = settings.colors_text | default: settings.page_text_color | default: settings.color_palette.foreground | default: '#000000'
  assign theme_bg_color_1 = settings.colors_background_1 | default: settings.page_background_color | default: settings.color_palette.background | default: '#ffffff'
  assign theme_bg_color_2 = settings.colors_background_2 | default: settings.color_palette.background | default: '#f4f4f4'
  assign theme_solid_btn_label = settings.colors_solid_button_labels | default: settings.palette_primary_button_text | default: settings.color_palette.background | default: '#ffffff'
  assign theme_outline_btn_label = settings.colors_outline_button_labels | default: settings.palette_secondary_button_text | default: settings.color_palette.foreground | default: '#000000'
  assign theme_accent_1 = settings.colors_accent_1 | default: settings.palette_primary_button_background | default: settings.color_palette.foreground | default: '#121212'
  assign theme_accent_2 = settings.colors_accent_2 | default: settings.palette_secondary_button_background | default: settings.color_palette.background | default: '#334fb4'
-%}
```
For calculated RGB and opacity values, always provide a numerical fallback:
```liquid
--sale-badge-custom-bg-color: {{ settings.sale_badge_custom_bg_color | default: theme_accent_1 }};
--sale-badge-custom-bg-color-rgb: {{ settings.sale_badge_custom_bg_color.rgb | default: '18, 18, 18' }};
```

---

## 3. Liquid Compiler & Validator Invariants
When validating or compiling Liquid templates programmatically:
1. **Hyphen-Trimmed Tags**: Opening and closing tags can include trimming hyphens (`{%-`, `-%}`, `{{-`, `-}}`). Tag-matching regex must handle hyphens:
   ```python
   re.compile(r"\{%-?\s*([a-zA-Z0-9_]+)")
   ```
2. **Tag Pairs Completeness**: Ensure the parser tracks all pairing tags:
   - `if` / `endif`
   - `unless` / `endunless`
   - `for` / `endfor`
   - `case` / `endcase`
   - `capture` / `endcapture`
   - `raw` / `endraw`
   - `schema` / `endschema`
   - `stylesheet` / `endstylesheet`
   - `javascript` / `endjavascript`

---

## 4. PDP Widget Isolation Standard
- All widget calls must use `{% render 'snippet-name', product: product, section: section %}`.
- Never use legacy `{% include %}` which leaks variables into the parent scope.
- Every snippet must start with a valid `DNK-MRH-HEADER`.
- Maintain decoupled state between variant picker change events and price updates using standard DOM dispatch events (`variant:change`).
