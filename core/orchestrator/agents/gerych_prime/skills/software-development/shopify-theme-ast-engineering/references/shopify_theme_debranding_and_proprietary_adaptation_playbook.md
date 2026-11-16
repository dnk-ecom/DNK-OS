# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_theme_debranding_and_proprietary_adaptation_playbook.md"
# purpose: "Comprehensive engineering playbook for de-branding commercial Shopify themes, removing DRM/phone-home checks, and adapting into proprietary DNK Ecom base themes."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛡️ Commercial Theme De-Branding & Proprietary Adaptation Playbook

## 1. Overview & Scope
When adopting modern third-party Shopify OS 2.0 / Summer '24 Theme Blocks bases (such as Casaio / Lumin 1.1.0 or Tinker 4.2.0) into proprietary store themes (e.g., `DNK_Ecom_v0_1`), commercial vendor artifacts must be thoroughly purged and re-engineered:
1. Remote licensing gates / phone-home DRM (Supabase/Firebase activation checks).
2. Vendor metadata and schema documentation URLs in `config/settings_schema.json`.
3. Vendor file naming prefixes (`lumin-*` ➔ `dnk-*`) across sections, blocks, snippets, and assets.
4. Scoped CSS namespaces and custom elements (`.lumin-*` ➔ `.dnk-*`).
5. External vendor documentation links in section/block `{% schema %}` definitions.
6. Auto-generated activation localization strings (`locales/*.schema.json`, `locales/*.json`).

---

## 2. Phase 1: DRM & Phone-Home Neutralization (Critical)

Commercial themes (such as LuminTheme / Casaio 1.1.0 and Story 4.x) implement multi-layered, distributed DRM telemetry and Dead-Man's Switch overlays that lock the storefront and `Shopify.designMode` (Theme Editor) via `position: fixed; z-index: 2147483647;`. Removing only the overlay file will trigger fallback kill-switches unless all 6 layers are neutralized together.

### 2.1. Complete 6-Layer Distributed DRM Architecture (LuminTheme / Casaio Pattern)
Always scan for and neutralize all 6 interdependent vectors:
1. **Store Domain Exposure (`window.__te_d`)**:
   - `snippets/scripts.liquid`: `window.__te_d = {{ shop.permanent_domain | json }};`
   - `snippets/theme-editor.liquid`: `<script>window.__te_d="{{ shop.permanent_domain }}";</script>`
2. **4 Distributed Base64 (`atob`) Beacons to Supabase (`verify-activation`)**:
   - **Beacon 1 (`snippets/scripts.liquid`)**: Two inline `<script>` blocks constructing `window.__su` via `atob()`, checking `localStorage.getItem('lumin_theme_activation_' + window.__te_d)`, sending a `POST` request with `{ store_url: window.__te_d }`, and invoking `window.__sd()` on failure.
   - **Beacon 2 + Dead-Man's Switch (`assets/section-hydration.js`)**: Re-verifies license after `onDocumentReady`. Contains a self-contained fallback `showHydrationFallback()` that injects `<div id="v2-d">This theme is not activated.</div>` (`z-index: 2147483647`) if `window.__sd` (`theme-activation-overlay.js`) was deleted.
   - **Beacon 3 (`assets/section-renderer.js`)**: Split into 3 fragments across the file (`window.__ru` base64 segments at top, mid-file, and bottom + `window.__rs` fetch trigger) that phones home on every dynamic section render.
   - **Beacon 4 (`assets/theme-editor.js`)**: Split into 3 fragments across the file (`window.__tu` base64 segments + `window.__ts` fetch trigger) that locks the Theme Customizer.
3. **Unremovable MutationObserver Overlay (`assets/theme-activation-overlay.js` + `assets/base.css` + `assets/global.d.ts`)**:
   - Delete `assets/theme-activation-overlay.js` completely.
   - Strip `#lumin-class-overlay` styles from `assets/base.css`.
   - Strip `__sd`, `__te_d`, `__su`, `__av` declarations from `assets/global.d.ts`.

