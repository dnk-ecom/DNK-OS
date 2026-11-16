# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_theme_licensing_and_activation_architecture.md"
# purpose: "Reverse engineering audit and production implementation guide for Shopify Theme licensing, DRM gates, and Story/Lumin verification mechanics."
# canonical_source: true
# status: "Active"
# version: "1.2.0"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛡️ Shopify Theme Licensing & Activation Architecture (SOTA Playbook)

## 1. Overview & Core Philosophy
Commercial third-party Shopify themes (e.g. Lumin 2.0, Casaio, Story Theme v4.0.0) implement remote licensing verification to protect intellectual property while navigating Shopify's constraints:
- **Zero Front-End Customer Impact**: Reputable theme DRM isolates license gates to Shopify Theme Customizer (`Shopify.designMode === true` or Liquid `request.design_mode`). Overly aggressive themes that run DRM on storefronts degrade Core Web Vitals and risk SEO penalties.
- **Camouflage & Poison-Pill Obfuscation**: Vendor scripts frequently use deceptive names (e.g. `section-loader.js` containing zero section-loading logic) and companion timer traps to defeat naive script deletion.
- **Domain Identity Anchoring**: Authentication binds to `shop.permanent_domain` (`store-name.myshopify.com`) or `location.hostname`.

---

## 2A. Reverse-Engineered Architecture: Shrine Pro v1.9.0 Pattern (Remote Core CDN + 9-Layer Kill-Switch)

Unlike Story or Lumin (which keep functional Web Components local and run DRM in sidecar scripts), Shrine Pro (`v1.9.0`) hosts its entire functional storefront engine (`assets/main.js`) on an external vendor CDN (`https://js.shrinetheme.com/js/v2/main.js?version=1`) and weaves 9 interlocking anti-tamper traps directly into the Web Component classes (`ModalDialog`, `PickupAvailabilityDrawer`, `ProductInfo`, `MenuDrawer`):

### 2A.1. Missing Local Core & External CDN Dependency (`layout/theme.liquid`)
- The theme ZIP ships **without** `assets/main.js`. Instead, `layout/theme.liquid` loads:
  - `<script src="https://shopify.jsdeliver.cloud/js/config.js" defer="defer"></script>` (typosquatted `jsdelivr` tracker).
  - `<script src="https://js.shrinetheme.com/js/v2/main.js?version=1" defer="defer"></script>` (217 KB obfuscated bundle with a 1,036-entry string array `a0_0x2bcf` rotated via checksum `0x8ef9a`).
- Removing the CDN tag without deobfuscating and localizing `assets/main.js` breaks all 31 custom elements (`cart-drawer`, `product-form`, `quantity-breaks`, `shrine-subscription-widget`, `quantity-break-upsells`, `bundle-deals`, `sticky-atc`, `variant-selects`, etc.).

### 2A.2. The 9 Interlocking DRM & Anti-Tamper Mechanisms
1. **CSS Main Visibility Blocker (`layout/theme.liquid` line 124)**:
   - `{% if settings.animations_type == blank or settings.animations_type.size < 196 %}main{visibility:hidden !important;}{% endif %}` hides the entire `<main>` storefront if the 196-character license token (`settings.animations_type`) is blank or shortened.
2. **Remote Kill-Switch Endpoint (`metafieldPoly()` in `main.js`)**:
   - Reconstructs a token from `<sticky-header data-modal="...">` (16-char middle slice) + `<footer data-animations-type="...">` (prefix + suffix) and sends `POST https://backend.shrinetheme.com/api/analytics/v2/stop` with `{ d: Shopify.shop, t: token, i: theme.id }`.
   - If the server returns HTTP `201`, it executes `document[b].innerHTML = h` (remote storefront wipe).
3. **Anti-Fetch-Monkeypatch Inspector (`_0x3f6b10` & `_0x27bf64`)**:
   - Scans `window.fetch.toString()`, `XMLHttpRequest.prototype.open.toString()`, and every inline `<script>` tag's `textContent` for strings like `shrinetheme.com`, `window.fetch`, `fetch.apply`, or `Response`.
   - If detected, immediately overwrites `document.body.innerHTML` with an unauthorized theme lockout screen and spawns a hidden `<iframe>` to grab an unpatched `iframe.contentWindow.fetch`.
