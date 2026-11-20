// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/context/dag-reevaluation.ts"
// purpose: "Topological DAG re-evaluation planner, token-budgeted smart context gathering with SCONES memory, and level-by-level parallel execution engine"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { Node, Edge } from '@xyflow/react';
import {
  ReevaluationPlan,
  ReevaluationProgress,
  ReevaluationResult,
  SmartContextOptions,
  SmartContextResult,
  SconesMemoryItem,
  ContextMessage,
  MessageSource,
} from '../types/thoughtdag';
import {
  buildContextFromWires,
  computeUpstreamFingerprint,
  isNodeStale,
  getUpstreamAncestors,
} from './context-builder';

/**
 * Rough token estimation: ~4 characters per token for English/code/markdown.
 */
export function estimateTokens(text: string): number {
  if (!text) return 0;
  return Math.ceil(text.length / 4);
}

export interface ReevaluationPlanOptions {
  targetNodeId?: string;
  onlyStale?: boolean;
}

/**
 * Computes a topological execution plan partitioned into parallel levels.
 * Handles single-node targeted refresh, downstream branch re-evaluation, or full canvas DAG recalculation.
 */
export function getReevaluationPlan(
  nodes: Node[],
  edges: Edge[],
  options: ReevaluationPlanOptions = {}
): ReevaluationPlan {
  const { targetNodeId, onlyStale = true } = options;

  const nodeMap = new Map<string, Node>(nodes.map((n) => [n.id, n]));
  const dependencies: Record<string, string[]> = {};
  const dependents: Record<string, string[]> = {};

  for (const n of nodes) {
    dependencies[n.id] = [];
    dependents[n.id] = [];
  }

  for (const e of edges) {
    if (nodeMap.has(e.source) && nodeMap.has(e.target)) {
      if (!dependencies[e.target].includes(e.source)) {
        dependencies[e.target].push(e.source);
      }
      if (!dependents[e.source].includes(e.target)) {
        dependents[e.source].push(e.target);
      }
    }
  }

  // 1. Identify Candidate Node Set
  let candidateIds: Set<string>;

  if (targetNodeId) {
    candidateIds = new Set<string>();
    // BFS down to collect all downstream dependents
    const queue = [targetNodeId];
    while (queue.length > 0) {
      const curr = queue.shift()!;
      candidateIds.add(curr);
      for (const childId of dependents[curr] || []) {
        if (!candidateIds.has(childId)) {
          candidateIds.add(childId);
          queue.push(childId);
        }
      }
    }
  } else {
    candidateIds = new Set<string>(nodes.map((n) => n.id));
  }

  // 2. Filter Candidate Nodes if onlyStale is enabled
  const selectedNodeIds = new Set<string>();

  if (onlyStale) {
    // If targetNodeId was explicitly specified, always include targetNodeId if it is in candidates
    if (targetNodeId && candidateIds.has(targetNodeId)) {
      selectedNodeIds.add(targetNodeId);
    }

    // Pass 1: Add nodes directly marked or computed as stale
    for (const nid of candidateIds) {
      const node = nodeMap.get(nid);
      if (!node) continue;
      const isExplicitlyStale = Boolean((node.data as any)?.isStale);
      const computedStale = isNodeStale(node, nodes, edges).isStale;
      if (isExplicitlyStale || computedStale) {
        selectedNodeIds.add(nid);
      }
    }

    // Pass 2: Cascade down - any downstream dependent of a node in selectedNodeIds must also be re-evaluated
    let added = true;
    while (added) {
      added = false;
      for (const nid of candidateIds) {
        if (selectedNodeIds.has(nid)) continue;
        const parents = dependencies[nid] || [];
        const hasReevaluatedParent = parents.some((pid) => selectedNodeIds.has(pid));
        if (hasReevaluatedParent) {
          selectedNodeIds.add(nid);
          added = true;
        }
      }
    }
  } else {
    for (const nid of candidateIds) {
      selectedNodeIds.add(nid);
    }
  }

  // 3. Compute Topological Sort & Parallel Levels (Kahn's Algorithm on Induced Subgraph)
  const inDegree: Record<string, number> = {};
  for (const nid of selectedNodeIds) {
    const parents = dependencies[nid] || [];
    inDegree[nid] = parents.filter((p) => selectedNodeIds.has(p)).length;
  }

  const levels: string[][] = [];
  const nodeOrder: string[] = [];
  const remainingNodes = new Set(selectedNodeIds);

  while (remainingNodes.size > 0) {
    // Find all nodes with inDegree === 0 in the current remaining subgraph
    const currentLevel: string[] = [];
    for (const nid of remainingNodes) {
      if (inDegree[nid] === 0) {
        currentLevel.push(nid);
      }
    }

    if (currentLevel.length === 0) {
      // Cycle detected fallback: pick the node with smallest in-degree
      let minIn = Infinity;
      let fallbackNid: string | null = null;
      for (const nid of remainingNodes) {
        if (inDegree[nid] < minIn) {
          minIn = inDegree[nid];
          fallbackNid = nid;
        }
      }
      if (fallbackNid) {
        currentLevel.push(fallbackNid);
      } else {
        break;
      }
    }

    levels.push(currentLevel);
    for (const nid of currentLevel) {
      nodeOrder.push(nid);
      remainingNodes.delete(nid);

      // Decrement in-degree for downstream children in remaining set
      for (const childId of dependents[nid] || []) {
        if (remainingNodes.has(childId)) {
          inDegree[childId] = Math.max(0, inDegree[childId] - 1);
        }
      }
    }
  }

  return {
    totalNodes: nodeOrder.length,
    levels,
    nodeOrder,
    targetNodeIds: Array.from(selectedNodeIds),
    dependencies,
    dependents,
  };
}

