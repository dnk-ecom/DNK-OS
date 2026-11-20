// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/context/__tests__/reevaluation-dag.test.ts"
// purpose: "Comprehensive unit tests for DAG topological re-evaluation, SCONES memory injection, and smart context gathering."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import test from 'node:test';
import assert from 'node:assert/strict';
import type { Node, Edge } from '@xyflow/react';
import {
  getReevaluationPlan,
  gatherSmartContext,
  executeDAGReevaluation,
  estimateTokens,
} from '../dag-reevaluation';
import { useCanvasStore } from '../../../../store/canvasStore';
import type { ThoughtDagNoteData } from '../../types/thoughtdag';

test('Re-evaluation DAG: Kahn topological sorting and multi-level batching', () => {
  // Graph: A -> B, A -> C, B -> D, C -> D (Diamond)
  const nodes: Node[] = [
    { id: 'node-A', type: 'thoughtDagNote', position: { x: 0, y: 0 }, data: { title: 'A', isStale: true } },
    { id: 'node-B', type: 'thoughtDagNote', position: { x: 100, y: 0 }, data: { title: 'B', isStale: true } },
    { id: 'node-C', type: 'thoughtDagNote', position: { x: 100, y: 100 }, data: { title: 'C', isStale: true } },
    { id: 'node-D', type: 'agentTask', position: { x: 200, y: 50 }, data: { title: 'D', isStale: true } },
  ];

  const edges: Edge[] = [
    { id: 'e-A-B', source: 'node-A', target: 'node-B' },
    { id: 'e-A-C', source: 'node-A', target: 'node-C' },
    { id: 'e-B-D', source: 'node-B', target: 'node-D' },
    { id: 'e-C-D', source: 'node-C', target: 'node-D' },
  ];

  const plan = getReevaluationPlan(nodes, edges, { onlyStale: false });

  assert.equal(plan.totalNodes, 4);
  assert.equal(plan.levels.length, 3);
  // Level 0: [node-A]
  assert.deepEqual(plan.levels[0], ['node-A']);
  // Level 1: [node-B, node-C] (can run in parallel!)
  assert.ok(plan.levels[1].includes('node-B') && plan.levels[1].includes('node-C'));
  // Level 2: [node-D]
  assert.deepEqual(plan.levels[2], ['node-D']);
});

test('Re-evaluation DAG: filters out fresh branches when onlyStale is true', () => {
  // Graph: A -> B -> D, and C -> D.
  // Only C and D are stale, A and B are fresh.
  const nodes: Node[] = [
    { id: 'node-A', type: 'thoughtDagNote', position: { x: 0, y: 0 }, data: { title: 'A', isStale: false } },
    { id: 'node-B', type: 'thoughtDagNote', position: { x: 100, y: 0 }, data: { title: 'B', isStale: false } },
    { id: 'node-C', type: 'thoughtDagNote', position: { x: 100, y: 100 }, data: { title: 'C', isStale: true } },
    { id: 'node-D', type: 'agentTask', position: { x: 200, y: 50 }, data: { title: 'D', isStale: true } },
  ];

  const edges: Edge[] = [
    { id: 'e-A-B', source: 'node-A', target: 'node-B' },
    { id: 'e-B-D', source: 'node-B', target: 'node-D' },
    { id: 'e-C-D', source: 'node-C', target: 'node-D' },
  ];

  const plan = getReevaluationPlan(nodes, edges, { onlyStale: true });

  assert.equal(plan.totalNodes, 2);
  assert.ok(plan.targetNodeIds.includes('node-C'));
  assert.ok(plan.targetNodeIds.includes('node-D'));
  assert.ok(!plan.targetNodeIds.includes('node-A'));
  assert.ok(!plan.targetNodeIds.includes('node-B'));
});

test('Smart Context: SCONES long-term memory injection and token budgeting', () => {
  const nodes: Node[] = [
    {
      id: 'node-source',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'Core Architecture Note',
        content: 'This is the main architecture documentation with extensive details on pipelines.',
      },
    },
    {
      id: 'node-task',
      type: 'agentTask',
      position: { x: 200, y: 0 },
      data: { title: 'Implement Module' },
    },
  ];

  const edges: Edge[] = [
    { id: 'e-1', source: 'node-source', target: 'node-task' },
  ];

  const sconesMemories = [
    {
      topic: 'Architecture Invariants',
      content: 'Rule 1: Always enforce Relative Paths. Rule 2: Anti-Sycophancy protocol active.',
      importance: 0.95,
    },
  ];

  const smartContext = gatherSmartContext('node-task', nodes, edges, {
    includeSconesMemories: true,
    sconesMemories,
    maxTokens: 500,
  });

  assert.ok(smartContext.rawText.includes('### Long-Term Episodic Memory (SCONES)'));
  assert.ok(smartContext.rawText.includes('Architecture Invariants'));
  assert.ok(smartContext.rawText.includes('Rule 1: Always enforce Relative Paths'));
  assert.equal(smartContext.sconesMemoriesInjected, 1);
  assert.equal(smartContext.truncated, false);
  assert.ok(smartContext.tokenEstimate > 0);
  assert.ok(smartContext.fingerprint.length > 0);
});

