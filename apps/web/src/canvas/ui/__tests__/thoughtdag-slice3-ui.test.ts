// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/ui/__tests__/thoughtdag-slice3-ui.test.ts"
// purpose: "Unit tests for ThoughtDAG Slice 3: UI interactions, ContextWireEdge data mutations, Stale Context syncing, and Add Note flow"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Gerych Builder & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';
import { useCanvasStore } from '../../../../store/canvasStore';
import type { ThoughtDagNoteData } from '../../types/thoughtdag';

describe('ThoughtDAG Slice 3: UI Interactions, Context Wires & Stale Syncing', () => {
  beforeEach(() => {
    useCanvasStore.getState().resetToDefault();
  });

  it('1. updates Context Wire edge data via updateEdgeData (scope toggle between all and selection)', () => {
    const store = useCanvasStore.getState();
    const noteId = store.addThoughtDagNote(100, 100, 'Feature specs for Swarm Worker');
    const agentId = store.addNode('agentTask', { x: 400, y: 100 }, {
      taskId: 'task-101',
      title: 'Build Feature',
      targetAgent: 'gerych_builder',
      status: 'QUEUED',
    });

    // Connect wire via onConnect
    store.onConnect({
      source: noteId,
      sourceHandle: 'source-bottom',
      target: agentId,
      targetHandle: 'input',
    });

    const edge = useCanvasStore.getState().edges.find((e) => e.source === noteId && e.target === agentId);

    assert.ok(edge, 'Wire edge must be created');
    assert.strictEqual(edge.type, 'context-wire');
    assert.strictEqual((edge.data as any).scope, 'all');

    // UI action: Toggle wire scope to 'selection'
    store.updateEdgeData(edge.id, { scope: 'selection' });
    const updatedEdge = useCanvasStore.getState().edges.find((e) => e.id === edge.id);
    assert.strictEqual((updatedEdge?.data as any).scope, 'selection');

    // UI action: Toggle wire scope back to 'all'
    store.updateEdgeData(edge.id, { scope: 'all' });
    const revertedEdge = useCanvasStore.getState().edges.find((e) => e.id === edge.id);
    assert.strictEqual((revertedEdge?.data as any).scope, 'all');
  });

  it('2. AgentTaskNode stale context detection and Sync & Re-run action', () => {
    const store = useCanvasStore.getState();
    const noteId = store.addThoughtDagNote(100, 100, 'Original API spec v1');
    const agentId = store.addNode('agentTask', { x: 500, y: 100 }, {
      taskId: 'task-202',
      title: 'Generate Backend Schema',
      targetAgent: 'dnk_dev_fullstack',
      status: 'QUEUED',
    });

    store.onConnect({
      source: noteId,
      sourceHandle: 'source-bottom',
      target: agentId,
      targetHandle: 'input',
    });

    // Initial compile
    const initialContext = store.compileNodeContext(agentId);
    store.updateNodeData(agentId, {
      isStale: false,
      upstreamFingerprint: initialContext.contextHash,
      contextPrompt: initialContext.rawText,
    });

    let agentNode = useCanvasStore.getState().nodes.find((n) => n.id === agentId);
    assert.strictEqual((agentNode?.data as any).isStale, false);
    assert.ok((agentNode?.data as any).contextPrompt.includes('Original API spec v1'));

    // Upstream note is edited
    store.updateNodeData(noteId, { content: 'Updated API spec v2 with OAuth2' });
    store.refreshNodeStaleness(agentId);

    // Agent node is now marked stale
    agentNode = useCanvasStore.getState().nodes.find((n) => n.id === agentId);
    assert.strictEqual((agentNode?.data as any).isStale, true, 'Agent node must be marked stale after upstream change');

    // UI Action: User clicks "Sync & Re-run" button
    const freshContext = store.compileNodeContext(agentId);
    store.updateNodeData(agentId, {
      isStale: false,
      upstreamFingerprint: freshContext.contextHash,
      contextPrompt: freshContext.rawText,
      updatedAt: Date.now(),
    });

    agentNode = useCanvasStore.getState().nodes.find((n) => n.id === agentId);
    assert.strictEqual((agentNode?.data as any).isStale, false, 'Node must no longer be stale after sync');
    assert.ok((agentNode?.data as any).contextPrompt.includes('Updated API spec v2 with OAuth2'));
  });

  it('3. ThoughtDagNoteNode supports highlightMode transitions, tag editing, and prompt compilation', () => {
    const store = useCanvasStore.getState();
    const noteId = store.addThoughtDagNote(200, 200, 'Full documentation of auth workflow', {
      title: 'Auth Guide',
    });

    // 1. Direct switch to 'filter' mode
    store.setNoteHighlightMode(noteId, 'filter');
    store.updateNodeData(noteId, { selectedText: 'Strict JWT verification only' });

    let node = useCanvasStore.getState().nodes.find((n) => n.id === noteId);
    let data = node?.data as unknown as ThoughtDagNoteData;
    assert.strictEqual(data.highlightMode, 'filter');
    assert.strictEqual(data.selectedText, 'Strict JWT verification only');

    // Compile from node
    let compiled = store.compileNodeContext(noteId);
    assert.ok(compiled.rawText.includes('Strict JWT verification only'));
    assert.strictEqual(compiled.rawText.includes('Full documentation'), false, 'Filter mode should only include selected text');

    // 2. Direct switch to 'tag' mode with tag editing
    store.setNoteHighlightMode(noteId, 'tag');
    store.updateNodeData(noteId, { tag: 'security-crit' });

    node = useCanvasStore.getState().nodes.find((n) => n.id === noteId);
    data = node?.data as unknown as ThoughtDagNoteData;
    assert.strictEqual(data.highlightMode, 'tag');
    assert.strictEqual(data.tag, 'security-crit');

    compiled = store.compileNodeContext(noteId);
    assert.ok(compiled.rawText.includes('[Tag: security-crit]'));

    // 3. Switch to 'off' mode
    store.setNoteHighlightMode(noteId, 'off');
    node = useCanvasStore.getState().nodes.find((n) => n.id === noteId);
    data = node?.data as unknown as ThoughtDagNoteData;
    assert.strictEqual(data.highlightMode, 'off');
  });

  it('4. Toolbar "Add Note" creates a living ThoughtDAG note at exact coordinates', () => {
    const store = useCanvasStore.getState();
    const countBefore = store.nodes.length;

    const newNoteId = store.addThoughtDagNote(350, 450);
    const state = useCanvasStore.getState();

    assert.strictEqual(state.nodes.length, countBefore + 1);
    const created = state.nodes.find((n) => n.id === newNoteId);
    assert.ok(created);
    assert.strictEqual(created?.type, 'thoughtDagNote');
    assert.deepStrictEqual(created?.position, { x: 350, y: 450 });
    assert.strictEqual((created?.data as any).title, 'Living Note');
  });
});
