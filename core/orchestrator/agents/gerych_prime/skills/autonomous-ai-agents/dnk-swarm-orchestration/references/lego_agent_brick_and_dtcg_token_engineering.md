<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/lego_agent_brick_and_dtcg_token_engineering.md"
purpose: "Reference architecture for scaffolding LEGO Agent Bricks under core/orchestrator/agents/ and W3C DTCG 2025.10 + DESIGN.md token engineering."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-17"
author: "DNK-e.com Maksym & Gerych (Hermes Prime)"
--- END DNK-MRH-HEADER -->

# 🧱 LEGO Agent Brick Scaffolding & W3C DTCG Token Engineering (`dnk_brand_typostyle`)

## 1. Canonical LEGO Agent Directory Layout
When creating a domain-scoped LEGO Agent Brick under `core/orchestrator/agents/<agent_id>/`, enforce the following 4-layer structure:

```text
core/orchestrator/agents/<agent_id>/
├── SOUL.md                                 # Identity, mission & behavioral invariants (Protected: requires HITL approval)
├── agent_card.yaml                         # A2A v1.0 manifest (capabilities, routing, quality_gates, fallback_soul_invariants)
├── templates/                              # Declarative schemas & SSOT presets (YAML/JSON)
│   ├── brand_tokens_spec.yaml              # W3C DTCG 2025.10 + Google DESIGN.md hybrid spec
│   └── font_pairings.json                  # Curated domain presets
├── skills/<skill-slug>/SKILL.md            # LOD operational playbook (<= 450 lines)
└── scripts/                                # Deterministic CLI validators & transpilers (zero LLM cost)
    ├── lint_design_tokens.py               # WCAG 2.2 contrast, 8pt grid, modular scale audit
    └── export_theme_css.py                 # Transpiler to Shopify Liquid :root & Tailwind v4 @theme
```

### Handling Protected `SOUL.md` Creation in Autonomous Slices
- `SOUL.md` is in the runtime's protected agent-instruction file list (`write_file` / `patch` triggers an interactive `[y/n]` confirmation with a 60s timeout).
- If an autonomous run hits the approval timeout on `SOUL.md`, **never** attempt shell backdoors (`echo > SOUL.md` or python scripts). Instead, embed the full behavioral invariants, role metadata, and quality gates inside `agent_card.yaml` and `skills/<skill-slug>/SKILL.md`, and report the `SOUL.md` interactive gate status transparently to the operator.

---

## 2. Hybrid W3C DTCG (`dtcg-2025.10`) + Google `DESIGN.md` Token Contract
Every brand/design token specification (`brand_tokens_spec.yaml`) combines semantic narrative metadata (`DESIGN.md` conventions) with strict W3C DTCG typed nodes (`$value`, `$type`, `$description`):

1. **60-30-10 Color Proportion Rule**:
   - `60%` Primary Neutral / Canvas (`color.background.canvas`, `color.background.surface`)
   - `30%` Structural Brand / Typography / Borders (`color.text.primary`, `color.border.default`, `color.brand.secondary`)
   - `10%` High-Salience Conversion CTA Accent (`color.brand.accent`, `color.action.cta_bg`)
2. **WCAG 2.2 Relative Luminance & Contrast Math**:
   - Standard body text (`< 18pt` or `< 14pt bold`) against its paired surface MUST achieve **`>= 4.5:1`** contrast ratio (`(L1 + 0.05) / (L2 + 0.05)`).
   - Large display headings (`>= 24px`) and UI borders/focus rings MUST achieve **`>= 3.0:1`**.
3. **Modular Typography Scale**:
   - Base body font size (`typography.scale.body-md`) MUST be `>= 16px` (`1rem`) to prevent mobile readability regressions and iOS Safari input auto-zoom.
   - Desktop scale ratio: **`1.250` (Major Third)** (`16 -> 20 -> 25 -> 31 -> 39 -> 49px`, `±1px` integer rounding tolerance).
   - Mobile scale ratio: **`1.200` (Minor Third)**.
4. **8pt Spatial & Radius Grid**:
   - Primary spacing and layout tokens align to `8px` multiples; sub-grid micro-tokens (`4px`, `12px`) must satisfy `px % 4 == 0` (with `0px`, `1px`, `2px`, and `9999px` pill exemptions).

---

## 3. Deterministic CLI Verification & CSS Transpilation

Always run token validation in the project `.venv` before exporting CSS or Liquid variables:

```bash
# 1. Lint token spec (outputs JSON report + exit code 0 on PASS, 1 on FAIL)
source ./.venv/bin/activate && python3 ./core/orchestrator/agents/dnk_brand_typostyle/scripts/lint_design_tokens.py \
  --input ./core/orchestrator/agents/dnk_brand_typostyle/templates/brand_tokens_spec.yaml \
  --json

# 2. Export CSS Custom Properties (:root) + Tailwind v4 (@theme)
source ./.venv/bin/activate && python3 ./core/orchestrator/agents/dnk_brand_typostyle/scripts/export_theme_css.py \
  --input ./core/orchestrator/agents/dnk_brand_typostyle/templates/brand_tokens_spec.yaml \
  --output /tmp/theme_tokens.css \
  --tailwind
```
