# --- DNK-MRH-HEADER ---
# mrh_id: "references/shopify_app_section_injection_and_theme_extensions.md"
# purpose: "Engineering Reference for Shopify App Section Injection: Theme App Extensions vs Direct Theme Asset API."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-10-09"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛍️ Shopify App Section Injection: Theme App Extensions vs Direct Asset API

This reference establishes the canonical architectural paradigms, operational contracts, and deterministic algorithms for Shopify applications adding sections, blocks, and embed widgets to merchant storefront themes.

---

## 🏛️ 1. Two Architectural Paradigms

```
                              ┌──────────────────────────────────────────────┐
                              │                 Shopify App                  │
                              └───────┬──────────────────────────────┬───────┘
                                      │                              │
                     [Track A: Official OS 2.0]       [Track B: Direct Injection]
                                      │                              │
                                      ▼                              ▼
                         Theme App Extensions (TAE)           Theme Asset API
                         (App Blocks / App Embeds)          (REST / GraphQL API)
                                      │                              │
                 ┌────────────────────┴──────────┐                   │
                 ▼                               ▼                   ▼
          App Block (Section)             App Embed Block     Physical files into theme:
          target: "section"               target: "body/head" • sections/app_*.liquid
                 │                               │            • blocks/app_*.liquid
                 ▼                               ▼            • assets/app_*.js/css
          Shopify CDN Hosted              Shopify CDN Hosted         │
                 │                               │                   ▼
                 └───────────────┬───────────────┘            Mutation of templates/*.json
                                 ▼                            (add key to sections & order)
                        Theme Customizer                             │
                    (admin.../themes/.../editor)                     ▼
                                 │                            Theme Git / Code Editor
                                 ▼                            (Code becomes native to theme)
                    Storefront Render Engine
```

---

## 📦 2. Track A: Theme App Extensions (TAE) — App Blocks (Shopify OS 2.0 Standard)

The standard required for public Shopify App Store approval. The app has **zero write access** to raw theme files (no `write_themes` scope needed).

### 2.1. File Structure & Configuration
```
my-app/
└── extensions/
    └── my-theme-extension/
        ├── shopify.extension.toml
        ├── blocks/
        │   └── custom_hero_section.liquid  # App Block (target: "section")
        ├── assets/
        │   ├── app-styles.css
        │   └── app-controller.js
        └── locales/
            └── en.default.json
```

### 2.2. App Block Schema Contract (`blocks/custom_hero_section.liquid`)
```liquid
{{ 'app-styles.css' | asset_url | stylesheet_tag }}

<div class="dnk-app-section" data-section-id="{{ section.id }}">
  <h2>{{ block.settings.heading }}</h2>
  <div class="dnk-content">{{ block.settings.description }}</div>
</div>

<script src="{{ 'app-controller.js' | asset_url }}" defer></script>

{% schema %}
{
  "name": "⚡ DNK Custom Section",
  "target": "section",
  "stylesheet": "app-styles.css",
  "javascript": "app-controller.js",
  "templates": ["index", "product", "page"],
  "settings": [
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Welcome to our store"
    },
    {
      "type": "richtext",
      "id": "description",
      "label": "Description"
    }
  ]
}
{% endschema %}
```

### 2.3. Deep-Link Theme Customizer Onboarding
Apps provide a direct onboarding link inside their dashboard to instantly open the theme customizer with the app block pre-staged:
```
https://admin.shopify.com/store/{shop}/themes/{theme_id}/editor?addAppBlockId={extension_id}/{block_id}&target=mainSection
```
- `{shop}`: Shop handle (e.g. `test01010126`).
- `{theme_id}`: Target theme ID.
- `{extension_id}`: UUID of the Theme App Extension registered in Shopify Partner Dashboard.
- `{block_id}`: Block filename without `.liquid` (e.g. `custom_hero_section`).
- `target`: `mainSection` or specific section ID.

### 2.4. Template JSON Persistence
When saved, Shopify updates `templates/*.json` referencing the app block via a canonical protocol URI:
```json
{
  "sections": {
    "apps": {
      "type": "apps",
      "blocks": {
        "dnk_hero_123": {
          "type": "shopify://apps/dnk-studio/blocks/custom_hero_section/a1b2c3d4-e5f6-7890",
          "settings": {
            "heading": "Summer Sale"
          }
        }
      },
      "block_order": ["dnk_hero_123"]
    }
  },
  "order": ["apps"]
}
```

