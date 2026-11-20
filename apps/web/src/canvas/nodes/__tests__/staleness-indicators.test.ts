// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/nodes/__tests__/staleness-indicators.test.ts"
// purpose: "Unit tests for ThoughtDAG Slice 2: Staleness Visual Indicators, branch propagation, and wire syncing"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';
import { useCanvasStore } from '../../../../store/canvasStore';
import {
  evaluateGraphStaleness,
  isNodeStale,
  computeUpstreamFingerprint,
} from '../../context/context-builder';
import type { Node, Edge } from '@xyflow/react';

describe('ThoughtDAG Slice 2: Staleness Visual Indicators & Branch Propagation', () => {
  beforeEach(() => {
    useCanvasStore.getState().resetToDefault();
  });

  it('1. evaluateGraphStaleness detects stale downstream nodes and flags incoming edges', () => {
    const upstreamNote: Node = {
      id: 'note-1',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'Original Architecture Note',
        content: 'Original content v1',
      },
    };

    const targetNode: Node = {
      id: 'agent-1',
      type: 'agentTask',
      position: { x: 300, y: 0 },
      data: {
        title: 'Reviewer Agent',
        status: 'READY',
      },
    };

    const edge: Edge = {
      id: 'edge-1',
      source: 'note-1',
      target: 'agent-1',
      data: { scope: 'all', isStale: false },
    };

    const initialNodes = [upstreamNote, targetNode];
    const initialEdges = [edge];

    // Compute initial fingerprint and sync target node
    const initialFingerprint = computeUpstreamFingerprint('agent-1', initialNodes, initialEdges);
    targetNode.data = {
      ...targetNode.data,
      upstreamFingerprint: initialFingerprint,
      isStale: false,
    };

    // Before mutation: neither node nor edge is stale
    const check1 = evaluateGraphStaleness([upstreamNote, targetNode], [edge]);
    assert.strictEqual(check1.report.staleNodeIds.length, 0);
    assert.strictEqual(check1.report.staleEdgeIds.length, 0);

    // Mutate upstream note content
    const mutatedNote: Node = {
      ...upstreamNote,
      data: {
        ...upstreamNote.data,
        content: 'Modified content v2 with updated requirements',
      },
    };

    // After mutation: target node and connecting edge must be detected as stale
    const check2 = evaluateGraphStaleness([mutatedNote, targetNode], [edge]);
    assert.deepStrictEqual(check2.report.staleNodeIds, ['agent-1']);
    assert.deepStrictEqual(check2.report.staleEdgeIds, ['edge-1']);
    assert.strictEqual(check2.nextNodes.find((n) => n.id === 'agent-1')?.data.isStale, true);
    assert.strictEqual((check2.nextEdges.find((e) => e.id === 'edge-1')?.data as any).isStale, true);
  });

  it('2. propagates staleness across multi-level downstream branch (A -> B -> C)', () => {
    const noteA: Node = {
      id: 'note-a',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: { title: 'Living Note A', content: 'Base specification' },
    };

    const agentB: Node = {
      id: 'agent-b',
      type: 'agentTask',
      position: { x: 250, y: 0 },
      data: { title: 'Synthesis Agent' },
    };

    const agentC: Node = {
      id: 'agent-c',
      type: 'agentTask',
      position: { x: 500, y: 0 },
      data: { title: 'Deployment Agent' },
    };

    const edgeAB: Edge = { id: 'edge-ab', source: 'note-a', target: 'agent-b', data: { scope: 'all' } };
    const edgeBC: Edge = { id: 'edge-bc', source: 'agent-b', target: 'agent-c', data: { scope: 'all' } };

    const nodes = [noteA, agentB, agentC];
    const edges = [edgeAB, edgeBC];

    // Lock in initial fingerprints
    agentB.data = {
      ...agentB.data,
      upstreamFingerprint: computeUpstreamFingerprint('agent-b', nodes, edges),
      isStale: false,
    };
    agentC.data = {
      ...agentC.data,
      upstreamFingerprint: computeUpstreamFingerprint('agent-c', nodes, edges),
      isStale: false,
    };

    // Mutate root Note A
    const mutatedNoteA: Node = {
      ...noteA,
      data: { ...noteA.data, content: 'Updated Base specification v2' },
    };

    const result = evaluateGraphStaleness([mutatedNoteA, agentB, agentC], edges);

    // Both downstream nodes and both connecting edges should be marked stale
    assert.ok(result.report.staleNodeIds.includes('agent-b'));
    assert.ok(result.report.staleNodeIds.includes('agent-c'));
    assert.ok(result.report.staleEdgeIds.includes('edge-ab'));
    assert.ok(result.report.staleEdgeIds.includes('edge-bc'));
  });

  it('3. refreshNodeStaleness updates canvas store nodes and edges atomically', () => {
    const store = useCanvasStore.getState();

    // Create note and agent
    const noteId = store.addThoughtDagNote(100, 100, 'Original Spec');
    const agentNode: Node = {
      id: 'agent-task-1',
      type: 'agentTask',
      position: { x: 400, y: 100 },
      data: { title: 'Worker' },
    };

    useCanvasStore.setState({
      nodes: [...useCanvasStore.getState().nodes, agentNode],
      edges: [
        {
          id: 'wire-1',
          source: noteId,
          target: 'agent-task-1',
          data: { scope: 'all', isStale: false },
        },
      ],
    });

    // Sync initial state
    useCanvasStore.getState().syncNodeContext('agent-task-1');

    let state = useCanvasStore.getState();
    let edge = state.edges.find((e) => e.id === 'wire-1');
    assert.strictEqual(edge?.data?.isStale, false);

    // Mutate the note
    store.updateNodeData(noteId, { content: 'Brand new spec content' });

    // updateNodeData auto-triggers refreshNodeStaleness
    state = useCanvasStore.getState();
    const updatedAgent = state.nodes.find((n) => n.id === 'agent-task-1');
    const updatedEdge = state.edges.find((e) => e.id === 'wire-1');

    assert.strictEqual(updatedAgent?.data?.isStale, true);
    assert.strictEqual((updatedEdge?.data as any)?.isStale, true);
  });

  it('4. syncNodeContext clears stale flags on target node and incoming wires', () => {
    const store = useCanvasStore.getState();
    const noteId = store.addThoughtDagNote(50, 50, 'V1 text');

    useCanvasStore.setState({
      nodes: [
        ...useCanvasStore.getState().nodes,
        {
          id: 'agent-x',
          type: 'agentTask',
          position: { x: 300, y: 50 },
          data: { title: 'Coder', isStale: true, upstreamFingerprint: 'stale-hash' },
        },
      ],
      edges: [
        {
          id: 'wire-x',
          source: noteId,
          target: 'agent-x',
          data: { isStale: true },
        },
      ],
    });

    // Execute 1-click sync
    store.syncNodeContext('agent-x');

    const state = useCanvasStore.getState();
    const syncedNode = state.nodes.find((n) => n.id === 'agent-x');
    const syncedEdge = state.edges.find((e) => e.id === 'wire-x');

    assert.strictEqual(syncedNode?.data?.isStale, false);
    assert.strictEqual((syncedEdge?.data as any)?.isStale, false);
    assert.ok(typeof syncedNode?.data?.upstreamFingerprint === 'string');
    assert.ok(syncedNode!.data.upstreamFingerprint!.length > 0);
  });
});
