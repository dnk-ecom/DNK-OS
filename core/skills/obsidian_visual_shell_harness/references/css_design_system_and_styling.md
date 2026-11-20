<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/obsidian_visual_shell_harness/references/css_design_system_and_styling.md"
# purpose: "Complete reference for Obsidian Visual Shell Design System, Tokens, and CSS Snippets."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🎨 Obsidian Visual Shell Design System & CSS Styling

The visual ergonomics of DNK OS Obsidian are governed by three custom CSS snippets located in `.obsidian/snippets/`.

---

## 💎 The 3 Canonical Snippets

### 1. `dnk-flat-green.css` (Flat Green Design System)
- **Philosophy**: Clean, high-contrast, distraction-free green aesthetic (`#10b981`, `#059669`, `#064e3b`).
- **Core Rules**:
  - **Font Family**: Standardized to `fontFamily: 2` (clean geometric sans-serif) across Excalidraw and notes.
  - **Zero Text Bleed**: Precise padding rules preventing text overlapping boxes or shapes.
  - **Status Pill Badges**: Custom styles for metadata tags:
    - `.tag[href="#active"]`: Emerald green pill with soft glow.
    - `.tag[href="#draft"]`: Amber subtle badge.
    - `.tag[href="#locked"]`: Slate dark lock badge.

### 2. `shopify-polaris-helix.css` (Polaris Design Tokens)
- **Philosophy**: Aligns DNK OS spatial tools with Shopify's production Polaris design language.
- **Key Features**:
  - Shopify Polaris surface colors (`--p-color-bg-surface-primary`).
  - Card elevation, border radiuses (`--p-border-radius-base: 8px`).
  - High-readability tables for Dataview registries.

### 3. `full-width-view.css` (Spatial Full-Width Canvas)
- **Philosophy**: Unlocks infinite canvas potential by suppressing standard markdown page gutters.
- **Key Features**:
  - Overrides Obsidian's default reading margin (`max-width: 100% !important`).
  - Adapts seamlessly to 4K displays and ultra-wide spatial development monitors.
  - Prevents horizontal scroll clipping in Dataview queries.

---

## 🖌️ Excalidraw Standard Scene Attributes

When synthesizing or modifying Excalidraw drawings for DNK OS, agents must adhere to the following defaults:

| Property | Value | Description |
| :--- | :--- | :--- |
| `fontFamily` | `2` | Clean modern sans-serif |
| `fontSize` | `16` (Body) / `24` (Subhead) / `32` (Header) | Uniform scale hierarchy |
| `roughness` | `0` | Architect-grade crisp lines (zero sketchy wobble) |
| `strokeSharpness` | `round` | Soft contemporary tech corners |
| `backgroundColor` | `#0f172a` (Dark) / `#ffffff` (Light) | Solid contrast surfaces |
| `strokeColor` | `#10b981` (Primary Green) / `#94a3b8` (Muted Slate) | DNK palette compliance |
