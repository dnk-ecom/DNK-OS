<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/task_inception_and_excalidraw_visual_workflow_protocol.md"
purpose: "Task Inception, Context Injection & Interactive Excalidraw Visual Workflow Protocol v3.0"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "3.0.0"
updated_at: "2026-09-09"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🎨 Task Inception & Interactive Excalidraw Visual Workflow Protocol (VIS-WORKFLOW-001)

## 1. Context & Architectural Challenge
Translating a 1–2 sentence human visionary intent into a fully autonomous, zero-hallucination swarm execution requires a structured multi-stage transformer:
1. **Human Intent (Inception)**: Natural language prompt without technical boilerplate.
2. **Context Injection Core**: Transparent enrichment using User Profile/Memory, Repo AST symbol resolution (`dnk_resolve_symbol`), SCONES cognitive lessons, and environment SSOT.
3. **Bulletproof Spec v3.0**: Formal contract containing Anti-Scope, Strict File Whitelist, Pre-declared Interface Pseudocode, and Phased MASE Slices (<=25 tools/turn).
4. **Swarm Execution Engine**: Parallel/sequential worker dispatch with isolated files and strict completion barriers.
5. **Quality Gate & Obsidian Knowledge Base**: Master Gate verification (`verify_all.sh`), completion reports, and spatial visualization.

## 2. Interactive Excalidraw Canvas Pipeline
To make this workflow visible, reviewable, and navigable within the Obsidian PKM ecosystem:
- The canvas is generated as a hybrid `.excalidraw.md` document stored under `docs/notes/Excalidraw/`.
- Every major component links directly to its source in the workspace via Obsidian `[[wikilinks]]`.
- Programmatic generator: `scripts/system/generate_task_workflow_excalidraw.py`.

### Critical Invariants for Obsidian Excalidraw Generation
1. **Arrow Two-Way Binding**:
   - The arrow element must declare `startBinding: {"elementId": source_id, "focus": 0, "gap": 1}` and `endBinding: {"elementId": target_id, "focus": 0, "gap": 1}`.
   - Both source and target containers must register the arrow in `boundElements: [{"id": arrow_id, "type": "arrow"}]`.
   - This ensures lines do not disconnect when shapes are moved manually on the Obsidian canvas.
2. **Container-Bound Text Elements**:
   - The container rectangle has `boundElements: [{"id": text_id, "type": "text"}]`.
   - The text element specifies `containerId: container_id`, `textAlign: "center"`, `verticalAlign: "middle"`.
3. **Interactive Workspace Links**:
   - Assign `link: "[[path/to/file.md]]"` directly on the container shapes.
   - In Obsidian, clicking (or `Cmd`+Click) navigates directly to that markdown file, task template, or script.

## 3. Reference Files & Artifacts
- **Excalidraw Visual Canvas**: `docs/notes/Excalidraw/002_DNK_Task_Inception_and_Agentic_Workflow.excalidraw.md`
- **Canvas Generator**: `scripts/system/generate_task_workflow_excalidraw.py`
- **Task Formulation Standard**: `docs/notes/127_bulletproof_task_formulation_standard_and_agentic_workflow.md`
- **Canonical Task Template**: `docs/templates/GERYCH_TASK_TEMPLATE.md` (v3.0)
- **User Intent Template**: `docs/templates/INTENT_TEMPLATE.md`
