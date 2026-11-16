---
mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_homepage_redirect_and_404_troubleshooting.md"
purpose: "Systematic troubleshooting and isolation playbook for Shopify homepage auto-redirects, Theme Customizer 404 preview collapses, and theme packaging/upload delivery UX."
status: "Active"
version: "1.4.0"
updated_at: "2026-09-23"
author: "DNK-e.com Maksym"
---

# 🧭 Shopify Homepage Auto-Redirect, 404 Customizer Fallback & Theme Upload Playbook

When previewing, editing, or uploading a Shopify theme (especially during migrations between themes like Shrine, Dawn, Horizon, or bespoke builds), loading `/` (the homepage) may trigger an automatic client-side or server-side redirection, landing on a 404 page ("Page not found"), switching the Theme Editor template to `404 page`, or causing upload friction in the Shopify Admin.

---

## 🔍 The 4 Discrete Root Causes & Structural Failures

### 1. Theme Setting "Enable Homepage Redirect" in Liquid (`theme.liquid`)
* **Mechanism**: Custom themes often provide a theme setting allowing merchants to redirect traffic from `/` directly to a hero product or landing page.
* **Vulnerable Pattern**:
  ```liquid
  {% if settings.enablehomepageredirect and settings.redirect_url != blank and template == 'index' %}
    <meta http-equiv="refresh" content="0; url={{ settings.redirect_url }}">
    <script>
      window.location.replace("{{ settings.redirect_url }}");
    </script>
  {% endif %}
  ```
* **Failure Mode**: When executed inside the Shopify Theme Editor preview iframe without a design mode guard, it immediately redirects the preview iframe. If the target URL does not exist on the current store or market, the iframe loads 404, prompting Shopify Editor to switch the active template to `404 page`.
* **Fix**:
  1. Wrap all redirection logic in `unless request.design_mode`:
     ```liquid
     {% unless request.design_mode %}
       {% if settings.enablehomepageredirect and settings.redirect_url != blank and template == 'index' %}
         <meta http-equiv="refresh" content="0; url={{ settings.redirect_url }}">
         <script>
           if (!window.Shopify || !window.Shopify.designMode) {
             window.location.replace("{{ settings.redirect_url }}");
           }
         </script>
       {% endif %}
     {% endunless %}
     ```
  2. In the Theme Customizer sidebar: **Theme Settings (⚙️) ➡️ Homepage redirect** ➡️ Uncheck "Enable homepage redirect" or clear "Redirect URL".

---

### 2. Shopify Admin URL Redirects (`Navigation ➡️ URL Redirects`)
* **Mechanism**: Server-side 301/302 redirects managed by Shopify core under `Online Store ➡️ Navigation ➡️ View URL Redirects`.
* **Failure Mode**: If an old redirect rule exists from `/` to a specific collection, promotional page, or product handle that was renamed, unpublished, or absent on a staging/development store, Shopify immediately redirects `/` to that handle and returns HTTP 404.
* **Fix**: Check `Navigation ➡️ View URL Redirects` in Shopify Admin. Filter by Redirect from `/` and delete or update any stale mappings.

---

### 3. Shopify Markets Geolocation Auto-Redirection
* **Mechanism**: In `Settings ➡️ Markets ➡️ Preferences`, Shopify provides "Automatic redirection" based on visitor IP/country.
* **Failure Mode**: When a merchant or developer accesses the theme from an international location (e.g., Ukraine `UA`), Shopify attempts to redirect the session to the market's subfolder (e.g., `/uk`, `/en-ua`) or domain. If that market subfolder is not configured, unmapped, or missing localized templates in the unpublished draft theme, Shopify returns 404.
* **Fix**:
  1. Temporarily toggle off **Automatic redirection** in `Settings ➡️ Markets ➡️ Preferences`.
  2. Or test preview with forced market parameters: `?locale=en&country=US`.

---

