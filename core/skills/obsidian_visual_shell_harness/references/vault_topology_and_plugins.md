<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/obsidian_visual_shell_harness/references/vault_topology_and_plugins.md"
# purpose: "Complete reference for Obsidian Vault Topology, Config Semantics, and the 11 Community Plugins."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🗺️ Obsidian Vault Topology & 11-Plugin Ecosystem

This reference details the file hierarchy, configuration contracts, and functional responsibilities of the 11 community plugins powering the DNK OS Visual Shell.

---

## 📂 Vault Topology

```
DNK_HUB/
├── .obsidian/                     # Obsidian runtime configurations
│   ├── app.json                   # Core editor behaviors (links, line lengths)
│   ├── appearance.json            # Active theme & enabled CSS snippets
│   ├── community-plugins.json     # List of active community plugins
│   ├── core-plugins.json          # Native Obsidian core plugins
│   ├── plugins/                   # 11 Community Plugins with data.json state
│   └── snippets/                  # Custom CSS stylesheets
│       ├── dnk-flat-green.css
│       ├── full-width-view.css
│       └── shopify-polaris-helix.css
├── docs/
│   └── notes/                     # Spatial PKM SSOT
│       ├── 00_MOC_DNK_OS.md       # Master Map of Content
│       ├── my Notes.md            # Founder scratchpad & vision
│       ├── my Notes.excalidraw.md # Spatial architecture canvas
│       ├── Excalidraw/            # Dedicated drawings folder
│       └── whiteboards/           # Canonical template canvases
```

---

## 🧩 The 11 Community Plugins

| Plugin ID | Name | Version | Role in DNK OS |
| :--- | :--- | :--- | :--- |
| `obsidian-excalidraw-plugin` | **Obsidian Excalidraw** | `2.8.0` | Primary spatial infinite canvas; supports compressed JSON embedding in markdown, transclusion, image/SVG import, and live pen/shape drafting. |
| `k-plex` | **Knowledge Plex** | `0.1.3` | SOTA visual knowledge outliner and relational graph navigator developed by Zsolt Viczian; enforces ontology hierarchies and lateral links. |
| `excalibrain` | **ExcaliBrain** | `0.2.14` | Interactive visual concept network generated directly from page frontmatter and bidirectional links. |
| `excalidraw-extras` | **Excalidraw Extras** | `1.0.0` | Helper toolset adding enhanced drawing controls, frames, and sticky-note utilities. |
| `dataview` | **Dataview** | `0.5.67` | Real-time JavaScript and SQL-like metadata query engine over markdown frontmatter (`status`, `updated_at`, `purpose`). |
| `obsidian-hover-editor` | **Hover Editor** | `0.11.23` | Converts transient hover popovers into fully functional, dockable, interactive note editors. |
| `mermaid-interactive-zoom` | **Mermaid Zoom** | `1.0.4` | Adds interactive pan, zoom, drag, and reset controls to rendered Mermaid sequence/flowchart blocks. |
| `obsidian-local-rest-api` | **Local REST API / MCP**| `5.1.0` | REST API (port `27123`/`27124`) and Model Context Protocol bridge for headless agent commands and file mutations. |
| `obsidian42-strange-new-worlds` | **Strange New Worlds** | `2.4.2` | Contextual reference discovery displaying inline link counter badges across headings and blocks. |
| `quickadd` | **QuickAdd** | `1.11.9` | High-velocity capture macros, template expansion, and atomic node inception. |
| `remotely-save` | **Remotely Save** | `0.5.2` | Multi-device encrypted synchronization supporting S3, WebDAV, Dropbox, and OneDrive. |

---

## ⚙️ Configuration Contracts

### `community-plugins.json`
Specifies which plugins Obsidian automatically initializes upon boot:
```json
[
  "mermaid-interactive-zoom",
  "obsidian-excalidraw-plugin",
  "dataview",
  "excalibrain",
  "excalidraw-extras",
  "obsidian-hover-editor",
  "quickadd",
  "obsidian-local-rest-api",
  "obsidian42-strange-new-worlds",
  "remotely-save",
  "k-plex"
]
```

### `appearance.json`
Guarantees design token activation:
```json
{
  "enabledCssSnippets": [
    "full-width-view",
    "shopify-polaris-helix",
    "dnk-flat-green"
  ]
}
```

### `app.json`
Ensures non-destructive edits and consistent link resolution:
```json
{
  "promptDelete": false,
  "readableLineLength": false,
  "alwaysUpdateLinks": true
}
```
