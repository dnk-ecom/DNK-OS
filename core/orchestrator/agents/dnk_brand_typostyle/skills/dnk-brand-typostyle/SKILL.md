---
name: dnk-brand-typostyle
description: "Use when designing brand token systems, auditing WCAG 2.2/APCA contrast, engineering 1.25/1.20 modular typography scales, or exporting W3C DTCG and Google DESIGN.md tokens to Tailwind v4 and Shopify CSS."
version: "1.0.0"
tags:
  - design-tokens
  - typography
  - wcag-22
  - dtcg
  - google-design-md
  - cro
  - tailwind-v4
  - shopify-liquid
metadata:
  hermes:
    related_skills:
      - design-md
      - claude-design
      - popular-web-designs
      - shopify-agentic-canvas-themes
---
<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/dnk_brand_typostyle/skills/dnk-brand-typostyle/SKILL.md"
# purpose: "Level-of-Detail (LOD) skill guide for dnk_brand_typostyle: Google DESIGN.md, W3C DTCG tokens, font substitution table, WCAG 2.2/APCA contrast matrix, and 60-30-10 CRO rules."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---
-->

# dnk-brand-typostyle Skill

## 1. Overview & Trigger Conditions

Use `dnk-brand-typostyle` whenever a task requires:
- Synthesizing a brand identity into deterministic **W3C DTCG (`$value`, `$type`)** and **Google `DESIGN.md`** token specifications.
- Auditing or fixing color palettes against **WCAG 2.2 AA/AAA** and **APCA perceptual contrast** thresholds.
- Enforcing the **60-30-10 CRO Color Allocation Rule** across e-commerce PDPs, SaaS dashboards, and landing pages.
- Engineering a **Modular Typography Scale** (`1.250` Major Third or `1.200` Minor Third) with a strict `16px` (`1.000rem`) mobile body floor.
- Validating the **8pt Spatial Grid** (`0, 4, 8, 16, 24, 32, 48, 64px`).
- Exporting YAML/JSON design tokens into **Tailwind v4 `@theme`** blocks and **Shopify Liquid `:root` CSS Custom Properties**.

---

## 2. Google `DESIGN.md` & W3C DTCG Architecture

Every brand token specification in DNK OS bridges two industry standards:
1. **Google `DESIGN.md` Structural Discipline**:
   - Canonical section hierarchy: `Overview` ➔ `Colors (Primitives & Semantic)` ➔ `Typography` ➔ `Spacing & Layout` ➔ `Components`.
   - Surface-first hierarchy: define canvas and card surfaces before decorative accents.
2. **W3C DTCG Token Format (`dtcg-2025.10`)**:
   - Every primitive and semantic leaf token declares `$value` and `$type` (`color`, `dimension`, `fontFamily`, `number`).
   - Semantic tokens declare explicit contrast pairs (`contrast_against`, `min_contrast`) so deterministic linters verify accessibility without manual inspection.

---

## 3. 60-30-10 CRO Color System & Contrast Matrix (WCAG 2.2 / APCA)

To maximize conversion rate optimization (CRO) and eliminate visual noise on e-commerce storefronts and SaaS interfaces, color tokens are partitioned into three strict buckets:

| Allocation | Bucket Role | Canonical Semantic Tokens | CRO & Perceptual Purpose |
| :--- | :--- | :--- | :--- |
| **60%** | **Dominant Surface** | `--color-bg-base`, `--color-bg-subtle` | High-luminance neutral canvas (or deep obsidian in dark mode) that lets product photography breathe and prevents cognitive fatigue. |
| **30%** | **Structural & Copy** | `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-border-default` | High-contrast typographic hierarchy, card hairlines, and form boundaries that guide eye-scanning paths. |
| **10%** | **Focal Conversion Accent** | `--color-action-primary`, `--color-action-primary-hover`, `--color-text-on-action` | Reserved **exclusively** for primary revenue CTAs (`Add to Cart`, `Complete Checkout`, `Start Trial`). Never dilute the 10% accent on secondary badges or decorative icons. |

### WCAG 2.2 & APCA Contrast Verification Matrix

