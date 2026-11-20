// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/nodes/textBlockParser.ts"
// purpose: "Deterministic block/paragraph parser and selection handle formatter for Canvas nodes."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { TextBlockItem, TextSelectionHandle } from '../types/thoughtdag';

export type { TextBlockItem, TextSelectionHandle };

const OBSIDIAN_BLOCK_REF_REGEX = /\^([a-zA-Z0-9\-_]+)$/;

/**
 * Deterministically parses markdown or plain text note content into stable blocks/paragraphs.
 * Supports Obsidian block references (`^blockId`) if present at the end of the line.
 */
export function parseContentIntoBlocks(content: string): TextBlockItem[] {
  if (!content || typeof content !== 'string') {
    return [];
  }

  // Split by double newline or individual header/list items
  const rawParagraphs = content.split(/\n\s*\n/);
  const blocks: TextBlockItem[] = [];
  let blockIndex = 0;

  for (let i = 0; i < rawParagraphs.length; i++) {
    const raw = rawParagraphs[i].trim();
    if (!raw) continue;

    // Check if paragraph ends with an Obsidian block reference (^p1, ^my-ref)
    const match = raw.match(OBSIDIAN_BLOCK_REF_REGEX);
    let id: string;
    let cleanText = raw;

    if (match && match[1]) {
      id = match[1];
      cleanText = raw.replace(OBSIDIAN_BLOCK_REF_REGEX, '').trim();
    } else {
      id = `p-${blockIndex}`;
    }

    // Check for inline tag prefix (e.g. [tag: research])
    let tag: string | undefined;
    const tagMatch = cleanText.match(/^\[([a-zA-Z0-9_\-]+)\]/);
    if (tagMatch) {
      tag = tagMatch[1];
    }

    blocks.push({
      id,
      text: cleanText,
      order: blockIndex,
      tag,
    });

    blockIndex++;
  }

  return blocks;
}

/**
 * Generates a unique ReactFlow handle identifier for a given block.
 */
export function formatBlockHandleId(blockId: string): string {
  return `handle-block-${blockId}`;
}

/**
 * Checks whether a ReactFlow handle ID represents a block-level handle.
 */
export function isBlockHandleId(handleId?: string | null): boolean {
  if (!handleId) return false;
  return handleId.startsWith('handle-block-');
}

/**
 * Extracts the underlying block_id from a block handle ID.
 */
export function parseBlockIdFromHandle(handleId?: string | null): string | null {
  if (!handleId || !isBlockHandleId(handleId)) return null;
  return handleId.replace(/^handle-block-/, '');
}

/**
 * Formats a text selection handle ID for a specific highlighted snippet.
 */
export function formatSelectionHandleId(snippetId: string): string {
  return `handle-sel-${snippetId}`;
}

/**
 * Checks whether a handle ID represents a snippet selection handle.
 */
export function isSelectionHandleId(handleId?: string | null): boolean {
  if (!handleId) return false;
  return handleId.startsWith('handle-sel-');
}

/**
 * Retrieves the specific text for a block_id from content or block list.
 */
export function extractBlockText(
  content: string,
  blockId: string,
  blocks?: TextBlockItem[]
): string | null {
  const activeBlocks = blocks && blocks.length > 0 ? blocks : parseContentIntoBlocks(content);
  const found = activeBlocks.find((b) => b.id === blockId);
  return found ? found.text : null;
}
