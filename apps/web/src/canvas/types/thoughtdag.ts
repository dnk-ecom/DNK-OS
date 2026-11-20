// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/types/thoughtdag.ts"
// purpose: "Canonical TypeScript interfaces and data model for ThoughtDAG Infinite Palette living notes and context wires"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

export type HighlightMode = 'filter' | 'tag' | 'off';

export interface TextBlockItem {
  id: string; // e.g. 'p-0', 'p-1', or Obsidian block ref '^b123'
  text: string;
  order: number;
  tag?: string;
}

export interface TextSelectionHandle {
  id: string; // handle id, e.g. `handle-block-${blockId}` or `handle-sel-${id}`
  blockId: string;
  text: string;
  offset?: { start: number; end: number };
  position?: 'left' | 'right';
}

export interface ThoughtDagNoteData {
  title: string;
  content: string;
  selectedText?: string;
  blocks?: TextBlockItem[];
  selectionHandles?: TextSelectionHandle[];
  activeBlockId?: string;
  highlightMode: HighlightMode;
  tag?: string;
  upstreamFingerprint?: string; // SHA-256 hash of upstream contents
  isStale?: boolean;
  author: string;
  updatedAt: number;
}

export interface ContextNodeWire {
  id: string;
  source: string; // Source is always ThoughtDagNoteNode id
  target: string; // Target is downstream AgentTaskNode id
  sourceHandle?: string | null;
  targetHandle?: string | null;
  selectedText?: string;
  fingerprint?: string;
  data?: {
    scope?: 'full' | 'selection' | 'filtered' | 'block';
    blockId?: string;
    extractedText?: string;
    fingerprint?: string;
    isCrossLink?: boolean;
    contextDepth?: 'quote' | 'full';
    contextOrder?: number;
    [key: string]: any;
  };
}

export interface ContextMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  name?: string;
}

export interface MessageSource {
  layer: 'system' | 'material' | 'reference' | 'chain';
  nodeId?: string;
  part?: 'role' | 'material' | 'reference' | 'question' | 'response';
}

export interface ContextReference {
  sourceId: string;
  sourceTitle: string;
  edgeId: string;
  depth: 'quote' | 'full';
  content: string;
}

export interface MaterialBlock {
  nodeId: string;
  title: string;
  content: string;
  highlightMode: HighlightMode;
}

export interface ContextPartition {
  materials: MaterialBlock[];
  references: ContextReference[];
  mainline: { nodeId: string; title?: string; question?: string; response?: string }[];
}

export interface BuildContextResult {
  messages: ContextMessage[];
  sources: MessageSource[];
  rawText: string;
  contextHash: string;
  partition: ContextPartition;
}

export type ReevaluationPhase = 'idle' | 'gathering' | 'evaluating' | 'complete' | 'error' | 'cancelled';

export interface ReevaluationProgress {
  phase: ReevaluationPhase;
  current: number;
  total: number;
  activeNodeId?: string;
  activeLevelIndex?: number;
  totalLevels?: number;
  completedNodeIds: string[];
  failedNodeIds: string[];
  error?: string;
}

export interface ReevaluationPlan {
  totalNodes: number;
  levels: string[][];
  nodeOrder: string[];
  targetNodeIds: string[];
  dependencies: Record<string, string[]>;
  dependents: Record<string, string[]>;
}

export interface SconesMemoryItem {
  id?: string;
  topic: string;
  content: string;
  importance?: number;
  created_at?: string | number;
  memory_type?: string;
}

export interface SmartContextOptions {
  includeSystemPrompt?: boolean;
  systemPrompt?: string;
  maxContextDepth?: number;
  maxTokens?: number;
  pruneStrategy?: 'prioritize_near' | 'prioritize_blocks' | 'truncate_tail';
  includeSconesMemories?: boolean;
  sconesMemories?: SconesMemoryItem[];
  targetTaskPrompt?: string;
}

export interface SmartContextResult extends BuildContextResult {
  tokenEstimate: number;
  truncated: boolean;
  sconesMemoriesInjected?: number;
  fingerprint: string;
}

export interface ReevaluationResult {
  success: boolean;
  completedCount: number;
  errorCount: number;
  updatedNodeIds: string[];
  updatedEdgeIds: string[];
  errors?: Record<string, string>;
}


