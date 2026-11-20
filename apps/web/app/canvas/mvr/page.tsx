// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_canvas_mvr_page"
// purpose: "Interactive Living Swarm Playground & Spatial Cockpit for MVR Core with real-time SSE & 1-Click HITL"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useMvrCanvasStore } from '../../../store/mvrCanvasStore';
import { AgentTaskNode } from '../../../components/canvas/AgentTaskNode';
import { HitlApprovalDrawer } from '../../../components/canvas/HitlApprovalDrawer';
import {
  useMvrStream,
  launchSwarmSimulation,
  abortSwarmSimulation,
} from '../../../lib/api/mvr_stream_client';
import {
  Play,
  Zap,
  Trash2,
  Activity,
  ShieldCheck,
  Sparkles,
  Square,
} from 'lucide-react';

export default function MvrLivingSwarmCanvasPage() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    handleStreamEnvelope,
    setStreamConnected,
    resetGraph,
    pendingApprovals,
    activeSimulationId,
    isSimulationRunning,
    setSimulationRunning,
  } = useMvrCanvasStore();

  const [isLaunching, setIsLaunching] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [simulationStatus, setSimulationStatus] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Auto-open drawer when approvals arrive
  useEffect(() => {
    if (pendingApprovals.length > 0) {
      setIsDrawerOpen(true);
    }
  }, [pendingApprovals.length]);

  // Custom node mapping
  const nodeTypes = useMemo(
    () => ({
      agentTask: AgentTaskNode,
    }),
    []
  );

  // Connect live SSE stream and pipe directly into Zustand store
  const { connected } = useMvrStream({
    onConnect: () => setStreamConnected(true),
    onDisconnect: () => setStreamConnected(false),
    onEvent: (envelope) => {
      handleStreamEnvelope(envelope);
      if (envelope.event_type === 'SIMULATION_COMPLETED') {
        setSimulationStatus('🎉 Simulation Completed Successfully!');
        setIsLaunching(false);
      } else if (envelope.event_type === 'SIMULATION_ABORTED') {
        setSimulationStatus('❌ Simulation Aborted / Rejected');
        setIsLaunching(false);
      }
    },
  });

  const handleLaunch = useCallback(
    async (scenario: 'PRODUCT_LAUNCH' | 'SECURITY_AUDIT', headless = false) => {
      setIsLaunching(true);
      setActiveScenario(scenario);
      setSimulationStatus('Initializing Swarm Nodes...');
      try {
        const res = await launchSwarmSimulation({
          scenario,
          canvas_id: 'canvas-main',
          target_audience: 'Founders & E-Commerce Merchants',
          step_delay_seconds: headless ? 0.05 : 0.6,
          auto_approve_after_seconds: headless ? 0.2 : undefined,
        });
        if (res?.simulation_id) {
          setSimulationRunning(true, res.simulation_id);
        }
        setSimulationStatus('Swarm Executing on Canvas...');
      } catch (err: any) {
        setSimulationStatus(`Launch Failed: ${err.message}`);
        setIsLaunching(false);
        setSimulationRunning(false, null);
      }
    },
    [setSimulationRunning]
  );

  const handleAbort = useCallback(async () => {
    if (!activeSimulationId) return;
    setSimulationStatus('Aborting Swarm Simulation...');
    try {
      await abortSwarmSimulation(activeSimulationId);
      setSimulationStatus('Simulation Aborted by Operator');
      setSimulationRunning(false, null);
      setIsLaunching(false);
    } catch (err: any) {
      setSimulationStatus(`Abort Failed: ${err.message}`);
    }
  }, [activeSimulationId, setSimulationRunning]);

  return (
    <div className="relative w-screen h-screen bg-[#07090E] text-slate-100 overflow-hidden font-sans select-none">
      {/* Top Cockpit Header */}
      <header className="absolute top-0 left-0 right-0 z-30 h-16 bg-[#0B0F19]/90 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-white text-base">
                DNK Swarm Cockpit
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono tracking-wider font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                PHASE 7 LIVE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              MVR Real-Time Reactive Swarm Playground
            </p>
          </div>
        </div>

        {/* Status Center */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                connected
                  ? 'bg-emerald-500 animate-pulse shadow-sm shadow-emerald-500/50'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-slate-300 font-mono">
              {connected ? 'SSE STREAM ACTIVE' : 'RECONNECTING...'}
            </span>
          </div>

          {simulationStatus && (
            <div className="px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-xs text-indigo-300 font-mono">
              {simulationStatus}
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleLaunch('PRODUCT_LAUNCH', false)}
            disabled={isLaunching}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 active:scale-95 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            Launch Interactive Swarm
          </button>

          <button
            onClick={() => handleLaunch('PRODUCT_LAUNCH', true)}
            disabled={isLaunching}
            title="Fast headless simulation with automated HITL approval"
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 text-xs font-medium border border-slate-700 transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            Fast Auto
          </button>

          {isSimulationRunning && activeSimulationId && (
            <button
              onClick={handleAbort}
              title="Abort running simulation immediately"
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-600/90 hover:bg-rose-500 active:scale-95 text-white text-xs font-semibold shadow-md shadow-rose-600/30 transition-all"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              Abort
            </button>
          )}

          <button
            onClick={resetGraph}
            title="Clear canvas graph"
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-rose-950/40 hover:text-rose-400 border border-slate-700/80 text-slate-400 transition-all"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Spatial Working Canvas */}
      <div className="w-full h-full pt-16">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          colorMode="dark"
          defaultEdgeOptions={{
            animated: true,
            style: { stroke: '#6366F1', strokeWidth: 2 },
          }}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={24}
            size={1.5}
            color="#1E293B"
          />
          <Controls className="bg-slate-900 border border-slate-800 rounded-xl fill-slate-300 text-slate-300" />
          <MiniMap
            nodeStrokeColor="#38BDF8"
            nodeColor="#1E293B"
            maskColor="rgba(7, 9, 14, 0.7)"
            className="bg-slate-950/80 border border-slate-800 rounded-xl"
          />
        </ReactFlow>
      </div>

      {/* Floating HITL Indicator (if pending) */}
      {pendingApprovals.length > 0 && !isDrawerOpen && (
        <button
          onClick={() => setIsDrawerOpen(true)}
          className="absolute bottom-6 left-6 z-40 flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-amber-950/80 border border-amber-500/40 shadow-2xl shadow-amber-950/50 backdrop-blur-md animate-bounce hover:bg-amber-900/80 transition-all text-left"
        >
          <ShieldCheck className="w-5 h-5 text-amber-400" />
          <div className="text-xs">
            <span className="font-bold text-amber-200">
              {pendingApprovals.length} Gate Action(s) Waiting
            </span>
            <p className="text-amber-400/80 text-[11px]">
              Click to open Approval Drawer
            </p>
          </div>
        </button>
      )}

      {/* Slide-over HITL Approval Drawer */}
      <HitlApprovalDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
}
