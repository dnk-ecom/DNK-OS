---
name: visual-thinking-pkm
description: Use for Obsidian, Excalidraw, and spatial PKM visual graphs.
version: 1.0.0
author: Gerych Prime, DNK OS
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Excalidraw, PKM, VisualThinking, ExcaliBrain, KnowledgeGraph, MindMap]
    related_skills: [obsidian, excalidraw]
---

# Visual Thinking & Spatial PKM (Obsidian + Excalidraw)

## When to use

Use this skill when:
- Integrating Obsidian markdown vaults with Excalidraw drawings, canvas boards, or mindmaps.
- Structuring dual-nature visual notes (`.excalidraw.md`) with bi-directional wikilinks and transclusion.
- Implementing structured knowledge graph navigation (TheBrain / ExcaliBrain topology).
- Automating diagrams via Mermaid-to-Excalidraw transpilation or ExcalidrawAutomate scripts (`ea-scripts`).
- Configuring modal popup live note editing (`obsidian-hover-editor`) over visual canvases.
- Translating competitor screenshots and Excalidraw visual notes into autonomous agent system specifications (Visual-First Pipeline).

## Core Architecture: Dual-Nature Visual Notes

In Obsidian, Excalidraw visual documents (`.excalidraw.md`) function as both vector drawings and first-class markdown citizens:

```markdown
---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data
## Text Elements
Visual Concept Label ^blockAnchor1

## Element Data
```

### Invariants & Linking Rules
1. **Full-Text & Backlink Searchability**: All text placed on canvas shapes is mirrored under `## Text Elements`. You can link to any specific text element using Obsidian block references: `[[DrawingNote#^blockAnchor1]]`.
2. **Font Family Standards & Mapping**:
   - **`fontFamily: 5` (Excalifont)**: Mandatory default handwriting font used across the DNK OS vault (matches `Нотатки структури DNK OS 090926.excalidraw.md`). Provides native Cyrillic glyphs. Set `appState.currentItemFontFamily: 5` and `"fontFamily": 5` on all text nodes.
   - **`fontFamily: 1` (Virgil)**: Legacy hand-drawn font. **Pitfall**: lacks Cyrillic glyphs, causing Ukrainian text to fall back to mismatched system fonts. Do NOT use for new vault diagrams.
   - **`fontFamily: 2` (Helvetica / Normal)**: Clean sans-serif for UI mockups or corporate docs.
   - **`fontFamily: 3` (Cascadia Code)**: Monospace font for code blocks, JSON snippets, and technical IDs.
   - **`fontFamily: 4` (Local Font)**: User-defined custom font configured in plugin settings.
3. **In-Memory Tab Caching & Reloading Pitfall**:
   - Obsidian's Excalidraw plugin caches open drawing views in memory (`if (this.lastLoadedFile === this.file) return;`).
   - When external scripts update `.excalidraw` or `.excalidraw.md` on disk, an already-open Obsidian tab will NOT automatically reload from disk.
   - To view updates: close the tab (`×`) and reopen, press `Cmd + R`, or choose "Reload without saving" in Excalidraw.
4. **Ukrainian Language SSOT**: All canvas node labels, zone headings, and cards must be in clear, structured Ukrainian (🇺🇦) using official DNK OS concepts (Task Forest, Graphify, Visual Prior, Tinker Blocks).
5. **Compressed Storage (`compressed-json`)**:
   - Obsidian Excalidraw plugin saves drawings as ````compressed-json\n<base64>\n```` using LZString (`lzstring.LZString().compressToBase64(json_str)`).
6. **Embedded Self-Documenting Manifest Invariant (Self-Explaining Canvas)**:
   - When generating or maintaining `.excalidraw.md` canvases representing architecture, workflows, or mental models, **ALWAYS embed the comprehensive explanation, rationale ("Why so?"), human guide, and agent invariants directly in the Markdown portion of the file** (above `%% # Excalidraw Data %%`).
   - This ensures both human operators and LLM agents reading the file via `read_file` obtain full operational context without needing separate notes or chat history.
