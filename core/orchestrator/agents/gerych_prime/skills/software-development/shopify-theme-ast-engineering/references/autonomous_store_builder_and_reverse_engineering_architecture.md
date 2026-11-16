# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/autonomous_store_builder_and_reverse_engineering_architecture.md"
# purpose: "Architecture playbook for autonomous AI Shopify store creation, reverse engineering, and Canvas-to-Liquid synthesis."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-29"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🏪 Autonomous AI Shopify Store Generator & Reverse Engineering Architecture

## 1. Executive Summary & Core Paradigm
Building production-grade Shopify stores autonomously requires an Intermediate Representation (IR) architecture rather than direct text-to-code generation. 

Direct LLM code generation fails on Shopify OS 2.0 due to:
1. Malformed JSON within `{% schema %}` blocks causing store crashes.
2. Inconsistent Liquid block nesting (`{% content_for 'blocks' %}`).
3. Broken setting IDs and schema-template desynchronization.

The solution is a 4-tier pipeline:
`Intelligence Sourcing ➔ Canvas IR Graph ➔ Store Synthesizer (AST Transpiler) ➔ FastMCP Verification & GitHub Delivery`.

---

## 2. 4-Tier System Architecture

```
                  ┌────────────────────────────────────────┐
                  │    1. INTELLIGENCE & SOURCING          │
                  │  ScrollStash MCP (1.76M+ DTC Ads/Pages)│
                  │  GitHub API (Shopify Horizon / Dawn)   │
                  │  Sitepeel Inspector (DOM & Style Peel) │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │     2. CANVAS INTERMEDIATE REP (IR)    │
                  │  ShopifyCanvasGraph (Nodes, Edges)     │
                  │  Design Tokens (Colors, Typography)    │
                  │  Section & Block Settings Schema       │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      3. STORE SYNTHESIZER ENGINE       │
                  │  services/dnk_shopify/studio/          │
                  │  - Brand DNA Analyzer                  │
                  │  - CanvasToLiquidTranspiler            │
                  │  - Horizon Theme Blocks Synthesizer    │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │    4. VERIFICATION & DEPLOYMENT        │
                  │  FastMCP Tool: shopify_validate_liquid │
                  │  Shopify Theme Check / AST Gate        │
                  │  GitHub PR / Theme Release Pipeline    │
                  │  Shopify Admin GraphQL API Sync        │
                  └────────────────────────────────────────┘
```

---

## 3. Tier 1: Intelligence Sourcing & Reverse Engineering
- **ScrollStash MCP (`053`)**: Queries high-converting DTC landing pages, PDPs, and listicles. Extracts structural blueprints and copy frameworks by brand/niche.
- **Sitepeel Inspector (`054`)**: Reverse-engineers live Shopify DOM and CSS into modular design tokens (`apps/web/styles/shopify-tokens.css`). Extracts typography, surface palettes, button states, and spacing scales.
- **GitHub Reference Themes**: Pulls atomic theme blocks from canonical open-source repositories (`Shopify/horizon` for theme blocks, `Shopify/dawn` for core templates).

---

## 4. Tier 2: Canvas Intermediate Representation (IR)
State is maintained as a deterministic JSON graph rather than raw code:
- **Node Contract**:
  ```json
  {
    "id": "hero_banner_01",
    "type": "horizon_block",
    "block_type": "hero_split",
    "settings": {
      "heading": "Next-Gen Bio-Adaptive Serum",
      "accent_color": "var(--shopify-accent)",
      "cta_label": "Shop Collection",
      "cta_url": "/collections/all"
    },
    "children": ["badge_01", "cta_button_01"]
  }
  ```
- **Advantages**:
  - Live interactive drag-and-drop editing in `apps/web/lib/api/shopify_canvas_client.ts`.
  - Zero context rot: changes are localized to individual node diffs (RFC 6902).

---

## 5. Tier 3: Store Synthesizer & Liquid Transpilation
- Located at `services/dnk_shopify/shopify_liquid/canvas_to_liquid_transpiler.py`.
- **Horizon Theme Blocks Support**:
  - Generates atomic `blocks/*.liquid` with standalone schemas.
  - Assembles section containers utilizing `{% content_for 'blocks' %}` to allow merchant customization.
- **Template Synthesis**:
  - Generates valid `templates/*.json` structure matching Shopify OS 2.0 specifications.

---

## 6. Tier 4: Verification, Quality Gate & Delivery
1. **FastMCP Validation**:
   - `shopify_validate_liquid`: Validates Liquid tag balance, filter validity, and JSON schema syntax.
   - Blocks deployment if schema JSON has trailing commas, unclosed brackets, or invalid input types.
2. **Automated GitHub Delivery**:
   - Uses pre-authenticated GitHub MCP tools (`mcp__github__create_pull_request`, `mcp__github__push_files`).
   - Pushes generated themes or app blocks directly to client repos as review-ready PRs.
