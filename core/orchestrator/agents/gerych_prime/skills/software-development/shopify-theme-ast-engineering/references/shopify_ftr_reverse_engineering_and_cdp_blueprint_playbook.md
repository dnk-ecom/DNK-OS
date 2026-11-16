# --- DNK-MRH-HEADER ---
# mrh_id: "skills_shopify_theme_ast_engineering_references_ftr_playbook"
# purpose: "First-Time-Right (FTR) 4-Stage Reverse-Engineering Protocol for Shopify Themes & PDP Blocks"
# author: "DNK-e.com Maksym"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# --- END DNK-MRH-HEADER ---

# 🎯 First-Time-Right (FTR) Reverse-Engineering Protocol for Shopify Themes

The First-Time-Right (FTR) methodology enforces a strict "Inspect ➔ Dissect ➔ Plan ➔ Gate" contract to eliminate repetitive LLM guessing, token waste, and brittle UI generation.

---

## 🏗️ 1. The 4-Stage FTR Execution Ladder

```
[1. INSPECT (Deterministic CDP)] ➔ [2. DISSECT (Sanitization)] ➔ [3. PLAN (Atomic Slices)] ➔ [4. GATE (Verification)]
       │                                   │                              │                             │
   Zero LLM                            Regex Filter                  <= 25 tools/slice             Playwright QA
   Computed CSS & DOM                  Zero Vendor Tokens            AST & Liquid Schema           Viewport Bounds
```

### Phase 1: Inspect (Headless Browser / CDP Extraction)
* **Goal:** Extract true runtime computed state rather than guessing styles from raw HTML.
* **Tools:** Headless Playwright / Chrome DevTools Protocol (`computer_use` or CLI script `scripts/tools/extract_pdp_blueprint.py`).
* **Artifacts Collected:**
  - Computed styles (typography: `font-size`, `line-height`, `font-weight`, `letter-spacing`).
  - Spatial box model (margins, paddings, gap, border-radius, elevation/shadows).
  - Raw SVG icons and asset dimensions.
  - Interactive states (`:hover`, `:focus-visible`, `:active`, open/close drawers).

### Phase 2: Dissect (Zero-Vendor Sanitization & Token Mapping)
* **Goal:** Strip proprietary vendor classes and extract design tokens.
* **Invariants:**
  - **Zero-Vendor Regex Filter:** Automatically remove vendor IDs, tracking pixels, third-party app prefixes (`criteo`, `klaviyo`, `shrine-*`, `loox`).
  - **Token Synthesis:** Convert hardcoded pixel values and hex codes into standard Shopify theme settings (`settings.colors_text`, `settings.font_heading`, `var(--color-primary)`).

### Phase 3: Plan (Atomic Slices & TaskDNA Mapping)
* **Goal:** Decompose the extracted blueprint into clean Shopify OS 2.0 theme components.
* **Component Partitioning:**
  - Main section (`sections/main-product-pdp.liquid`)
  - Modular theme blocks (`blocks/product-buy-buttons.liquid`, `blocks/product-rating-stars.liquid`)
  - Isolated CSS schema (`assets/component-ftr-product.css`)
  - Schema JSON with presets and customizer controls.
* **Execution Bound:** Maximum 25 tool calls per implementation slice (Mandatory Atomic Slice Execution).

### Phase 4: Gate (Automated Dual-State Verification)
* **Goal:** Deterministic machine proof before declaring completion.
* **Automated Checks:**
  1. **Schema Integrity:** `python3 scripts/system/validate_liquid.py` (JSON schema syntax & tag balance).
  2. **Viewport Bounding:** Playwright test verifying zero horizontal overflow (`overflow-x == 0`) across 375px, 390px, 768px, and 1280px.
  3. **Touch Targets:** Minimum 44x44px for all mobile interactive elements (buttons, quantity selectors, variant pills).

---

## 🚫 2. Anti-Patterns & Invariants

1. **No Agent Proliferation:**
   - Do NOT create standalone ephemeral subagents for simple extraction tasks.
   - Use deterministic CLI scripts for extraction (0 LLM tokens) and route coding to the core workhorse `dnk_shopify`.
2. **Zero-Rsync & Root Working Tree:**
   - Modify theme assets directly in the target repository structure without intermediate mirror copies.
3. **No Guessing CSS:**
   - If an element's alignment or typography is ambiguous, re-inspect via CDP rather than iteratively guessing CSS properties.
