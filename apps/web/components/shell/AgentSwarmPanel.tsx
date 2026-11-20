// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/AgentSwarmPanel.tsx"
// purpose: "Horizontal panel showing active Gerych Prime swarm agents with live task pulse."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { Bot, Zap, CheckCircle, Clock, Cpu } from 'lucide-react';

export interface Agent {
  id: string;
  name: string;
  role: string;
  emoji: string;
  status: 'running' | 'waiting' | 'done' | 'error';
  task: string;
  runtime: number; // seconds
  color: string;
  toolCalls: number;
}

const STATUS_CONFIG = {
  running: { label: 'RUNNING', color: '#00dc82', bg: '#00dc8215' },
  waiting: { label: 'WAITING', color: '#f59e0b', bg: '#f59e0b15' },
  done:    { label: 'DONE',    color: '#22d3ee', bg: '#22d3ee15' },
  error:   { label: 'ERROR',   color: '#f87171', bg: '#f8717115' },
};

function formatRuntime(s: number): string {
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return `${m}m ${s % 60}s`;
}

interface AgentCardProps {
  agent: Agent;
}

function AgentCard({ agent }: AgentCardProps) {
  const [runtime, setRuntime] = useState(agent.runtime);
  const [toolCalls, setToolCalls] = useState(agent.toolCalls);
  const st = STATUS_CONFIG[agent.status];

  useEffect(() => {
    if (agent.status !== 'running') return;
    const id = setInterval(() => {
      setRuntime(r => r + 1);
      if (Math.random() > 0.8) setToolCalls(t => t + 1);
    }, 1000);
    return () => clearInterval(id);
  }, [agent.status]);

  return (
    <div
      className="flex-1 min-w-[220px] max-w-xs flex flex-col gap-2.5 p-4 rounded-2xl
        bg-[#0e1117]/80 border border-white/[0.07] transition-all duration-300
        hover:border-white/[0.12]"
      style={{ boxShadow: `inset 0 0 20px ${agent.color}0a` }}
    >
      {/* Agent header */}
      <div className="flex items-center gap-3">
        {/* Avatar */}
        <div
          className="relative w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0 font-medium"
          style={{ background: `${agent.color}18`, border: `1px solid ${agent.color}30` }}
        >
          {agent.emoji}
          {/* Pulse for running agents */}
          {agent.status === 'running' && (
            <span
              className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-[#0e1117]"
              style={{ background: st.color }}
            >
              <span
                className="absolute inset-0 rounded-full animate-ping"
                style={{ background: st.color, opacity: 0.5 }}
              />
            </span>
          )}
        </div>

        <div className="overflow-hidden">
          <p className="text-[13px] font-bold text-white truncate">{agent.name}</p>
          <p className="text-[10px] text-slate-500 truncate">{agent.role}</p>
        </div>

        <div className="ml-auto shrink-0">
          <span
            className="text-[9px] font-bold tracking-widest px-2 py-0.5 rounded-full"
            style={{ background: st.bg, color: st.color, border: `1px solid ${st.color}40` }}
          >
            {st.label}
          </span>
        </div>
      </div>

      {/* Current task */}
      <div
        className="px-3 py-2 rounded-lg text-[11px] text-slate-400 line-clamp-2 leading-relaxed"
        style={{ background: '#ffffff07' }}
      >
        {agent.task}
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-4 text-[10px]">
        <div className="flex items-center gap-1 text-slate-500">
          <Clock size={11} />
          <span className="font-mono text-slate-400">{formatRuntime(runtime)}</span>
        </div>
        <div className="flex items-center gap-1 text-slate-500">
          <Zap size={11} />
          <span className="font-mono text-slate-400">{toolCalls} tools</span>
        </div>
      </div>

      {/* Activity bar */}
      {agent.status === 'running' && (
        <div className="h-[3px] w-full rounded-full overflow-hidden bg-white/[0.05]">
          <div
            className="h-full rounded-full animate-pulse"
            style={{
              background: `linear-gradient(90deg, ${agent.color}90, ${agent.color})`,
              width: `${30 + (runtime % 70)}%`,
              transition: 'width 1s ease',
            }}
          />
        </div>
      )}
    </div>
  );
}

interface AgentSwarmPanelProps {
  agents: Agent[];
}

export default function AgentSwarmPanel({ agents }: AgentSwarmPanelProps) {
  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <Bot size={15} className="text-purple-400" />
        <h2 className="text-[13px] font-bold text-white">Agent Swarm</h2>
        <span className="text-[10px] text-slate-600 ml-1">
          {agents.filter(a => a.status === 'running').length} active
        </span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1">
        {agents.map(agent => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </section>
  );
}
