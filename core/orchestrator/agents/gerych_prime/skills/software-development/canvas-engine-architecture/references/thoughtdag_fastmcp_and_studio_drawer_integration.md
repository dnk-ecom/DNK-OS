# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/thoughtdag_fastmcp_and_studio_drawer_integration.md"
# purpose: "Technical specifications for ThoughtDAG FastMCP server tools and DNK Studio Drawer UI integration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# ThoughtDAG FastMCP Tools & DNK Studio Drawer Integration

## 1. Domain FastMCP Server Tools (`core/bricks/brick_03_spatial_canvas/mcp_server.py`)
Registered under the `canvas` domain and exposed via `core/orchestrator/tool_aliases.py`:

| Tool Name | Alias | Purpose | Return Structure |
|---|---|---|---|
| `canvas_parse_thought_dsl` | `thoughtdag.parse_dsl` | Parse text DSL into nodes & edges with Kahn cycle check | `{"nodes": [...], "edges": [...], "has_cycle": bool, "cycle_nodes": [...]}` |
| `canvas_export_thought_dsl` | `thoughtdag.export_dsl` | Export graph nodes and edges into clean DSL text | `{"dsl_text": str, "node_count": int, "edge_count": int}` |
| `canvas_merge_thought_context` | `thoughtdag.merge` | Deduplicate and merge multi-parent thought paths | `{"status": "merged", "synthesis_node": {...}, "edges": [...], "parent_ids": [...], "ancestors_deduped_count": int, "fingerprint": str}` |
| `canvas_compile_thought_context` | `thoughtdag.compile` | Compile upstream context chain for agent prompts | `{"status": "compiled", "target_node_id": str, "compiled_context": str, "included_nodes": [...], "estimated_tokens": int}` |

## 2. Pydantic Model Alignment Pitfall
When returning dictionary outputs from FastMCP tools that wrap Pydantic models (such as `MultiParentMergeResult` and `CompiledContext`), ensure dictionary key lookup in tests matches model attributes:
- `MultiParentMergeResult` defines `parent_id` (not `parent_ids`) and `ancestors_deduped_count` (not `ancestors_count`).
- `CompiledContext` defines `target_node_id` (not `target_id`).

## 3. DNK Studio Workspace Drawer (`apps/web/components/stitch/StitchThoughtDagDrawer.tsx`)
- Registered in `apps/web/components/stitch/index.ts` and rendered in `DNKStudioWorkspace.tsx`.
- Activated via top navigation button in `StitchTopNav.tsx` with active pill and hypothesis count.
- Three functional tabs:
  1. **DSL Editor/Preview**: Real-time syntax feedback, Kahn cycle detection alert badge, preset templates, import to canvas (`useCanvasStore.addThoughtDagNote` + `connectContextWire`), and export from canvas.
  2. **Multi-Parent Synthesis Merge**: Checkbox selection of parent nodes, target synthesis title, preview of deduped ancestors count and SHA-256 fingerprint, canvas insertion.
  3. **Context Compiler**: Target node selector, compiled prompt viewer with estimated tokens, one-click clipboard copy for LLM injection.