---

## 🛠️ 3. Track B: Direct Theme Asset Injection (Section Store / Design Packs Model)

Used by section marketplaces, bespoke migration tools, and private apps. Code lives directly in the theme repository.

### 3.1. Required Scope & Credentials
- Requires `write_themes` OAuth scope or private Theme Access token (`shptka_...`).

### 3.2. REST Asset API Injection Flow
```
1. Query Themes List:
   GET /admin/api/2026-01/themes.json
   Target theme selected by role: 'main' (published) or development theme ID.

2. Verify Theme Blocks / OS 2.0 Compatibility:
   GET /admin/api/2026-01/themes/{theme_id}/assets.json?asset[key]=config/settings_schema.json
   Verify presence of JSON templates (e.g. templates/index.json).

3. Upload Section & Asset Files:
   PUT /admin/api/2026-01/themes/{theme_id}/assets.json
   Payload:
   {
     "asset": {
       "key": "sections/dnk_promo_banner.liquid",
       "value": "<Liquid + Schema + Presets source code>"
     }
   }

4. Upload Assets (CSS / JS):
   PUT /admin/api/2026-01/themes/{theme_id}/assets.json
   { "asset": { "key": "assets/dnk_promo.css", "value": "..." } }
```

### 3.3. Crucial Presets Invariant
In order for an injected section (`sections/dnk_promo_banner.liquid`) to appear in the Shopify Customizer "+ Add section" picker, the schema **MUST** contain a `presets` array:
```liquid
{% schema %}
{
  "name": "⚡ Promo Banner",
  "tag": "section",
  "settings": [ ... ],
  "presets": [
    {
      "name": "⚡ Promo Banner",
      "category": "Custom Sections"
    }
  ]
}
{% endschema %}
```
*Without `presets`, the section can only be included via hardcoded `{% section 'dnk_promo_banner' %}` and will remain invisible in the Theme Customizer GUI.*

---

## ⚡ 4. Comparison Matrix

| Vector | Theme App Extensions (TAE) | Direct Asset Injection (Asset API) |
| :--- | :--- | :--- |
| **App Store Review** | **100% Permitted & Recommended** | Requires strict review exception for `write_themes` |
| **Theme Code Cleanliness** | **Zero-Pollution**: Clean uninstall, files on CDN | High pollution risk if uninstall script is missing |
| **Merchant Code Customization** | Restricted to Customizer settings GUI | **Full Access** via "Edit code" in Shopify Admin |
| **Speed & Caching** | Managed by Shopify CDN | Native theme assets, cacheable with `asset_url` |
| **Theme Blocks 2.0 Compatibility** | Injected via `@app` blocks | Can define native `blocks/*.liquid` with `content_for 'blocks'` |
| **Trial Themes** | Fully functional in Customizer | **Blocked**: 403 Forbidden on unpurchased Theme Store themes |

---

## 💣 5. Implementation Landmines & Defenses

1. **Header Comments in `templates/*.json`**:
   Shopify auto-generates comments like `/* IMPORTANT: auto-generated */` at the top of JSON template files. Direct `json.loads()` will throw `JSONDecodeError`.
   *Defense*: Always slice string starting from the first `{`:
   ```python
   raw_json = content[content.find("{"):]
   data = json.loads(raw_json)
   ```
2. **Trial Theme API Write Lock**:
   Commercial Theme Store themes running in trial mode reject Asset API writes with `403 Forbidden` (`Theme cannot be modified while in trial`).
   *Defense*: Warn merchant or detect trial status before initiating batch asset uploads.
3. **Max Nesting Depth Invariant (<= 3)**:
   Sections containing nested blocks must not exceed `Section (1) -> Container Block (2) -> Leaf Block (3)`. Depth >= 4 causes Customizer UI thread lockups.
4. **CSS Isolation & Specificity**:
   All injected styles must be encapsulated with `.section-{{ section.id }}` or `[data-section-id="{{ section.id }}"]` to prevent cascading collisions with host theme styling rules.

---

## 🔬 6. Empirical Case Study: Design Packs vs Section Store Live Audit (Store `test01010126`)

Live audit comparing clean baseline `Tinker` against active app installations:

