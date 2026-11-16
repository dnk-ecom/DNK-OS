<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/shopify_theme_reverse_engineering_and_evolution_playbook.md"
purpose: "Playbook for reverse-engineering Shopify themes via CDN source maps and architectural comparison between theme generations."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-29"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🧬 Shopify Theme Reverse-Engineering & Evolution Playbook

## 1. Source Map Reverse-Engineering Pipeline (`.js.map` Extraction)

When acquiring or analyzing commercial themes (especially unpurchased trial themes omitted from `shopify theme pull` / Theme API), full original source code can be deterministically extracted from live demo stores on the Shopify CDN:

### A. Extraction Steps
1. **Identify Demo Store & Theme ID**:
   - Inspect network assets: `https://<demo-store>.myshopify.com/cdn/shop/t/<theme_id>/assets/<asset>.js`.
2. **Crawl Primary Surface Areas**:
   - Scan `/`, `/collections/all`, representative PDP (`/products/<handle>`), and `/cart` to collect all script references.
3. **Companion `.js.map` Retrieval**:
   - For every `.js` file, probe `https://<demo-store>.myshopify.com/cdn/shop/t/<theme_id>/assets/<name>.js.map`.
   - If present, parse JSON and extract `sources` and `sourcesContent`.
4. **Reconstruct Clean Unminified Source**:
   - Save the raw source files matching internal module paths (e.g. `src_unminified/`).
   - Yields 100% authentic TypeScript/ESNext source with private fields (`#field`), docstrings, and developer comments.
5. **Section Schema & HTML Extraction**:
   - Use Shopify Section Rendering API (`/?section_id=<section_name>`) to fetch isolated section markup.

---

## 2. Architectural Evolution Patterns: Modern Themes (Helix) vs Prior Gen (Tinker)

Modern Shopify OS 2.0 Web Component architectures show clear generational upgrades:

### A. Component Lifecycle & Memory Safety (`component.js`)
* **Prior Gen (Tinker)**: Relies on manual `removeEventListener` calls. During rapid Section Rendering API morphing, detached DOM elements frequently retain lingering event listeners, causing memory leaks.
* **Modern (Helix)**:
  - **Lazy `AbortController`**: Uses `get abortController()` passing `{ signal: this.abortController.signal }` to all listeners. Upon `disconnectedCallback()`, calling `this.#abortController?.abort()` cleanly severs all attached listeners in one atomic operation.
  - **Dynamic Ref Observation (`refsUpdatedCallback`)**: Emits lifecycle hook when DOM mutations occur inside the component, avoiding full teardown/rehydration.
  - **Soft Reinitialization (`reinitialize()`)**: Explicit method running `disconnectedCallback()` -> `connectedCallback()` for in-place re-evaluation without DOM replacement.

### B. Section Renderer & Predictive Prefetching (`section-renderer.js`)
* **Prior Gen**: Reacts only to `click` or `submit` events, introducing 150-400ms network delay.
* **Modern (Helix)**:
  - **LRU Cache with Hover Prefetching**: When cursor hovers over quick-add buttons, variant swatches, or filter facets, triggers `prefetch(url)`. On actual click, HTML is retrieved from in-memory cache in 0-5ms.
  - **Race Condition Guard (`#isClickFetching`)**: Prevents casual hover events from aborting or overtaking active user clicks.
  - **View Transitions API**: Wraps morphing in `document.startViewTransition()` for 60fps hardware-accelerated animations without bulky animation libraries.

### C. Core Web Vitals & Layout Shift Prevention (CLS)
* **CLS Bug in Prior Gen**: When opening cart drawer or modals with `overflow: hidden` on `<body>`, the browser scrollbar disappears, causing a jarring 15-17px horizontal layout shift on desktop.
* **Modern (Helix `critical.js`)**:
  - Dynamically calculates window vs document width and sets `--scrollbar-width: ${window.innerWidth - document.documentElement.clientWidth}px`.
  - Applies compensation padding to `<body>` and fixed headers on modal open, achieving 0 CLS.

