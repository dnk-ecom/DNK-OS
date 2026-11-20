// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_MacroClusterNode"
// purpose: "XYFlow Custom Node for Macro Workhorse Clusters (Task Forest L0), Semantic Zoom, and Subgraph Expansion"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  ShoppingBag,
  Film,
  TrendingUp,
  Cpu,
  Layers,
  ChevronRight,
  CheckCircle2,
  Sparkles,
  ArrowUpRight,
  Sliders,
  PlayCircle,
  BarChart2,
  Database
} from 'lucide-react';

export interface MacroClusterNodeData {
  hubId: 'shopify' | 'media' | 'distribution' | 'core';
  title: string;
  subtitle: string;
  versionBadge: string;
  progressPercent: number;
  totalTasks: number;
  completedTasks: number;
  metricLabel: string;
  metricValue: string;
  isExpanded?: boolean;
  onToggleExpand?: (hubId: string) => void;
  onActionClick?: (hubId: string, actionType: string) => void;
}

interface HubMeta {
  accentColor: string;
  borderColor: string;
  glowClass: string;
  badgeBg: string;
  icon: React.ReactNode;
  tags: string[];
  actionLabel: string;
  actionIcon: React.ReactNode;
}

const HUB_META: Record<MacroClusterNodeData['hubId'], HubMeta> = {
  shopify: {
    accentColor: '#10b981',
    borderColor: 'border-emerald-500/30 hover:border-emerald-500/60',
    glowClass: 'hover:shadow-[0_0_24px_rgba(16,185,129,0.12)]',
    badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    icon: <ShoppingBag className="w-4 h-4 text-emerald-400" />,
    tags: ['Sticky ATC', 'Cart Rewards', 'PDP Upsell', 'Liquid 2.0'],
    actionLabel: 'Студія Блоків',
    actionIcon: <Sliders className="w-3 h-3 text-emerald-400" />,
  },
  media: {
    accentColor: '#f43f5e',
    borderColor: 'border-rose-500/30 hover:border-rose-500/60',
    glowClass: 'hover:shadow-[0_0_24px_rgba(244,63,94,0.12)]',
    badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    icon: <Film className="w-4 h-4 text-rose-400" />,
    tags: ['60FPS WebGL', 'Remotion AST', 'Viral Hook', 'Beat Sync'],
    actionLabel: 'Студія Відео',
    actionIcon: <PlayCircle className="w-3 h-3 text-rose-400" />,
  },
  distribution: {
    accentColor: '#3b82f6',
    borderColor: 'border-blue-500/30 hover:border-blue-500/60',
    glowClass: 'hover:shadow-[0_0_24px_rgba(59,130,246,0.12)]',
    badgeBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    icon: <TrendingUp className="w-4 h-4 text-blue-400" />,
    tags: ['TikTok', 'Instagram', 'Shorts / X', 'DTC Funnel'],
    actionLabel: 'Аналітика DTC',
    actionIcon: <BarChart2 className="w-3 h-3 text-blue-400" />,
  },
  core: {
    accentColor: '#a855f7',
    borderColor: 'border-purple-500/30 hover:border-purple-500/60',
    glowClass: 'hover:shadow-[0_0_24px_rgba(168,85,247,0.12)]',
    badgeBg: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    icon: <Cpu className="w-4 h-4 text-purple-400" />,
    tags: ['FastMCP', 'TaskDNA DAG', 'SCONES Memory', '< 12ms'],
    actionLabel: 'SCONES Пам\'ять',
    actionIcon: <Database className="w-3 h-3 text-purple-400" />,
  },
};

