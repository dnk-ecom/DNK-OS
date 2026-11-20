// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_AgentTaskNode"
// purpose: "XYFlow Custom Node for MVR Agent Tasks, Live Status Badges, Artifact previews, and 1-Click HITL Approval"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import React, { memo, useState } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Bot,
  FileText,
  Clock,
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Play,
  Sparkles,
} from 'lucide-react';
import { useMvrCanvasStore, MvrTaskNodeData } from '@/store/mvrCanvasStore';
import { useCanvasStore } from '@/store/canvasStore';

const AGENT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  antigravity: { bg: 'bg-emerald-950/40', text: 'text-emerald-300', border: 'border-emerald-500/40' },
  denchik: { bg: 'bg-blue-950/40', text: 'text-blue-300', border: 'border-blue-500/40' },
  gerych_prime: { bg: 'bg-purple-950/40', text: 'text-purple-300', border: 'border-purple-500/40' },
  goldfish: { bg: 'bg-amber-950/40', text: 'text-amber-300', border: 'border-amber-500/40' },
  gerych_builder: { bg: 'bg-blue-950/40', text: 'text-blue-300', border: 'border-blue-500/40' },
  dnk_dev_fullstack: { bg: 'bg-cyan-950/40', text: 'text-cyan-300', border: 'border-cyan-500/40' },
  dnk_shopify: { bg: 'bg-emerald-950/40', text: 'text-emerald-300', border: 'border-emerald-500/40' },
  gerych_auditor: { bg: 'bg-amber-950/40', text: 'text-amber-300', border: 'border-amber-500/40' },
  dnk_video_ai_creator: { bg: 'bg-pink-950/40', text: 'text-pink-300', border: 'border-pink-500/40' },
};