7. **Executive Presentation & Anti-"Child-Drawing" Invariant (Design Skills Synthesis)**:
   - **Cross-Skill Synthesis**: Combine `architecture-diagram` (dark slate `#090d16`, semantic 4-color discipline, container hierarchy), `baoyu-infographic` (physical illustrative schematics over empty text blocks — pyrometers, cutaways, chamber stratification, cyclone traps), and `popular-web-designs` (Linear/Vercel pill badges, micro-chips, structured information density).
   - **Vector Schematics over Blank Boxes**: Never leave visual zones as mere bulleted text containers. Draw concrete physical objects (cutaways, instruments, chambers, flow loops, instruments, gradients) using Excalidraw vector primitives (`roughness: 0` for architectural precision).
   - **Avoid Clutter & Micro-Fonts**: Canvas background: Dark slate baseline (`#090d16` or `#121212`) with high-contrast, disciplined semantic palette (max 4 colors: Danger `#ef4444`, Warning `#f97316`, Tech/Brand `#06b6d4`, Success `#10b981`). Strictly no micro-fonts (<14px) or pastel rainbow clutter which look amateurish ("child's drawing").
   - **Sizing**: Generous human-scale card dimensions (440–500px wide, 750–880px high for 9:16 vertical video storyboards; margins 50–60px).
   - **Typography scale**: Titles 24–32px, Subtitles 18–20px, Section Badges 16–18px, Body bullets 14–16px (strictly never drop below 14px for body copy).
   - **Storyboarding structure**: 5-Frame Horizontal Timeline (Hook ➔ Physics ➔ Chaos ➔ Solution ➔ Payoff/CTA) + Full-Width Bottom Comparative Matrix.
   - **Dual-File Sync**: Always generate both `.excalidraw.md` (Obsidian with LZString compressed JSON) and `.excalidraw` (raw JSON) for cross-platform compatibility.
8. **Transclusion & Frame Embedding**: Embed drawings or specific frames inside Markdown notes:
   - Entire drawing: `![[DrawingNote.excalidraw]]`
   - Specific named frame or group: `![[DrawingNote#^frame=ArchitectureOverview]]`
   - Scaled/styled: `![[DrawingNote.excalidraw|600]]`
9. **Live Modal Editing**: Pair with `obsidian-hover-editor` so clicking markdown backlinks or note transclusions inside a canvas opens a full floating editor rather than navigating away from the visual space.
10. **Visual Cohesion & Corner Radius Invariants (`roundness` & Color Tokens)**:
   - **Corner Radius Uniformity**: Never mix `roundness: {"type": 2}` (proportional legacy, dynamic `min(w, h)*0.1`) and `{"type": 3}` (adaptive fixed ~10–12px) across container cards on the same canvas. Standardize all cards, containers, and badges to `roundness: {"type": 3}` to eliminate visual dissonance.
   - **`roughness: 0` Invariant**: Architectural/flow schemas must strictly enforce `roughness: 0` for crisp vector precision (no hand-drawn wobble).
   - **Strict Color Tokens (Linear / Shadcn Dark)**: Never scatter arbitrary hex literals across individual generator functions. Use a centralized `TOKENS` dictionary (`#090d16` canvas, `#0f172a` stages, `#38bdf8` sky, `#c084fc` purple, `#34d399` emerald, `#fbbf24` amber, `#f43f5e` rose).
11. **Dual-Optics Human/Agent Document Specification**: Every formal document created in the vault must adhere to the Master Documentation Standard (see `references/dnk-master-dual-optics-document-standard.md` and `Do not Delete - Example.md`). It pairs human-readable callouts and Excalidraw canvas embeds with machine-parseable frontmatter, task syntax, and invisible HTML agent comments.
12. **Interactive Element-Level Wikilinks (`link: "[[Target]]"`)**:
   - Setting `[[Note Name]]` inside the text body only renders text; it does NOT make cards clickable.
   - To make containers or headers interactive in Obsidian Excalidraw (hover preview, Cmd+Click / Click navigation), set `"link": "[[Target Note]]"` directly on the container's or text's JSON object.
   - When generating or editing via Node.js/Python, decompress the LZ-String `compressed-json` block, inject `link: "[[Target]]"`, and re-compress.
