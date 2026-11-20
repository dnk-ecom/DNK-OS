// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/stream/flowStepParser.test.ts"
// purpose: "Unit tests for parseFlowSteps function"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { describe, it } from 'node:test';
import assert from 'node:assert';
import { parseFlowSteps, type FlowStep } from './flowStepParser.ts';

describe('flowStepParser', () => {
  it('returns empty nodes and edges for empty steps', () => {
    const res = parseFlowSteps([]);
    assert.deepStrictEqual(res.nodes, []);
    assert.deepStrictEqual(res.edges, []);
  });

  it('correctly arranges linear sequential steps into topological levels', () => {
    const steps: FlowStep[] = [
      {
        step_id: 'step_1',
        agent_id: 'strategist',
        title: 'Plan Strategy',
        status: 'completed',
      },
      {
        step_id: 'step_2',
        agent_id: 'denchik',
        title: 'Build Code',
        status: 'running',
        depends_on: ['step_1'],
      },
      {
        step_id: 'step_3',
        agent_id: 'gerych',
        title: 'Audit & Gate',
        status: 'queued',
        depends_on: ['step_2'],
      },
    ];

    const { nodes, edges } = parseFlowSteps(steps, { startX: 100, gapX: 100, columnWidth: 300 });

    assert.strictEqual(nodes.length, 3);
    assert.strictEqual(edges.length, 2);

    // Step 1: level 0 -> x = 100
    assert.strictEqual(nodes[0].position.x, 100);
    // Step 2: level 1 -> x = 100 + 1 * (300 + 100) = 500
    assert.strictEqual(nodes[1].position.x, 500);
    // Step 3: level 2 -> x = 100 + 2 * (300 + 100) = 900
    assert.strictEqual(nodes[2].position.x, 900);

    // Verify edges
    assert.strictEqual(edges[0].source, 'step_1');
    assert.strictEqual(edges[0].target, 'step_2');
    assert.strictEqual(edges[1].source, 'step_2');
    assert.strictEqual(edges[1].target, 'step_3');
  });

  it('supports Fan-Out and Fan-In DAG dependencies', () => {
    const steps: FlowStep[] = [
      { step_id: 'root', agent_id: 'supervisor', title: 'Task Intake', status: 'completed' },
      { step_id: 'worker_a', agent_id: 'denchik', title: 'Code Frontend', status: 'completed', depends_on: ['root'] },
      { step_id: 'worker_b', agent_id: 'dnk_shopify', title: 'Liquid AST', status: 'completed', depends_on: ['root'] },
      { step_id: 'merge', agent_id: 'gerych', title: 'Fan-In Synthesis', status: 'running', depends_on: ['worker_a', 'worker_b'] },
    ];

    const { nodes, edges } = parseFlowSteps(steps);

    assert.strictEqual(nodes.length, 4);
    assert.strictEqual(edges.length, 4); // root->worker_a, root->worker_b, worker_a->merge, worker_b->merge

    const mergeNode = nodes.find((n) => n.id === 'merge');
    assert(mergeNode);
    // mergeNode is at depth 2
    assert(mergeNode.position.x > nodes.find((n) => n.id === 'worker_a')!.position.x);
  });
});
