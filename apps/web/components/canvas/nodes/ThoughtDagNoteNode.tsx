// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_nodes_ThoughtDagNoteNode"
// purpose: "ThoughtDAG Infinite Palette Living Note Node: ReactFlow Node component with markdown content, selection range, highlight modes, and source handles for downstream swarm agents"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-16"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { memo, useState, useCallback, useEffect } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  FileText,
  Filter,
  Tag,
  AlertTriangle,
  Clock,
  User,
  Hash,
  Sparkles,
  Check,
  ChevronDown,
  RefreshCw,
} from 'lucide-react';
import { useCanvasStore } from '../../../store/canvasStore';
import type { ThoughtDagNoteData, HighlightMode } from '../../../src/canvas/types/thoughtdag';
import {
  parseContentIntoBlocks,
  formatBlockHandleId,
  TextBlockItem,
} from '../../../src/canvas/nodes/textBlockParser';

const HIGHLIGHT_MODE_CONFIG: Record<HighlightMode, { label: string; bg: string; text: string; border: string; icon: React.ReactNode }> = {
  filter: {
    label: 'FILTER',
    bg: 'bg-cyan-950/60',
    text: 'text-cyan-300',
    border: 'border-cyan-500/40',
    icon: <Filter className="w-3 h-3" />
  },
  tag: {
    label: 'TAG',
    bg: 'bg-emerald-950/60',
    text: 'text-emerald-300',
    border: 'border-emerald-500/40',
    icon: <Tag className="w-3 h-3" />
  },
  off: {
    label: 'STANDARD',
    bg: 'bg-slate-900/60',
    text: 'text-slate-400',
    border: 'border-slate-700/40',
    icon: null
  }
};

