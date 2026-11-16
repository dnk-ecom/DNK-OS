---
name: shopify-native-bundle-widgets
description: "Use for native Shopify Liquid Bundle & Save PDP widgets."
version: "1.0.0"
author: "DNK-e.com Maksym & Gerych"
license: "MIT"
metadata:
  hermes:
    tags: [shopify, liquid, bundle, pdp, cro, e-commerce]
    related_skills: [shopify-theme-ast-engineering, shopify_dynamic_pdp_playbook_assimilated]
---

# Shopify Native Bundle & Save PDP Widgets

## When to Use
- Replacing third-party bundle apps (e.g., Kaching Bundles) with zero-app native Liquid/CSS/Vanilla JS "Bundle & Save" quantity-break widgets on Shopify Product Detail Pages (PDPs).
- Auditing or fixing tier-switching radio cards, multi-variant pair dropdowns, free-gift cart injection, or split-test `template.suffix` presets on Shopify themes.

## Core Implementation Workflow

### 1. Scoped Liquid & CSS Architecture
- Render the widget as a self-contained snippet (e.g., `snippets/bundle-save.liquid`) mounted inside `sections/main-product.liquid` via a theme block or snippet render tag.
- Scope all CSS variables and selectors to a unique root wrapper so multiple split-test templates can customize colors and badges without leaking styles.
- **Critical `[hidden]` CSS Rule**: Author stylesheets that set `display: flex` or `display: grid` on `.bundle-options` will override the browser's user-agent `[hidden] { display: none; }` rule, leaving all tiers' variant selectors visible simultaneously. Always include:
  ```css
  .bundle-options[hidden] {
    display: none !important;
  }
  ```

### 2. Mobile Touch Targets & Viewport Hygiene (375px / 390px / 768px / 1280px+)
- **Touch Target Minimums (`>= 44x44px`)**: Radio card headers (`.bundle-card__head`), custom color swatch dropdown triggers (`.mb-color-btn`), dropdown option rows (`.mb-color-opt`), native size `<select>` elements (`.mb-sel-size`), and "Size guide" trigger pills must all enforce `min-height: 44px` and `min-width: 44px` (WCAG AAA / Apple HIG). Do not rely on padding alone when mobile media queries shrink font sizes (`13px`) or button heights (`34px–38px`).
- **Zero Horizontal Overflow**: Verify across all 4 canonical breakpoints — `375px` (iPhone SE), `390px` (iPhone 15), `768px` (iPad Mini / Tablet), and `1280px+` (Desktop) — that `document.documentElement.scrollWidth <= window.innerWidth`. Tablet viewports (`768px`) frequently experience 2–5px horizontal overflow from flex/grid buy-box badges; enforce `overflow-x: hidden` on `html, body, main#MainContent` and `box-sizing: border-box` on all PDP section containers.

### 3. Dynamic Client-Side Asset Resolution (`asset_url` JSON Map Pattern)
- **Never Use Empty `asset_url` Base Strings**: In Shopify Liquid, `{{ '' | asset_url }}` or stripping a single asset's filename to concatenate dynamic image names in JavaScript fails in production because Shopify CDN appends per-file version hashes (`?v=...`) and fingerprinted paths. Furthermore, hardcoding a donor store's CDN (`//donor-store.com/cdn/shop/files/`) violates brand isolation and breaks when donor assets move.
- **Canonical Liquid Asset Map**: When client-side JS (such as a review grid `#cm-reviews`, modal viewer, or dynamic swatch switcher) needs to resolve local theme assets, generate a JSON lookup table in Liquid using `asset_url` for every file:
  ```liquid
  <script type="application/json" data-cm-rv-assets>
  {
    {%- for i in (1..48) -%}
      {%- assign num = i | prepend: '00' | slice: -2, 2 -%}
      {%- assign fname = 'monteau-rv-' | append: num | append: '.jpg' -%}
      {{ fname | json }}: {{ fname | asset_url | json }}{% unless forloop.last %},{% endunless %}
    {%- endfor -%}
  }
  </script>
  ```
