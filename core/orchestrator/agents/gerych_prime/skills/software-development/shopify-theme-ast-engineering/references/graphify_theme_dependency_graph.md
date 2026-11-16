# Shopify Theme Dependency Graph & Graphify Integration Guide

## Overview
Shopify Online Store 2.0 themes operate as directed acyclic graphs (DAGs). This reference details how to structure and query the theme dependency graph using Graphify to achieve deterministic blast-radius calculation, agent context minimization, and dead-code elimination.

## Graph Schema Mapping for Shopify OS 2.0
| Shopify Concept | Graphify Node Type | Edge Relationship |
|---|---|---|
| `templates/*.json` | `template` | `includes_section` -> `section` |
| `sections/*.liquid` | `section` | `renders_snippet` -> `snippet`, `contains_block` -> `block` |
| `snippets/*.liquid` | `snippet` | `renders_snippet` -> `snippet` |
| `blocks/*.liquid` | `block` | `renders_snippet` -> `snippet` |
| `config/settings_schema.json` | `config` | `configures` -> `section`, `snippet` |
| Theme App Extension | `extension` | `injects_block` -> `template` |

## Exporting Theme Dependencies to Graphify Format
Use `ThemeIntelligence` (`services/dnk_shopify/src/theme_intel.py`) to build the raw nodes and edges:

```python
from services.dnk_shopify.src.theme_intel import ThemeIntelligence

intel = ThemeIntelligence("services/dnk_shopify/DNK-e.com")
graph = intel.build_dependency_graph()
# graph contains:
# - nodes: list of component file paths
# - edges: [{'from': str, 'to': str, 'type': 'render' | 'section'}]
```

Export nodes and edges into Graphify-compliant JSON (`graph.json`):
```json
{
  "nodes": [
    {"id": "snippets/price.liquid", "label": "price.liquid", "type": "snippet"},
    {"id": "sections/main-product.liquid", "label": "main-product.liquid", "type": "section"},
    {"id": "templates/product.json", "label": "product.json", "type": "template"}
  ],
  "edges": [
    {"source": "sections/main-product.liquid", "target": "snippets/price.liquid", "relation": "render"},
    {"source": "templates/product.json", "target": "sections/main-product.liquid", "relation": "include"}
  ]
}
```

## Essential Graphify Workflows for Theme Development

### 1. Blast Radius Inspection Before Editing
Before mutating any snippet or section:
```bash
graphify affected "snippets/price.liquid"
```
Output reveals all sections, templates, and presets that depend directly or transitively on this snippet.

### 2. Context Subgraph Extraction for LLM Agents
Instead of feeding hundreds of theme files to `dnk_shopify`:
```bash
graphify path "templates/product.json" "snippets/buy-buttons.liquid"
```
Feeds only the exact execution chain files into the agent prompt, cutting token overhead by up to 90%.

### 3. Detecting Dead Snippets & Blocks (Tree-Shaking)
Query nodes with zero incoming edges (in-degree = 0) that are not entrypoint templates:
```bash
graphify query --in-degree 0 --type snippet
```
Identifies abandoned snippets that can be safely deleted to optimize theme bundle size and Time To First Byte (TTFB).