| Element Category | Font Size / Weight Threshold | Minimum WCAG 2.2 Ratio | Target APCA ($L_c$) | Mandatory Token Pair Check |
| :--- | :--- | :--- | :--- | :--- |
| **Normal Body Copy** | `< 18pt` (`< 24px`) regular or `< 14pt` (`< 18.66px`) bold | **$\ge 4.5 : 1$** (AA) / $7.0:1$ (AAA) | $L_c \ge 75$ | `text-primary`, `text-secondary` vs `bg-base` & `bg-subtle` |
| **Muted / Caption Copy** | `12px–14px` (`0.75rem–0.875rem`) | **$\ge 4.5 : 1$** | $L_c \ge 60$ | `text-muted` vs `bg-subtle` |
| **Large Display / Headings** | $\ge 18pt$ (`24px+`) regular or $\ge 14pt$ (`18.66px+`) bold | **$\ge 3.0 : 1$** | $L_c \ge 45$ | `h1`, `h2`, `display` vs `bg-base` |
| **Primary CTA Button Label** | `14px–18px` medium/semibold (`weight 500–600`) | **$\ge 4.5 : 1$** | $L_c \ge 75$ | `text-on-action` vs `action-primary` |
| **Interactive UI & Borders** | Input borders, focus rings, card dividers, CTA surface vs canvas | **$\ge 3.0 : 1$** | $L_c \ge 30$ | `border-default` & `action-primary` vs `bg-base` |

---

## 4. Modular Typography Scale & Font Substitution Table

### A. Modular Scale Invariants (Major Third `1.250` & Minor Third `1.200`)
- **Base Floor Invariant**: `body-md` MUST be `16px` (`1.000rem`). Never set mobile input or body copy below `16px` (prevents forced iOS viewport zoom).
- **Line-Height Guardrails**:
  - Headings (`display`, `h1`, `h2`, `h3`): `1.10` to `1.25` (tight vertical lockup).
  - Body copy (`body-lg`, `body-md`, `body-sm`, `caption`): `1.40` to `1.60` (comfortable reading rhythm).

| Token Step | Major Third (`1.250`) `rem` | Major Third `px` | Minor Third (`1.200`) `rem` | Minor Third `px` | Line Height | Tracking |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `display` | `2.441rem` | `39.06px` | `2.074rem` | `33.18px` | `1.12` | `-0.025em` |
| `h1` | `1.953rem` | `31.25px` | `1.728rem` | `27.65px` | `1.15` | `-0.020em` |
| `h2` | `1.563rem` | `25.00px` | `1.440rem` | `23.04px` | `1.20` | `-0.015em` |
| `h3` | `1.250rem` | `20.00px` | `1.200rem` | `19.20px` | `1.25` | `-0.010em` |
| `body-lg` | `1.125rem` | `18.00px` | `1.125rem` | `18.00px` | `1.50` | `0.000em` |
| `body-md` | `1.000rem` | `16.00px` | `1.000rem` | `16.00px` | `1.50` | `0.000em` |
| `body-sm` | `0.875rem` | `14.00px` | `0.875rem` | `14.00px` | `1.45` | `+0.005em` |
| `caption` | `0.750rem` | `12.00px` | `0.750rem` | `12.00px` | `1.40` | `+0.010em` |

### B. Commercial-to-Open Font Substitution Table (Zero-License-Friction)
When assimilating reference designs (Stripe, Linear, Vercel, Aesop) that use proprietary commercial typefaces, substitute them deterministically using open-source Google Fonts from `templates/font_pairings.json`:

