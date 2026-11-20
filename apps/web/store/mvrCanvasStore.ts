// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/store/mvrCanvasStore.ts"
// purpose: "Zustand state store for MVR Core Visual Working Canvas, live task graph, SSE event stream dispatch, and HITL approvals"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import { create } from 'zustand';
import {
  Node,
  Edge,
  Connection,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from '@xyflow/react';
import {
  ActionTaskStatus,
  StreamEnvelope,
  HitlApprovalRequest,
  ArtifactMetadata,
  HitlApprovalDecisionPayload,
} from '../types/mvrTypes';
import {
  submitApprovalDecision,
  sendCanvasNodeMove,
} from '../lib/api/mvr_stream_client';

export interface MvrTaskNodeData {
  [key: string]: unknown;
  taskId: string;
  actionType: string;
  targetAgent?: string;
  status: ActionTaskStatus;
  title: string;
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
  approvalRequestId?: string;
  approvalStatus?: 'pending' | 'approved' | 'rejected';
  affectedFiles?: string[];
  artifacts?: ArtifactMetadata[];
  memoryMb?: number;
  durationMs?: number;
  error?: string;
  updatedAt: string;
  payload?: Record<string, any>;
  runtimeProgress?: {
    completedSlices?: number;
    totalSlices?: number;
    progressPct: number;
    filesMutated?: number;
    verified: boolean;
    verificationCommand?: string;
  };
  runtimeEvidence?: {
    verified: boolean;
    testPassed: boolean;
    filesMutated: number;
    sealedAt: string;
    evidenceFile?: string;
  };
}

export interface MvrCanvasStore {
  // Graph state
  nodes: Node<MvrTaskNodeData>[];
  edges: Edge[];
  selectedNodeId: string | null;
  resetGraph: () => void;

  // HITL state
  pendingApprovals: HitlApprovalRequest[];
  isSubmittingDecision: boolean;

  // Stream state
  streamConnected: boolean;
  lastEventId: string | null;

  // XYFlow standard graph actions
  onNodesChange: (changes: NodeChange<Node<MvrTaskNodeData>>[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  selectNode: (nodeId: string | null) => void;

  // Spatial & Node Mutators
  upsertTaskNode: (
    taskData: Partial<MvrTaskNodeData> & { taskId: string },
    position?: { x: number; y: number }
  ) => void;
  updateNodePosition: (nodeId: string, x: number, y: number, syncRemote?: boolean) => void;

  // Stream & Event Handlers
  setStreamConnected: (connected: boolean) => void;
  handleStreamEnvelope: (envelope: StreamEnvelope) => void;

  // HITL Approval Actions
  syncPendingApprovals: (approvals: HitlApprovalRequest[]) => void;
  approveRequest: (requestId: string, approverId?: string) => Promise<void>;
  rejectRequest: (requestId: string, reason?: string, approverId?: string) => Promise<void>;

  // Simulation Controls
  activeSimulationId: string | null;
  isSimulationRunning: boolean;
  setSimulationRunning: (running: boolean, simulationId?: string | null) => void;
}

export const useMvrCanvasStore = create<MvrCanvasStore>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  resetGraph: () =>
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      pendingApprovals: [],
      isSimulationRunning: false,
      activeSimulationId: null,
    }),
  activeSimulationId: null,
  isSimulationRunning: false,
  setSimulationRunning: (running, simulationId = null) =>
    set({ isSimulationRunning: running, activeSimulationId: simulationId }),
  pendingApprovals: [],
  isSubmittingDecision: false,
  streamConnected: false,
  lastEventId: null,

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },

  selectNode: (nodeId) => {
    set({ selectedNodeId: nodeId });
  },

  setStreamConnected: (connected) => {
    set({ streamConnected: connected });
  },

  upsertTaskNode: (taskData, position) => {
    const { nodes } = get();
    const existingIndex = nodes.findIndex((n) => n.id === taskData.taskId);

    if (existingIndex >= 0) {
      const updatedNodes = [...nodes];
      const existing = updatedNodes[existingIndex];
      updatedNodes[existingIndex] = {
        ...existing,
        data: {
          ...existing.data,
          ...taskData,
          updatedAt: new Date().toISOString(),
        },
      };
      set({ nodes: updatedNodes });
    } else {
      const defaultPos = position || {
        x: 100 + (nodes.length % 5) * 280,
        y: 100 + Math.floor(nodes.length / 5) * 200,
      };

      const newNode: Node<MvrTaskNodeData> = {
        id: taskData.taskId,
        type: 'agentTaskNode',
        position: defaultPos,
        data: {
          taskId: taskData.taskId,
          actionType: taskData.actionType || 'agent_task',
          targetAgent: taskData.targetAgent || 'gerych_prime',
          status: taskData.status || 'PENDING',
          title: taskData.title || `Task ${taskData.taskId.slice(0, 8)}`,
          riskLevel: taskData.riskLevel || 'low',
          updatedAt: new Date().toISOString(),
          ...taskData,
        },
      };

      set({ nodes: [...nodes, newNode] });
    }
  },

  updateNodePosition: (nodeId, x, y, syncRemote = true) => {
    const { nodes } = get();
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;

    set({
      nodes: nodes.map((n) =>
        n.id === nodeId ? { ...n, position: { x, y } } : n
      ),
    });

    if (syncRemote) {
      sendCanvasNodeMove({
        node_id: nodeId,
        x,
        y,
      }).catch((err) => {
        console.error('[mvrCanvasStore] Failed to sync node move to backend:', err);
      });
    }
  },

  handleStreamEnvelope: (envelope) => {
    const { event_type, task_id, payload, event_id, timestamp = new Date().toISOString() } =
      envelope;
    set({ lastEventId: event_id });

    switch (event_type) {
      case 'TASK_SUBMITTED':
      case 'TASK_QUEUED':
        get().upsertTaskNode({
          taskId: task_id,
          status: 'QUEUED',
          actionType: payload?.action_type || 'task',
          targetAgent: payload?.target_agent,
          title: payload?.title || `Task ${task_id.slice(0, 8)}`,
        });
        break;

      case 'TASK_STARTED':
        get().upsertTaskNode({
          taskId: task_id,
          status: 'RUNNING',
          targetAgent: payload?.agent || payload?.target_agent,
        });
        break;

      case 'TASK_COMPLETED':
        if (payload?.simulation_completed) {
          set({ isSimulationRunning: false, activeSimulationId: null });
        }
        get().upsertTaskNode({
          taskId: payload?.node_id || task_id,
          status: 'COMPLETED',
          memoryMb: payload?.memory_mb,
          durationMs: payload?.duration_ms,
        });
        break;

      case 'SIMULATION_ABORTED': {
        const targetNodeId = payload?.node_id || task_id;
        const { nodes } = get();
        set({
          isSimulationRunning: false,
          activeSimulationId: null,
          nodes: nodes.map((n) => {
            if (!targetNodeId || n.id === targetNodeId || n.data.taskId === targetNodeId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  status: 'ABORTED' as ActionTaskStatus,
                  error: payload?.message || payload?.reason || 'Simulation aborted by operator',
                  updatedAt: timestamp,
                },
              };
            }
            return n;
          }),
        });
        break;
      }

      case 'SANDBOX_EXECUTION_COMPLETED': {
        const targetNodeId = payload?.node_id || task_id;
        const ramBytes = payload?.ram_bytes || 0;
        const memoryMb =
          payload?.memory_mb ?? (ramBytes ? +(ramBytes / (1024 * 1024)).toFixed(1) : undefined);
        const durationMs = payload?.duration_ms;
        get().upsertTaskNode({
          taskId: targetNodeId,
          memoryMb,
          durationMs,
        });
        break;
      }

      case 'TASK_FAILED':
        get().upsertTaskNode({
          taskId: task_id,
          status: 'FAILED',
          error: payload?.error || 'Task execution failed',
        });
        break;

      case 'APPROVAL_REQUESTED':
        {
          const req: HitlApprovalRequest = {
            request_id: payload?.request_id || `req-${Date.now()}`,
            action_id: payload?.action_id || task_id,
            risk_level: payload?.risk_level || 'high',
            description: payload?.description || 'Operator confirmation required',
            affected_files: payload?.affected_files || [],
            diff_preview: payload?.diff_preview || null,
            created_at: payload?.created_at || new Date().toISOString(),
            status: 'pending',
            metadata: payload?.metadata || {},
          };

          const pending = [...get().pendingApprovals.filter((p) => p.request_id !== req.request_id), req];
          set({ pendingApprovals: pending });

          get().upsertTaskNode({
            taskId: task_id,
            status: 'WAITING_APPROVAL',
            approvalRequestId: req.request_id,
            riskLevel: req.risk_level,
            approvalStatus: 'pending',
          });
        }
        break;

      case 'APPROVAL_RESOLVED':
        {
          const reqId = payload?.request_id;
          const status = payload?.status === 'approved' ? 'approved' : 'rejected';

          set({
            pendingApprovals: get().pendingApprovals.filter((p) => p.request_id !== reqId),
          });

          get().upsertTaskNode({
            taskId: task_id,
            status: status === 'approved' ? 'RUNNING' : 'REJECTED',
            approvalStatus: status,
          });
        }
        break;

      case 'ARTIFACT_CREATED':
        {
          const artMeta: ArtifactMetadata = {
            artifact_id: payload?.artifact_id || `art-${Date.now()}`,
            uri: payload?.uri || '',
            filename: payload?.filename || 'artifact.bin',
            content_type: payload?.content_type || 'text/plain',
            size_bytes: payload?.size_bytes || 0,
            checksum_sha256: payload?.checksum_sha256 || '',
            created_at: payload?.created_at || new Date().toISOString(),
            storage_path: payload?.storage_path || '',
          };

          const target = get().nodes.find((n) => n.id === task_id);
          const currentArts = target?.data.artifacts || [];
          get().upsertTaskNode({
            taskId: task_id,
            artifacts: [...currentArts, artMeta],
          });
        }
        break;

      case 'CANVAS_NODE_MOVED':
        if (payload?.node_id && payload?.x !== undefined && payload?.y !== undefined) {
          get().updateNodePosition(payload.node_id, payload.x, payload.y, false);
        }
        break;

      case 'CANVAS_BATCH_MUTATION':
        if (payload?.mutations && Array.isArray(payload.mutations)) {
          payload.mutations.forEach((mut: any) => {
            if (mut.type === 'add_node' || mut.type === 'update_node') {
              get().upsertTaskNode(mut.data);
            }
          });
        }
        break;

      default:
        break;
    }
  },

  syncPendingApprovals: (approvals) => {
    set({ pendingApprovals: approvals });
  },

  approveRequest: async (requestId, approverId = 'maksym') => {
    set({ isSubmittingDecision: true });
    try {
      const decisionPayload: HitlApprovalDecisionPayload = {
        approved: true,
        reason: 'Approved via Visual Working Canvas Cockpit',
        approver_id: approverId,
      };

      await submitApprovalDecision(requestId, decisionPayload);

      // Optimistically update store
      set({
        pendingApprovals: get().pendingApprovals.filter((p) => p.request_id !== requestId),
      });

      const affectedNode = get().nodes.find((n) => n.data.approvalRequestId === requestId);
      if (affectedNode) {
        get().upsertTaskNode({
          taskId: affectedNode.id,
          status: 'RUNNING',
          approvalStatus: 'approved',
        });
      }
    } catch (err) {
      console.error('[mvrCanvasStore] approveRequest failed:', err);
      throw err;
    } finally {
      set({ isSubmittingDecision: false });
    }
  },

  rejectRequest: async (requestId, reason = 'Rejected by Operator', approverId = 'maksym') => {
    set({ isSubmittingDecision: true });
    try {
      const decisionPayload: HitlApprovalDecisionPayload = {
        approved: false,
        reason,
        approver_id: approverId,
      };

      await submitApprovalDecision(requestId, decisionPayload);

      // Optimistically update store
      set({
        pendingApprovals: get().pendingApprovals.filter((p) => p.request_id !== requestId),
      });

      const affectedNode = get().nodes.find((n) => n.data.approvalRequestId === requestId);
      if (affectedNode) {
        get().upsertTaskNode({
          taskId: affectedNode.id,
          status: 'REJECTED',
          approvalStatus: 'rejected',
        });
      }
    } catch (err) {
      console.error('[mvrCanvasStore] rejectRequest failed:', err);
      throw err;
    } finally {
      set({ isSubmittingDecision: false });
    }
  },
}));
