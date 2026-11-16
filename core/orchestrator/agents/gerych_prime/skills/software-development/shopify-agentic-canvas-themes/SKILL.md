---
name: shopify-agentic-canvas-themes
description: Use when building themes for Shopify Canvas and Sidekick.
category: software-development
version: "1.0.0"
author: "DNK-e.com Maksym & Gerych Prime"
license: "MIT"
metadata:
  hermes:
    tags: ["shopify", "canvas", "skeleton-theme", "sidekick", "agentic-commerce", "partial-rendering", "theme-blocks"]
    related_skills: ["shopify_theme_handbook_assimilated", "shopify-theme-ast-engineering"]
---

# 🎨 Shopify Canvas & Agentic Theme Architecture Skill

## When to Use
- Designing, developing, converting, or auditing themes for the **Shopify Canvas** standard (Early Access).
- Developing block-first architectures conforming to **Shopify Skeleton Theme** (`Shopify/skeleton-theme`).
- Implementing `{% block %}`, LiquidDoc `{% doc %}`, or `@shopify/partial-rendering`.
- Enabling autonomous AI coding agents (Sidekick, Claude Code, Gerych Swarm) to manipulate themes without breaking layout.

---

## 🏛️ 1. Architecture Paradigm: OS 2.0 vs. Agentic Canvas

| Feature | OS 2.0 (Dawn) | Agentic Canvas (Skeleton) |
|---|---|---|
| **Primary Building Unit** | Sections (`sections/*.liquid`) | Blocks (`blocks/*.liquid`) |
| **Templates** | JSON (`templates/*.json`) | Direct Liquid (`templates/*.liquid`) |
| **Composition Tag** | `{% section %}` / `{% content_for 'blocks' %}` | `{% block 'name', param: val %}` + `{{ content }}` |
| **Editor Interface** | 1D Left-Sidebar Section Tree | 2D Spatial Infinite Canvas (all templates side-by-side) |
| **AI Integration** | None | Sidekick (Global prompt + Block-level contextual chat) |
| **DOM Reactivity** | Full reload or Section Rendering API | `{% partial 'name' %}` + `@shopify/partial-rendering` |
| **Asset Location** | `{% stylesheet %}` / `{% javascript %}` allowed | Banned in Liquid; 100% centralized in `assets/` |

---

## 🚫 2. Skeleton Non-Negotiables

1. **No `sections/` directory**: Do not create or reference sections.
2. **No JSON templates**: All pages are direct Liquid composition roots (`templates/*.liquid`).
3. **No schema `presets`**: Block schemas contain only `name` and `settings`.
4. **No embedded styles or scripts**: Never use `{% stylesheet %}` or `{% javascript %}` inside Liquid.
5. **No hardcoded paths**: Always use `routes.*` (`routes.cart_url`, `routes.search_url`).
6. **Strict Theme Check**: Maintain `.theme-check.yml` with `extends: theme-check:recommended` with zero overrides.

---

## 🧱 3. The `{% block %}` Tag & Composition Pattern

Page structure flows top-down:
`layout/theme.liquid` → `<main>` → `templates/*.liquid` → `{% block 'container' %}` → child blocks.

```liquid
{% comment %} templates/index.liquid {% endcomment %}
{% block 'container' %}
  {% block 'hello-world' %}
    {% block 'liquid-tips', tips: ['hello_world.liquid_tips_1', 'hello_world.liquid_tips_2'] %}{% endblock %}
  {% endblock %}
{% endblock %}
```

### Parameter Binding Rules:
1. Named arguments passed to `{% block %}` are exposed as local variables inside the block.
2. If an argument name matches an `id` in the block's `{% schema %}`, it also sets `block.settings.<id>`.
3. Arguments without a schema match remain plain local variables.
4. Inline literal arrays are fully supported: `tips: ['key1', 'key2']`.
5. Child body content is rendered inside the block via `{{ content }}`.
6. The root element must retain `{{ block.shopify_attributes }}` for Canvas inspector interaction.

