// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/KernelStatusBar.tsx"
// purpose: "Top status bar for DNK OS Visual Shell. Shows kernel health, active branch, time."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, GitBranch, Wifi, Clock, ChevronDown, Bell, Search } from 'lucide-react';

interface KernelStatusBarProps {
  agentCount: number;
  serviceCount: number;
  taskCount: number;
}

export default function KernelStatusBar({ agentCount, serviceCount, taskCount }: KernelStatusBarProps) {
  const [time, setTime] = useState('');
  const [cpuLoad, setCpuLoad] = useState(24);

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setCpuLoad(Math.floor(18 + Math.random() * 22));
    }, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-[52px] border-b border-white/[0.06] bg-[#080b12]/80 backdrop-blur-xl flex items-center px-5 gap-4 shrink-0 z-30">
      {/* Title */}
      <div className="flex items-center gap-3">
        <h1 className="text-[15px] font-bold tracking-tight text-white">
          DNK <span className="text-[#00dc82]">OS</span>
        </h1>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400" />
          </span>
          <span className="text-[10px] font-semibold text-emerald-400 tracking-widest uppercase">Kernel Online</span>
        </div>
      </div>

      {/* Branch */}
      <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-mono pl-2 border-l border-white/[0.06]">
        <GitBranch size={12} />
        <span className="text-slate-400">dnk-mvp/feature/dnk-studio-arch-001</span>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Search */}
      <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.06] text-slate-500 text-[11px] transition-colors">
        <Search size={13} />
        <span>Search...</span>
        <kbd className="text-[9px] bg-white/[0.06] px-1.5 py-0.5 rounded font-mono">⌘K</kbd>
      </button>

      {/* Stats pills */}
      <div className="flex items-center gap-2">
        <StatPill value={agentCount} label="Agents" color="#a78bfa" />
        <StatPill value={serviceCount} label="Services" color="#22d3ee" />
        <StatPill value={taskCount} label="Tasks" color="#f59e0b" />
      </div>

      {/* Divider */}
      <div className="w-px h-5 bg-white/[0.08]" />

      {/* CPU */}
      <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
        <Cpu size={13} className="text-purple-400" />
        <span className="text-slate-300 font-mono">{cpuLoad}%</span>
      </div>

      {/* Clock */}
      <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
        <Clock size={12} />
        <span>{time}</span>
      </div>

      {/* Notifications */}
      <button className="relative p-1.5 rounded-lg hover:bg-white/[0.06] text-slate-500 hover:text-slate-300 transition-colors">
        <Bell size={15} />
        <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-purple-500 rounded-full" />
      </button>
    </header>
  );
}

function StatPill({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium"
      style={{ background: `${color}12`, border: `1px solid ${color}25` }}
    >
      <span className="font-bold font-mono" style={{ color }}>{value}</span>
      <span className="text-slate-500">{label}</span>
    </div>
  );
}
