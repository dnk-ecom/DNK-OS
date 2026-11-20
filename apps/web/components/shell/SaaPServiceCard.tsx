// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/SaaPServiceCard.tsx"
// purpose: "Glassmorphic card for a single SaaP service showing status, metrics and sparkline."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useEffect, useState } from 'react';
import {
  Video, ShoppingBag, Search, Mic, Music, BarChart3,
  Globe, Database, Zap, Bot, Layers, Activity
} from 'lucide-react';

export interface SaaPService {
  id: string;
  name: string;
  domain: string;
  status: 'active' | 'idle' | 'error' | 'starting';
  cpu: number;
  requests: number;
  latencyMs: number;
  icon: string;
  color: string;
}

const ICON_MAP: Record<string, React.ElementType> = {
  video: Video,
  shopify: ShoppingBag,
  search: Search,
  voice: Mic,
  media: Music,
  analytics: BarChart3,
  web: Globe,
  data: Database,
  ai: Zap,
  agent: Bot,
  layers: Layers,
  default: Activity,
};

const STATUS_CONFIG = {
  active:   { label: 'ACTIVE',    bg: '#00dc8214', border: '#00dc8240', text: '#00dc82' },
  idle:     { label: 'IDLE',      bg: '#94a3b814', border: '#94a3b840', text: '#94a3b8' },
  error:    { label: 'ERROR',     bg: '#f8717114', border: '#f8717140', text: '#f87171' },
  starting: { label: 'STARTING',  bg: '#f59e0b14', border: '#f59e0b40', text: '#f59e0b' },
};

function generateSparkData(base: number, len = 20): number[] {
  return Array.from({ length: len }, (_, i) =>
    Math.max(0, base + Math.sin(i * 0.8) * 15 + (Math.random() - 0.5) * 20)
  );
}

interface SaaPServiceCardProps {
  service: SaaPService;
  onClick?: () => void;
}

export default function SaaPServiceCard({ service, onClick }: SaaPServiceCardProps) {
  const [sparkData, setSparkData] = useState<number[]>(() => generateSparkData(service.cpu));
  const [cpu, setCpu] = useState(service.cpu);
  const [requests, setRequests] = useState(service.requests);

  useEffect(() => {
    if (service.status !== 'active') return;
    const id = setInterval(() => {
      const newCpu = Math.max(5, Math.min(95, cpu + (Math.random() - 0.5) * 8));
      setCpu(Math.round(newCpu));
      setRequests(r => r + Math.floor(Math.random() * 3));
      setSparkData(d => [...d.slice(1), newCpu]);
    }, 2000);
    return () => clearInterval(id);
  }, [cpu, service.status]);

  const Icon = ICON_MAP[service.icon] || ICON_MAP.default;
  const st = STATUS_CONFIG[service.status];

  return (
    <button
      onClick={onClick}
      className="group relative flex flex-col gap-3 p-4 rounded-2xl text-left cursor-pointer
        transition-all duration-300 hover:scale-[1.015] active:scale-[0.99]
        bg-[#0e1117]/80 border border-white/[0.07]
        hover:border-white/[0.14] hover:bg-[#131720]/90"
      style={{
        boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 32px rgba(0,0,0,0.5), 0 0 20px ${service.color}18`;
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 24px rgba(0,0,0,0.4)';
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5">
          {/* Icon */}
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
            style={{ background: `${service.color}18`, border: `1px solid ${service.color}35` }}
          >
            <Icon size={16} style={{ color: service.color }} />
          </div>
          {/* Name */}
          <div>
            <p className="text-[12px] font-semibold text-slate-200 leading-tight font-mono">
              {service.name}
            </p>
            <p className="text-[10px] text-slate-600 mt-0.5">{service.domain}</p>
          </div>
        </div>

        {/* Status badge */}
        <span
          className="shrink-0 text-[9px] font-bold tracking-widest px-2 py-0.5 rounded-full mt-0.5"
          style={{ background: st.bg, border: `1px solid ${st.border}`, color: st.text }}
        >
          {service.status === 'active' && (
            <span className="inline-flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: st.text }} />
              {st.label}
            </span>
          )}
          {service.status !== 'active' && st.label}
        </span>
      </div>

      {/* Metrics row */}
      <div className="flex items-center gap-4">
        <div>
          <p className="text-[11px] text-slate-600 uppercase tracking-wider">CPU</p>
          <p className="text-[18px] font-bold font-mono text-slate-100 leading-tight">
            {cpu}<span className="text-[11px] text-slate-500 ml-0.5">%</span>
          </p>
        </div>
        <div>
          <p className="text-[11px] text-slate-600 uppercase tracking-wider">Req/min</p>
          <p className="text-[18px] font-bold font-mono text-slate-100 leading-tight">
            {requests}
          </p>
        </div>
        <div>
          <p className="text-[11px] text-slate-600 uppercase tracking-wider">Latency</p>
          <p className="text-[18px] font-bold font-mono leading-tight" style={{ color: service.latencyMs < 100 ? '#00dc82' : service.latencyMs < 300 ? '#f59e0b' : '#f87171' }}>
            {service.latencyMs}<span className="text-[11px] text-slate-500 ml-0.5">ms</span>
          </p>
        </div>
      </div>

      {/* High-fidelity SVG Sparkline */}
      <div className="h-10 w-full overflow-hidden flex items-end pt-1">
        <svg className="w-full h-8 overflow-visible" viewBox="0 0 100 30" preserveAspectRatio="none">
          <defs>
            <linearGradient id={`grad-${service.id}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={service.status === 'active' ? service.color : '#334155'} stopOpacity={0.4} />
              <stop offset="100%" stopColor={service.status === 'active' ? service.color : '#334155'} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          {(() => {
            const min = Math.min(...sparkData, 0);
            const max = Math.max(...sparkData, 100);
            const range = max - min || 1;
            const pts = sparkData.map((val, idx) => {
              const x = (idx / (sparkData.length - 1)) * 100;
              const y = 28 - ((val - min) / range) * 24;
              return `${x.toFixed(1)},${y.toFixed(1)}`;
            });
            const polyPoints = pts.join(' ');
            const areaPoints = `0,30 ${polyPoints} 100,30`;
            return (
              <>
                <polygon points={areaPoints} fill={`url(#grad-${service.id})`} />
                <polyline
                  points={polyPoints}
                  fill="none"
                  stroke={service.status === 'active' ? service.color : '#475569'}
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </>
            );
          })()}
        </svg>
      </div>
    </button>
  );
}
