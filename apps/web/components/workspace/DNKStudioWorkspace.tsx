// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_workspace_DNKStudioWorkspace"
// purpose: "Pixel-perfect Google Stitch Canvas Workspace with full-bleed canvas, floating controls, and artboards."
// author: "DNK-e.com Maksym"
// status: "Active"
// version: "3.2.0"
// updated_at: "2026-09-03"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { Node } from '@xyflow/react';
import { HardDrive, Save, RefreshCw } from 'lucide-react';
import CanvasEngine from '../canvas/CanvasEngine';
import StitchTopNav from '../canvas/StitchTopNav';
import StitchSpatialToolbar from '../canvas/StitchSpatialToolbar';
import StitchPromptDock from '../canvas/StitchPromptDock';
import StitchCanvasControls from '../canvas/StitchCanvasControls';
import StitchGenerationStatusCard from '../canvas/StitchGenerationStatusCard';
import StitchAgentLog from '../canvas/StitchAgentLog';
import { useCanvasStore } from '../../store/canvasStore';
import { computeUpstreamFingerprint } from '../../src/canvas/context/context-builder';
import {
  StitchSwarmCommandCenter,
  StitchKineticTimeline,
  StitchSmartInspector,
  StitchShopifyPreviewDrawer,
  StitchBiAnalystDrawer,
  StitchTaskForestDrawer,
  StitchThoughtDagDrawer,
} from '../stitch';

// Initial Living ThoughtDAG Workflow replicating CONTRACT-002 Architecture
const INITIAL_LIVING_THOUGHTDAG_NODES: Node[] = [
  {
    id: 'note-living-arch',
    type: 'thoughtDagNote',
    position: { x: 120, y: 160 },
    data: {
      title: 'Architectural Specs & Living Context',
      content: '## DNK OS Architecture & Living Context\n\n- Zero-Waste High-Velocity Protocol v4.5\n- Swarm Concurrency: 8 active domain agents\n- CONTRACT-002 Context Wires enabled\n\nDrag wires from this note to any Swarm Agent to stream context.',
      highlightMode: 'all',
      isLiving: true,
      updatedAt: new Date().toISOString(),
    },
  },
  {
    id: 'agent-task-builder',
    type: 'agentTaskNode',
    position: { x: 600, y: 160 },
    data: {
      taskId: 'agent-task-builder',
      targetAgent: 'gerych_builder',
      title: 'Gerych Builder: UI & Swarm Sync',
      agent: 'gerych_builder',
      description: 'Implement living canvas components and verify context wire updates.',
      status: 'RUNNING',
      isStale: false,
      upstreamFingerprint: 'cdfadb23bec61f1a',
    },
  },
];

const INITIAL_LIVING_THOUGHTDAG_EDGES: any[] = [
  {
    id: 'wire-arch-to-builder',
    source: 'note-living-arch',
    target: 'agent-task-builder',
    type: 'context-wire',
    animated: true,
    data: {
      scope: 'all',
      isBlocked: false,
    },
  },
];