### 2.2. Verification Regex Scan
Run a comprehensive scan across `assets/`, `snippets/`, `sections/`, and `layout/` to ensure zero obfuscated beacons or external calls remain:
```bash
grep -rnE "(__su|__ru|__tu|__rs|__ts|__te_d|__sd|__av|verify-activation|supabase|lumin_theme_activation|showHydrationFallback|v2-d|atob\()" assets/ snippets/ sections/ layout/
```

### 2.3. External Font & GDPR Leak Neutralization (`fonts.googleapis.com`)
- Scan all CSS and Liquid files for third-party font imports (`fonts.googleapis.com`, `fonts.gstatic.com`, `use.typekit.net`).
- In `assets/renewlift-styles.css` (and similar addon stylesheets), remove `@import url('https://fonts.googleapis.com/...');` and bind CSS custom properties directly to native Shopify font variables (`--rl-font-heading: var(--font-heading--family);`, `--rl-font-body: var(--font-body--family);`).

### 2.4. Locale Cleansing & RFC 8259 JSON Comment Stripping (`locales/*.json`, `sections/*.json`, `templates/*.json`)
- Remove the `"listing"` namespace containing activation modal copy (`unlisted_heading`, `unlisted_message`, `l1`, `l2`, `store_url_instruction`, `copy_title`) from all `locales/*.json` files and `Theme.translations` in `snippets/scripts.liquid`.
- Strip C-style block (`/* ... */`) and line (`//`) comments from all JSON files using a string-aware state machine (preserving `https://` inside JSON string literals) so every JSON file passes strict `json.loads()` and Shopify's ZIP uploader without rejection.

---

## 3. Phase 2: Theme Metadata & Manifest Refactoring

Update `config/settings_schema.json` entry 0 (`theme_info`):

```json
{
  "name": "theme_info",
  "theme_name": "DNK Ecom",
  "theme_version": "0.1.0",
  "theme_author": "DNK OS",
  "theme_documentation_url": "https://dnk-e.com/docs",
  "theme_support_url": "https://dnk-e.com/support"
}
```

---

## 4. Phase 3: Filesystem & Component Renaming Matrix

Rename all vendor-prefixed files to `dnk-*` while maintaining strict Liquid AST and asset references:

| Category | Source File (Vendor) | Target File (DNK) | Required Code Updates |
| :--- | :--- | :--- | :--- |
| **Sections** | `sections/Lumin-review.liquid` | `sections/dnk-review.liquid` | Update template JSON section mappings |
| | `sections/lumin-slideshow.liquid` | `sections/dnk-slideshow.liquid` | Update template JSON section mappings |
| | `sections/section-lumin.liquid` | `sections/section-dnk.liquid` | Update template JSON section mappings |
| **Blocks** | `blocks/lumin-image-slide.liquid` | `blocks/dnk-image-slide.liquid` | Update parent section `{% schema %} blocks` |
| | `blocks/_lumin-image-slide.liquid` | `blocks/_dnk-image-slide.liquid` | Update parent section `{% schema %} blocks` |
| **Snippets** | `snippets/lumin-review-*.liquid` | `snippets/dnk-review-*.liquid` | Update `{% render 'dnk-review-*' %}` calls |
| **Assets JS** | `assets/lumin-review.js` | `assets/dnk-review.js` | Update Liquid `asset_url` or schema `javascript` |
| | `assets/lumin-slider.js` | `assets/dnk-slider.js` | Update `asset_url` in sections |
| | `assets/luminslider-slideshow.js` | `assets/dnk-slideshow.js` | Update `asset_url` in sections |
| **Assets CSS**| `assets/lumin-review.css` | `assets/dnk-review.css` | Update schema `stylesheet` or Liquid tag |
| | `assets/luminslider-slideshow.css`| `assets/dnk-slideshow.css` | Update schema `stylesheet` or Liquid tag |

---

## 5. Phase 4: CSS Namespaces & Custom Elements