/**
 * Gathers rich smart context for a target node with token budget management,
 * priority pruning, and optional SCONES long-term episodic memory injection.
 */
export function gatherSmartContext(
  targetNodeId: string,
  nodes: Node[],
  edges: Edge[],
  options: SmartContextOptions = {}
): SmartContextResult {
  const {
    maxTokens = 4000,
    pruneStrategy = 'prioritize_blocks',
    includeSconesMemories = false,
    sconesMemories = [],
    targetTaskPrompt,
  } = options;

  // 1. Gather baseline context via wire connections
  const baseContext = buildContextFromWires(targetNodeId, nodes, edges, {
    includeSystemPrompt: options.includeSystemPrompt,
    systemPrompt: options.systemPrompt,
    maxContextDepth: options.maxContextDepth,
  });

  const messages: ContextMessage[] = [...baseContext.messages];
  const sources: MessageSource[] = [...baseContext.sources];
  let rawText = baseContext.rawText;
  let sconesMemoriesInjected = 0;

  // 2. Augment with SCONES Long-Term Memories if requested
  if (includeSconesMemories && sconesMemories && sconesMemories.length > 0) {
    const memoryBlocks: string[] = [];
    for (const mem of sconesMemories) {
      sconesMemoriesInjected++;
      const block = `[SCONES Long-Term Memory: ${mem.topic}]\n${mem.content.trim()}\n[/SCONES Long-Term Memory]`;
      memoryBlocks.push(block);
    }

    const memorySection = `\n\n### Long-Term Episodic Memory (SCONES)\n${memoryBlocks.join('\n\n')}`;
    rawText += memorySection;

    // Inject into messages list right before user prompt or as system guidance
    messages.push({
      role: 'system',
      content: memorySection.trim(),
    });
    sources.push({
      layer: 'material',
      part: 'material',
    });
  }

  // 3. Token Budget Pruning
  let tokenEstimate = estimateTokens(rawText);
  let truncated = false;

  if (tokenEstimate > maxTokens) {
    truncated = true;
    const maxChars = maxTokens * 4;

    if (pruneStrategy === 'prioritize_blocks') {
      // Keep materials that are block/selection level, prune full raw materials
      const preservedMaterials = baseContext.partition.materials.filter(
        (m) => m.highlightMode === 'filter' || m.content.length < 500
      );
      const prunedText = preservedMaterials.map((m) => `[Context from Note: ${m.title}]\n${m.content}\n[/Context from Note]`).join('\n\n');
      rawText = prunedText.slice(0, maxChars) + '\n\n... [Truncated to fit token diet]';
    } else if (pruneStrategy === 'prioritize_near') {
      // Keep only immediate parents
      const immediateIncoming = edges.filter((e) => e.target === targetNodeId).map((e) => e.source);
      const nearMaterials = baseContext.partition.materials.filter((m) => immediateIncoming.includes(m.nodeId));
      rawText = nearMaterials.map((m) => `[Context: ${m.title}]\n${m.content}`).join('\n\n').slice(0, maxChars);
    } else {
      // Default: truncate tail
      rawText = rawText.slice(0, maxChars) + '\n\n... [Truncated: Token Budget Exceeded]';
    }

    tokenEstimate = estimateTokens(rawText);
  }

  // 4. Calculate Fresh Fingerprint
  const fingerprint = computeUpstreamFingerprint(targetNodeId, nodes, edges);

  return {
    messages,
    sources,
    rawText,
    contextHash: baseContext.contextHash,
    partition: baseContext.partition,
    tokenEstimate,
    truncated,
    sconesMemoriesInjected,
    fingerprint,
  };
}

