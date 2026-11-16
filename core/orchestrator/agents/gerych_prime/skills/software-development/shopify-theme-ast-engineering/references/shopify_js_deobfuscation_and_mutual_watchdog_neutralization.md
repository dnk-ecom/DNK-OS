# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_js_deobfuscation_and_mutual_watchdog_neutralization.md"
# purpose: "Playbook for full JS deobfuscation (_0x count = 0), Baseline Rosetta-Stone AST alignment, and Mutual Watchdog Mesh neutralization in commercial Shopify OS 2.0 / Theme Blocks 2.0 themes (Shrine Pro 1.9.0, Ascendify 2.10.0)."
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🔓 Full JS Deobfuscation (`_0x = 0`), Baseline Rosetta-Stone Alignment & Mutual Watchdog Neutralization

## 1. Two-Tier Obfuscation Architecture in Commercial Shopify Themes
Commercial Shopify themes built on Dawn / Shrine Pro cores (`Shrine Pro 1.9.0`, `Ascendify 2.10.0`) frequently protect their JavaScript engines (`assets/main.js`, `assets/global.js`, `assets/secondary.js`, `assets/kit-fontawesome.js`) and inline `<script>` snippets using `javascript-obfuscator` with:
1. **Rotating String Array + Dual Decoders**:
   - A base array `_0xXXXX()` of 500–2,000 strings rotated at runtime via a checksum `while (!![]) { try { parseInt(...) } catch { push(shift()) } }` IIFE.
   - Often paired with two distinct decoder functions: a plain index lookup decoder (`_0xdec1`) and a Base64 + `decodeURIComponent` alphabet decoder (`_0xdec2`) for sensitive DRM endpoints and DOM selectors.
2. **Control-Flow Flattening & Proxy Object Dictionaries**:
   - Every function creates a local proxy object mapping 5-letter keys (`abcde: function(x, y) { return x + y; }`, `fghij: "string literal"`) so binary operators, function invocations, and string constants are hidden behind `_0xproxy["abcde"](a, b)`.
3. **Cross-File Mutual Watchdog Mesh (Ascendify 2.10.0 Pattern)**:
   - Removing the primary license check (`backend.ascendifytheme.com/api/validate.php`) inside `global.js` triggers secondary time-bombed watchdogs hidden inside innocently named asset files and Liquid snippets.

---

## 2. The 4-Stage Deterministic Deobfuscation Pipeline (`_0x count = 0`)

### Stage 1: Safe Sandbox String-Table Evaluation (`vm.runInNewContext`)
Never attempt to statically calculate the string rotation offset by hand. Extract the preamble (from byte 0 up to the first custom element class or `function getFocusableElements`) and execute the string array + rotator IIFE inside an isolated Node.js `vm` context:
- Capture all decoder functions (`_0xdec1`, `_0xdec2`).
- Walk the AST/token stream to resolve all wrapper alias functions (`const _0xalias = _0xdec1;`, `function _0xwrap(a, b) { return _0xdec1(a - 0x1a4, b); }`) transitively (4–5 passes) and replace every call with `JSON.stringify(decodedString)`.

### Stage 2: Proxy Dictionary Inlining & Dead Dictionary Removal
- Parse local proxy object declarations (`const _0xobj = { 'abcde': function(a, b) { return a === b; }, 'fghij': 'literal' };`).
- Inline string properties directly and replace proxy method calls (`_0xobj.abcde(x, y)`) with their underlying binary/logical expressions `((x) === (y))` or function calls `fn(arg1, arg2)`.
- Caution: Ensure regexes matching property assignments check negative lookahead `(?!\s*=[^=]|\s*\()` so equality comparisons (`===` or `==`) inside `if (...)` conditions are never mistaken for property reassignments.

### Stage 3: Baseline "Rosetta Stone" AST Alignment (`CLEAR JS Shrine Pro 1.3.2`)
When an unminified reference baseline of the same theme family exists (such as `CLEAR JS Shrine Pro 1.3.2`):
- **Shared Core Replacement**: Replace identical Web Components (`QuantityInput`, `CartRemoveButton`, `CartDrawer`, `ModalDialog`, `BulkModal`, `StickyHeader`, `LocalizationForm`, `ProductRollup`, `DeferredMedia`, `SplideComponent`, `AtcButton`, ` Upsell`, `QuickAdd`, `ProductRecommendations`, `BundleDeals`, `SlideshowComponent`, `CouponCode`, `ScrollSpy`, `Testimonials`, `ComparisonSlider`, `ContentContainer`) directly with the clean unminified baseline source.
- **Delta Isolation & Clean Reconstruction**: Isolate newly added methods or components in the newer release (`Shrine Pro 1.9.0`'s `CartDrawerGift`, `CompareColor`, `MainProductDetails`, `ProductVariant`; `Ascendify 2.10.0`'s `ThemeSubscriptionWidget`, `DynamicDates.month_day` ordinal suffixes, `.sizing-chart-button` listener) and reconstruct them with 100% semantic parameter and local variable names (`_0x count = 0`).

