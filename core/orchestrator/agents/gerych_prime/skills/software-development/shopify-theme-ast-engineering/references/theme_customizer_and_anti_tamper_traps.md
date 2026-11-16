# Shopify Theme Customizer & Anti-Tamper Traps (Deobfuscation & Reliability Guide)

This guide documents critical pitfalls, forensic debugging techniques, and fixes for proprietary Shopify themes (e.g., Story, Impulse, Prestige, Shrine Pro, Ella, Casaio, DNK Ecom Sections) containing anti-tamper traps, customizer event conflicts, and schema localization gaps.

---

## 1. Vendor Anti-Tamper / Deceptive Failure Traps

### 1.1 The Deceptive "Connection Lost" Network Error (Story / GroupThought)
* **Symptom**: Clicking "Add to Cart" or interacting with cart forms fails with:
  > *"Connection lost. Check your network and try again"*
* **Underlying Trap**:
  Theme vendors conceal licensing checks not only in dedicated files (`theme-runtime.js`, `section-loader.js`), but also inject poisoned conditionals into standard utility files (`assets/global.js`):
  ```javascript
  // Poisoned snippet in global.js
  if (window.mediaFeatures === "hover") {
    window.fetchConfig = function(type = 'json') { ... };
    window.debounce = function(fn, wait) { ... };
  }
  ```
  If licensing or runtime scripts are removed or fail, `window.mediaFeatures` is never set to `"hover"`. As a result:
  1. `window.fetchConfig` remains `undefined`.
  2. In `assets/cart.js`, calling `fetch('/cart/add.js', fetchConfig('javascript'))` throws `ReferenceError: fetchConfig is not defined`.
  3. The error handler catches the exception and assumes a network failure, surfacing the deceptive localized string: `"Connection lost. Check your network and try again"`.
  4. In `assets/product-form.js`, `this.cart.noService()` or `holdExpress()` freezes express checkout buttons (Shop Pay, PayPal).

* **Detection & Remediation**:
  1. Search for conditionals guarding utility definitions:
     `grep -rn "window.mediaFeatures" assets/`
     `grep -rn "fetchConfig" assets/`
  2. Remove the condition completely. Ensure `debounce` and `fetchConfig` are always unconditionally declared and attached to `window`.
  3. Rebuild minified bundles (`esbuild assets/global.js --minify --outfile=assets/global.min.js`).

### 1.2 Secondary Obfuscated Inline CSS/Style Poisoning (`snippets/css-variables.liquid`)
* **Symptom**: Even after removing or stubbing `assets/theme-runtime.js` and `assets/section-loader.js`, the storefront suddenly turns bright red with `font-size: 70px !important` after ~2000ms.
* **Underlying Trap**:
  Vendors hide a secondary dead-man's switch right after `{% endstyle %}` inside `snippets/css-variables.liquid` using `String.fromCharCode` to check `window.__stArmed !== false`:
  ```javascript
  var k = String.fromCharCode(95, 95, 115, 116, 65, 114, 109, 101, 100); // "__stArmed"
  setTimeout(function() {
    if (window[k] !== false) { /* injects * { color: red !important; font-size: 70px !important; } */ }
  }, 2000);
  ```
* **Detection & Remediation**:
  1. Scan all `.liquid` files for `String.fromCharCode` or inline `<script>` blocks inside style snippets (`snippets/css-variables.liquid`).
  2. Strip the `<script>` block after `{% endstyle %}` completely.
  3. Also remove the hidden license modal `.theme__modal--callback` in `sections/header.liquid` and any `get-story-theme.js` / `get-story-theme.min.js` promo scripts across `layout/theme.liquid`, `layout/password.liquid`, and `templates/gift_card.liquid`.

### 1.3 Shrine Pro / Ecom Sections 6-Layer Anti-Tamper & Silent ATC Sabotage Traps
* **Symptoms**:
  - Blank page (`main { visibility: hidden !important; }`) when license setting is empty.
  - Works on `.myshopify.com`, but on any custom domain (`store.com`) either wipes `document.body.innerHTML` + clears `/cart/clear.js`, or silently breaks "Add to Cart" (`400 Bad Request: missing id`).
