---
name: "obsidian_visual_shell_harness"
description: "Comprehensive harness and automation standard for Obsidian as the DNK OS Visual Shell: 11-plugin spatial stack, Excalidraw canvas, K-Plex ontology, Local REST API bridge, and dual-vault parity."
version: "1.0.0"
category: "architecture"
author: "DNK-e.com Maksym & Antigravity"
assimilated_at: "2026-10-26"
license: "Proprietary DNK OS"
target_worker: "gerych_builder"
---

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/obsidian_visual_shell_harness/SKILL.md"
# purpose: "Canonical DNK OS Skill for Obsidian Visual Shell Harness, Spatial PKM, 11-Plugin Stack, and Agent Automation."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 🧠 Obsidian Visual Shell Harness (DNK OS Spatial PKM)

This skill operationalizes **Obsidian** as the native spatial visualization, knowledge graph, and interactive canvas layer ("Visual Shell") for **DNK OS**. It guarantees zero split-brain, headless agent programmatic control, and seamless spatial thinking through an aligned 11-plugin ecosystem.

---

## 🏛️ Architectural Foundations

```
                    ┌──────────────────────────────────────────────┐
                    │          DNK OS Agent Swarm (Hermes)         │
                    │   (Antigravity, Gerych Prime, DevFullstack)  │
                    └──────────────────────┬───────────────────────┘
                                           │ FastMCP / REST (27123)
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      Obsidian Local REST API & MCP Bridge    │
                    │      (Auth: Bearer Token, Crypto Handshake)   │
                    └──────┬───────────────────────┬───────────────┘
                           │                       │
         ┌─────────────────▼────────┐    ┌─────────▼─────────────────┐
         │ Spatial & Visual Engine  │    │ Knowledge Graph Engine    │
         │ - Excalidraw Canvas      │    │ - K-Plex Relational Graph │
         │ - Excalibrain Network    │    │ - Strange New Worlds      │
         │ - Hover Editor Popovers  │    │ - Dataview Queries        │
         └──────────────────────────┘    └───────────────────────────┘
                           │                       │
                           └───────────┬───────────┘
                                       ▼
                    ┌──────────────────────────────────────────────┐
                    │       DNK OS Design System (CSS Snippets)    │
                    │   dnk-flat-green | shopify-polaris | full-width│
                    └──────────────────────────────────────────────┘
```

---

## 📁 Level-of-Detail (LOD) Reference Map

For in-depth specifications, consult the dedicated references:
- **Topology & Plugin Roster**: [`references/vault_topology_and_plugins.md`](./references/vault_topology_and_plugins.md)
- **Agent Programmatic Control**: [`references/agent_control_rest_api.md`](./references/agent_control_rest_api.md)
- **CSS Design System & Tokens**: [`references/css_design_system_and_styling.md`](./references/css_design_system_and_styling.md)
- **Runtime Lifecycle & Debugging**: [`references/runtime_lifecycle_and_troubleshooting.md`](./references/runtime_lifecycle_and_troubleshooting.md)
- **Canonical Architecture Spec**: [`docs/architecture/OBSIDIAN_VISUAL_SHELL_HARNESS_SPEC.md`](file:///Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_HUB/docs/architecture/OBSIDIAN_VISUAL_SHELL_HARNESS_SPEC.md)

---

## ⚡ Mandatory Invariants

1. **Monorepo Vault SSOT Invariant**:
   `DNK_HUB` is the primary and authoritative vault. Standalone builds (`DNK_OS_APP`) receive strictly mirrored `.obsidian/` configurations and identical drawings via `scripts/export_standalone_app.py`.
2. **Canonical 8-Root Directory Invariant**:
   All user notes, whiteboards, and Excalidraw scenes live strictly inside `docs/notes/` (`docs/notes/whiteboards/`, `docs/notes/Excalidraw/`). Never create new top-level directories in the repository root.
3. **Electron Runtime Memory Barrier**:
   Obsidian caches community plugins and CSS in memory on startup. When syncing plugins via scripts or git, you MUST trigger `app:reload` via REST API or restart Obsidian (`open -a Obsidian`) before expecting visual changes to take effect.
4. **Markdown-First Excalidraw Standard**:
   All drawings must maintain frontmatter:
   ```yaml
   ---
   excalidraw-plugin: parsed
   tags: [excalidraw]
   ---
   ```
   This ensures drawings remain human-readable and git-diffable Markdown.

---

## 🧪 Quick Recipes (High-Velocity Execution)

### Recipe 1: Programmatic View Switch & Reload via CLI
```bash
# Set Local REST API Token
REST_API_KEY="1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f"

# 1. Reload entire Obsidian UI without saving (hot-reload plugins)
curl -s -X POST -H "Authorization: Bearer $REST_API_KEY" \
  http://127.0.0.1:27123/commands/app:reload/

# 2. Open any Excalidraw note in active tab
curl -s -X POST -H "Authorization: Bearer $REST_API_KEY" \
  "http://127.0.0.1:27123/open/docs/notes/my%20Notes.excalidraw.md"
```

### Recipe 2: Python Client for Agent Manipulation
```python
import urllib.request
import json

def open_obsidian_drawing(file_path: str, api_key: str = "1dc2362c168969e165c56a216137db69788189bb9dfc5e1071d3025ded21a42f"):
    url = f"http://127.0.0.1:27123/open/{urllib.parse.quote(file_path)}"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req) as resp:
        return resp.status == 200
```

### Recipe 3: K-Plex Semantic Ontology Triggers
When writing notes inside Obsidian, use native K-Plex syntax for zero-friction graph mapping:
- `::p` -> Defines a **Parent** relation (e.g. `System One ::p DNK OS Architecture`)
- `::c` -> Defines a **Child** relation (e.g. `Kernel Engine ::c Microkernel`)
- `::f` -> Defines a **Left Friend** (support / alternative)
- `::r` -> Defines a **Right Friend** (challenger / opposing)
- `::s` -> Defines a **Previous** step
- `::n` -> Defines a **Next** step

### Recipe 4: Verifying Vault Parity
Run the verification check to validate that `DNK_HUB` and `DNK_OS_APP` have synchronized configurations:
```bash
python3 -c "
import json
with open('.obsidian/community-plugins.json') as f1, open('../DNK_OS_APP/.obsidian/community-plugins.json') as f2:
    assert json.load(f1) == json.load(f2), 'Plugins diverged!'
print('✅ Dual-Vault Parity Verified!')
"
```
