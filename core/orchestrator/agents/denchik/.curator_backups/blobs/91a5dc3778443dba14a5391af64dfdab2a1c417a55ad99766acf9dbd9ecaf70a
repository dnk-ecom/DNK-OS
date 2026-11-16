<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/agentic_commerce_storefront_events_and_theme_blocks.md"
purpose: "Reference guide for Agentic Commerce, Storefront Events/Actions, and Theme Blocks (assimilated from KS Origin)."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym & Gerych"
--- END DNK-MRH-HEADER -->

# 🤖 Agentic Commerce, Storefront Events & Native Theme Blocks Architecture

Derived and assimilated from high-performance benchmark theme architectures (such as `kondasoft/ks-origin`).

---

## 1. Zero-Bundler Import Maps & Standard Events

Rather than forcing heavy runtime bundlers (Vite/Webpack) for storefront analytics, modern Shopify themes utilize native browser ES module import maps.

### Liquid Integration (`snippets/theme-head.liquid`):
```liquid
<script type="importmap">
  { 
    "imports": { 
      "@shopify/standard-events": "https://cdn.shopify.com/storefront/standard-events.js" 
    } 
  }
</script>
<script src="{{ 'storefront-actions.js' | asset_url }}"></script>
<script src="{{ 'storefront-events.js' | asset_url }}" type="module"></script>
```

### Event Tracking Dispatcher (`assets/storefront-events.js`):
```javascript
import { 
  ready, 
  pageView, 
  productView, 
  collectionView, 
  cartView, 
  searchSubmitted, 
  productAddedToCart 
} from '@shopify/standard-events';

ready().then(() => {
  // Dispatches to native standard events pipeline
  document.addEventListener('cart:item-added', (e) => {
    productAddedToCart(e.detail.cart, e.detail.item);
  });
});
```

---

## 2. Agentic Storefront Actions Contract

Exposes clean programmatic actions for autonomous shopping agents, AI search bots, and client scripts via `window.Shopify.actions`:

```javascript
window.Shopify = window.Shopify || {};
window.Shopify.actions = {
  getCart: async () => {
    const res = await fetch('/cart.js');
    return await res.json();
  },
  updateCart: async (updates) => {
    const res = await fetch('/cart/update.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates })
    });
    return await res.json();
  },
  openCart: () => {
    document.querySelector('cart-drawer')?.open();
  }
};
```

---

## 3. `<s-view-event>` & Liquid Standard Event Filter

For automated view telemetry on product cards, collections, and search results:

```liquid
<s-view-event data-event="{{ product | standard_event_data: 'view' }}">
  <!-- Product Card Content -->
</s-view-event>
```

In custom web components (`components.js`):
```javascript
class SViewEvent extends HTMLElement {
  connectedCallback() {
    const data = this.dataset.event;
    if (!data) return;
    try {
      const payload = JSON.parse(data);
      // Emit view event to Storefront standard-events
      document.dispatchEvent(new CustomEvent('shopify:view-event', { detail: payload }));
    } catch (e) {
      console.error('Invalid event JSON', e);
    }
  }
}
customElements.define('s-view-event', SViewEvent);
```

---

## 4. Native Theme Blocks (Horizon / OS 2.0+)

### Structure:
- `blocks/*.liquid`: Reusable components (e.g. `blocks/product-card.liquid`, `blocks/quantity-input.liquid`).
- Private helper blocks: prefixed with underscore (e.g. `blocks/_product-card-form.liquid`).
- `{% doc %}`: In-file documentation comments recognized by Shopify Theme Check and AI agents.

### Parent Context Passing:
```liquid
{% content_for 'blocks', closest.product: product %}
```

---

## 5. LLM Agent Coding Invariants for Shopify Themes (`AGENTS.md`)

When an autonomous AI agent develops or refactors Shopify themes:
1. **Two-Phase Schema Mutations**:
   - First modify `.liquid` sections/blocks schemas.
   - Run theme check or allow live reload to register schemas before touching `templates/*.json`. If a JSON template references a section setting before the schema is updated, Shopify CLI will reject the template.
2. **Schema Key Order**:
   - Strictly follow: `name` → `tag` → `class` → `settings` → `blocks` → `disabled_on`/`enabled_on` → `presets`.
3. **No Selector Grouping in CSS**:
   - Keep classes isolated. Avoid grouping selectors with commas when rules might diverge across breakpoints.
4. **Mobile-First Dynamic EM Scaling**:
   - In Liquid settings for font sizes and spacing, calculate relative `em` values dynamically:
     ```liquid
     font-size: {{ block.settings.font_size | divided_by: 16.0 }}em;
     ```
