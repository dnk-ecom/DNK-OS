# --- DNK-MRH-HEADER ---
# mrh_id: "references/third_party_design_systems_and_theme_app_extensions_audit.md"
# purpose: "SOTA Audit & Isolation Protocol for Third-Party Design Systems & Theme App Extensions (Design Packs on Tinker OS 2.0)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-02"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🎨 Third-Party Design Systems & Theme App Extensions Audit Playbook

This reference establishes the canonical protocol for analyzing, auditing, and safely isolating third-party design systems and Theme App Extensions (App Embeds) within modern Shopify Online Store 2.0 themes (such as Tinker OS 2.0). Derived from the live production audit of **Design Packs** (`mcraft-top.myshopify.com`, Theme ID `190353637678`).

---

## 📌 1. Executive Summary: Zero-Pollution Architecture

Modern enterprise Shopify apps must comply with the **Zero-Pollution Standard**:
- **0 modifications to core theme templates**: `layout/theme.liquid`, `assets/`, `snippets/`, and core theme `sections/` MUST remain 100% untouched (`git diff` is empty).
- **Theme App Extension Isolation**: All injected runtime scripts and global stylesheets are hosted on CDN and injected dynamically by the Shopify platform via `{{ content_for_header }}`.
- **Self-Contained Theme Blocks**: All customizable visual primitives exist purely as discrete section files (`sections/*.liquid`) and nested theme blocks (`blocks/*.liquid`), using isolated private namespaces (`_dpb_-_*`).

---

## 🛠️ 2. Shopify CLI Multi-Binary & macOS Environment Scoping

When pulling themes for audit or deployment on macOS, conflicts between legacy global npm modules and Homebrew packages frequently cause silent or fatal failures:

### The Pitfall: `Permission denied @ apply2files - Gemfile.lock`
- **Root Cause**: An outdated `/usr/local/bin/shopify` (e.g. v3.52.0 installed via npm) invokes CLI-Ruby embedded inside root-owned `/usr/local/lib/node_modules/@shopify/cli-kit/assets/cli-ruby/` and fails when attempting to update `Gemfile.lock`.
- **Deterministic Fix**:
  1. Use Homebrew-installed CLI (`/opt/homebrew/bin/shopify` v3.80+).
  2. Set user-scoped Ruby environment:
     ```bash
     export GEM_HOME="$HOME/.gem"
     export PATH="/opt/homebrew/bin:$GEM_HOME/bin:$PATH"
     ```
  3. When running authentication (`shopify theme pull` or `shopify theme list`), execute in pseudo-terminal (PTY) to handle browser device codes (`https://shopify.com/admin/oauth/device_login`).

---

## 🧩 3. App Embed Registration Contract (`settings_data.json`)

Theme App Extensions do NOT edit `layout/theme.liquid`. Instead, they register an App Embed block inside `config/settings_data.json`:

```json
{
  "current": {
    "blocks": {
      "13416097264177121472": {
        "type": "shopify://apps/design-packs/blocks/design_packs/1efa8e58-6fa1-4c9a-9c0a-e71446c20785",
        "disabled": false,
        "settings": {}
      }
    }
  }
}
```

### Invariant Checks:
1. `type` starts with `shopify://apps/<app-handle>/blocks/<block-handle>/<uuid>`.
2. Enabling or disabling the embed in Theme Customizer only toggles `"disabled": false | true`.
3. If disabled, the Shopify platform completely omits the external script from `{{ content_for_header }}`.

---

## 🧱 4. Architecture of Third-Party Design Blocks (`_dpb_-_*` Namespace)

Third-party style systems structure design primitives into atomic, isolated blocks rather than giant monolithic sections:

