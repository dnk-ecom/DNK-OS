# Understand-Anything Knowledge Graph, Guided Tours, & Diff Impact Patterns

## Overview
Assimilated patterns from Egonex-AI/Understand-Anything (MIT) for codebase comprehension and multi-agent interaction.

## Key Architectural Patterns

### 1. Spatial Community Clustering & Guided Walkthrough Tours
- **Component**: `apps/web/components/canvas/MultiAgentSwarmCanvas.tsx`
- **Node Extension**: `apps/web/components/canvas/nodes/MultiAgentSwarmNode.tsx`
- **Types**: `apps/web/types/mcp.ts` (`community`, `highlighted`, `dimmed`)
- **Pattern**: Nodes are tagged with functional communities (`Orchestration`, `Knowledge & AST`, `Synthesis & UI`, `Adversarial Gate`).
- **Tour State Machine**: Interactive step-by-step traversal highlighting active node (`ring-2 ring-[#35d5d5] shadow-lg scale-105`) while dimming background nodes (`opacity-30`).
- **Verification**: `npm --prefix apps/web run type-check`

### 2. Diff Impact Analysis & Blast Radius Engine
- **Component**: `core/task_forest/diff_impact_analyzer.py`
- **Module Exports**: `core/task_forest/__init__.py` (`DiffImpactAnalyzer`, `DiffImpactReport`, `BlastRadiusNode`)
- **Pattern**: Evaluates file diffs (`git status --porcelain` or explicit relative paths) and cascades impact through TaskForest/TaskDNA nodes.
- **Transitive Depth**: Downstream nodes linked via dependency graph are flagged with `transitive_dependency` depth markers.
- **Risk Scoring**: Evaluates blast radius tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and assigns adversarial audit focus.
- **Canvas Overlay**: Exports JSON Canvas 1.0 graph with red highlight (`color: "1"`) on blast radius nodes.
- **Verification**: `./.venv/bin/pytest tests/core/test_diff_impact_analyzer.py -v`

### 3. SCONES Cognitive Rules ⇄ ADR Semantic Graph
- **Component**: `core/memory/scones_semantic_connector.py`
- **Pattern**: Tokenizes concepts across SCONES cognitive rules and Architecture Decision Records (ADRs). Computes bipartite similarity and relationship types (`governs`, `implements`, `supports`).
- **Artifact**: `docs/scones/scones_adr_semantic_graph.json`.
- **CLI Runner**: `python3 core/memory/scones_semantic_connector.py --rules-dir docs/scones/assimilated_rules --adr-dir docs/architecture/adr --output docs/scones/scones_adr_semantic_graph.json`
- **Verification**: `./.venv/bin/pytest tests/core/test_scones_semantic_connector.py -v`

### 4. Bidirectional Karpathy LLM Wiki ⇄ Obsidian Canvas
- **Component**: `core/obsidian/wiki_canvas_translator.py`
- **Pattern**:
  - `wiki_to_canvas`: Parses markdown wikilinks `[[Link]]` into directed edges on an Obsidian Canvas 1.0 (`.canvas`).
  - `canvas_to_wiki`: Ingests canvas graph mutations and serializes clean markdown articles with reconstructed `## 🔗 Related Knowledge Nodes`.
- **CLI Runner**: `python3 core/obsidian/wiki_canvas_translator.py --direction wiki_to_canvas --wiki-dir docs/notes --canvas-path docs/notes/knowledge_graph.canvas`
- **Verification**: `./.venv/bin/pytest tests/core/test_wiki_canvas_translator.py -v`

## Combined Verification Suite
```bash
./.venv/bin/pytest tests/core/test_diff_impact_analyzer.py tests/core/test_scones_semantic_connector.py tests/core/test_wiki_canvas_translator.py -v
npm --prefix apps/web run type-check
```