13. **Strict Flat Dark Task Status Design Tokens & Invariants**:
   - Prohibit neon, acid, or rainbow colors on task management boards. Use restrained, disciplined Flat Dark tokens matching Markdown task states:
     - Canvas Background: `#0f1713` (Deep forest charcoal)
     - Backlog (`Planned`): Fill `#141a16`, Stroke `#28362d`, Badge `#94a3b8`
     - In Progress (`In_Progress`): Fill `#1a2014`, Stroke `#3a4420`, Badge `#fde047`
     - Review Gate (`Review`): Fill `#131f24`, Stroke `#224350`, Badge `#38bdf8`
     - Completed (`Completed`): Fill `#13221a`, Stroke `#254837`, Badge `#86efac`
     - Blocked (`Blocked`): Fill `#201416`, Stroke `#422024`, Badge `#f87171`
   - **Font Invariant for Task Boards**: Use `fontFamily: 2` (Normal / Clean Sans-serif / Helvetica-Inter) so Ukrainian and English glyphs render identically with zero text bounding-box overlap or baseline clipping.
14. **SOTA Dark Teal / Slate-Cyan Invariant (Mermaid, Excalidraw & Obsidian Callouts)**:
   - For all technical diagrams, architecture schemas, and callouts, enforce unified Dark Slate-Teal palette:
     - Outer Canvas: `#1e2022` (Charcoal Slate)
     - Card / Node Fill: `#162c2f` (Deep Muted Teal)
     - Header / Subgraph Fill: `#112224` (Darker Slate Teal)
     - 1px Border Stroke: `#224447` (subtle muted teal, `roundness: {"type": 3}`)
     - Title / Link Accent: `#35d5d5` (Aqua / Cyan) with glowing status orb `🟢` (`#22c55e`)
     - Body Text: `#d4d8db` (Clean sans-serif Helvetica/Inter, `fontFamily: 2`)
     - Connectors / Arrows: `#2a6368` with `#35d5d5` arrowheads
   - In Mermaid CSS / Obsidian snippets, target `.node rect` (`fill:#162c2f; stroke:#224447; rx:8px`), `.cluster rect` (`fill:#112224; stroke:#1f3d40`), and link paths (`stroke:#2a6368; marker-end:#35d5d5`).
15. **Obsidian & `zsviczian/kplex` Smart Linking Invariants (`core/obsidian/smart_linker.py`)**:
   - **Typed Semantic Triples**: Use `relation:: [[target#section|alias]]` with ExcaliBrain/kplex directional compass hierarchy: `up` (`parent`, `depends_on`), `down` (`child`, `implements`, `verifies`, `alters`), and `same` (`friend`, `references`).
   - **Unlinked Mention Hygiene**: Always mask existing `[[...]]` wikilink spans before scanning text, enforce alias length `>= 4` chars sorted longest-first, and keep `sota_repo` IDs separate from `module` relative paths so entity registration never collides on `target_dnk_module`.
   - **Bounded K-Hop Subgraph**: Limit local Graph-RAG neighborhood extraction (`get_k_hop_context_subgraph`) to `k_hops=2` and `max_nodes=25` to prevent hub-node explosion on core files like `DEC-012` or `core/kernel.py`.

## Essential Ecosystem Plugins & Roles

| Plugin | Purpose | Integration Method |
| :--- | :--- | :--- |
| **`obsidian-excalidraw-plugin`** | Core vector canvas | Primary drawing surface, text transclusion, handwriting, and custom assets. |
| **`obsidian-excalidraw-extras`** | Heavy computation engine | Encapsulates `MermaidToExcalidraw` (converting Mermaid code blocks to editable shapes) and `MathjaxToSVG` (LaTeX equations). |
| **`excalibrain`** | Structured knowledge graph | TheBrain-style directional navigator using Excalidraw. Organizes notes into Parents (top), Children (bottom), Siblings (left), and Friends (right). Requires `Dataview`. |
| **`blacksmithgu/obsidian-dataview`** | Metadata indexing | Provides semantic metadata querying for ExcaliBrain (`Parent::`, `Child::`). |
| **`nothingislost/obsidian-hover-editor`** | Modal note editing | Transforms popovers into fully functional editors on top of canvases. |

