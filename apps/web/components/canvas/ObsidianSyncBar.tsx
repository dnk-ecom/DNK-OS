// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_ObsidianSyncBar"
// purpose: "Obsidian Vault & JSON Canvas Two-Way Sync Bar with Conflict Resolution & Status Indicator"
// author: "DNK-e.com Maksym"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-04"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useCanvasStore } from '../../store/canvasStore';
import { 
  FileText, 
  RefreshCw, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Settings2, 
  CheckCircle2, 
  AlertCircle,
  FolderSync,
  X,
  ChevronDown
} from 'lucide-react';

interface ObsidianSyncBarProps {
  defaultVaultPath?: string;
  defaultCanvasName?: string;
  className?: string;
}

export const ObsidianSyncBar: React.FC<ObsidianSyncBarProps> = ({
  defaultVaultPath = './docs/notes',
  defaultCanvasName,
  className = ''
}) => {
  const { 
    obsidianSyncStatus, 
    obsidianSyncMessage, 
    syncToObsidian, 
    canvasId,
    nodes,
    edges 
  } = useCanvasStore();

  const [vaultPath, setVaultPath] = useState(defaultVaultPath);
  const [canvasName, setCanvasName] = useState(defaultCanvasName || `canvas_${canvasId}`);
  const [conflictStrategy, setConflictStrategy] = useState<'last-write-wins' | 'merge-tags'>('last-write-wins');
  const [showSettings, setShowSettings] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Sync canvas name when canvasId changes
  useEffect(() => {
    if (!defaultCanvasName) {
      setCanvasName(`canvas_${canvasId}`);
    }
  }, [canvasId, defaultCanvasName]);

  // Handle toast notifications on sync status updates
  useEffect(() => {
    if (obsidianSyncStatus === 'success' || obsidianSyncStatus === 'error') {
      setToastMessage(obsidianSyncMessage || (obsidianSyncStatus === 'success' ? 'Sync completed' : 'Sync failed'));
      const timer = setTimeout(() => {
        setToastMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [obsidianSyncStatus, obsidianSyncMessage]);

  const handleExport = async () => {
    await syncToObsidian('export', {
      vaultPath,
      canvasName,
      conflictStrategy
    });
  };

  const handleImport = async () => {
    await syncToObsidian('import', {
      vaultPath,
      canvasName,
      conflictStrategy
    });
  };

  const handleTwoWaySync = async () => {
    await syncToObsidian('sync', {
      vaultPath,
      canvasName,
      conflictStrategy
    });
  };

  const isSyncing = obsidianSyncStatus === 'syncing';

  return (
    <div className={`relative z-20 flex flex-col items-center select-none ${className}`}>
      {/* Toast Alert Banner */}
      {toastMessage && (
        <div
          className={`absolute top-full mt-2 left-0 right-0 z-50 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 shadow-lg backdrop-blur-md transition-all duration-300 border ${
            obsidianSyncStatus === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200'
              : 'bg-rose-950/90 border-rose-500/40 text-rose-200'
          }`}
        >
          {obsidianSyncStatus === 'success' ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
          )}
          <span className="truncate flex-1">{toastMessage}</span>
          <button
            type="button"
            onClick={() => setToastMessage(null)}
            className="text-neutral-400 hover:text-white"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Compact Obsidian Sync Trigger Pill */}
      <button
        type="button"
        onClick={() => setShowSettings(!showSettings)}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#14151a]/90 hover:bg-[#1c1d25] border border-purple-500/30 hover:border-purple-500/50 text-xs text-neutral-200 transition-all shadow-sm cursor-pointer shrink-0"
        title="Obsidian Vault Sync & Controls"
      >
        <FolderSync className={`w-3.5 h-3.5 text-purple-400 shrink-0 ${isSyncing ? 'animate-spin' : ''}`} />
        <span className="font-semibold text-white tracking-wide hidden sm:inline">Obsidian</span>
        <span className="text-[10px] px-1.5 py-0.2 bg-purple-500/20 text-purple-300 rounded font-mono">
          {nodes.length}n • {edges.length}e
        </span>
        <ChevronDown className={`w-3 h-3 text-neutral-400 transition-transform ${showSettings ? 'rotate-180' : ''}`} />
      </button>

      {/* Expandable Settings & Actions Flyout Popover */}
      {showSettings && (
        <div className="absolute top-full mt-2 left-0 w-80 p-3.5 rounded-xl bg-[#14151a]/95 backdrop-blur-xl border border-purple-500/30 shadow-2xl text-xs space-y-3.5 z-50">
          <div className="flex items-center justify-between pb-2 border-b border-[#262835]">
            <span className="font-semibold text-white flex items-center gap-1.5 text-xs">
              <FolderSync className="w-4 h-4 text-purple-400" />
              Obsidian Vault Sync
              <span className="text-[10px] px-1.5 py-0.2 bg-purple-500/20 text-purple-300 rounded">v1.0</span>
            </span>
            <button
              type="button"
              onClick={() => setShowSettings(false)}
              className="text-neutral-400 hover:text-white p-0.5 rounded hover:bg-white/5 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Stats Bar */}
          <div className="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-[#1c1d25] border border-white/5 text-neutral-400 text-[11px]">
            <span>Полотно: <strong className="text-white font-mono">{nodes.length}</strong> нод, <strong className="text-white font-mono">{edges.length}</strong> зв'язків</span>
            {isSyncing && <span className="text-purple-400 font-medium animate-pulse">Синхронізація...</span>}
          </div>

          {/* Action Buttons Row */}
          <div className="grid grid-cols-3 gap-1.5">
            <button
              type="button"
              disabled={isSyncing}
              onClick={handleExport}
              title="Export living canvas to Markdown notes and .canvas in Obsidian Vault"
              className="flex flex-col items-center justify-center gap-1 p-2 rounded-lg bg-[#20222e] hover:bg-[#2b2e3d] active:scale-95 disabled:opacity-50 text-neutral-200 hover:text-white transition-all font-medium border border-neutral-700/50 cursor-pointer"
            >
              <ArrowUpRight className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-[11px]">Export</span>
            </button>

            <button
              type="button"
              disabled={isSyncing}
              onClick={handleImport}
              title="Import Markdown notes and .canvas from Obsidian Vault"
              className="flex flex-col items-center justify-center gap-1 p-2 rounded-lg bg-[#20222e] hover:bg-[#2b2e3d] active:scale-95 disabled:opacity-50 text-neutral-200 hover:text-white transition-all font-medium border border-neutral-700/50 cursor-pointer"
            >
              <ArrowDownLeft className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px]">Import</span>
            </button>

            <button
              type="button"
              disabled={isSyncing}
              onClick={handleTwoWaySync}
              title="Two-way bidirectional synchronization with conflict resolution"
              className="flex flex-col items-center justify-center gap-1 p-2 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-200 active:scale-95 disabled:opacity-50 transition-all font-medium border border-purple-500/40 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-purple-400 ${isSyncing ? 'animate-spin' : ''}`} />
              <span className="text-[11px]">{isSyncing ? 'Syncing...' : 'Sync'}</span>
            </button>
          </div>

          <div className="pt-2 border-t border-[#262835] space-y-2.5">
            <div className="space-y-1">
              <label className="text-[11px] text-neutral-400 font-medium">Vault Target Directory</label>
              <input
                type="text"
                value={vaultPath}
                onChange={(e) => setVaultPath(e.target.value)}
                placeholder="./docs/notes"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#1b1c24] border border-[#2f3140] text-neutral-200 text-[11px] focus:outline-none focus:border-purple-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[11px] text-neutral-400 font-medium">Canvas File Name</label>
              <input
                type="text"
                value={canvasName}
                onChange={(e) => setCanvasName(e.target.value)}
                placeholder="canvas_default"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#1b1c24] border border-[#2f3140] text-neutral-200 text-[11px] focus:outline-none focus:border-purple-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[11px] text-neutral-400 font-medium">Conflict Resolution</label>
              <select
                value={conflictStrategy}
                onChange={(e) => setConflictStrategy(e.target.value as any)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[#1b1c24] border border-[#2f3140] text-neutral-200 text-[11px] focus:outline-none focus:border-purple-500"
              >
                <option value="last-write-wins">Last Write Wins (Timestamp based)</option>
                <option value="merge-tags">Merge Tags & Preserve Structure</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ObsidianSyncBar;