- **Verify Non-Contiguous / Sparse Asset Indices**: Donor review/gallery payloads frequently reference sparse or non-contiguous indices beyond a sequential `(1..N)` range (e.g., `41, 49, 55, 60, 62, 66..86` alongside `01..48`). Never assume a single `(1..N)` loop covers all referenced files — extract every unique filename referenced in the JS array / blocks and cross-check 100% coverage against `[data-cm-rv-assets]` keys so no fallback raw path (`assets/filename.jpg`) produces a 404 on Shopify CDN.
- Parse `[data-cm-rv-assets]` once in JS and resolve every card/modal image directly from the map (`assetMap[filename]`), guaranteeing 100% `HTTP 200` on Shopify's CDN with zero external vendor traces.

### 4. PDP Structural & Donor Fidelity Pitfalls (Sliders, Media Containment, Size Guide & Hero Icons)
- **Close Slider Track `.cm-rail` Outside `{%- if / else / endif -%}` Before `.cm-railnav`**: When a horizontal flex/grid slider section supports both dynamic `section.blocks` (`{%- if has_slides -%}`) and a static fallback (`{%- else -%}`), NEVER place the closing `</div>` of `<div class="cm-rail">` inside the `{%- else -%}` branch. Doing so leaves `.cm-rail` unclosed when blocks are present, pulling `<div class="cm-railnav">` inside the horizontal flex container so navigation arrows hang to the right of cards on mobile instead of centering underneath the slider:
  ```liquid
  <div class="cm-rail" data-cm-rail>
    {%- if has_slides -%}
      {%- for block in section.blocks -%}...{%- endfor -%}
    {%- else -%}
      <!-- fallback cards -->
    {%- endif -%}
  </div>
  <div class="cm-railnav">...</div>
  ```
- **Zone / Pin Overlay Media Aspect Ratio (`object-fit: cover` vs `contain`)**: When an interactive hotspot/pin section (e.g., `.cm-zn__media` with percentage-positioned pins `top: 86%`, `left: 48%`) wraps a square image (`1100x1100` or `1254x1254`) inside a portrait container (`aspect-ratio: 4 / 5`), NEVER override the image with `object-fit: contain` or `max-height: min(72vh, ...)`. Using `contain` shrinks the rendered image box inside the `4 / 5` container, creating top/bottom letterbox gaps and shifting percentage-based pins off their anatomical targets (e.g., ankle pins floating below the shoes). Keep `.cm-zn__media { display: block; aspect-ratio: 4 / 5; width: 100%; overflow: hidden; }` and `.cm-zn__media img { width: 100%; height: 100%; object-fit: cover; object-position: center center; }` so container and `<img>` bounding boxes match 1:1.
- **Dawn `modal-dialog` Direct `.show()` Trigger for Size Guides & Hide Duplicate Native Openers**: In Dawn-based themes, custom "Size guide" buttons inside bundle widgets may fail if `modal-opener` lacks a `.sizing-chart` class or if the native button is hidden. Invoke the Dawn web component directly with a fallback:
  ```html
  onclick="event.preventDefault(); const m = document.querySelector('modal-dialog#PopupModal-sizing_chart') || document.querySelector('modal-dialog[id*=\'sizing\']'); if (m && typeof m.show === 'function') { m.show(); } else { document.querySelector('modal-opener[data-modal*=\'sizing\'] button, .sizing-chart__button')?.click(); }"
  ```
  Simultaneously, hide the theme's standalone `modal-opener.sizing-chart` block in `main-product` (`modal-opener.sizing-chart { display: none !important; }`) when the bundle widget renders its own size-guide pill or interactive "Find my size in 10 seconds" drawer, preventing duplicate size triggers in the buy box.