### 6.1. Design Packs (DP) Hybrid Theme Blocks v2 Mechanism
- **Physical Files Injected**:
  - `sections/design_pack_-_design_system.liquid`
  - 9 Theme Blocks in `blocks/_dpb_-_styleguide-*.liquid` (`buttons-custom`, `buttons-main`, `buttons-product`, `color-schemes`, `custom-css`, `headings`, `layout`, `media`, `text`).
- **Theme Mutation Footprint**:
  - **`templates/index.json` modified**: Added section `design_pack_design_system_VpMPcz` with all 9 blocks registered under `blocks` and `block_order`, and placed in `order`.
  - **`config/settings_data.json` modified**: Styleguide color and typography tokens updated.
- **Verdict**: True Theme Blocks v2 implementation, excellent centralized design token management, but mutates core templates and risks leaving orphan references upon app removal.

### 6.2. Section Store (SS) Standalone Sections (Track B)
- **Physical Files Injected**:
  - 5 standalone sections in `sections/ss-*.liquid` (`ss-faq-pro`, `ss-feature-54`, `ss-scrolling-features`, `ss-steps-pro`, `ss-testimonials-42`).
  - 1 dedicated landing template `templates/product.500-in-1-retro-games-pixboy.json`.
- **Theme Mutation Footprint**:
  - **0 common theme files modified**: Baseline `templates/index.json` and `config/settings_data.json` remained 100% byte-identical.
  - Dedicated landing template automatically chains sections into a conversion sequence:
    `main (product-information)` ➔ `ss-scrolling-features` ➔ `ss-feature-54` ➔ `ss-steps-pro` ➔ `ss-testimonials-42` ➔ `ss-faq-pro`.
- **Verdict**: Maximum safety and isolation; zero risk of theme breakage upon installation or deletion. Ideal for product landing page bundles and CRO funnels.

### 6.3. Section Store (SS) Hybrid Delivery Strategy: App Blocks vs Standalone Sections
Section Store does not use a single monolithic delivery method. Instead, it employs an **adaptive hybrid architecture**:
1. **Full-Width Standalone Sections (Track B - Asset API)**:
   - For page sections (FAQ, Testimonials, Hero, Steps, and standalone Tabs like `ss-tabs-3.liquid`), it injects native `sections/ss-*.liquid` files.
   - **Physical Code Availability**: These files (~40KB - 220KB) contain complete HTML markup, CSS stylesheet tags, JavaScript controllers, and Shopify OS 2.0 schemas (`{% schema %}`) with nested block definitions (`Heading`, `Text`, `Button`, `Image`, `Accordion`).
   - Running `shopify theme pull --store <store> --theme <theme_id> --path <target_dir>` downloads the full source code directly to disk, allowing offline customization, refactoring, and zero-dependency migration.
2. **In-Section Micro-Widgets / PDP Blocks (Track A - Theme App Extensions)**:
   - When merchants add component blocks intended to live *inside* an existing section (such as the **Tabs block** inside `product-information`), Section Store does **NOT** inject a physical `.liquid` file into `sections/` or `blocks/`.
   - Instead, it injects a Shopify CDN-hosted Theme App Extension block:
     ```json
     "section_store_block_tabs_beQrmJ": {
       "type": "shopify://apps/section-store/blocks/block-tabs/d7a2e423-ea88-4344-b866-6d0fb487c3dd",
       "settings": {
         "default_tab": "first",
         "tab_layout": "filled",
         "first_title": "Expert Review",
         "second_title": "Description",
         "third_title": "Delivery Info",
         "fourth_title": "Specifications",
         ...
       }
     }
     ```
   - **Template Integration**: The block is registered inside `templates/product.json` under `"sections" -> "main" -> "blocks"` and inserted into `block_order` directly between `buy_buttons` and `product_description`.
   - **Code Editing Strategy**: Because the App Block Liquid code is hosted remotely on Shopify's App CDN and cannot be pulled via `shopify theme pull`, developers who need full code-level control over tabs should install the standalone Section version (`ss-tabs-3.liquid`), which provides the exact physical Liquid/CSS/JS source on disk.
   - **Advantage**: Zero risk of breaking host section liquid code, automatic schema updates via Shopify's App Extension CDN, and native drag-and-drop support inside Shopify Theme Customizer.