| Commercial / Proprietary Font | Open-Source Google Font Substitute | Archetype Fit | Metric Adjustment |
| :--- | :--- | :--- | :--- |
| **Neue Haas Grotesk / Helvetica Now** | `Inter` or `Plus Jakarta Sans` | SaaS Precision / DTC E-commerce | `letter-spacing: -0.015em` on headings |
| **Söhne / Fakt / Graphik** | `Plus Jakarta Sans` or `Manrope` | High-Velocity E-commerce / Fintech | `font-weight: 600` for subheadings |
| **GT America / Apercu** | `Space Grotesk` + `DM Sans` | Streetwear / Hardware Retail | Enable `font-variant-numeric: tabular-nums` |
| **Canela / Tiempos Headline** | `Fraunces` or `Instrument Serif` | Editorial / Organic Wellness DTC | Tighten display line-height to `1.12` |
| **Didot / Optima / Ogg** | `Cormorant Garamond` or `Playfair Display` | Haute Luxury / Horology / Jewelry | Pair with `Montserrat` (`0.04em` uppercase tracking) |
| **Berkeley Mono / PragmataPro** | `JetBrains Mono` or `IBM Plex Mono` | Technical Specs / SKU / Price Tickers | `font-feature-settings: "zero" 1` |

---

## 5. 8pt Spatial Grid System

All layout spacing, container padding, and flex/grid gaps MUST resolve to exact multiples of `4px` / `8px`:
- `none`: `0px`
- `xs`: `4px` (`0.25rem`) — inline icon-to-label gap, tight badge padding
- `sm`: `8px` (`0.50rem`) — compact input padding, stacked list gap
- `md`: `16px` (`1.00rem`) — standard card padding, mobile container gutter
- `lg`: `24px` (`1.50rem`) — desktop card padding, form group spacing
- `xl`: `32px` (`2.00rem`) — section sub-grid gap
- `2xl`: `48px` (`3.00rem`) — mobile section vertical rhythm
- `3xl`: `64px` (`4.00rem`) — desktop hero and major section rhythm

---

## 6. Deterministic CLI Workflow

### Step 1: Author or Customize Token Specification
Copy `./core/orchestrator/agents/dnk_brand_typostyle/templates/brand_tokens_spec.yaml` and select a font pairing from `./core/orchestrator/agents/dnk_brand_typostyle/templates/font_pairings.json`.

### Step 2: Run Deterministic Linter (`lint_design_tokens.py`)
```bash
python3 ./core/orchestrator/agents/dnk_brand_typostyle/scripts/lint_design_tokens.py \
  --spec ./core/orchestrator/agents/dnk_brand_typostyle/templates/brand_tokens_spec.yaml \
  --json
```
The linter checks:
1. **WCAG 2.2 Contrast**: Relative luminance $L = 0.2126 R + 0.7152 G + 0.0722 B$ and contrast ratio $(L_1 + 0.05) / (L_2 + 0.05)$ across all semantic pairs ($\ge 4.5:1$ normal text, $\ge 3.0:1$ large text and UI components).
2. **8pt Grid Alignment**: Every spacing token is a valid multiple of `4px`/`8px` matching the canonical set.
3. **Typography Scale & Ratio**: `body-md == 16px`, valid scale ratio (`1.20` or `1.25`), and line-height bounds (`1.1–1.25` headings, `1.4–1.6` body).
4. **60-30-10 Allocation Sum**: `dominant_surface_pct + structural_typography_pct + focal_accent_pct == 100`.

### Step 3: Export CSS Custom Properties (`export_theme_css.py`)
```bash
python3 ./core/orchestrator/agents/dnk_brand_typostyle/scripts/export_theme_css.py \
  --spec ./core/orchestrator/agents/dnk_brand_typostyle/templates/brand_tokens_spec.yaml \
  --output ./artifacts/theme_tokens.css
```
Generates both `:root` variables (for Shopify Liquid `theme.liquid` / `base.css`) and `@theme` variables (for Tailwind CSS v4).

---

## 7. WCAG & CRO Verification Checklist

- [ ] `lint_design_tokens.py` exits with `code 0` and `"status": "PASS"`.
- [ ] Normal text pairs achieve $\ge 4.5:1$ contrast; UI borders and large text achieve $\ge 3.0:1$.
- [ ] `body-md` base font size is exactly `16px` (`1.000rem`).
- [ ] Primary CTA (`--color-action-primary`) is isolated to the 10% focal conversion bucket with $\ge 4.5:1$ label contrast (`--color-text-on-action`).
- [ ] All spacing tokens strictly follow the `4px / 8px` spatial grid.