- **Sticky CTA `IntersectionObserver` Target Synchronization**: When replacing standard `product-form` or third-party bundle bars (`.kaching-bundles__bar`) with a custom native bundle root (`.monteau-bundle-root`, `.mb-atc-pill-btn`), prepend the custom bundle selectors to `TARGET_SELECTORS` in the sticky CTA section (`sections/*-sticky-cta.liquid`). Otherwise, the sticky bar won't hide while the user is actively viewing the buy box and won't smooth-scroll back to the bundle selector on mobile.
- **Hero Chips Above `H1` via JS Re-Parenting**: When a single snippet (`snippets/*-hero-highlights.liquid`) renders both top category/compression pills (`BEST SELLER`, `15–20 MMHG`) and below-title benefit bullets without modifying `sections/main-product.liquid` block order, place the chips in a dedicated `.mhh-chips--top` wrapper and synchronously `insertBefore` the `.product__title` node on load so the visual hierarchy matches the donor (`Chips -> H1 -> Bullets`) with zero layout shift.
- **Hero Price Anchor, Gold Star Rating & H1 Typography Lock**: When replicating high-converting DTC compression/shapewear PDPs, embed the gold star social proof row (`★★★★★ 4.8 · 100,000+ women <u>Reviews</u>`, star color `#C9A85C`) and the per-unit anchor price row (`<b>$22.47</b> <span>per pair</span> <em>SAVE 50%</em>`, pill `#6E1E3C`, white bold uppercase text, `border-radius: 4px`) directly inside the hero highlights snippet above the benefit bullets rather than relying on standalone theme price blocks. Lock `.product__title h1` to a clean geometric sans-serif (`Montserrat, -apple-system, sans-serif !important; font-weight: 700 !important; letter-spacing: -0.02em !important;`) so global serif heading variables (`--font-heading-family`) do not bleed into performance apparel PDPs.
- **Desktop Left-Column Vertical Gallery Thumbnails (`> 990px`)**: In Dawn-based themes (`sections/main-product.liquid` + `snippets/product-media-gallery.liquid`), setting `desktop_thumbnails_position: "left"` in the template JSON alone can fail if CSS or suffix defaults fall back to bottom horizontal strips. Explicitly enforce `desktop_thumbnails_position = 'left'` for the target `template.suffix` in `snippets/product-media-gallery.liquid` AND include a `@media screen and (min-width: 990px)` override on `.media-gallery--desktop-thumbnails-left` (`.product-media-slider { width: calc(100% - var(--desktop-vertical-thumbnails-width, 16%) - 1.2rem); margin-left: auto; }` and `.thumbnail-slider { position: absolute; top: 0; left: 0; bottom: 0; width: var(--desktop-vertical-thumbnails-width, 16%); flex-direction: column; }`).
- **Authentic Donor Benefit SVGs Over Generic Checkmarks**: In PDP hero highlight lists (`snippets/*-hero-highlights.liquid`), preserve the donor's domain-specific vector SVG icons (`22x22` viewBox `0 0 24 24`, e.g., `legs`, `smooth`, `lift`, `squat`) rather than substituting generic 16px checkmark ticks.

