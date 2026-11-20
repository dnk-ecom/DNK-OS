// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_edges_ContextWireEdge"
// purpose: "ThoughtDAG Context Wire Edge with interactive scope toggle badge and animated cybernetic styling"
// author: "DNK-e.com Maksym"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// --- END DNK-MRH-HEADER ---

'use client';

import React from 'react';
import {
  BaseEdge,
  EdgeProps,
  getBezierPath,
  EdgeLabelRenderer,
  MarkerType,
} from '@xyflow/react';
import { Sparkles, FileText, RefreshCw, AlertCircle } from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';

export interface ContextWireEdgeData {
  scope?: 'all' | 'selection';
  isStale?: boolean;
  highlightMode?: string;
  bytes?: number;
  [key: string]: unknown;
}

export default function ContextWireEdge({
  id,
  source,
  target,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  data,
  selected,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const edgeData = (data || {}) as ContextWireEdgeData;
  const scope = edgeData.scope || 'all';
  const isStale = Boolean(edgeData.isStale);
  const updateEdgeData = useCanvasStore((s) => s.updateEdgeData);
  const syncNodeContext = useCanvasStore((s) => s.syncNodeContext);

  const toggleScope = (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextScope = scope === 'selection' ? 'all' : 'selection';
    if (updateEdgeData) {
      updateEdgeData(id, { scope: nextScope });
    }
  };

  const handleQuickSync = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (syncNodeContext && target) {
      syncNodeContext(target);
    }
  };

  const strokeColor = isStale
    ? '#f59e0b' // Amber/Warning when stale
    : selected
    ? '#38bdf8' // Sky blue when selected
    : '#06b6d4'; // Cyan default

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd || MarkerType.ArrowClosed}
        style={{
          stroke: strokeColor,
          strokeWidth: selected ? 2.5 : isStale ? 2.5 : 2,
          strokeDasharray: isStale ? '5 5' : '6 3',
          filter: isStale
            ? 'drop-shadow(0 0 5px rgba(245, 158, 11, 0.7))'
            : selected
            ? 'drop-shadow(0 0 6px rgba(56, 189, 248, 0.6))'
            : 'none',
          animation: 'dashdraw 30s linear infinite',
          ...style,
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={toggleScope}
              title={`Click to toggle scope. Current: ${scope === 'selection' ? 'Filter Selection Only' : 'Full Note Content'}`}
              className={`group flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-medium tracking-wide transition-all duration-150 backdrop-blur-md shadow-lg border ${
                isStale
                  ? 'bg-amber-950/80 border-amber-500/50 text-amber-300 hover:bg-amber-900/90'
                  : scope === 'selection'
                  ? 'bg-cyan-950/80 border-cyan-500/50 text-cyan-300 hover:bg-cyan-900/90'
                  : 'bg-slate-900/90 border-slate-700/80 text-slate-300 hover:bg-slate-800'
              }`}
            >
              {isStale ? (
                <AlertCircle className="h-3 w-3 text-amber-400 animate-pulse" />
              ) : scope === 'selection' ? (
                <Sparkles className="h-3 w-3 text-cyan-400" />
              ) : (
                <FileText className="h-3 w-3 text-slate-400" />
              )}
              <span>
                {isStale
                  ? 'Stale Wire'
                  : scope === 'selection'
                  ? 'Wire: Selection'
                  : 'Wire: Full'}
              </span>
            </button>
            {isStale && (
              <button
                type="button"
                onClick={handleQuickSync}
                title="Quick-sync target node context with latest upstream state"
                className="flex items-center justify-center p-1 rounded-full bg-amber-500/20 border border-amber-500/50 text-amber-300 hover:bg-amber-500/40 hover:text-amber-100 transition-colors shadow-sm cursor-pointer"
              >
                <RefreshCw className="h-2.5 w-2.5 hover:rotate-180 transition-transform" />
              </button>
            )}
          </div>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
