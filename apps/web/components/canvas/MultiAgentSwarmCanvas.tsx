// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/MultiAgentSwarmCanvas.tsx"
// purpose: "Assimilated Multi-Agent Swarm Canvas powered by @xyflow/react with live step logs, active node indicator, and MCP management."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym & Gerych"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Play,
  RotateCcw,
  Server,
  Layers,
  Sparkles,
  Bot,
  Loader2,
  CheckCircle2,
  Plus,
  Compass,
  ChevronRight,
  ChevronLeft,
  X,
  RefreshCw,
} from 'lucide-react';
import { MultiAgentSwarmNode } from './nodes/MultiAgentSwarmNode';
import { AgentTaskNode } from './AgentTaskNode';
import { MacroClusterNode, type MacroClusterNodeData } from './MacroClusterNode';
import { MCPConfigModal } from './modals/MCPConfigModal';
import type { MultiAgentSwarmNodeData, MCPServerConfig } from '@/types/mcp';

export const WORKHORSE_CLUSTER_NODES: Node<any>[] = [
  {
    id: 'cluster-shopify',
    type: 'macroCluster',
    position: { x: 80, y: 60 },
    data: {
      hubId: 'shopify',
      title: 'Shopify Apex Hub',
      subtitle: '98+ SaaP Blocks, Liquid 2.0 Engine, Cart Rewards, Sticky ATC, Upsells & Dynamic PDP.',
      versionBadge: 'Pillar 1 • Apex',
      progressPercent: 100,
      totalTasks: 24,
      completedTasks: 24,
      metricLabel: 'CRO Uplift',
      metricValue: '+18.4% CVR',
    },
  },
  {
    id: 'cluster-media',
    type: 'macroCluster',
    position: { x: 500, y: 60 },
    data: {
      hubId: 'media',
      title: 'Media Studio Hub',
      subtitle: 'HyperFrames 60FPS Video Engine, Dynamic Remotion Scenes, Viral Hooks & Audio Beat Matching.',
      versionBadge: 'Pillar 2 • Media',
      progressPercent: 100,
      totalTasks: 18,
      completedTasks: 18,
      metricLabel: 'Render Speed',
      metricValue: '60 FPS WebGL',
    },
  },
  {
    id: 'cluster-distribution',
    type: 'macroCluster',
    position: { x: 80, y: 380 },
    data: {
      hubId: 'distribution',
      title: 'Growth & Distribution Hub',
      subtitle: 'Omnichannel Viral Syndication (TikTok, IG, X, Shorts), DTC Unit Economics & AOV Tracker.',
      versionBadge: 'Pillar 3 • Growth',
      progressPercent: 100,
      totalTasks: 12,
      completedTasks: 12,
      metricLabel: 'ROAS Target',
      metricValue: '4.2x Target',
    },
  },
  {
    id: 'cluster-core',
    type: 'macroCluster',
    position: { x: 500, y: 380 },
    data: {
      hubId: 'core',
      title: 'Microkernel Host & Memory',
      subtitle: 'FastMCP In-Memory Execution, TaskDNA Evolutionary DAG, SCONES Cognitive Reflexions & RLM Compactor.',
      versionBadge: 'Pillar 4 • Host',
      progressPercent: 100,
      totalTasks: 35,
      completedTasks: 35,
      metricLabel: 'Narrow Waist Latency',
      metricValue: '< 12ms p99',
    },
  },
];

