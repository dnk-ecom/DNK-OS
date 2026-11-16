# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/ai_template_builder_validation_and_patching_patterns.md"
# purpose: "Reference patterns for AI Shopify theme builder: referential integrity validation, Liquid raw wrapping, and scoped DOM patching."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-10"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🛡️ AI Shopify Template Builder: AST Validation & Delta Patching Patterns

Condensed architecture patterns distilled from SOTA AI theme builder implementations (e.g. `rrs301/ai-shopify-template-builder`):

---

## 1. Pre-Export Referential Integrity Validation Gate
Before packing any synthesized Shopify OS 2.0 theme into a ZIP release, run strict multi-point integrity checks:

1. **Path-Traversal Barrier**: Verify all file paths inside the archive do not contain directory traversal tokens (`..`, leading `/`, backslashes `\`).
2. **Template-to-Section Referential Integrity**:
   - Parse all `templates/*.json` (e.g. `index.json`, `product.json`, `collection.json`, `cart.json`).
   - Iterate over `order` and `sections` objects.
   - For every entry `sections[section_id].type`, assert that `sections/${type}.liquid` physically exists in the theme bundle.
   - If a section reference is dangling or missing, fail the export immediately with an explicit error rather than allowing Shopify cloud ingestion to silently discard the template or crash.
3. **Mandatory OS 2.0 Schema Gate**:
   - Every file under `sections/*.liquid` must include a valid `{% schema %}{...}{% endschema %}` JSON block.
   - Validate that the schema contains at minimum a `"name"` and a valid `"presets"` array (with at least one preset) so merchants can insert and customize the section in Shopify Theme Customizer.
4. **Mandatory Boilerplate Invariant**:
   - Ensure the theme bundle contains all required Shopify root files: `layout/theme.liquid`, `config/settings_schema.json`, `config/settings_data.json`, `locales/en.default.json`, `templates/404.json`, and `templates/gift_card.json`.

---

## 2. Liquid Raw Wrapping for Model Output Ingestion
LLM-generated marketing copy, pricing tables, or promotional banners frequently emit characters that collide with Shopify Liquid syntax (`{{ ... }}` or `{% ... %}`).
- **Failure Mode**: When Shopify compiles a section containing unescaped double braces from raw AI output, it throws an unresolved variable or filter error.
- **Architectural Solution**: Wrap untrusted model-generated text or HTML slices containing dynamic symbols in Liquid raw tags:
  ```liquid
  {% raw %}
    <!-- Model-generated HTML with potential curly braces -->
    <p>Exclusive 20% discount applied: {{DISCOUNT_CODE}}</p>
  {% endraw %}
  ```
- Keep dynamic Liquid variables (e.g. `{{ section.settings.heading }}`) OUTSIDE the `{% raw %}` blocks.

---

## 3. Scoped Delta Patching (Client & Server Protocol)
To maintain zero-waste context and prevent regeneration rot, avoid full-page re-synthesis during conversational tweaks:

1. **Deterministic Element Tagging**:
   - AI generates HTML elements tagged with deterministic attributes:
     - `data-builder-section-id="<slug>"` on section containers.
     - `data-builder-element-id="<slug>"` on key editable nodes (headings, buttons, cards).
2. **Standard Delta Operations Contract**:
   ```typescript
   export type PatchOperation =
     | { op: 'replace_inner'; targetId: string; html: string }
     | { op: 'replace_outer'; targetId: string; html: string }
     | { op: 'set_attribute'; targetId: string; name: string; value: string }
     | { op: 'set_text'; targetId: string; text: string }
     | { op: 'set_classes'; targetId: string; classes: string };
   ```
3. **Server-Side Sanitization**:
   - Sanitize all incoming `PatchOperation` payloads: strip `<script>` tags, inline event handlers (`onclick`, `onerror`), and unsafe URI protocols (`javascript:`, `data:text/html`).
4. **Targeted DOM Application**:
   - In the browser/canvas engine, apply patches via `querySelector('[data-builder-element-id="..."]')` or `DOMParser`. Sibling DOM subtrees and section states remain completely untouched.

---

## 4. Two-Phase Token-First Theme Synthesis
Prevent stylistic dissonance across distinct pages (e.g. home page vs product page):
- **Phase 1: Global Theme Spec**:
  - LLM synthesizes a single global stylesheet defining CSS custom properties on `:root` (`--brand`, `--accent`, `--surface`, `--ink`, `--font-heading`) and reusable component classes (`.site-header`, `.btn-primary`, `.brand-logo`).
- **Phase 2: Page-Level Generation**:
  - Pass the concise `styleGuide` summary to subsequent page prompts. The LLM reuses established classes and design tokens instead of inventing conflicting utility palettes.
