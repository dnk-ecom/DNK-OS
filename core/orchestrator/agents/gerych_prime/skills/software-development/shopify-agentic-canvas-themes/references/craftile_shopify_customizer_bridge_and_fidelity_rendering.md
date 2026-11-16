# 🎨 Craftile Editor <-> Shopify OS 2.0 Theme Customizer Integration & High-Fidelity Rendering

This reference documents the architecture and techniques for running Craftile Editor as a full-fidelity visual editor for Shopify OS 2.0 themes (e.g. `staging` Theme Blocks 2.0 chassis).

---

## 🏗️ 1. Architecture: Bidirectional Template & Schema Synchronization

### Schema Extraction (`sync_theme_to_craftile.py`)
- Scans `sections/*.liquid` and `blocks/*.liquid`.
- Extracts `{% schema %}` JSON blocks using regex.
- Resolves localization keys (`t:names.*`, `t:settings.*`) against `locales/en.default.schema.json` and `locales/uk.schema.json`.
- Maps Shopify setting types to Craftile `PropertyDefinition`:
  - `range` -> `control: 'number'`
  - `select` -> `control: 'select'` (with options translated)
  - `color` / `color_background` -> `control: 'color'`
  - `checkbox` -> `control: 'boolean'`
  - `text` / `textarea` / `inline_richtext` -> `control: 'text'`
- **TypeScript Interface Safety**: Shopify-specific schema fields (e.g., `target: "section"`, `presets`) MUST be nested under `meta: { ... }` so they do not violate Craftile's strict `@craftile/types` `BlockSchema` definition.

### Lossless JSON Roundtrip
- Converts `templates/*.json` (`sections`, `order`, nested `blocks`) into a Craftile `Page` object (`blocks: Record<string, Block>`, `regions: Region[]`).
- Preserves template metadata (`name`, `wrapper`) and section-level root settings so that exporting back to Shopify produces a valid, runnable JSON template with 0 AST corruption.

---

## 🖼️ 2. High-Fidelity Preview Rendering (Shopify Customizer Parity)

### Asset & CSS Bundle Injection
- Copy or symlink theme assets (`staging/assets/*` including `base.css`) into the playground's public assets folder (`public/theme-assets/`).
- Register the theme stylesheet in `StaticBlocksRenderer`:
  ```typescript
  StaticBlocksRenderer({
    styles: ['/theme-assets/base.css'],
    blockRenderers: shopifyBlockRenderers,
    scripts: ['https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4'],
  })
  ```

### Dynamic Proxy Block & Section Renderers
Instead of hardcoding 135+ individual renderers or rendering generic wireframe boxes, use a dynamic JavaScript `Proxy` with curated templates for primary e-commerce sections:
1. **`section_hero`**: Dark gradient banner, responsive heading typography, badge, and CTA button container.
2. **`section_product_list`**: 4-column responsive grid with product cards, images, prices, and hover animations.
3. **`section_media_with_content`**: Split 2-column editorial showcase layout.
4. **`block_group`**: Flex/grid container with direction, gap, and child marker slots:
   ```html
   <!--BEGIN children: ${id}-->
   ${children}
   <!--END children: ${id}-->
   ```
5. **Proxy Fallback**: For any unmatched `section_*` or `block_*`, automatically wrap children in an styled container with Shopify section/block badges to guarantee 100% test and render coverage without runtime exceptions.

---

## ⚡ 3. Avoiding Stale Demo Traps
- When integrating Craftile into real workspaces, disable or override standard generic demo action buttons (`createComplexDemoPage()`).
- Bind header actions directly to real theme templates (`editor.engine.replacePage(shopifyInitialPage)`).
- Ensure the editor boots directly into the live Shopify theme template by default rather than a blank or generic dummy canvas.
