# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/tinker_migration_graphify_and_reverse_engineering_playbook.md"
# purpose: "Canonical Playbook for Horizon/Tinker Migration via Graphify, Visual Prior Reverse Engineering & Core DNK OS Integration for 2-10% Conversion Rate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🚀 Tinker Horizon Migration, Graphify Decomposition & Reverse-Engineering Playbook

This reference provides the end-to-end engineering architecture for:
1. Synthesizing SOTA open-source donors from the 1300+ repo catalog into a unified Shopify 3.0 system.
2. Migrating legacy monolithic themes (e.g. `DNK_Ecom_v1`) into the modular Horizon/Tinker engine via Graphify.
3. Rapid visual prototyping (HTML/PNG) and reverse-engineering competitor sites/screenshots into native Shopify Theme Customizer schemas.
4. Deep integration with the DNK OS Core (Brand Kit, SCONES Memory, Swarm Agents) to hit 2%–10% conversion rates.

---

## 🏛️ 1. Multi-Donor SOTA Repository Synthesis

| System Component | Donor Repository / Tool | Assimilated Capability & Advantage |
|---|---|---|
| **Theme Graph & AST** | `Graphify` + `@shopify/liquid-html-parser` | Directed Acyclic Graph (DAG) extraction, Leiden community detection for splitting monolithic sections into atomic features. |
| **Visual Prior Engine** | `yejy53/Editable-Design` | "Visual Prior, Without Pixel Shipping": layered semantic HTML/CSS + Tailwind instead of baked pixel graphics. |
| **Reverse Engineering** | `screenshot-to-code` + `patchright` | Undetectable DOM/Computed CSS extraction without WAF/Cloudflare blocks, paired with multimodal VLM element parsing. |
| **Theme Core (3.0)** | `Shopify/horizon` / `Tinker 4.3.1` | Block-first architecture: sections act as slot containers; all features reside as independent `blocks/*.liquid`. |
| **JSON State Mutations** | `RFC 6902 JSON Patch` | Deterministic template mutation (`templates/*.json`) avoiding key collisions or layout shifts. |
| **Cognitive Memory** | `DNK SCONES Memory` | Long-term storage of brand voice, niche conversion patterns, margin rules, and previous CRO experiments. |

---

## 🧬 2. Graphify AST Decomposition & Legacy-to-Tinker Migration

Legacy themes bundle hundreds of concerns into monolithic sections (e.g. 1,500 lines in `main-product.liquid`).

### Migration Flowchart:
```
[Monolithic Section (main-product.liquid)]
               │
               ▼  1. Liquid AST Parsing (@shopify/liquid-html-parser)
    [AST Node Tree: HTML + Liquid tags + schema settings]
               │
               ▼  2. Graphify Dependency Extraction
    [Graph: Nodes (Blocks, Snippets, Settings) + Edges (render, include, css)]
               │
               ▼  3. Community Detection (Leiden Algorithm)
    ┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
    ▼                          ▼                          ▼                          ▼
 [PDP Price Cluster]      [Sticky ATC Cluster]     [Trust & Proofs]       [Dynamic Bundles]
    │                          │                          │                          │
    ▼                          ▼                          ▼                          ▼
[tinker-price.liquid]     [tinker-sticky-atc.liquid] [tinker-trust.liquid]   [tinker-fbt.liquid]
   + {% schema %}             + {% schema %}             + {% schema %}             + {% schema %}
```

### Execution Protocol:
1. **Dependency Extraction**:
   - Extract nodes (`section`, `snippet`, `asset`, `setting`) and edges (`renders_snippet`, `uses_setting`, `fires_event`).
2. **Community Detection (Cluster by Intent)**:
   - Identify tightly coupled markup islands:
     - `pdp_conversion`: pricing, variant swatches, sticky ATC, inventory countdown.
     - `social_proof`: star ratings, customer review sliders, trust badges.
     - `cart_and_checkout`: cart drawer upsells, free shipping progress bar.