export type NodeEvaluatorFn = (
  node: Node,
  context: SmartContextResult,
  signal?: AbortSignal
) => Promise<string | Record<string, any>>;

export interface ReevaluationExecuteOptions {
  nodes: Node[];
  edges: Edge[];
  evaluateNodeFn?: NodeEvaluatorFn;
  onProgress?: (progress: ReevaluationProgress) => void;
  signal?: AbortSignal;
  smartContextOptions?: SmartContextOptions;
}

/**
 * Default fallback evaluator when no custom LLM backend function is supplied.
 * Synthesizes an updated response based on smart context and current node prompt.
 */
export async function defaultNodeEvaluator(
  node: Node,
  context: SmartContextResult,
  signal?: AbortSignal
): Promise<string> {
  if (signal?.aborted) {
    throw new Error('Reevaluation aborted');
  }

  const nodeData = (node.data || {}) as Record<string, any>;
  const title = nodeData.title || nodeData.label || `Task ${node.id}`;
  const prompt = nodeData.prompt || nodeData.instruction || nodeData.question || 'Synthesize task output';
  const materialsCount = context.partition.materials.length;
  const referencesCount = context.partition.references.length;

  // Short async tick to simulate processing
  await new Promise((resolve) => setTimeout(resolve, 10));

  return `[Re-evaluated Output for: ${title}]\nInstruction: ${prompt}\nIntegrated ${materialsCount} upstream notes and ${referencesCount} references.\nContext Hash: ${context.fingerprint.slice(0, 10)} (Tokens: ~${context.tokenEstimate})\nUpdated at: ${new Date().toISOString()}`;
}

/**
 * Executes a DAG re-evaluation plan level-by-level, updating node states, fingerprints,
 * clearing staleness flags, and tracking progress.
 */
