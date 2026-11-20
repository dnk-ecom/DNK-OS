// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/json-canvas/converter.ts"
// purpose: "Bidirectional serializer between @xyflow/react canvas state and standard JSON Canvas specification (.canvas)"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-02"
// author: "DNK-e.com Maksym & Gerych"
// --- END DNK-MRH-HEADER ---

import type { Node, Edge } from '@xyflow/react';
import type { 
  JSONCanvasDocument, 
  JSONCanvasNode, 
  JSONCanvasEdge, 
  CanvasSide, 
  DNKExtendedJSONCanvasNode 
} from './types';

function handleToSide(handle?: string | null): CanvasSide | undefined {
  if (!handle) return undefined;
  const lower = handle.toLowerCase();
  if (lower.includes('top') || lower === 't') return 'top';
  if (lower.includes('right') || lower === 'r') return 'right';
  if (lower.includes('bottom') || lower === 'b') return 'bottom';
  if (lower.includes('left') || lower === 'l') return 'left';
  return undefined;
}

function sideToHandle(side?: CanvasSide): string | undefined {
  return side;
}

/**
 * Converts @xyflow/react Nodes and Edges into a standard JSON Canvas v1.0 document.
 */
export function reactFlowToJSONCanvas(nodes: Node[], edges: Edge[]): JSONCanvasDocument {
  const jsonNodes: JSONCanvasNode[] = nodes.map((node) => {
    const width = Number(node.width) || Number(node.measured?.width) || 360;
    const height = Number(node.height) || Number(node.measured?.height) || 320;
    const dnkType = node.type || 'text';

    const base: DNKExtendedJSONCanvasNode = {
      id: node.id,
      x: Math.round(node.position.x),
      y: Math.round(node.position.y),
      width,
      height,
      type: 'text',
      dnkType,
      text: typeof node.data?.content === 'string' && node.data.content.trim() 
        ? node.data.content 
        : typeof node.data?.text === 'string' && node.data.text.trim()
          ? node.data.text
          : typeof node.data?.description === 'string' && node.data.description.trim()
            ? node.data.description
            : `# ${node.data?.title || node.id}\n${JSON.stringify(node.data || {}, null, 2)}`,
      data: node.data || {}
    };

    return base;
  });

  const jsonEdges: JSONCanvasEdge[] = edges.map((edge) => {
    return {
      id: edge.id,
      fromNode: edge.source,
      fromSide: handleToSide(edge.sourceHandle),
      fromEnd: 'none',
      toNode: edge.target,
      toSide: handleToSide(edge.targetHandle),
      toEnd: 'arrow',
      label: typeof edge.label === 'string' ? edge.label : undefined,
      color: edge.style?.stroke ? String(edge.style.stroke) : undefined,
      dataFlow: edge.data ? {
        payloadType: (edge.data as any)?.payloadType,
        variableMapping: (edge.data as any)?.variableMapping
      } : undefined
    };
  });

  return {
    nodes: jsonNodes,
    edges: jsonEdges
  };
}

/**
 * Parses a JSON Canvas v1.0 document back into @xyflow/react Nodes and Edges.
 */