3. **Block Synthesis**:
   - Save each cluster to `blocks/tinker-[name].liquid`.
   - Strip parent section wrappers and synthesize an isolated `{% schema %}` with `"tag": null`.
4. **Blast-Radius & Dead Code Elimination (Tree-Shaking)**:
   - Run `graphify affected <snippet>` to ensure all required assets are copied.
   - Run `graphify query --in-degree 0 --type snippet` to delete orphan snippets.

---

## 🎨 3. Rapid Prototyping & Multimodal Reverse Engineering

Enables instant client approval and conversion of any external design into an editable Shopify theme.

### Dual-Speed Workflow:
1. **Input**: Competitor URL, design screenshot, or conversational prompt ("Create a luxury apparel hero with split video").
2. **Extraction / VLM Layer**:
   - For URLs: `patchright` extracts clean DOM, typography tokens, and computed CSS.
   - For Screenshots: Multimodal VLM decomposes the image into semantic UI layers (Background, Text, Media, CTA).
3. **Stage 1 — Rapid Prototype (HTML/PNG)**:
   - Generates a standalone HTML/Tailwind mockup in <5 seconds via `generate_html_prototype`.
   - Includes multi-viewport preview switcher (Desktop 100%, Tablet 768px, Mobile 390px) and a Dual-Mode Inspector Toggle:
     * **Live Preview**: Clean client-facing rendering.
     * **Customizer Inspector**: Interactive visual cues with green boundary borders and badges for all settings editable in Shopify Customizer.
   - Renders a headless Chromium screenshot or interactive preview URL for immediate approval.
4. **Stage 2 — Mechanical Transpilation (`mechanical_transpiler.py`)**:
   - `clean_competitor_html`: Strips third-party tracking scripts (Pixel, GA, Hotjar, TikTok), iframes, `on*` inline handlers, tracking hidden fields, and normalizes URLs.
   - `extract_design_tokens_from_html`: Derives color schemes, background modes, and border radii.
   - Converts the approved HTML prototype into a Shopify 3.0 Tinker Block/Section:
     - Text strings ➔ `{{ block.settings.title }}` (`type: "text"` or `"richtext"`).
     - Images ➔ `{{ block.settings.image | image_url: width: 1200 }}` (`type: "image_picker"`).
     - Links/Buttons ➔ `{{ block.settings.btn_url }}` (`type: "url"`).
     - Style tokens ➔ CSS custom properties (`--dnk-accent`, `--dnk-radius`).
5. **Shopify Customizer Parity & REST API Exposure**:
   - The merchant can edit every element directly in the native Shopify Theme Editor without code changes.
   - Exposed in `services/dnk_store_studio/src/router.py`:
     * `POST /api/v1/dnk_store_studio/reverse-engineer`
     * `POST /api/v1/dnk_store_studio/prototype`
     * Task actions: `reverse_engineer_competitor`, `transpile_visual_prior`, `generate_prototype`.

---

## 🧠 4. Deep Integration with DNK OS Core

```
┌────────────────────────────────────────────────────────────────────────┐
│                         DNK OS CORE                                    │
├───────────────────┬──────────────────────────┬─────────────────────────┤
│ 🎨 BRAND KIT SSOT │ 🧠 SCONES MEMORY         │ 🤖 SWARM ORCHESTRATION  │
│ • Color tokens    │ • Niche conversion data  │ • gerych_prime (Lead)   │
│ • Typography      │ • Free shipping threshold│ • gerych_researcher     │
│ • Tone of Voice   │ • Target AOV & margins   │ • gerych_builder        │
│ • Media assets    │ • Previous CRO winners   │ • dnk_shopify           │
│                   │                          │ • gerych_auditor        │
└─────────┬─────────┴────────────┬─────────────┴────────────┬────────────┘
          │                      │                          │
          └──────────────────────┼──────────────────────────┘
                                 ▼
                     [DNK STORE STUDIO]
                                 │
                                 ▼
                 Shopify 3.0 High-Converting Store
```

