<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_reliability_landmines_and_importer_sync_guide.md"
purpose: "Canonical reference for the 14 Shopify Theme Importer & Runtime Landmines that pass theme-check but fail in production, distilled from shopify-theme-builder assimilation."
canonical_source: true
status: "Active"
version: "1.2.0"
updated_at: "2026-10-08"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🚨 Shopify OS 2.0 Reliability & Importer Landmines Playbook

Standard linter tools (`shopify theme check`) only inspect surface-level Liquid syntax. They miss critical structural and schema traps that cause Shopify's Theme Importer (ZIP upload and GitHub Sync) to silently drop sections, produce HTTP 404s, or break runtime storefront operations.

---

## 💣 The 14 Hidden Landmines & Safe Replacements

### 1. `{% stylesheet %}` and `{% javascript %}` Silent Section Drop
* **Trap**: Shopify Theme Importer silently strips sections containing `{% stylesheet %}` or `{% javascript %}` tags without raising errors during ZIP extraction or GitHub sync. Templates referencing those sections then produce 404 errors.
* **Fix**: Never use `{% stylesheet %}` or `{% javascript %}`. Use `{% style %}#Section-{{ section.id }} { ... }{% endstyle %}` for scoped dynamic CSS, and external assets (`assets/*.css`, `assets/*.js`) linked via `{{ 'file.css' | asset_url | stylesheet_tag }}`.

### 2. Block `name` Exceeding 25 Characters
* **Trap**: Section schema block `name` strings longer than 25 characters are rejected by Shopify's theme synchronization engine. This causes the entire section or template to fail registration.
* **Fix**: Enforce strict length constraint: `len(block["name"]) <= 25`. E.g., change `"Rating (reviews metafield)"` (26 chars) to `"Rating (Reviews)"` (16 chars).

### 3. Invalid `color_scheme_group` Role Keys
* **Trap**: Adding unapproved keys (e.g. `"shadow"`, `"card"`, `"border"`) to `color_scheme_group` roles invalidates the store's entire color palette. The theme drops custom styling and falls back to browser-default serif typography (Times New Roman).
* **Fix**: Restrict roles strictly to the 10 approved keys:
  `background`, `text`, `primary_button`, `on_primary_button`, `primary_button_border`, `secondary_button`, `on_secondary_button`, `secondary_button_border`, `links`, `icons`.

### 4. Layout Static Section vs Section Group Collision
* **Trap**: Calling a static section tag `{% section 'cart-drawer' %}` inside `layout/theme.liquid` alongside section groups (`{% sections 'footer-group' %}`) breaks layout compilation.
* **Fix**: Place utility sections like Cart Drawer inside `sections/footer-group.json` or embed as a snippet `{% render 'cart-drawer' %}` rather than a root layout static section.

### 5. Nested Filters in `image_tag` Arguments
* **Trap**: Piping filters inside argument expressions like `{{ image | image_tag: alt: image.alt | escape }}` throws `LiquidHTMLSyntaxError`.
* **Fix**: Assign and escape into a local variable first:
  ```liquid
  {% assign image_alt = image.alt | default: shop.name | escape %}
  {{ image | image_tag: alt: image_alt, loading: 'lazy' }}
  ```

### 6. Single-Variant Products Missing Hidden `id` Input
* **Trap**: Hiding the variant selector when `product.has_only_default_variant == true` without rendering `<input type="hidden" name="id" value="{{ product.selected_or_first_available_variant.id }}">` breaks Add-to-Cart and Dynamic Checkout ("Buy it now").
* **Fix**: Always include the hidden variant ID input unconditionally inside `<form action="/cart/add" ...>`.

### 7. Custom Elements Defaulting to `display: inline`
* **Trap**: Custom HTML tags (e.g. `<cart-drawer>`, `<predictive-search>`, `<variant-selects>`) default to browser `display: inline`, ignoring margins, paddings, and width definitions.
* **Fix**: Declare `:where(cart-drawer, predictive-search, variant-selects) { display: block; }` in global CSS tokens.

### 8. Flex/Grid Children Causing Mobile Horizontal Overflow
* **Trap**: Flexbox and CSS Grid children have an implicit `min-width: auto`, which causes wide image carousels or table rows to trigger horizontal scrollbars on mobile viewports.
* **Fix**: Enforce `min-inline-size: 0` (or `min-width: 0`) on all flex/grid items and scroll wrappers.

### 9. Directional `transform: translateX()` in RTL Locales
* **Trap**: Logical CSS properties (`margin-inline-start`) auto-mirror in RTL layouts (Arabic, Hebrew), but `transform: translateX(...)` does not, reversing slide animations.
* **Fix**: Use CSS variables for coordinate multipliers or `[dir="rtl"]` overrides:
  ```css
  :root { --dir-mult: 1; }
  [dir="rtl"] { --dir-mult: -1; }
  .slider { transform: translateX(calc(var(--offset) * var(--dir-mult))); }
  ```

### 10. Declarative Scripts in Section Rendering API Updates
* **Trap**: `<script src="...">` tags injected into section HTML do not execute when the section is re-rendered via the Section Rendering API (`fetch('?section_id=...')`).
* **Fix**: Wrap section logic in Web Components whose `connectedCallback()` manages state and imperative initialization upon DOM insertion.