Search and replace vendor CSS prefixes in HTML markup, Liquid files, and CSS stylesheets:
- `.lumin-tabs-*` ➔ `.dnk-tabs-*` (`blocks/tabs.liquid`)
- `.lumin-timer-*` ➔ `.dnk-timer-*` (`blocks/timer.liquid`)
- `.lumin-swiper-*` ➔ `.dnk-swiper-*` (`blocks/slider-swiper.liquid`)
- Custom web components: replace `<lumin-slider>` or similar custom tags with `<dnk-slider>` in both markup and `customElements.define('dnk-slider', ...)`.

---

## 6. Phase 5: Schema Link Neutralization

In section and block `{% schema %}` definitions, replace third-party documentation URLs (`help.lumintheme.com/...`, `lumintheme.com/blogs/...`) with internal merchant tooltips or clean generic help text:
- `blocks/_quantity-breaks-simple.liquid`: Remove vendor blog link; provide inline instructions for discount tier configuration.
- `blocks/variant-picker.liquid`: Replace vendor setup guide link with native Shopify variant image instructions.
- `blocks/_inline-text.liquid`: Replace vendor anchor tutorial link with standard `#section-id` guidance.

---

## 7. Verification Checklist
- [ ] `grep -rnI "lumintheme" .` returns 0 results.
- [ ] `grep -rnI "theme-activation-overlay" .` returns 0 results.
- [ ] Zero Vendor Traces Gate: `git diff origin/Dev..HEAD | grep -i "<vendor_name>"` returns 0 results prior to sync/push.
- [ ] CDN Asset Hygiene: All images/videos/styles resolved via `{{ 'file' | asset_url }}` or validated Shopify CDN; zero broken 404 external asset URLs.
- [ ] Mobile-First Viewport Verification: Layout, touch hotspots, and overlays verified at 375px & 414px (mobile bottom sheets, touch drag, and iOS Safari audio policies: `playsinline`, `muted`, user-gesture unmuting).
- [ ] Theme Editor opens without modal dialogs or console network calls to external Supabase functions.
- [ ] All renamed blocks and sections render properly in `templates/*.json`.
- [ ] Theme passes `shopify theme check` with zero schema errors.
- [ ] Zero residual `shopify://shop_images/` client media references in packaged `.zip` test bundles.

---

## 8. Media Neutralization & Clean Shopify Zip Bundle Packaging

When packaging a client theme or external OS 2.0 theme for clean sandbox testing in Shopify Admin, all hardcoded client store CDN media (`shopify://shop_images/...`) must be scrubbed and replaced with native Shopify SVG placeholders (`placeholder_svg_tag`).

### 8.1 Scrubbing `shopify://shop_images/` in JSON Templates & Config
Client themes frequently hardcode hundreds of store-specific `shopify://shop_images/...` references inside `config/settings_data.json`, `sections/*.json` (e.g., `header-group.json`), and `templates/*.json`. Importing these into a different Shopify store results in broken media references or unauthorized client imagery.

```python
def scrub_shop_images(obj):
    count = 0
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and v.startswith("shopify://shop_images/"):
                obj[k] = ""
                count += 1
            else:
                count += scrub_shop_images(v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and item.startswith("shopify://shop_images/"):
                obj[i] = ""
                count += 1
            else:
                count += scrub_shop_images(item)
    return count
```
*Note*: Preserve standard JSON indentation (`indent=2` or original header comments if any) so schema/theme guards continue to pass.

### 8.2 Native Shopify `placeholder_svg_tag` Fallback Mapping
Instead of bloating `assets/` with static dummy PNG/JPG files, always wire Liquid `{% else %}` branches to Shopify's native `placeholder_svg_tag` filter:

| Component / Section Context | Recommended Placeholder Name | Liquid Snippet Pattern |
|---|---|---|
| **Hero / Split Banner / Service Hero** | `'lifestyle-1'` or `'lifestyle-2'` | `{{ 'lifestyle-1' \| placeholder_svg_tag: 'hero__placeholder-svg' }}` |
| **Category Cards / Mega-Menu Tiles / Finder** | `'collection-1'` to `'collection-6'` | `{% assign ph_idx = forloop.index0 \| modulo: 6 \| plus: 1 %}`<br>`{% assign ph_name = 'collection-' \| append: ph_idx %}`<br>`{{ ph_name \| placeholder_svg_tag: 'card__placeholder-svg' }}` |
| **Product Cards / Cross-sell / Samples** | `'product-1'` to `'product-6'` | `{{ 'product-1' \| placeholder_svg_tag: 'product__placeholder-svg' }}` |
| **Generic Media / Icon / Logo / Impressum** | `'image'` | `{{ 'image' \| placeholder_svg_tag: 'media__placeholder-svg' }}` |

### 8.3 Critical Pitfalls When Adding SVG Fallbacks to Existing Themes
1. **Unconditional Wrapper Rendering vs. Blank-Image Test Contracts**:
   - Navigation snippets (`tp-menu-bild`, `tp-menu-karte`) or tile blocks often conditionally hide the image container when `image == blank` or set a `[data-ohne-bild]` attribute on the parent tile.
   - When switching to unconditional placeholder rendering (so sandbox stores always render visual layout boxes), inspect unit tests (`qa/tests/*.test.mjs`) that assert on blank-image states or `shopify://shop_images/` fixture strings and update those assertions in lockstep.
2. **Scoped CSS & Aspect Ratio Preservation for `<svg>`**:
   - Native `placeholder_svg_tag` outputs an `<svg class="placeholder-svg">` without intrinsic bitmap dimensions.
   - Ensure the parent wrapper or SVG class applies `width: 100%; height: 100%; object-fit: cover; display: block; background: var(--color-bg-subtle, #f4f1ec);` so cards and hero containers do not collapse to `0px` height or overflow flex layouts.

### 8.4 Canonical Shopify OS 2.0 `.zip` Packaging Specification
Shopify Admin (`Online Store -> Themes -> Add theme -> Upload zip file`) strictly validates the archive structure and rejects archives containing dev/CI artifacts or nested root folders:
- **Allowed Root Directories ONLY**:
  `assets/`, `blocks/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/`
- **Strictly Excluded**:
  `node_modules/`, `.git/`, `.github/`, `qa/`, `docs/`, `scripts/`, `.claude/`, `package.json`, `package-lock.json`, `.DS_Store`, `*.map`.
- **Verification Gate Before Delivery**:
  1. Run all static guards (`liquid:guard`, `schema:guard`, `secret:scan`, `qa:unit:test`).
  2. Run `zipfile.ZipFile.testzip()` integrity check.
  3. Scan every file inside the `.zip` to confirm `0` occurrences of `shopify://shop_images/` and verify all paths begin with one of the 8 canonical OS 2.0 directories.

---

## 8. Foreign Media Stripping, Native SVG Placeholder Replacement & Silent `index.json` Drop Prevention

When sanitizing a cloned or adapted theme (e.g., Horizon / ISOA / Rhode-inspired themes) so it can be uploaded cleanly via ZIP to a fresh development store without 404 errors on the homepage or broken third-party brand images/videos:

### 8.1. Why `templates/index.json` Silently Drops on Upload (Root Cause of Homepage Opening 404 in Theme Editor)
If the Shopify Theme Editor immediately opens onto the **`404 page`** (`templates/404.json`) when customizing a newly uploaded theme, `templates/index.json` was silently discarded by Shopify's cloud ZIP importer due to one or more of:
1. **Invalid `select` Option Values in Nested Theme Blocks (`blocks/*.liquid`)**:
   - In Horizon-based themes, `blocks/text.liquid` defines `"color"` as a `select` setting restricted to `["var(--color-foreground)", "var(--color-foreground-heading)", "var(--color-primary)"]` and `"font"` restricted to `["var(--font-body--family)", "var(--font-subheading--family)", "var(--font-heading--family)", "var(--font-accent--family)"]`.
   - Passing raw HEX strings (`"#ffffff"`, `"#67645e"`), invalid CSS variables (`"var(--font-primary--family)"`), or unlisted `font_size` rem values (`"2.75rem"`, `"2.2rem"`) in `templates/index.json` or `config/settings_data.json` triggers an importer schema rejection that silently drops `templates/index.json`.
   - **Fix**: Run `python3 scripts/validate_template_schemas.py --theme-dir <path> --fix --strip-external-media` to validate both `sections/*.liquid` and recursive `blocks/*.liquid` schemas across all JSON files.
