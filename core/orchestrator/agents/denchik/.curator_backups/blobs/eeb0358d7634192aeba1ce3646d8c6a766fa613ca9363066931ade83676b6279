# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/cart_drawer_modular_block_migration_playbook.md"
# purpose: "Playbook for decomposing monolithic cart-drawer.liquid snippets into modular Shopify OS 2.0 theme blocks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-23"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# 🛒 Modular Cart Drawer Block Migration Playbook (Shopify OS 2.0 / Shrine Pro 1.9.0)

## Overview
Vintage/Sections 1.0 Shopify themes often house all slide-out cart logic in a single monolithic file (`snippets/cart-drawer.liquid` or `sections/cart-drawer.liquid`, 50–100KB+), containing hardcoded timers, shipping threshold bars, line items, urgency badges, upsell blocks, subtotals, checkout CTAs, and payment trust badges.

Modern Shopify OS 2.0 themes (e.g. Shrine Pro 1.9.0, Dawn, Horizon Tinker) split the cart drawer into modular, reorderable Theme Blocks:
- `sections/cart-drawer.liquid` (Drawer container, overlay, close button `✕`, main layout grids)
- `blocks/cart-drawer_body.liquid` & `blocks/cart-drawer_footer.liquid` (Block container zones with `{% content_for 'blocks' %}`)
- `blocks/cart-drawer_items.liquid` (Line items loop, product options, line item properties, stock urgency notices)
- `blocks/cart_product-upsells.liquid` & `snippets/upsell-block.liquid` (In-cart cross-sells, countdown timer, dashed borders)
- `blocks/cart_subtotals.liquid` (Savings calculation, shipping line status, subtotal display)
- `blocks/cart_checkout-btn.liquid` (Checkout CTA button, custom text, security lock icon, sticky footer behavior)
- `blocks/cart_payment-badges.liquid` (Payment processor SVG icons)

---

## 1. Cart Drawer Structural Components & Invariants

### 1.1 Close Button Styling (`sections/cart-drawer.liquid`)
- **Vintage Pattern:** Minimal transparent square with plain `✕` icon.
- **OS 2.0 Pitfall:** Base themes often apply default button classes (`header__icon--menu header__icon--summary link focus-inset flex-center`) resulting in unwanted gray rectangular backgrounds (`#f7f7f7`, `#ebebeb`).
- **Fix:** Ensure `.cart-drawer .drawer__close` supports explicit schema settings for `close_btn_bg_color` (`transparent`), `close_btn_x_color` (`#000000`), and `close_btn_size` (`24px`–`26px`) without inheriting default header button backgrounds.

```liquid
<button
  class="drawer__close"
  type="button"
  onclick="this.closest('cart-drawer').close()"
  aria-label="{{ 'accessibility.close' | t }}"
>
  <svg class="x-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <line x1="6" y1="6" x2="18" y2="18"></line>
    <line x1="18" y1="6" x2="6" y2="18"></line>
  </svg>
</button>
```

---

### 1.2 Line Items & Stock Urgency Indicator (`blocks/cart-drawer_items.liquid`)
- **Urgency Badge:** Pulsing low-stock dot and notice (e.g., `<p>Only a few left</p>`).
- **Styles:**
```css
.sfrom_text {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: {{ block.settings.dot_textsize }}px;
  color: {{ block.settings.dot_textcolor }};
  margin-top: 4px;
}
.sfrom_text::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: {{ block.settings.dot_color | default: '#fd8935' }};
  animation: pulse-dot 1.5s infinite ease-in-out;
}
@keyframes pulse-dot {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}
```
- **Line Item Properties:** Ensure custom properties (`His Name`, `Her Name`, `His Birthstone`, etc.) loop without hardcoded property filters:
```liquid
{%- for property in item.properties -%}
  {%- assign property_first_char = property.first | slice: 0 -%}
  {%- if property.last != blank and property_first_char != '_' -%}
    <div class="product-option">
      <dt>{{ property.first }}: </dt>
      <dd>
        {%- if property.last contains '/uploads/' -%}
          <a href="{{ property.last }}" class="link" target="_blank">{{ property.last | split: '/' | last }}</a>
        {%- else -%}
          {{ property.last }}
        {%- endif -%}
      </dd>
    </div>
  {%- endif -%}
{%- endfor -%}
```

---