### 11. Masking Linter Exit Codes in Build Pipelines
* **Trap**: Piping CLI commands (e.g. `shopify theme check | tail -n 20`) causes the shell to return the exit code of `tail` (0), hiding lint failures from CI/CD gates.
* **Fix**: Run commands bare or enable `set -o pipefail` in shell scripts.

### 12. Deprecated Runtime Filters
* **Trap**: Using deprecated filters such as `payment_icon_png_url` or `img_url` without modern dimensions triggers shop deprecation warnings and performance degradation.
* **Fix**: Use `image_url` with explicit width descriptors and `payment_type_svg_tag`.

### 13. Shopify Theme Editor JSON Collisions
* **Trap**: Committing changes to `config/settings_data.json` while a merchant or admin is active in the Theme Editor leads to overwriting live customizations.
* **Fix**: Never commit the `current` object in `settings_data.json` directly from code generators; only update `presets.Default`.

### 14. Asset Directory Clutter and Path Traversal
* **Trap**: Placing nested directories inside `assets/` (e.g. `assets/css/main.css`) fails in Shopify. All theme assets must reside in a flat root inside `assets/`.
* **Fix**: Keep `assets/` strictly flat (`assets/main.css`, `assets/component-hero.js`).

### 15. Trailing Commas in `{% schema %}` JSON Blocks & Settings
* **Trap**: Leaving a trailing comma before a closing bracket (`]` or `}`) inside `{% schema %}` (e.g. after adding a new block or setting to massive sections like `main-product.liquid` with 90+ blocks) violates RFC 8259 JSON and crashes the Shopify Theme Customizer with silent parsing failures or `JSONDecodeError: Illegal trailing comma`.
* **Fix**: Sanitize schema JSON strings with regex `re.sub(r',\s*([\]}])', r'\1', schema_str)` before verification and ensure valid syntax via `json.loads`.

### 16. Standalone vs PDP Block Dual-Track Architecture for E-commerce Widgets
* **Trap**: Building interactive storefront widgets (e.g. Free Shipping Countdown, Geo-location Badges) only as an internal section block restricts portability, preventing merchants from using them on landing pages, cart drawers, or outside `main-product.liquid`.
* **Fix**: Produce dual artifacts: (1) an integrated theme block snippet registered in `main-product.liquid` schema for native dragging in PDP, and (2) a standalone section + zero-dependency copy-paste snippet in `Sections DNK/` using client-side geo-detection (`/browsing_context_suggestions.json`) and fallback to `localization.country.iso_code`.

### 17. Comment Headers in `templates/*.json` & `config/` Breaking Template Registration
* **Trap**: Auto-generated C-style comment headers (`/* IMPORTANT: The contents of this file are auto-generated... */` injected by Dawn/ThemeKit exports) at the top of `templates/*.json` (e.g. `templates/product.json`, `product.*.json`) violate RFC 8259 standard JSON. While local CLI servers may tolerate them, Shopify's cloud Theme Importer (ZIP upload) fails to register the template family. The theme imports without a hard error, but the Theme Editor Customizer dropdown displays: `"No templates found for products"` (or collections/pages), while the homepage renders normally.
* **Fix**: Strip comment headers using `re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL).strip()` across all `templates/*.json`, `config/*.json`, and `locales/*.json`. Validate with strict `json.loads` before packaging the theme ZIP, and ensure the ZIP root contains `templates/`, `sections/`, etc., directly without `.DS_Store` or `__MACOSX`.

### 18. Theme Block Snippet Scope & Parent `section` Object Isolation
* **Trap**: In Shopify OS 2.0 Theme Blocks architecture (`blocks/*.liquid`), invoking a snippet via `{% render 'buy-buttons' %}` does NOT automatically inherit the parent `section` object. If the snippet targets element IDs using `{{ section.id }}` (e.g. `#ProductSubmitButton-{{ section.id }}`), `section.id` evaluates to an empty string (`#ProductSubmitButton-`). This silently disables targeted scoped styles and JavaScript event listeners.
* **Fix**: Always pass `section: section` explicitly:
  ```liquid
  {% render 'buy-buttons', block: block, product: product, section: section %}
  ```
  Additionally, back ID selectors with robust class selectors (`.product-form__submit`, `.atc-button`) to guarantee styling lands regardless of snippet scoping.

### 19. Hidden Schema Controls (`visible_if`) & Missing Fallbacks
* **Trap**: Gating essential dimension controls behind conditions (e.g. `"visible_if": "{{ block.settings.atc_label_2 != blank }}"`) completely conceals the control in the Shopify Customizer when the merchant has no second label line. Concurrently, snippet Liquid checking the same condition skips inline padding styles entirely, resulting in shrunken, misaligned buttons.
* **Fix**: Keep critical sizing controls (such as vertical padding / height) unconditional in the schema. Implement a defensive 3-tier fallback in Liquid:
  ```liquid
  {% assign atc_pad_y = block.settings.atcbuttonpadding | default: block.settings.atc_button_padding_y | default: 20 %}
  ```