2. **Unsupported `{% doc %}` Tags in `sections/*.liquid` or Stray Closing Tags in `blocks/*.liquid`**:
   - Ensure `{% doc %}...{% enddoc %}` is stripped from `sections/*.liquid` (where `shopify theme check` flags `UnknownTag`), no HTML exists outside `{% endschema %}`, and all `<style>` / `</style>` tags inside `blocks/*.liquid` are balanced.
3. **Non-Asset IDE Config Files in `assets/`**:
   - Remove `assets/global.d.ts`, `assets/jsconfig.json`, or `.map` files from `assets/` before creating the ZIP archive, as Shopify rejects non-asset files in `assets/`.

### 8.2. Stripping Foreign Media (`shopify://`) & Switching Video Heroes to Image Placeholders
- Strip all foreign store bindings (`"shopify://shop_images/..."`, `"shopify://files/videos/..."`) and foreign handles (`product`, `collection`, `menu`, `page`) from `templates/*.json`, `sections/*.json`, and `config/settings_data.json`.
- **CRITICAL: Scrubbing ONLY `shopify://shop_images/...` is insufficient for Theme Customizer preview**:
  - Leaving client-specific resource handles in `"collection"`, `"product"`, `"product_list"`, `"collection_list"`, `"blog"`, `"article"`, `"page"`, `"metaobject"`, or non-default `"link_list"` (e.g., `"customer-account-main-menu"`, `"teppichboden"`, `"kettelservice"`), or leaving `"shopify://collections/<custom>"`, `"shopify://pages/<custom>"`, and `"shopify://apps/<app>/blocks/..."` UUIDs in `config/settings_data.json`, `sections/*.json`, or `templates/*.json` will break template/section rendering in the Theme Customizer on a clean test store.
  - **Complete Schema-Typed Sanitization Rule**:
    1. Parse every section and block `{% schema %}` to build a `setting_id -> type` map.
    2. In all `templates/*.json`, `sections/*.json`, and `config/settings_data.json`:
       - Remove all `"shopify://apps/..."` app embed/block entries in `config/settings_data.json` (`current.blocks = {}`).
       - Set any setting of type `collection`, `product`, `blog`, `article`, `page`, `metaobject`, `image_picker`, `video`, `video_url` to `""` (while **preserving** valid dynamic source expressions like `"{{ closest.product }}"`).
       - Set any setting of type `product_list`, `collection_list`, `metaobject_list` to `[]`.
       - Set any `link_list` setting that is not `"main-menu"` or `"footer"` to `""` (and remove `"default": "customer-account-main-menu"` from `sections/header.liquid` schema).
       - For `url` settings: preserve pure anchors (`#...`), `/`, or `/collections/all`; convert page-specific anchors (`/pages/xyz#section` -> `#section`); replace other custom store URLs (`shopify://pages/...`, `shopify://collections/...`, `https://wa.me/...`, `https://maps.google.com/...`) with `"#"` if paired with a button label (so button-link QA guards never fail on empty button links) or `""` if optional.
    3. **Prevent Empty/Collapsed Sections in Theme Customizer (`request.design_mode`)**:
       - Audit custom sections for fail-closed guards like `if target == blank -> continue`, `if collection.products_count == 0 -> hide`, or `if list_items == blank -> hide`.
       - Add `request.design_mode` fallbacks so that when collections/products/metaobjects are empty in a test store, the section still renders its cards, fallback titles (`block.settings.title`), and native `placeholder_svg_tag` wireframes (`collection-1`, `product-1`, `lifestyle-1`, or `_product-card` with `closest.product: null`).
