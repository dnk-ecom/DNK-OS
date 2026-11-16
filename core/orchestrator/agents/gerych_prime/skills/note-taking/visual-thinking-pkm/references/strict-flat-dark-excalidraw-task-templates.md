<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/visual-thinking-pkm/references/strict-flat-dark-excalidraw-task-templates.md"
purpose: "Specification for Strict Flat Dark Task Management Boards, Interactive Wikilink Wiring, and Node.js LZ-String Manipulation."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-09-19"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Strict Flat Dark Task Canvases & Interactive Wikilinks Specification

This reference codifies the production standard for creating high-discipline, executive-grade task boards in Obsidian Excalidraw, eliminating color noise and ensuring 100% interactive bi-directional linking.

---

## 1. SOTA Dark Teal / Slate-Cyan Design Tokens (Mermaid, Excalidraw & Callouts)

To prevent visual fatigue, eliminate childish rainbow diagrams, and ensure visual unity between **Mermaid diagrams, Excalidraw boards, and Obsidian Callouts**, the canonical design system uses a restrained **Dark Slate-Teal / Cyan** aesthetic:

| Role / Element | Hex Token | Visual Semantic |
| :--- | :--- | :--- |
| **Canvas / Background** | `#1e2022` | Deep Charcoal Slate — calm non-fatiguing backdrop |
| **Card / Box Fill** | `#162c2f` | Deep Muted Teal — containers, nodes, callout body |
| **Header Strip / Subgraph** | `#112224` | Darker Slate Teal — card headers, cluster frames |
| **Border / Stroke (1px)** | `#224447` | Subtle muted teal border, `roundness: {"type": 3}` / 8–10px |
| **Primary Accent / Titles** | `#35d5d5` | Aqua / Cyan — bold headers, link highlights, arrow tips |
| **Status Orb** | `🟢` / `#22c55e` | Glowing emerald status orb next to title |
| **Body Text** | `#d4d8db` | Clean light gray text (`fontFamily: 2` Inter/Helvetica) |
| **Connectors & Arrows** | `#2a6368` | Muted teal connection lines with `#35d5d5` tips |

### Task State Variations (Subtle Accent Tinting)

| Task State | Frontmatter `status` | Container Fill | Stroke (1.5px) | Header Strip | Badge / Accent Hex |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **📋 Backlog** | `Planned` | `#162c2f` | `#224447` | `#112224` | `#94a3b8` (Slate Muted) |
| **🟡 In Progress** | `In_Progress` | `#1c2a20` | `#2d4734` | `#142218` | `#fde047` (Warm Amber Muted) |
| **🟣 Audit Gate** | `Review` | `#182330` | `#243f55` | `#121b24` | `#38bdf8` (Muted Cyan) |
| **🟢 Completed** | `Completed` | `#162c2f` | `#224447` | `#112224` | `#35d5d5` (Aqua Mint SOTA) |
| **🔴 Blocked** | `Blocked` | `#261a1e` | `#4a222a` | `#1c1216` | `#f87171` (Muted Rose) |

### Layout & Card Structure Invariants
- **Dimensions**: Cards are standardized to `width: 320–360px`, `height: 220–260px` with 30–40px horizontal and vertical gutters.
- **Header Strip**: Separate rectangle (`height: 36–42px`) docked at top of the card with `roundness: {"type": 3}` and darker tint.
- **Card Body Text**: `#f1f5f9` (Slate-100), `fontSize: 12–13px`, line height 1.35.
- **Card Badges & Chips**: Pill badges inside cards use subtle fills (`rgba` or dark tone) and status-colored border.
- **Roughness**: Strictly `roughness: 0` for all cards, borders, connectors, and badges.

---

## 2. Interactive Wikilink Wiring (`link: "[[Target]]"`)

In Obsidian Excalidraw, placing `[[Note Name]]` inside the raw text string only renders a visual label. It does **NOT** make the surrounding card or container clickable.

### The Mandatory Linking Invariant:
For an element (card container or text title) to act as a native Obsidian hyperlink:
1. The element JSON object **must** have:
   ```json
   "link": "[[Target Note Name]]"
   ```
2. When the user hovers over the element in Obsidian, a tooltip with the destination note appears.
3. Clicking (or `Cmd/Ctrl + Click` depending on settings) navigates directly to that note or opens an `obsidian-hover-editor` modal.
4. **Target Whitelist**: Always link to real canonical specs, MOC notes, or active task nodes (e.g. `[[00_MOC_DNK_OS]]`, `[[specs/04_TASK_FOREST_DAG_SPEC]]`).

---

## 3. Programmatic Update of Compressed Excalidraw Canvases

Obsidian Excalidraw stores the drawing JSON in a base64-encoded LZ-String block:

````markdown
# Excalidraw Data
## Text Elements
...
%%
# Drawing
```compressed-json
<Base64-LZString-Payload>
```
%%
````

### Decompress-Modify-Compress Workflow (Node.js)

```javascript
const fs = require('fs');
const LZString = require('lz-string');

function updateExcalidrawFile(filePath, mutatorFn) {
  const content = fs.readFileSync(filePath, 'utf8');
  const startMarker = '```compressed-json\n';
  const endMarker = '\n```';
  
  const startIndex = content.indexOf(startMarker);
  const endIndex = content.indexOf(endMarker, startIndex);
  if (startIndex === -1 || endIndex === -1) {
    throw new Error('No compressed-json block found');
  }

  const base64Data = content.substring(startIndex + startMarker.length, endIndex).trim();
  const jsonStr = LZString.decompressFromBase64(base64Data);
  const data = JSON.parse(jsonStr);

  // Apply mutations (e.g. set element.link, update colors, set fontFamily: 2)
  mutatorFn(data);

  const updatedJsonStr = JSON.stringify(data);
  const newBase64Data = LZString.compressToBase64(updatedJsonStr);

  const newContent = content.substring(0, startIndex + startMarker.length) +
                     newBase64Data +
                     content.substring(endIndex);

  fs.writeFileSync(filePath, newContent, 'utf8');
}
```

### Text Element Synchronization
Always keep the readable `## Text Elements` section in sync with `data.elements.filter(e => e.type === "text")`. This guarantees Obsidian backlink search, fuzzy title searching, and graph view indexing function seamlessly.

---

## 4. Typography Discipline: Cyrillic / Latin Parity (`fontFamily: 2`)

- For technical boards, task templates, and architecture cards with mixed Ukrainian and English text, **`fontFamily: 2` (Normal / Clean Sans-serif / Helvetica-Inter)** is mandatory.
- It prevents letter-spacing anomalies, missing glyph fallbacks, and label bounding-box miscalculations that occur with handwriting fonts (`fontFamily: 1`).
- Heading text: `fontSize: 15–16px`, bold accent color.
- Metadata rows (Assignee, Complexity C, MASE Slice): `fontSize: 11–12px`, muted `#94a3b8`.
