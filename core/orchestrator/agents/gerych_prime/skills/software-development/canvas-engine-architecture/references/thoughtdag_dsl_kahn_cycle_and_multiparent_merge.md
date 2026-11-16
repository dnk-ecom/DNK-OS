# ThoughtDAG 2.0 DSL, Kahn Cycle Detection & Multi-Parent Context Merging

## 1. Overview & Clean-Room Architecture
ThoughtDAG enables graph-based multi-agent deliberation on an infinite canvas where edges ("Context Wires") route state, prompts, and context.
Core modules in DNK OS:
- `core/domain/dag_models.py`: Pydantic SSOT graph models (`ThoughtDAGGraph`, `ThoughtNode`, `Wire`).
- `core/domain/thought_dsl.py`: Clean-room DSL parser, Kahn's cycle gate, and multi-parent topological context merger.
- `apps/api/routers/thoughtdag_router.py`: FastAPI endpoints for AST DSL compilation, export, and context compilation.
- `apps/web/components/canvas/edges/ContextWireEdge.tsx`: React Flow / XYFlow custom context wire edge.

---

## 2. Thought DSL Syntax Specification
```text
[hypothesis] H1: Monolith Migration
Evaluate moving from serverless to monolith for low latency.

[hypothesis] H2: Micro-frontend Isolation
Split frontend into isolated bundle domains.

[critique] C1: Team overhead risk
Addresses risk of coordination complexity across boundaries.

[synthesis] S1: Hybrid Core with Islands
H1 -> C1 : evaluates
H2 -> C1
C1 -> S1 : synthesizes
```

### Supported Token Tags
- `[hypothesis]` (maps to `NodeKind.NOTE` with `thought_type="hypothesis"`)
- `[critique]` (maps to `NodeKind.NOTE` with `thought_type="critique"`)
- `[synthesis]` (maps to `NodeKind.NOTE` with `thought_type="synthesis"`)
- `[decision]` (maps to `NodeKind.NOTE` with `thought_type="decision"`)
- `[question]` (maps to `NodeKind.NOTE` with `thought_type="question"`)
- `[observation]` (maps to `NodeKind.NOTE` with `thought_type="observation"`)
- `[action]` (maps to `NodeKind.AGENT_TASK` with `thought_type="action"`)

---

## 3. Kahn's Cycle Detection Algorithm
To prevent infinite context aggregation loops, any edge mutation or parsed DSL is validated via Kahn's algorithm:

```python
def validate_dag_kahn(graph: ThoughtDAGGraph) -> Tuple[bool, List[str]]:
    # In-degree computation
    in_degree = {nid: 0 for nid in graph.nodes}
    adj = {nid: [] for nid in graph.nodes}
    for wire in graph.wires:
        if wire.from_node in in_degree and wire.to_node in in_degree:
            adj[wire.from_node].append(wire.to_node)
            in_degree[wire.to_node] += 1

    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    topo_order = []
    while queue:
        curr = queue.pop(0)
        topo_order.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(topo_order) == len(graph.nodes):
        return True, topo_order
    # If len differs, nodes with in_degree > 0 are part of cycles
    cycle_nodes = [nid for nid, deg in in_degree.items() if deg > 0]
    return False, cycle_nodes
```

---

## 4. Multi-Parent Context Merging & Deduplication
When synthesizing conclusions from multiple independent parents (e.g. $H_1, H_2 \to S_1$), naive recursive traversal duplicates shared ancestors.
`merge_multi_parent_context` resolves this:
1. Traverses BFS/DFS upwards to collect all ancestors.
2. Orders ancestors topologically according to Kahn's sorted sequence.
3. Deduplicates common ancestors so shared premises appear exactly once.
4. Computes deterministic SHA-256 `upstream_fingerprint`.
5. Formats structured prompt sections:
   - `### Ancestor Context (Topologically Ordered & Deduplicated)`
   - `### Direct Upstream Influences`
   - `### Synthesis Objective`

---

## 5. API Endpoints
- `POST /api/v1/thoughtdag/dsl/parse` -> returns `{ graph: ThoughtDAGGraph, has_cycles: bool, cycle_nodes: [...] }`
- `POST /api/v1/thoughtdag/dsl/export` -> returns `{ dsl_text: str }`
- `POST /api/v1/thoughtdag/merge` -> returns `MultiParentMergeResult` with deduplicated context and fingerprint.