| Component Role | Canonical File | Responsibilities |
| :--- | :--- | :--- |
| **Section Orchestrator** | `sections/design_pack_-_design_system.liquid` | Master container; manages `@theme` blocks (`{% content_for 'blocks' %}`), Drawer UI, and global CSS output. |
| **Typography Tokens** | `blocks/_dpb_-_styleguide-headings.liquid` | Defines Primary, Secondary, Eyebrow, Display, and h1–h6 font families, weights, letter-spacing, line-heights, and responsive sizes. |
| **Body & Paragraphs** | `blocks/_dpb_-_styleguide-text.liquid` | Configures body font, lead text, lists, quotes, and links. |
| **Main Buttons** | `blocks/_dpb_-_styleguide-buttons-main.liquid` | Primary & Secondary button states (fill, hover background, border-width, padding, border-radius, shadows). |
| **Custom CTA Slots** | `blocks/_dpb_-_styleguide-buttons-custom.liquid` | Up to 5 custom button classes for specialized campaigns. |
| **Commerce / Product Buttons** | `blocks/_dpb_-_styleguide-buttons-product.liquid` | Dedicated tokens for Add-to-Cart (ATC) and Quick Buy buttons. |
| **Layout & Grid Tokens** | `blocks/_dpb_-_styleguide-layout.liquid` | Max page width, responsive desktop/mobile gutter, grid columns. |
| **Media & Surfaces** | `blocks/_dpb_-_styleguide-media.liquid` | Image and video border radii, drop shadows, hover zoom transitions. |
| **Color Schemes** | `blocks/_dpb_-_styleguide-color-schemes.liquid` | Dynamic CSS custom property generation for background, surface, text, and accent colors. |

> **Naming Rule**: Prefixed blocks (`_dpb_-_*`) prevent theme editor clutter by preventing internal design-system primitives from appearing in general page-level "Add Block" pickers where they do not belong.

---

## ⚡ 5. Dual-Mode Rendering Lifecycle: Editor Drawer vs Storefront CSS

A critical SOTA pattern for third-party design guides is conditional execution based on `request.design_mode`:

### A. Theme Customizer Mode (`request.design_mode == true`):
- Renders an interactive sidebar / floating drawer UI.
- Generates live visual previews of all typography, color palettes, button variants, and spacing meters.
- Includes custom JS event listeners to reflect live setting tweaks without requiring full page reloads.

### B. Live Storefront Mode (`request.design_mode == false`):
- **DOM Elimination**: The entire Drawer HTML, preview widgets, and editor controls are excluded via Liquid conditional tags (`{% if request.design_mode %} ... {% endif %}`).
- **Headless Token Generation**: The section outputs **only** a minified `<style>` block containing generated CSS custom properties (variables) and targeted selectors.
- **Zero JS Overhead**: No client-side JavaScript is executed on the public storefront.

---

## 🛡️ 6. Anti-Collision CSS Scoping Protocol

To guarantee that the host theme's core styles (e.g. Tinker v4.2.0 components) are never accidentally corrupted or overwritten, the design system enforces strict selector scoping:

```liquid
{%- assign force_scope = '.dsgn-pck__section:not(.dsgn-pck__no_design_system)' -%}
```

### Specificity Invariants:
1. **Per-Section Scoping**: Rules are prefixed with `[data-section-id="{{ section.id }}"]` or `.dsgn-pck__section`.
2. **Selective Global Override**: Global overrides (e.g. applying design pack styles to native theme buttons) are ONLY enabled when the merchant explicitly checks `enable_overrides: true` and configures a targeted `custom_selector` in the block schema.
3. **No Unconditional `!important`**: Overrides avoid brute-force `!important` injections unless specifically requested via a dedicated toggle (`force_selectors_important: true`).

---

## 🔒 7. Liquid DRM & Licensing Interceptors

Third-party extensions frequently include graceful license verification checks:

```liquid
{%- unless shop.metafields['app--4742649'].design_packs_status contains 'active' or content_for_header contains 'design_packs_file.js' -%}
  {%- break -%}
{%- endunless -%}
```

- If the merchant uninstalls the app or disables the App Embed, the check fails.
- The Liquid template executes `{% break %}` (or `{%- render 'app-disabled-notice' -%}` in editor mode), preventing stale or unauthorized rendering without throwing fatal Liquid runtime exceptions.

---

## 🚀 8. Performance & Web Font Optimization

