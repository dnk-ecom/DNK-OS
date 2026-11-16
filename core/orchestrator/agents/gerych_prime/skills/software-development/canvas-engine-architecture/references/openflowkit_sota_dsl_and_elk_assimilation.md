<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/openflowkit_sota_dsl_and_elk_assimilation.md"
purpose: "SOTA assimilation patterns from Vrun-design/openflowkit: OpenFlow DSL v2, ELK.js worker layout, and MCP canvas tool contracts."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-19"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# OpenFlowKit SOTA Assimilation: DSL v2, ELK.js Worker Layout & Agentic MCP Contracts

## 1. Executive Summary & Stack Profile
- **Repository**: `Vrun-design/openflowkit` (MIT License)
- **Core Engine**: `@xyflow/react` v12, React 19, Tailwind CSS v4, Lucide Icons, ELK.js
- **Key Innovations**:
  1. **OpenFlow DSL v2**: Human-readable, LLM-optimized Diagram-as-Code grammar (80% token reduction vs raw React Flow JSON).
  2. **ELK.js Web Worker Layout**: Multi-threaded non-blocking layout calculations supporting layered, hierarchical, and anchored layouts.
  3. **Canvas MCP Server**: Model Context Protocol interface exposing canvas inspection, node placement, edge wiring, and layout execution to AI agents.
  4. **Client-Side Cinematic Export**: In-browser video rendering using WebCodecs API and `mp4-muxer`.

---

## 2. OpenFlow DSL v2 Specification
OpenFlow DSL provides an ultra-compact syntax for LLMs to generate and mutate flow graphs without coordinates or verbose JSON geometry.

### Grammar Overview
```text
flow: Architecture Overview
direction: TB

# Typed Node Declarations
[start] start: User Entry { icon: "User", color: "blue" }
[process] auth: Auth Gateway { icon: "Shield", color: "amber" }
[decision] verify: Token Valid? { color: "purple" }
[end] dashboard: Studio Workspace { icon: "LayoutDashboard", color: "emerald" }

# Typed Edge Declarations
start ==> auth
auth -> verify
verify ->|Yes| dashboard
verify ->|No| start
```

### Edge Style Token Mapping
- `->` : Standard directed edge (default dependency flow).
- `==>` : Primary / critical execution path (high-contrast pulse).
- `-->` : Secondary / asynchronous flow.
- `..` : Optional or weak reference.
- `->|Label|` : Labeled branch condition (e.g. decision routing).

---

## 3. ELK.js Web Worker & Anchored Layout Architecture
To prevent UI thread jank when running complex graph layouts (e.g. 50+ nodes):

1. **Dedicated Web Worker**:
   Run `elkjs/lib/elk.bundled.js` inside a Web Worker. Serialize graph nodes/edges into ELK JSON format, compute layout off-thread, and post back updated `(x, y)` coordinates.
2. **Preserving Spatial Memory (Anchored Layout)**:
   - **Hazard**: Global DAG auto-layout disrupts user-pinned cards and manual clusters.
   - **Solution**: Pass `elk.nodeLabels.placement` and mark manual nodes as `layoutOptions: { 'elk.fixCoordinates': 'true' }`.
   - ELK routes new agent-generated nodes around fixed manual cards without repositioning the user's focal nodes.

---

## 4. ThoughtDAG 2.0 Synthesis: Context Wires & Multi-Parent Merge
OpenFlowKit patterns directly enhance DNK OS's ThoughtDAG reasoning canvas:

### Architecture Mapping
- **Thought Node (`ThoughtDagNoteNode`)**:
  Represents an atomic reasoning hypothesis, test run, or research claim. Contains status badges (`verified`, `refuted`, `exploring`), token costs, and confidence weights.
- **Context Wire (`ContextWireEdge`)**:
  Represents provenance and context transfer. Carries array of upstream `message_ids` and cached prompt fingerprints.
- **Multi-Parent Context Synthesis**:
  When two independent reasoning branches connect to a synthesis node `C`, the orchestrator collects context from both parents and passes them as multi-part context to the LLM agent.

```text
[thought] H1: Monolithic FastMCP { confidence: 0.85 }
[thought] H2: Isolated Worker Subprocesses { confidence: 0.92 }
[critique] Risk: Memory footprint on low-spec VPS
[synthesis] FinalArchitecture

H1 -> Risk
H2 -> FinalArchitecture
Risk ->|Mitigation| FinalArchitecture
```

---

## 5. Architectural Boundaries & Anti-Patterns
1. **Rich-Text DOM Overhead**: Do not render full heavy Markdown WYSIWYG editors inside 200+ simultaneous XYFlow canvas nodes. Use lightweight preview cards with lazy portal hydration upon click/double-click.
2. **Global DSL Re-Serialization Bottleneck**: For graphs exceeding 100 nodes, avoid re-serializing the entire canvas to DSL on every keystroke. Use incremental AST patches (`add_node`, `connect_edge`) via the MCP protocol.
3. **SVG/Icon Injection Security**: Always sanitize user-provided or remote SVG icons using DOMPurify before mounting them onto canvas node headers.
