// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/context/context-builder.ts"
// purpose: "Deterministic DAG context assembly, upstream ancestor walk, highlightMode filtering, and fingerprint staleness engine for ThoughtDAG Infinite Palette"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { Node, Edge } from '@xyflow/react';
import {
  HighlightMode,
  ThoughtDagNoteData,
  ContextMessage,
  MessageSource,
  ContextReference,
  MaterialBlock,
  ContextPartition,
  BuildContextResult,
} from '../types/thoughtdag';
import {
  isBlockHandleId,
  parseBlockIdFromHandle,
  extractBlockText,
} from '../nodes/textBlockParser';

/**
 * Pure deterministic 64-bit FNV-1a style string hash (hex/base36).
 * Safe for both browser (React/Vite) and Node/TSX test environments.
 */
export function deterministicHash(input: string): string {
  let h1 = 0x811c9dc5;
  let h2 = 0xcbf29ce4;

  for (let i = 0; i < input.length; i++) {
    const ch = input.charCodeAt(i);
    h1 ^= ch;
    h1 = Math.imul(h1, 0x01000193);

    h2 ^= ch;
    h2 = Math.imul(h2, 0x100000001b3);
  }

  const part1 = (h1 >>> 0).toString(16).padStart(8, '0');
  const part2 = (h2 >>> 0).toString(16).padStart(8, '0');
  return `${part1}${part2}`;
}

export interface BuildContextOptions {
  includeSystemPrompt?: boolean;
  systemPrompt?: string;
  maxContextDepth?: number;
}

/**
 * Traverses incoming edges backwards from targetNodeId to find all upstream ancestor nodes.
 * Returns ancestors in topological order (earliest dependencies first).
 */
export function getUpstreamAncestors(
  targetNodeId: string,
  nodes: Node[],
  edges: Edge[]
): { ancestors: Node[]; incomingEdges: Edge[] } {
  const nodeMap = new Map<string, Node>(nodes.map((n) => [n.id, n]));
  const incomingEdgeMap = new Map<string, Edge[]>();

  for (const edge of edges) {
    const list = incomingEdgeMap.get(edge.target) || [];
    list.push(edge);
    incomingEdgeMap.set(edge.target, list);
  }

  const visited = new Set<string>();
  const ancestorNodes: Node[] = [];
  const relevantEdges: Edge[] = [];

  function dfs(currId: string) {
    const inEdges = incomingEdgeMap.get(currId) || [];
    for (const e of inEdges) {
      relevantEdges.push(e);
      if (!visited.has(e.source)) {
        visited.add(e.source);
        dfs(e.source);
        const sourceNode = nodeMap.get(e.source);
        if (sourceNode) {
          ancestorNodes.push(sourceNode);
        }
      }
    }
  }

  dfs(targetNodeId);

  return {
    ancestors: ancestorNodes,
    incomingEdges: relevantEdges,
  };
}

/**
 * Extracts effective text content from a ThoughtDAG living note according to its highlightMode,
 * edge wire scope, or block-level connection handle.
 */
