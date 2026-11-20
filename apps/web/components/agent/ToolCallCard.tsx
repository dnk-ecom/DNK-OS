// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_agent_ToolCallCard"
// purpose: "Meta Astryx Agent-Native Live Tool Call Card with terminal stream, syntax-highlighted unified diff viewer, and duration badge."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useMemo } from 'react';
import {
  Terminal,
  CheckCircle2,
  XCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  FileCode,
  Play,
  Copy,
  Check,
  Split,
  FileText
} from 'lucide-react';

export interface ToolCallData {
  tool_call_id: string;
  tool_name: string;
  tool_args: Record<string, any>;
  result?: any;
  status: 'executing' | 'completed' | 'failed';
  exit_code?: number;
  duration_ms?: number;
  started_at?: number;
  completed_at?: number;
}

interface ToolCallCardProps {
  toolCall: ToolCallData;
  agentName?: string;
  className?: string;
}

function detectDiff(text: string): boolean {
  if (!text || typeof text !== 'string') return false;
  return (
    text.includes('diff --git') ||
    text.includes('@@ ') ||
    (text.includes('\n+') && text.includes('\n-'))
  );
}

function DiffLine({ line, index }: { line: string; index: number }) {
  let lineClass = 'text-neutral-300 hover:bg-white/5';
  let badgeClass = 'text-neutral-600';
  let prefix = ' ';

  if (line.startsWith('+') && !line.startsWith('+++')) {
    lineClass = 'bg-emerald-950/40 text-emerald-300 border-l-2 border-emerald-500 font-medium';
    badgeClass = 'text-emerald-500/70';
    prefix = '+';
  } else if (line.startsWith('-') && !line.startsWith('---')) {
    lineClass = 'bg-rose-950/40 text-rose-300 border-l-2 border-rose-500 font-medium line-through/20';
    badgeClass = 'text-rose-500/70';
    prefix = '-';
  } else if (line.startsWith('@@')) {
    lineClass = 'bg-cyan-950/30 text-cyan-400 font-semibold border-y border-cyan-800/30 my-0.5';
    badgeClass = 'text-cyan-500/70';
    prefix = '@';
  } else if (line.startsWith('diff --git') || line.startsWith('index ')) {
    lineClass = 'text-amber-300/80 font-bold';
    badgeClass = 'text-amber-500/50';
  }

  return (
    <div className={`flex items-start px-2 py-0.5 text-[11px] font-mono leading-relaxed transition-colors ${lineClass}`}>
      <span className={`w-8 select-none text-[10px] text-right pr-2 shrink-0 ${badgeClass}`}>
        {index + 1}
      </span>
      <span className="select-none pr-1.5 font-bold shrink-0 opacity-70">
        {prefix}
      </span>
      <span className="whitespace-pre-wrap break-all flex-1">
        {prefix !== ' ' && line.length > 1 ? line.slice(1) : line}
      </span>
    </div>
  );
}

