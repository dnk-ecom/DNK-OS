// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_StitchCanvasControls"
// purpose: "Google Stitch Bottom-Right Zoom and History Controls"
// author: "DNK-e.com Maksym"
// status: "Active"
// version: "3.2.0"
// updated_at: "2026-09-17"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState } from 'react';
import { Undo2, Redo2, HelpCircle, ZoomIn, ZoomOut, X } from 'lucide-react';
import { useReactFlow, useViewport } from '@xyflow/react';
import { useCanvasStore } from '../../store/canvasStore';

export default function StitchCanvasControls() {
  const [showHelp, setShowHelp] = useState(false);
  
  const undo = useCanvasStore((s) => s.undo);
  const redo = useCanvasStore((s) => s.redo);
  const historyIndex = useCanvasStore((s) => s.historyIndex);
  const history = useCanvasStore((s) => s.history);
  
  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < (history?.length || 0) - 1;

  let zoomIn = () => {};
  let zoomOut = () => {};
  let fitView = (_options?: any) => {};
  let zoom = 1;

  try {
    const reactFlowInstance = useReactFlow();
    zoomIn = reactFlowInstance.zoomIn;
    zoomOut = reactFlowInstance.zoomOut;
    fitView = reactFlowInstance.fitView;
    const viewport = reactFlowInstance.getViewport();
    zoom = viewport.zoom;
  } catch (e) {
    // Context safety block
  }

  try {
    const vp = useViewport();
    if (vp && typeof vp.zoom === 'number') {
      zoom = vp.zoom;
    }
  } catch (e) {
    // Fallback if not inside ReactFlowProvider
  }

  const zoomPercent = Math.round(zoom * 100);

  return (
    <div className="absolute bottom-6 left-48 z-30 flex items-center gap-2 select-none">
      {/* Undo/Redo & Zoom Group */}
      <div className="flex items-center gap-1.5 bg-[#16181f]/95 border border-white/10 rounded-full px-2.5 py-1.5 shadow-2xl backdrop-blur-2xl">
        <button
          type="button"
          onClick={() => undo()}
          disabled={!canUndo}
          className="p-1 text-neutral-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-neutral-400 rounded-full transition-colors cursor-pointer"
          title="Скасувати (Cmd+Z)"
        >
          <Undo2 className="w-4 h-4" />
        </button>
        
        <button
          type="button"
          onClick={() => redo()}
          disabled={!canRedo}
          className="p-1 text-neutral-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-neutral-400 rounded-full transition-colors cursor-pointer"
          title="Повторити (Shift+Cmd+Z)"
        >
          <Redo2 className="w-4 h-4" />
        </button>

        <div className="h-4 w-px bg-white/10 mx-0.5" />

        <button
          type="button"
          onClick={() => zoomOut()}
          className="p-1 text-neutral-400 hover:text-white hover:bg-white/5 rounded-full transition-colors cursor-pointer"
          title="Зменшити масштаб (-)"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        {/* Zoom Selector Display */}
        <button
          type="button"
          onClick={() => fitView({ padding: 0.2, duration: 400 })}
          className="text-[11px] font-semibold text-neutral-300 hover:text-white px-1.5 py-0.5 rounded hover:bg-white/5 transition-colors font-mono cursor-pointer"
          title="Вмістити в екран (Fit View)"
        >
          {zoomPercent}%
        </button>

        <button
          type="button"
          onClick={() => zoomIn()}
          className="p-1 text-neutral-400 hover:text-white hover:bg-white/5 rounded-full transition-colors cursor-pointer"
          title="Збільшити масштаб (+)"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Help Circle Button */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setShowHelp(!showHelp)}
          className={`flex items-center justify-center p-2 rounded-full shadow-2xl backdrop-blur-2xl transition-all cursor-pointer ${
            showHelp
              ? 'bg-purple-600/30 text-purple-200 border border-purple-500/50'
              : 'bg-[#16181f]/95 border border-white/10 text-neutral-400 hover:text-white hover:bg-white/5'
          }`}
          title="Гарячі клавіші та довідка"
        >
          <HelpCircle className="w-4 h-4" />
        </button>

        {/* Shortcuts Popover */}
        {showHelp && (
          <div className="absolute bottom-full mb-3 left-0 w-64 p-3 rounded-xl bg-[#14151a]/95 backdrop-blur-xl border border-white/10 shadow-2xl text-xs space-y-2 text-neutral-300 z-50">
            <div className="flex items-center justify-between pb-1.5 border-b border-white/10 font-semibold text-white">
              <span>Гарячі клавіші Stitch</span>
              <button 
                type="button" 
                onClick={() => setShowHelp(false)}
                className="text-neutral-400 hover:text-white p-0.5 rounded hover:bg-white/5 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="space-y-1.5 text-[11px]">
              <div className="flex justify-between">
                <span className="text-neutral-400">Панорамування:</span>
                <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-white text-[10px]">Space + Drag</kbd>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Масштабування:</span>
                <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-white text-[10px]">Колесо / Pinch</kbd>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Скасувати дію:</span>
                <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-white text-[10px]">Cmd + Z</kbd>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Повторити дію:</span>
                <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-white text-[10px]">Cmd + Shift + Z</kbd>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Вмістити все:</span>
                <kbd className="px-1.5 py-0.5 rounded bg-white/10 font-mono text-white text-[10px]">Клік на %</kbd>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