export function extractEffectiveNoteContent(
  data: ThoughtDagNoteData | undefined,
  edgeWireScope?: string,
  sourceHandle?: string | null,
  edgeData?: Record<string, any>
): { content: string; mode: HighlightMode } {
  if (!data) {
    return { content: '', mode: 'off' };
  }

  const mode = data.highlightMode || 'off';
  const fullContent = data.content || '';
  const selectedText = data.selectedText || '';

  // 1. Block-level handle or explicit block scope
  const blockId = edgeData?.blockId || (sourceHandle ? parseBlockIdFromHandle(sourceHandle) : null);
  if ((edgeWireScope === 'block' || isBlockHandleId(sourceHandle)) && blockId) {
    const blockText = extractBlockText(fullContent, blockId, data.blocks);
    if (blockText && blockText.trim()) {
      return { content: blockText.trim(), mode: 'filter' };
    }
  }

  // 2. Explicit extracted snippet from selection handle
  if (edgeData?.extractedText && typeof edgeData.extractedText === 'string' && edgeData.extractedText.trim()) {
    return { content: edgeData.extractedText.trim(), mode: 'filter' };
  }

  // 3. If edge has explicit wire scope override
  if (edgeWireScope === 'selection' && selectedText.trim()) {
    return { content: selectedText.trim(), mode: 'filter' };
  }

  // 4. HighlightMode evaluation
  switch (mode) {
    case 'filter':
      // ZERO-WASTE token diet: only pass selected text if present
      return {
        content: selectedText.trim() ? selectedText.trim() : fullContent,
        mode: 'filter',
      };

    case 'tag':
      if (selectedText.trim()) {
        const tagLabel = data.tag ? `Tag: ${data.tag}` : 'Important Context';
        const formatted = `[${tagLabel}]\n${selectedText.trim()}\n[/${tagLabel}]`;
        return { content: formatted, mode: 'tag' };
      }
      return { content: fullContent, mode: 'tag' };

    case 'off':
    default:
      return { content: fullContent, mode: 'off' };
  }
}

/**
 * Partitions ancestors into materials (living notes), references (cross-links), and mainline turns.
 */
export function partitionContext(
  targetNodeId: string,
  ancestors: Node[],
  edges: Edge[]
): ContextPartition {
  const materials: MaterialBlock[] = [];
  const references: ContextReference[] = [];
  const mainline: { nodeId: string; title?: string; question?: string; response?: string }[] = [];

  const targetEdges = edges.filter((e) => e.target === targetNodeId);
  const targetEdgeBySource = new Map<string, Edge>(targetEdges.map((e) => [e.source, e]));

  for (const node of ancestors) {
    const edge = targetEdgeBySource.get(node.id) || edges.find((e) => e.source === node.id && e.target === targetNodeId);
    const isReference = edge?.data?.isCrossLink === true || edge?.style?.strokeDasharray !== undefined;

    // A. ThoughtDAG Note or Markdown Note
    if (node.type === 'thoughtDagNote' || node.type === 'note') {
      const noteData = (node.data || {}) as unknown as ThoughtDagNoteData;
      const edgeData = (edge?.data || {}) as Record<string, any>;
      const sourceHandle = edge?.sourceHandle || null;
      const { content, mode } = extractEffectiveNoteContent(
        noteData,
        typeof edgeData.scope === 'string' ? edgeData.scope : undefined,
        sourceHandle,
        edgeData
      );

      if (isReference) {
        references.push({
          sourceId: node.id,
          sourceTitle: noteData.title || `Note ${node.id}`,
          edgeId: edge?.id || '',
          depth: edgeData.contextDepth === 'quote' ? 'quote' : 'full',
          content,
        });
      } else {
        materials.push({
          nodeId: node.id,
          title: noteData.title || `Note ${node.id}`,
          content,
          highlightMode: mode,
        });
      }
      continue;
    }

    // B. Conversation / Agent Turn (Mainline)
    if (node.type === 'agentTask' || node.type === 'promptNode' || node.type === 'default') {
      const nData = (node.data || {}) as Record<string, any>;
      mainline.push({
        nodeId: node.id,
        title: typeof nData.title === 'string' ? nData.title : (typeof nData.label === 'string' ? nData.label : undefined),
        question: typeof nData.prompt === 'string' ? nData.prompt : (typeof nData.instruction === 'string' ? nData.instruction : (typeof nData.question === 'string' ? nData.question : undefined)),
        response: typeof nData.response === 'string' ? nData.response : (typeof nData.output === 'string' ? nData.output : (typeof nData.content === 'string' ? nData.content : undefined)),
      });
      continue;
    }

    // C. Generic Fallback Node with content
    const genData = (node.data || {}) as Record<string, any>;
    if (genData.content || genData.text) {
      materials.push({
        nodeId: node.id,
        title: typeof genData.title === 'string' ? genData.title : `Node ${node.id}`,
        content: String(genData.content || genData.text),
        highlightMode: 'off',
      });
    }
  }

  return {
    materials,
    references,
    mainline,
  };
}

