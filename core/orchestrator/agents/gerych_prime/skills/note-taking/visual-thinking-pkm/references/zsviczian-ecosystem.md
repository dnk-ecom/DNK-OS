# Zsolt Viczián (`zsviczian`) Visual PKM & Excalidraw Tooling Inventory

Author: Zsolt Viczián (Principal developer of Obsidian Excalidraw, ExcaliBrain, and Visual PKM ecosystem).

## Core Repositories & Architecture

### 1. `obsidian-excalidraw-plugin` (GitHub: `zsviczian/obsidian-excalidraw-plugin`)
- **Stars**: ~7,580
- **Purpose**: Primary Excalidraw integration for Obsidian.md.
- **Key Features**:
  - Treats `.excalidraw.md` as dual-nature files (Markdown text element indexing + vector canvas data).
  - Supports Markdown transclusion (`![[Note]]` rendered inside shapes).
  - Backlinks and block references (`^blockAnchor`) attached to visual elements.
  - Script Store automation interface (`ExcalidrawAutomate`).
  - Supports customizable icon/sticker libraries (`.excalidrawlib`).

### 2. `excalibrain` (GitHub: `zsviczian/excalibrain`)
- **Stars**: ~1,000
- **Purpose**: An interactive visual knowledge graph navigating Obsidian vaults, inspired by TheBrain.
- **Navigation Topology**:
  - **Top (Parents)**: High-level concepts, categories, or MOCs (Maps of Content).
  - **Bottom (Children)**: Subtopics, specific implementation files, breakdown tasks.
  - **Left (Siblings)**: Parallel topics sharing the same parent.
  - **Right (Friends)**: Associative or cross-domain links.
- **Dependencies**: Requires `obsidian-dataview` for relation indexing.

### 3. `obsidian-excalidraw-extras` (GitHub: `zsviczian/obsidian-excalidraw-extras`)
- **Purpose**: Modular companion plugin isolating heavyweight dependencies and high-privilege operations:
  - `MermaidToExcalidraw`: Native parsing of Mermaid syntax into editable vector Excalidraw elements.
  - `MathjaxToSVG`: Rendering mathematical and scientific formulas.
  - High-privilege IPC and filesystem calls for PDF export/printing.

### 4. `ea-scripts` (GitHub: `zsviczian/ea-scripts`)
- **Purpose**: Collection of user-facing automation scripts accessible via Excalidraw Script Store:
  - `Mindmap Builder`: Instant keyboard-driven node branching.
  - `Auto Layout`: Graph hierarchy solver using Sugiyama algorithms.
  - `Convert text elements to sticky notes`: Batch transformer for text outlines.
  - `Connect elements`: Orthogonal connector routing.

### 5. `KPlex` (GitHub: `zsviczian/kplex`) & Kernel Smart Linking Architecture
- **Purpose**: Semantic knowledge plexus combining Obsidian bi-directional wikilinks, ExcaliBrain 4-way directional compass hierarchy, and TheBrain interaction models directly into an integrated canvas and microkernel graph engine.
- **DNK OS Kernel Implementation (`core/obsidian/smart_linker.py`)**:
  1. **Typed Semantic Triples (`KPLEX_RELATION_ONTOLOGY`)**:
     - Inline Dataview/ExcaliBrain syntax: `relation:: [[target#section|alias]]`.
     - Directional compass mapping:
       - `up` (`↑` Parents / Prerequisites): `parent`, `depends_on`, `derived_from`.
       - `down` (`↓` Children / Implementations): `child`, `implements`, `verifies`, `alters`.
       - `same` (`↔` Friends / Peers): `friend`, `references`, `related_to`, `contradicts`.
  2. **Bi-Directional Wikilink & Backlink Indexing**:
     - Regex extraction of `(!?)\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]` plus optional `([a-zA-Z0-9_-]+)::\s*` prefix.
     - Automatically builds a reverse `backlinks_index` so every architectural decision (`DEC-012`, `DEC-008`) and module knows all incoming thoughts and tests.
  3. **Unlinked Mention Discovery & Auto-Linking (`discover_unlinked_mentions`)**:
     - Masks existing `[[...]]` spans before scanning raw text so already-linked entities are never double-wrapped.
     - Enforces an alias minimum length threshold (`>= 4` chars) and sorts candidate aliases longest-first to avoid false-positive collisions on short tokens.
     - Assigns distinct `entity_id` namespaces for SOTA repositories vs. local file modules (e.g., `repo.id` vs. `module.relative_path`) to prevent registry overwrite collisions when a blueprint points to `target_dnk_module`.
  4. **Bounded K-Hop Graph-RAG Subgraph (`get_k_hop_context_subgraph`)**:
     - Breadth-first traversal (`k_hops=2`, capped at `max_nodes=25`, `k_hops <= 4`) across both outgoing and incoming semantic edges to assemble compact context capsules without hub-node explosion.

### 6. `obsidian42-strange-new-worlds` (SNW)
- **Purpose**: Displays inline counts of bi-directional linkages next to headers, links, and blocks, revealing connection density across the vault.
