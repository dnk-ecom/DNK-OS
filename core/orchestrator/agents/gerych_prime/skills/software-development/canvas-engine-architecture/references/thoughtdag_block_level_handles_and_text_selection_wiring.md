<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/canvas-engine-architecture/references/thoughtdag_block_level_handles_and_text_selection_wiring.md"
purpose: "Reference guide for paragraph-level and block-selection handles in ReactFlow/ThoughtDAG nodes."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-20"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# ThoughtDAG Block-Level Handles & Text Selection Wiring

## 1. Overview & Motivation
Standard node-level connections wire the entire text/content of a note into downstream agent prompts, risking context bloat and prompt dilution.
Block-level handles allow users to drag connection wires directly from individual paragraphs, list items, or highlighted text spans to target agents.

## 2. Core Components
- **`textBlockParser.ts` (`apps/web/src/canvas/nodes/textBlockParser.ts`)**:
  - `parseContentIntoBlocks(content: string): TextBlockItem[]`: Deterministically splits markdown content into discrete blocks/paragraphs, capturing Obsidian block references (`^ref123`) or synthetic sequential IDs (`p-0`, `p-1`).
  - `formatBlockHandleId(blockId: string): string`: Maps block IDs to valid ReactFlow handle strings (`handle-block-${blockId.replace(/[^a-zA-Z0-9_-]/g, '_')}`).
  - `isBlockHandleId(handleId: string | null | undefined): boolean`: Fast check whether a handle represents a block slice.
  - `parseBlockIdFromHandle(handleId: string): string | null`: Extracts blockId from handle identifier.
  - `extractBlockText(content: string, blockId: string): string | null`: Extracts isolated block text.
- **Node Components (`apps/web/components/canvas/nodes/ThoughtDagNoteNode.tsx` & `TextNode.tsx`)**:
  - Render dynamically positioned `Handle` components (`type="source"`, `position={Position.Right}`) along the note's right border with section badge `§`.
  - Provide live preview toggle (`showBlockHandles`) and visual indicators.
- **Store & Edge Creation (`apps/web/store/canvasStore.ts`)**:
  - In `onConnect`, checks if `connection.sourceHandle` matches `handle-block-*` or `handle-sel-active`.
  - Sets edge data: `{ scope: 'block', blockId, extractedText }`.
- **Context Compilation (`apps/web/src/canvas/context/context-builder.ts`)**:
  - In `extractEffectiveNoteContent(node, wireScope, blockId)`: if `wireScope === 'block'` and `blockId` is set, only the targeted paragraph is fed into the downstream prompt, strictly maintaining zero-waste token diet.

## 3. Headless Verification Pattern
```bash
npx tsx --test apps/web/src/canvas/nodes/__tests__/text-selection-handles.test.ts
npm --prefix apps/web run type-check
```