/**
 * Assembles a unified DAG prompt context from upstream wires for a downstream agent node.
 */
export function buildContextFromWires(
  targetNodeId: string,
  nodes: Node[],
  edges: Edge[],
  options: BuildContextOptions = {}
): BuildContextResult {
  const { ancestors: upstreamAncestors } = getUpstreamAncestors(targetNodeId, nodes, edges);
  const targetNode = nodes.find((n) => n.id === targetNodeId);
  const isTargetNote = targetNode?.type === 'thoughtDagNote' || targetNode?.type === 'ThoughtDagNoteNode';
  const ancestors = isTargetNote && !upstreamAncestors.some((a) => a.id === targetNodeId)
    ? [targetNode!, ...upstreamAncestors]
    : upstreamAncestors;
  const partition = partitionContext(targetNodeId, ancestors, edges);

  const messages: ContextMessage[] = [];
  const sources: MessageSource[] = [];
  const rawSections: string[] = [];

  // 1. System Prompt Layer
  if (options.includeSystemPrompt && options.systemPrompt) {
    messages.push({
      role: 'system',
      content: options.systemPrompt,
    });
    sources.push({ layer: 'system', part: 'role' });
    rawSections.push(`SYSTEM:\n${options.systemPrompt}`);
  }

  // 2. Materials Layer (Living Notes Context)
  if (partition.materials.length > 0) {
    const materialsHeader = '--- MATERIALS & LIVING NOTES CONTEXT ---';
    const materialsContent = partition.materials
      .map((m) => `### [Material: ${m.title}] (Node: ${m.nodeId})\n${m.content}`)
      .join('\n\n');

    const combinedMaterials = `${materialsHeader}\n${materialsContent}`;
    messages.push({
      role: 'user',
      content: combinedMaterials,
    });
    for (const m of partition.materials) {
      sources.push({ layer: 'material', nodeId: m.nodeId, part: 'material' });
    }
    rawSections.push(combinedMaterials);
  }

  // 3. References Layer (Cross-links)
  if (partition.references.length > 0) {
    const referencesHeader = '--- CROSS-REFERENCES ---';
    const referencesContent = partition.references
      .map((r) => `> Reference from [${r.sourceTitle}]:\n> ${r.content}`)
      .join('\n\n');

    const combinedRefs = `${referencesHeader}\n${referencesContent}`;
    messages.push({
      role: 'user',
      content: combinedRefs,
    });
    for (const r of partition.references) {
      sources.push({ layer: 'reference', nodeId: r.sourceId, part: 'reference' });
    }
    rawSections.push(combinedRefs);
  }

  // 4. Mainline Dialogue Layer
  for (const turn of partition.mainline) {
    if (turn.question) {
      messages.push({
        role: 'user',
        content: turn.question,
      });
      sources.push({ layer: 'chain', nodeId: turn.nodeId, part: 'question' });
      rawSections.push(`USER (${turn.nodeId}):\n${turn.question}`);
    }
    if (turn.response) {
      messages.push({
        role: 'assistant',
        content: turn.response,
      });
      sources.push({ layer: 'chain', nodeId: turn.nodeId, part: 'response' });
      rawSections.push(`ASSISTANT (${turn.nodeId}):\n${turn.response}`);
    }
  }

  const rawText = rawSections.join('\n\n');
  const contextHash = deterministicHash(rawText);

  return {
    messages,
    sources,
    rawText,
    contextHash,
    partition,
  };
}

/**
 * Computes deterministic upstream fingerprint for a node based on all its upstream dependencies.
 */
