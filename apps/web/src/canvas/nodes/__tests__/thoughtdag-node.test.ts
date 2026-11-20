// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/nodes/__tests__/thoughtdag-node.test.ts"
// purpose: "Unit tests for ThoughtDAG NoteNode data model, state mutations, and ReactFlow edge connectivity"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';
import { useCanvasStore } from '../../../../store/canvasStore';
import type { ThoughtDagNoteData, HighlightMode, ContextNodeWire } from '../../types/thoughtdag';

describe('ThoughtDAG Slice 1: NoteNode & Data Model', () => {
  beforeEach(() => {
    useCanvasStore.getState().resetToDefault();
  });

  it('1. adds a ThoughtDagNoteNode as a first-class ReactFlow node (Invariant 1: Not a WhiteboardElement)', () => {
    const store = useCanvasStore.getState();
    const nodeId = store.addThoughtDagNote(150, 250, 'Initial living note content', {
      title: 'Architecture Strategy',
      tag: 'PRD-001',
      author: 'Maksym'
    });

    const state = useCanvasStore.getState();
    const node = state.nodes.find((n) => n.id === nodeId);

    // Invariant 1: First-class ReactFlow node
    assert.ok(node, 'Node should exist in state.nodes');
    assert.strictEqual(node?.type, 'thoughtDagNote');
    assert.deepStrictEqual(node?.position, { x: 150, y: 250 });
    assert.strictEqual(state.selectedNodeId, nodeId);

    // Verify it is NOT in whiteboardElements
    const whiteboardHasNode = state.whiteboardElements.some((elem) => elem.id === nodeId);
    assert.strictEqual(whiteboardHasNode, false, 'Note must NOT be a WhiteboardElement');

    // Verify data payload conforms to ThoughtDagNoteData
    const data = node?.data as unknown as ThoughtDagNoteData;
    assert.strictEqual(data.title, 'Architecture Strategy');
    assert.strictEqual(data.content, 'Initial living note content');
    assert.strictEqual(data.highlightMode, 'off');
    assert.strictEqual(data.tag, 'PRD-001');
    assert.strictEqual(data.author, 'Maksym');
    assert.strictEqual(data.isStale, false);
    assert.ok(typeof data.updatedAt === 'number');
  });

  it('2. mutates highlightMode via setNoteHighlightMode', () => {
    const store = useCanvasStore.getState();
    const nodeId = store.addThoughtDagNote(100, 100, 'Context to be filtered');

    // Initial state is 'off'
    let node = useCanvasStore.getState().nodes.find((n) => n.id === nodeId);
    assert.strictEqual((node?.data as any).highlightMode, 'off');

    // Mutate to 'filter'
    store.setNoteHighlightMode(nodeId, 'filter');
    node = useCanvasStore.getState().nodes.find((n) => n.id === nodeId);
    assert.strictEqual((node?.data as any).highlightMode, 'filter');

    // Mutate to 'tag'
    store.setNoteHighlightMode(nodeId, 'tag');
    node = useCanvasStore.getState().nodes.find((n) => n.id === nodeId);
    assert.strictEqual((node?.data as any).highlightMode, 'tag');
  });

  it('3. updates selection range, upstream fingerprint, and stale status', () => {
    const store = useCanvasStore.getState();
    const nodeId = store.addThoughtDagNote(200, 200, 'Full documentation markdown content');

    const sampleFingerprint = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855';
    store.updateNodeData(nodeId, {
      selectedText: 'markdown content',
      upstreamFingerprint: sampleFingerprint,
      isStale: true
    });

    const updated = useCanvasStore.getState().nodes.find((n) => n.id === nodeId);
    const data = updated?.data as unknown as ThoughtDagNoteData;
    assert.strictEqual(data.selectedText, 'markdown content');
    assert.strictEqual(data.upstreamFingerprint, sampleFingerprint);
    assert.strictEqual(data.isStale, true);
  });

  it('4. connects wire FROM note TO agent (Invariant 2: source is note, target is agent)', () => {
    const store = useCanvasStore.getState();

    // 1. Create ThoughtDagNoteNode (Source)
    const noteId = store.addThoughtDagNote(50, 50, 'Agent briefing: optimize checkout conversion', {
      title: 'Checkout Prompt',
      highlightMode: 'filter'
    });

    // 2. Create AgentTaskNode (Target)
    const agentNodeId = store.addNode('AgentTaskNode', { x: 450, y: 50 }, {
      targetAgent: 'dnk_shopify',
      prompt: 'Optimize theme checkout'
    });

    // 3. Connect wire FROM Note (source) TO Agent (target)
    store.onConnect({
      source: noteId,
      sourceHandle: 'source-bottom',
      target: agentNodeId,
      targetHandle: null
    });

    const state = useCanvasStore.getState();
    assert.strictEqual(state.edges.length, 1);

    const wireEdge = state.edges[0];
    // Invariant 2 assertion: source is Note, target is Agent
    assert.strictEqual(wireEdge.source, noteId, 'Source must be the ThoughtDagNoteNode');
    assert.strictEqual(wireEdge.target, agentNodeId, 'Target must be the AgentTaskNode');
    assert.strictEqual(wireEdge.sourceHandle, 'source-bottom');

    // Validate ContextNodeWire compatibility
    const contextWire: ContextNodeWire = {
      id: wireEdge.id,
      source: wireEdge.source,
      target: wireEdge.target,
      sourceHandle: wireEdge.sourceHandle,
      targetHandle: wireEdge.targetHandle,
      selectedText: 'Agent briefing: optimize checkout conversion',
      fingerprint: 'sha256-mock-hash'
    };

    assert.strictEqual(contextWire.source, noteId);
    assert.strictEqual(contextWire.target, agentNodeId);
  });
});