### 5. Split-Test `template.suffix` Preset Mapping & Dynamic Multi-Product Variant Resolution
- When a single snippet powers multiple A/B test product JSON templates (`product.<suffix>.json` inside the theme's templates directory), verify exact `template.suffix` strings (e.g., `sculpt-legging-default-ab`, `3d-weave-ab-oct17`, `sculpt-legging-default-1`).
- Avoid brittle exact-string checks against shortened names; match full suffix strings or use `template.suffix contains 'ab'` so 4-pack vs 3-pack tier quantities and gift banners render the intended number of pair `<select>` rows.
- **Dynamic `product.options_with_values` Pair Selector (Never Hardcode Flagship Options Across Catalog PDPs)**:
  - A bundle pair-selector snippet (`snippets/*-pair-selector.liquid`) reused across multiple products (e.g., Flagship Leggings V1, Leggings V2, Bra, Shorts, Arm Sleeves, Lipedema 3-option Leggings) MUST dynamically iterate over `product.options_with_values` rather than hardcoding the flagship product's color names (`Gray`, `Navy`) and size list (`S`–`7XL`).
  - **Spelling & Alias Mismatches**: Different catalog products frequently use different option strings in Shopify Admin (`"Blue"` vs `"Navy"`, `"Grey"` vs `"Gray"`, `"2XL"` vs `"XXL"`). If the dropdown hardcodes `data-value="Navy"` or `"Gray"` while `product.variants` has `option1: "Blue"` or `"Grey"`, client-side `resolveVariant(color, size)` fails to match and silently falls back to `product.selected_or_first_available_variant` (adding the wrong color/size to cart).
  - **Single-Option & 3-Option Products**: Products like Arm Sleeves may have only 1 option (`Color`, no `Size`), while specialized products (e.g., Lipedema Leggings) may have 3 options (`Color`, `Size`, `Style: Original / Pockets`). Render option selectors conditionally based on `product.options_with_values` and resolve all active option positions (`option1`, `option2`, `option3`).
- **Prevent Duplicate Size Finder Modals & Double Sticky ATC Bars on Catalog PDPs**:
  - When the bundle snippet already embeds the Size Finder trigger and modal (`{% render '*-size-finder' %}`), do NOT also enable a standalone `*_size_finder` block or legacy `custom_liquid` size-toggle block in `templates/product.*.json` — doing so duplicates `<h2>Find your size</h2>` and modal IDs in the DOM.
  - When a dedicated bottom section (`sections/*-sticky-cta.liquid`) is in the template's `"order"`, disable the legacy block-level `sticky_atc` inside `sections/main-product.liquid` so two floating ATC bars do not stack on scroll.
- **Dynamic "Ships By" Date Calculation**:
  - Never hardcode static calendar dates in bundle trust strips (e.g., `'Ships by <b>Oct 19</b>'`), which immediately go stale. Compute a rolling date in Liquid (`{{ 'now' | date: '%s' | plus: 86400 | date: '%b %d' }}`) with a Theme Customizer setting override, and clear any hardcoded date strings in `templates/product.*.json` block settings so the dynamic Liquid fallback takes effect.
- **PDP First-Fold & Single-H1 Hierarchy**:
  - Ensure `main` (`main-product`) precedes any secondary hero banners in `templates/product.*.json` `"order"` so the gallery and bundle buy-box remain above the fold, and demote secondary banner headings from `<h1>` to `<h2>`.
- **Storefront-Wide Foreign CDN & Scraped Tail Sanitization**:
  - Scan all `cdn.shopify.com/s/files/1/(\d{4}/\d{4}/\d{4})` patterns across `sections/`, `snippets/`, and `templates/` (including `templates/cart.json` and `templates/collection.*.json`) to eliminate donor or legacy base-theme CDN URLs, and strip any accidentally pasted raw storefront HTML (`<product-rerender>`, foreign `product-id` inputs) before `{% schema %}`.

### 6. Multi-Item + Free Gift `/cart/add.js` Submission
- Collect the selected `variant_id` from each visible pair `<select>` in the active tier.
- When a tier includes a free gift product/variant, append the gift item to the `/cart/add.js` `items` array with line item property `_free_gift: "true"`:
  ```javascript
  const items = selectedVariantIds.map((id) => ({ id: Number(id), quantity: 1 }));
  if (activeTierHasGift && giftVariantId) {
    items.push({
      id: Number(giftVariantId),
      quantity: 1,
      properties: { _free_gift: "true" }
    });
  }
  await fetch(window.Shopify.routes.root + "cart/add.js", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ items })
  });
  ```

### 7. Crisp Payment Badges & Main-Product Block Deconfliction
- Factor crisp vector payment SVG badges (Visa, Mastercard, Amex, Apple Pay, Google Pay, PayPal, Shop Pay) into a standalone reusable snippet (e.g. `snippets/*-payment-icons.liquid`).
- To prevent duplicate payment badge rows when a merchant configures a separate theme block in `sections/main-product.liquid`, guard the embedded render inside the bundle snippet:
  ```liquid
  {%- assign has_separate_payment_icons = section.blocks | where: 'type', 'monteau_payment_icons' -%}
  {%- if has_separate_payment_icons.size == 0 -%}
    {% render 'monteau-payment-icons' %}
  {%- endif -%}
  ```
- In unit/parity test suites, verify both the parent bundle snippet and the rendered child payment snippet to avoid false negatives when vector SVGs are decoupled.

### 8. Zero-App Dimensional / Custom-Cut Pricing (`0.01 m²` Unit Pattern & Cart Tamper Guard)
- **Fractional Quantity Workaround Without Shopify Plus**: Standard Shopify carts only accept integer `quantity` values (`variant.price * quantity`), which forces custom-cut products (carpets, fabrics, cables, flooring, custom print) to round up to whole units. To achieve centimeter-exact pricing without paid calculator apps:
  - Set the variant price to `0.01 m²` (or `0.01` linear unit) and flag the product with metafield `custom.preis_pro_001_qm = true`.
  - Convert customer centimeter dimensions (`width_cm * length_cm / 100`) into an exact integer unit count passed as `quantity` to `/cart/add.js`, while recording human-readable dimensions in line-item properties (`_laenge_cm`, `_breite_cm`, `_flaeche_m2`, `_form`).
  - Automatically compare the custom cut (`Raummaß`) against full roll widths (`Meterware`) across live variant prices and recommend the next wider roll if its lower per-m² rate reduces total order cost.
- **Server-Side Liquid & Email Quantity Anti-Tampering Guard**:
  - **Threat**: Buyers can use browser DevTools (`/cart/change.js`) to reduce `quantity` from `600` (`6.00 m²`) to `75` (`0.75 m²`) while leaving `properties["Dimensions"] = "200 x 300 cm"` intact.
  - **Defense**: In the cart template/snippet (`snippets/tp-cart-gruppe.liquid`) and order confirmation email, NEVER trust the display surface property (`_flaeche_m2`). Recompute the required integer units directly in Liquid from raw `_laenge_cm` and `_breite_cm` (handling rectangles, circles `πr²`, and ovals). If `item.quantity < expected_units`, physically disable the Checkout button in cart and render a tamper warning in order confirmation emails.

## Verification & QA Checklist
1. **JSON Template Syntax**: Validate all modified product JSON template files with `json.loads` to ensure valid JSON structure and section ordering.
2. **Zero Vendor Traces**: When migrating templates or snippets across brands/stores, run `git diff <base>..HEAD | grep -i "<old_vendor>"` to guarantee zero residual brand strings, hard-coded product handles, or foreign variant IDs.
3. **Headless Browser Tier Switching**: Programmatically click Tier 1, Tier 2, and Tier 3 cards across 375px, 390px, and 1280px viewports and assert that only the active tier's `.bundle-options` has `getComputedStyle(el).display !== 'none'` and renders the exact expected count of `<select>` dropdowns.
4. **Live Storefront `/cart/add.js` Probe**: Using a valid storefront session cookie jar, POST the multi-item + `_free_gift` payload to `/cart/add.js` and verify HTTP 200, automatic bundle discount application, and line-item property retention in `/cart.js`.
5. **10-Point DTC Bundle Parity Gate**: For pixel-perfect donor replication, enforce automated unit test assertions across the 10 canonical elements:
   - Upper Trust-strip (`Secure Checkout • 90-Day Guarantee • Tracked Shipping`)
   - Risk-free guarantee divider (`Try it risk-free — 90-day guarantee`)
   - Tier 2 (BOGO) pill badge (`#FFD84D`) & subtitle (`One to wear, one to wash.`)
   - Tier 3 Burgundy banner (`24-HOUR SPECIAL OFFER` `#6E1E3C`), active border, and `✓ FREE Shipping` row
   - 2-Column selectors (`COLOR, SIZE` header, row index `#N`, separate dropdowns)
   - Double Free Gifts Box (Header, subtitle, 2 gift items with `FREE` badges and local WebP assets)
   - Size guide pill button (`Find my size →`)
   - Main ATC button (Solid black `#000000`, 999px pill border-radius, `Add to cart`)
   - Decoupled payment icons (7 vector SVGs via child snippet)
   - Dynamic `Ships by` rolling date & `Shipping to` geo indicator.