- **Critical Hero Video Fallback Rule**: In Horizon `sections/hero.liquid`, when `media_type_1` is set to `"video"` and `"video_1": "shopify://files/videos/..."` is removed without changing `media_type_1`, the hero attempts to render an empty video container instead of an image placeholder. Always switch `"media_type_1": "video"` to `"image"` whenever stripping `"video_1"` so the hero automatically falls back to `{{ 'hero-apparel-1' | placeholder_svg_tag }}`.

### 8.3. Replacing Custom Brand Assets in `assets/` with Native Shopify `placeholder_svg_tag`
- Delete proprietary brand photos/illustrations from `assets/` (e.g., `assets/isoa-*.png/jpg`, `assets/spotwear-*.jpg`) and remove external CDN URLs (`https://www.rhodeskin.com/...`).
- In `sections/*.liquid` and `snippets/*.liquid`, replace hardcoded `asset_url` fallback images with native Shopify SVG placeholders:
  ```liquid
  {% if section.settings.image != blank %}
    {{ section.settings.image | image_url: width: 1200 | image_tag: loading: 'lazy' }}
  {% else %}
    {{ 'lifestyle-1' | placeholder_svg_tag: 'placeholder-svg' }}
  {% endif %}
  ```
  Use `'hero-apparel-1'`, `'lifestyle-1'`, `'lifestyle-2'`, `'product-1'..'product-4'`, `'collection-1'`, or `'image'` with `placeholder_svg_tag` so every section displays clean native Shopify wireframes out of the box and seamlessly swaps to merchant media when selected in the Theme Editor.

---

## 9. One-Shot Execution Architecture (3 Core Workhorses Rule) & Multi-Vendor DRM Matrix

### 9.1. Why "Script + Hook + Template + Skill" Beats Creating a New Subagent
Per the **3 Core Workhorses** invariant (`services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`), never spawn a dedicated theme-sanitization subagent. Creating a separate LLM agent incurs ~5k tokens of handoff overhead and forces brittle multi-turn manual file scanning across 350–900 files. Instead, execute theme audits, debranding, section surgery, and licensing in **One Shot** inside `dnk_shopify` via 4 deterministic layers:
1. **Deterministic CLI Script (`dnk_theme_surgeon.py`)**: Performs single-pass ZIP inspection/extraction, string-aware RFC 8259 comment/trailing-comma stripping across all `.json` and `{% schema %}` blocks, known DRM neutralization, external CDN localization, asymmetric locale repair + `uk.json`/`uk.schema.json` synthesis, and clean ZIP packaging in ~1.5s (0 LLM tokens).
2. **Fail-Closed Pre-Package Validator Hook (`theme_zero_leak_hook.py`)**: Blocks ZIP output if any file contains `supabase`, `verify-activation`, `atob(`, `String.fromCharCode`, `fonts.googleapis`, `cdn.jsdelivr.net`, `__te_d`, `__stArmed`, `1.envato.market`, invalid RFC 8259 JSON (`json.loads`), or unbalanced `<script>/<style>` tags.
3. **Standardized Templates (`templates/`)**: Auto-populated `*_DNK_ARCHITECTURE_AND_CHANGELOG.md` passport, Theme Blocks 2.0 `section_v2.liquid.j2`, and `dnk_license_gate.liquid.j2`.
4. **Skill-Guided Exception Handling**: The agent runs the deterministic audit script first and only reads targeted 20-line slices when a novel obfuscation/CDN pattern is flagged, immediately appending the new signature to the script's signature registry.

### 9.2. Cross-Vendor Forensic Signature Matrix (Story vs. Casaio vs. Ella)