test('Smart Context: token budget truncation triggers when budget is exceeded', () => {
  const hugeContent = 'A'.repeat(8000); // ~2000 tokens
  const nodes: Node[] = [
    {
      id: 'node-huge',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: { title: 'Huge Note', content: hugeContent },
    },
    {
      id: 'node-task',
      type: 'agentTask',
      position: { x: 200, y: 0 },
      data: { title: 'Target' },
    },
  ];

  const edges: Edge[] = [
    { id: 'e-huge', source: 'node-huge', target: 'node-task' },
  ];

  const smartContext = gatherSmartContext('node-task', nodes, edges, {
    maxTokens: 200, // Budget 200 tokens ~800 chars
  });

  assert.equal(smartContext.truncated, true);
  assert.ok(smartContext.rawText.length <= 1000);
});

test('Re-evaluation DAG: executes multi-level plan, updates node outputs, and clears staleness', async () => {
  const nodes: Node[] = [
    {
      id: 'node-1',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'Spec',
        content: 'Refactor Canvas architecture.',
        isStale: true,
      },
    },
    {
      id: 'node-2',
      type: 'agentTask',
      position: { x: 200, y: 0 },
      data: {
        title: 'Code Generation',
        isStale: true,
        upstreamFingerprint: 'old-hash',
      },
    },
  ];

  const edges: Edge[] = [
    { id: 'e-1-2', source: 'node-1', target: 'node-2', data: { isStale: true } },
  ];

  const plan = getReevaluationPlan(nodes, edges, { onlyStale: false });
  const progressSnapshots: string[] = [];

  const evaluated = await executeDAGReevaluation(plan, {
    nodes,
    edges,
    evaluateNodeFn: async (node, ctx) => {
      return `Processed ${node.id} with context chars: ${ctx.rawText.length}`;
    },
    onProgress: (p) => {
      progressSnapshots.push(`${p.phase}:${p.current}/${p.total}`);
    },
  });

  assert.equal(evaluated.result.success, true);
  assert.equal(evaluated.result.completedCount, 2);

  // Check that nodes have been updated and are no longer stale
  const updatedTask = evaluated.updatedNodes.find((n) => n.id === 'node-2');
  assert.ok(updatedTask);
  assert.equal((updatedTask.data as any).isStale, false);
  assert.ok((updatedTask.data as any).response.includes('Processed node-2'));
  assert.notEqual((updatedTask.data as any).upstreamFingerprint, 'old-hash');

  // Check that edge staleness was cleared
  const updatedEdge = evaluated.updatedEdges.find((e) => e.id === 'e-1-2');
  assert.equal((updatedEdge?.data as any)?.isStale, false);

  // Check progress events
  assert.ok(progressSnapshots.some((s) => s.startsWith('evaluating')));
});

test('CanvasStore: runDAGReevaluation updates store state and clears stale badges', async () => {
  const store = useCanvasStore.getState();

  // Setup store nodes & edges
  useCanvasStore.setState({
    nodes: [
      {
        id: 'n-spec',
        type: 'thoughtDagNote',
        position: { x: 0, y: 0 },
        data: {
          title: 'Design Spec',
          content: 'Updated high-performance DAG specification.',
          isStale: true,
        },
      },
      {
        id: 'n-worker',
        type: 'agentTask',
        position: { x: 200, y: 0 },
        data: {
          title: 'Execute Task',
          isStale: true,
          upstreamFingerprint: 'stale-hash',
        },
      },
    ],
    edges: [
      { id: 'e-wire-1', source: 'n-spec', target: 'n-worker', data: { isStale: true } },
    ],
  });

  const res = await useCanvasStore.getState().runDAGReevaluation({
    onlyStale: true,
    evaluateNodeFn: async (node) => `Synthetic Execution Output for ${node.id}`,
  });

  assert.equal(res.success, true);
  assert.equal(res.completedCount, 2);

  const state = useCanvasStore.getState();
  assert.equal(state.isReevaluating, false);
  assert.equal(state.reevaluationProgress?.phase, 'complete');

  const workerNode = state.nodes.find((n) => n.id === 'n-worker');
  assert.equal((workerNode?.data as any).isStale, false);
  assert.ok((workerNode?.data as any).response.includes('Synthetic Execution Output for n-worker'));

  const wireEdge = state.edges.find((e) => e.id === 'e-wire-1');
  assert.equal((wireEdge?.data as any)?.isStale, false);
});