### Stage 4: ESBuild AST Normalization & `node --check` Verification
- Pass the reconstructed bundle through `esbuild --loader=js` (without `--minify`) to normalize bracket properties (`obj["addEventListener"]` ➔ `obj.addEventListener`), fold constants (`!0` / `!1`), and format with consistent 2-space indentation.
- Run `node --check` on every `.js` file and verify `grep -c "_0x" assets/*.js` returns `0`.
- **Concatenated Keyword Guard (`returnfalse;` / `returntrue;`)**: Note that `returnfalse;` is **syntactically valid JavaScript** (parsed as an expression statement referencing an undeclared identifier `returnfalse`), so `node --check` and `esbuild` will **not** flag it! It only throws `ReferenceError: returnfalse is not defined` at runtime (e.g., at the end of `validateSingleQuantityCartItems` inside `CartItems.updateQuantity`'s `finally` block or `selectAvailableOption`). Always scan deobfuscated JS for `\breturn(false|true|null|undefined)\b` and replace with `return $1`.

---

## 3. Taxonomy of the 15 DRM, Sabotage & Watchdog Traps (Shrine Pro & Ascendify)

When auditing a Shrine-derived or Ascendify-derived commercial theme, check and neutralize all 15 layers:

| Layer | Location | Mechanism & Sabotage Payload | Neutralization Action |
| :--- | :--- | :--- | :--- |
| **1** | `layout/theme.liquid` | External `<script src="https://js.shrinetheme.com/js/v2/main.js">` + `visibility:hidden !important` inline `<style>` | Replace with local `{{ 'main.js' \| asset_url \| script_tag }}` and remove blocking `<style>` |
| **2** | `snippets/meta-tags.liquid` | `{% if settings.icon_fav == blank or settings.icon_fav.size < 10 %}main{visibility:hidden !important;}{% endif %}` + `<meta name="meta-tag-data" data-meta-value="{{ settings.icon_fav }}">` | Strip the conditional `<style>` and telemetry `<meta>` tag completely |
| **3** | `assets/cart-functions.js` & `assets/header-icons.js` | **100% Trojan Watchdogs**: Monkey-patch `window.fetch` to track calls to `backend.ascendifytheme.com/api/validate.php` and `token.php`. If both are not called within `5000ms` of `DOMContentLoaded`, executes `document.querySelector('main').innerHTML = ''` | Delete files and remove `<script>` tags from `sections/header.liquid` and `sections/cta-header-section.liquid` |
| **4** | `assets/header-drawer-icons.js` | **Anti-Mock Watchdog**: Wraps `window.fetch`; if any response returns `status === 403 && statusText === 'Blocked'`, wipes `<main>` after `3000ms` | Delete file and remove `<script>` tag from `sections/header.liquid` |
| **5** | `assets/footer-form.js` | **Secondary Domain Watchdog**: Sends `POST` to `backend.ecomoptimizationblueprint.com/api/validate.php` (`key: "demo-key"`). Wipes `<main>` after `3000ms` on failure | Delete file and remove `<script>` tags from `sections/footer.liquid` and `sections/footer-2.liquid` |
| **6** | `snippets/cart-items-data.liquid` & `snippets/footer-data.liquid` | **Inline Obfuscated Lockout**: Checks `.header_search_form[header-search-value]` length `< 31`. Replaces `document.body.innerHTML` with `"Oops! 😳 It seems like you are not authorized to use this theme!"` | Delete both snippets and remove `{% render %}` from `sections/footer.liquid`, `sections/footer-2.liquid`, and `snippets/cart-drawer.liquid` |
| **7** | `snippets/section-previews.liquid` | **Console Hijack & ReDoS**: Hijacks `window.console.*`, runs catastrophic backtracking regex `(((.+)+)+)+$`, intercepts `document.documentElement.replaceChild` | Delete snippet and remove `{% render 'section-previews' %}` from `layout/theme.liquid` |
| **8** | `assets/kit-fontawesome.js` & `assets/global.js` (after `PredictiveSearch`) | **Silent Cart Quantity Sabotage**: If `meta[data-meta-value]` is missing or `< 31` (`< 25`) chars, injects `<input type="hidden" name="quantity" value="<random 0..10>">` into every `<product-form>` so customers add random item counts to cart | Strip the sabotage tail from `kit-fontawesome.js` and `global.js` |
| **9** | `assets/global.js` (after `DynamicDates`) | **Silent ATC & Checkout Button Removal**: Checks `.menu-drawer-container[header-drawer-value]` length `< 30`; runs `document.querySelectorAll('.atc-button, .cart__checkout-button').forEach(btn => btn.remove())` | Remove block and strip `header-drawer-value` attribute from `snippets/header-drawer.liquid` |
| **10** | `assets/global.js` (after `ComparisonSlider`) & `assets/secondary.js` (after `TncCheckbox`) | **Primary License Fetch**: Sends `POST` to `https://backend.ascendifytheme.com/api/validate.php` and `token.php`, replacing `document.body` on failure | Strip both network IIFEs completely |
| **11** | `assets/global.js` (`checkDateValidity` & `formatDates`) | **Time-Bomb (`2027-12-31`) & Customizer Break**: Compares current date against `var date = "2027-12-31"`, clears `<body class="gradient">` and calls `Shopify.postLink('', {})` on `shopify:section:load` | Remove `var date`, `formatDates`, and `checkDateValidity` |
| **12** | `assets/global.js` (`POST_LINK_INT`, `metafieldPoly`, `initTrapFocus`, `popupTimer`) | **DOM / Fetch Poisoning**: Redirects forms to `https://vitalize.shrine.io`, strips `type="application/json"` script tags after 15s, deletes `<main>` after 19s, injects piracy popup in `Shopify.designMode` | Strip all 4 functions and set `Shopify.internationalAccessAccept = true` cleanly |
| **13** | `assets/secondary.js` (`serial`, `defMed`, `oseid`, `playMedia`) | **Secondary Traps**: Sends `GET https://api.THEMENAME.com/api/get_serial`, removes `<style>` tags (`defMed`), deletes `[data-shopify]` (`oseid`), wipes `document.body` (`playMedia`) | Strip all 4 functions from `secondary.js` |
| **14** | `assets/shopify-jsdeliver-cloud.js` & `layout/theme.liquid` | **External Tracker**: Loads `https://shopify.jsdeliver.cloud/js/config.js` | Delete file and remove `<script>` tag from `layout/theme.liquid` |
| **15** | `snippets/cart-drawer.liquid:423` | **ASCII-Array `String.fromCharCode` Loader**: Decodes decimal array (`[104,116,116,112,...]`) without `_0x` names to inject external `cdn.shopify.com/s/files/1/0557/0887/6873/files/header-theme.min.js`, which POSTs to `backend.ascendifytheme.com/api/validate.php` and replaces `document.body` | Strip inline `<script>` and audit all `fromCharCode`/`createElement('script')` across all `.liquid` files |

---

## 4. Residual Coupled Poison-Pills in Web Components (`CartItems`, `ProductForm`, `ProductInfo`)

Removing top-level DRM functions (`formatDates`, `checkDateValidity`, `defMed`) is **not sufficient** on its own if you leave behind the coupled boolean flags they initialized inside legitimate Web Components. Always audit and strip these 4 coupled poison-pills in `assets/global.js` / `assets/main.js`:

1. **`CartItems.updateQuantity` Stale-DOM Trap (`❗ line parameter is invalid.`)**:
   - **Symptom**: Clicking `+`, `-`, or `<cart-remove-button>` in Cart Drawer mutates the server cart on the first click, does **not** re-render the Cart Drawer DOM, and throws `❗ line parameter is invalid.` on the second click.
   - **Root Cause**: Right after `fetch('/cart/change.js')` parses `parsedState`, Shrine/Ascendify inserts:
     ```js
     if (!this.lineItemContainer) return;
     ```
     Because `this.lineItemContainer = true` was only set inside the removed `formatDates()` DRM function, `updateQuantity` returns early *after* mutating the backend cart but *before* `this.getSectionsToRender().forEach(...)` updates the Cart Drawer HTML!
   - **Fix**: Delete `if (!this.lineItemContainer) return;` and make `getSectionsToRender().forEach(...)`, `updateLiveRegions`, `enableLoading`, `disableLoading`, and `fixParsedHtml(oldHtml, parsedHTML)` null-safe (`const oldTimer = ...`).

2. **`ProductForm.handleSubmit` & `ProductInfo` `this.ref` Poison-Pill**:
   - **Symptom**: Product bundles, quantity breaks, or main product variants fail to add to cart or submit with missing `id`.
   - **Root Cause**: `ProductInfo` sets `if (!this.deferredMedia || !this.deferredMedia.src || !this.deferredMedia.src.includes('net')) this.form.ref = true;`. Then `ProductForm.handleSubmit` checks `if (this.variantInputs && !this.ref)` (skipping variant inputs) and `if (this.ref) deleteId = true;` (deleting the main variant `id` from `formData`!).
   - **Fix**: Remove `this.form.ref = true`, change `if (this.variantInputs && !this.ref)` to `if (this.variantInputs)`, and remove `if (this.ref) deleteId = true;`.

3. **`ProductInfo.initShareLinks` (`this.shareUrl`)**:
   - Remove `if (!urlBtn) this.shareUrl = true;` from `initShareLinks()`.

4. **`snippets/cart-drawer.liquid` (`{% when 'subtotals' %}`) Order-Independent Savings & Floating Drawer Pitfalls**:
   - **Symptom**: After fixing `CartItems.updateQuantity`, changing line item quantities updates `.cart-drawer__totals`, or leaves the savings badge (`[savings]`), crossed-out compare total (`total_compare_price`), or `additional_text` stale/zeroed out; or the closed floating cart drawer (`enablefloatingcartdrawer`) peeks 10px into the right edge of the viewport.
   - **Root Cause**:
     - In Shrine/Ascendify/DNK_Ecom monolithic `snippets/cart-drawer.liquid`, `total_compare_price` is initially accumulated inside `{% when 'cart_items' %}`. Inside `{% when 'subtotals' %}`, `if block.settings.display_subtotal` resets `{% assign total_compare_price = 0 %}` and loops only over `item.variant.compare_at_price` (ignoring automatic/line-level discounts where `item.original_line_price > item.final_line_price`), or leaves `total_compare_price` uninitialized if `subtotals` is ordered above `cart_items` or if `display_subtotal` is unchecked while `display_savings` is checked.
     - In `DNK_Ecom_sections 1.0.0`, the `if block.settings.additional_text != blank` branch accidentally re-renders `subtotal_left_text` and `subtotal_right_text` instead of `block.settings.additional_text`.
     - When `settings.enablefloatingcartdrawer` is active, `.drawer__inner.spacingouter { position: absolute; right: 10px; }` combined with base `transform: translateX(100%)` leaves 10px visible on the right edge when closed.
   - **Fix**:
     - Compute `total_compare_price` and `display_compare2` autonomously at the very top of `{% when 'subtotals' %}` (handling both `item.variant.compare_at_price > item.final_price` and `item.original_line_price > item.final_line_price`), and remove the redundant `{% assign total_compare_price = 0 %}` reset inside `display_subtotal`.
     - Preserve `.cart-drawer__body` scroll position (`cartBodyScroll`) across `fixParsedHtml(oldHtml, parsedHTML)` so quantity updates do not jump the drawer scroll to top.
     - Add `transform: translateX(calc(100% + 20px));` on `.drawer__inner.spacingouter` and `transform: translateX(0);` on `.drawer.active .drawer__inner.spacingouter`.

---

## 5. Live Storefront Verification & Direct Admin GraphQL `themeFilesUpsert`

1. **Fixing `DNS_PROBE_FINISHED_NXDOMAIN` on Storefront Preview**:
   - If `<store>.myshopify.com/?preview_theme_id=<id>` redirects (`HTTP 301 x-redirect-reason: primary_domain_redirection`) to an unregistered/expired custom domain, open `https://admin.shopify.com/store/<store>/settings/domains`, click the `<store>.myshopify.com` entry, and switch **Change domain type -> Primary domain**.
2. **Direct In-Browser Theme Asset Patching (`themeFilesUpsert`)**:
   - When connected to an authenticated Shopify Admin tab in Chrome, push fixed `.js` / `.liquid` files directly into any theme (`gid://shopify/OnlineStoreTheme/<THEME_ID>`) via `/admin/internal/web/graphql/core`:
     ```js
     mutation themeFilesUpsert($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
       themeFilesUpsert(themeId: $themeId, files: $files) {
         upsertedThemeFiles { filename }
         userErrors { field message }
       }
     }
     ```
     where each file item is `{ filename: "assets/global.js", body: { type: "TEXT", value: "<file_content>" } }`.