export async function executeDAGReevaluation(
  plan: ReevaluationPlan,
  options: ReevaluationExecuteOptions
): Promise<{
  result: ReevaluationResult;
  updatedNodes: Node[];
  updatedEdges: Edge[];
}> {
  const {
    nodes,
    edges,
    evaluateNodeFn = defaultNodeEvaluator,
    onProgress,
    signal,
    smartContextOptions,
  } = options;

  let currentNodes = [...nodes];
  let currentEdges = [...edges];
  const completedNodeIds: string[] = [];
  const failedNodeIds: string[] = [];
  const errors: Record<string, string> = {};

  const total = plan.totalNodes;
  let current = 0;

  const emitProgress = (phase: ReevaluationProgress['phase'], activeNodeId?: string, activeLevelIndex?: number) => {
    if (onProgress) {
      onProgress({
        phase,
        current,
        total,
        activeNodeId,
        activeLevelIndex,
        totalLevels: plan.levels.length,
        completedNodeIds: [...completedNodeIds],
        failedNodeIds: [...failedNodeIds],
      });
    }
  };

  emitProgress('gathering', undefined, 0);

  try {
    for (let levelIdx = 0; levelIdx < plan.levels.length; levelIdx++) {
      const level = plan.levels[levelIdx];
      if (signal?.aborted) {
        emitProgress('cancelled');
        throw new Error('Reevaluation was cancelled by user');
      }

      emitProgress('evaluating', level[0], levelIdx);

      // Execute all nodes in the current level concurrently
      const levelPromises = level.map(async (nodeId) => {
        const node = currentNodes.find((n) => n.id === nodeId);
        if (!node) return null;

        try {
          if (signal?.aborted) {
            throw new Error('Aborted');
          }

          // Gather fresh smart context with current graph state
          const smartCtx = gatherSmartContext(nodeId, currentNodes, currentEdges, smartContextOptions);

          // Run evaluation
          const evalResult = await evaluateNodeFn(node, smartCtx, signal);

          const responseText = typeof evalResult === 'string' ? evalResult : evalResult.response || evalResult.output;
          const patchData = typeof evalResult === 'object' && evalResult !== null ? evalResult : { response: responseText };

          return {
            nodeId,
            success: true,
            patch: {
              ...patchData,
              response: responseText,
              upstreamFingerprint: smartCtx.fingerprint,
              isStale: false,
              isReevaluating: false,
              lastEvaluatedAt: Date.now(),
            },
            incomingEdges: currentEdges.filter((e) => e.target === nodeId).map((e) => e.id),
          };
        } catch (err: any) {
          return {
            nodeId,
            success: false,
            error: err?.message || String(err),
          };
        }
      });

      const results = await Promise.all(levelPromises);

      for (const res of results) {
        if (!res) continue;
        current++;
        if (res.success && res.patch) {
          completedNodeIds.push(res.nodeId);

          // Update node in state
          currentNodes = currentNodes.map((n) => {
            if (n.id === res.nodeId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  ...res.patch,
                },
              };
            }
            return n;
          });

          // Clear isStale flag on incoming edges to this node
          if (res.incomingEdges && res.incomingEdges.length > 0) {
            const incomingSet = new Set(res.incomingEdges);
            currentEdges = currentEdges.map((e) => {
              if (incomingSet.has(e.id)) {
                return {
                  ...e,
                  data: {
                    ...(e.data || {}),
                    isStale: false,
                  },
                };
              }
              return e;
            });
          }
        } else {
          failedNodeIds.push(res.nodeId);
          errors[res.nodeId] = res.error || 'Evaluation failed';
        }
      }
    }

    emitProgress(failedNodeIds.length === 0 ? 'complete' : 'error');

    return {
      result: {
        success: failedNodeIds.length === 0,
        completedCount: completedNodeIds.length,
        errorCount: failedNodeIds.length,
        updatedNodeIds: completedNodeIds,
        updatedEdgeIds: currentEdges.filter((e) => !(e.data as any)?.isStale).map((e) => e.id),
        errors: Object.keys(errors).length > 0 ? errors : undefined,
      },
      updatedNodes: currentNodes,
      updatedEdges: currentEdges,
    };
  } catch (err: any) {
    emitProgress(signal?.aborted ? 'cancelled' : 'error');
    throw err;
  }
}