export const WORKHORSE_CLUSTER_EDGES: Edge[] = [
  {
    id: 'edge-core-shopify',
    source: 'cluster-core',
    sourceHandle: 'top',
    target: 'cluster-shopify',
    targetHandle: 'bottom',
    animated: true,
    style: { stroke: '#10b981', strokeWidth: 1.5, opacity: 0.8 },
  },
  {
    id: 'edge-core-media',
    source: 'cluster-core',
    sourceHandle: 'top',
    target: 'cluster-media',
    targetHandle: 'bottom',
    animated: true,
    style: { stroke: '#f43f5e', strokeWidth: 1.5, opacity: 0.8 },
  },
  {
    id: 'edge-shopify-distribution',
    source: 'cluster-shopify',
    sourceHandle: 'bottom',
    target: 'cluster-distribution',
    targetHandle: 'top',
    animated: true,
    style: { stroke: '#10b981', strokeWidth: 1.5, opacity: 0.6 },
  },
  {
    id: 'edge-core-distribution',
    source: 'cluster-core',
    sourceHandle: 'left',
    target: 'cluster-distribution',
    targetHandle: 'right',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 1.5, opacity: 0.8 },
  },
  {
    id: 'edge-media-shopify',
    source: 'cluster-media',
    sourceHandle: 'left',
    target: 'cluster-shopify',
    targetHandle: 'right',
    animated: true,
    style: { stroke: '#8b5cf6', strokeWidth: 1.5, strokeDasharray: '4,4', opacity: 0.6 },
  },
];

const INITIAL_NODES: Node<MultiAgentSwarmNodeData>[] = [
  {
    id: 'agent-prime',
    type: 'multiAgentSwarmNode',
    position: { x: 50, y: 150 },
    data: {
      id: 'agent-prime',
      agentRole: 'gerych_prime',
      agentName: 'Gerych Prime',
      status: 'idle',
      taskGoal: 'Step 0 Autonomous Triage, TaskDNA DAG Decomposition & Swarm Orchestration',
      logs: [
        { id: '1', message: 'TaskDNA DAG initialized', done: true, timestamp: Date.now() - 5000 },
        { id: '2', message: 'Triage classifier: SWARM_PARALLEL mode chosen', done: true, timestamp: Date.now() - 4000 },
      ],
      response: 'Decomposed into 3 parallel execution streams with strict whitelists.',
      metrics: { tokensUsed: 1420, durationMs: 850 },
    },
  },
  {
    id: 'agent-researcher',
    type: 'multiAgentSwarmNode',
    position: { x: 450, y: 40 },
    data: {
      id: 'agent-researcher',
      agentRole: 'gerych_researcher',
      agentName: 'Gerych Researcher',
      status: 'idle',
      taskGoal: 'SOTA Repository Assimilation & AST Pattern Extraction from GitHub',
      logs: [
        { id: '1', message: 'License audit: MIT permissive verified', done: true, timestamp: Date.now() - 3000 },
        { id: '2', message: 'AST parsing of MCP & Canvas nodes completed', done: true, timestamp: Date.now() - 2000 },
      ],
      response: 'Extracted Stdio/SSE transport contracts and multi-agent step logs.',
      mcpServers: {
        github_tools: { transport: 'stdio', command: 'gh', args: ['mcp', 'serve'] },
      },
      metrics: { tokensUsed: 3100, durationMs: 1450 },
    },
  },
  {
    id: 'agent-builder',
    type: 'multiAgentSwarmNode',
    position: { x: 450, y: 280 },
    data: {
      id: 'agent-builder',
      agentRole: 'gerych_builder',
      agentName: 'Gerych Builder',
      status: 'idle',
      taskGoal: 'Synthesis of Dark Teal @xyflow/react Swarm Node & MCP Config Modal',
      logs: [
        { id: '1', message: 'MRH headers and TypeScript interfaces created', done: true, timestamp: Date.now() - 1500 },
        { id: '2', message: 'Synthesized MultiAgentSwarmNode with live active pulse', done: true, timestamp: Date.now() - 500 },
      ],
      response: 'Component tree rendered with zero dependencies on Copilot Cloud.',
      metrics: { tokensUsed: 2800, durationMs: 1100 },
    },
  },
  {
    id: 'agent-auditor',
    type: 'multiAgentSwarmNode',
    position: { x: 850, y: 150 },
    data: {
      id: 'agent-auditor',
      agentRole: 'gerych_auditor',
      agentName: 'Gerych Auditor',
      status: 'idle',
      taskGoal: 'Adversarial Security Review Gate, Anti-Tautology AST & Typecheck',
      logs: [
        { id: '1', message: 'Security check: No external cloud telemetry leaks detected', done: true, timestamp: Date.now() - 200 },
      ],
      response: 'Master Quality Gate: 100% Green. Ready for git commit.',
      metrics: { tokensUsed: 950, durationMs: 420 },
    },
  },
];

