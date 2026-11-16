<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/visual-thinking-pkm/references/excalidraw-visual-cohesion-and-tokens.md"
purpose: "Excalidraw Visual Cohesion Guide: Solving Radius & Color Inconsistencies via Design Tokens and Roundness Invariants."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-12"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Excalidraw Visual Cohesion & Design Tokens Standards

This reference resolves common visual discrepancies when generating architectural and technical diagrams in Excalidraw: mismatched corner radii (`roundness`), color dissonance, and inconsistent stroke styles.

---

## 1. Corner Radius Discrepancies (`roundness` Invariant)

Excalidraw JSON elements support three distinct `roundness` values:

| Value | Behavior | Geometry | Recommended Use |
| :--- | :--- | :--- | :--- |
| `null` | **Sharp corners** | Strict 90° angles | Bounding viewports, outer boundary masks, or strict matrix charts. |
| `{"type": 2}` | **Proportional (Legacy)** | Radius = `min(width, height) * 0.1` (clamped up to 32px) | **Do NOT use for mixed card sizes.** A 500x300 card gets a huge ~30px radius, while a 180x50 card gets ~5px, causing severe visual mismatch. Use only for smooth connector lines / arrows. |
| `{"type": 3}` | **Adaptive Fixed Radius** | Constant modern radius (~10–12px) across all card sizes | **MANDATORY for all cards, containers, badges, and boxes.** Guarantees visual harmony across different card proportions. |

### The Uniformity Rule
- **Never mix `{"type": 2}` and `{"type": 3}` on cards in the same diagram.**
- Standardize all diagram cards and inner boxes to `roundness: {"type": 3}`.
- Connectors / arrows: `roundness: {"type": 2}` (smooth elbow curves) or `null`.

---

## 2. Stroke & Style Invariants (`roughness` & `strokeWidth`)

1. **`roughness: 0` (Clean Architectural Invariant)**:
   - For all technical architectures, system flows, and UI layouts, set `roughness: 0`.
   - Never leave default `roughness: 1` (wobbly/hand-drawn) on formal architecture schemas unless an intentional paper-sketch aesthetic is explicitly requested.
2. **`strokeWidth` Hierarchy**:
   - `strokeWidth: 1`: All standard structural cards, nested boxes, and badge borders.
   - `strokeWidth: 2`: Primary data-flow arrows, active stage boundaries, or security gates.
   - `strokeWidth: 3`: Critical system failure paths or high-priority warning boxes.

---

## 3. Strict Dark Mode Color Tokens (Linear / Shadcn Palette)

Never hardcode arbitrary hex literals across individual element functions. Use this semantic token system:

| Role | Token Name | Stroke Hex | Fill Hex | Semantic Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **Viewport Background** | `CANVAS_BG` | `transparent` | `#090d16` (or `#020617`) | Global canvas backdrop |
| **Stage Container** | `CONTAINER` | `#1e293b` (Slate-800) | `#0f172a` (Slate-900) | Stage columns / group boxes |
| **Nested Card Base** | `CARD_BASE` | `#334155` (Slate-700) | `#182234` | Sub-tasks, component details |
| **Domain: Blue/Sky** | `DOMAIN_SKY` | `#38bdf8` (Sky-400) | `#0c2340` (Sky-950) | Ingestion, R&D, Prime, Discovery |
| **Domain: Purple** | `DOMAIN_PURPLE` | `#c084fc` (Purple-400) | `#2e1065` (Purple-950) | Security, Auditor, Gating, Review |
| **Domain: Emerald** | `DOMAIN_EMERALD` | `#34d399` (Emerald-400) | `#064e3b` (Emerald-950) | Librarian, Storage, SCONES, Approved |
| **Domain: Amber** | `DOMAIN_AMBER` | `#fbbf24` (Amber-400) | `#451a03` (Amber-950) | Human-in-the-loop, Decisions |
| **Domain: Rose** | `DOMAIN_ROSE` | `#f43f5e` (Rose-500) | `#4c0519` (Rose-950) | Blocked, Quarantined, Violation |
| **Text Primary** | `TEXT_PRIMARY` | `#f8fafc` (Slate-50) | `transparent` | Node titles, headings (>= 16px) |
| **Text Muted** | `TEXT_MUTED` | `#94a3b8` (Slate-400) | `transparent` | Descriptions, meta, specs (>= 14px) |

---

## 4. Python Generator Template with Centralized Tokens

When authoring custom Python generation scripts (e.g. `scripts/system/generate_*_excalidraw.py`), always structure with a centralized token dictionary:

```python
TOKENS = {
    "canvas_bg": "#090d16",
    "stage_bg": "#0f172a",
    "stage_border": "#1e293b",
    "card_border": "#334155",
    "text_primary": "#f8fafc",
    "text_muted": "#94a3b8",
    "sky_stroke": "#38bdf8",
    "sky_fill": "#0c2340",
    "purple_stroke": "#c084fc",
    "purple_fill": "#2e1065",
    "emerald_stroke": "#34d399",
    "emerald_fill": "#064e3b",
    "rose_stroke": "#f43f5e",
    "rose_fill": "#4c0519",
}

# Standard card defaults:
# roughness = 0
# roundness = {"type": 3}
# strokeWidth = 1
```
