<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/shopify_theme_handbook_assimilated/references/shopify_theme_store_handbook_complete_architecture_guide.md"
# purpose: "Complete Modern Architectural Guide, Theme Store Requirements & Horizon Best Practices distilled from Shopify Theme Handbook (Saabbir)."
# author: "DNK-e.com Maksym & Gerych Prime"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-30"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# --- END DNK-MRH-HEADER ---
-->

# 🛍️ Modern Shopify Theme Store Architecture & Horizon Engineering Handbook

Distilled SOTA knowledge base from **Saabbir's Shopify Theme Handbook** (`https://saabbir.github.io/shopify-theme-handbook/`). Covers everything needed to scaffold, build, audit, and publish high-performance themes compliant with the official Shopify Theme Store standards and the modern Horizon (2025+) component architecture.

---

## 🏛️ 1. Architecture Paradigm: The Horizon Revolution (2025+)

Modern Shopify themes have evolved beyond the legacy Dawn monoliths. The modern best practice is **Horizon-style block-based architecture**:

### Key Architectural Differences

| Feature | Legacy / Early OS 2.0 (Dawn) | Modern Horizon (2025+) |
|---|---|---|
| **Blocks location** | Embedded inside `sections/*.liquid` schema | Standalone modular files in `/blocks/*.liquid` |
| **Nesting capability** | Flat (sections can only hold 1 level of blocks) | Nested (blocks inside blocks, up to 8 levels deep) |
| **Block targeting** | Any block anywhere | Explicit `@theme` (theme blocks) & `@app` (app blocks) targeting |
| **CSS Delivery** | Large monolithic `base.css` + `section-*.css` | `{% stylesheet %}` with automatic per-page subsetting |
| **JS Delivery** | Monolithic `global.js` asset script | `{% javascript %}` + lightweight scoped Custom Elements |
| **State Management** | Global window events or scattered data attributes | Custom Element encapsulation + DOM as SSOT |

### Nested Theme Blocks (`/blocks/*.liquid`)
In Horizon architecture, building blocks like buttons, text, badges, and media cards reside in the `blocks/` directory:
```
blocks/
  ├── button.liquid
  ├── heading.liquid
  ├── text.liquid
  ├── card.liquid
  └── group.liquid
```
In `sections/my-section.liquid` or `blocks/group.liquid`, you define supported blocks via schema:
```json
{
  "name": "t:sections.hero.name",
  "blocks": [
    { "type": "@theme" },
    { "type": "@app" }
  ]
}
```
`@theme` permits any theme block in `blocks/` that targets this section. `@app` allows third-party Shopify apps to inject app blocks seamlessly.

---

## 🎨 2. CSS Delivery Strategy & Automatic Subsetting

Shopify provides three distinct mechanisms for CSS. Choosing the wrong one introduces performance regressions or styling conflicts:

### The 3 CSS Mechanisms

| Mechanism | Location | Liquid Rendered? | Per-Page Subsetting? | Primary Use Case |
|---|---|---|---|---|
| `{% stylesheet %}` | Inside `.liquid` file | **NO** (pure CSS only) | **YES** (Only loaded on pages where the component appears) | Component-scoped CSS (sections, blocks, snippets) |
| `{% style %}` | Inside `.liquid` file | **YES** (evaluates `{{ ... }}`) | **NO** (always inlined where rendered) | Dynamic styles tied to merchant schema settings |
| Asset CSS (`assets/*.css`) | Independent file in `assets/` | **NO** (static asset) | **NO** (loaded globally via `layout/theme.liquid`) | Design tokens, resets, base typography, global layout grid |

### Best-Practice Pattern
1. **Global Tokens & Reset**: Define CSS custom properties (`--color-*`, `--space-*`, `--font-*`) in `assets/theme.css` or `assets/base.css`.
2. **Component CSS**: Write component rules inside `{% stylesheet %} ... {% endstylesheet %}` at the bottom of each section or block. Shopify automatically extracts and merges them into a single optimized stylesheet per page.
3. **Dynamic Customizer Overrides**: When a merchant chooses a specific background or margin setting, apply it via inline CSS variables:
   ```liquid
   <div class="hero" style="--hero-bg: {{ section.settings.bg_color }}; --hero-padding: {{ section.settings.padding }}px;">
   ```
   Avoid large `{% style %}` blocks containing repeated CSS rules.

---

## ⚡ 3. JavaScript: Scoped Web Components & Storefront Events

### `{% javascript %}` Tag vs Asset Scripts
- `{% javascript %}` tags are automatically concatenated and loaded deferred by Shopify only on pages that contain that component.
- Scope: Variables declared in `{% javascript %}` live in a shared module/script scope, so always encapsulate code within Custom Elements.