- **Font Loading Anti-Pattern**: Injecting raw `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` tags causes render-blocking FOIT (Flash of Invisible Text).
- **SOTA Standard**: Leverage Shopify's native Font API with `font_display: 'swap'`:
  ```liquid
  {%- assign heading_font = block.settings.heading_font -%}
  <style>
    {{ heading_font | font_face: font_display: 'swap' }}
  </style>
  ```
- **Payload Footprint**: Storing 900+ configuration parameters across 8 blocks in `templates/index.json` results in an inline stylesheet of ~12–18 KB uncompressed (~3–4 KB gzip), preserving <1.5s LCP on mobile.

---

## 🔄 9. Deterministic Zero-Residue Rollback Playbook

When retiring or rolling back a third-party design system, execute the following 4-step sequence to guarantee 100% bitwise parity with the baseline theme:

1. **Disable App Embed**:
   In Theme Customizer, toggle off the App Embed, or delete the app block from `config/settings_data.json`.
2. **Remove Section from Template**:
   Remove the design system section key from `templates/index.json` under `sections` and remove its ID from `order`.
3. **Delete Injected Files**:
   ```bash
   rm sections/design_pack_-_design_system.liquid
   rm blocks/_dpb_-_styleguide-*.liquid
   ```
4. **Verify Bitwise Zero-Diff**:
   ```bash
   git diff --stat
   # Verify 0 files changed against pre-install commit
   ```

---

## ⚖️ 10. Architectural Comparison: Native Tinker OS 2.0 vs Design Packs System

| Architectural Vector | Native Tinker v4.2.0 (Dawn Primitives) | Design Packs Design System (Section/Blocks) |
| :--- | :--- | :--- |
| **Mounting & Orchestration** | Global: `config/settings_schema.json` ➔ `snippets/theme-styles-variables.liquid` ➔ `layout/theme.liquid` | Section-level: `sections/design_pack_-_design_system.liquid` hosting 9 atomic Theme Blocks (`@theme`) |
| **Storage & Persistence** | `config/settings_data.json` (store-wide single state) | Template JSON (e.g. `templates/index.json`) per page |
| **Token Granularity** | **Compact / Optimized (~40–60 tokens)**: 4 typography scales, global palette (5 colors), 3 container widths | **Ultra-Detailed (~950+ parameters)**: Per-tag headings (h1-h6, display, eyebrow), up to 5 custom button classes, ATC tokens |
| **CSS Scope & Specificity** | Strictly global (`:root { ... }`), applies across entire storefront | Hybrid: Isolated to `.dsgn-pck__section` by default; optional targeted overrides (`custom_selector`) |
| **Theme Customizer UX** | Standard Shopify sidebar settings tabs (blind configuration) | **Live Interactive Style Guide Drawer**: In-canvas sliding drawer previewing all tokens, buttons, and typography |
| **Storefront CSS Delivery** | Static/cached stylesheet (`assets/base.css`) or minimal `:root` block in `<head>` | Dynamic `<style>` generated on the fly inside page body; DOM stripped via `{% if request.design_mode %}` |
| **Template Weight Impact** | 0 lines added to template JSON | +1,114 lines in `templates/index.json` |

---

## 🏗️ 11. The DNK OS Hybrid Blueprint: Zero-Overhead Live Visual Design System

When building proprietary design systems for DNK OS, combine the visual UX of Design Packs with the high-performance pipeline of Tinker:
1. **Interactive Style Guide Drawer in Editor**: Implement the sliding drawer in the Customizer (`request.design_mode == true`) for live visual feedback across buttons, text hierarchy, and color swatches.
2. **Compile to Native `:root` Variables**: Instead of outputting 950+ scoped CSS selectors inline into the HTML body, map the drawer's tokens directly to native Tinker CSS custom properties (`--font-heading-family`, `--color-background`, `--button-border-radius`).
3. **Autonomous DRM-Free Isolation**: Remove external licensing script dependencies (`design_packs_file.js` / DRM conditionals) so the design system operates 100% offline and standalone without vendor lock-in.
4. **Preserve 100/100 PageSpeed**: Keep HTML body clean of inline CSS bloat; maintain browser HTTP cacheability of stylesheets.
