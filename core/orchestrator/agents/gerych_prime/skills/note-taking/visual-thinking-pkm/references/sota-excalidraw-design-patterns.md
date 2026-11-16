# SOTA Excalidraw Design System: Adapted from Modern Web & Architecture Skills

<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/visual-thinking-pkm/references/sota-excalidraw-design-patterns.md"
purpose: "Unified SOTA Excalidraw design system synthesizing architecture-diagram, baoyu-infographic, and popular-web-designs for executive and viral visual artifacts."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-09"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

## 1. Synthesis of Design Skills for Excalidraw

To eliminate the "child's drawing" appearance and produce high-authority, executive-grade Excalidraw diagrams, we synthesize principles from three core design skills:

1. **`architecture-diagram` (Dark Tech Aesthetic & Layered Containment)**:
   - **Dark Slate Canvas**: Background `#090d16` (Slate-950) or `#0b0f19`.
   - **Layered Cards**: High-contrast container boxes (`#111827`, `#0f172a`, `#1e293b`) with subtle stroke hierarchy (`#334155`, `#475569`).
   - **Double-Layer Masking**: Solid dark backing underneath semi-transparent vector elements prevents intersecting connector bleed.
   - **Semantic Color Tokens**: Strict 4-color discipline (Danger/Heat `#ef4444`, Warning/Mechanism `#f97316`, Tech/Isothermal `#06b6d4`, Success/Payoff `#10b981`).

2. **`baoyu-infographic` (Visual Storytelling & Physical Metaphors)**:
   - **Illustrative Schematics over Empty Blocks**: Never leave visual zones as mere bulleted text containers. Draw concrete physical objects (cutaways, instruments, chambers, flow loops, instruments, gradients).
   - **Problem ➔ Mechanism ➔ Chaos ➔ Solution ➔ Payoff Architecture**: Clear cognitive progression from shock to engineering resolution.
   - **Micro-Visuals**: Gauges, LCD meters, fluid levels, droplets, temperature gradients, laser beams, and stamps.

3. **`popular-web-designs` (Linear / Vercel Modern UI Language)**:
   - **Pill Badges & Status Chips**: Rounded pill containers (`roundness: {"type": 3}`) for timestamps, scene numbers, and tags (e.g. `[ 0:00 - 0:04 ]`, `[ SFX: BASS DROP ]`).
   - **Micro-typography Hierarchy**:
     - Large Canvas Title: 28–36px bold.
     - Frame / Card Title: 22–26px bold.
     - Section Badges: 16–18px bold.
     - Body & Voiceover: 14–16px (line-height 1.35). Strictly no micro-fonts (<14px).
   - **Generous Human-Scale Spacing**: Minimum 440–500px card width, 50–60px gutters, consistent vertical padding.

---

## 2. Palette & Visual Token Reference

| Semantic Role | Stroke Hex | Fill Hex | Usage in Diagrams |
| :--- | :--- | :--- | :--- |
| **Canvas Baseline** | `None` | `#090d16` | Global viewport background |
| **Container Card** | `#334155` | `#111827` / `#0f172a` | Main structural card frames |
| **Sub-Container** | `#1e293b` | `#182234` / `#1e1e2e` | Inner compartments (voiceover, camera, SFX) |
| **Critical / Heat** | `#ef4444` | `#450a0a` / `#7f1d1d` | Fatal errors, pyrometer, +60°C smoke, acid |
| **Combustion / Warning** | `#f97316` | `#431407` | Amber heat, fire base, tar, warning calls |
| **Engineering / SOTA** | `#06b6d4` / `#38bdf8`| `#083344` | Reburn condenser, isothermal smoke +23°C, cooling |
| **Success / Payoff** | `#10b981` / `#34d399`| `#064e3b` | Perfect smoked salmon, stamps, CTA buttons |
| **Text Primary** | — | `#f8fafc` | Main titles and high-priority labels |
| **Text Secondary** | — | `#94a3b8` / `#cbd5e1` | Descriptions, specifications, voiceover script |

---

## 3. Physical Vector Schematics Library (Code Recipes)

### 3.1 Digital Laser Pyrometer
- Gun handle (`rectangle` rotated or angled `width: 35, height: 70`).
- Barrel housing (`rectangle` `width: 90, height: 45`).
- Laser sight line (`arrow` with `strokeStyle: "dashed"`, `strokeColor: "#ef4444"`).
- Digital LCD Screen: High-contrast box with large 24–28px red digits (`62.4 °C`) and warning badge.

### 3.2 Muscle Tissue Cutaway & Denaturation
- Outer fillet boundary (`rectangle` with `roundness: {"type": 3}`).
- Denatured surface layer: Outer border band in milky pink/red (`#7f1d1d`).
- Droplets: Multiple small `ellipse` elements (`#38bdf8` or `#ef4444`) with down-pointing arrows indicating moisture loss / weeping.

### 3.3 500L Chamber Thermal Stratification
- Outer insulated box (`#1e293b`, border `#64748b`).
- Upper Hot Zone: `#450a0a` fill with +50°C label and blackened product icons.
- Lower Cold Zone: `#083344` fill with +18°C label and raw product icons.
- Recirculation stagnation spiral arrow showing lack of aerodynamic velocity.

### 3.4 Reburn Multi-Stage Separation Engine
- Combustion canister with amber flame base.
- Multi-pass stainless cooling loop with heat dissipation radiating lines.
- Transparent cyclone condensate jar with dark tar liquid fill (`#1c1917` level: "100 ml смоли й оцту").
- Clean blue isothermal laminar smoke stream entering chamber at `+23°C`.

### 3.5 4K Amber Product Payoff & Glowing CTA Button
- Rich wooden cutting board (`#292524`).
- Sliced translucent salmon fillet (`#f97316`) with glossy oil sheen accents.
- Quality Certificate / Stamp Badge (`#064e3b` fill, `#10b981` border).
- High-visibility Glowing CTA Button (`#047857` fill, `#34d399` stroke, 20px bold text).