export function ToolCallCard({ toolCall, agentName = 'denchik', className = '' }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(toolCall.status !== 'completed');
  const [isCopied, setIsCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'diff' | 'raw'>('diff');

  const isSuccess = toolCall.status === 'completed' && (toolCall.exit_code === undefined || toolCall.exit_code === 0);
  const isFailed = toolCall.status === 'failed' || (toolCall.exit_code !== undefined && toolCall.exit_code !== 0);

  const rawOutputString = useMemo(() => {
    if (toolCall.result === undefined || toolCall.result === null) return '';
    return typeof toolCall.result === 'string' ? toolCall.result : JSON.stringify(toolCall.result, null, 2);
  }, [toolCall.result]);

  const hasDiff = useMemo(() => {
    if (detectDiff(rawOutputString)) return true;
    if (toolCall.tool_name === 'edit_file' || toolCall.tool_name === 'write_file') return true;
    return false;
  }, [rawOutputString, toolCall.tool_name]);

  const copyPayload = () => {
    const text = JSON.stringify({ args: toolCall.tool_args, result: toolCall.result }, null, 2);
    navigator.clipboard.writeText(text);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const targetPath = toolCall.tool_args?.Path || toolCall.tool_args?.path || toolCall.tool_args?.file_path;

  return (
    <div
      className={`rounded-xl border transition-all duration-200 overflow-hidden ${isFailed
          ? 'border-red-500/40 bg-red-950/20 shadow-red-950/10'
          : isSuccess
            ? 'border-emerald-500/30 bg-emerald-950/10 shadow-emerald-950/10'
            : 'border-blue-500/40 bg-blue-950/20 animate-pulse-subtle'
        } ${className}`}
      data-agent-target="tool-call-card"
      data-tool-id={toolCall.tool_call_id}
      data-tool-name={toolCall.tool_name}
    >
      {/* Header bar */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between px-3.5 py-2.5 cursor-pointer select-none bg-black/30 hover:bg-black/40 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <button
            type="button"
            aria-label={isExpanded ? "Collapse tool details" : "Expand tool details"}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>

          <div className="p-1 rounded bg-muted/60 text-foreground">
            {toolCall.tool_name.includes('file') ? (
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            ) : (
              <Terminal className="w-3.5 h-3.5 text-amber-400" />
            )}
          </div>

          <span className="font-mono text-xs font-semibold tracking-wide text-foreground truncate">
            {toolCall.tool_name}
          </span>

          {targetPath && (
            <span className="text-[10px] px-1.5 py-0.5 rounded border border-cyan-500/30 bg-cyan-950/40 text-cyan-200 font-mono truncate max-w-[180px]">
              {String(targetPath).split('/').pop()}
            </span>
          )}

          <span className="text-[10px] px-1.5 py-0.5 rounded-full border border-border/60 text-muted-foreground font-mono">
            {agentName}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {toolCall.duration_ms !== undefined && (
            <span className="text-[11px] font-mono text-muted-foreground flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {Math.round(toolCall.duration_ms)}ms
            </span>
          )}

          {toolCall.status === 'executing' && (
            <span className="flex items-center gap-1 text-[11px] font-medium text-blue-400">
              <Play className="w-3 h-3 animate-spin" />
              Running
            </span>
          )}

          {isSuccess && (
            <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Exit 0
            </span>
          )}

          {isFailed && (
            <span className="flex items-center gap-1 text-[11px] font-medium text-red-400">
              <XCircle className="w-3.5 h-3.5" />
              {toolCall.exit_code !== undefined ? `Exit ${toolCall.exit_code}` : 'Failed'}
            </span>
          )}
        </div>
      </div>

      {/* Expanded body */}
      {isExpanded && (
        <div className="p-3 border-t border-border/40 space-y-2.5 text-xs font-mono">
          {/* Tool arguments */}
          <div>
            <div className="flex items-center justify-between text-muted-foreground text-[10px] uppercase tracking-wider mb-1">
              <span>Arguments</span>
              <button
                onClick={(e) => { e.stopPropagation(); copyPayload(); }}
                className="hover:text-foreground flex items-center gap-1 text-[10px] transition-colors"
              >
                {isCopied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {isCopied ? 'Copied' : 'Copy Payload'}
              </button>
            </div>
            <pre className="p-2 rounded-lg bg-black/50 border border-border/40 overflow-x-auto text-blue-200/90 text-[11px] max-h-36">
              {JSON.stringify(toolCall.tool_args, null, 2)}
            </pre>
          </div>

          {/* Tool result with Unified Diff support */}
          {toolCall.result !== undefined && (
            <div>
              <div className="flex items-center justify-between text-muted-foreground text-[10px] uppercase tracking-wider mb-1">
                <span>Output / Result</span>
                {hasDiff && (
                  <div className="flex items-center gap-1 bg-neutral-900/80 p-0.5 rounded border border-border/40">
                    <button
                      onClick={() => setViewMode('diff')}
                      className={`px-1.5 py-0.5 rounded text-[10px] flex items-center gap-1 transition-colors ${viewMode === 'diff'
                          ? 'bg-purple-600 text-white font-medium'
                          : 'text-neutral-400 hover:text-white'
                        }`}
                    >
                      <Split className="w-2.5 h-2.5" />
                      Diff
                    </button>
                    <button
                      onClick={() => setViewMode('raw')}
                      className={`px-1.5 py-0.5 rounded text-[10px] flex items-center gap-1 transition-colors ${viewMode === 'raw'
                          ? 'bg-purple-600 text-white font-medium'
                          : 'text-neutral-400 hover:text-white'
                        }`}
                    >
                      <FileText className="w-2.5 h-2.5" />
                      Raw
                    </button>
                  </div>
                )}
              </div>

              {hasDiff && viewMode === 'diff' ? (
                <div className="rounded-lg border border-border/50 bg-black/70 overflow-hidden max-h-64 overflow-y-auto">
                  {rawOutputString.split('\n').map((line, idx) => (
                    <DiffLine key={idx} line={line} index={idx} />
                  ))}
                </div>
              ) : (
                <pre className={`p-2.5 rounded-lg bg-black/60 border overflow-x-auto text-[11px] max-h-64 leading-relaxed ${isFailed ? 'border-red-500/30 text-red-300' : 'border-border/40 text-emerald-200/90'
                  }`}>
                  {rawOutputString}
                </pre>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
