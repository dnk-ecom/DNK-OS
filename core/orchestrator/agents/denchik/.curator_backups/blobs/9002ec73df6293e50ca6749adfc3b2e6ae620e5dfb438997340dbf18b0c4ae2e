# 🛍️ Agentic Brand System (ABS) & Shopify Theme AST Integration

---
tags: [shopify, branding, tokens, ast, theme-blocks, cro, agentic-brand-system]
author: "DNK-e.com Maksym & Denchik"
date: "2026-10-29"
---

## 🎯 Architectural Principle: Brand as Machine-Readable Code (SSOT)

Static branding artifacts (PDF brand guidelines, unstructured Figma files, Notion notes) cause agentic code degradation ("mid/slop drift"). When autonomous agents generate new Shopify OS 2.0 theme sections or PDP blocks without rigid machine-readable boundaries, they default to generic styling and weak copy.

The **Agentic Brand System (ABS)** pattern binds the brand repository directly to the Shopify theme compilation pipeline:
1. `brand/visual/tokens.json` ➡️ automated compilation into `assets/brand-tokens.css` + `config/settings_data.json`.
2. `brand/verbal/vocabulary.md` & `cro-heuristics.md` ➡️ prompt injection for agentic copy and block generation.
3. `brand/art_direction/rules.md` ➡️ AST composition heuristics for Theme Blocks v2.
4. `brand/DECISIONS.md` ➡️ decision history preventing regressive style changes.

---

## 🧱 The 4 Layers of Store Brand Integration

### 1. Visual Design Tokens (`brand/visual/tokens.json`)
```json
{
  "$schema": "https://json.schemastore.org/design-tokens",
  "color": {
    "primary": { "value": "#112224" },
    "surface": { "value": "#162c2f" },
    "accent": { "value": "#35d5d5" },
    "text-main": { "value": "#d4d8db" },
    "border": { "value": "#224447" }
  },
  "radii": {
    "button": { "value": "9999px" },
    "card": { "value": "12px" }
  }
}
```
- Generated into CSS custom properties (`:root { --color-primary: #112224; --radius-button: 9999px; }`).
- Directly injected into Shopify theme presets in `config/settings_data.json`.

### 2. Verbal & CRO Layer (`brand/verbal/`)
- **Banned Words Filter**: "cheap", "buy now", "best quality", "100% guarantee", "discount".
- **Approved Terminology**: "investment in daily comfort", "limited release", "activate order", "clinical protocol".
- **PDP Hierarchy Rule**: Primary headline focuses on life transformation (Before vs After); technical specs go strictly into collapsible accordions.

### 3. Theme Blocks v2 Art Direction (`brand/art_direction/`)
- **Media Rules**: Product media aspect ratio strictly 4:5 or 1:1. Never mix aspect ratios within a single carousel.
- **CTA Rule**: Minimum tap target height 48px on mobile viewports.
- **Badge Rule**: Fixed top-left positioning on product cards with `var(--radius-badge)`.

---

## 🛡️ Theme Engineering Safeguards & Pitfalls

1. **Customizer Degradation Protection**:
   - In `config/settings_schema.json`, restrict color choices via `type: "select"` populated with curated brand palettes from `tokens.json`, instead of free-form `type: "color"` pickers.
2. **Theme App Extensions Sandboxing**:
   - Third-party app widgets (reviews, upsells) pollute theme CSS.
   - Wrap theme containers in scoped attributes: `[data-dnk-theme="v1"]`. Use scoped variables or reset rules for injected elements.
3. **JIT Brand Loci (Anti-Bloat Context Routing)**:
   - Do not pass the entire brand kit to coding agents.
   - For UI blocks: route only `tokens.json` (radii, colors, typography).
   - For copy/text: route only `vocabulary.md` + `cro-heuristics.md`.
4. **Deterministic Pre-Commit Brand Linter**:
   - Run AST/Regex checks on liquid templates before staging:
     - Disallow raw hex colors (e.g. `#fff`) without CSS variables.
     - Disallow banned vocabulary terms in default section schemas.