export function computeUpstreamFingerprint(
  targetNodeId: string,
  nodes: Node[],
  edges: Edge[]
): string {
  const { ancestors, incomingEdges } = getUpstreamAncestors(targetNodeId, nodes, edges);

  if (ancestors.length === 0) {
    return '';
  }

  // Normalize ancestor data to avoid non-deterministic order
  const normalized = ancestors.map((node) => {
    const data = node.data || {};
    return {
      id: node.id,
      type: node.type,
      title: data.title,
      content: data.content,
      selectedText: data.selectedText,
      highlightMode: data.highlightMode,
      response: data.response,
      tag: data.tag,
    };
  });

  const normalizedEdges = incomingEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    scope: e.data?.scope,
    blockId: (e.data as any)?.blockId,
    sourceHandle: e.sourceHandle,
  }));

  const payload = JSON.stringify({
    ancestors: normalized,
    edges: normalizedEdges,
  });

  return deterministicHash(payload);
}

/**
 * Checks if a node's existing upstreamFingerprint differs from its freshly calculated upstream fingerprint.
 */
export function isNodeStale(
  node: Node,
  nodes: Node[],
  edges: Edge[]
): { isStale: boolean; currentFingerprint: string; storedFingerprint?: string } {
  const currentFingerprint = computeUpstreamFingerprint(node.id, nodes, edges);
  const storedFingerprint = ((node.data || {}) as Record<string, any>)?.upstreamFingerprint as string | undefined;

  if (!storedFingerprint) {
    return {
      isStale: false,
      currentFingerprint,
      storedFingerprint,
    };
  }

  const isStale = Boolean(currentFingerprint && storedFingerprint !== currentFingerprint);

  return {
    isStale,
    currentFingerprint,
    storedFingerprint,
  };
}

export interface GraphStalenessReport {
  staleNodeIds: string[];
  staleEdgeIds: string[];
  staleBranchCount: number;
}

/**
 * Traverses the DAG to evaluate staleness across all nodes and connecting edges.
 * If an upstream note/turn changes, downstream nodes whose stored fingerprint differs
 * are flagged as isStale: true.
 * Furthermore, all incoming edges to stale downstream nodes are flagged with edge.data.isStale: true.
 */
export function evaluateGraphStaleness(
  nodes: Node[],
  edges: Edge[],
  targetNodeId?: string
): {
  report: GraphStalenessReport;
  nextNodes: Node[];
  nextEdges: Edge[];
} {
  const staleNodeSet = new Set<string>();
  const staleEdgeSet = new Set<string>();

  const nextNodes = nodes.map((node) => {
    if (targetNodeId && node.id !== targetNodeId) {
      if ((node.data as any)?.isStale) {
        staleNodeSet.add(node.id);
      }
      return node;
    }

    const { isStale } = isNodeStale(node, nodes, edges);
    if (isStale) {
      staleNodeSet.add(node.id);
    }

    const currentStoredStale = Boolean((node.data as any)?.isStale);
    if (currentStoredStale !== isStale) {
      return {
        ...node,
        data: {
          ...node.data,
          isStale,
        },
      };
    }
    return node;
  });

  const nextEdges = edges.map((edge) => {
    // If the target node is stale, this wire is stale because the downstream context is outdated.
    const isTargetStale = staleNodeSet.has(edge.target);
    if (isTargetStale) {
      staleEdgeSet.add(edge.id);
    }

    const currentEdgeStale = Boolean((edge.data as any)?.isStale);
    if (currentEdgeStale !== isTargetStale) {
      return {
        ...edge,
        data: {
          ...(edge.data || {}),
          isStale: isTargetStale,
        },
      };
    }
    return edge;
  });

  return {
    report: {
      staleNodeIds: Array.from(staleNodeSet),
      staleEdgeIds: Array.from(staleEdgeSet),
      staleBranchCount: staleNodeSet.size,
    },
    nextNodes,
    nextEdges,
  };
}
