# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_theme_store_theme_blocks_v2_catalog_audit.md"
# purpose: "Deterministic Shopify Theme Store scanning methodology (sitemap + Turbo-Stream changelog extraction) and the verified 3-Tier Theme Blocks 2.0 catalog registry."
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-19"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🔎 Shopify Theme Store Audit & Theme Blocks 2.0 Catalog Registry

## 1. Deterministic Theme Store Discovery & Changelog Scraping Protocol

Because `https://themes.shopify.com/themes` does not expose a native sidebar filter checkbox for `blocks/` or Theme Blocks 2.0 (see Shopify Community #579008), auditing the catalog requires a deterministic 3-step extraction pipeline rather than manual UI pagination:

### Step 1: Canonical Sitemap Extraction (`sitemap_theme_en.xml`)
- **Endpoint**: `https://themes.shopify.com/sitemap_theme_en.xml`
- **Important Header Pitfall (`HTTP 406 Not Acceptable`)**: Sending custom `Accept: text/vnd.turbo-stream.html` headers to `.xml` sitemap endpoints causes Shopify's router to reject the request with `HTTP 406 Not Acceptable`. Always request sitemaps with a standard browser `User-Agent` and default `Accept` headers.
- **URL Pattern**: Extract all canonical theme and preset pairs via regex:
  `r'https://themes\.shopify\.com/themes/([a-z0-9-]+)/presets/([a-z0-9-]+)'`

### Step 2: Turbo-Stream Release Notes Modal Extraction (`modal_version_details`)
- **Why Main Listing HTML Is Insufficient**: Commercial agencies (`Maestrooo`, `KrownThemes`, `Corknine`, `EcomxHQ`, `Invisible Themes`) frequently announce `blocks/` architecture, `nested blocks`, `OS 3.0 sections`, and `AI-generated blocks` inside their version release notes rather than main marketing blurbs. On the main listing page, the release notes modal (`#ModalVersionDetails`) is empty until triggered.
- **Endpoint**: `https://themes.shopify.com/themes/<slug>/presets/<preset>/modal_version_details?open_first=true`
- **Required Header**: Include `"Accept": "text/vnd.turbo-stream.html, text/html, application/xhtml+xml"` to retrieve the full HTML changelog history across all theme versions.

### Step 3: False-Positive Elimination & Rate-Limit Pacing
- **Global Navigation Strip**: Every page on `themes.shopify.com` includes a global navigation link to `/collections/horizon-themes` labeled `"Horizon themes"`. Always strip `<header>...</header>` and `<footer>...</footer>` before matching keywords so legacy themes are not falsely flagged as Horizon-based.
- **Rate-Limit Detection**: High-concurrency requests (`>10` threads) trigger soft rate limiting that returns the generic catalog landing page (`<title>Ecommerce Website Templates - Shopify Theme Store</title>`) with HTTP 200. Pace requests at `0.3s–0.35s` sequentially and verify `<title>` matches the theme name.

---

## 2. Verified 34 Shopify Themes on Theme Blocks 2.0 Architecture (3-Tier Classification)

### 🏆 Tier 1: 100% Native Theme Blocks 2.0 — Official Shopify Horizon Collection (10 Free Themes)
All 10 themes share the unified **Horizon Engine (v4.3.0+)** where every section mounts nested blocks (`blocks/*.liquid`, up to 8 nesting levels), uses private sub-blocks (`_group.liquid`, `_product-card.liquid`, `_product-details.liquid`), and natively supports Sidekick / Shopify Magic AI block generation (`https://themes.shopify.com/collections/horizon-themes`):

| # | Theme | Slug | Version | Price | Target Vertical / Preset Focus |
|---|---|---|---|---|---|
| 1 | **Horizon** | `horizon` | v4.3.0 | Free | Universal baseline reference for Theme Blocks 2.0 |
| 2 | **Ritual** | `ritual` | v4.3.0 | Free | Beauty, cosmetics, wellness, editorial grids |
| 3 | **Tinker** | `tinker` | v4.3.0 | Free | Tech, gadgets, DIY, modular hardware specs |
| 4 | **Pitch** | `pitch` | v4.3.0 | Free | High-converting DTC landers & single-product brands |
| 5 | **Heritage** | `heritage` | v4.3.0 | Free | Luxury, classic apparel, high-fashion storytelling |
| 6 | **Vessel** | `vessel` | v4.3.0 | Free | Home decor, furniture, ceramics, interior objects |
| 7 | **Savor** | `savor` | v4.3.0 | Free | Food & beverage, restaurants, craft consumables |
| 8 | **Fabric** | `fabric` | v4.3.0 | Free | Streetwear, high-SKU fashion catalogs |
| 9 | **Atelier** | `atelier` | v4.3.0 | Free | Boutiques, fine jewelry, artisan collections |
| 10 | **Dwell** | `dwell` | v4.3.0 | Free | Home living, lifestyle, modern essentials |

---

### 🚀 Tier 2: Native Commercial Theme Blocks 2.0 — Built from Scratch on Nested Blocks (6 Paid Themes)
Commercial themes architected specifically around nested `blocks/`, Group/Spacer layout primitives, and AI-generated blocks:

| # | Theme | Developer | Version | Architectural Evidence |
|---|---|---|---|---|
| 11 | **Bricks** (`bricks`) | Getsitecontrol | v2.2.0 | *"Latest Theme Architecture: Create richer layouts with Shopify’s nested theme blocks... built for seamless Sidekick compatibility"* |
| 12 | **Helix** (`helix`) | ModuTheme | v1.2.1 | *"Fully built with theme blocks and custom sections... card takes Spacer and Group blocks so title, meta, tag and button arrange in rows"* |
| 13 | **Unicorn** (`unicorn`) | MPIthemes | v5.0.0 | *"Packed w/ Nested Theme Blocks: Create flexible, layered layouts directly in the theme editor"* |
| 14 | **Primavera** (`primavera`) | Ultramarine | v1.6.1 | *"Versatile theme blocks or AI-generated blocks... Card theme block wraps other theme blocks"* |
| 15 | **Seventh** (`seventh`) | KrownThemes | v4.0.0 | *"Build with cards, theme blocks and sections in a flexible layout system that scales from classic grids to asymmetric designs"* |
| 16 | **Prompt** (`prompt`) | Noordthemes | v1.2.2 | *"Generate any theme block — describe it, and it’s coded instantly, simplifying customization"* |

---

### 🔧 Tier 3: Hybrid OS 2.0 + Theme Blocks 2.0 — Flagship Themes with Modular Block Sections (18 Paid Themes)
Established commercial flagships that integrated the `blocks/` directory, `{"type": "@theme"}` containers, nested blocks ("OS 3.0 sections"), and AI block generation into major releases:

1. **Maestrooo Portfolio** (Reusable Liquid Theme Blocks with nesting + AI-generated block support):
   - **Prestige** (`prestige`, v11.4.1) — Includes reusable theme blocks enabling nesting + AI-generated blocks.
   - **Impact** (`impact`, v7.2.0) — Includes reusable theme blocks enabling nesting + AI-generated blocks.
   - **Stretch** (`stretch`, v2.1.1) — Theme blocks (`Image`, `Image with caption`) with width controls + AI-generated blocks.
   - **Focal** (`focal`, v13.0.0) — Support for AI-generated theme blocks.
   - **Warehouse** (`warehouse`, v7.0.1) — Support for AI-generated theme blocks.
2. **KrownThemes Portfolio** (Flex Grid, Flexible Columns & Flexible Slideshow powered by 10+ reusable Theme Blocks):
   - **Combine** (`combine`, v4.2.0), **Local** (`local`, v4.2.1), **Borders** (`borders`, v3.1.0), **Split** (`split`, v5.1.0), **Highlight** (`highlight`, v4.1.0), **Kingdom** (`kingdom`, v6.2.0).
3. **Corknine, EcomxHQ, Invisible Themes, Envora & XoTiny**:
   - **Pipeline** (`pipeline`, Corknine, v8.2.0) — *"First to Support Nested Blocks: five new OS 3.0 sections with nested blocks"*.
   - **Electro** (`electro`, EcomxHQ, v3.5.0) — Free-form custom canvas section hosting reworked Text, Heading, Button, Image, Video, Group, and Icon theme blocks.
   - **Blum** (`blum`, EcomxHQ, v3.9.1) — FAQ Navigator revamped with nested blocks + Custom Section with AI-generated blocks.
   - **Normcore** (`normcore`, EcomxHQ, v2.5.0) — Custom Section with AI-generated blocks support.
   - **Broadcast** (`broadcast`, Invisible Themes, v8.1.1) — `"Slideshow (Nested)"` section introducing nested blocks.
   - **Soul** (`soul`, Envora Software, v5.1.0) — `"Product list: Tab"` and `"Flexible content"` sections built with Theme Blocks.
   - **Gentech** (`gentech`, XoTiny, v2.2.0) — Dedicated theme block showcase and block sections.