4. **Coupled DOM Token Attributes (`sections/header.liquid`, `sections/footer.liquid`, `snippets/header-drawer.liquid`)**:
   - `header.liquid` splits `settings.animations_type` via `slice: 90, 16` into `data-model`/`data-modal` and `data-Loading` (`size`).
   - `footer.liquid` injects `data-type="{{ settings.animations_type }}"` and `data-animations-type` (prefix + suffix without the 16-char middle slice).
   - `MenuDrawer.initTrapFocus()` and `ModalDialog` verify that these DOM attributes exist and match length `196`; otherwise they call `popupTimer()` which wipes `document.body.innerHTML = ''` after a random 1.5s–4.5s delay.
5. **Checksum & `Shopify.postLink` Fingerprint (`Shopify.internationalAccessAccept` & `POST_LINK_INT`)**:
   - Computes character code sums (`serial = 3811`, `POST_LINK_INT = 259`) of `Shopify.postLink.toString()` and stores length mismatches in `localStorage.getItem('xml_eval')`. If tampered, calls `popupTimer()`.
6. **Hardcoded Expiration Timebomb (`formatDates` / `checkDateValidity`)**:
   - Compares current date against `'2027-10-10'` inside `PickupAvailabilityDrawer`.
7. **Section Dataset Trap (`oseid` & `defMed` in `ProductInfo`)**:
   - Checks `this.dataset.oseid || this.dataset.section` and `window.defMed` during variant changes; breaks product form submission if missing.

### 2A.3. Deobfuscation & Localization Remediation Recipe
1. **Decode String Array (`a0_0x2bcf` / `a0_0x2419`)**:
   - Extract the array and rotation IIFE, evaluate in Node.js (`vm.runInNewContext`), and replace all `a0_0x2419(0x...)` calls (plus proxy aliases `const _0x... = a0_0x2419`) with JSON-escaped string literals.
2. **Strip DRM Functions & Keep Clean Web Components**:
   - Remove the top-level anti-tamper IIFE, `metafieldPoly()`, `popupTimer()`, `playMedia()`, `formatDates()`, `checkDateValidity()`, `Shopify.internationalAccessAccept()`, `POST_LINK_INT`, and `serial`.
   - Replace `MenuDrawer.prototype.initTrapFocus` with a no-op (`initTrapFocus() {}`), clean `PickupAvailabilityDrawer.prototype. trapFocus`, and simplify `ProductInfo` `sectionId` getter to `return this.dataset.section || this.dataset.originalSection;`.
   - Format via Prettier (`--parser babel`), verify with `node --check assets/main.js`, and wire `<script src="{{ 'main.js' | asset_url }}" defer="defer"></script>` in `layout/theme.liquid`.
3. **Clean Liquid & JSON Trailing Commas**:
   - Remove `animations_type` from `layout/theme.liquid`, `sections/header.liquid`, `sections/footer.liquid`, `blocks/header-drawer.liquid`, `snippets/header-drawer.liquid`, `config/settings_schema.json`, and `config/settings_data.json`.
   - Strip trailing commas `,}` / `,]` inside `{% schema %}` blocks (`blocks/logo.liquid`, `blocks/header-drawer_localization.liquid`, `blocks/product_subscription.liquid`, `sections/header.liquid`, `sections/main-collection-product-grid.liquid`, `sections/page-scroll-progress.liquid`) before running strict `json.loads`.

---

## 2. Reverse-Engineered Architecture: Story Theme v4.0.0 Pattern

### 2.1. Dual-Script Ingestion & Snippet Tripwires
- `layout/theme.liquid`, `layout/password.liquid`, `templates/gift_card.liquid`:
```liquid
<script src="{{ 'theme-runtime.js' | asset_url }}" defer></script>
<script src="{{ 'section-loader.js' | asset_url }}" defer></script>
```
- Injected into `<head>` via `{%- render 'css-variables' -%}`:
```liquid
snippets/css-variables.liquid (inline <script> right after {% endstyle %})
```

### 2.2. Triple-Component Mechanics & Camouflage
1. **`theme-runtime.js` (Visual Blocker & Primary Timebomb Trap)**:
   - Sets global state: `window.__stBlocked = false; window.__stArmed = true;`
   - Exports global API: `window.__st = { ok: () => { window.__stArmed = false; }, showBlock: fn };`
   - **Poison-Pill Watchdog**: Starts a 1900ms timer (`setTimeout`). If `window.__stArmed` remains `true` (i.e. if an unauthorized user deletes `section-loader.js` without deleting `theme-runtime.js`), it injects a CSS payload inflating all headings (`h1`, `h2`, `p`) to 70px red text and disables checkout/cart buttons.
   - **`showBlock()` Trigger**: Reads the pre-rendered DOM template from `.theme__modal--callback` in `sections/header.liquid` (designed by vendors to survive merchant locale modifications), injects a full-page modal (`Your licence is not active`), applies `pointer-events: none` to the page, and adds a direct CTA to `https://www.story-theme.com/dashboard`.

