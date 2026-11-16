---
name: shopify_theme_handbook_assimilated
description: SOTA Shopify Theme Store & Horizon block architecture patterns from Saabbir handbook.
category: software-development
version: "2.0.0"
author: "DNK-e.com Maksym & Gerych Prime"
license: "MIT"
metadata:
  hermes:
    tags: ["shopify", "horizon", "theme-store", "theme-blocks", "web-components", "customizer", "accessibility"]
    related_skills: ["shopify-theme-ast-engineering", "sota-repository-assimilation"]
---

# 🛍️ Modern Shopify Theme Store & Horizon Architecture Skill

Distilled and verified architecture guidelines from **Saabbir's Shopify Theme Handbook** (`https://saabbir.github.io/shopify-theme-handbook/`).
For detailed specifications, see `references/shopify_theme_store_handbook_complete_architecture_guide.md`.

## When to Use
Use when developing, auditing, or refactoring Shopify themes for the official Shopify Theme Store or modern custom merchant builds. Covers Horizon-style nested theme blocks (`blocks/`), Web Components, Theme Customizer lifecycle events, strict schema validation, WCAG 2.1 AA accessibility, CSS subsetting, and zero-defect submission packaging.

---

## 🏛️ 1. Architecture: Horizon Nested Blocks (`/blocks/*.liquid`)

1. **Modular Block Decomposition**:
   - Move atomic UI components (button, heading, badge, price, media, accordion) from monolithic sections into `/blocks/*.liquid`.
   - Sections become structural layout containers that accept nested blocks via schema:
     ```json
     {
       "name": "t:sections.hero.name",
       "blocks": [
         { "type": "@theme" },
         { "type": "@app" }
       ]
     }
     ```
2. **Nesting up to 8 Levels**:
   - Horizon allows containers/groups to hold child blocks. In Liquid, loop through child blocks via:
     ```liquid
     {% for block in section.blocks %}
       {% render block %}
     {% endfor %}
     ```
3. **App Blocks (`@app`)**:
   - Always include `{ "type": "@app" }` in product, collection, and article sections to allow third-party app injection without liquid hacks.

---

## 🎨 2. CSS Delivery & Dynamic Variables

1. **Component CSS (`{% stylesheet %}`)**:
   - Place static, non-Liquid component CSS inside `{% stylesheet %} ... {% endstylesheet %}` at the bottom of the section or block.
   - Shopify extracts, deduplicates, and subsets this CSS automatically per page.
2. **Dynamic Schema Overrides**:
   - Use CSS custom properties attached to the element style attribute:
     ```liquid
     <div class="banner" style="--banner-bg: {{ section.settings.bg }};">
     ```
   - Avoid massive `{% style %}` blocks that duplicate static CSS.
3. **Global Tokens**:
   - Centralize colors, font stacks, and layout spacing in `assets/base.css` or `assets/theme.css`.

---

## ⚡ 3. JavaScript: Custom Elements & Editor Lifecycle

1. **Encapsulated Custom Elements**:
   - All interactive UI (cart drawer, product form, quick view, tabs) must extend `HTMLElement`.
   - Never attach naked global listeners in `assets/global.js` that fail to clean up.
2. **Theme Customizer Event Integration**:
   Always listen to editor events in `connectedCallback`:
   - `shopify:section:load`: Re-initialize carousels and observers.
   - `shopify:section:unload`: Destroy observers and event listeners.
   - `shopify:section:select` / `shopify:block:select`: Open modals/drawers or scroll element into viewport.
3. **DOM as Single Source of Truth**:
   - Read attributes directly from the DOM (`this.dataset.variantId`) instead of storing parallel state in JS memory.

---

## 📝 4. Schema & Settings: Theme Store Quality Standards

1. **Strict Sentence Case**: Only capitalize the first letter and proper nouns (`Color scheme`, `Heading size`).
2. **American English**: Always use American spelling (`Color`, `Center`, `Catalog`).
3. **Forbidden in Labels**:
   - No questions (`Show banner`, NEVER `Show banner?`).
   - No ampersands (`Terms and conditions`, NEVER `Terms & conditions`).
   - No numbered options (`Left`, `Right`, NEVER `1. Left`, `2. Right`).
   - No marketing slang or hype copy.
4. **Localization Keys (`t:`)**:
   - All schema names, labels, and info fields must use translation keys referencing `locales/en.default.schema.json`.
5. **Strict JSON Invariant**:
   - **ZERO C-style comments (`/* ... */` or `// ...`)** in any `.json` file (`locales/`, `config/`, `templates/`). Shopify Cloud parser will throw `SyntaxError` and break the Customizer.

---

## ♿ 5. Accessibility (WCAG 2.1 AA) & Performance Invariants

1. **Lighthouse Targets**:
   - Mobile Performance: $\ge 60$ (LCP $< 2.5s$, CLS $< 0.1$).
   - Accessibility Score: $\ge 90$ across all 14 required templates.
2. **Contrast & Keyboard Focus**:
   - Minimum 4.5:1 text contrast ratio (3:1 for large text / graphical objects).
   - Clear `:focus-visible` focus rings (2px solid outline) with adequate contrast.
3. **No Content Clipping**:
   - Never truncate product titles or descriptions with fixed-height overflow hidden. Let layouts expand naturally.

---

## 📦 6. Packaging & Submission Invariant

1. **Permitted Folders (Canonical 8 + Listings)**:
   `assets/`, `blocks/`, `config/`, `layout/`, `locales/`, `sections/`, `snippets/`, `templates/` (and optional `listings/`).
2. **Strict Exclusions**:
   Never package `.git/`, `.github/`, `AGENTS.md`, `CLAUDE.md`, `.cursor/`, `node_modules/`, `package.json`, `.DS_Store`, or build toolchains in the submission ZIP.
