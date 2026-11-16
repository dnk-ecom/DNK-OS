# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shrine_buy_buttons_height_and_liquid_whitespace_ast.md"
# purpose: "Technical playbook for modern Shopify Theme Blocks buy buttons height customization, customizer schema hierarchy, and Liquid AST whitespace trimming validation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-10-09"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛍️ Shrine Theme Buy Buttons Height & Liquid AST Whitespace Playbook

## 1. Problem Statement & Architecture Context
In modern Shopify OS 2.0 themes (e.g., Shrine theme, Horizon, Dawn 15+ Theme Blocks architecture):
1. **Schema & Logic Decoupling**: Schema settings reside in `blocks/*.liquid` (e.g. `blocks/product_buy-buttons.liquid`), while HTML rendering and styling live inside reusable snippets (e.g. `snippets/buy-buttons.liquid`).
2. **Customizer Discovery & Schema Positioning**: If button height sliders are appended to the end of a 40+ setting block schema or buried under secondary sections, merchants perceive them as missing. In theme blocks with large settings manifests, vital sizing controls MUST be placed directly after primary switches (`General` / `skip_cart`) under an explicit visual header (e.g. `📏 Button Height (Desktop & Mobile)`).
3. **Dynamic Checkout Button Height Resistance**: Styling only `.product-form__submit` leaves Shopify Dynamic Checkout (`.shopify-payment-button__button`, `[role="button"]`, and internal payment iframes) at hardcoded default heights (usually `4.6rem` / `46px`). Complete CSS overrides require both `min-height: ... !important;` and `height: auto;`.
4. **Quantity Input Misalignment**: If the quantity selector is displayed on the same row (`.product-form__quantity-and-btn`), changing button height without synchronizing the quantity input breaks vertical alignment and row symmetry.
5. **CRO Shipping Estimator Schema Ordering**: In conversion-rate-optimization (CRO) blocks, input prefix texts (e.g., `Order prefix text` / `order_text`) must precede visual group headers (e.g., `🚚 Delivery Dates Range`) so merchants configure the sentence flow naturally in the theme editor.
6. **Liquid AST Validator False Positives**: Static AST / syntax validators that check tag balancing (`if`/`endif`, `for`/`endfor`) often use naive regexes (`\{%\s*if\b`) which fail to recognize whitespace-trimming tags (`{%- if` and `{%- endif`). This results in false "Missing endif tags" errors on valid production themes.

---

## 2. Prominent Schema Settings (`blocks/product_buy-buttons.liquid`)
Place slider controls directly near the top of `settings` in `blocks/product_buy-buttons.liquid` under a prominent header:

```json
{
  "type": "header",
  "content": "📏 Button Height (Desktop & Mobile)"
},
{
  "type": "range",
  "id": "button_height",
  "label": "Button height (desktop)",
  "min": 30,
  "max": 80,
  "step": 1,
  "unit": "px",
  "default": 46,
  "info": "Sets the minimum height of the buy buttons (Add to cart, dynamic checkout, skip cart). Default: 46px."
},
{
  "type": "range",
  "id": "button_height_mobile",
  "label": "Button height (mobile)",
  "min": 30,
  "max": 80,
  "step": 1,
  "unit": "px",
  "default": 44,
  "info": "Sets the minimum height of the buy buttons on mobile screens. Default: 44px."
}
```

> **Invariant Check**: In Shopify schema, range settings must strictly satisfy `(max - min) % step == 0`. `(80 - 30) % 1 = 50 % 1 = 0`.

---

## 3. High-Specificity CSS & Button Height Overrides (`snippets/buy-buttons.liquid`)
Apply scoped styles ensuring all checkout variants, skip-cart buttons, payment iframes, and adjacent quantity selectors respect the custom height:

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

{%- if block.settings.button_height_mobile != blank -%}
  @media screen and (max-width: 749px) {
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
      min-height: {{ block.settings.button_height_mobile }}px !important;
      height: auto;
    }
  }
{%- endif -%}
```

---

## 4. CRO Block Settings Flow & Dynamic Alpha Colors
1. **Settings Reading Hierarchy**:
   Inputs configuring prefix copy (e.g., `Order prefix text`) must strictly appear before the header introducing date ranges (`🚚 Delivery Dates Range`):
   ```json
   {
     "type": "text",
     "id": "order_text",
     "label": "Order prefix text",
     "default": "Order in the next"
   },
   {
     "type": "header",
     "content": "🚚 Delivery Dates Range"
   },
   {
     "type": "text",
     "id": "receive_text",
     "label": "Receive prefix text",
     "default": "to receive between"
   }
   ```

2. **Native Liquid Opacity for Border/Accent Hex Colors**:
   Always compute dynamic RGBA colors via Shopify Liquid's `color_modify` filter instead of string manipulation or hardcoded alpha hexes:
   ```liquid
   {% assign border_color = b_settings.border_color | default: '#EADFD3' %}
   {% assign border_opacity = b_settings.border_opacity | default: 100 %}
   {% assign border_alpha = border_opacity | divided_by: 100.0 %}
   {% assign border_color_final = border_color | color_modify: 'alpha', border_alpha %}
   {% if border_color_final == blank %}
     {% assign border_color_final = border_color %}
   {% endif %}
   ```
   Inject as CSS custom property: `--dnk-se-border-c: {{ border_color_final }};`.

---

## 5. AST Validator Whitespace Trimming Fix (`theme_ast_validator.py`)
To prevent false syntax rejections during automated verification, Liquid tag regexes must support optional whitespace-trimming hyphens `{%-?` and `-?%}`:

```python
# Before (Buggy - missed tags using {%- or -%}):
TAG_PAIRS = {
    "if": re.compile(r"\{%\s*if\b(?!else|elsif)"),
    "endif": re.compile(r"\{%\s*endif\b"),
}

# After (Correct - matches both standard and trimmed tags):
TAG_PAIRS = {
    "if": re.compile(r"\{%-?\s*if\b(?!else|elsif)"),
    "endif": re.compile(r"\{%-?\s*endif\b"),
}
```

Also update schema and comment patterns:
```python
SCHEMA_PATTERN = re.compile(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}", re.DOTALL)
COMMENT_PATTERN = re.compile(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", re.DOTALL)
```