* **The 6 Hidden Layers**:
  1. **CSS Kill-Switch (`layout/theme.liquid`)**:
     `{% if settings.coun_viriality == blank or settings.coun_viriality.size < 22 %}main{visibility:hidden !important;}{% endif %}` hides the entire `<main>` content unless `settings.coun_viriality` has >= 22 characters.
  2. **Domain Lock & Cart Wipe (`assets/main.js` — `initThemeLicenseCheck` / `validateDomainAccess` / `handleUnauthorizedAccess`)**:
     Allows `.myshopify.com`, `shopify.com`, `shopifypreview` only if `document.documentElement.innerHTML.includes(expectedKey)`. On custom domains, runs `window.stop()`, `fetch("/cart/clear.js", { method: "POST" })`, and replaces `document.body.innerHTML` with a Telegram ransom screen.
  3. **Obfuscated String-Concat `<body>` Wipe (`popupTimer` / `initTrapFocus` in `assets/main.js`)**:
     ```javascript
     var menuIndex = 'bod' + 'y';
     var linkContent = 'inne' + 'rH' + 'TML';
     document[menuIndex][linkContent] = '';
     ```
     Triggered if `<footer>` (`sections/footer.liquid`) does not have `data-type="{{ settings.coun_viriality }}"`.
  4. **Silent Add-To-Cart Sabotage on Custom Domains (`defMed` / `this.form.ref` / `deleteId` in `assets/main.js`)**:
     In `ProductInfo.connectedCallback()`:
     ```javascript
     this.deferredMedia = document.querySelector('[src*="main"]');
     if (!this.deferredMedia || !this.deferredMedia.src || !this.deferredMedia.src.includes('net')) this.form.ref = true;
     ```
     And in `ProductForm.handleSubmit()`:
     ```javascript
     if (this.ref) deleteId = true;
     if (deleteId) { formData.delete('id'); formData.delete('quantity'); }
     ```
     When a store uses a custom domain (`https://brand.com/cdn/shop/...`), `main.js` `src` does not contain `'net'`, setting `this.form.ref = true` and silently stripping `id` and `quantity` from every Add-To-Cart POST!
  5. **Cross-Component DOM Dataset Traps (`this.oseid` in `CartDrawer` & `ririality` in `SearchForm`)**:
     `this.oseid = headerIcons.querySelector('form').dataset[this.dataset.type]` queries `data-model="{{ settings.coun_viriality }}"` on the header search form. If the merchant disables header search, `querySelector('form')` is `null`, throwing an uncaught `TypeError` that breaks `CartDrawer`.
  6. **Base64 Endpoint Ping (`POST_LINK_INT` / `xml_eval` / `Shopify.internationalAccessAccept`) & Dropshipping Backdoors**:
     Remove `POST_LINK_INT` from `assets/main.js` and `assets/media-gallery.js`, remove `Shopify.internationalAccessAccept`, and delete third-party backdoor scripts (`assets/pod3.js`, `snippets/cjpod.liquid` calling `cjdropshipping.com` / `zippyhound.com`).

---

## 2. Theme Customizer, Web Components & Asset Integrity Pitfalls

### 2.1 Modal & Cart Drawer Click Suppression
* **Symptom**: Cart Drawer or Slide-out Modals open perfectly on the live storefront, but clicking the cart trigger icon inside the Shopify Theme Editor (Customizer) does nothing.
* **Underlying Cause**:
  Shopify Theme Editor's "Inspect" tool intercepts DOM clicks to highlight sections/blocks in the admin sidebar, calling `event.preventDefault()`.
  Many themes contain defensive code:
  ```javascript
  if (!trigger || event.defaultPrevented || event.metaKey || event.ctrlKey) return;
  ```
* **Remediation**:
  Check `this.inEditor` / `window.Shopify.designMode` before blocking on `event.defaultPrevented`:
  ```javascript
  const isBlocked = this.inEditor ? false : event.defaultPrevented;
  if (!trigger || isBlocked || event.metaKey || event.ctrlKey) return;
  ```

