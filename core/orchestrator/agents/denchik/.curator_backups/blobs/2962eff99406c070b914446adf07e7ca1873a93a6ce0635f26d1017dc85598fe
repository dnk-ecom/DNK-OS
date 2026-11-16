---
title: "Shopify Theme Blocks UX, Liquid Color Filter and Button Specificity Playbook"
category: "software-development"
tags: ["shopify", "liquid", "color_modify", "theme-blocks", "ux", "css-specificity"]
---
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_theme_blocks_ux_and_liquid_color_modify_playbook.md"
# purpose: "Playbook for Shopify Liquid Color Modification, Block Schema UX Discoverability, and High-Specificity CSS Button Overrides."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-09"
# author: "DNK OS Gerych Prime & Maksym"
# --- END DNK-MRH-HEADER ---

# 🛍️ Shopify Theme Blocks UX, Liquid Color Filter & Button Specificity Playbook

## 1. Liquid Color Modification Filter (`color_modify`)
When creating widgets or theme blocks that allow users to control border or background opacity via a range setting (e.g. `0` to `100%`), NEVER concatenate raw hex strings or use CSS `opacity` on the container (which fades child text and icons).

### Correct Liquid Pattern:
```liquid
{% assign border_color = b_settings.border_color | default: '#EADFD3' %}
{% assign border_opacity = b_settings.border_opacity %}
{% if border_opacity == blank %}
  {% assign border_opacity = 100 %}
{% endif %}
{% assign border_alpha = border_opacity | divided_by: 100.0 %}
{% assign border_color_final = border_color | color_modify: 'alpha', border_alpha %}
{% if border_color_final == blank %}
  {% assign border_color_final = border_color %}
{% endif %}
```
This produces valid `rgba(...)` output in CSS custom properties:
```css
--dnk-se-border-c: {{ border_color_final }};
```

## 2. Block Schema Ergonomics & Discoverability
In blocks containing 30+ settings (e.g. `product_buy-buttons`), merchants will not find critical dimensional settings if they are appended to the bottom or buried inside low-priority sub-headers.

### Best Practices:
1. **Promote Primary Dimensions**: Place height and layout controls at the top of the schema (immediately after the `General` header / core checkboxes).
2. **Distinctive Visual Header**: Use an emoji and clear naming (e.g., `"📏 Button Height (Desktop & Mobile)"`).
3. **Avoid Unnecessary `visible_if` Restrictions**: Do not hide core dimension sliders behind conditional style toggles unless they are strictly irrelevant.
4. **Natural Sentence Flow**: If settings compose a sentence (e.g. `"Order in the next [Timer] to receive between [Dates]"`), the prefix input (`order_text`) must precede the range header (`🚚 Delivery Dates Range`).

## 3. High-Specificity CSS Button Overrides
Shopify themes often hardcode `height` or `line-height` on native `.product-form__submit` or dynamically injected payment button iframes.

### Robust Override Pattern:
```liquid
{%- if block.settings.button_height != blank -%}
  #ProductSubmitButton-{{ section.id }},
  #SectionAtcBtn-{{ section.id }},
  #ProductForm-{{ section.id }} .product-form__submit,
  #ProductForm-{{ section.id }} .shopify-payment-button__button,
  #ProductForm-{{ section.id }} .shopify-payment-button [role="button"],
  #ProductForm-{{ section.id }} .shopify-payment-button iframe,
  .product-form__buy-buttons-block--{{ block.id }} .product-form__submit,
  .product-form__buy-buttons-block--{{ block.id }} .shopify-payment-button__button,
  .product-form__buy-buttons-block--{{ block.id }} .shopify-payment-button [role="button"],
  .product-form__buy-buttons-block--{{ block.id }} .shopify-payment-button iframe,
  #ProductForm-{{ section.id }} .product-form__quantity-and-btn--stretch-quantity .quantity,
  .product-form__buy-buttons-block--{{ block.id }} .product-form__quantity-and-btn--stretch-quantity .quantity {
    min-height: {{ block.settings.button_height }}px !important;
    height: auto;
  }
{%- endif -%}
```

## 4. Shopify Schema Validation Limits
- `options[].label` must be `<= 50` characters. Exceeding 50 characters fails schema validation on save.
- Detailed explanations must be placed in `info`, not `label`.
- `default: ""` on `type: "text"` is invalid and must be omitted or replaced with non-empty defaults.
- **Section Block Schema `type` Requirement**: When exporting or generating block schema JSON intended to be added to a section's `"blocks": [ ... ]` array, the block object **MUST** define `"type": "<block_type_identifier>"`. Omission results in Shopify aborting with `FileSaveError: Invalid block '<name>': type is required`. The `type` must strictly match the Liquid case statement in the section (`{%- when 'block_type_identifier' -%}`).
- **Attribute Isolation in Section Blocks**: Block objects nested within a section's `"blocks": [ ... ]` list must **NOT** carry root-level section/file attributes such as `"tag": null` or `"presets": [ ... ]`. Those belong only to top-level section schemas or standalone theme block files (`blocks/*.liquid`).
