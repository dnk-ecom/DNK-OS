<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/theme_codex_protocol_and_zero_bundler_import_maps.md"
purpose: "Reference guide for Theme Codex Protocol (Two-Phase Schema Mutation) and Zero-Bundler Import Maps in Shopify OS 2.0."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🛡️ Theme Codex Protocol & Zero-Bundler Import Maps Playbook

## 1. Overview & Architectural Motivation
This reference establishes the execution standards distilled from modern modular Shopify OS 2.0 themes (including `kondasoft/ks-origin` and DNK Horizon Tinker). It formalizes:
1. **Theme Codex Protocol**: Deterministic two-phase ordering for modifying Liquid schemas and JSON templates.
2. **Zero-Bundler Import Maps**: Browser-native ES module resolution and non-render-blocking CSS loading without Vite or Webpack bundling overhead.
3. **Canonical Agent Instructions**: Reference template housed at `services/dnk_shopify/templates/AGENTS.shopify-theme.md`.

---

## 2. Theme Codex Protocol: Two-Phase Schema Mutation

### The Failure Mode
When AI agents or automated scripts modify both section `{% schema %}` and `templates/*.json` in a single combined patch, race conditions occur:
- If a template references a new setting or block type before the platform/compiler verifies the Liquid schema, the entire template is rejected or dropped with an HTTP 422 error ("Setting not found in schema").
- If a theme sync runs mid-edit, the Shopify Theme Editor drops invalid templates and falls back to a 404 page.

### The Two-Phase Solution
```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Schema Mutation (Atomic Liquid Update)        │
│ • Update sections/*.liquid or blocks/*.liquid          │
│ • Validate {% schema %} JSON structure & AST syntax     │
│ • Verify schema type limits (range step, limits)        │
└──────────────────────────┬─────────────────────────────┘
                           │ Verification Pass (Green)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Template Usage (JSON Template Mutation)       │
│ • Update templates/*.json or sections/*-group.json     │
│ • Reference only pre-verified blocks & settings         │
│ • Clean trailing commas & strip C-style comments       │
└────────────────────────────────────────────────────────┘
```

### Invariants for Liquid Schemas
1. **Property Ordering**:
   `name` ➔ `tag` ➔ `class` ➔ `settings` ➔ `blocks` ➔ `disabled_on` / `enabled_on` ➔ `presets`
2. **Settings Constraints**:
   - Keys must use `snake_case`.
   - Merchant-facing inputs should be in integer px and converted to `em` inside Liquid (`divided_by: 16.0`).
   - Use schema translation keys (`t:sections...`) for merchant labels.

---

## 3. Zero-Bundler Native ESM & Import Maps

### Native Browser Module Resolution
Avoid complex node bundlers for theme storefront runtime. Define dependencies via native import maps in `layout/theme.liquid`:

```html
<script type="importmap">
{
  "imports": {
    "theme/cart": "{{ 'cart-actions.js' | asset_url }}",
    "theme/events": "{{ 'view-events.js' | asset_url }}",
    "vendor/splide": "{{ 'splide.esm.js' | asset_url }}"
  }
}
</script>
```

### Non-Render-Blocking CSS Loading
Load non-critical, below-the-fold or route-specific stylesheets asynchronously:

```html
<link
  rel="stylesheet"
  href="{{ 'product-reviews.css' | asset_url }}"
  media="print"
  onload="this.media='all'"
>
<noscript>
  {{ 'product-reviews.css' | asset_url | stylesheet_tag }}
</noscript>
```

### Dynamic Alpha Compositing via Space-Separated RGB
Define color design tokens in `:root` as space-separated RGB triplets:

```css
:root {
  --color-surface: 255 255 255;
  --color-primary: 26 26 26;
  --color-accent: 53 213 213;
}

/* Enable dynamic alpha transparency without duplicate hex codes */
.card-glass {
  background-color: rgb(var(--color-surface) / 0.85);
  border: 1px solid rgb(var(--color-primary) / 0.12);
}
```

---

## 4. Agent Instructions Template
Whenever configuring AI subagents for theme modifications, seed their workspace or system context with:
`services/dnk_shopify/templates/AGENTS.shopify-theme.md`
This ensures agents strictly follow scoped edits, avoid unsolicited fallbacks, enforce two-phase schema updates, and preserve mobile-first CSS architecture.
