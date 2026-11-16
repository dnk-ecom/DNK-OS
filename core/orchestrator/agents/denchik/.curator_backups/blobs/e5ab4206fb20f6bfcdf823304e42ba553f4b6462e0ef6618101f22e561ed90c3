# --- DNK-MRH-HEADER ---
# mrh_id: "skills_software_dev_canvas_engine_references_codespring_visual_planning"
# purpose: "Technical Specification and Invariants for CodeSpring Visual Planning, Context Boundaries, and Scout Synthesis"
# author: "DNK-e.com Maksym & Gerych Prime"
# license: "DNK-INTERNAL"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-10"
# --- END DNK-MRH-HEADER ---

# CodeSpring Visual Planning, Context Boundaries & Scout Synthesis

## 1. Architectural Philosophy: "The Map is the Memory"
Modern LLM coding agents suffer from chronic context rot across sessions, resulting in repetitive explanations and regressions ("fixing one thing, breaking another"). CodeSpring establishes a visual mindmap/canvas as the persistent Single Source of Truth (SSOT) between human architects and autonomous agent swarms.

## 2. Spatial Hierarchy & Node Boundary Typology
To prevent context window bloat and visual clutter, nodes follow a strict hierarchical nesting:

```
[Project Node (Root)]
       │
  ┌────┴────────────────────────┐
  ▼                             ▼
[Feature Node A]          [Feature Node B]
  │                             │
  ├─► [Sub-feature Node]        └─► [Sub-feature Node]
  │
  └─► [Bridge Node]
        │
        ├─► [Notes Node] (Green card: simple business rules, low-token human guidance)
        └─► [PRD Node] (UI / Backend / Database specifications)
```

- **Project Node (Root)**: Contains repository bindings, target environment, and linked primary agent.
- **Feature Node**: High-level capability domain (e.g., Auth, Dashboard, Checkout).
- **Sub-feature Node**: Granular views, modal components, or isolated workflow steps.
- **Bridge Node**: Decoupling hub that isolates metadata (notes, moodboards, specs) from parent feature cards, keeping the main graph clean.
- **Notes Node**: Plain-language human guidelines and constraints. Acts as an ultra-compact context injection for agents.
- **PRD Nodes**: Modular functional contracts split into 3 distinct domains:
  1. *Frontend / UI PRD*
  2. *Backend Features PRD*
  3. *Database Design PRD*

## 3. The "Mockup-First PRD" Invariant
**Rule**: Generate visual mockups, clickable prototypes, or UI component tokens BEFORE drafting deep technical PRDs.
- *Rationale*: Writing comprehensive PRDs based purely on raw conceptual prompts leads agents to formalize false assumptions. Validating a fast visual mockup aligns human intent first; the PRD is then authored against confirmed visual contracts.

## 4. The 5-Gate Codebase Audit Protocol
Before importing or wrapping legacy/unfamiliar codebases into the canvas, execute the 5-Gate Audit:
1. **Functional Truth**: Does the application actually perform the required business logic?
2. **Zero Fabrication**: Are any outputs, metrics, or APIs mocked or faked under the guise of real data?
3. **Architectural Viability**: Does the module's architecture meet scalability and concurrency goals?
4. **Extensibility**: Can future swarm agents safely build atop this foundation without cascading breakage?
5. **Runtime Stability**: Can real users exercise core user journeys without unhandled crashes?

*Failure on any single gate mandates refactoring/remediation rather than direct adoption.*

## 5. Context Tagging Protocol ("Tag First, Then Ask")
- Rather than dumping the entire repository tree into an agent turn, the developer tags the target node or cluster on the canvas (`Feature: Auth`).
- The runtime automatically scopes the prompt to:
  `Node Definition + Associated Notes + Connected PRDs + Target File Paths`
- Eliminates 80%+ of extraneous context tokens, preventing context compression and tool budget exhaustion.

## 6. Autonomous Scouts-to-Canvas Backlog Synthesis
- Background scout tasks (e.g., competitive intelligence, dependency CVE monitoring, SOTA repository scans) do not terminate as dead log files.
- Scout findings automatically compile into new `Feature Proposal` nodes on the Spatial Canvas in `Draft / Backlog` state.

## 7. Architecture Drift Detection (Resync Protocol)
- At milestone intervals, an AST scanner traverses the repository files and reconciles them against the registered canvas node definitions.
- Discrepancies (untracked endpoints, orphaned UI components, mutated schemas) trigger visual drift indicators on the corresponding canvas cards.