### D. CSS Modularity (FCP/LCP Optimization)
* **Prior Gen**: Large monolithic stylesheet (`base.css` ~45-80KB) loaded on every page.
* **Modern (Helix)**: Section-scoped CSS bundles (16 isolated stylesheets, e.g. `product-information.css`, `collection.css`, `mobile-dock.css`) loaded conditionally only when the section is rendered.

### E. Zero-App Native Merchandising Modules
Modern theme engineering internalizes high-converting eCommerce features to eliminate slow 3rd-party apps:
1. `bundle-product-card.js` & `bundle.js`: Client-side product bundling with tiered discounts and single Cart API commit.
2. `scrolling-hotspots.js`: Interactive shoppable lookbooks synced with scroll via RAF / `IntersectionObserver`.
3. `product-finder.js`: Multi-step interactive quiz engine.
4. `cart-drawer.js` extending `DialogComponent`: Fully accessible drawer with `FreeShippingBar`, `cart-shipping.js` (live calculator), and `cart-share.js`.

---

## 3. Cross-Version AST Token-Alignment & Lexical Scope Identifier Recovery

When upgrading a Shopify theme across major/minor releases (e.g., `v1.3.2` -> `v1.9.0`) where an earlier release has clean human-readable local variable names (`eventName`, `callback`, `unsubscribe`, `cartItems`, `debouncedOnChange`, `parsedState`) while the newer release is minified or hex-mangled (`_0x...`) and introduces new Web Components:

### A. Why Direct File Substitution Fails
- **Missing New Web Components & Subsystem Hooks**: Newer theme releases frequently add new custom elements (e.g. `<shrine-subscription-widget>`, `<quantity-break-upsells>`), new `PUB_SUB_EVENTS` keys (`optionValueSelectionChange`, `cartError`), and gift/upsell state validators. Overwriting the newer `assets/main.js` with an older version's file breaks every new Theme Block 2.0 feature.
- **Unverified Legacy Code Paths**: Older reference bundles may still contain deprecated or unwanted remote telemetry hooks that were already cleaned in the target bundle.

### B. 4-Step AST Token-Alignment Pipeline ("Rosetta Stone" Method)
1. **Normalize Structural Formatting (`esbuild --format=esm`)**:
   - Format both the reference bundle (`v1.3.2/assets/main.js`) and the target bundle (`v1.9.0/assets/main.js`) through `esbuild` (without minification) so both files share identical indentation, bracket placement, and property access syntax.
2. **Token-Stream Sequence Alignment (`difflib.SequenceMatcher`)**:
   - Tokenize both files while normalizing non-keyword identifiers to a structural placeholder (`_ID_`).
   - Run `SequenceMatcher(None, ref_norm, tgt_norm, autojunk=False)` and map each mangled identifier in `equal` opcode blocks to the highest-frequency human identifier at the corresponding position in the reference token stream.
3. **Contextual Fallback Naming for New Version-Specific Code**:
   - For identifiers belonging to newly introduced classes/methods absent from the older reference version, assign semantic base names from their AST declaration context (`catch (e)` -> `error`, `addEventListener(..., (e) =>` -> `event`, `querySelectorAll` -> `elements`, `querySelector`/`closest` -> `element`, `JSON.parse` -> `parsedData`, `fetch` -> `response`, `FormData` -> `formData`).
4. **Innermost Lexical Brace-Span Scope Collision Guard & `node --check`**:
   - Compute the innermost enclosing `{ ... }` block (including the preceding `(...)` parameter list) covering all occurrences `[min_pos, max_pos]` of each identifier.
   - Ensure no two distinct identifiers whose lexical scopes overlap receive the same name (appending numeric suffixes `2`, `3` only when scopes overlap), and protect global function/class declarations (`subscribe`, `publish`, Web Component class names) from shadowing.
   - Restore module section headers (`// constants.js`, `// pubsub.js`, `// cart.js`, `// global.js`) and verify both `assets/main.js` and formatted `assets/secondary.js` with `node --check` before repacking the theme `.zip`.