### 4. App Embeds (Translation / Currency / Geolocation Switchers)
* **Mechanism**: Third-party apps (e.g. Translation Lab, Geolocation App, Langify) inject client-side switchers via `App Embeds` (`content_for_header`).
* **Failure Mode**: Scripts like `advanced-switcher.js` inspect `navigator.language` or query GeoIP APIs and invoke `window.location.replace()` without checking `window.Shopify?.designMode`.
* **Fix**:
  1. In Theme Customizer, navigate to **App embeds** (3rd tab on left panel, cube icon 🧊).
  2. Toggle off the translation/geolocation embed and verify whether the homepage loads.

---

### 5. Orphaned Market Context Files (`*.context.<market-id>.json`)
* **Mechanism**: When exporting themes from stores with customized Shopify Markets, Shopify creates market-specific context overlays like `sections/header-group.context.<market-uuid>.json` or `templates/index.context.<market-uuid>.json`.
* **Failure Mode**: When imported into another store (e.g. staging or dev store) where that specific Market UUID does not exist, Shopify's Theme Editor fails to resolve the contextual hierarchy and collapses the preview iframe into a 404 or broken editor route.
* **Fix**:
  1. Search for any context files: `find . -name "*.context.*.json"`.
  2. Remove orphaned market context files before re-packing the theme ZIP archive so that default root templates (`index.json`, `header-group.json`, `footer-group.json`) serve all markets cleanly.

---

