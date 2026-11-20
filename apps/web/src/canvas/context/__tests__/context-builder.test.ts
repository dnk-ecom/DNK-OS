// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/context/__tests__/context-builder.test.ts"
// purpose: "Unit tests for ThoughtDAG Context Builder, Highlight Filtering, Upstream Fingerprinting and Staleness Detection"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import test from 'node:test';
import assert from 'node:assert/strict';
import { Node, Edge } from '@xyflow/react';
import {
  deterministicHash,
  getUpstreamAncestors,
  extractEffectiveNoteContent,
  partitionContext,
  buildContextFromWires,
  computeUpstreamFingerprint,
  isNodeStale,
} from '../context-builder';
import { useCanvasStore } from '../../../../store/canvasStore';
import { ThoughtDagNoteData } from '../../types/thoughtdag';

test('ThoughtDAG Slice 2: Context Builder & Upstream Fingerprint', async (t) => {
  await t.test('1. deterministicHash produces reproducible and sensitive hashes', () => {
    const hash1 = deterministicHash('hello thoughtdag');
    const hash2 = deterministicHash('hello thoughtdag');
    const hash3 = deterministicHash('hello thoughtdag 2');

    assert.equal(hash1, hash2, 'Identical inputs must yield identical hashes');
    assert.notEqual(hash1, hash3, 'Distinct inputs must yield distinct hashes');
    assert.equal(typeof hash1, 'string');
    assert.ok(hash1.length >= 8);
  });

  await t.test('2. extractEffectiveNoteContent respects HighlightMode invariants', () => {
    const baseData: ThoughtDagNoteData = {
      title: 'Strategy Living Note',
      content: 'Line 1: Context overview.\nLine 2: Critical instruction: focus on retention.\nLine 3: Appendix.',
      selectedText: 'Critical instruction: focus on retention.',
      highlightMode: 'filter',
      tag: 'Directive',
      author: 'Maxim',
      updatedAt: Date.now(),
    };

    // Mode: filter (Token Diet - only selectedText)
    const filterResult = extractEffectiveNoteContent(baseData);
    assert.equal(filterResult.mode, 'filter');
    assert.equal(filterResult.content, 'Critical instruction: focus on retention.');

    // Mode: tag (fences with [Tag: ...])
    const tagData: ThoughtDagNoteData = { ...baseData, highlightMode: 'tag' };
    const tagResult = extractEffectiveNoteContent(tagData);
    assert.equal(tagResult.mode, 'tag');
    assert.ok(tagResult.content.includes('[Tag: Directive]'));
    assert.ok(tagResult.content.includes('Critical instruction: focus on retention.'));

    // Mode: off (Full markdown content)
    const offData: ThoughtDagNoteData = { ...baseData, highlightMode: 'off' };
    const offResult = extractEffectiveNoteContent(offData);
    assert.equal(offResult.mode, 'off');
    assert.equal(offResult.content, baseData.content);

    // Wire Scope Override: 'selection'
    const overrideResult = extractEffectiveNoteContent(offData, 'selection');
    assert.equal(overrideResult.mode, 'filter');
    assert.equal(overrideResult.content, 'Critical instruction: focus on retention.');
  });

  await t.test('3. getUpstreamAncestors and partitionContext separate materials and cross-references', () => {
    const noteNode: Node = {
      id: 'note-1',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'User Persona',
        content: 'E-commerce buyer personas with high conversion intent.',
        selectedText: 'high conversion intent',
        highlightMode: 'filter',
      },
    };

    const refNode: Node = {
      id: 'note-ref',
      type: 'thoughtDagNote',
      position: { x: 0, y: 150 },
      data: {
        title: 'Brand Voice',
        content: 'Tone should be bold, confident, Ukrainian pride.',
        highlightMode: 'off',
      },
    };

    const agentNode: Node = {
      id: 'agent-target',
      type: 'agentTask',
      position: { x: 300, y: 100 },
      data: {
        title: 'CMO Swarm Worker',
        prompt: 'Generate 3 high-converting video script hooks.',
      },
    };

    const edgeMain: Edge = {
      id: 'wire-1',
      source: 'note-1',
      target: 'agent-target',
    };

    const edgeRef: Edge = {
      id: 'wire-ref',
      source: 'note-ref',
      target: 'agent-target',
      data: { isCrossLink: true, contextDepth: 'quote' },
    };

    const nodes = [noteNode, refNode, agentNode];
    const edges = [edgeMain, edgeRef];

    const { ancestors } = getUpstreamAncestors('agent-target', nodes, edges);
    assert.equal(ancestors.length, 2);

    const partition = partitionContext('agent-target', ancestors, edges);
    assert.equal(partition.materials.length, 1);
    assert.equal(partition.materials[0].nodeId, 'note-1');
    assert.equal(partition.materials[0].content, 'high conversion intent'); // filtered

    assert.equal(partition.references.length, 1);
    assert.equal(partition.references[0].sourceId, 'note-ref');
    assert.equal(partition.references[0].depth, 'quote');
  });

  await t.test('4. buildContextFromWires constructs unified DAG prompt context', () => {
    const noteNode: Node = {
      id: 'note-brand',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'Brand DNA',
        content: 'Value prop: Autonomous AI Operating System.',
        highlightMode: 'off',
      },
    };

    const agentNode: Node = {
      id: 'agent-worker',
      type: 'agentTask',
      position: { x: 300, y: 0 },
      data: {
        title: 'Copywriter',
      },
    };

    const edge: Edge = {
      id: 'e-1',
      source: 'note-brand',
      target: 'agent-worker',
    };

    const result = buildContextFromWires('agent-worker', [noteNode, agentNode], [edge], {
      includeSystemPrompt: true,
      systemPrompt: 'You are the Chief Copywriter of DNK OS.',
    });

    assert.ok(result.messages.length >= 2);
    assert.equal(result.messages[0].role, 'system');
    assert.equal(result.messages[0].content, 'You are the Chief Copywriter of DNK OS.');

    assert.equal(result.messages[1].role, 'user');
    assert.ok(result.messages[1].content.includes('Brand DNA'));
    assert.ok(result.messages[1].content.includes('Autonomous AI Operating System.'));

    assert.ok(result.contextHash);
    assert.equal(typeof result.contextHash, 'string');
  });

  await t.test('5. computeUpstreamFingerprint and isNodeStale detect upstream mutations', () => {
    const noteNode: Node = {
      id: 'note-upstream',
      type: 'thoughtDagNote',
      position: { x: 0, y: 0 },
      data: {
        title: 'Pricing Spec',
        content: 'Price: $99',
        highlightMode: 'off',
      },
    };

    const agentNode: Node = {
      id: 'agent-downstream',
      type: 'agentTask',
      position: { x: 300, y: 0 },
      data: {
        title: 'Checkout Agent',
      },
    };

    const edge: Edge = {
      id: 'e-pricing',
      source: 'note-upstream',
      target: 'agent-downstream',
    };

    // Calculate baseline fingerprint
    const fp1 = computeUpstreamFingerprint('agent-downstream', [noteNode, agentNode], [edge]);
    assert.ok(fp1);

    // Node with matching stored fingerprint is NOT stale
    const freshAgent: Node = {
      ...agentNode,
      data: { ...agentNode.data, upstreamFingerprint: fp1, isStale: false },
    };

    const staleness1 = isNodeStale(freshAgent, [noteNode, freshAgent], [edge]);
    assert.equal(staleness1.isStale, false);

    // Mutate upstream note (e.g. price changed to $129)
    const mutatedNote: Node = {
      ...noteNode,
      data: { ...noteNode.data, content: 'Price: $129' },
    };

    const fp2 = computeUpstreamFingerprint('agent-downstream', [mutatedNote, freshAgent], [edge]);
    assert.notEqual(fp1, fp2, 'Fingerprint must change when upstream content changes');

    // Downstream node now detects that it is STALE!
    const staleness2 = isNodeStale(freshAgent, [mutatedNote, freshAgent], [edge]);
    assert.equal(staleness2.isStale, true);
  });

  await t.test('6. CanvasStore methods compileNodeContext and refreshNodeStaleness function correctly', () => {
    const store = useCanvasStore.getState();

    // Create note node
    const noteId = store.addThoughtDagNote(100, 100, 'Original living context', {
      title: 'Context Alpha',
      selectedText: 'living context',
      highlightMode: 'filter',
    });

    // Create agent node
    const agentId = store.addNode('agentTask', { x: 400, y: 100 }, {
      title: 'Swarm Worker',
    });

    // Connect wire note -> agent
    store.onConnect({
      source: noteId,
      target: agentId,
      sourceHandle: 'source-bottom',
      targetHandle: 'target-top',
    });

    // Compile context from wires
    const contextResult = store.compileNodeContext(agentId, {
      includeSystemPrompt: true,
      systemPrompt: 'You are an agent.',
    });

    assert.ok(contextResult);
    assert.equal(contextResult.partition.materials.length, 1);
    assert.equal(contextResult.partition.materials[0].content, 'living context'); // filter mode applied

    // Set stored fingerprint to match current state
    const currentFp = computeUpstreamFingerprint(agentId, useCanvasStore.getState().nodes, useCanvasStore.getState().edges);
    store.updateNodeData(agentId, { upstreamFingerprint: currentFp, isStale: false });

    // Refresh staleness -> should be 0 stale
    const check1 = store.refreshNodeStaleness(agentId);
    assert.equal(check1.staleCount, 0);

    // Mutate note content
    store.updateNodeData(noteId, {
      selectedText: 'mutated living context',
      content: 'Updated living context with mutations',
    });

    // Refresh staleness -> agent node should become STALE!
    const check2 = store.refreshNodeStaleness(agentId);
    assert.equal(check2.staleCount, 1);
    assert.ok(check2.updatedNodeIds.includes(agentId));

    const updatedAgent = useCanvasStore.getState().nodes.find((n) => n.id === agentId);
    assert.equal(updatedAgent?.data?.isStale, true);
  });
});