export const AgentTaskNode = memo(({ id, data, selected }: NodeProps<any>) => {
  const rawData = (data || {}) as Record<string, any>;
  const nodeData = {
    ...rawData,
    taskId: rawData.taskId || id || 'task-unknown',
    targetAgent: rawData.targetAgent || rawData.agent || 'gerych_prime',
    title: rawData.title || 'Agent Task',
  } as MvrTaskNodeData & {
    isStale?: boolean;
    upstreamFingerprint?: string;
    contextPrompt?: string;
  };
  const { approveRequest, rejectRequest, isSubmittingDecision } = useMvrCanvasStore();
  const [isSyncing, setIsSyncing] = useState(false);
  const compileNodeContext = useCanvasStore((s) => s.compileNodeContext);
  const updateNodeData = useCanvasStore((s) => s.updateNodeData);
  const syncNodeContext = useCanvasStore((s) => s.syncNodeContext);
  const isReevaluating = useCanvasStore((s) => s.isReevaluating);
  const reevaluationProgress = useCanvasStore((s) => s.reevaluationProgress);
  const runDAGReevaluation = useCanvasStore((s) => s.runDAGReevaluation);

  const isCurrentNodeReevaluating = isReevaluating && reevaluationProgress?.activeNodeId === id;

  const handleReevaluateDAG = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!runDAGReevaluation || isReevaluating) return;
    try {
      await runDAGReevaluation({ targetNodeId: id, onlyStale: true });
    } catch (err) {
      console.error('DAG Re-evaluation failed:', err);
    }
  };

  const handleSyncContext = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSyncing(true);
    try {
      if (syncNodeContext && id) {
        syncNodeContext(id);
      } else if (compileNodeContext && id) {
        const result = compileNodeContext(id);
        if (updateNodeData) {
          updateNodeData(id, {
            isStale: false,
            upstreamFingerprint: result.contextHash,
            contextPrompt: result.rawText,
            updatedAt: Date.now(),
          });
        }
      }
    } catch (err) {
      console.error('Failed to sync context:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  const [executingActionId, setExecutingActionId] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const actions = (nodeData.actions || nodeData.dualSurfaceActions || []) as Array<{
    action_id: string;
    label_uk: string;
    description_en?: string;
  }>;

  const handleExecuteAction = async (action: { action_id: string; label_uk: string }) => {
    setExecutingActionId(action.action_id);
    setActionFeedback(null);
    try {
      const res = await fetch('/api/v1/kernel/actions/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: action.action_id,
          payload: {
            node_id: id,
            task_id: nodeData.taskId || id,
            target_agent: nodeData.targetAgent,
          },
          requester: 'vibe_coder',
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setActionFeedback(`✓ ${action.label_uk || action.action_id}: Виконано`);
        setTimeout(() => setActionFeedback(null), 4000);
      } else {
        setActionFeedback(`Помилка: ${data.detail || 'Не вдалося виконати'}`);
      }
    } catch (err: any) {
      setActionFeedback(`Мережева помилка: ${err.message || 'Error'}`);
    } finally {
      setExecutingActionId(null);
    }
  };

  const agentTheme =
    AGENT_COLORS[nodeData.targetAgent || 'gerych_prime'] ||
    AGENT_COLORS.gerych_prime;

  const isWaitingApproval = nodeData.status === 'WAITING_APPROVAL';
  const isRunning = nodeData.status === 'RUNNING';
  const isCompleted = nodeData.status === 'COMPLETED';
  const isPendingVerification = (nodeData.status as string) === 'PENDING_VERIFICATION';
  const isFailed = nodeData.status === 'FAILED' || nodeData.status === 'REJECTED';

  const handleApprove = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!nodeData.approvalRequestId) return;
    try {
      await approveRequest(nodeData.approvalRequestId);
    } catch (err) {
      console.error('Approve failed:', err);
    }
  };

  const handleReject = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!nodeData.approvalRequestId) return;
    try {
      await rejectRequest(nodeData.approvalRequestId, 'Rejected via Node 1-Click');
    } catch (err) {
      console.error('Reject failed:', err);
    }
  };

  return (
    <div
      className={`relative min-w-[280px] max-w-[340px] rounded-xl border bg-slate-900/90 p-4 text-slate-100 shadow-2xl backdrop-blur-md transition-all duration-200 ${
        selected ? 'ring-2 ring-indigo-500 shadow-indigo-500/20' : ''
      } ${
        nodeData.isStale
          ? 'border-amber-500/80 shadow-[0_0_15px_rgba(245,158,11,0.25)] ring-1 ring-amber-500/50'
          : isWaitingApproval
          ? 'border-amber-500/80 shadow-amber-500/20 ring-1 ring-amber-500/50'
          : 'border-slate-800'
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3 !w-3 !rounded-full !border-2 !border-slate-900 !bg-indigo-500"
      />

      {/* Header: Agent + Status Badge */}
      <div className="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div
          className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-semibold ${agentTheme.bg} ${agentTheme.text} ${agentTheme.border}`}
        >
          <Bot className="h-3.5 w-3.5" />
          <span>{nodeData.targetAgent || 'agent'}</span>
        </div>

        {/* Dynamic Status Badge */}
        {isWaitingApproval && (
          <span className="inline-flex animate-pulse items-center gap-1 rounded-full bg-amber-500/20 px-2 py-0.5 text-xs font-semibold text-amber-400 border border-amber-500/40">
            <AlertTriangle className="h-3 w-3" />
            Wait Approval
          </span>
        )}
        {isRunning && (
          <span className="inline-flex items-center gap-1 rounded-full bg-blue-500/20 px-2 py-0.5 text-xs font-semibold text-blue-400 border border-blue-500/40">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </span>
        )}
        {isCompleted && (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/40">
            <CheckCircle2 className="h-3 w-3" />
            Completed
          </span>
        )}
        {isPendingVerification && (
          <span className="inline-flex items-center gap-1 rounded-full bg-cyan-500/20 px-2 py-0.5 text-xs font-semibold text-cyan-400 border border-cyan-500/40">
            <Loader2 className="h-3 w-3 animate-spin" />
            Verifying
          </span>
        )}
        {isFailed && (
          <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/20 px-2 py-0.5 text-xs font-semibold text-rose-400 border border-rose-500/40">
            <XCircle className="h-3 w-3" />
            {nodeData.status}
          </span>
        )}
        {nodeData.status === 'ABORTED' && (
          <span className="inline-flex items-center gap-1 rounded-full bg-orange-500/20 px-2 py-0.5 text-xs font-semibold text-orange-400 border border-orange-500/40">
            <XCircle className="h-3 w-3" />
            Aborted
          </span>
        )}
        {nodeData.status === 'QUEUED' && (
          <span className="inline-flex items-center gap-1 rounded-full bg-slate-700/40 px-2 py-0.5 text-xs font-semibold text-slate-300 border border-slate-600/40">
            <Clock className="h-3 w-3" />
            Queued
          </span>
        )}
      </div>

      {/* Body: Title & Details */}
      <div className="py-3">
        <h4 className="text-sm font-semibold leading-snug text-slate-200">
          {nodeData.title}
        </h4>

        {/* Node Text / Description Content */}
        {Boolean(nodeData.description) && (
          <p className="mt-1.5 text-xs text-slate-400 line-clamp-3 leading-relaxed whitespace-pre-line font-normal">
            {String(nodeData.description).replace(/^[#\s]+[^\n]+\n*/, '').trim()}
          </p>
        )}

        {/* ThoughtDAG Stale Indicator Badge */}
        {nodeData.isStale && (
          <div className="mt-2.5 flex items-center justify-between gap-1.5 rounded-lg border border-amber-500/50 bg-amber-950/60 px-2.5 py-1.5 text-xs text-amber-300 shadow-md">
            <div className="flex items-center gap-1.5 font-medium">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
              <span>Context Outdated</span>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleSyncContext}
                disabled={isSyncing || isReevaluating}
                className="flex items-center gap-1 rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-semibold text-amber-200 border border-amber-500/40 hover:bg-amber-500/40 transition-colors cursor-pointer"
                title="Sync prompt with updated upstream ThoughtDAG notes"
              >
                <RefreshCw className={`h-3 w-3 ${isSyncing ? 'animate-spin' : ''}`} />
                <span>{isSyncing ? 'Syncing...' : 'Sync'}</span>
              </button>
              <button
                type="button"
                onClick={handleReevaluateDAG}
                disabled={isReevaluating}
                className="flex items-center gap-1 rounded bg-cyan-500/20 px-2 py-0.5 text-[10px] font-semibold text-cyan-200 border border-cyan-500/40 hover:bg-cyan-500/40 transition-colors cursor-pointer"
                title="Topologically re-evaluate DAG branch"
              >
                <RefreshCw className={`h-3 w-3 ${isCurrentNodeReevaluating ? 'animate-spin' : ''}`} />
                <span>{isCurrentNodeReevaluating ? 'Re-evaluating...' : 'Re-eval DAG'}</span>
              </button>
            </div>
          </div>
        )}
        <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
          <span className="font-mono text-[11px] text-slate-400">
            ID: {(nodeData.taskId || id || 'task').slice(0, 8)}
          </span>
          {nodeData.riskLevel && (
            <span
              className={`inline-flex items-center gap-1 text-[11px] font-semibold ${
                nodeData.riskLevel === 'critical'
                  ? 'text-rose-400'
                  : nodeData.riskLevel === 'high'
                  ? 'text-amber-400'
                  : 'text-slate-400'
              }`}
            >
              {nodeData.riskLevel === 'critical' || nodeData.riskLevel === 'high' ? (
                <ShieldAlert className="h-3 w-3" />
              ) : (
                <ShieldCheck className="h-3 w-3" />
              )}
              {nodeData.riskLevel.toUpperCase()}
            </span>
          )}
        </div>

        {/* Telemetry Badge: RAM & Duration */}
        {(nodeData.memoryMb !== undefined || nodeData.durationMs !== undefined) && (
          <div className="mt-2.5 flex items-center gap-1.5 rounded bg-slate-900/80 px-2 py-1 text-[11px] font-mono text-cyan-300 border border-cyan-800/40">
            <span>💾 {String(nodeData.memoryMb ?? 0)} MB</span>
            <span className="text-slate-600">|</span>
            <span>⏱️ {String(nodeData.durationMs ?? 0)} ms</span>
          </div>
        )}

        {/* SOTA arXiv:2609.08589v1 Deterministic Runtime Progress Bar */}
        {nodeData.runtimeProgress && (
          <div className="mt-2.5 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span className="flex items-center gap-1">
                {nodeData.runtimeProgress.verified ? (
                  <ShieldCheck className="h-3 w-3 text-emerald-400" />
                ) : (
                  <Loader2 className="h-3 w-3 text-indigo-400 animate-spin" />
                )}
                {nodeData.runtimeProgress.completedSlices !== undefined && nodeData.runtimeProgress.totalSlices !== undefined
                  ? `Slice ${nodeData.runtimeProgress.completedSlices}/${nodeData.runtimeProgress.totalSlices}`
                  : `Mutations: ${nodeData.runtimeProgress.filesMutated ?? 0}`}
              </span>
              <span className="font-semibold text-slate-300">
                {Math.round(nodeData.runtimeProgress.progressPct)}%
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full transition-all duration-300 ${
                  nodeData.runtimeProgress.verified
                    ? 'bg-emerald-500'
                    : 'bg-indigo-500'
                }`}
                style={{ width: `${Math.min(100, Math.max(0, nodeData.runtimeProgress.progressPct))}%` }}
              />
            </div>
          </div>
        )}

        {/* Deterministic Proof Badge (arXiv:2609.08589v1) */}
        {nodeData.runtimeEvidence?.verified && (
          <div className="mt-2 flex items-center gap-1 rounded bg-emerald-950/40 px-2 py-0.5 text-[10px] font-medium text-emerald-300 border border-emerald-500/30">
            <ShieldCheck className="h-3 w-3 text-emerald-400" />
            <span>Deterministic Proof: 100% Green</span>
          </div>
        )}

        {/* Error message if failed */}
        {nodeData.error && (
          <div className="mt-2.5 rounded-md bg-rose-950/40 border border-rose-800/40 p-2 text-xs text-rose-300">
            {nodeData.error}
          </div>
        )}

        {/* Artifacts preview */}
        {nodeData.artifacts && nodeData.artifacts.length > 0 && (
          <div className="mt-3 border-t border-slate-800/60 pt-2.5">
            <div className="mb-1 text-[11px] font-medium text-slate-400">Artifacts:</div>
            <div className="space-y-1">
              {nodeData.artifacts.map((art) => (
                <div
                  key={art.artifact_id}
                  className="flex items-center gap-1.5 rounded bg-slate-800/40 px-2 py-1 text-xs text-slate-300"
                >
                  <FileText className="h-3 w-3 text-indigo-400" />
                  <span className="truncate">{art.filename}</span>
                  <span className="ml-auto text-[10px] text-slate-400 font-mono">
                    {Math.round(art.size_bytes / 1024)} KB
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dual-Surface Actions (LLM FastMCP Tool <-> React UI Button) */}
        {actions.length > 0 && (
          <div className="mt-3 border-t border-slate-800/80 pt-2.5 space-y-1.5">
            <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
              <span>Dual-Surface Actions</span>
              <span className="text-indigo-400">FastMCP</span>
            </div>
            <div className="grid grid-cols-1 gap-1.5">
              {actions.map((act) => (
                <button
                  key={act.action_id}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleExecuteAction(act);
                  }}
                  disabled={executingActionId === act.action_id}
                  className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-500/30 text-indigo-200 text-xs font-medium transition-all shadow-sm hover:shadow-indigo-500/10 cursor-pointer disabled:opacity-50 text-left"
                >
                  <span className="flex items-center gap-1.5 truncate">
                    {executingActionId === act.action_id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400 shrink-0" />
                    ) : (
                      <Play className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                    )}
                    <span className="truncate">{act.label_uk || act.action_id}</span>
                  </span>
                  <span className="text-[9px] font-mono text-indigo-400/70 bg-indigo-950/80 px-1 py-0.5 rounded border border-indigo-800/40 shrink-0">
                    RUN
                  </span>
                </button>
              ))}
            </div>
            {actionFeedback && (
              <div className="mt-1 text-[11px] font-mono text-emerald-300 bg-emerald-950/40 border border-emerald-500/30 rounded px-2 py-1">
                {actionFeedback}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 1-Click HITL Action Area */}
      {isWaitingApproval && (
        <div className="mt-2 border-t border-amber-500/30 pt-3">
          <div className="mb-2 text-center text-xs font-medium text-amber-300">
            Requires Operator Approval
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={isSubmittingDecision}
              className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-white shadow-lg shadow-emerald-900/30 transition-all disabled:opacity-50"
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              Approve
            </button>
            <button
              onClick={handleReject}
              disabled={isSubmittingDecision}
              className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-rose-600/80 hover:bg-rose-500 px-3 py-1.5 text-xs font-semibold text-white shadow-lg shadow-rose-900/30 transition-all disabled:opacity-50"
            >
              <XCircle className="h-3.5 w-3.5" />
              Reject
            </button>
          </div>
        </div>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-3 !w-3 !rounded-full !border-2 !border-slate-900 !bg-indigo-500"
      />
    </div>
  );
});

AgentTaskNode.displayName = 'AgentTaskNode';