### Modern Web Component Standard (Autonomous Custom Elements)
All interactive components (`cart-drawer`, `product-form`, `variant-picker`, `accordion`, `modal`) must be built as Web Components:
```javascript
class CartDrawer extends HTMLElement {
  constructor() {
    super();
    this.drawer = null;
    this.closeButton = null;
  }

  connectedCallback() {
    this.drawer = this.querySelector('[data-drawer]');
    this.closeButton = this.querySelector('[data-close]');
    
    this.closeButton?.addEventListener('click', this.close.bind(this));
    
    // Listen for global cart update events
    document.addEventListener('cart:updated', this.onCartUpdated.bind(this));
    
    // Shopify Theme Customizer integration
    document.addEventListener('shopify:section:select', this.onSectionSelect.bind(this));
    document.addEventListener('shopify:block:select', this.onBlockSelect.bind(this));
  }

  disconnectedCallback() {
    this.closeButton?.removeEventListener('click', this.close.bind(this));
    document.removeEventListener('cart:updated', this.onCartUpdated.bind(this));
  }

  open() {
    this.setAttribute('open', '');
    document.body.classList.add('overflow-hidden');
  }

  close() {
    this.removeAttribute('open');
    document.body.classList.remove('overflow-hidden');
  }

  onSectionSelect(e) {
    if (e.target.contains(this) || this.contains(e.target)) {
      this.open();
    }
  }

  onBlockSelect(e) {
    if (e.target.dataset.shopifyEditorBlock?.includes('cart')) {
      this.open();
    }
  }
}

if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}
```

### Critical Theme Editor Lifecycle Events
When merchants edit their store in the Theme Customizer, Shopify does not always reload the whole page; it fires DOM events:
- `shopify:section:load`: A section re-rendered. Re-attach plugins, carousels, or dynamic observers.
- `shopify:section:unload`: A section was removed or is about to be replaced. Tear down intervals and listeners to prevent memory leaks.
- `shopify:section:select` / `shopify:section:deselect`: Merchant clicked the section in the sidebar. Auto-open drawers/tabs or scroll the section into view.
- `shopify:block:select` / `shopify:block:deselect`: Merchant clicked a specific block. Highlight or activate the matching slider slide, accordion item, or drawer.

---

## 📝 4. Schema & Settings: Strict Theme Store Rules

Shopify reviewers rigorously audit schema labels. Over 40% of first-time rejections stem from schema formatting violations:

### The Unbreakable Schema Rules

| Rule | ❌ Rejected | ✅ Approved |
|---|---|---|
| **Sentence Case** | `"Heading Size"`, `"Button Label"` | `"Heading size"`, `"Button label"` |
| **American English** | `"Colour scheme"`, `"Centre alignment"` | `"Color scheme"`, `"Center alignment"` |
| **No Questions** | `"Show share buttons?"`, `"Enable zoom?"` | `"Show share buttons"`, `"Enable image zoom"` |
| **No Ampersands** | `"Terms & conditions"`, `"Shipping & delivery"` | `"Terms and conditions"`, `"Shipping and delivery"` |
| **No Numbered Options** | `"1. Left"`, `"2. Center"`, `"3. Right"` | `"Left"`, `"Center"`, `"Right"` |
| **No Slang / Marketing CTA** | `"Supercharge your sales"`, `"Click here"` | `"Display badge"`, `"Secondary link"` |
| **Strict Translation Keys** | `"name": "Header"` (hardcoded string) | `"name": "t:sections.header.name"` |

### JSON Formatting Invariant
- **ZERO Comments**: Standard JSON strictly forbids `/* ... */` and `// ...` comments.
- Files in `locales/*.json`, `locales/*.schema.json`, `config/*.json`, and `templates/*.json` must strictly parse with `JSON.parse`. Any comment will crash the Shopify Cloud parser and brick the Theme Customizer.

---

## ♿ 5. Accessibility (WCAG 2.1 AA) & Performance Gates

### Review Gates (5 Stages)
1. **Stage 1: OS 2.0 Requirements & Required Templates**: 14 mandatory templates (`index`, `product`, `collection`, `list-collections`, `cart`, `blog`, `article`, `page`, `search`, `404`, `password`, `gift_card`, `customers/account`, `customers/order`, etc.). Support for Section Groups (`sections/header-group.json`, `sections/footer-group.json`).
2. **Stage 2: Lighthouse Audit**:
   - Mobile Performance score: $\ge 60$ (LCP $< 2.5s$, CLS $< 0.1$).
   - Accessibility score: $\ge 90$ across all core templates.
3. **Stage 3: Technical Integrity**:
   - Contrast ratio: minimum 4.5:1 for normal text, 3:1 for large text (18pt+) and UI icons/borders.
   - Visible `:focus-visible` ring on every interactive element.
   - No keyboard traps.
   - All images must include non-empty, descriptive `alt` attributes.
   - Screen-reader announcement (`aria-live="polite"`) for cart drawers, variant updates, and filter changes.
4. **Stage 4: Design & UX**:
   - Consistent layout grids, typography hierarchy, and spacing tokens.
   - Responsive across mobile ($320px+$), tablet ($768px+$), and desktop ($1440px+$).
   - No content clipping: Never apply `text-overflow: ellipsis` or fixed `height` that cuts off merchant product titles or descriptions.
5. **Stage 5: Merchant Documentation & Final Sign-Off**.

---

## 📦 6. Clean Packaging & Submission Invariant

Shopify rejects submissions containing extraneous repository files.

### The Canonical 8 Folders Whitelist
Only the following directories are permitted in the uploaded theme ZIP:
```
assets/
blocks/
config/
layout/
locales/
sections/
snippets/
templates/
listings/ (Optional: only if providing multiple preset overrides)
```

### Blacklisted From Theme Store ZIP
- Version Control: `.git/`, `.gitignore`
- Tooling & AI: `AGENTS.md`, `CLAUDE.md`, `.cursor/`, `.cursorrules`, `.mcp.json`, `.github/`
- Build Artifacts: `package.json`, `package-lock.json`, `node_modules/`, `vite.config.js`, `src/`
- OS Junk: `.DS_Store`, `Thumbs.db`
- Temp files: `*.tmp`, `*.bak`, `*.log`
