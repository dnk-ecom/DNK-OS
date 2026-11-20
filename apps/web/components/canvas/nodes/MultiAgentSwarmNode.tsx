// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/nodes/MultiAgentSwarmNode.tsx"
// purpose: "Assimilation of CopilotKit open-multi-agent-canvas node patterns for @xyflow/react with real-time step streaming and MCP status."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym & Gerych"
// --- END DNK-MRH-HEADER ---

import React, { useState, memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  Bot,
  Play,
  Pause,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Server,
  Terminal,
  Globe,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  Sparkles,
} from 'lucide-react';
import type { MultiAgentSwarmNodeData, AgentRunStatus } from '@/types/mcp';

const ROLE_COLOR_MAP: Record<string, { badge: string; border: string }> = {
  gerych_prime: { badge: 'bg-[#35d5d5]/15 text-[#35d5d5]', border: 'border-[#35d5d5]/40' },
  gerych_builder: { badge: 'bg-emerald-500/15 text-emerald-400', border: 'border-emerald-500/40' },
  gerych_researcher: { badge: 'bg-sky-500/15 text-sky-400', border: 'border-sky-500/40' },
  gerych_auditor: { badge: 'bg-rose-500/15 text-rose-400', border: 'border-rose-500/40' },
  dnk_dev_fullstack: { badge: 'bg-indigo-500/15 text-indigo-400', border: 'border-indigo-500/40' },
  dnk_shopify: { badge: 'bg-amber-500/15 text-amber-400', border: 'border-amber-500/40' },
  dnk_video_ai_creator: { badge: 'bg-purple-500/15 text-purple-400', border: 'border-purple-500/40' },
  mcp_agent: { badge: 'bg-teal-500/15 text-teal-300', border: 'border-teal-500/40' },
};