### 1.3 Subtotals, Order-Independent Savings & Floating Drawer (`blocks/cart_subtotals.liquid` / `snippets/cart-drawer.liquid`)
- **Order-Independent `total_compare_price` & `display_compare2` Calculation**:
  - In monolithic `snippets/cart-drawer.liquid` (Ascendify 2.10.0, DNK_Ecom_sections 1.0.0) and modular `blocks/cart_subtotals.liquid` (Shrine Pro 1.9.0), never rely on `total_compare_price` being initialized in an earlier `cart_items` block, and never reset `{% assign total_compare_price = 0 %}` inside `{% if block.settings.display_subtotal %}` with a partial loop that only checks `item.variant.compare_at_price`.
  - Always compute `total_compare_price` and `display_compare2` autonomously at the top of `{% when 'subtotals' %}` (covering both `item.variant.compare_at_price > item.final_price` and automatic/line-level discounts where `item.original_line_price > item.final_line_price`, falling back to `item.original_line_price` when undiscounted):
```liquid
{%- assign total_compare_price = 0 -%}
{%- assign display_compare2 = false -%}
{%- for item in cart.items -%}
  {%- assign has_item_compare = false -%}
  {%- assign item_compare_line = item.original_line_price -%}
  {%- if item.variant.compare_at_price > item.final_price -%}
    {%- assign has_item_compare = true -%}
    {%- assign item_compare_line = item.variant.compare_at_price | times: item.quantity -%}
  {%- elsif item.original_line_price > item.final_line_price -%}
    {%- assign has_item_compare = true -%}
    {%- assign item_compare_line = item.original_line_price -%}
  {%- endif -%}
  {%- if has_item_compare -%}
    {%- assign display_compare2 = true -%}
    {%- assign total_compare_price = total_compare_price | plus: item_compare_line -%}
  {%- else -%}
    {%- assign total_compare_price = total_compare_price | plus: item.original_line_price -%}
  {%- endif -%}
{%- endfor -%}
```
- **`additional_text` Duplication Guard (`DNK_Ecom_sections 1.0.0`)**:
  - Verify that `{% if block.settings.additional_text != blank %}` outputs `{{ block.settings.additional_text }}` rather than accidentally duplicating `subtotal_left_text` and `subtotal_right_text`.
- **Floating Cart Drawer Off-Screen Geometry (`settings.enablefloatingcartdrawer`)**:
  - When `.drawer__inner.spacingouter` uses `right: 10px;`, base `transform: translateX(100%)` leaves 10px of the closed drawer protruding into the viewport. Always pair `spacingouter` with:
```css
.drawer__inner.spacingouter {
  transform: translateX(calc(100% + 20px));
}
.drawer.active .drawer__inner.spacingouter {
  transform: translateX(0);
}
```
- **DOM Re-Render & Scroll Preservation (`CartItems.updateQuantity` & `fixParsedHtml`)**:
  - Ensure all coupled DRM poison-pills (`if (!this.lineItemContainer) return;` in `CartItems.updateQuantity`, `updateCart`, and `initShareLinks`) are removed from `assets/main.js` / `assets/global.js`.
  - Preserve `.cart-drawer__body` scroll position (`cd.cartBodyScroll = oldBody.scrollTop`) inside `fixParsedHtml(oldHtml, parsedHTML)` and restore it after `sectionEl.innerHTML` replacement in `CartItems.updateQuantity`, `updateCart`, and `clearCart`.
- **Shipping Status & Total Calculation:** Insert conditional `Shipping: FREE` line above or below the Subtotal row based on `block.settings.position` and `block.settings.display_shipping`, with bold accent font size (`20px`) for final payable total.

---

### 1.4 Checkout CTA with Security Lock (`blocks/cart_checkout-btn.liquid`)
- **Lock SVG Icon:** Render inline SVG lock icon before the CTA text when `block.settings.checkout_lock` is enabled.
```liquid
{% if block.settings.checkout_lock %}
  <svg class="cart__lock-icon" width="13" height="15" viewBox="0 0 13 15" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fill-rule="evenodd" clip-rule="evenodd" d="M3.75 3.5C3.75 2.11929 4.86929 1 6.25 1C7.63071 1 8.75 2.11929 8.75 3.5V5.5H3.75V3.5ZM2.25 5.5V3.5C2.25 1.29086 4.04086 -0.5 6.25 -0.5C8.45914 -0.5 10.25 1.29086 10.25 3.5V5.5H11C11.8284 5.5 12.5 6.17157 12.5 7V13C12.5 13.8284 11.8284 14.5 11 14.5H1.5C0.671573 14.5 0 13.8284 0 13V7C0 6.17157 0.671573 5.5 1.5 5.5H2.25Z" fill="currentColor"/>
  </svg>
{% endif %}
<span>{{ block.settings.cart_custom_label | default: 'Checkout' }}</span>
```

---

## 2. Synchronization Checklist
1. Extract custom schema settings from source theme's `config/settings_data.json` under `cart-drawer`.
2. Ensure each block schema in `blocks/` declares matching setting IDs (`enable_lowstock`, `dot_color`, `checkout_lock`, `display_shipping`).
3. Deploy modified liquid blocks and `settings_data.json` simultaneously via Shopify Theme Access API (`PUT /assets.json`).
4. Validate both empty cart and multi-item cart states in storefront preview.