export const ThoughtDagNoteNode = memo(({ id, data, selected }: NodeProps) => {
  const noteData = (data || {}) as unknown as ThoughtDagNoteData;
  const updateNodeData = useCanvasStore((state) => state.updateNodeData);
  const setNoteHighlightMode = useCanvasStore((state) => state.setNoteHighlightMode);

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(noteData.title || 'Living Note');
  const [contentInput, setContentInput] = useState(noteData.content || '');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showBlockHandles, setShowBlockHandles] = useState(false);
  const compileNodeContext = useCanvasStore((state) => state.compileNodeContext);
  const isReevaluating = useCanvasStore((state) => state.isReevaluating);
  const runDAGReevaluation = useCanvasStore((state) => state.runDAGReevaluation);

  const handleReevaluateDAG = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!runDAGReevaluation || isReevaluating) return;
    try {
      await runDAGReevaluation({ targetNodeId: id, onlyStale: true });
    } catch (err) {
      console.error('DAG Re-evaluation failed:', err);
    }
  };

  const currentMode = noteData.highlightMode || 'off';
  const modeBadge = HIGHLIGHT_MODE_CONFIG[currentMode] || HIGHLIGHT_MODE_CONFIG.off;

  const blocks: TextBlockItem[] = React.useMemo(() => {
    return parseContentIntoBlocks(contentInput || noteData.content || '');
  }, [contentInput, noteData.content]);

  const handleTitleSubmit = useCallback(() => {
    setIsEditingTitle(false);
    updateNodeData(id, {
      title: titleInput,
      updatedAt: Date.now()
    });
  }, [id, titleInput, updateNodeData]);

  const handleContentBlur = useCallback(() => {
    updateNodeData(id, {
      content: contentInput,
      updatedAt: Date.now()
    });
  }, [id, contentInput, updateNodeData]);

  // Debounced auto-save so typing immediately triggers staleness and reactive graph propagation without waiting for onBlur
  useEffect(() => {
    if (contentInput === (noteData.content || '')) return;
    const timer = setTimeout(() => {
      updateNodeData(id, {
        content: contentInput,
        updatedAt: Date.now()
      });
    }, 200);
    return () => clearTimeout(timer);
  }, [id, contentInput, noteData.content, updateNodeData]);

  const handleTextSelection = useCallback((e: React.SyntheticEvent<HTMLTextAreaElement>) => {
    const target = e.target as HTMLTextAreaElement;
    const start = target.selectionStart;
    const end = target.selectionEnd;
    if (start !== undefined && end !== undefined && start !== end) {
      const selectedStr = target.value.substring(start, end).trim();
      if (selectedStr) {
        updateNodeData(id, {
          selectedText: selectedStr,
          updatedAt: Date.now()
        });
      }
    }
  }, [id, updateNodeData]);

  const cycleHighlightMode = useCallback(() => {
    const modes: HighlightMode[] = ['off', 'filter', 'tag'];
    const nextIdx = (modes.indexOf(currentMode) + 1) % modes.length;
    setNoteHighlightMode(id, modes[nextIdx]);
  }, [id, currentMode, setNoteHighlightMode]);

  return (
    <div
      className={`w-[340px] rounded-2xl bg-[#121620]/95 backdrop-blur-2xl border p-4 text-slate-200 shadow-2xl transition-all font-sans relative ${
        noteData.isStale
          ? 'border-amber-500/80 ring-2 ring-amber-500/40 shadow-[0_0_20px_rgba(245,158,11,0.25)]'
          : selected
          ? 'border-indigo-500 ring-2 ring-indigo-500/30 shadow-[0_0_30px_rgba(99,102,241,0.25)]'
          : 'border-[#232938] hover:border-slate-700'
      }`}
    >
      {/* 
        INVARIANT 2:
        - Top & Left Handles: TARGET (for incoming references from upstream notes/documents)
        - Bottom & Right Handles: SOURCE (primary wire connectors to downstream Swarm Agents)
      */}
      <Handle
        type="target"
        position={Position.Top}
        id="target-top"
        className="w-3 h-3 bg-indigo-400 border-2 border-[#121620] rounded-full shadow-[0_0_8px_#818cf8] -top-1.5"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="target-left"
        className="w-3 h-3 bg-indigo-400 border-2 border-[#121620] rounded-full shadow-[0_0_8px_#818cf8] -left-1.5"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="source-right"
        className="w-3 h-3 bg-emerald-400 border-2 border-[#121620] rounded-full shadow-[0_0_8px_#34d399] -right-1.5"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="source-bottom"
        className="w-3 h-3 bg-emerald-400 border-2 border-[#121620] rounded-full shadow-[0_0_8px_#34d399] -bottom-1.5"
      />

      {/* Dynamic Block/Paragraph-level Handles on Right Edge */}
      {blocks.map((block, idx) => {
        const handleId = formatBlockHandleId(block.id);
        const topOffset = 80 + idx * 28;
        return (
          <Handle
            key={handleId}
            type="source"
            position={Position.Right}
            id={handleId}
            style={{ top: `${topOffset}px` }}
            className={`w-2.5 h-2.5 !bg-cyan-400 border-2 border-[#121620] rounded-full shadow-[0_0_6px_#38bdf8] transition-all hover:scale-150 ${
              showBlockHandles ? 'opacity-100' : 'opacity-0 pointer-events-none'
            }`}
            title={`Wire from paragraph block: ${block.id}`}
          />
        );
      })}

      {/* Dynamic Text Selection Handle when Text is Selected */}
      {noteData.selectedText && (
        <Handle
          type="source"
          position={Position.Right}
          id="handle-sel-active"
          style={{ top: '65px' }}
          className="w-2.5 h-2.5 !bg-amber-400 border-2 border-[#121620] rounded-full shadow-[0_0_6px_#f59e0b] hover:scale-150"
          title={`Wire selected text: "${noteData.selectedText.slice(0, 20)}..."`}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-2.5 pb-2 border-b border-[#232938]">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
          {isEditingTitle ? (
            <input
              type="text"
              value={titleInput}
              onChange={(e) => setTitleInput(e.target.value)}
              onBlur={handleTitleSubmit}
              onKeyDown={(e) => e.key === 'Enter' && handleTitleSubmit()}
              autoFocus
              className="bg-[#1b2030] text-sm text-white px-1.5 py-0.5 rounded border border-indigo-500/50 outline-none w-full"
            />
          ) : (
            <span
              onClick={() => setIsEditingTitle(true)}
              className="font-semibold text-sm text-white truncate cursor-pointer hover:text-indigo-300 transition-colors"
              title="Click to edit title"
            >
              {noteData.title || 'Living Note'}
            </span>
          )}
        </div>

        {/* Highlight Mode Badge & Selectors */}
        <div className="flex items-center gap-1.5 shrink-0 ml-2">
          <div className="flex items-center gap-0.5 bg-[#161a26] p-0.5 rounded-lg border border-slate-800">
            {(['off', 'filter', 'tag'] as HighlightMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setNoteHighlightMode(id, mode)}
                className={`px-1.5 py-0.5 text-[9px] font-mono uppercase rounded transition-colors cursor-pointer ${
                  currentMode === mode
                    ? 'bg-indigo-600 text-white font-bold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title={`Switch to ${mode} mode`}
              >
                {mode}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowPreview((p) => !p)}
            className={`p-1 rounded-md border text-[10px] transition-colors cursor-pointer ${
              showPreview
                ? 'bg-indigo-950/80 border-indigo-500/50 text-indigo-300'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
            title="Toggle compiled prompt context preview"
          >
            <Sparkles className="w-3 h-3" />
          </button>
          <button
            onClick={() => setShowBlockHandles((b) => !b)}
            className={`px-1.5 py-0.5 rounded-md border text-[10px] font-mono transition-colors cursor-pointer flex items-center gap-1 ${
              showBlockHandles
                ? 'bg-cyan-950/80 border-cyan-500/50 text-cyan-300 font-bold'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
            title="Toggle Paragraph/Block connection handles"
          >
            <span>§</span>
            <span>{blocks.length}</span>
          </button>
        </div>
      </div>

      {/* Tag editor when in 'tag' mode */}
      {currentMode === 'tag' && (
        <div className="flex items-center gap-1.5 mb-2 px-2 py-1 bg-amber-950/20 border border-amber-500/30 rounded-lg text-xs">
          <Hash className="w-3 h-3 text-amber-400 shrink-0" />
          <input
            type="text"
            value={noteData.tag || ''}
            onChange={(e) => updateNodeData(id, { tag: e.target.value, updatedAt: Date.now() })}
            placeholder="context-tag (e.g. constraints, api)"
            className="w-full bg-transparent text-amber-200 outline-none placeholder:text-amber-500/50 text-[11px] font-mono"
          />
        </div>
      )}

      {/* Live Compiled Context Preview Sub-panel */}
      {showPreview && (
        <div className="mb-2.5 p-2.5 rounded-lg bg-slate-950 border border-indigo-500/40 text-[11px] font-mono text-slate-300 space-y-1.5">
          <div className="flex items-center justify-between text-indigo-400 font-bold uppercase text-[9px]">
            <span>Compiled Prompt Preview</span>
            <span>Mode: {currentMode}</span>
          </div>
          <div className="max-h-28 overflow-y-auto whitespace-pre-wrap break-words rounded bg-[#0b0e14] p-2 text-[10px] text-slate-300 border border-slate-800">
            {compileNodeContext ? compileNodeContext(id).rawText || '(Empty prompt)' : '(Store unmounted)'}
          </div>
        </div>
      )}

      {/* Block Connection Handles Sub-panel */}
      {showBlockHandles && (
        <div className="mb-2.5 p-2 rounded-lg bg-[#0b0e14] border border-cyan-500/40 text-[10px] space-y-1.5">
          <div className="flex items-center justify-between text-cyan-400 font-bold uppercase text-[9px]">
            <span>Paragraph Connection Handles ({blocks.length})</span>
            <span className="text-[8px] text-slate-400">Drag wires from cyan dots</span>
          </div>
          <div className="max-h-28 overflow-y-auto space-y-1">
            {blocks.map((block) => (
              <div
                key={block.id}
                className="p-1 rounded bg-[#161a26] border border-slate-800 text-slate-300 flex items-start justify-between gap-1.5"
              >
                <span className="font-mono text-cyan-300 shrink-0 font-bold">§ {block.id}</span>
                <span className="truncate flex-1 text-slate-400">{block.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tag and Metadata Bar */}
      {(noteData.tag || noteData.author) && (
        <div className="flex items-center gap-2 mb-2 text-[11px] text-slate-400">
          {noteData.tag && (
            <span className="flex items-center gap-1 bg-slate-800/80 px-2 py-0.5 rounded text-indigo-300 border border-indigo-500/20">
              <Hash className="w-2.5 h-2.5" />
              {noteData.tag}
            </span>
          )}
          {noteData.author && (
            <span className="flex items-center gap-1">
              <User className="w-2.5 h-2.5" />
              {noteData.author}
            </span>
          )}
        </div>
      )}

      {/* Stale Context Alert (if upstream changed) */}
      {noteData.isStale && (
        <div className="mb-2.5 p-2 rounded-lg bg-amber-950/40 border border-amber-500/40 flex items-center justify-between gap-2 text-amber-300 text-xs">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
            <span className="leading-tight">Context out of date.</span>
          </div>
          <button
            type="button"
            onClick={handleReevaluateDAG}
            disabled={isReevaluating}
            className="flex items-center gap-1 rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-semibold text-amber-200 border border-amber-500/40 hover:bg-amber-500/40 transition-colors cursor-pointer shrink-0"
            title="Re-evaluate DAG"
          >
            <RefreshCw className={`w-3 h-3 ${isReevaluating ? 'animate-spin' : ''}`} />
            <span>{isReevaluating ? 'Re-eval...' : 'Re-eval'}</span>
          </button>
        </div>
      )}

      {/* Content Area / Markdown Input */}
      <div className="space-y-2">
        <textarea
          value={contentInput}
          onChange={(e) => setContentInput(e.target.value)}
          onBlur={handleContentBlur}
          onSelect={handleTextSelection}
          placeholder="Enter note thoughts, requirements, or architecture context..."
          rows={4}
          className="w-full text-xs bg-[#161a26] text-slate-200 border border-[#2b3345] rounded-lg p-2.5 focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/40 outline-none resize-none leading-relaxed transition-all placeholder:text-slate-500"
        />

        {/* Selected Context Sub-card (when snippet is highlighted) */}
        {noteData.selectedText && (
          <div className="p-2 rounded bg-indigo-950/30 border border-indigo-500/30 text-[11px] text-indigo-200">
            <div className="flex items-center justify-between mb-1 text-[10px] text-indigo-400 font-semibold uppercase tracking-wider">
              <span className="flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Active Wire Context
              </span>
              <button
                onClick={() => updateNodeData(id, { selectedText: undefined })}
                className="text-slate-400 hover:text-white"
              >
                Clear
              </button>
            </div>
            <p className="line-clamp-2 italic text-slate-300">"{noteData.selectedText}"</p>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="mt-3 pt-2 border-t border-[#1e2433] flex items-center justify-between text-[10px] text-slate-500">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{new Date(noteData.updatedAt || Date.now()).toLocaleTimeString()}</span>
        </div>
        {noteData.upstreamFingerprint && (
          <span className="font-mono text-[9px] text-slate-600 truncate max-w-[120px]" title={noteData.upstreamFingerprint}>
            fp:{noteData.upstreamFingerprint.substring(0, 8)}
          </span>
        )}
      </div>
    </div>
  );
});

ThoughtDagNoteNode.displayName = 'ThoughtDagNoteNode';
export default ThoughtDagNoteNode;
