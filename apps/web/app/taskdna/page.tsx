// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_taskdna_page"
// purpose: "Unified TaskDNA Hub integrating Live HUD (Anti-Poisoning HITL), OpenMontage Shorts Studio & Legacy Dashboard"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.1.0"
// updated_at: "2026-09-14"
// author: "DNK-e.com Maksym & Gerych Builder"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState } from 'react';
import WorkspaceShell from '../../components/workspace/WorkspaceShell';
import TaskDNADashboard from '../../components/taskdna/TaskDNADashboard';
import TaskDNALiveHUD from '../../components/taskdna/TaskDNALiveHUD';
import ShortsKineticPlayer from '../../components/video/ShortsKineticPlayer';
import { Crown, Film, LayoutGrid } from 'lucide-react';

export default function TaskDNAPage() {
  const [workspaceId, setWorkspaceId] = useState<string>('ws-alpha-001');
  const [viewMode, setViewMode] = useState<'live-hud' | 'shorts-studio' | 'dashboard'>('live-hud');

  return (
    <WorkspaceShell
      currentWorkspaceId={workspaceId}
      onWorkspaceChange={setWorkspaceId}
      activeTab="taskdna"
    >
      <div className="flex flex-col h-full w-full bg-slate-950 overflow-y-auto">
        {/* Sub-navigation Tabs */}
        <div className="flex items-center space-x-2 px-6 pt-4 pb-2 border-b border-slate-800 bg-slate-950/80 sticky top-0 z-20 backdrop-blur-md">
          <button
            onClick={() => setViewMode('live-hud')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
              viewMode === 'live-hud'
                ? 'bg-purple-600/30 text-purple-300 border border-purple-500/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Crown className="w-3.5 h-3.5 text-purple-400" />
            <span>Swarm Live HUD (HITL)</span>
          </button>

          <button
            onClick={() => setViewMode('shorts-studio')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
              viewMode === 'shorts-studio'
                ? 'bg-cyan-600/30 text-cyan-300 border border-cyan-500/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Film className="w-3.5 h-3.5 text-cyan-400" />
            <span>Shorts Studio (OpenMontage)</span>
          </button>

          <button
            onClick={() => setViewMode('dashboard')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
              viewMode === 'dashboard'
                ? 'bg-slate-800 text-slate-200 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5 text-slate-400" />
            <span>Architecture & DoD Map</span>
          </button>
        </div>

        {/* View Content */}
        <div className="flex-1 w-full">
          {viewMode === 'live-hud' && <TaskDNALiveHUD />}
          {viewMode === 'shorts-studio' && <ShortsKineticPlayer />}
          {viewMode === 'dashboard' && <TaskDNADashboard workspaceId={workspaceId} />}
        </div>
      </div>
    </WorkspaceShell>
  );
}