---

## 📝 4. LiquidDoc (`{% doc %}`) Contract for AI Agents

Every block MUST begin with typed LiquidDoc annotations:
```liquid
{% doc %}
  Renders a container with custom HTML tag and alignment.

  @param {string} [tag] - HTML element wrapper (default: 'section').
  @param {string} content - Required caller-supplied body content.

  @example
  {% block 'container', tag: 'div' %}
    {{ page.content }}
  {% endblock %}
{% enddoc %}
```

---

## ⚡ 5. Partial Rendering Workflow

1. **Liquid region declaration**:
   ```liquid
   {% partial 'cart-items' %}
     <div class="cart-content">...</div>
   {% endpartial %}
   ```
2. **JavaScript trigger**:
   ```javascript
   import { partials } from "@shopify/partial-rendering";

   await partials.refresh("cart-items");
   ```
3. **Behavior**: Preserves focus, selection, form inputs, and scroll position. Requires `shop.features.agentic_editor_enabled?`.

---

## 📚 6. Open Design, Theme Blocks 2.0 & Canvas Transpiler Reference
- See `references/open_design_ast_sidecar_and_theme_transpiler.md` for dual-track Open Design AST sidecar patterns, CSS module tokens, and Next.js memory allocation recipes.
- See `references/dnk_ecom_v2_multi_donor_synthesis_and_github_sync.md` for the `DNK-Ecom v2.0` 3-Tier Molecular Donor Lab (`services/dnk_shopify/DNK-e.com` / `https://github.com/DNKShopify/DNK-e.com`), DEC-018 pure theme branch & scoped SemVer tag standard (`<theme-slug>` branches: `ascendify`, `casaio`, `dnk-ecom-sections`, `ella`, `ks-origin`, `shrine-pro`, `story`, `tinker`, `donor-lab`, `sections-vault`, while keeping `main` and `staging` 100% empty [`0 files`] until core donor selection; every release = atomic commit + annotated scoped tag `<theme-slug>-vX.Y.Z` + `theme_version` bump in `config/settings_schema.json`), the `./scripts/shopify/deconstruct_donors.py` CLI for `search`/`inspect`/`extract`, the 4-level `Sections DNK` deduplication pipeline (`./scripts/shopify/dedup_sections_dnk.py`), RFC 8259 JSON comment-stripping pitfalls, 100% Ukrainian (`uk.json` + `uk.schema.json`) Horizon localization parity, Shopify GitHub App `.shopifyignore` root hygiene, and `DNKShopify` PAT policy workarounds.
- See `references/theme_blocks_2_0_patterns_and_donor_matrix.md` for the Shopify Theme Store Blocks 2.0 (`Horizon` / `/blocks/*.liquid`) donor matrix (`Bricks v2.2.0`, `Helix v1.2.1`, `Seventh v4.0.0`, `Unicorn v5.0.0`, `Prompt`), comparison of Universal `Group` flex/grid composition vs. Three-Tier `Sections -> Cards -> Blocks` guardrails, the 4 hard Liquid context/snippet/loop limitations of `{% content_for 'blocks' %}`, and macOS Chrome accessibility (`osascript` + `System Events`) inspection recipes for live Shopify Theme Editor sidebars.
- See `references/craftile_shopify_customizer_bridge_and_fidelity_rendering.md` for the Craftile Editor bidirectional JSON bridge, `@craftile/types` schema typing rules (`meta` wrapping), asset & `base.css` injection into `StaticBlocksRenderer`, dynamic JavaScript Proxy section renderers, and high-fidelity Shopify Customizer simulation without wireframe placeholders.
- See `references/cinematic_cro_scrollcraft_and_cart_bridge.md` for Cinematic CRO Sections (ScrollCraft + Cart Bridge), 5-plane exploded hero, horizontal bundle rail, rAF idle snooze, ResizeObserver reflow caching, iOS Safari OOM guards, and Theme Editor lifecycle integration.