export const MacroClusterNode = memo(({ id, data, selected }: NodeProps<any>) => {
  const nodeData = (data || {}) as MacroClusterNodeData;
  const hubId = nodeData.hubId || 'shopify';
  const meta = HUB_META[hubId] || HUB_META.shopify;
  const isComplete = (nodeData.progressPercent || 0) >= 100;

  return (
    <div
      className={`relative w-[360px] rounded-2xl bg-[#0c0e14]/90 backdrop-blur-2xl p-5 border transition-all duration-300 shadow-2xl ${
        meta.borderColor
      } ${meta.glowClass} ${
        selected ? 'ring-2 ring-emerald-500/80 shadow-[0_0_30px_rgba(16,185,129,0.2)] scale-[1.01]' : ''
      }`}
      data-agent-target="macro-cluster-node"
      data-hub-id={hubId}
    >
      {/* 4 Handles for clean, natural routing in any topological orientation */}
      <Handle
        type="target"
        id="top"
        position={Position.Top}
        className="w-2.5 h-2.5 !bg-zinc-800 border-2 !border-zinc-500 transition-colors"
      />
      <Handle
        type="source"
        id="bottom"
        position={Position.Bottom}
        className="w-2.5 h-2.5 !bg-zinc-800 border-2 !border-zinc-500 transition-colors"
      />
      <Handle
        type="target"
        id="left"
        position={Position.Left}
        className="w-2.5 h-2.5 !bg-zinc-800 border-2 !border-zinc-500 transition-colors"
      />
      <Handle
        type="source"
        id="right"
        position={Position.Right}
        className="w-2.5 h-2.5 !bg-zinc-800 border-2 !border-zinc-500 transition-colors"
      />

      {/* Card Header */}
      <div className="flex items-center justify-between mb-3.5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] shadow-inner">
            {meta.icon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${meta.badgeBg}`}>
                {nodeData.versionBadge || 'Pillar'}
              </span>
              {isComplete && (
                <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-mono">
                  <CheckCircle2 className="w-3 h-3" /> Live
                </span>
              )}
            </div>
            <h3 className="text-sm font-semibold text-white tracking-tight mt-1">
              {nodeData.title || 'Workhorse Hub'}
            </h3>
          </div>
        </div>
      </div>

      {/* Subtitle */}
      <p className="text-xs text-zinc-400 leading-relaxed mb-3.5 line-clamp-2">
        {nodeData.subtitle || 'Sovereign R&D Workhorse Pillar of DNK OS.'}
      </p>

      {/* Domain Interactive Capability Pills */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {meta.tags.map((tag) => (
          <span
            key={tag}
            className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/[0.03] border border-white/[0.06] text-zinc-300"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Compact Telemetry & Progress Strip */}
      <div className="flex items-center justify-between p-2.5 rounded-xl bg-black/40 border border-white/[0.06] text-xs mb-4">
        <div className="flex flex-col">
          <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">
            {nodeData.metricLabel || 'Метрика'}
          </span>
          <span className="font-mono font-bold text-white text-xs mt-0.5">
            {nodeData.metricValue || '100%'}
          </span>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-zinc-500 font-mono">
            {nodeData.completedTasks || 0}/{nodeData.totalTasks || 0} тасок
          </span>
          <div className="w-20 h-1.5 rounded-full bg-zinc-800 border border-white/5 overflow-hidden mt-1">
            <div
              className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
              style={{ width: `${Math.min(100, nodeData.progressPercent || 0)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Action Footer: 2-Action Split */}
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => nodeData.onActionClick?.(hubId, 'studio')}
          className="py-2 px-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs font-medium text-white transition-all flex items-center justify-center gap-1.5 group"
        >
          {meta.actionIcon}
          <span>{meta.actionLabel}</span>
          <ArrowUpRight className="w-3 h-3 text-zinc-500 group-hover:text-white transition-colors" />
        </button>

        <button
          type="button"
          onClick={() => nodeData.onToggleExpand?.(hubId)}
          className="py-2 px-2.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 border border-white/[0.08] text-xs font-medium text-zinc-300 hover:text-emerald-300 transition-all flex items-center justify-center gap-1.5 group"
        >
          <Layers className="w-3 h-3 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
          <span>{nodeData.isExpanded ? 'Згорнути' : 'Розгорнути'}</span>
          <ChevronRight className="w-3 h-3 text-zinc-500 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
});

MacroClusterNode.displayName = 'MacroClusterNode';