export const MultiAgentSwarmNode = memo(({ data, selected }: NodeProps<any>) => {
  const nodeData = data as MultiAgentSwarmNodeData;
  const [showLogs, setShowLogs] = useState(true);
  const [showResponse, setShowResponse] = useState(true);

  const roleStyle = ROLE_COLOR_MAP[nodeData.agentRole] || {
    badge: 'bg-cyan-500/15 text-cyan-300',
    border: 'border-[#224447]',
  };

  const isRunning = nodeData.status === 'running';
  const isCompleted = nodeData.status === 'completed';
  const isFailed = nodeData.status === 'failed';
  const isHighlighted = !!nodeData.highlighted;
  const isDimmed = !!nodeData.dimmed;

  const mcpServerCount = nodeData.mcpServers ? Object.keys(nodeData.mcpServers).length : 0;

  return (
    <div
      className={`relative w-84 rounded-xl shadow-2xl transition-all duration-300 select-none ${
        selected ? 'ring-2 ring-[#35d5d5] shadow-[#35d5d5]/20' : ''
      } ${
        isHighlighted
          ? 'ring-4 ring-[#35d5d5] scale-105 z-30 opacity-100 shadow-[0_0_35px_rgba(53,213,213,0.5)]'
          : isDimmed
          ? 'opacity-30 scale-95 blur-[0.5px] pointer-events-none'
          : 'opacity-100'
      } border ${roleStyle.border} bg-[#162c2f] text-[#d4d8db]`}
      style={{
        boxShadow: isHighlighted
          ? '0 0 35px rgba(53, 213, 213, 0.45)'
          : selected
          ? '0 0 20px rgba(53, 213, 213, 0.25)'
          : '0 8px 32px rgba(0, 0, 0, 0.4)',
      }}
    >
      {/* Port Handles for full DAG Wires */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-[#35d5d5] border-2 border-[#112224] rounded-full transition-transform hover:scale-125"
      />
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-[#35d5d5] border-2 border-[#112224] rounded-full transition-transform hover:scale-125"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-[#22c55e] border-2 border-[#112224] rounded-full transition-transform hover:scale-125"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-[#22c55e] border-2 border-[#112224] rounded-full transition-transform hover:scale-125"
      />

      {/* Header Strip */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-[#112224] rounded-t-xl border-b border-[#224447]">
        <div className="flex items-center space-x-2 min-w-0">
          <div className="p-1 rounded-md bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
            <Bot className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <span className="text-xs font-semibold text-slate-100 truncate block">
              {nodeData.agentName || nodeData.agentRole}
            </span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${roleStyle.badge}`}>
              {nodeData.agentRole}
            </span>
            {nodeData.community && (
              <span className="text-[9px] px-1.5 py-0.5 rounded font-mono bg-[#35d5d5]/15 text-[#35d5d5] border border-[#35d5d5]/30 ml-1">
                {nodeData.community}
              </span>
            )}
          </div>
        </div>

        {/* Status Indicator Orb */}
        <div className="flex items-center space-x-1.5 pl-2">
          {isRunning && (
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#22c55e] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#22c55e]"></span>
            </span>
          )}
          {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
          {isFailed && <AlertCircle className="w-3.5 h-3.5 text-rose-400" />}
          {nodeData.status === 'idle' && (
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-slate-500"></span>
          )}
          <span className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
            {nodeData.status}
          </span>
        </div>
      </div>

      {/* Body Section */}
      <div className="p-3.5 space-y-2.5">
        {/* Active Node / Subtask Banner (Assimilated from open-multi-agent-canvas) */}
        {isRunning && nodeData.activeNodeName && (
          <div className="flex items-center justify-between px-2.5 py-1.5 bg-[#112224]/80 border border-[#35d5d5]/30 rounded-lg text-xs">
            <div className="flex items-center space-x-2 truncate">
              <Loader2 className="w-3.5 h-3.5 text-[#35d5d5] animate-spin flex-shrink-0" />
              <span className="text-slate-300 truncate">
                Executing:{' '}
                <strong className="text-[#35d5d5] font-mono">{nodeData.activeNodeName}</strong>
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono ml-1 flex-shrink-0">active</span>
          </div>
        )}

        {/* Task Goal */}
        {nodeData.taskGoal && (
          <div className="text-xs text-slate-300 leading-relaxed bg-[#112224]/40 p-2 rounded border border-[#224447]/60">
            {nodeData.taskGoal}
          </div>
        )}

        {/* MCP Servers Info Chip (Assimilated MCP connectivity) */}
        {mcpServerCount > 0 && (
          <div className="flex items-center justify-between text-[11px] px-2 py-1 bg-[#112224]/60 rounded border border-[#224447]">
            <div className="flex items-center space-x-1.5 text-slate-400">
              <Server className="w-3.5 h-3.5 text-teal-400" />
              <span>MCP Tools:</span>
              <span className="text-teal-300 font-mono font-medium">{mcpServerCount} connected</span>
            </div>
            {nodeData.onConfigureMCP && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  nodeData.onConfigureMCP?.(nodeData.id);
                }}
                className="text-[10px] text-[#35d5d5] hover:underline"
              >
                Configure
              </button>
            )}
          </div>
        )}

        {/* Subtask Execution Steps / Logs (Assimilated from mcp-agent logs) */}
        {nodeData.logs && nodeData.logs.length > 0 && (
          <div className="border border-[#224447] rounded-lg overflow-hidden bg-[#112224]/50">
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="w-full flex items-center justify-between px-2.5 py-1.5 bg-[#112224] text-[11px] font-medium text-slate-300 hover:text-white"
            >
              <div className="flex items-center space-x-1.5">
                <Layers className="w-3 h-3 text-[#35d5d5]" />
                <span>Execution Steps ({nodeData.logs.length})</span>
              </div>
              {showLogs ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>

            {showLogs && (
              <div className="max-h-36 overflow-y-auto p-2 space-y-1.5 divide-y divide-[#224447]/40 text-xs">
                {nodeData.logs.map((step) => (
                  <div key={step.id} className="pt-1.5 first:pt-0 flex items-start space-x-2">
                    {step.done ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                    ) : (
                      <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin mt-0.5 flex-shrink-0" />
                    )}
                    <div className="min-w-0 flex-1">
                      <p
                        className={`text-[11px] ${
                          step.done ? 'text-slate-300' : 'text-amber-200 font-medium'
                        }`}
                      >
                        {step.message}
                      </p>
                      {step.nodeName && (
                        <span className="text-[9px] text-slate-500 font-mono">
                          [{step.nodeName}]
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Agent Response Preview */}
        {nodeData.response && (
          <div className="border border-[#224447] rounded-lg overflow-hidden bg-[#112224]/40">
            <button
              onClick={() => setShowResponse(!showResponse)}
              className="w-full flex items-center justify-between px-2.5 py-1.5 bg-[#112224] text-[11px] font-medium text-slate-300 hover:text-white"
            >
              <div className="flex items-center space-x-1.5">
                <Sparkles className="w-3 h-3 text-emerald-400" />
                <span>Synthesized Output</span>
              </div>
              {showResponse ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>

            {showResponse && (
              <div className="p-2.5 max-h-40 overflow-y-auto text-[11px] text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
                {nodeData.response}
              </div>
            )}
          </div>
        )}

        {/* Action Controls & Telemetry Footer */}
        <div className="pt-2 border-t border-[#224447] flex items-center justify-between text-[10px] text-slate-400">
          <div className="flex items-center space-x-2">
            {nodeData.metrics?.tokensUsed && (
              <span>Tokens: {nodeData.metrics.tokensUsed.toLocaleString()}</span>
            )}
            {nodeData.metrics?.durationMs && (
              <span>{(nodeData.metrics.durationMs / 1000).toFixed(1)}s</span>
            )}
          </div>

          <div className="flex items-center space-x-1">
            {isRunning ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  nodeData.onPause?.(nodeData.id);
                }}
                className="p-1 rounded bg-[#112224] hover:bg-slate-700 text-amber-400 border border-[#224447]"
                title="Pause Agent"
              >
                <Pause className="w-3 h-3" />
              </button>
            ) : (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  nodeData.onDispatch?.(nodeData.id);
                }}
                className="p-1 rounded bg-[#112224] hover:bg-slate-700 text-[#35d5d5] border border-[#224447]"
                title="Dispatch Agent"
              >
                <Play className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

MultiAgentSwarmNode.displayName = 'MultiAgentSwarmNode';