### 6. Invalid Block Types in Template Section Schema (`templates/*.json`)
* **Mechanism**: In Shopify OS 2.0, when migrating templates across different theme versions or distinct themes (e.g. Dawn ➡️ Shrine Pro with Summer '24 Theme Blocks), block types within sections often change. For example, standard Dawn `featured-product` uses block types `title`, `price`, `variant_picker`, `buy_buttons`, whereas modern themes use `product_title`, `product_price`, `product_product-variant-picker-block` or scoped theme blocks (`blocks/*.liquid`).
* **Failure Mode**: When `templates/index.json` references block types that are NOT declared in `sections/<type>.liquid`'s schema (or missing from `blocks/`), the Shopify Liquid parser fails to compile the section. When the template render fails on the root path `/`, Shopify's engine triggers an internal fallback to `templates/404.json`, rendering the 404 page inside the Theme Editor iframe!
* **Detection & Fix**:
  1. Inspect `templates/index.json` (and all JSON templates) against the `{% schema %}` of each referenced section.
  2. Verify that every key in `section.blocks.*.type` exists in the section's `schema.blocks[].type` or is an existing theme block in `blocks/<type>.liquid`.
  3. Remove or re-map deprecated/incompatible blocks.

---

### 7. Custom Liquid Sections with Raw JS Location Scripts (`custom_liquid_*`)
* **Mechanism**: Merchants or legacy scripts often insert a "Custom Liquid" section containing inline `<script>` tags that check `window.location.pathname == '/'` and execute `window.location.href = targetProductUrl;` on `window.onload`.
* **Failure Mode**: Unlike `theme.liquid`, custom liquid sections placed in `templates/index.json` lack `request.design_mode` checks, triggering instant redirection during Theme Customizer preview. If the target product handle does not exist on the development store, it yields an immediate 404.
* **Fix**: Purge any `<script>` redirection logic from `custom-liquid` sections, or wrap them with `{% unless request.design_mode %}`.

---

### 8. Announcement Bar Theme Blocks & Pill Styling Defaults (Summer '24 Theme Blocks)
* **Mechanism**: In modern themes supporting Theme Blocks (e.g. `blocks/countdown-timer.liquid`), blocks placed in `header-group.json` default to `bg_color_scheme: "accent-1"`, `border_width: 1`, and `timer_style: "4"` (split digit boxes).
* **Fix**: To match seamless header styling without unwanted capsules/boxes:
  - Set `bg_color_scheme: "custom-solid"`, `background_solid: "rgba(0,0,0,0)"`.
  - Set `border_width: 0`, `border_radius: 0`.
  - Set `timer_style: "3"` (continuous colon-separated numbers) instead of `4` (split digit boxes).
  - Ensure visibility helper CSS classes (`.always-display`, `.only-mobile`, `.no-mobile`) are defined in `assets/custom.css`.

---

### 9. Theme Packaging & Zip Upload Delivery UX
* **Distinct & Short Filenames**: Avoid overly long archive names with redundant `-0-` or repeated words (e.g. `verdojewelry-com-shrine-theme-pro-1-9-0-FINAL-MIGRATED.zip`) which get truncated to `verdojewelry-com-shrine-the...` in OS file pickers, causing version confusion. Use concise, unambiguous names (e.g. `verdo-shrine-pro-1-9-0-FIXED.zip`).
* **Multi-Location Staging**: Copy verified theme releases to accessible staging targets (`~/Desktop`, `~/Downloads`, and project dir) to ensure rapid access.
* **OS File Picker Selection State Trap**: In macOS Finder upload modals, the "Open" button remains disabled (greyed out) until a file row is actively clicked/highlighted in blue or double-clicked.
* **Direct Drag-and-Drop Fast-Path**: Instruct users to drag the `.zip` archive directly from Desktop/Downloads into Shopify Admin's *"Drag and drop your zip file here"* modal area, completely bypassing file picker selection glitches.

---

### 10. Product Card Unclickable Media & `disablecopy.liquid` Pointer-Events Trap
* **Mechanism**: In modern OS 2.0 themes (e.g. Shrine Pro / Dawn variants), the product card media container (`.card__media` in `snippets/card-product.liquid`) is often rendered as a plain `<div>`, relying on the heading link pseudo-element `.card__heading a::after` to cover the entire card.
* **Failure Mode**:
  1. Stacking Context / Relative Positioning: If `.card__content` or `.card__information` has `position: relative`, `.card__heading a::after` is constrained to the text box and cannot stretch over `.card__media` inside `.card__inner`.
  2. Copyright / Image Protection Injections: If `snippets/disablecopy.liquid` or an anti-theft app applies global `img { pointer-events: none !important; }`, click events pass straight through the image into the unlinked `div.card__inner`, rendering the product image completely dead to user clicks and taps.
* **Fix**:
  1. Explicitly wrap the media container in an anchor tag in `snippets/card-product.liquid`:
     ```liquid
     <a href="{{ card_product.url }}" class="card__media" aria-label="{{ card_product.title | escape }}">
       ...
     </a>
     ```
  2. Ensure pointer events and stacking context in `assets/custom.css`:
     ```css
     a.card__media {
       display: block;
       cursor: pointer;
       z-index: 2;
       text-decoration: none;
     }
     a.card__media img {
       pointer-events: auto !important;
       cursor: pointer !important;
     }
     ```

---

### 11. Stale Monolithic Section Settings in Product JSON Templates Causing 404
* **Mechanism**: During migration from older monolithic theme architectures to modern Summer '24 Theme Blocks (where `sections/main-product.liquid` delegates options to `blocks/main-product_gallery.liquid` and `blocks/main-product_details.liquid`), transferred `templates/product*.json` templates retain hundreds of obsolete settings in `sections.main.settings`.
* **Failure Mode**: Shopify Liquid engine validates JSON template settings against section schemas during route compilation. Stale, unrecognised settings or missing schema attributes can cause the Liquid compiler to fail during template resolution, causing Shopify to return a 404 (Not Found) or template render error when navigating to product pages.
* **Fix**:
  1. Extract all allowed setting IDs from target theme section schemas (`sections/*.liquid`).
  2. Run an automated schema cleaner script across all `templates/product*.json` and `templates/*.json` to prune deprecated settings keys not present in the section schema.
  3. Validate that all block types referenced in `templates/product*.json` exist in either the section's schema blocks or under `blocks/<type>.liquid`.

---

### 12. Missing `"type": "main-product"` in `templates/product.*.json` Sections Root
* **Mechanism**: In Shopify OS 2.0 JSON templates, every section in `sections` MUST define a `"type"` property pointing to a valid section in `sections/<type>.liquid` (e.g. `"type": "main-product"`).
* **Failure Mode**: When migrating or reconstructing custom product templates (`product.<suffix>.json`), if `"main": { "blocks": { ... } }` is generated or transferred without `"type": "main-product"`, the Shopify Theme Engine cannot determine which Liquid section file to render. When navigating to any product using that `template_suffix` (e.g. `/products/always-yours-birthstone-heart-necklace`), Shopify fails to resolve the route and renders a 404 Not Found error page.
* **Fix**:
  1. Audit all `templates/product.*.json` files and verify `data["sections"]["main"]["type"] == "main-product"`.
  2. If missing, inject `"type": "main-product"` before `blocks` and `order` properties.

---

### 13. Card Product Title Span Degradation (`show_quick_add_as_link`)
* **Mechanism**: In `snippets/card-product.liquid`, themes implementing quick-add or direct-to-product buttons may check `{% if show_quick_add_as_link == 'link-to-product-page' %}` and swap the title link `<a href="{{ card_product.url }}">` for a plain `<span>{{ card_product.title | escape }}</span>`.
* **Failure Mode**: Clicking the product title does not navigate to the product page, leaving users with dead clicks or unhandled card behavior.
* **Fix**: Always retain `<a href="{{ card_product.url }}" class="full-unstyled-link">` around product titles in `snippets/card-product.liquid` regardless of quick-add mode.

---

### 14. Countdown Timer Theme Block Color Scheme Discrepancy
* **Mechanism**: In Summer '24 Theme Blocks (`blocks/countdown-timer.liquid` / `snippets/countdown-timer.liquid`), background styling uses `bg_color_scheme: "custom-solid"` paired with `background_solid: "#..."`, whereas typography (heading, colon, digits) uses `heading_color_scheme: "custom"`, `timer_colon_color_scheme: "custom"`, `timer_text_color_scheme: "custom"` paired with `heading_color`, `timer_colon_color`, `timer_text_color`.
* **Failure Mode**: Setting text color schemes to `"custom-solid"` generates invalid CSS `rgb(var(--color-base-custom-solid))`, causing text and timer colons to revert to theme default or transparent colors.
* **Fix**: Ensure JSON settings use `"custom-solid"` only for `bg_color_scheme` and `"custom"` for text/digits/colon color schemes with explicit hex color values.

---

### 15. Context-Dependent Collection Product URL vs Canonical Product URL (`| within: nil`)
* **Mechanism**: In Liquid collection loops (e.g. `featured-collection.liquid` or `main-collection-product-grid.liquid`), accessing `card_product.url` by default resolves to `/collections/<collection-handle>/products/<product-handle>`.
* **Failure Mode**: When previewing a theme on a development or staging store where collection handles, automated smart collection conditions, or manual product assignments differ from production, navigating to `/collections/<collection-handle>/products/<product-handle>` causes Shopify's routing engine to return `404 Not Found` if that product is not assigned to that specific collection in the active store database.
* **Fix**: Apply the canonical product URL filter `within: nil` at the top of `snippets/card-product.liquid`:
  ```liquid
  {% assign card_product_url = card_product.url | within: nil %}
  ```
  Replace all `{{ card_product.url }}` occurrences with `{{ card_product_url }}` on media links (`<a class="card__media" ...>`), title links, quick-action buttons, and `data-url` / `data-product-url` attributes. This guarantees direct navigation to `/products/<product-handle>` and prevents collection routing 404s.

---

### 16. Missing Product Template Suffix Files (`product.<suffix>.json`) and Incomplete ZIP Archives
* **Mechanism**: In Shopify stores with diverse product catalogs, individual products often have custom templates assigned via `template_suffix` (e.g. `17-always-yours`, `1-the-heart-of-the-family`), while others have `template_suffix: null` (relying on default `templates/product.json`).
* **Failure Mode**: When packaging or updating a theme, if an archive is compiled with only a partial subset of product templates (e.g., 22 templates packaged while 43 exist in the source or store catalog):
  1. Any product whose specific `template_suffix` template is missing in the uploaded theme (and where fallback `templates/product.json` is missing or unable to render) immediately returns HTTP 404 Not Found when clicking the product card or navigating to `/products/<product-handle>`.
  2. The merchant/developer observes that *only one specific product opens* (the one whose template happened to be included in the archive) while all other product cards fail with 404. This easily masquerades as a card-click JavaScript bug or collection link issue, when in reality it is a missing template suffix in the theme.
* **Detection & Diagnostic Protocol**:
  1. Inspect the live store products via Shopify JSON API:
     ```bash
     curl -s "https://<store-domain>/products.json?limit=250" | jq '.products[] | {title, handle, template_suffix}'
     ```
  2. Collect all distinct `template_suffix` values across active catalog products:
     ```python
     suffixes = {p['template_suffix'] for p in data['products'] if p.get('template_suffix')}
     ```
  3. Verify that for every unique non-empty suffix, `templates/product.<suffix>.json` physically exists in the theme.
  4. Verify that the default base template `templates/product.json` is physically present for all products with `template_suffix: null`.
* **Fix**: Ensure the theme packaging pipeline copies the complete inventory of all `templates/product*.json` files (and asserts `templates/product.json` presence) rather than building from a selective or truncated template list.

---

### 17. Overlapping Anchor Collision & Touch Cancellation (`.card__media` vs `.card__heading a::after`)
* **Mechanism**: In Dawn and derivative themes (such as Shrine Pro), cards rely on a CSS pseudo-element overlay:
  ```css
  .card__heading a::after {
    bottom: 0; content: ""; left: 0; position: absolute; right: 0; top: 0; z-index: 1;
  }
  ```
  This creates an invisible full-card click target. If developers also convert `.card__media` into an explicit anchor `<a href="{{ card_product_url }}" class="card__media">` without adjusting `z-index`, two clickable `<a>` elements overlap in the DOM: the media anchor (at `z-index: 0`) and the pseudo-element overlay from the title anchor (at `z-index: 1`).
* **Failure Mode**: On mobile Safari, WebKit, and touch devices, overlapping interactive anchor tags can trigger touch cancellation, synthetic click suppression, or conflicting event bubbling, causing taps on product images to fail or appear dead. Furthermore, applying `| within: nil` unnecessarily on pre-resolved product URLs can introduce Liquid filter overhead or formatting quirks in custom preview environments.
* **Fix**:
  1. If `.card__media` is rendered as an explicit anchor tag `<a>`, ensure it sits above the heading pseudo-element (`z-index: 2` in CSS) with `pointer-events: auto !important` on inner images, OR retain `.card__media` as a semantic `<div>` and let `.card__heading a::after` handle the entire card click area cleanly.
  2. Use clean direct URL bindings: `assign card_product_url = card_product.url` on product cards to avoid filter chaining side-effects.

---

### 18. Template Counting Discrepancy & Optical Sorting Trap (Numeric vs Named Slugs)
* **Mechanism**: In stores with evolving template naming conventions, a theme often contains two distinct cohorts of product JSON templates:
  1. **Numbered Suffixes**: e.g., `product.1-...` through `product.20-...`, `product.100-...` plus base `product.json` (e.g. exactly 22 files).
  2. **Named Suffixes (Slugs)**: e.g., `product.cross-chain.json`, `product.verdo-caspian.json`, `product.siempre-tuya-collar-de.json` (e.g. 21 files).
* **Failure Mode & Human Friction**:
  When users or developers inspect an extracted archive in GUI file managers (macOS Finder, unarchivers) or simple alphabetical directory listings, the numeric templates sort consecutively at the top (from 1 to 20 + 100), leading to the visual assumption that *"the archive only has 22 templates"* because the non-numeric slug templates are separated down below alphabetically.
* **Deterministic Verification Invariant**:
  Never rely on visual inspection or selective GUI folder listings to confirm template inventory. Always verify zip archive contents via exact shell inspection:
  ```bash
  unzip -l "theme-archive.zip" "templates/product*"
  ```
  Confirm both the total file count (e.g. 43 files) and that target staging archives (`~/Desktop`, `~/Downloads`, and project repository) match the identical SHA256 checksum:
  ```bash
  shasum -a 256 ~/Desktop/theme.zip ~/Downloads/theme.zip path/to/project/theme.zip
  ```

---

### 19. Shopify Cloud Silent File Dropping on ZIP Import (Foreign Theme IDs & Block Collisions)
* **Mechanism**: When exporting themes or migrating JSON templates from another store or theme version, templates often retain legacy foreign theme IDs in block settings or scroll targets (e.g. `scroll_id: "#shopify-section-template--27549311271250__testimonials_..."` or `template--<theme_id>__...` key prefixes).
* **Failure Mode**: When importing a `.zip` theme via Shopify Admin (**Online Store ➡️ Themes ➡️ Add theme ➡️ Upload zip file**), Shopify's cloud ingestion parser validates each JSON template. If a template contains corrupt block keys, foreign theme section anchors, or unresolvable block bindings, Shopify **silently drops the affected template files**, importing only the valid subset without displaying any error banner in the admin UI!
* **Consequence**: The uploaded theme ends up with a truncated template inventory (e.g. only 22 templates out of 43), causing all products mapped to the missing templates to immediately return HTTP 404 Not Found on the storefront.
* **Deterministic Remediation**:
  1. **Sanitize Template Block Keys**: Recursively strip all `template--\d+__` and `template-\d+_` prefixes from template keys, `block_order`, and setting values (such as `scroll_id`), normalizing them to clean canonical IDs.
  2. **Direct CLI Push Verification**: Push via Shopify CLI (`shopify theme push --theme <theme_id>`) or Theme Access API — this logs granular per-file HTTP responses with exact line numbers, preventing silent upload dropping.

---

### 20. Section Schema Range Limit Violations (The Primary Mechanism of Silent ZIP Drops)
* **Mechanism**: In Shopify theme schemas (`{% schema %}` inside `sections/*.liquid`), settings of `\"type\": \"range\"` specify strict boundaries (`min`, `max`, `step`). In newer theme versions (e.g., Shrine Theme Pro 1.9.0 vs older releases), settings such as `horizontal-ticker`'s `speed` are bounded to `max: 5`. Migrated templates transferred from older themes or bespoke setups often carry legacy values (`speed: 25` or `50`).
* **Failure Mode**: When Shopify's cloud ZIP ingestion parser processes a `.zip` archive, it runs schema validation against each section. If ANY setting in a JSON template violates schema boundaries (e.g., `speed > 5`), Shopify's validator fails with `HTTP 422: Setting '<key>' can't be greater than <max>`.
* **The Silent Drop Trap**: Shopify DOES NOT reject the theme upload, nor does it display an error banner in the admin UI! Instead, it **silently skips and omits the failing template file**, successfully importing all others. This creates partial template inventories (e.g. exactly 22 templates imported out of 43), where the dropped templates cause HTTP 404s on the storefront.
* **Deterministic Fix**:
  1. Scan all templates against their target section schema ranges.
  2. Clamp out-of-bounds numeric values to the schema `max` or `min` boundary.
  3. Validate templates using `scripts/validate_template_schemas.py`.

---

### 21. Shopify Theme Access App API Headless Inspection & Sync Protocol
* **Mechanism**: Merchants can generate a Theme Access password/token (`shptka_...`) via Shopify's Theme Access App. This token grants headless Theme Kit Access to themes and assets without exposing full store admin credentials or requiring Shopify CLI Ruby gems.
* **Endpoint Architecture**:
  - Base URL: `https://theme-kit-access.shopifyapps.com/cli/admin/api/unstable/themes/<theme_id>/assets.json`
  - Required Headers:
    - `X-Shopify-Shop: <shop_fqdn>` (e.g. `6c1e24-9d.myshopify.com`)
    - `X-Shopify-Access-Token: <shptka_token>`
* **Diagnostic Advantage Over ZIP Uploads**:
  While Shopify's ZIP importer silently suppresses schema errors, uploading an individual template asset directly via `PUT /assets.json` immediately exposes the raw schema validation failure in the HTTP response:
  ```json
  {\"errors\": {\"asset\": [\"Setting 'speed' can't be greater than 5\"]}}
  ```
  This isolates the exact invalid setting and section within milliseconds.
* **Headless Batch Sync**:
  Allows syncing all product templates, page templates, and `config/settings_data.json` directly into a target draft theme ID (`208027025746`), followed by automated live HTTP status verification across all product handles using `?preview_theme_id=<theme_id>`.

---

### 22. Secondary Section Block Settings Restoration & Headless Theme Access Sync
* **Mechanism**: During multi-template migrations between theme architectures (e.g. legacy monolithic Dawn/Shrine to modern modular Summer '24 Theme Blocks), secondary narrative sections (`image-with-text`, `rich-text`, `image-banner`, `collapsible-content`) often preserve their section keys and block IDs, but naive AST or dictionary merges can inadvertently wipe their inner `settings: {}` across dozens of templates (e.g., 40+ templates losing 800+ block settings for headings, copy, buttons, and alignments).
* **Failure Mode**: Products load without critical narrative copy, reviews, value props, or action buttons, rendering empty containers on the storefront while technically returning HTTP 200.
* **Deterministic Restoration Protocol**:
  1. **Schema Extraction**: Parse `{% schema %}` of each target section in `sections/*.liquid` to compile the whitelist of valid block types and their allowed setting keys and default types.
  2. **Source-to-Target AST Rehydration**: Match block keys and block types between the reference/source theme template and the destination theme template. Restore matching non-empty setting values into `section.blocks[block_id].settings` while skipping obsolete or removed schema keys.
  3. **Active/Disabled State Audit**: Verify that block `disabled: true/false` flags strictly mirror the source theme configuration so intentionally hidden promotional blocks remain inactive.
  4. **Headless Theme Access Batch Sync**:
     Instead of manual GUI ZIP imports that may silently drop files or require human reloads, push the complete template suite directly via Shopify Theme Access Gateway:
     ```python
     # PUT https://theme-kit-access.shopifyapps.com/cli/admin/api/unstable/themes/{theme_id}/assets.json
     # Headers: X-Shopify-Shop, X-Shopify-Access-Token, User-Agent: Shopify CLI
     payload = {"asset": {"key": f"templates/{template_filename}", "value": template_json_str}}
     ```
  5. **Live Runtime Probe**: Validate active storefront handles via `https://<domain>/products/<handle>?preview_theme_id=<theme_id>`, asserting `HTTP 200` and checking for the complete absence of Liquid error markers (`Liquid error:`, `Translation missing:`).

---

## 🛠️ Instant Theme Editor Bypass
To load the Theme Editor homepage bypassing client-side auto-redirectors, pass the `redirect=disable` query parameter in the `previewPath`:
```
https://admin.shopify.com/store/<store-id>/themes/<theme-id>/editor?previewPath=%2F%3Fredirect%3Ddisable
```
