// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/nodes/ArtifactSandboxNode.tsx"
// purpose: "Spatial Canvas Node rendering interactive Web Component Sandbox with real-time editing & multi-format export."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-30"
// author: "Denchik (Master Developer) & Antigravity (Mentor)"
// --- END DNK-MRH-HEADER ---

import React, { useState } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import {
  Code,
  Eye,
  Trash2,
  Share2,
  Layers,
  Sparkles,
  Maximize2,
  Check,
  Download,
} from 'lucide-react';
import { useCanvasStore } from '../../../store/canvasStore';
import type { ArtifactNodeData, ArtifactViewport } from '../../../types/artifact';
import { ComponentSandbox } from '../ComponentSandbox';

export const ArtifactSandboxNode: React.FC<NodeProps> = ({ id, data, selected }) => {
  const nodeData = data as unknown as ArtifactNodeData;
  const removeNode = useCanvasStore((s) => s.removeNode);
  const updateNodeData = useCanvasStore((s) => s.updateNodeData);

  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [codeValue, setCodeValue] = useState(nodeData.code || '');
  const [viewport, setViewport] = useState<ArtifactViewport>(nodeData.viewport || 'inline');
  const [isExported, setIsExported] = useState(false);

  const handleSaveCode = () => {
    updateNodeData(id, {
      code: codeValue,
      lastModified: new Date().toISOString(),
    });
    setActiveTab('preview');
  };

  const handleExport = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(codeValue);
    setIsExported(true);
    setTimeout(() => setIsExported(false), 2000);
  };

  const handleViewportChange = (newVp: ArtifactViewport) => {
    setViewport(newVp);
    updateNodeData(id, { viewport: newVp });
  };

  return (
    <div
      className={`relative group rounded-xl bg-[#162c2f]/95 border text-slate-200 shadow-2xl backdrop-blur-md transition-all duration-200 select-none ${
        selected ? 'border-[#35d5d5] ring-2 ring-[#35d5d5]/30' : 'border-[#224447]'
      }`}
      style={{
        width: viewport === 'mobile' ? 420 : viewport === 'tablet' ? 820 : 540,
        maxWidth: '90vw',
      }}
    >
      {/* React Flow Handles */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-[#35d5d5] !border-2 !border-[#112224] transition-transform hover:scale-125"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-[#22c55e] !border-2 !border-[#112224] transition-transform hover:scale-125"
      />

      {/* Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-[#112224] border-b border-[#224447] rounded-t-xl">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded bg-[#35d5d5]/15 text-[#35d5d5]">
            <Layers className="w-3.5 h-3.5" />
          </span>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-slate-100 tracking-wide flex items-center gap-1.5">
              {nodeData.title || 'Live Web Component'}
              <span className="text-[10px] font-mono font-normal text-emerald-400 bg-emerald-500/10 px-1 py-0.2 rounded border border-emerald-500/20">
                Sandboxed
              </span>
            </span>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-1">
          {/* Tab Switcher: Preview / Code */}
          <div className="flex bg-[#162c2f] p-0.5 rounded border border-[#224447]">
            <button
              type="button"
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2 py-0.5 text-xs rounded transition-colors ${
                activeTab === 'preview'
                  ? 'bg-[#35d5d5]/20 text-[#35d5d5] font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Live</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2 py-0.5 text-xs rounded transition-colors ${
                activeTab === 'code'
                  ? 'bg-[#35d5d5]/20 text-[#35d5d5] font-medium'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3 h-3" />
              <span>Source</span>
            </button>
          </div>

          {/* Export Code */}
          <button
            type="button"
            onClick={handleExport}
            className="p-1 rounded text-slate-400 hover:text-[#35d5d5] hover:bg-[#162c2f] transition-colors"
            title="Export / Copy Component Code"
          >
            {isExported ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Download className="w-3.5 h-3.5" />}
          </button>

          {/* Delete Node */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              removeNode(id);
            }}
            className="p-1 rounded text-slate-400 hover:text-red-400 hover:bg-[#162c2f] transition-colors"
            title="Delete Artifact Node"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Node Body */}
      <div className="p-2 bg-[#162c2f]">
        {activeTab === 'preview' ? (
          <ComponentSandbox
            code={nodeData.code || codeValue}
            kind={nodeData.kind || 'html_tailwind'}
            viewport={viewport}
            onViewportChange={handleViewportChange}
          />
        ) : (
          <div className="flex flex-col gap-2 p-1">
            <textarea
              value={codeValue}
              onChange={(e) => setCodeValue(e.target.value)}
              className="w-full h-72 font-mono text-xs p-2.5 bg-[#112224] text-slate-200 border border-[#224447] rounded-lg focus:outline-none focus:border-[#35d5d5] focus:ring-1 focus:ring-[#35d5d5] resize-y"
              placeholder="Paste or edit HTML / Tailwind / Liquid code..."
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setCodeValue(nodeData.code || '');
                  setActiveTab('preview');
                }}
                className="px-2.5 py-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveCode}
                className="px-3 py-1 text-xs font-medium rounded bg-[#35d5d5] text-[#112224] hover:bg-[#35d5d5]/90 transition-colors"
              >
                Apply Changes
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#112224]/80 border-t border-[#224447] text-[11px] text-slate-400 rounded-b-xl">
        <span className="flex items-center gap-1 font-mono text-[10px]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Vite Native Sandbox
        </span>
        <span className="text-[10px] text-slate-500 font-mono">
          {nodeData.lastModified ? `Updated ${new Date(nodeData.lastModified).toLocaleTimeString()}` : 'Ready'}
        </span>
      </div>
    </div>
  );
};

export default ArtifactSandboxNode;
