---
name: obsidian-excalidraw
description: "Create Obsidian Excalidraw drawings and JSON Canvas graphs."
version: 1.0.0
author: Gerych Prime & Maxim
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Excalidraw, Visual-PKM, ExcaliBrain, JSON-Canvas, Zsolt-Viczian]
    related_skills: [obsidian, obsidian-task-forest, excalidraw]
---

# Obsidian Excalidraw & Visual PKM Skill

Complete workflow and generator toolkit for integrating Obsidian with Excalidraw (`obsidian-excalidraw-plugin` by Zsolt Viczián) and JSON Canvas (`obsidianmd/jsoncanvas`).

## When to Use

Use this skill when:
- Creating or editing visual diagrams, system architecture charts, flowcharts, or mind maps in Obsidian.
- Generating hybrid `.excalidraw.md` files with interactive Obsidian `[[wikilinks]]`.
- Creating infinite spatial boards with `.canvas` (JSON Canvas) linking notes, markdown files, and groups.
- Integrating agent research, task forest dependencies, or architectural blueprints into visual Obsidian artifacts.

## Core Concepts & Ecosystem (SSOT)

1. **Hybrid `.excalidraw.md` Format**:
   - Stores visual drawing and markdown metadata in a single file.
   - Frontmatter tag: `excalidraw-plugin: parsed`, `tags: [excalidraw]`.
   - Drawing data is stored inside a markdown comment block `%% # Excalidraw Data ... %%` containing a ```json ... ``` block.
   - Fully compatible with Obsidian search, Dataview queries, graph view, and backlinks!

2. **Bidirectional Linking & Transclusion**:
   - Any shape or text in Excalidraw can have a `link: "[[Note Name]]"` or `link: "[[Note Name#^block]]"`.
   - Clicking with `Cmd/Ctrl` navigates directly to that Obsidian note.
   - Excalidraw drawings can be transcluded into normal markdown notes: `![[Drawing.excalidraw]]` or `![[Drawing.excalidraw.svg]]`.
   - Specific frames can be embedded: `![[Drawing.excalidraw#^frameId]]`.

3. **ExcaliBrain Concept Mapping (Ontology)**:
   - Hierarchical visual relationship model:
     - **Parent (Ontology / Super-concept)**: Pointing upstream (`up: [[Parent]]`).
     - **Child (Components / Slices)**: Downstream breakdown.
     - **Friend (Associative link)**: Lateral relationships.
     - **Sibling**: Elements sharing the same parent.

4. **JSON Canvas (`.canvas`)**:
   - Native infinite spatial whiteboard standard by Obsidian (`jsoncanvas.org`).
   - Pure JSON schema with `nodes` (type: `text`, `file`, `link`, `group`) and `edges` (fromNode, toNode, label, color).

---

## File Formats

### 1. Hybrid `.excalidraw.md` File Structure

```markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data
## Text Elements
%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [
    {
      "id": "box1",
      "type": "rectangle",
      "x": 100,
      "y": 100,
      "width": 240,
      "height": 100,
      "strokeColor": "#1971c2",
      "backgroundColor": "#e7f5ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 1,
      "opacity": 100,
      "roundness": { "type": 3 },
      "link": "[[System Architecture]]",
      "boundElements": [{ "id": "txt1", "type": "text" }]
    },
    {
      "id": "txt1",
      "type": "text",
      "x": 110,
      "y": 135,
      "width": 220,
      "height": 30,
      "text": "System Architecture",
      "originalText": "System Architecture",
      "fontSize": 18,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "box1",
      "autoResize": true
    }
  ],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```
%%
```

### 2. Obsidian JSON Canvas (`.canvas`) File Structure

```json
{
  "nodes": [
    {
      "id": "node-1",
      "type": "text",
      "text": "## Core Engine\nFastAPI + TaskDAG orchestrator",
      "x": 100,
      "y": 100,
      "width": 300,
      "height": 180,
      "color": "1"
    },
    {
      "id": "node-2",
      "type": "file",
      "file": "013 Architecture Map.md",
      "x": 500,
      "y": 100,
      "width": 350,
      "height": 400
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "node-1",
      "fromSide": "right",
      "toNode": "node-2",
      "toSide": "left",
      "label": "documents"
    }
  ]
}
```

---

## Programmatic Utilities

Use the built-in python generators in `scripts/`:
- `scripts/generate_excalidraw.py`: Generates valid `.excalidraw.md` notes with shapes, text bindings, arrows, and `[[wikilinks]]`.
- `scripts/generate_canvas.py`: Generates valid `.canvas` files for spatial brainstorming.