export default function DNKStudioWorkspace() {
  const [activeTool, setActiveTool] = useState<string>('select');
  const [showStatusCard, setShowStatusCard] = useState<boolean>(false);
  const [activeDrawer, setActiveDrawer] = useState<'swarm' | 'timeline' | 'inspector' | 'shopify' | 'bi' | 'forest' | 'thoughtdag' | null>(null);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'info' | 'warning' | 'error' } | null>(null);
  const [isPromptLoading, setIsPromptLoading] = useState<boolean>(false);

  const {
    nodes,
    setNodes,
    setEdges,
    addThoughtDagNote,
    addAgentTaskNode,
    connectContextWire,
    selectedNodeId,
    activeCanvasFile,
    availableCanvasFiles,
    isLocalSyncing,
    loadLocalCanvas,
    saveLocalCanvas,
    fetchLocalCanvasFiles,
    setActiveCanvasFile,
  } = useCanvasStore();
  const selectedElement = nodes.find((n) => n.id === selectedNodeId);

  const handleNotification = (msg: { text: string; type: 'success' | 'info' | 'warning' | 'error' }) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const toggleDrawer = (drawer: 'swarm' | 'timeline' | 'inspector' | 'shopify' | 'bi' | 'forest' | 'thoughtdag') => {
    setActiveDrawer((prev) => (prev === drawer ? null : drawer));
  };

  const handleSaveCanvas = async () => {
    const targetFile = activeCanvasFile || 'docs/canvas/projects/dnk_ecom/main.canvas';
    const res = await saveLocalCanvas(targetFile);
    if (res.status === 'success') {
      handleNotification({
        text: `💾 Збережено у ${targetFile}`,
        type: 'success',
      });
    } else {
      handleNotification({
        text: `Помилка збереження: ${res.message}`,
        type: 'error',
      });
    }
  };

  const handleSwitchCanvasFile = async (filePath: string) => {
    setActiveCanvasFile(filePath);
    const res = await loadLocalCanvas(filePath);
    if (res.status === 'success') {
      handleNotification({
        text: `📂 Завантажено ${res.nodes?.length ?? 0} нод із ${filePath}`,
        type: 'success',
      });
    } else {
      handleNotification({
        text: `Помилка завантаження ${filePath}: ${res.message}`,
        type: 'error',
      });
    }
  };

  // Keyboard shortcut listener for Cmd+S / Ctrl+S
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        handleSaveCanvas();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeCanvasFile, nodes, useCanvasStore]);

  // Initial mount: load local canvas or fallback to Living ThoughtDAG
  useEffect(() => {
    let isMounted = true;
    const initializeLocalWorkspace = async () => {
      await fetchLocalCanvasFiles();
      const target = activeCanvasFile || 'docs/canvas/projects/dnk_ecom/main.canvas';
      const res = await loadLocalCanvas(target);
      if (isMounted) {
        if (res.status === 'success' && res.nodes && res.nodes.length > 0) {
          handleNotification({
            text: `⚡ DEC-043 NodeCanvasCore: Завантажено ${res.nodes.length} нод із ${target}`,
            type: 'success',
          });
        } else {
          const currentNodes = useCanvasStore.getState().nodes;
          if (!currentNodes || currentNodes.length === 0) {
            setNodes(INITIAL_LIVING_THOUGHTDAG_NODES);
            setEdges(INITIAL_LIVING_THOUGHTDAG_EDGES);
          }
        }
      }
    };
    initializeLocalWorkspace();
    return () => {
      isMounted = false;
    };
  }, []);

  // Ensure downstream nodes without fingerprint are initialized for staleness reactivity
  useEffect(() => {
    if (nodes && nodes.length > 0) {
      const currentEdges = useCanvasStore.getState().edges;
      nodes.forEach((n) => {
        if (n.type === 'agentTaskNode' && !(n.data as any)?.upstreamFingerprint) {
          const fp = computeUpstreamFingerprint(n.id, nodes, currentEdges);
          if (fp) {
            useCanvasStore.getState().updateNodeData(n.id, { upstreamFingerprint: fp });
          }
        }
      });
    }
  }, [nodes]);

  const handleSubmitPromptDock = async (prompt: string) => {
    if (!prompt.trim() || isPromptLoading) return;
    setIsPromptLoading(true);
    handleNotification({
      text: `✨ Герич Prime аналізує: "${prompt.slice(0, 35)}..."`,
      type: 'info',
    });

    try {
      const res = await fetch('/api/v1/orchestrator/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Workspace-ID': 'ws-alpha-001',
        },
        body: JSON.stringify({
          message: prompt,
          session_id: 'stitch-dock',
          target_agent: 'gerych_prime',
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      let lastNoteId = '';
      let lastAgentId = '';

      if (data.canvas_actions && Array.isArray(data.canvas_actions)) {
        for (const action of data.canvas_actions) {
          if (action.action_type === 'add_note') {
            const p = action.payload || {};
            lastNoteId = addThoughtDagNote(
              p.x || 150 + Math.random() * 40,
              p.y || 200 + Math.random() * 40,
              p.content || '',
              { title: p.title || 'ThoughtDAG Living Note' }
            );
          } else if (action.action_type === 'add_agent_task') {
            const p = action.payload || {};
            lastAgentId = addAgentTaskNode(
              p.x || 600 + Math.random() * 40,
              p.y || 200 + Math.random() * 40,
              p
            );
          } else if (action.action_type === 'connect_wire') {
            const p = action.payload || {};
            const src = p.from_node || lastNoteId;
            const tgt = p.to_node || lastAgentId;
            if (src && tgt) {
              connectContextWire(src, tgt, p.scope || 'all');
            }
          }
        }
      }

      handleNotification({
        text: `✨ Герич Prime: ${data.reply?.slice(0, 50)}...`,
        type: 'success',
      });
    } catch (err: any) {
      handleNotification({
        text: `Помилка оркестратора: ${err.message || 'Не вдалося виконати запит'}`,
        type: 'error',
      });
    } finally {
      setIsPromptLoading(false);
      setShowStatusCard(false);
    }
  };

  return (
    <div className="flex flex-col w-screen h-screen overflow-hidden bg-[#0e1014] select-none text-white font-sans">
      {/* 1. Google Stitch Top Navigation Bar */}
      <StitchTopNav
        projectName="Custom Main Screen Redesign"
        onExport={() => alert('Exporting Google Stitch Canvas Artifacts...')}
        onShare={() => alert('Project share link copied to clipboard!')}
        onPlayPreview={() => alert('Opening Live Design Preview...')}
        onToggleSwarm={() => toggleDrawer('swarm')}
        onToggleTimeline={() => toggleDrawer('timeline')}
        onToggleShopify={() => toggleDrawer('shopify')}
        onToggleBi={() => toggleDrawer('bi')}
        onToggleForest={() => toggleDrawer('forest')}
        onToggleThoughtDag={() => toggleDrawer('thoughtdag')}
        onToggleInspector={() => toggleDrawer('inspector')}
        activeDrawer={activeDrawer}
      />

      {/* 2. Full-Bleed Infinite Canvas Workspace */}
      <div className="relative flex-1 w-full h-full overflow-hidden bg-[#0e1014]">
        {/* Full Interactive Canvas Surface with Contextual Drawer Bus */}
        <CanvasEngine onOpenDrawer={(drawer) => setActiveDrawer(drawer)} />

        {/* DEC-043 NodeCanvasCore Offline Control Bar */}
        <div className="absolute top-18 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#161921]/90 backdrop-blur-xl border border-white/10 shadow-2xl text-xs font-mono pointer-events-auto">
          <div className="flex items-center gap-1.5 text-slate-300">
            <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-[11px] text-slate-400 font-medium hidden sm:inline">DEC-043:</span>
          </div>

          <div className="relative flex items-center">
            <select
              value={activeCanvasFile}
              onChange={(e) => handleSwitchCanvasFile(e.target.value)}
              className="bg-black/40 border border-white/10 rounded-lg px-2 py-0.5 text-[11px] text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer max-w-[260px] truncate"
              title="Обрати файл полотна .canvas"
            >
              {availableCanvasFiles.map((file) => (
                <option key={file} value={file} className="bg-[#161921] text-slate-200">
                  {file.replace('docs/canvas/projects/', '🚀 ').replace('docs/canvas/', '🌌 ').replace('docs/diagrams/', '📊 ').replace('docs/architecture/diagrams/', '📐 ')}
                </option>
              ))}
            </select>
          </div>

          <div className="h-3 w-[1px] bg-white/10" />

          <button
            onClick={() => handleSwitchCanvasFile(activeCanvasFile)}
            disabled={isLocalSyncing}
            className="flex items-center gap-1 px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-colors text-[11px] disabled:opacity-50 cursor-pointer"
            title="Оновити з диска"
          >
            <RefreshCw className={`w-3 h-3 ${isLocalSyncing ? 'animate-spin text-indigo-400' : ''}`} />
            <span className="hidden sm:inline">Оновити</span>
          </button>

          <button
            onClick={handleSaveCanvas}
            disabled={isLocalSyncing}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white font-medium transition-colors text-[11px] shadow-sm shadow-indigo-500/20 disabled:opacity-50 cursor-pointer"
            title="Зберегти на диск (Cmd+S / Ctrl+S)"
          >
            <Save className="w-3 h-3" />
            <span>Зберегти</span>
          </button>

          <div className="flex items-center gap-1 pl-1">
            <span className={`w-1.5 h-1.5 rounded-full ${isLocalSyncing ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`} />
            <span className="text-[10px] text-slate-400 hidden md:inline">
              {isLocalSyncing ? 'Запис...' : 'Офлайн'}
            </span>
          </div>
        </div>

        {/* 3. Top-Left: Google Stitch AI Generation Status Card */}
        {showStatusCard && (
          <StitchGenerationStatusCard
            userPrompt="прибери останній к..."
            errorMessage="Something unexpected happened, and Stitch couldn't complete your generation. Please try again in a moment."
            onRetry={() => {
              console.log('Retrying generation in Stitch Canvas...');
            }}
          />
        )}

        {/* 4. Bottom-Left: Google Stitch Agent Log Pill Widget */}
        <div className="absolute bottom-6 left-6 z-30">
          <StitchAgentLog />
        </div>

        {/* 5. Left/Floating: Google Stitch Spatial Toolbar */}
        <StitchSpatialToolbar
          activeTool={activeTool}
          onSelectTool={(tool) => {
            setActiveTool(tool);
          }}
        />

        {/* 6. Center Bottom: Google Stitch Prompt Command Dock (deprecated in favor of CapCut OrchestratorChatPanel) */}
        {/* Chat and commands are handled cleanly via the right CapCut AI Cockpit */}

        {/* 7. Canvas controls (Undo, Redo, Zoom %, Help) are now mounted inside CanvasEngine within ReactFlowProvider */}

        {/* 8. Floating Toast Notification Banner */}
        {toastMessage && (
          <div className="absolute top-20 right-6 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-xl border backdrop-blur-xl shadow-2xl transition-all animate-in fade-in slide-in-from-top-2 bg-[#161921]/95 border-emerald-500/40 text-emerald-300 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{toastMessage.text}</span>
          </div>
        )}

        {/* 9. Interactive Spatial Drawers */}
        <StitchSwarmCommandCenter
          isOpen={activeDrawer === 'swarm'}
          onClose={() => setActiveDrawer(null)}
          onNotification={handleNotification}
        />

        {activeDrawer === 'timeline' && (
          <div className="absolute bottom-24 left-6 right-6 z-40">
            <StitchKineticTimeline
              onNotification={handleNotification}
            />
          </div>
        )}

        {activeDrawer === 'inspector' && (
          <div className="absolute top-20 right-6 z-40 w-96">
            <StitchSmartInspector
              selectedElement={selectedElement}
              onClose={() => setActiveDrawer(null)}
              onNotification={handleNotification}
            />
          </div>
        )}

        {activeDrawer === 'shopify' && (
          <StitchShopifyPreviewDrawer
            onClose={() => setActiveDrawer(null)}
            onNotification={handleNotification}
          />
        )}

        {activeDrawer === 'bi' && (
          <StitchBiAnalystDrawer
            onClose={() => setActiveDrawer(null)}
            onNotification={handleNotification}
          />
        )}

        {activeDrawer === 'forest' && (
          <StitchTaskForestDrawer
            onClose={() => setActiveDrawer(null)}
            onNotification={handleNotification}
          />
        )}

        {activeDrawer === 'thoughtdag' && (
          <StitchThoughtDagDrawer
            isOpen={true}
            onClose={() => setActiveDrawer(null)}
            onNotification={handleNotification}
          />
        )}
      </div>
    </div>
  );
}

export { DNKStudioWorkspace };