### 2.2 Header Block Selection vs Drawer Close
* **Symptom**: Selecting the header cart block in the Customizer causes the open drawer to abruptly close.
* **Remediation**: Check if the selected target is a cart trigger block (e.g. `_header-cart` or `[data-cart-drawer-trigger]`) and call `this.open()` instead of closing.

### 2.3 Statically Included Sections (e.g., `{% section 'cart-drawer' %}`)
* **Remediation**: Add a `preview_drawer` checkbox setting to `sections/cart-drawer.liquid` and check `if (this.inEditor && this.dataset.previewDrawer === 'true') this.open();`.

### 2.4 CustomElement Registry Collisions, Orphaned Web Components & Foreign Store CDN Leaks
* **Duplicate `customElements.define` Crashes**:
  - Commercial themes often define `<localization-form>` inline inside `sections/footer.liquid` (`{% javascript %}`) AND inside `assets/secondary.js`, or reload scripts on `shopify:section:load`.
  - **Rule**: Wrap EVERY `customElements.define('tag-name', ClassName)` in `if (!customElements.get('tag-name')) { ... }` and guard global class declarations (`window.CountdownTimer = window.CountdownTimer || class ...`).
* **Orphaned / Typoed Web Components in Snippets**:
  - Always cross-check custom tags (`<modal-v2>`, `<quantity-break-upsells>`, `<countdowns-timer>`) in `sections/*.liquid` and `snippets/*.liquid` against registered `customElements.define(...)` calls in `assets/*.js`.
  - Fix tag typos (`<countdowns-timer>` -> `<countdown-timer>`) and ensure missing interactive handlers (e.g., `.sizing-chart-button[data-unit="inches"|"cm"]` toggling `#inches-table` and `#cm-table`) and modal CSS (`modal-v2[open]`) are implemented.
* **Hardcoded Foreign Shopify Store CDN Assets**:
  - Commercial section packs frequently hardcode SVG/PNG URLs pointing to other merchants' Shopify stores (`//cdn.shopify.com/s/files/1/0691/6820/1986/files/...`, `cdn4.iconfinder.com`, or `cdnjs.cloudflare.com/.../jquery.min.js` with `defer` before inline `$(document).ready()`).
  - **Rule**: Replace all foreign `cdn.shopify.com/s/files/1/<store_id>/...` and `iconfinder.com` URLs with self-contained inline SVGs or `data:image/svg+xml;utf8,...` data URIs, and rewrite inline jQuery tabs (`snippets/horizontal-tabs.liquid`) into pure Vanilla JS.

---

## 3. Schema Localization & Strict RFC 8259 JSON Traps

### The Auto-Generated Comment & Trailing Comma Trap
* **Symptom**: Theme Customizer sidebars are covered in `missing translation` errors or sections fail to mount.
* **Underlying Cause**:
  Shopify's internal Theme Engine strictly enforces **RFC 8259 JSON** (no `/* ... */` headers, no `//` comments, no trailing commas `,}`).
* **Detection & Remediation**:
  Use a string-aware parser (`scripts/audit_commercial_theme_zip.py`) over all `.json` files in `locales/`, `config/`, `templates/` AND all `{% schema %}...{% endschema %}` blocks in `sections/*.liquid` and `blocks/*.liquid` to strip comments and trailing commas, then verify with `json.loads()`.

---

## 4. Cart Drawer Customizer DOM Invariant (`request.design_mode`)

Always add `request.design_mode` fallback in `layout/theme.liquid` and `blocks/_header-cart.liquid` so `<cart-drawer>` mounts in the Theme Editor even when `settings.cart_type != 'drawer'`.

---

## 5. Archive vs On-Disk Synchronization Checklist

* **Clean Archive Structure**: The root of the `.zip` archive must ONLY contain the canonical Shopify directories (`assets/`, `blocks/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/`). Never leave non-standard root directories (`docs/`, `__MACOSX/`) or `.DS_Store` inside a Shopify theme ZIP (Shopify rejects ZIP uploads with unrecognized root folders).
* **Full Schema & Storefront Localization (`locales/uk.json` & `locales/uk.schema.json`)**: Ensure both `locales/uk.json` and `locales/uk.schema.json` exist and are 100% valid RFC 8259 JSON.
