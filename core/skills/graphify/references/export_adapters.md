### Step 6b - Wiki (only if --wiki flag)

**Only run this step if `--wiki` was explicitly given in the original command.**

Run this before Step 9 (cleanup) so `.graphify_labels.json` is still available.

```bash
$(cat graphify-out/.graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.wiki import to_wiki
from graphify.analyze import god_nodes
from pathlib import Path

extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('graphify-out/.graphify_labels.json').read_text()) if Path('graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
gods = god_nodes(G)

n = to_wiki(G, communities, 'graphify-out/wiki', community_labels=labels or None, cohesion=cohesion, god_nodes_data=gods)
print(f'Wiki: {n} articles written to graphify-out/wiki/')
print('  graphify-out/wiki/index.md  ->  agent entry point')
"
```

### Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag)

**If `--neo4j`** - generate a Cypher file for manual import:

```bash
$(cat graphify-out/.graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.export import to_cypher
from pathlib import Path

G = build_from_json(json.loads(Path('graphify-out/.graphify_extract.json').read_text()))
to_cypher(G, 'graphify-out/cypher.txt')
print('cypher.txt written - import with: cypher-shell < graphify-out/cypher.txt')
"
```

**If `--neo4j-push <uri>`** - push directly to a running Neo4j instance. Ask the user for credentials if not provided:

```bash
$(cat graphify-out/.graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.cluster import cluster
from graphify.export import push_to_neo4j
from pathlib import Path

extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}

result = push_to_neo4j(G, uri='NEO4J_URI', user='NEO4J_USER', password='NEO4J_PASSWORD', communities=communities)
print(f'Pushed to Neo4j: {result[\"nodes\"]} nodes, {result[\"edges\"]} edges')
"
```

Replace `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` with actual values. Default URI is `bolt://localhost:7687`, default user is `neo4j`. Uses MERGE - safe to re-run without creating duplicates.

### Step 7b - SVG export (only if --svg flag)

```bash
$(cat graphify-out/.graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.export import to_svg
from pathlib import Path

extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('graphify-out/.graphify_labels.json').read_text()) if Path('graphify-out/.graphify_labels.json').exists() else {}

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
labels = {int(k): v for k, v in labels_raw.items()}

to_svg(G, communities, 'graphify-out/graph.svg', community_labels=labels or None)
print('graph.svg written - embeds in Obsidian, Notion, GitHub READMEs')
"
```

### Step 7c - GraphML export (only if --graphml flag)

```bash
$(cat graphify-out/.graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_graphml
from pathlib import Path

extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text())
analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text())

G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}

to_graphml(G, communities, 'graphify-out/graph.graphml')
print('graph.graphml written - open in Gephi, yEd, or any GraphML tool')
"
```

### Step 7d - MCP server (only if --mcp flag)

```bash
python3 -m graphify.serve graphify-out/graph.json
```

This starts a stdio MCP server that exposes tools: `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`. Add to Claude Desktop or any MCP-compatible agent orchestrator so other agents can query the graph live.

To configure in Claude Desktop, add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "graphify": {
      "command": "python3",
      "args": ["-m", "graphify.serve", "/absolute/path/to/graphify-out/graph.json"]
    }
  }
}
```