## Automation via EA-Scripts (Script Store)

Excalidraw includes a built-in Script Store (`Excalidraw/Scripts`). Key productivity recipes:
- **Mindmap Builder**: Instant mind mapping via keyboard shortcuts (`Tab` creates child node, `Enter` creates sibling node).
- **Auto Layout**: Automatically organizes tangled freeform nodes into clean hierarchical directed trees (Sugiyama layout algorithm).
- **Text to Sticky Notes**: Automatically splits structured markdown lists or paragraphs into colored canvas sticky notes.
- **Connect Elements**: Generates smart orthogonal elbow connectors between selected shapes that persist across dragging.

## Interactive Vector & Mermaid Canvas Architecture

When embedding interactive vector diagrams (Mermaid, SVG, canvas, Excalidraw embeds) into Obsidian notes:
- **CodeMirror 6 Containment Trap**: `.cm-embed-block` applies `contain: layout paint; overflow: hidden;`. Never use `position: fixed` inside embed blocks; use inline viewport expansion (`calc(100vh - 120px)`) or mount directly to `activeDocument.body`.
- **Bounded Initial Viewport (≤ 500px) & Auto-Fit**: Bounded initial height (≤ 500px) with `preserveAspectRatio="xMidYMid meet"`, `object-fit: contain`, and flexbox centering guarantees tall diagrams fit 100% on first load without bottom clipping.
- **Ergonomics & Interactive Controls (v2.0)**: Smooth mousewheel zoom (3% step), button zoom (±15%), Ghost Mode toolbar (opacity 0.18 -> 1.0 on hover). For Excalidraw embeds, panning suppresses native file navigation clicks when mouse movement >3px. Fullscreen button (`⛶ На все вікно`) expands to `calc(100vh - 120px)`, with Escape key or double-click to Auto-Fit.

## References
- See `references/dnk-master-dual-optics-document-standard.md` for the DNK OS Master Documentation & Architecture Template specification, Dual-Optics human/agent ergonomics, task matrix status symbols, and DAG extraction syntax.
- See `references/excalidraw-visual-cohesion-and-tokens.md` for complete design token specifications, corner radius (`roundness`) invariants, and Python generator templates.
- See `references/excalidraw-and-mermaid-interactive-controls.md` for complete technical specification and UX invariants of the unified Excalidraw and Mermaid interactive toolbar plugin (v2.0).
- See `scripts/excalidraw_builder.py` for reusable SOTA Excalidraw builder supporting dark mode, Cyrillic Excalifont 5, vector primitives, and LZString dual-file generation.
- See `references/sota-excalidraw-design-patterns.md` for unified SOTA Excalidraw design system synthesizing architecture-diagram, baoyu-infographic, and popular-web-designs.
- See `references/excalidraw-viral-storyboard-and-executive-design.md` for anti-child-drawing invariants, generous sizing rules, and 5-frame viral video storyboard specifications.
- See `references/excalidraw-font-and-compression-standards.md` for font family integer mapping (Excalifont `5` vs Virgil `1`), `currentItemFontFamily`, and LZString `compressed-json` recipes.
- See `references/self-documenting-canvas-manifest.md` for the canonical structure, markdown layout, and generation recipe for self-explaining `.excalidraw.md` canvases.
- See `references/zsviczian-ecosystem.md` for full inventory of Zsolt Viczián's PKM tooling and SOTA integration recipes.
- See `references/obsidian-mermaid-dom-containment.md` for CodeMirror 6 containment traps, 500px bounded viewport auto-fit, and interactive zoom/pan architecture.
- See `references/strict-flat-dark-excalidraw-task-templates.md` for strict Flat Dark task status design tokens, interactive element-level wikilink wiring (`link: "[[...]]"`), and Node.js LZ-String update patterns.
- See `references/visual-first-agent-system-spec-pipeline.md` for the ADHD-engineered visual-to-agent pipeline, 3-surface extraction model (Control, Execution, Artifact), Zero-LLM UI testing, and template mapping.
