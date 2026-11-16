# Shopify Canvas & Skeleton Theme Reference Specification

## 1. Shopify Canvas Interface & Navigation
- **Location**: Shopify Admin -> Online Store -> Themes -> Canvas (Early Access).
- **Spatial 2D Canvas**: All store templates (Home, Product, Cart, Pages, etc.) are rendered side-by-side on an infinite zoomable/pannable canvas.
- **Sidekick AI Assistant**:
  - Global theme chat bar at bottom for high-level styling and full-theme layout modifications.
  - Contextual block prompt when a specific block is selected, allowing localized generation and logic tweaks.
- **Visual Editing**: Direct text edits within preview, real-time responsive testing across breakpoints.
- **Compatibility**: Requires Shopify official or agentic custom themes following the block-first skeleton standard.

## 2. Skeleton Theme Architecture Invariants
- `sections/` directory is completely omitted.
- `templates/*.liquid` files act as direct composition roots.
- All building units reside in `blocks/*.liquid`.
- All CSS/JS assets reside in `assets/`.
- No embedded `{% stylesheet %}` or `{% javascript %}` tags in Liquid.

## 3. Block Tag & Parameter Rules
- `{% block 'name', param: val %}...{% endblock %}`
- Arguments matching `{% schema %}` keys set `block.settings.<id>`.
- Other arguments are local variables within the block scope.
- `{{ content }}` yields the caller-supplied inner markup.
- `{{ block.shopify_attributes }}` must be present on the block wrapper node.

## 4. Partial Rendering via `@shopify/partial-rendering`
- `{% partial 'name' %}...{% endpartial %}` declares a morph-target region.
- Client calls `partials.refresh('name')` or `partials.apply(await partials.fetch(...))`.
- Automatically preserves form values, focus, and viewport scroll position.
