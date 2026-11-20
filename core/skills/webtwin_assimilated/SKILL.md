---
name: webtwin_assimilated
description: "Assimilated SOTA Website Cloner, Asset Extractor, and UI Component Analyzer from sirioberati/WebTwin. Used for demo-first sales pipelines, Shopify brand analysis, and headless asset ingestion."
version: "1.0.0"
category: "scraping_and_ingestion"
assimilated_at: "2026-10-31"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "dnk_dev_fullstack"
status: active
domain: webtwin_assimilated
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/skills/webtwin_assimilated/SKILL.md"
> purpose: "Assimilated WebTwin Website Extractor and UI Extraction Engine for DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-10-31"
> author: "Denchik Master Builder & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌐 WEBTWIN SOTA Assimilation Index & Ecom Extractor Engine

Assimilated from **[sirioberati/WebTwin](https://github.com/sirioberati/WebTwin)** (MIT License).

Equips DNK OS with automated website cloning, deep asset extraction (HTML, CSS, JS, Fonts, Images), and UI component separation (Hero, Nav, Cards, Modals). Enables our **Demo-First Spec Selling** pipeline to analyze competitor stores or client candidates and scaffold high-converting Shopify demo storefronts in under 15 minutes.

---

## 📌 Repository Intel & Legal Boundary
- **Upstream Repository**: `sirioberati/WebTwin`
- **Author**: Sirio Berati (`@sirioberati`)
- **License**: `MIT` (Commercial-Safe / Permissive)
- **Assimilation Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Workers**: `dnk_shopify` (Shopify Theme Mapping), `dnk_dev_fullstack` (Catalog Ingestion & Extraction)
- **Status**: 🟢 **ACTIVE & PRODUCTION READY**

---

## 🚀 Key Capabilities for DNK OS

1. **Brand Asset Ingestion**:
   - Downloads client fonts, primary color schemes, logo SVG/PNG, and OpenGraph metadata in a single run.
2. **Product & Image Catalog Extraction**:
   - Maps out high-resolution product imagery from non-Shopify sites (WooCommerce, Prom, OpenCart, custom CMS) for automated re-import into Shopify.
3. **UI Component Deconstruction**:
   - Classifies page sections into semantic blocks: `Header`, `Hero`, `ProductGrid`, `Testimonials`, `Footer`.
   - Allows instant mapping onto DNK OS modular Liquid/JSON theme blocks.

---

## 🛠️ Usage Recipe: Fast Brand Asset Extraction

```python
from core.skills.webtwin_assimilated.scripts.fast_brand_extractor import extract_brand_palette

# Extract brand assets and color palette from candidate target
brand_data = extract_brand_palette("https://example-brand.com")
print(brand_data["colors"], brand_data["logo_url"])
```
