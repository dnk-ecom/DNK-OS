// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/stream/flowStepParser.ts"
// purpose: "Dynamic Agent Flow Step to React Flow DAG Parser (assimilated from Worley UAIP ai-platform-frontend)."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import type { Node, Edge } from '@xyflow/react';

export type FlowStepStatus = 'queued' | 'running' | 'completed' | 'failed' | 'quarantined';

export interface FlowStep {
  step_id: string;
  agent_id: string;
  title: string;
  description?: string;
  status: FlowStepStatus;
  depends_on?: string[];
  duration_ms?: number;
  memory_mb?: number;
  output_summary?: string;
  actions?: Array<{ action_id: string; label_uk: string }>;
}

export interface ParseFlowOptions {
  startX?: number;
  startY?: number;
  columnWidth?: number;
  rowHeight?: number;
  gapX?: number;
  gapY?: number;
}

/**
 * Parses raw multi-agent execution steps (from SSE streams or Fan-Out/Fan-In Supervisor)
 * into a topologically arranged React Flow DAG subgraph.
 */
export function parseFlowSteps(
  steps: FlowStep[],
  options: ParseFlowOptions = {}
): { nodes: Node[]; edges: Edge[] } {
  if (!steps || steps.length === 0) {
    return { nodes: [], edges: [] };
  }

  const startX = options.startX ?? 100;
  const startY = options.startY ?? 100;
  const colWidth = options.columnWidth ?? 340;
  const gapX = options.gapX ?? 80;
  const gapY = options.gapY ?? 60;

  // Compute depth level for each step in the DAG
  const depthMap = new Map<string, number>();
  const stepMap = new Map<string, FlowStep>();

  steps.forEach((s) => stepMap.set(s.step_id, s));

  function getDepth(stepId: string, visited = new Set<string>()): number {
    if (depthMap.has(stepId)) return depthMap.get(stepId)!;
    if (visited.has(stepId)) return 0; // Guard against cycles
    visited.add(stepId);

    const step = stepMap.get(stepId);
    if (!step || !step.depends_on || step.depends_on.length === 0) {
      depthMap.set(stepId, 0);
      return 0;
    }

    const maxParentDepth = Math.max(
      ...step.depends_on.map((pId) => getDepth(pId, new Set(visited)))
    );
    const depth = maxParentDepth + 1;
    depthMap.set(stepId, depth);
    return depth;
  }

  steps.forEach((s) => getDepth(s.step_id));

  // Group steps by topological level
  const levels = new Map<number, FlowStep[]>();
  steps.forEach((s) => {
    const d = depthMap.get(s.step_id) ?? 0;
    if (!levels.has(d)) levels.set(d, []);
    levels.get(d)!.push(s);
  });

  const nodes: Node[] = [];
  const edges: Edge[] = [];

  levels.forEach((levelSteps, levelIdx) => {
    levelSteps.forEach((step, rowIdx) => {
      const x = startX + levelIdx * (colWidth + gapX);
      const y = startY + rowIdx * (260 + gapY);

      nodes.push({
        id: step.step_id,
        type: 'agentTaskNode',
        position: { x, y },
        data: {
          taskId: step.step_id,
          title: step.title,
          description: step.description || step.output_summary || '',
          targetAgent: step.agent_id,
          agent: step.agent_id,
          status: step.status.toUpperCase(),
          durationMs: step.duration_ms,
          memoryMb: step.memory_mb,
          actions: step.actions || [],
          dualSurfaceActions: step.actions || [],
          isLiving: true,
        },
      });

      // Create directed edges for dependencies
      if (step.depends_on && step.depends_on.length > 0) {
        step.depends_on.forEach((parentStepId) => {
          edges.push({
            id: `edge_${parentStepId}_to_${step.step_id}`,
            source: parentStepId,
            target: step.step_id,
            type: 'context-wire',
            animated: step.status === 'running',
            style: {
              stroke: step.status === 'completed' ? '#10b981' : step.status === 'failed' ? '#f43f5e' : '#6366f1',
              strokeWidth: 2,
            },
            data: {
              scope: 'all',
              status: step.status,
            },
          });
        });
      }
    });
  });

  return { nodes, edges };
}