export function jsonCanvasToReactFlow(doc: JSONCanvasDocument): { nodes: Node[]; edges: Edge[] } {
  if (!doc || !Array.isArray(doc.nodes)) {
    return { nodes: [], edges: [] };
  }

  const nodes: Node[] = doc.nodes.map((jNode) => {
    const extended = jNode as DNKExtendedJSONCanvasNode;
    const text = ('text' in jNode && typeof (jNode as any).text === 'string')
      ? (jNode as any).text
      : (typeof extended.data?.content === 'string' ? extended.data.content : '');

    // Extract title from markdown header or fallback
    let title = extended.label || extended.data?.title || '';
    if (!title && text) {
      const firstLine = text.split('\n')[0].trim();
      title = firstLine.replace(/^[#\s]+/, '').trim();
    }
    if (!title) {
      title = jNode.id;
    }

    // Extract agent, status, and actions from markdown metadata or data
    const agentMatch = text.match(/[*_]*agent[*_]*\s*:\s*[`*_]*([a-zA-Z0-9_\-]+)[`*_]*/i);
    const targetAgent = agentMatch
      ? agentMatch[1].trim()
      : (extended.data?.targetAgent || extended.data?.agent || undefined);

    const statusMatch = text.match(/[*_]*status[*_]*\s*:\s*[`*_]*([^\n`*]+)[`*_]*/i);
    let status = statusMatch ? statusMatch[1].trim() : (extended.data?.status || 'QUEUED');
    if (status.includes('CRYSTALLIZED')) {
      status = 'COMPLETED';
    } else if (status.includes('DECOMPOSED')) {
      status = 'QUEUED';
    }

    // Default Dual-Surface actions based on agent role
    let actions: Array<{ action_id: string; label_uk: string }> = extended.data?.actions || [];
    if (actions.length === 0 && targetAgent) {
      if (targetAgent === 'dnk_shopify' || targetAgent === 'denchik') {
        actions = [
          { action_id: 'shopify.run_theme_check', label_uk: '🔍 Theme Check AST' },
          { action_id: 'shopify.package_theme', label_uk: '📦 Зібрати Preview ZIP' },
          { action_id: 'canvas.spawn_subtask', label_uk: '🌿 Розгалужити підзадачу' },
        ];
      } else if (targetAgent === 'strategist' || targetAgent === 'dnk_distribution') {
        actions = [
          { action_id: 'distribution.audit_copy', label_uk: '✍ Перевірити Tone of Voice' },
          { action_id: 'canvas.approve_artifact', label_uk: '🛡 Затвердити копірайт' },
          { action_id: 'canvas.spawn_subtask', label_uk: '🌿 Розгалужити підзадачу' },
        ];
      } else if (targetAgent === 'gerych' || targetAgent === 'gerych_auditor') {
        actions = [
          { action_id: 'shopify.audit_donor_theme', label_uk: '🧪 Деконструювати донора' },
          { action_id: 'scones.upsert_benchmark', label_uk: '📊 Оновити матрицю патернів' },
          { action_id: 'canvas.spawn_subtask', label_uk: '🌿 Розгалужити підзадачу' },
        ];
      } else {
        actions = [
          { action_id: 'canvas.spawn_subtask', label_uk: '🌿 Розгалужити підзадачу' },
          { action_id: 'canvas.approve_artifact', label_uk: '🛡 Затвердити артефакт' },
        ];
      }
    }

    // Determine ReactFlow node type
    let dnkType = extended.dnkType;
    if (!dnkType) {
      const isAgentTask = Boolean(targetAgent) && (
        /track|subtask|task|node_t\d+/i.test(jNode.id) ||
        /T\d+\.\d+|agent|task/i.test(text)
      );
      if (isAgentTask) {
        dnkType = 'agentTaskNode';
      } else {
        dnkType = 'thoughtDagNote';
      }
    }

    return {
      id: jNode.id,
      type: dnkType,
      position: { x: jNode.x, y: jNode.y },
      width: jNode.width,
      height: jNode.height,
      data: {
        ...(extended.data || {}),
        taskId: jNode.id,
        title,
        content: text,
        description: text,
        targetAgent: targetAgent || 'gerych_prime',
        agent: targetAgent || 'gerych_prime',
        status,
        actions,
        dualSurfaceActions: actions,
        highlightMode: 'all',
        isLiving: true,
      }
    };
  });

  const edges: Edge[] = (doc.edges || []).map((jEdge) => {
    return {
      id: jEdge.id,
      source: jEdge.fromNode,
      target: jEdge.toNode,
      sourceHandle: sideToHandle(jEdge.fromSide),
      targetHandle: sideToHandle(jEdge.toSide),
      type: jEdge.dataFlow ? 'dataFlow' : 'default',
      animated: Boolean(jEdge.dataFlow),
      label: jEdge.label,
      style: jEdge.color ? { stroke: jEdge.color, strokeWidth: 2 } : undefined,
      data: jEdge.dataFlow
    };
  });

  return { nodes, edges };
}