const INITIAL_EDGES: Edge[] = [
  {
    id: 'edge-prime-researcher',
    source: 'agent-prime',
    target: 'agent-researcher',
    animated: true,
    style: { stroke: '#2a6368', strokeWidth: 2 },
  },
  {
    id: 'edge-prime-builder',
    source: 'agent-prime',
    target: 'agent-builder',
    animated: true,
    style: { stroke: '#2a6368', strokeWidth: 2 },
  },
  {
    id: 'edge-researcher-auditor',
    source: 'agent-researcher',
    target: 'agent-auditor',
    animated: true,
    style: { stroke: '#2a6368', strokeWidth: 2 },
  },
  {
    id: 'edge-builder-auditor',
    source: 'agent-builder',
    target: 'agent-auditor',
    animated: true,
    style: { stroke: '#2a6368', strokeWidth: 2 },
  },
];

const COMMUNITY_MAP: Record<string, string> = {
  'agent-prime': 'Orchestration',
  'agent-researcher': 'Knowledge & AST',
  'agent-builder': 'Synthesis & UI',
  'agent-auditor': 'Adversarial Gate',
};

const GUIDED_TOUR_STEPS = [
  {
    step: 1,
    agentId: 'agent-prime',
    title: 'Gerych Prime — Orchestration Community',
    role: 'gerych_prime',
    description:
      'Step 0 Autonomous Complexity Classifier & TaskDNA Decomposition. Evaluates blast radius, selects SOLO vs SWARM mode, and schedules atomic slices.',
  },
  {
    step: 2,
    agentId: 'agent-researcher',
    title: 'Gerych Researcher — Knowledge & AST Community',
    role: 'gerych_researcher',
    description:
      'Extracts AST signatures, deep patterns, and license compliance audits from SOTA repositories. Connects with SCONES cognitive memory.',
  },
  {
    step: 3,
    agentId: 'agent-builder',
    title: 'Gerych Builder — Synthesis & Code Community',
    role: 'gerych_builder',
    description:
      'One-shot high-fidelity code and UI component synthesis. Implements modular TypeScript/React and Tailwind architectures without iterative churn.',
  },
  {
    step: 4,
    agentId: 'agent-auditor',
    title: 'Gerych Auditor — Adversarial Review Gate',
    role: 'gerych_auditor',
    description:
      'Red-team adversary enforcing Anti-Tautology AST, deterministic test pass, and Master Quality Gate (100% Green) before git commits.',
  },
];

