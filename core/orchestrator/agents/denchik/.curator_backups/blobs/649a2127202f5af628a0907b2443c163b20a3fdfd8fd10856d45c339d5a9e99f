# --- DNK-MRH-HEADER ---
# mrh_id: "references/shopify_cro_shipping_countdown_estimator_playbook.md"
# purpose: "Architecture, engineering patterns, and deployment playbook for zero-dependency CRO Shipping & Countdown Timer widgets in Shopify (Theme Blocks 2.0 & OS 2.0)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.3.0"
# updated_at: "2026-10-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🚚 Shopify Zero-Dependency CRO Shipping & Countdown Timer Widget Playbook (v2.3)

---

## 1. Architectural Philosophy: The Autonomous Theme Block 2.0 Invariant

Modern Shopify themes (Dawn 15+, Shrine Pro 2.0+, Horizon) use **Theme Blocks 2.0** architecture. The core architectural tenet of DNK CRO widgets is **Complete Autonomy**:

1. **Self-Contained Single File (`blocks/dnk-shipping-estimator.liquid`)**:
   - Liquid logic, HTML markup, embedded CSS scoped via `#dnk-shipping-estimator-{{ block.id }}`, vanilla JavaScript execution, and full `{% schema %}` live inside **one single file**.
   - No external `.js` or `.css` assets required in `assets/`.
   - **Zero Snippet Dependency**: In Theme Blocks 2.0, the block does **NOT** call `{% render 'snippet-name' %}`. It executes directly. Copying files to `snippets/` is strictly redundant for Theme Blocks 2.0 setups.

2. **Backward-Compatible Hybrid Mode (`snippets/dnk-shipping-estimator.liquid`)**:
   - For legacy Online Store 2.0 themes that lack nested `blocks/` support, the identical visual logic is mirrored into `snippets/`, driven by a section-level schema definition (`schema_block_code/block_schema.json`) and invoked via `{% render %}`.

---

## 2. Global GeoIP & FlagCDN Invariant (v2.3 SOTA Pattern)

- **Vector SVG Flags**: Use `https://flagcdn.com/w40/{country_code}.png` or SVG equivalents, dynamically set based on Shopify Localization / Cart country or client IP geolocation (`https://ipapi.co/json/` / Cloudflare `CF-IPCountry` header / Shopify `localization.country.iso_code`).
- **Graceful Fallback**: If GeoIP fails or client blocks external fetch, fallback immediately to default country configured in Theme Customizer settings (`default_country_code`).
- **Fixed Country Mode**: Option to override dynamic GeoIP and lock to a primary market (e.g. US, UK, DE, UA).

---

## 3. Real-Time Dynamic Date Calculation Engine

To prevent consumer skepticism, delivery date estimates must never show fixed or stale strings. The client engine calculates real relative dates:

```javascript
// Calculate cutoff and dispatch dates
const now = new Date();
const cutoffHour = {{ block.settings.cutoff_hour | default: 14 }};
const dispatchDaysMin = {{ block.settings.dispatch_days_min | default: 1 }};
const dispatchDaysMax = {{ block.settings.dispatch_days_max | default: 3 }};
const deliveryDaysMin = {{ block.settings.delivery_days_min | default: 3 }};
const deliveryDaysMax = {{ block.settings.delivery_days_max | default: 7 }};
```

1. **Business Days Logic**: Automatically skip weekends (Saturday/Sunday) if configured.
2. **Same-Day Dispatch Threshold**: If order placed before `cutoff_hour`, dispatch begins today (Day 0). If placed after cutoff, dispatch begins next business day (Day 1).
3. **Locale-Aware Formatting**: Output formatted using `Intl.DateTimeFormat(userLocale, { month: 'short', day: 'numeric', weekday: 'short' })`.

---

## 4. Theme Blocks 2.0 Deployment & Registration (Shrine Pro / Dawn 15+)

### Step 1: Copy Autonomous Block
Place `blocks/dnk-shipping-estimator.liquid` into the theme's `blocks/` directory.

### Step 2: Register in Parent Container Block Schema
In nested-block themes like Shrine Pro, product details are managed by a container block (e.g., `blocks/main-product_details.liquid`), NOT the root section file:

```json
// Inside blocks/main-product_details.liquid schema:
"blocks": [
  { "type": "dnk-shipping-estimator" },
  { "type": "@app" },
  ...
]
```

> **⚠️ Critical JSON Trap**: Never insert `{ "type": "dnk-shipping-estimator" },` at the very end of `"blocks": [...]` if followed by `]`. Trailing commas will fail Shopify theme JSON schema validation! Always place it immediately after `[` or safely before another element with proper commas.

### Step 3: Visual Customizer Activation
1. Open Shopify Theme Customizer (`/admin/themes/.../editor`).
2. Navigate to any Product Template.
3. In the left sidebar under `Product information`, expand the **`Details`** (or **`Product details`**) container block.
4. Click **`+ Add block`** inside `Details`.
5. Select **`Shipping & Timer DNK🧬`** and drag it to desired position (optimal: directly below `Buy Buttons` / Price).

---

## 5. Classical Online Store 2.0 Deployment (Legacy Fallback)

For themes without `blocks/` folder support:
1. Copy `snippets/dnk-shipping-estimator.liquid` to `snippets/`.
2. Open `sections/main-product.liquid`.
3. Locate `{% case block.type %}` in the template and add:
   ```liquid
   {%- when 'dnk_shipping_estimator' -%}
     {% render 'dnk-shipping-estimator', block: block %}
   ```
4. Insert contents of `schema_block_code/block_schema.json` into the `blocks` array in `sections/main-product.liquid` `{% schema %}`.

---

## 6. Pre-Commit Verification Checklist

- [ ] Block renders cleanly without horizontal overflow on mobile viewports (<375px).
- [ ] Countdown timer ticks every second and auto-resets past daily cutoff hour.
- [ ] Flag image loads without 404/CORS errors via FlagCDN.
- [ ] Estimated delivery date displays future date formatted in customer's local language.
- [ ] Theme Customizer settings update live without full iframe reload (Shopify Block Events `shopify:block:select`).