| Forensic Vector | `Story 4.0.5` (GroupThought) | `Casaio 1.1.0` (LuminTheme) | `Ella 7.3.1` (HaloThemes) |
| :--- | :--- | :--- | :--- |
| **Architecture Generation** | Classic OS 2.0 (`section.blocks`) | Classic OS 2.0 (`section.blocks`) | **Theme Blocks 2.0 / Horizon (`243 blocks/*.liquid`, `{% content_for 'blocks' %}`)** |
| **DRM / Kill-Switch** | `String.fromCharCode` array (`__stArmed`) in `assets/theme.dev.js` | 6-layer `atob()` Supabase `verify-activation` beacon + `showHydrationFallback` DOM blocker + `global.d.ts` types | None (`0` `atob`, `0` `fromCharCode`), but logs orange DevTools banner in `assets/global.js:28-35` via `window.info` (`snippets/global-script.liquid:175`) |
| **External CDN / Font Leaks** | Clean | `@import url('https://fonts.googleapis.com/...')` in `assets/renewlift-styles.css` | Dynamic `<script>` injection of `https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js` in `blocks/_color-comparison.liquid:79` + `assets/halo-compare-color.js:41-49` |
| **Vendor / Affiliate Leaks** | `settings_schema.json` metadata | `lumintheme.com` help links in block schemas + `listing.*` locale keys | `1.envato.market/dokaB2`, `new-ella-demo-07.myshopify.com`, `halothemes.net`, `themeforest.net` in `header-group.json`, `footer-group.json`, `footer.liquid`, `page.faqs.json` |
| **RFC 8259 JSON Landmines** | Comment headers in `locales/*.json` | 65 JSON files with `/* */`, `//`, and trailing commas | `config/settings_schema.json:519` trailing comma + 58 JSON files with `/* */` headers + 11 `.liquid` `{% schema %}` blocks with trailing commas |
| **Locale Asymmetry** | Missing `uk` locales | Missing `uk` locales | Missing `uk.json`/`uk.schema.json` + **11 broken pairs** (`ar.schema.json` & `hi.schema.json` lack storefront `.json`, causing `translation missing` on all 714 storefront keys; 9 locales lack `.schema.json`) |

### 9.3. HaloThemes / Ella 7.x Specific Sanitization Rules
1. **Safe Neutralization of `Sortable.min.js` CDN Injection**:
   - Never blindly delete `data-url-script-compare-color` in `blocks/_color-comparison.liquid:79` without updating `assets/halo-compare-color.js:52` (`new Sortable(...)`), or desktop color comparison drag-and-drop will throw `ReferenceError: Sortable is not defined`. Either bundle `assets/sortable.min.js` locally via `{{ 'sortable.min.js' | asset_url }}` or guard instantiation with `if (typeof Sortable !== 'undefined')`.
2. **String-Aware Trailing Comma & Comment Cleaner for `{% schema %}`**:
   - In addition to `.json` files, scan and clean all `{% schema %}...{% endschema %}` blocks inside `sections/*.liquid` and `blocks/*.liquid` for trailing commas (`re.sub(r',\s*([}\]])', r'\1', ...)` outside string literals) so every schema parses cleanly under strict `json.loads()`.
3. **Selective Vendor Scrubbing vs. Internal CSS/JS Selectors**:
   - Do not blindly regex-replace `halo-` across `Ella 7.x` unless performing a full AST class rename—`halo-*` is used in 62+ structural CSS selectors and custom elements (`halo-compare-color.js`, `snippets/halo-popup.liquid`, `window.__haloLoadedScripts`). Scrub public metadata (`settings_schema.json`), console banners (`global.js`, `global-script.liquid`), and preset links (`header-group.json`, `footer-group.json`, `footer.liquid`, `page.faqs.json`) while keeping internal selectors intact.
4. **Locale Pair Balancing Gate**:
   - Always verify that every `<lang>.schema.json` in `locales/` has a matching `<lang>.json` storefront dictionary (especially `ar` and `hi`), and generate both `locales/uk.json` and `locales/uk.schema.json` together.
