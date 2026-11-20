// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/nodes/__tests__/text-selection-handles.test.ts"
// purpose: "Unit tests for text block/paragraph parsing, handle formatting, and context wire extraction."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import test from 'node:test';
import assert from 'node:assert/strict';
import {
  parseContentIntoBlocks,
  formatBlockHandleId,
  isBlockHandleId,
  parseBlockIdFromHandle,
  extractBlockText,
} from '../textBlockParser';
import { extractEffectiveNoteContent } from '../../context/context-builder';
import { ThoughtDagNoteData } from '../../types/thoughtdag';

test('Text Block Parser - splits standard markdown paragraphs into stable block IDs', () => {
  const content = `First paragraph with key hypothesis.

Second paragraph with specific architectural decision.

Third paragraph with metrics.`;

  const blocks = parseContentIntoBlocks(content);
  assert.equal(blocks.length, 3);
  assert.equal(blocks[0].id, 'p-0');
  assert.equal(blocks[0].text, 'First paragraph with key hypothesis.');
  assert.equal(blocks[1].id, 'p-1');
  assert.equal(blocks[1].text, 'Second paragraph with specific architectural decision.');
  assert.equal(blocks[2].id, 'p-2');
  assert.equal(blocks[2].text, 'Third paragraph with metrics.');
});

test('Text Block Parser - extracts Obsidian-style block references (^ref-id)', () => {
  const content = `Core architecture rule ^arch-rule-01

Another decision here. ^decision-42`;

  const blocks = parseContentIntoBlocks(content);
  assert.equal(blocks.length, 2);
  assert.equal(blocks[0].id, 'arch-rule-01');
  assert.equal(blocks[0].text, 'Core architecture rule');
  assert.equal(blocks[1].id, 'decision-42');
  assert.equal(blocks[1].text, 'Another decision here.');
});

test('Handle ID formatting, validation, and parsing', () => {
  const handleId = formatBlockHandleId('p-2');
  assert.equal(handleId, 'handle-block-p-2');
  assert.equal(isBlockHandleId(handleId), true);
  assert.equal(isBlockHandleId('source-right'), false);
  assert.equal(isBlockHandleId('handle-sel-active'), false);
  assert.equal(isBlockHandleId(null), false);

  assert.equal(parseBlockIdFromHandle(handleId), 'p-2');
  assert.equal(parseBlockIdFromHandle('source-right'), null);
});

test('extractBlockText - retrieves target block text accurately', () => {
  const content = `P0: Overview\n\nP1: Detailed spec\n\nP2: Rollback strategy`;
  const text = extractBlockText(content, 'p-1');
  assert.equal(text, 'P1: Detailed spec');

  const textFromObsidianRef = extractBlockText('Mission critical note ^ref-99', 'ref-99');
  assert.equal(textFromObsidianRef, 'Mission critical note');

  const missing = extractBlockText(content, 'non-existent');
  assert.equal(missing, null);
});

test('extractEffectiveNoteContent - block handle wire extracts only the connected paragraph', () => {
  const noteData: ThoughtDagNoteData = {
    title: 'Architecture Blueprint',
    content: `Overview paragraph.\n\nTarget paragraph for Agent: Run schema migration.\n\nFooter conclusion.`,
    highlightMode: 'off',
    author: 'Architect',
    updatedAt: Date.now(),
  };

  // When wire sourceHandle connects to handle-block-p-1
  const result = extractEffectiveNoteContent(
    noteData,
    'block',
    'handle-block-p-1',
    { blockId: 'p-1' }
  );

  assert.equal(result.mode, 'filter');
  assert.equal(result.content, 'Target paragraph for Agent: Run schema migration.');
});

test('extractEffectiveNoteContent - fallback to edgeData.extractedText if present', () => {
  const noteData: ThoughtDagNoteData = {
    title: 'Living Note',
    content: 'Full note content here with lots of tokens.',
    highlightMode: 'off',
    author: 'Architect',
    updatedAt: Date.now(),
  };

  const result = extractEffectiveNoteContent(
    noteData,
    'selection',
    'handle-sel-active',
    { extractedText: 'isolated snippet only' }
  );

  assert.equal(result.mode, 'filter');
  assert.equal(result.content, 'isolated snippet only');
});
