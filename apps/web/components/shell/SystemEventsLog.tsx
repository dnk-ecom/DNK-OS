// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/SystemEventsLog.tsx"
// purpose: "Scrollable real-time event log panel for DNK OS kernel events with severity colors."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle, Zap } from 'lucide-react';

export type LogLevel = 'info' | 'success' | 'warning' | 'error' | 'system';

export interface LogEntry {
  id: string;
  ts: string;
  level: LogLevel;
  source: string;
  message: string;
}

const LEVEL_CONFIG: Record<LogLevel, { icon: React.ElementType; color: string; bg: string }> = {
  info:    { icon: Info,          color: '#94a3b8', bg: '#94a3b810' },
  success: { icon: CheckCircle,   color: '#00dc82', bg: '#00dc8210' },
  warning: { icon: AlertTriangle, color: '#f59e0b', bg: '#f59e0b10' },
  error:   { icon: XCircle,       color: '#f87171', bg: '#f8717110' },
  system:  { icon: Zap,           color: '#a78bfa', bg: '#a78bfa10' },
};

// Simulated event feed
const SIMULATED_EVENTS: Omit<LogEntry, 'id' | 'ts'>[] = [
  { level: 'success', source: 'kernel',      message: 'Harness initialized — 19 SaaP plugins registered' },
  { level: 'info',    source: 'fastmcp',     message: 'Namespace resolver: dnk_video_ai_creator.generate_short' },
  { level: 'info',    source: 'fastmcp',     message: 'Namespace resolver: dnk_shopify.deploy_theme' },
  { level: 'system',  source: 'gerych_prime',message: 'Gerych Prime woke up — task DNA dispatched (24 nodes)' },
  { level: 'info',    source: 'task_forest', message: 'Task slice 1/4 — refactor: core cleanup complete' },
  { level: 'warning', source: 'workspace',   message: 'workspace_janitor pruned artifacts/ dir (14 files)' },
  { level: 'success', source: 'pre-commit',  message: '8/8 quality gates PASSED in 31.1s ✅' },
  { level: 'info',    source: 'canvas',      message: 'StitchArtboard node connected: stitch-thumb-metrics → stitch-design-system' },
  { level: 'info',    source: 'dnk_shopify', message: 'Theme deploy started: DNK_Ecom_v1_0_0 → ReBurn Store' },
  { level: 'success', source: 'dnk_shopify', message: 'Theme deployed successfully in 4.2s' },
  { level: 'error',   source: 'dnk_video',   message: 'Frame 0 audio latency detected — auto-patched via punch-in zoom' },
  { level: 'info',    source: 'memory',      message: 'SCONES L3 distillation: 3 new patterns indexed' },
  { level: 'system',  source: 'kernel',      message: 'Root hygiene guard: 8-root invariant verified ✅' },
];

function now(): string {
  return new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

let _eventIdx = 0;
function nextSimulatedEvent(): LogEntry {
  const e = SIMULATED_EVENTS[_eventIdx % SIMULATED_EVENTS.length];
  _eventIdx++;
  return { ...e, id: `log-${Date.now()}-${Math.random()}`, ts: now() };
}

interface SystemEventsLogProps {
  initialEntries?: LogEntry[];
}

export default function SystemEventsLog({ initialEntries = [] }: SystemEventsLogProps) {
  const [entries, setEntries] = useState<LogEntry[]>(() => {
    // Seed with some initial entries
    return SIMULATED_EVENTS.slice(0, 8).map((e, i) => ({
      ...e,
      id: `init-${i}`,
      ts: now(),
    }));
  });
  const bottomRef = useRef<HTMLDivElement>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused) return;
    const id = setInterval(() => {
      setEntries(prev => {
        const next = [...prev, nextSimulatedEvent()];
        return next.slice(-80); // keep last 80 entries
      });
    }, 3500 + Math.random() * 2000);
    return () => clearInterval(id);
  }, [paused]);

  useEffect(() => {
    if (!paused) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [entries, paused]);

  return (
    <aside className="w-[280px] shrink-0 flex flex-col border-l border-white/[0.06] bg-[#080b12]/60">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
          <span className="text-[12px] font-bold text-white">System Events</span>
        </div>
        <button
          onClick={() => setPaused(p => !p)}
          className="text-[10px] text-slate-500 hover:text-slate-300 transition-colors font-medium px-2 py-0.5 rounded border border-white/[0.06] hover:border-white/[0.12]"
        >
          {paused ? '▶ Resume' : '⏸ Pause'}
        </button>
      </div>

      {/* Log entries */}
      <div className="flex-1 overflow-y-auto py-2 px-2 space-y-1" style={{ scrollbarWidth: 'none' }}>
        {entries.map(entry => {
          const cfg = LEVEL_CONFIG[entry.level];
          const Icon = cfg.icon;
          return (
            <div
              key={entry.id}
              className="flex gap-2 px-2 py-1.5 rounded-lg transition-colors hover:bg-white/[0.03]"
            >
              {/* Icon */}
              <div className="shrink-0 mt-0.5">
                <Icon size={12} style={{ color: cfg.color }} />
              </div>
              {/* Content */}
              <div className="overflow-hidden">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="text-[9px] font-mono text-slate-600">{entry.ts}</span>
                  <span
                    className="text-[9px] font-bold font-mono px-1 rounded"
                    style={{ color: cfg.color, background: cfg.bg }}
                  >
                    {entry.source}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 leading-relaxed break-words">{entry.message}</p>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* Footer count */}
      <div className="px-4 py-2 border-t border-white/[0.06] flex items-center justify-between">
        <span className="text-[9px] text-slate-600 font-mono">{entries.length} events</span>
        <button
          onClick={() => setEntries([])}
          className="text-[9px] text-slate-600 hover:text-slate-400 transition-colors"
        >
          Clear
        </button>
      </div>
    </aside>
  );
}