---

## 3. Shopify Theme Editor & Customizer Integration Invariants

### 3.1 Inspector Interception & `event.defaultPrevented` Trap
- **The Pitfall**: In Shopify Theme Customizer, the editor default mode is "Inspect" (`Shopify.designMode === true`). The editor iframe scripts intercept clicks on visual elements, firing `event.preventDefault()` so that links do not navigate away while the sidebar focuses the clicked component.
- **The Bug**: If `cart-drawer.js` checks `if (event.defaultPrevented) return;`, clicking on `[data-cart-open]` or the header cart button in customizer will be blocked, making it impossible for the merchant to open the drawer in the editor preview.
- **The Fix**: In the click listener, check for editor mode before returning on `defaultPrevented`:
```javascript
const trigger = event.target.closest('[data-cart-open]');
const isEditor = Boolean(window.Shopify && window.Shopify.designMode);
if (!trigger || (!isEditor && event.defaultPrevented) || event.metaKey || event.ctrlKey || event.shiftKey) return;
event.preventDefault();
this.open(trigger);
```

### 3.2 Header Block Select Auto-Close Collision
- **The Pitfall**: In Shopify customizer, clicking on the cart icon in the header selects the `_header-cart` block and fires `shopify:block:select`. If the drawer has an `onEditorBlock` listener:
```javascript
onEditorBlock(event) {
  if (!this.contains(event.target)) {
    this.close();
    return;
  }
  this.open();
}
```
Because `_header-cart` lives inside `sections/header.liquid` (outside the `<cart-drawer>` container), `this.contains(event.target)` evaluates to `false`, immediately slamming the drawer shut.
- **The Fix**: Explicitly check if the selected block or element is a cart trigger or `_header-cart`:
```javascript
onEditorBlock(event) {
  if (event.target.matches('[data-cart-open], [data-cart-drawer-trigger], .header__icon--cart, [data-block-id*="header-cart"]')) {
    this.open();
    return;
  }
  if (!this.contains(event.target)) {
    this.close({ restoreFocus: false });
    return;
  }
  this.open();
}
```

### 3.3 Static Section vs Section Group Sidebar Visibility
- **The Pitfall**: When `cart-drawer.liquid` is statically rendered in `layout/theme.liquid` via `{% section 'cart-drawer' %}`, Shopify OS 2.0 does NOT display it in the left-hand sidebar navigation of the Theme Editor. Merchants cannot find the section or configure its settings unless they click an element that triggers it.
- **Best Practice Solution**:
  1. Teach merchants to switch from "Inspect" mode to "Live Preview / View" mode (`Cmd+Shift+I`) to interact with slide-out drawers freely.
  2. Or migrate `cart-drawer` into a modern OS 2.0 Section Group (e.g. `sections/overlay-group.json` or `sections/aside-group.json`), which renders natively in the Customizer sidebar tree.

---

## 4. Vintage Sections 2.0 (`DNK_Ecom_v1_0_0`) ➔ Agent-First Skeleton Theme Decomposition Matrix

Legacy high-converting themes (such as `DNK_Ecom_v1_0_0`, housing 105 sections and 167 snippets) pack conversion boosters into complex, interdependent Liquid snippets. When porting to Agent-First Skeleton Theme / Theme Blocks v2, decompose these monolithic snippets into isolated Web Components and Theme Blocks:

| Legacy Snippet (`DNK_Ecom_v1_0_0`) | Agent-First Architecture | Role & Implementation Contract |
| :--- | :--- | :--- |
| `snippets/cart-drawer.liquid` | `<dnk-cart-drawer>` Web Component | Custom element encapsulating open/close state, trap focus, and DOM hydration. Renders layout slots via `{{ content }}`. |
| `snippets/cart-progress-bar.liquid`<br>`snippets/cart-checkpoints-bar.liquid` | `blocks/cart-progress.liquid` | Tiered free shipping / discount progress bar. Calculates `cart.total_price` against threshold and updates dynamically via `@shopify/partial-rendering`. |
| `snippets/cart-gift.liquid` | `blocks/cart-gift.liquid` | Auto-adds / displays free promotional gift product when subtotal passes threshold tier. |
| `snippets/cart-fomo-block.liquid` | `blocks/cart-timer.liquid` | Reserved cart countdown timer stored in `sessionStorage` with localized expiration alert. |
| `snippets/upsell-block.liquid` | `blocks/cart-upsell.liquid` | 1-click in-cart upsell card using `routes.cart_add_url` without triggering a full page navigation. |
| `snippets/cart-item.liquid` | `<dnk-cart-item>` Web Component | Atomic line-item row handling quantity increment/decrement/removal via Ajax Cart API. |