2. **`section-loader.js` (Camouflaged License Auditor)**:
   - Contains **zero** section loading logic. The filename is purely deceptive.
   - Immediately disarms the timebomb: `window.__st.ok()`.
   - Resolves store identity via `<meta name="shop-url" content="...">` or `location.hostname.toLowerCase().replace(/^www\./, '')`.
   - Sends network probe via `fetch(..., { credentials: "omit" })`:
     - Primary: `GET https://www.story-theme.com/api/v1/runtime/{domain}`
     - Fallback: `GET https://api.story-theme.com/api/v1/runtime/{domain}`
   - If payload returns `{ "active": false }` or HTTP error occurs, invokes `window.__st.showBlock()`.

3. **`snippets/css-variables.liquid` (Secondary Liquid Inline Tripwire / Dead Man's Switch)**:
   - Placed after `{% endstyle %}` (e.g. line 693) as a standalone `<script>`.
   - Obfuscated key resolution:
     `var k = String.fromCharCode(95, 95, 115, 116, 65, 114, 109, 101, 100); // "__stArmed"`
   - Fail-closed condition:
     `if (window[k] !== false) { ... }`
   - **The Deletion Trap**: If an auditor deletes both `theme-runtime.js` and `section-loader.js`, `window.__stArmed` is `undefined`. Because `undefined !== false` evaluates to `true`, the secondary trap fires at 2000ms, mutating all `h1, h2, h3, h4, h5, p, a, span, li, button, label, small, strong, em` styles to `color: red !important; font-size: 70px !important;`.

---

## 3. Reverse-Engineered Architecture: Lumin / Casaio Pattern

### 3.1. Liquid Entry Points (`theme-editor.liquid` & `scripts.liquid`)
```liquid
{%- if request.design_mode -%}
  <script>window.__te_d = "{{ shop.permanent_domain }}";</script>
  <script src="{{ 'theme-activation-overlay.js' | asset_url }}" defer="defer"></script>
  <script src="{{ 'theme-editor.js' | asset_url }}" type="module" defer="defer"></script>
{%- endif -%}
```

### 3.2. Obfuscation & Verification Routine (`theme-editor.js`)
Endpoints are assembled via Base64 chunks to avoid simple string grep by unauthorized redistributors:
```javascript
if (typeof window.__te_d === 'string' && window.Shopify?.designMode) {
  const _p = atob('aHR0cHM6Ly88cHJvamVjdD4uc3VwYWJhc2UuY28vZnVuY3Rpb25zL3YxLw==');
  const _q = atob('dmVyaWZ5') + '-' + atob('YWN0aXZhdGlvbg==');
  window.__tu = _p + _q;
}

if (window.__tu && typeof window.__ts === 'function') {
  fetch(window.__tu, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ store_url: window.__te_d })
  })
  .then(res => res.json())
  .then(data => {
    if (data.activated) {
      window.__av = true;
    } else {
      window.__ts?.(); // Triggers overlay modal window.__sd()
    }
  })
  .catch(() => {
    if (!window.__av) window.__ts?.(); // Fail-closed on unauthorized network block
  });
}
```

### 3.3. Modal Overlay (`theme-activation-overlay.js`)
If `data.activated !== true`:
1. Creates a backdrop with `position: fixed`, `inset: 0`, `background: rgba(15,23,42,0.45)`, `backdrop-filter: blur(6px)`.
2. Sets `zIndex: 2147483647` (highest possible 32-bit signed integer).
3. Locks page scroll: `document.body.style.overflow = 'hidden'`.
4. Displays the store's `permanent_domain` in a read-only input with 1-click clipboard copy.
5. Directs the merchant to the activation portal (e.g., `https://activate.lumintheme.com/`).

---

## 4. Serverless Backend Schema & Edge Functions (Supabase / PostgreSQL)

### 4.1. Database Schema
```sql
CREATE TABLE licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key TEXT UNIQUE NOT NULL, -- e.g. '8UQF-NZ8B-WQCF-DO9L-I6T6-EIDH'
    max_activations INT DEFAULT 1,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'revoked')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE activations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_id UUID REFERENCES licenses(id) ON DELETE CASCADE,
    store_url TEXT NOT NULL UNIQUE, -- e.g. 'store-test-ecom.myshopify.com'
    activated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_activations_store_url ON activations(store_url);
CREATE INDEX idx_licenses_license_key ON licenses(license_key);
```

### 4.2. Activation Edge Function (`POST /activate-theme`)
- **Input**: `{ "activation_key": "XXXX-...", "store_url": "store.myshopify.com", "force_change": false }`
- **Validation**:
  1. Clean `store_url` (strip protocol, trailing slashes, enforce `.myshopify.com`).
  2. Query `licenses` table for active key.
  3. If already bound to another store and `force_change == false`, return `{ already_activated: true, current_store_url }`.
  4. If re-binding allowed, update or insert into `activations`.
  5. Return `{ success: true, message: "Theme activated successfully!" }`.

### 4.3. Verification Edge Function (`POST /verify-activation`)
- **Input**: `{ "store_url": "store.myshopify.com" }`
- **Execution**: Fast lookup in `activations` joined with active `licenses`.
- **Response**: `{ "activated": true, "message": "Theme is activated", "activated_at": "..." }` or `{ "activated": false }`.

---

## 5. Audit & Neutralization Pitfalls
- **Trap 1: Removing only the auditor script**: Deleting `section-loader.js` without removing `theme-runtime.js` triggers the poison-pill timeout (70px red fonts). Both coupled assets must be handled together.
- **Trap 2: Assuming filename reflects purpose**: Vendor DRM scripts intentionally mimic core theme modules (`section-loader.js`, `theme-runtime.js`, `cart-helper.js`). Always perform AST/deobfuscation analysis before refactoring.
- **Trap 3: Customizer iframe bypass**: Client-side fetch gates run inside Shopify Admin iframe (`admin.shopify.com/.../editor`). Whitelisting development stores via vendor dashboard is the primary compliant resolution.
- **Trap 4: Missing DOM-coupled modal payloads**: DRM visual blockers frequently rely on hidden pre-rendered DOM blocks in core sections (e.g., `sections/header.liquid` containing `.theme__modal--callback` with un-translatable merchant warnings) rather than dynamically constructing markup in JS.
- **Trap 5: Secondary inline Liquid tripwires (Snippets Dead Man's Switch)**:
  Vendors plant secondary fallback tripwires in snippet templates (e.g. `snippets/css-variables.liquid` right after `{% endstyle %}`).
  - Uses obfuscated `String.fromCharCode(...)` to check `window['__stArmed'] !== false`.
  - If both runtime and auditor scripts were deleted, `window.__stArmed` is `undefined`, which satisfies `!== false` and triggers font/color destruction after a 2s timer.
  - **Resolution**: Always scan all `.liquid` files for `String.fromCharCode`, inline `<script>` tags inside `snippets/`, and selectors targeting `setProperty('font-size', ...)`.

---

## 6. SOTA Theme Telemetry & Obfuscation Audit Protocol

When auditing a commercial or imported theme for external network calls and obfuscation:
1. **Obfuscation Signatures Scan**:
   - Variable name scrambling: `_0x[a-f0-9]{4,6}`, `a0_0x[a-f0-9]{4,6}`.
   - String array shuffles & rotation functions: `(function(arr, offset) { ... })(array, 0x12345)`.
   - Hex / Unicode escapes: `\x[0-9a-fA-F]{2}`, `\u[0-9a-fA-F]{4}`.
   - Character code reconstructions: `String.fromCharCode(`.
   - Base64 encoders / decoders: `atob(`, `btoa(`.
2. **Third-Party Telemetry vs Essential App Distinction**:
   - **Proprietary Vendor Telemetry**: Endpoints targeting author domains (e.g. `api.story-theme.com`, `activate.lumintheme.com`, `/dashboard`).
   - **Supported E-Commerce Integrations**: Klaviyo (`a.klaviyo.com`), 17Track (`17track.net`), Trustpilot (`widget.trustpilot.com`), CDN fonts (`fonts.shopifycdn.com`), YouTube/Vimeo embeds.
3. **Template Coupling Audit**:
   - Cross-check asset references across `layout/*.liquid` (`theme.liquid`, `password.liquid`) and `templates/*.liquid` (`gift_card.liquid`).
   - Inspect `snippets/css-variables.liquid` and other core CSS/style snippets for post-`{% endstyle %}` inline script injections.
   - Inspect `sections/header.liquid` or `sections/footer.liquid` for hidden callback elements or fallback modals (`.theme__modal--callback`).
