// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_workspace_agent_page"
// purpose: "Meta Astryx Agent-Native Master Cockpit: Living Node Canvas, Node-Scoped Chat, and Live Swarm HUD."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Terminal, 
  MessageSquare, 
  Sparkles, 
  Command, 
  X,
  Radio,
  Layers
} from 'lucide-react';
import { AgentStreamHUD } from '@/components/agent/AgentStreamHUD';
import MultiAgentSwarmCanvas from '@/components/canvas/MultiAgentSwarmCanvas';
import { OrchestratorChatPanel } from '@/components/canvas/OrchestratorChatPanel';

export default function AgentWorkspacePage() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'hud'>('chat');

  // Keyboard shortcuts: Cmd+J for Copilot, Cmd+L for HUD, Escape to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'j') {
        e.preventDefault();
        setActiveTab('chat');
        setIsDrawerOpen((prev) => !prev);
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        setActiveTab('hud');
        setIsDrawerOpen((prev) => !prev);
      }
      if (e.key === 'Escape' && isDrawerOpen) {
        setIsDrawerOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDrawerOpen]);

  const handleOpenTab = (tab: 'chat' | 'hud') => {
    if (isDrawerOpen && activeTab === tab) {
      setIsDrawerOpen(false);
    } else {
      setActiveTab(tab);
      setIsDrawerOpen(true);
    }
  };

  return (
    <div 
      className="flex flex-col h-screen w-screen overflow-hidden bg-[#090a0f] text-slate-100 font-sans"
      data-agent-target="agent-workspace-cockpit"
    >
      {/* Sleek Minimalist Studio Header (48px) */}
      <header className="h-12 border-b border-white/[0.08] bg-[#0c0e14]/90 backdrop-blur-2xl px-4 flex items-center justify-between z-20 select-none">
        {/* Brand & Breadcrumb */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-bold tracking-wider text-white">DNK OS</span>
          </div>
          <span className="text-zinc-600 text-xs">/</span>
          <span className="text-xs font-medium text-zinc-300">Sovereign Swarm Studio</span>
          <span className="text-zinc-600 text-xs hidden sm:inline">•</span>
          <span className="text-[11px] font-mono text-zinc-400 hidden sm:inline">
            4 Agents Mesh Active
          </span>
        </div>

        {/* Right Action Controls */}
        <div className="flex items-center gap-2">
          {/* Quick HUD button */}
          <button
            type="button"
            onClick={() => handleOpenTab('hud')}
            className={`px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 transition-all ${
              isDrawerOpen && activeTab === 'hud'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 shadow-sm'
                : 'bg-white/[0.03] hover:bg-white/[0.08] text-zinc-400 hover:text-white border border-white/[0.06]'
            }`}
            title="Terminal HUD (⌘L)"
          >
            <Terminal className="w-3.5 h-3.5 text-blue-400" />
            <span className="hidden md:inline">Terminal HUD</span>
          </button>

          {/* Quick Chat button */}
          <button
            type="button"
            onClick={() => handleOpenTab('chat')}
            className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 transition-all ${
              isDrawerOpen && activeTab === 'chat'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/20'
            }`}
            title="Copilot Chat (⌘J)"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Copilot Chat</span>
          </button>
        </div>
      </header>

      {/* Main Full-Bleed Canvas Workspace */}
      <div className="flex-1 w-full h-full relative overflow-hidden">
        {/* Full-bleed living canvas takes 100% space */}
        <MultiAgentSwarmCanvas />

        {/* Floating Quick Action Launcher (when drawer is closed) */}
        {!isDrawerOpen && (
          <div className="fixed bottom-5 right-5 z-20 flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleOpenTab('chat')}
              className="px-3.5 py-2 rounded-full bg-zinc-950/80 hover:bg-zinc-900 border border-white/10 text-xs font-medium text-white shadow-2xl backdrop-blur-xl flex items-center gap-2 transition-all hover:border-emerald-500/40 hover:scale-105 group"
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-400 group-hover:rotate-12 transition-transform" />
              <span>Copilot Chat</span>
              <kbd className="text-[10px] font-mono text-zinc-500 bg-white/5 px-1.5 py-0.5 rounded">⌘J</kbd>
            </button>

            <button
              type="button"
              onClick={() => handleOpenTab('hud')}
              className="p-2 rounded-full bg-zinc-950/80 hover:bg-zinc-900 border border-white/10 text-zinc-400 hover:text-white shadow-2xl backdrop-blur-xl transition-all hover:border-blue-500/40"
              title="Terminal HUD (⌘L)"
            >
              <Terminal className="w-4 h-4 text-blue-400" />
            </button>
          </div>
        )}

        {/* Floating Glassmorphism Slide-Over Drawer (non-destructive over canvas) */}
        {isDrawerOpen && (
          <aside className="fixed top-14 right-4 bottom-4 w-[480px] max-w-[calc(100vw-32px)] z-40 bg-zinc-950/90 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-[0_24px_72px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden animate-in fade-in slide-in-from-right duration-200">
            {/* Drawer Header with Seamless Tabs */}
            <div className="flex items-center justify-between border-b border-white/[0.08] bg-black/40 px-3.5 py-2.5">
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setActiveTab('chat')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'chat'
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm'
                      : 'text-zinc-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Copilot Chat</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('hud')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'hud'
                      ? 'bg-blue-500/15 text-blue-300 border border-blue-500/30 shadow-sm'
                      : 'text-zinc-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Terminal className="w-3.5 h-3.5 text-blue-400" />
                  <span>Terminal HUD</span>
                </button>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setIsDrawerOpen(false)}
                  className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors"
                  title="Закрити панель (Esc)"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Drawer Content */}
            <div className="flex-1 overflow-hidden relative">
              {activeTab === 'chat' && (
                <OrchestratorChatPanel isOpen={true} />
              )}
              {activeTab === 'hud' && (
                <AgentStreamHUD className="h-full rounded-none border-none shadow-none" />
              )}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}
