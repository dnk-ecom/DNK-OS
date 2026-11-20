// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/nodes/TextNode.tsx"
// purpose: "Canvas Text & Markdown Node with block-level visual connection handles and text selection wiring."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import React, { useState, useMemo, useRef, useCallback } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { AlertCircle } from 'lucide-react';
import {
  parseContentIntoBlocks,
  formatBlockHandleId,
  TextBlockItem,
} from './textBlockParser';
import { ThoughtDagNoteData } from '../types/thoughtdag';

export interface TextNodeProps extends NodeProps {
  data: any;
}

/**
 * TextNode: A visual canvas node allowing fine-grained connections directly from
 * paragraphs, markdown blocks, or highlighted text selections via custom ReactFlow Handles.
 */
export const TextNode: React.FC<NodeProps> = ({ id, data, selected }) => {
  const noteData = (data || {}) as unknown as ThoughtDagNoteData;
  const isStale = Boolean(data?.isStale);
  const [content, setContent] = useState<string>(noteData?.content || '');
  const [title, setTitle] = useState<string>(noteData?.title || 'Text Note');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [selectedText, setSelectedText] = useState<string>(noteData?.selectedText || '');
  const [activeBlockId, setActiveBlockId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'edit' | 'blocks'>('blocks');

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Deterministically parse content into stable blocks/paragraphs
  const blocks: TextBlockItem[] = useMemo(() => {
    return parseContentIntoBlocks(content);
  }, [content]);

  // Handle text selection inside the textarea
  const handleTextSelection = useCallback(() => {
    if (!textareaRef.current) return;
    const { selectionStart, selectionEnd, value } = textareaRef.current;
    if (selectionStart !== selectionEnd) {
      const selected = value.substring(selectionStart, selectionEnd).trim();
      setSelectedText(selected);
    }
  }, []);

  return (
    <div
      className={`relative rounded-xl border transition-all duration-200 select-none min-w-[280px] max-w-[340px] shadow-lg ${
        isStale
          ? 'ring-2 ring-amber-500/80 border-amber-500/80 shadow-[0_0_15px_rgba(245,158,11,0.25)] bg-[#162c2f]/95'
          : selected
          ? 'ring-2 ring-cyan-400 border-cyan-400 bg-[#162c2f]/95 shadow-cyan-900/30'
          : 'border-[#224447] bg-[#162c2f]/90 hover:border-cyan-500/50'
      }`}
      style={{
        backgroundColor: '#162c2f',
        borderColor: isStale ? '#f59e0b' : selected ? '#35d5d5' : '#224447',
        color: '#d4d8db',
      }}
    >
      {/* Default Top/Left Target Handles for General Inbound Connections */}
      <Handle
        type="target"
        position={Position.Top}
        id="target-top"
        className="w-2.5 h-2.5 !bg-cyan-400 border-2 border-[#112224] transition-transform hover:scale-125"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="target-left"
        className="w-2.5 h-2.5 !bg-cyan-400 border-2 border-[#112224] transition-transform hover:scale-125"
      />

      {/* Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#224447] bg-[#112224]/80 rounded-t-xl">
        <div className="flex items-center gap-2 truncate">
          <span className={`w-2 h-2 rounded-full ${isStale ? 'bg-amber-400 animate-ping' : 'bg-emerald-400 animate-pulse'}`} />
          {isEditingTitle ? (
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onBlur={() => setIsEditingTitle(false)}
              onKeyDown={(e) => e.key === 'Enter' && setIsEditingTitle(false)}
              className="bg-transparent text-cyan-300 font-semibold text-xs outline-none border-b border-cyan-400"
              autoFocus
            />
          ) : (
            <span
              onClick={() => setIsEditingTitle(true)}
              className="font-medium text-xs text-cyan-300 hover:underline cursor-pointer truncate"
              title="Click to rename"
            >
              {title}
            </span>
          )}
          {isStale && (
            <span className="flex items-center gap-1 text-[9px] font-semibold text-amber-400 bg-amber-950/70 border border-amber-500/40 px-1.5 py-0.2 rounded-full">
              <AlertCircle className="w-2.5 h-2.5" />
              Stale
            </span>
          )}
        </div>

        {/* View Mode Toggle: Edit raw markdown vs Paragraph Blocks */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setViewMode(viewMode === 'edit' ? 'blocks' : 'edit')}
            className="px-1.5 py-0.5 text-[9px] font-mono rounded bg-[#1e2022] hover:bg-[#2a6368] text-cyan-200 border border-[#224447] transition-colors"
            title="Toggle between block handles view and raw edit"
          >
            {viewMode === 'edit' ? 'Blocks' : 'Edit'}
          </button>
        </div>
      </div>

      {/* Body Area */}
      <div className="p-3 space-y-2">
        {viewMode === 'edit' ? (
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onSelect={handleTextSelection}
              onMouseUp={handleTextSelection}
              onKeyUp={handleTextSelection}
              rows={5}
              placeholder="Enter note text. Separate paragraphs with blank lines..."
              className="w-full bg-[#112224] border border-[#224447] focus:border-cyan-400 rounded-lg p-2 text-xs text-[#d4d8db] placeholder-slate-500 outline-none resize-none font-sans leading-relaxed"
            />
            {selectedText && (
              <div className="mt-1.5 flex items-center justify-between p-1.5 bg-[#1e2022] border border-cyan-500/30 rounded text-[10px] text-cyan-300">
                <span className="truncate max-w-[200px]">
                  Selection: &ldquo;{selectedText}&rdquo;
                </span>
                <button
                  type="button"
                  onClick={() => setSelectedText('')}
                  className="text-slate-400 hover:text-white text-xs ml-1"
                >
                  &times;
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Blocks View with Interactive Visual Connection Handles */
          <div className="space-y-2">
            {blocks.length === 0 ? (
              <p className="text-[11px] text-slate-400 italic">No content. Switch to Edit to add text.</p>
            ) : (
              blocks.map((block) => {
                const handleId = formatBlockHandleId(block.id);
                const isActive = activeBlockId === block.id;

                return (
                  <div
                    key={block.id}
                    onClick={() => setActiveBlockId(block.id)}
                    className={`relative p-2 rounded-lg border text-xs transition-all cursor-pointer ${
                      isActive
                        ? 'border-cyan-400 bg-[#112224] text-white shadow-sm'
                        : 'border-[#224447]/60 bg-[#112224]/50 text-[#d4d8db] hover:border-cyan-500/40'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[9px] font-mono text-cyan-400 font-bold">
                        § {block.id}
                      </span>
                      {block.tag && (
                        <span className="text-[9px] bg-[#2a6368] px-1 rounded text-cyan-100">
                          {block.tag}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] leading-snug break-words">
                      {block.text}
                    </p>

                    {/* Dedicated Block-Level Handle on the Right side */}
                    <Handle
                      type="source"
                      position={Position.Right}
                      id={handleId}
                      className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-[#112224] !transition-transform hover:!scale-150"
                      style={{ top: '50%', right: '-5px' }}
                      title={`Connect wire from block § ${block.id}`}
                    />
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>

      {/* Global Bottom/Right Default Handles */}
      <Handle
        type="source"
        position={Position.Right}
        id="source-right"
        className="w-2.5 h-2.5 !bg-cyan-400 border-2 border-[#112224] transition-transform hover:scale-125"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="source-bottom"
        className="w-2.5 h-2.5 !bg-cyan-400 border-2 border-[#112224] transition-transform hover:scale-125"
      />
    </div>
  );
};

export default TextNode;