export function MultiAgentSwarmCanvas() {
  const nodeTypes = useMemo(() => ({
    multiAgentSwarmNode: MultiAgentSwarmNode,
    agentTask: AgentTaskNode,
    macroCluster: MacroClusterNode,
  }), []);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node<any>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [viewMode, setViewMode] = useState<'clusters' | 'swarm' | 'taskboard'>('clusters');
  const [selectedHubFilter, setSelectedHubFilter] = useState<string | null>(null);
  const [isMCPModalOpen, setIsMCPModalOpen] = useState(false);
  const [isClusteringEnabled, setIsClusteringEnabled] = useState(false);
  const [isTaskboardMode, setIsTaskboardMode] = useState(false);
  const [isSyncingTaskboard, setIsSyncingTaskboard] = useState(false);
  const [activeTourStep, setActiveTourStep] = useState<number | null>(null);
  const [activeRunningAgent, setActiveRunningAgent] = useState<{
    name: string;
    nodeName: string;
  } | null>(null);

  const handleSyncTaskboard = useCallback(async (hubFilter?: string | null) => {
    setIsSyncingTaskboard(true);
    try {
      const res = await fetch('/api/v1/taskboard/canvas');
      if (res.ok) {
        const data = await res.json();
        if (data.nodes && data.nodes.length > 0) {
          let filteredNodes = data.nodes;
          if (hubFilter) {
            filteredNodes = data.nodes.filter((n: any) => {
              const text = `${n.data?.title || ''} ${n.data?.description || ''} ${n.data?.scope || ''}`.toLowerCase();
              if (hubFilter === 'shopify') {
                return text.includes('shopify') || text.includes('liquid') || text.includes('theme') || text.includes('cart') || text.includes('store') || text.includes('atc');
              }
              if (hubFilter === 'media') {
                return text.includes('media') || text.includes('video') || text.includes('hyperframes') || text.includes('remotion') || text.includes('audio');
              }
              if (hubFilter === 'distribution') {
                return text.includes('distribution') || text.includes('growth') || text.includes('social') || text.includes('analytics') || text.includes('aov') || text.includes('cvr');
              }
              if (hubFilter === 'core') {
                return text.includes('core') || text.includes('kernel') || text.includes('taskdna') || text.includes('scones') || text.includes('rlm') || text.includes('mcp');
              }
              return true;
            });
            if (filteredNodes.length === 0) {
              filteredNodes = data.nodes;
            }
          }
          setNodes(filteredNodes);
          const nodeIds = new Set(filteredNodes.map((n: any) => n.id));
          const filteredEdges = (data.edges || []).filter((e: any) => nodeIds.has(e.source) && nodeIds.has(e.target));
          setEdges(filteredEdges);
          setIsTaskboardMode(true);
          setViewMode('taskboard');
        }
      }
    } catch (err) {
      console.error('Failed to sync canvas with taskboard:', err);
    } finally {
      setIsSyncingTaskboard(false);
    }
  }, [setNodes, setEdges]);

  const handleDrilldownCluster = useCallback((hubId: string) => {
    setSelectedHubFilter(hubId);
    handleSyncTaskboard(hubId);
  }, [handleSyncTaskboard]);

  const handleSwitchViewMode = useCallback((mode: 'clusters' | 'swarm' | 'taskboard') => {
    setViewMode(mode);
    if (mode === 'clusters') {
      setSelectedHubFilter(null);
      setIsTaskboardMode(false);
      setNodes(
        WORKHORSE_CLUSTER_NODES.map((node) => ({
          ...node,
          data: {
            ...node.data,
            onToggleExpand: (hubId: string) => handleDrilldownCluster(hubId),
            onActionClick: (hubId: string) => handleDrilldownCluster(hubId),
          },
        }))
      );
      setEdges(WORKHORSE_CLUSTER_EDGES);
    } else if (mode === 'swarm') {
      setSelectedHubFilter(null);
      setIsTaskboardMode(false);
      setNodes(INITIAL_NODES);
      setEdges(INITIAL_EDGES);
    } else if (mode === 'taskboard') {
      handleSyncTaskboard(selectedHubFilter);
    }
  }, [handleDrilldownCluster, handleSyncTaskboard, selectedHubFilter, setNodes, setEdges]);

  // Initial load: 4 Macro Sovereign Clusters
  useEffect(() => {
    setNodes(
      WORKHORSE_CLUSTER_NODES.map((node) => ({
        ...node,
        data: {
          ...node.data,
          onToggleExpand: (hubId: string) => handleDrilldownCluster(hubId),
          onActionClick: (hubId: string) => handleDrilldownCluster(hubId),
        },
      }))
    );
    setEdges(WORKHORSE_CLUSTER_EDGES);
  }, [handleDrilldownCluster, setNodes, setEdges]);

  // Real-time Push Synchronization for Living Canvas from Hermes / Swarm SSE
  useEffect(() => {
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource('/api/v1/swarm/live/stream');
      eventSource.addEventListener('stream_event', (e) => {
        try {
          const parsed = JSON.parse(e.data);
          if (parsed.payload?.kind === 'taskboard_mutation') {
            handleSyncTaskboard();
          }
        } catch {
          // ignore parsing error
        }
      });
    } catch (err) {
      console.warn('Living Canvas SSE connection error:', err);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [handleSyncTaskboard]);

  const onConnect = useCallback(
    (params: Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            animated: true,
            style: { stroke: '#2a6368', strokeWidth: 2 },
          },
          eds
        )
      ),
    [setEdges]
  );

  // Simulated Dispatch Runner adhering to zero-waste protocol
  const handleDispatchSwarm = useCallback(() => {
    setActiveRunningAgent({ name: 'Gerych Prime', nodeName: 'DecomposeTaskDNA' });

    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === 'agent-prime') {
          return {
            ...node,
            data: {
              ...node.data,
              status: 'running',
              activeNodeName: 'DecomposeTaskDNA',
            },
          };
        }
        return node;
      })
    );

    // Simulate flow transition
    setTimeout(() => {
      setActiveRunningAgent({ name: 'Gerych Builder', nodeName: 'SynthesizeCanvasNode' });
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === 'agent-prime') {
            return {
              ...node,
              data: { ...node.data, status: 'completed', activeNodeName: undefined },
            };
          }
          if (node.id === 'agent-builder') {
            return {
              ...node,
              data: {
                ...node.data,
                status: 'running',
                activeNodeName: 'SynthesizeCanvasNode',
              },
            };
          }
          return node;
        })
      );
    }, 2000);

    setTimeout(() => {
      setActiveRunningAgent({ name: 'Gerych Auditor', nodeName: 'AdversarialGateReview' });
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === 'agent-builder') {
            return {
              ...node,
              data: { ...node.data, status: 'completed', activeNodeName: undefined },
            };
          }
          if (node.id === 'agent-auditor') {
            return {
              ...node,
              data: {
                ...node.data,
                status: 'running',
                activeNodeName: 'AdversarialGateReview',
              },
            };
          }
          return node;
        })
      );
    }, 4000);

    setTimeout(() => {
      setActiveRunningAgent(null);
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: { ...node.data, status: 'completed', activeNodeName: undefined },
        }))
      );
    }, 6000);
  }, [setNodes]);

  const handleToggleClustering = useCallback(() => {
    setIsClusteringEnabled((prev) => {
      const next = !prev;
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            community: next ? COMMUNITY_MAP[node.id] : undefined,
          },
        }))
      );
      return next;
    });
  }, [setNodes]);

  const handleStartTour = useCallback(() => {
    setActiveTourStep(0);
    const targetAgentId = GUIDED_TOUR_STEPS[0].agentId;
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          highlighted: node.id === targetAgentId,
          dimmed: node.id !== targetAgentId,
        },
      }))
    );
  }, [setNodes]);

  const handleNextTour = useCallback(() => {
    setActiveTourStep((curr) => {
      if (curr === null) return 0;
      const nextStep = (curr + 1) % GUIDED_TOUR_STEPS.length;
      const targetAgentId = GUIDED_TOUR_STEPS[nextStep].agentId;
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            highlighted: node.id === targetAgentId,
            dimmed: node.id !== targetAgentId,
          },
        }))
      );
      return nextStep;
    });
  }, [setNodes]);

  const handlePrevTour = useCallback(() => {
    setActiveTourStep((curr) => {
      if (curr === null) return 0;
      const prevStep = curr === 0 ? GUIDED_TOUR_STEPS.length - 1 : curr - 1;
      const targetAgentId = GUIDED_TOUR_STEPS[prevStep].agentId;
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            highlighted: node.id === targetAgentId,
            dimmed: node.id !== targetAgentId,
          },
        }))
      );
      return prevStep;
    });
  }, [setNodes]);

  const handleCloseTour = useCallback(() => {
    setActiveTourStep(null);
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          highlighted: false,
          dimmed: false,
        },
      }))
    );
  }, [setNodes]);

  const handleReset = useCallback(() => {
    setActiveRunningAgent(null);
    setActiveTourStep(null);
    setIsClusteringEnabled(false);
    setNodes(INITIAL_NODES);
    setEdges(INITIAL_EDGES);
  }, [setNodes, setEdges]);

  const handleAutoLayout = useCallback(() => {
    const inDegree: Record<string, number> = {};
    const adj: Record<string, string[]> = {};

    nodes.forEach((n) => {
      inDegree[n.id] = 0;
      adj[n.id] = [];
    });

    edges.forEach((e) => {
      if (inDegree[e.target] !== undefined) {
        inDegree[e.target] = (inDegree[e.target] || 0) + 1;
      }
      if (adj[e.source]) {
        adj[e.source].push(e.target);
      }
    });

    const rank: Record<string, number> = {};
    const queue: string[] = nodes.filter((n) => (inDegree[n.id] || 0) === 0).map((n) => n.id);

    queue.forEach((id) => {
      rank[id] = 0;
    });

    const processed = new Set<string>();
    while (queue.length > 0) {
      const curr = queue.shift()!;
      processed.add(curr);
      const currRank = rank[curr] || 0;

      (adj[curr] || []).forEach((neighbor) => {
        rank[neighbor] = Math.max(rank[neighbor] || 0, currRank + 1);
        inDegree[neighbor]--;
        if (inDegree[neighbor] <= 0 && !processed.has(neighbor)) {
          queue.push(neighbor);
        }
      });
    }

    nodes.forEach((n) => {
      if (rank[n.id] === undefined) {
        rank[n.id] = 0;
      }
    });

    const layers: Record<number, string[]> = {};
    nodes.forEach((n) => {
      const r = rank[n.id];
      if (!layers[r]) layers[r] = [];
      layers[r].push(n.id);
    });

    const COLUMN_WIDTH = 380;
    const ROW_HEIGHT = 220;
    const OFFSET_X = 60;
    const OFFSET_Y = 80;

    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        const r = rank[node.id] || 0;
        const indexInLayer = (layers[r] || []).indexOf(node.id);
        return {
          ...node,
          position: {
            x: OFFSET_X + r * COLUMN_WIDTH,
            y: OFFSET_Y + (indexInLayer >= 0 ? indexInLayer : 0) * ROW_HEIGHT,
          },
        };
      })
    );
  }, [nodes, edges, setNodes]);

  return (
    <div className="w-full h-full bg-[#090a0f] text-slate-100 relative flex flex-col font-sans overflow-hidden">
      {/* Main ReactFlow Canvas */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="bg-[#090a0f]"
        >
          {/* Deep Obsidian Background Dots */}
          <Background
            variant={BackgroundVariant.Dots}
            gap={24}
            size={1}
            color="#212433"
          />
          <Controls className="!bg-zinc-950/80 !border-white/10 !text-zinc-400 fill-zinc-400 backdrop-blur-md rounded-xl shadow-2xl" />
          <MiniMap
            nodeColor="rgba(255, 255, 255, 0.12)"
            maskColor="rgba(9, 10, 15, 0.85)"
            className="!bg-zinc-950/70 !border-white/10 backdrop-blur-md rounded-xl overflow-hidden shadow-2xl opacity-40 hover:opacity-100 transition-opacity"
          />

          {/* Centered Raycast / Dynamic Island Floating Command Dock */}
          <Panel position="top-center" className="flex items-center justify-center mt-3 z-30">
            <div className="flex items-center gap-1 p-1 rounded-full bg-zinc-950/85 backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.6)]">
              {/* Segmented view switcher */}
              <button
                type="button"
                onClick={() => handleSwitchViewMode('clusters')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                  viewMode === 'clusters'
                    ? 'bg-white/15 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                <span>Хаби Рою (4)</span>
              </button>

              <button
                type="button"
                onClick={() => handleSwitchViewMode('swarm')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                  viewMode === 'swarm'
                    ? 'bg-white/15 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <Bot className="w-3.5 h-3.5 text-purple-400" />
                <span>ThoughtDAG</span>
              </button>

              <button
                type="button"
                onClick={() => handleSwitchViewMode('taskboard')}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                  viewMode === 'taskboard'
                    ? 'bg-white/15 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isSyncingTaskboard ? 'animate-spin' : ''}`} />
                <span>Таски ({selectedHubFilter ? `${selectedHubFilter}` : '61'})</span>
              </button>

              {selectedHubFilter && (
                <button
                  type="button"
                  onClick={() => handleSwitchViewMode('clusters')}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-medium hover:bg-emerald-500/30 transition-all ml-0.5"
                >
                  <span>↩ До Хабів</span>
                </button>
              )}

              <div className="h-4 w-px bg-white/10 mx-1" />

              {/* Quick actions */}
              <button
                type="button"
                onClick={handleAutoLayout}
                className="p-1.5 rounded-full text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                title="Topological Auto-Layout"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              </button>

              <button
                type="button"
                onClick={() => handleSyncTaskboard()}
                disabled={isSyncingTaskboard}
                className="p-1.5 rounded-full text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                title="Синхронізувати Taskboard SQLite"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${isSyncingTaskboard ? 'animate-spin' : ''}`} />
              </button>

              <button
                type="button"
                onClick={() => setIsMCPModalOpen(true)}
                className="p-1.5 rounded-full text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                title="MCP Сервери"
              >
                <Server className="w-3.5 h-3.5 text-teal-400" />
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="p-1.5 rounded-full text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                title="Скинути полотно"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={handleDispatchSwarm}
                disabled={!!activeRunningAgent}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-lg transition-all ml-1 ${
                  activeRunningAgent
                    ? 'bg-zinc-800 text-zinc-400 cursor-not-allowed'
                    : 'bg-emerald-500 hover:bg-emerald-400 text-black font-semibold'
                }`}
              >
                {activeRunningAgent ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Рій працює</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3 h-3 fill-current" />
                    <span>Запустити рій</span>
                  </>
                )}
              </button>
            </div>
          </Panel>
        </ReactFlow>

        {/* Guided Tour Floating Overlay Card */}
        {activeTourStep !== null && (
          <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-40 w-[480px] max-w-[90vw] bg-[#162c2f] border border-[#35d5d5] rounded-xl shadow-2xl p-4 text-[#d4d8db]">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#224447]">
              <div className="flex items-center space-x-2">
                <span className="p-1 rounded bg-[#35d5d5]/20 text-[#35d5d5]">
                  <Compass className="w-4 h-4" />
                </span>
                <span className="text-xs font-semibold uppercase tracking-wider text-[#35d5d5]">
                  Guided Tour: Step {activeTourStep + 1} of {GUIDED_TOUR_STEPS.length}
                </span>
              </div>
              <button
                onClick={handleCloseTour}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <h4 className="text-sm font-bold text-white mb-1">
              {GUIDED_TOUR_STEPS[activeTourStep].title}
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              {GUIDED_TOUR_STEPS[activeTourStep].description}
            </p>
            <div className="flex items-center justify-between">
              <div className="flex space-x-1.5">
                {GUIDED_TOUR_STEPS.map((_, idx) => (
                  <span
                    key={idx}
                    className={`h-1.5 rounded-full transition-all ${
                      idx === activeTourStep ? 'w-6 bg-[#35d5d5]' : 'w-1.5 bg-slate-600'
                    }`}
                  />
                ))}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePrevTour}
                  className="px-2.5 py-1 text-xs rounded bg-[#112224] hover:bg-[#1e2022] border border-[#224447] text-slate-300 flex items-center space-x-1"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Prev</span>
                </button>
                <button
                  onClick={handleNextTour}
                  className="px-3 py-1 text-xs rounded bg-[#35d5d5] hover:bg-[#35d5d5]/80 text-[#112224] font-semibold flex items-center space-x-1"
                >
                  <span>{activeTourStep === GUIDED_TOUR_STEPS.length - 1 ? 'Finish' : 'Next'}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* MCP Configuration Modal */}
      <MCPConfigModal
        isOpen={isMCPModalOpen}
        onClose={() => setIsMCPModalOpen(false)}
      />
    </div>
  );
}

export default MultiAgentSwarmCanvas;