- **Brand Kit SSOT**: Brand colors, font pairings, and Tone of Voice are automatically injected into theme CSS variables and marketing copy.
- **SCONES Memory**: Stores client-specific business rules (e.g. Free shipping at 1500 UAH, 30-day warranty badge, high-margin accessories).
- **Swarm Execution**:
  - `gerych_researcher`: Gathers competitor layouts and review sentiments.
  - `gerych_builder`: Generates rapid Tailwind prototypes.
  - `dnk_shopify`: Compiles Liquid AST, schemas, and validates `shopify theme check`.
  - `dnk_video_ai_creator`: Generates dynamic product video compositions (Remotion).
  - `gerych_auditor`: Quality gate validator (Core Web Vitals, zero CLS, mobile thumb-zone compliance).

---

## 📈 5. High-Conversion Playbook (2% – 10% CR & AOV Boost)

1. **Mobile-First Thumb Zone**: All critical CTAs (Variant Selector, Sticky ATC, Cart Drawer trigger) reside in the bottom 40% of the mobile viewport.
2. **Sticky Add to Cart**: Activates automatically when the main product button scrolls out of view. Includes instant variant thumbnail & price.
3. **In-Cart Drawer Upsells & Progress Bar**:
   - Dynamic Free Shipping Bar updating in real-time via the AJAX Cart API.
   - 1-Click accessory upsells inside the cart drawer (lifts AOV by 15–25%).
4. **Frequently Bought Together (Bundles)**: Native PDP bundle cards offering 1-click combo purchase with automated discount calculation.
5. **Core Web Vitals 100/100**: Zero heavy client frameworks (Vanilla JS / Web Components < 30KB total); inlined critical section CSS.

---

## 🏛️ 6. Store Studio v2.0 Invariants & Strategic Mentorship Standards

### 6.1 Two-Phase "Prototype-First" Generation Lifecycle
To prevent context rot, 90/90 budget exhaustion, and wasteful Liquid schema compilation churn:
1. **Phase 1: Rapid Interactive Prototype (HTML/CSS & Canvas Preview)**:
   - Generate lightweight semantic layout within 5 seconds based on brand styles or VLM-analyzed competitor references.
   - Run **Design QA Gate**: WCAG contrast, spacing scale consistency, typography hierarchy, and thumb-zone compliance.
2. **Phase 2: Client Verification Gate**:
   - Client confirms layout, vibe, and CRO element placement (`status: 'approved'`).
3. **Phase 3: Deep Mechanical Transpilation & Theme Compilation**:
   - Only upon approval, engage `mechanical_transpiler.py` and `store_synthesizer.py` to synthesize atomic `blocks/*.liquid` and `templates/*.json`.

### 6.2 Core Data Architecture for Brand SSOT & CRO Analytics
Persist store assets across four dedicated relational/vector models (in PostgreSQL / SCONES):
- `brand_styles`: `(id, project_id, colors_json, fonts_json, logo_url, tone_of_voice)` — single source of truth for brand tokens preventing generic AI styling.
- `design_prototypes`: `(id, project_id, html_payload, image_urls, status)` — tracks prototype iterations and approvals.
- `theme_migrations`: `(id, project_id, old_theme_ref, new_theme_ref, graphify_blocks_json)` — audit trail of legacy section-to-molecule transformations.
- `cro_experiments`: `(id, project_id, cart_drawer_variant, bundles_variant, conversion_rate)` — closed-loop A/B conversion measurement.

### 6.3 Architectural Invariants & Anti-Patterns to Reject
- **Reject Generic External Swarm Frameworks (crewAI, autogen)**: Do not inject bulky external multi-agent libraries with high latency into DNK OS. DNK's native `dnk_swarm_parallel`, `TaskDNA`, and `Gerych Prime` are the unified SSOT.
- **In-House Graphify AST Engine**: Do not look for unmaintained external packages; use DNK Store Studio's native `theme_adapter.py` Graphify AST engine with community clustering.
- **Ethical Reverse Engineering**: Treat external competitor URLs and screenshots strictly as structural layout/CRO references, never as 1:1 pixel/code clones. Synthesize clean-room Horizon Tinker blocks adhering to DNK brand tokens.