### 20. ATC Button Padding & Quantity Selector Height Alignment
* **Trap**: When button height is adjusted via vertical padding (`padding-top` / `padding-bottom`), an adjacent quantity picker inside a flex row (`.product-form__quantity-and-btn`) does not resize automatically, appearing smaller or awkwardly offset.
* **Fix**: Force flex children to stretch and set the quantity input wrapper to 100% height:
  ```css
  .product-form__quantity-and-btn {
    align-items: stretch !important;
  }
  .product-form__quantity-and-btn .quantity {
    min-height: 100% !important;
    height: 100% !important;
  }
  ```

### 21. Missing Canonical Root Template Breaking Custom Template Tree (`No templates found for products`)
* **Trap**: In Shopify OS 2.0, all custom templates (e.g. `templates/product.1-the-heart-of-the-family.json`, `templates/product.custom.json`) strictly depend on the canonical root template (`templates/product.json` or `templates/product.liquid`). If a theme export or zip package includes dozens of custom product templates but omits `templates/product.json` (or if `product.json` was discarded during zip extraction due to a parsing/schema error), Shopify's template indexing engine fails completely:
  1. The Theme Editor customizer dropdown displays: `"No templates found for products"`.
  2. The `+ Create template` button disappears from the dropdown modal.
  3. All custom product templates become orphaned and cannot be assigned to products or previewed in the customizer dropdown.
  4. Storefront product URLs return HTTP 404!
* **Fix**:
  1. Always ensure `templates/product.json` (or `templates/product.liquid`) exists at the root of `templates/` before packaging any Shopify theme.
  2. If the theme only contains custom product templates (e.g. exported from a theme where `product.json` was renamed or deleted), duplicate the primary or default custom template (such as `product.default.json` or `product.1-*.json`) to `templates/product.json`.
  3. Validate that `templates/product.json` defines a valid `sections` dictionary with `main` section type matching the theme's core product section (e.g. `main-product`).

### 22. Theme Customizer Dropdown Desync & Live Preview Click-Through Navigation
* **Trap**: In draft (unpublished) themes, the top navigation dropdown in the Shopify Theme Editor can suffer from administrative search indexing delays or cached state, showing `"No templates found for products"` even when templates exist in the codebase, especially if no products are explicitly assigned to `product.json` or if the sales channel index is lagging.
* **Fix**: Instead of navigating through the top search dropdown modal:
  1. Click directly on any product card or link inside the interactive mobile/desktop canvas preview iframe on the homepage (e.g. in "Featured Collection" or "New Arrivals").
  2. The Shopify Theme Editor automatically catches the navigation event and shifts the editor context directly to that product and its assigned template.
  3. Alternatively, verify in Shopify Admin -> Products that at least one product has **Active** status and is published to the **Online Store** sales channel.

### 23. Theme ZIP Upload Forking (New Theme ID) vs Stale Browser Tab Desync
* **Trap**: Uploading a `.zip` archive via `Online Store > Themes > Add theme > Upload zip file` always creates a **new theme instance with a brand new Theme ID** (`admin.shopify.com/.../themes/<NEW_THEME_ID>/editor`). If the developer or merchant continues working in an existing browser tab pointing to the previous draft (`themes/<OLD_THEME_ID>/editor`), they are still inspecting the stale, un-updated theme. This leads to the false conclusion that local code fixes or added templates "did not work".
* **Fix**:
  1. Always check the theme ID in the URL: `.../themes/<THEME_ID>/editor`.
  2. After uploading a new ZIP archive, go back to the Themes dashboard and explicitly click **Customize** on the newly created theme in the Theme Library.
  3. Alternatively, for fast in-place recovery on the currently open theme without uploading a full ZIP: open `... > Edit code` on that specific theme, click `Add a new template` under `Templates`, select `Product` > `JSON`, name it `product`, and paste the clean `templates/product.json` content directly. Saving immediately restores the template tree and customizer dropdown in that specific theme ID.

---

## 🎨 Design Tokens: RGB Triplet Pattern & Fluid Clamp Typography

### Space-Separated RGB Triplets (Universal Alpha Channel)
Declare colors as triplets without commas or `rgb()` wrapper:
```css
:root {
  --color-background: 255 255 255;
  --color-foreground: 18 18 18;
  --color-primary: 0 90 220;
}
```
Usage in Liquid sections allowing arbitrary opacity:
```css
.card {
  background-color: rgb(var(--color-background));
  border: 1px solid rgb(var(--color-foreground) / 0.12);
  box-shadow: 0 4px 12px rgb(var(--color-foreground) / 0.08);
}
```

### Fluid Typography Clamp Calculations
Prevent rigid breakpoint jumps with viewport-fluid typography:
```css
:root {
  --font-heading-hero: clamp(2rem, 1.2rem + 3.2vw, 4.5rem);
  --font-heading-section: clamp(1.5rem, 1.1rem + 1.8vw, 2.75rem);
  --font-body: clamp(0.95rem, 0.9rem + 0.25vw, 1.125rem);
}
```