5. **Multi-Line `console.log` Regex Truncation Pitfall & Mandatory `node --check` Gate (`assets/global.js:28-35`)**:
   - **Trap**: HaloThemes `assets/global.js` contains an 8-line styled `console.log('%c...', 'color: #ff8800; font-weight: bold;...')` with semicolons `;` inside CSS string arguments. A naive regex like `console\.log\([^;]*\);` stops at the first `;` inside `'color: #ff8800;...'`, leaving orphaned arguments on lines 29–34 and causing `Uncaught SyntaxError: Unexpected token ':'`.
   - **Cascade**: When `assets/global.js` fails to parse, `window.theme`, `trapFocus`, `removeTrapFocus`, and `customElements.define('recently-viewed-products', ...)` never execute. Consequently, `<side-drawer>` opens (via `assets/details-disclosure.js`), but clicking `✕` or the overlay crashes in `SideDrawer.close()` at `removeTrapFocus(this.activeElement)` (`ReferenceError`) before reaching `this.classList.remove('active', 'open')`, permanently locking the drawer open.
   - **Rule**: Never strip multi-line JS statements with `[^;]*`. Match balanced parentheses or the exact multi-line block, and run `node --check` on **every** `assets/*.js` file and extracted `{% javascript %}` block as a mandatory pre-package gate.
6. **HaloThemes `RecentlyViewedProducts` & `SideDrawer` Factory Bug Fixes (`Ella 7.3.1`)**:
   - **Current-Product Self-Splicing in Floating Drawer**: `blocks/_recently_viewed_products.liquid` passes `data-product-id="{{ product.id }}"` inside `#popup-recently-viewed`. In `RecentlyViewedProducts.getItems()`, splicing out `this.dataset.productId` leaves the list empty (`Sorry, there are no products.`) when the shopper has viewed only the current product. Only exclude `data-product-id` when rendering the bottom page section, NOT inside `#popup-recently-viewed`.
   - **`defer` Script Order Race Condition (`global.js` vs `product-info.js`)**: `assets/global.js` loads in `<head defer>` while `assets/product-info.js` loads in `<body defer>`. `RecentlyViewedProducts` reads `localStorage.getItem('_halo_recently_viewed')` before `ProductInfo.setRecentlyViewed()` records the product. Fix by calling a synchronous `recordCurrentProduct()` helper inside `RecentlyViewedProducts` (reading `product-info[data-product-id]`) and dispatching `new CustomEvent('recently-viewed:updated')` from `ProductInfo.setRecentlyViewed()`.
   - **Incomplete `<side-drawer>` Markup Across 7 Templates**: `blocks/_product-tabs.liquid`, `blocks/accelerated-checkout.liquid`, `sections/section-product-tabs.liquid` (also missing `id="Drawer-Overlay-..."`, causing `this.overlay.closest('details')` null crash), `snippets/global-popup.liquid`, `snippets/product-popup.liquid`, `snippets/purchase-conditions.liquid`, and `snippets/social-share-button.liquid` lack `data-drawer-content` and `data-drawer-direction="center"`. Add those attributes and harden `SideDrawer.open()` / `SideDrawer.close()` with optional chaining (`this.overlay?.closest('details')`), `typeof removeTrapFocus === 'function'` guards, and `try/catch` around `Motion.timeline(...).finished`.
   - **`MultitaskingBar` Reparenting**: Because `SideDrawer.connectedCallback()` moves `#popup-recently-viewed` to `document.body`, `MultitaskingBar.init()` must query `document.getElementById('popup-recently-viewed')` rather than `this.querySelector(...)` when binding `.drawer__close` and overlay listeners.
7. **Regex Replacement String Escape Trap in JSON/`{% schema %}` (`\.` Invalid JSON Escape)**:
   - Never use `\.` in a regex replacement string (e.g., `support@dnk-e\.com`) when sanitizing `.json` or `.liquid` files—in JSON, `\.` is an illegal escape sequence (`json.decoder.JSONDecodeError: Invalid \escape`). Always validate 100% of `.json` files AND all extracted `{% schema %}` blocks with `json.loads()`.


