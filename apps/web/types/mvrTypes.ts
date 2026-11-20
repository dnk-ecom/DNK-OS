// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/types/mvrTypes.ts"
// purpose: "TypeScript definitions for MVR Core Action Bus, SSE Streaming, HITL Approvals, and Canvas Sync"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

export type ActionTaskStatus =
  | 'PENDING'
  | 'QUEUED'
  | 'RUNNING'
  | 'WAITING_APPROVAL'
  | 'PENDING_VERIFICATION'
  | 'COMPLETED'
  | 'FAILED'
  | 'REJECTED'
  | 'ABORTED';

export type BusEventType =
  | 'TASK_SUBMITTED'
  | 'TASK_QUEUED'
  | 'TASK_STARTED'
  | 'TASK_COMPLETED'
  | 'TASK_FAILED'
  | 'TASK_REJECTED'
  | 'TASK_ROUTED'
  | 'TASK_DELEGATED'
  | 'SWARM_PARALLEL_STARTED'
  | 'SWARM_PARALLEL_COMPLETED'
  | 'SWARM_PIPELINE_STARTED'
  | 'SWARM_PIPELINE_COMPLETED'
  | 'ARTIFACT_CREATED'
  | 'APPROVAL_REQUESTED'
  | 'APPROVAL_RESOLVED'
  | 'CANVAS_NODE_MOVED'
  | 'CANVAS_BATCH_MUTATION'
  | 'SANDBOX_EXECUTION_COMPLETED'
  | 'SIMULATION_COMPLETED'
  | 'SIMULATION_ABORTED'
  | 'RUNTIME_PROGRESS'
  | 'RUNTIME_EVIDENCE'
  | 'RUNTIME_VERIFICATION_PASS'
  | 'RUNTIME_VERIFICATION_FAIL';

export interface StreamEnvelope {
  event_id: string;
  event_type: BusEventType;
  task_id: string;
  timestamp: string;
  payload: Record<string, any>;
}

export interface ActionTask {
  task_id: string;
  action_type: string;
  plugin_card_path?: string | null;
  payload: Record<string, any>;
  tenant_id: string;
  workspace_id: string;
  target_agent?: string | null;
  delegated_by?: string | null;
  routing_metadata?: Record<string, any>;
  created_at: string;
}

export interface ArtifactMetadata {
  artifact_id: string;
  uri: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  created_by_agent?: string | null;
  task_id?: string | null;
  checksum_sha256: string;
  created_at: string;
  storage_path: string;
}

export interface HitlApprovalRequest {
  request_id: string;
  action_id: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  diff_preview?: string | null;
  affected_files: string[];
  created_at: string;
  status: 'pending' | 'approved' | 'rejected';
  metadata?: Record<string, any>;
}

export interface HitlApprovalDecisionPayload {
  approved: boolean;
  reason?: string;
  approver_id: string;
}

export interface CanvasNodeMovePayload {
  node_id: string;
  x: number;
  y: number;
  delta_x?: number;
  delta_y?: number;
  canvas_id?: string;
}

export interface CanvasBatchMutationPayload {
  canvas_id: string;
  mutations: Array<{
    type: 'add_node' | 'update_node' | 'remove_node' | 'add_edge' | 'remove_edge';
    data: Record<string, any>;
  }>;
}

export interface MvrStreamClientOptions {
  baseUrl?: string;
  lastEventId?: string;
  onEvent?: (event: StreamEnvelope) => void;
  onError?: (err: Event | Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectIntervalMs?: number;
  maxReconnectIntervalMs?: number;
}
