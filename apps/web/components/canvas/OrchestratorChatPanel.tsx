// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_OrchestratorChatPanel"
// purpose: "Living CapCut-Style Orchestrator Cockpit & Bi-directional ThoughtDAG Canvas Bridge with Gerych Prime"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "4.0.0"
// updated_at: "2026-09-16"
// author: "DNK-e.com Maksym & Gerych Prime"
// --- END DNK-MRH-HEADER ---

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2,
  Layers,
  Cpu,
  RefreshCw,
  Zap,
  Shield,
  Code2,
  ShoppingBag,
  Film,
  TrendingUp,
  X,
  ExternalLink,
  ArrowUp,
  Plus,
  Box,
  BookOpen,
  Trash2,
  Bot
} from 'lucide-react';
import { useCanvasStore } from '@/store/canvasStore';
import {
  ShopifyBlockPreviewWidget,
  AnalyticsMetricCardWidget,
  SocialContentCardWidget,
  ThoughtDAGCardWidget,
} from '@/components/generative_ui';

interface ToolEvent {
  tool: string;
  args?: any;
  result?: string;
  status?: 'calling' | 'done';
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'gerych';
  text: string;
  timestamp: string;
  actions?: Array<{ action_type: string; payload: Record<string, any> }>;
  activeAgents?: string[];
  model?: string;
  provider?: string;
  thoughts?: string[];
  toolEvents?: ToolEvent[];
  streaming?: boolean;
  focusNodeTitle?: string;
}

interface OrchestratorChatPanelProps {
  isOpen?: boolean;
  onToggle?: () => void;
  className?: string;
}

interface SkillItem {
  id: string;
  title: string;
  category: string;
  icon: React.ReactNode;
  bgGradient: string;
  prompt: string;
}

const SWARM_SKILLS: SkillItem[] = [
  {
    id: 'shopify_liquid',
    title: 'Shopify Liquid',
    category: 'E-commerce',
    icon: <ShoppingBag className="w-3.5 h-3.5 text-emerald-400" />,
    bgGradient: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-200 hover:border-emerald-400/50',
    prompt: 'Створи таску для dnk_shopify: розроби Sticky ATC блок з прев\'ю віджетом Astryx та валідацією Liquid AST',
  },
  {
    id: 'growth_analytics',
    title: 'CRO & Аналітика',
    category: 'Analytics',
    icon: <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />,
    bgGradient: 'from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-200 hover:border-cyan-400/50',
    prompt: 'Створи аналітичний віджет CVR/AOV для магазину та розрахуй приріст конверсії з sparkline графіком',
  },
  {
    id: 'video_cover',
    title: 'Відео сценарій',
    category: 'Video AI',
    icon: <Film className="w-3.5 h-3.5 text-rose-400" />,
    bgGradient: 'from-rose-500/20 to-orange-500/10 border-rose-500/30 text-rose-200 hover:border-rose-400/50',
    prompt: 'Створи таску для dnk_video_ai_creator: розроби промо-відео сценарій для TikTok/Reels з хуком та віджетом',
  },
  {
    id: 'tech_spec',
    title: 'Архітектурна спека',
    category: 'ThoughtDAG',
    icon: <Layers className="w-3.5 h-3.5 text-amber-400" />,
    bgGradient: 'from-amber-500/20 to-yellow-500/10 border-amber-500/30 text-amber-200 hover:border-amber-400/50',
    prompt: 'Створи нову нотатку архітектурної специфікації ThoughtDAG з 3-Flaws критикою та прив\'яжи її до контексту',
  },
  {
    id: 'builder_task',
    title: 'Builder Task',
    category: 'Code/UI',
    icon: <Code2 className="w-3.5 h-3.5 text-purple-400" />,
    bgGradient: 'from-purple-500/20 to-indigo-500/10 border-purple-500/30 text-purple-200 hover:border-purple-400/50',
    prompt: 'Створи таску для gerych_builder: розроби новий UI віджет та підключи його до React Flow полотна',
  },
  {
    id: 'security_audit',
    title: 'Аудит безпеки',
    category: 'Auditor',
    icon: <Shield className="w-3.5 h-3.5 text-sky-400" />,
    bgGradient: 'from-sky-500/20 to-blue-500/10 border-sky-500/30 text-sky-200 hover:border-sky-400/50',
    prompt: 'Створи таску для gerych_auditor: запусти Red-Team аудит безпеки та перевір інваріанти якості',
  },
  {
    id: 'scones_memory',
    title: 'SCONES Пам\'ять',
    category: 'Knowledge',
    icon: <Cpu className="w-3.5 h-3.5 text-fuchsia-400" />,
    bgGradient: 'from-fuchsia-500/20 to-pink-500/10 border-fuchsia-500/30 text-fuchsia-200 hover:border-fuchsia-400/50',
    prompt: 'Знайди у пам\'яті SCONES перевірені архітектурні патерни та правила для поточного завдання',
  },
  {
    id: 'task_forest',
    title: 'Task Forest DAG',
    category: 'Orchestration',
    icon: <Sparkles className="w-3.5 h-3.5 text-lime-400" />,
    bgGradient: 'from-lime-500/20 to-emerald-500/10 border-lime-500/30 text-lime-200 hover:border-lime-400/50',
    prompt: 'Декомпозуй задачу на еволюційний DAG залежностей TaskDNA та розгорни вузли на полотні',
  },
];

const MessageBodyWithGenerativeUI: React.FC<{
  text: string;
  streaming?: boolean;
  onApplyAction?: (actions: Array<{ action_type: string; payload: Record<string, any> }>) => void;
}> = ({ text, streaming, onApplyAction }) => {
  const regex = /<!--\s*GENERATIVE_UI:([a-z_]+)\s+([\s\S]*?)\s*-->/g;
  const segments: Array<{ type: 'text' | 'widget'; content: string; widgetType?: string; widgetData?: any }> = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: text.slice(lastIndex, match.index),
      });
    }
    try {
      const widgetData = JSON.parse(match[2]);
      segments.push({
        type: 'widget',
        content: match[0],
        widgetType: match[1],
        widgetData,
      });
    } catch {
      segments.push({
        type: 'text',
        content: match[0],
      });
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    segments.push({
      type: 'text',
      content: text.slice(lastIndex),
    });
  }

  return (
    <div className="space-y-3">
      {segments.map((seg, idx) => {
        if (seg.type === 'text') {
          if (!seg.content.trim() && idx > 0 && idx < segments.length - 1) return null;
          return (
            <div key={`seg-${idx}`} className="text-neutral-200 leading-relaxed whitespace-pre-wrap">
              {seg.content}
            </div>
          );
        }

        if (seg.widgetType === 'shopify_block') {
          return (
            <div key={`seg-${idx}`} className="my-2">
              <ShopifyBlockPreviewWidget
                {...seg.widgetData}
                onApplyToCanvas={(blockType, schema) => {
                  onApplyAction?.([
                    {
                      action_type: 'add_note',
                      payload: {
                        title: `Shopify Block: ${blockType}`,
                        content: JSON.stringify(schema, null, 2),
                        x: 350,
                        y: 200,
                      },
                    },
                  ]);
                }}
              />
            </div>
          );
        }

        if (seg.widgetType === 'analytics') {
          return (
            <div key={`seg-${idx}`} className="my-2">
              <AnalyticsMetricCardWidget
                {...seg.widgetData}
                onDrillDown={() => {
                  onApplyAction?.([
                    {
                      action_type: 'add_agent_task',
                      payload: {
                        title: `Deep-Dive: ${seg.widgetData?.title || 'Analytics'}`,
                        agent: 'dnk_dev_fullstack',
                        description: `Analyze historical cohort metrics for ${seg.widgetData?.metricType || 'metrics'}`,
                        status: 'pending',
                        x: 600,
                        y: 250,
                      },
                    },
                  ]);
                }}
              />
            </div>
          );
        }

        if (seg.widgetType === 'social') {
          return (
            <div key={`seg-${idx}`} className="my-2">
              <SocialContentCardWidget
                {...seg.widgetData}
                onRenderVideo={() => {
                  onApplyAction?.([
                    {
                      action_type: 'add_agent_task',
                      payload: {
                        title: `Render HyperFrames Video: ${seg.widgetData?.platform || 'Social'}`,
                        agent: 'dnk_video_ai_creator',
                        description: `Generate 60FPS video composition for script: ${seg.widgetData?.hook || ''}`,
                        status: 'pending',
                        x: 650,
                        y: 150,
                      },
                    },
                  ]);
                }}
              />
            </div>
          );
        }

        if (seg.widgetType === 'thought_dag') {
          return (
            <div key={`seg-${idx}`} className="my-2">
              <ThoughtDAGCardWidget
                {...seg.widgetData}
                onBranchFork={() => {
                  onApplyAction?.([
                    {
                      action_type: 'add_note',
                      payload: {
                        title: `Counter-Hypothesis: ${seg.widgetData?.title || 'Branch'}`,
                        content: `Dissenting branch attacking assumptions:\n${(seg.widgetData?.flaws || []).join('\n')}`,
                        x: 400,
                        y: 350,
                      },
                    },
                  ]);
                }}
              />
            </div>
          );
        }

        return null;
      })}

      {streaming && (
        <span className="inline-block w-2 h-4 ml-1 bg-purple-400 animate-pulse align-middle" />
      )}
    </div>
  );
};

export const OrchestratorChatPanel: React.FC<OrchestratorChatPanelProps> = ({
  isOpen: propIsOpen,
  onToggle,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(propIsOpen ?? true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeModelInfo, setActiveModelInfo] = useState<{ model: string; provider: string } | null>(null);
  const [showAllSkills, setShowAllSkills] = useState(false);
  const [expandedAccordions, setExpandedAccordions] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    nodes,
    edges,
    selectedNodeId,
    selectNode,
    applyCanvasActions,
  } = useCanvasStore();

  const selectedNode = selectedNodeId ? nodes.find((n) => n.id === selectedNodeId) : null;
  const selectedNodeTitle = selectedNode
    ? (selectedNode.data as any)?.title || selectedNode.id
    : null;

  // Maintain isolated message thread per selected node (with fallback to '__canvas_global__')
  const [nodeThreads, setNodeThreads] = useState<Record<string, ChatMessage[]>>({});
  const activeThreadKey = selectedNodeId || '__canvas_global__';
  const messages = (nodeThreads[activeThreadKey] && nodeThreads[activeThreadKey].length > 0)
    ? nodeThreads[activeThreadKey]
    : (nodeThreads['__canvas_global__'] || []);

  const setMessages = useCallback(
    (updater: ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[])) => {
      setNodeThreads((prevThreads) => {
        const current = (prevThreads[activeThreadKey] && prevThreads[activeThreadKey].length > 0)
          ? prevThreads[activeThreadKey]
          : (prevThreads['__canvas_global__'] || []);
        const updated = typeof updater === 'function' ? (updater as (prev: ChatMessage[]) => ChatMessage[])(current) : updater;
        const nextThreads = { ...prevThreads, [activeThreadKey]: updated };
        if (activeThreadKey !== '__canvas_global__' && (!prevThreads[activeThreadKey] || prevThreads[activeThreadKey].length === 0)) {
          nextThreads['__canvas_global__'] = updated;
        }
        return nextThreads;
      });
    },
    [activeThreadKey]
  );

  const toggleAccordion = (msgId: string) => {
    setExpandedAccordions((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const handleClearHistory = () => {
    setMessages([]);
    setInputMessage('');
  };

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/v1/orchestrator/status', {
      headers: { 'X-Workspace-ID': 'ws-alpha-001' },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.active_model) {
          setActiveModelInfo({
            model: data.active_model,
            provider: data.active_provider || 'vertex',
          });
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (propIsOpen !== undefined) {
      setIsOpen(propIsOpen);
    }
  }, [propIsOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (customPrompt?: string) => {
    const rawVal = textareaRef.current?.value || '';
    const textToSend = customPrompt || inputMessage.trim() || rawVal.trim();
    if (!textToSend || isLoading) return;

    const userMsg: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const agentMsgId = `msg-agent-${Date.now()}`;
    const initialAgentMsg: ChatMessage = {
      id: agentMsgId,
      sender: 'gerych',
      text: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      thoughts: [],
      toolEvents: [],
      actions: [],
      streaming: true,
      focusNodeTitle: selectedNodeTitle || undefined,
    };

    setMessages((prev) => [...prev, userMsg, initialAgentMsg]);
    // Keep reasoning accordion collapsed by default for clean CapCut chat aesthetic
    if (!customPrompt) setInputMessage('');
    setIsLoading(true);

    const payload = {
      message: textToSend,
      session_id: 'session-canvas-main',
      target_agent: 'gerych_prime',
      history: messages.slice(-6).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      })),
      canvas_context: {
        nodes: nodes.map((n) => ({ id: n.id, type: n.type, title: (n.data as any)?.title })),
        edges_count: edges.length,
        selected_node_id: selectedNodeId,
      },
      selected_node: selectedNode
        ? {
            id: selectedNode.id,
            type: selectedNode.type,
            title: (selectedNode.data as any)?.title || selectedNode.id,
            content: (selectedNode.data as any)?.content || (selectedNode.data as any)?.description || '',
          }
        : null,
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/orchestrator/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Workspace-ID': 'ws-alpha-001',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok || !response.body) {
        throw new Error(`SSE streaming failed with status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;
          const jsonStr = trimmed.slice(6).trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr);

            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== agentMsgId) return msg;

                if (event.type === 'thought') {
                  return {
                    ...msg,
                    thoughts: [...(msg.thoughts || []), event.text],
                  };
                }

                if (event.type === 'tool_call') {
                  return {
                    ...msg,
                    toolEvents: [
                      ...(msg.toolEvents || []),
                      { tool: event.tool, args: event.args, status: 'calling' },
                    ],
                  };
                }

                if (event.type === 'tool_result') {
                  const updatedTools = (msg.toolEvents || []).map((te) =>
                    te.tool === event.tool ? { ...te, result: event.result, status: 'done' as const } : te
                  );
                  return {
                    ...msg,
                    toolEvents: updatedTools,
                  };
                }

                if (event.type === 'canvas_mutation' && event.action) {
                  applyCanvasActions([event.action]);
                  return {
                    ...msg,
                    actions: [...(msg.actions || []), event.action],
                  };
                }

                if (event.type === 'content_chunk' && event.delta) {
                  return {
                    ...msg,
                    text: msg.text + event.delta,
                  };
                }

                if (event.type === 'done') {
                  if (event.canvas_actions?.length && (!msg.actions || msg.actions.length === 0)) {
                    applyCanvasActions(event.canvas_actions);
                  }
                  return {
                    ...msg,
                    text: event.reply || msg.text,
                    model: event.model || msg.model,
                    provider: event.provider || msg.provider,
                    activeAgents: event.active_agents || msg.activeAgents,
                    actions: event.canvas_actions || msg.actions,
                    streaming: false,
                  };
                }

                return msg;
              })
            );
          } catch {
            // Ignore parse errors on individual SSE chunks
          }
        }
      }
    } catch (err) {
      console.warn('Streaming encountered an issue, falling back to synchronous chat POST:', err);
      try {
        const fallbackRes = await fetch('http://127.0.0.1:8000/api/v1/orchestrator/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Workspace-ID': 'ws-alpha-001',
          },
          body: JSON.stringify(payload),
        });

        if (fallbackRes.ok) {
          const fallbackData = await fallbackRes.json();
          if (fallbackData.canvas_actions?.length) {
            applyCanvasActions(fallbackData.canvas_actions);
          }
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === agentMsgId
                ? {
                    ...msg,
                    text: fallbackData.reply,
                    model: fallbackData.model,
                    provider: fallbackData.provider,
                    activeAgents: fallbackData.active_agents,
                    actions: fallbackData.canvas_actions,
                    streaming: false,
                  }
                : msg
            )
          );
        }
      } catch (fallbackErr) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === agentMsgId
              ? {
                  ...msg,
                  text: "⚠️ Помилка з'єднання з ядром або тайм-аут провайдера. Будь ласка, перевірте backend або повторіть спробу.",
                  streaming: false,
                }
              : msg
          )
        );
      }
    } finally {
      setIsLoading(false);
      setMessages((prev) =>
        prev.map((msg) => (msg.id === agentMsgId ? { ...msg, streaming: false } : msg))
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => {
          setIsOpen(true);
          onToggle?.();
        }}
        className={`fixed right-6 bottom-6 z-40 flex items-center gap-2.5 px-4 py-3 bg-[#18181b] hover:bg-[#27272a] text-white border border-white/10 rounded-full shadow-2xl transition-all duration-200 group ${className}`}
      >
        <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-inner">
          <Sparkles className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="text-sm font-medium">Герич Prime</span>
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
      </button>
    );
  }

  const visibleSkills = showAllSkills ? SWARM_SKILLS : SWARM_SKILLS.slice(0, 5);

  return (
    <aside
      className={`fixed top-14 right-0 bottom-0 z-30 flex flex-col bg-[#121214] border-l border-white/[0.08] text-white shadow-2xl transition-all duration-300 font-sans ${
        isExpanded ? 'w-[520px]' : 'w-[400px]'
      } ${className}`}
    >
      {/* 1. Header (CapCut Minimalist Style) */}
      <header className="flex items-center justify-between px-5 py-3.5 border-b border-white/[0.06] bg-[#121214]/90 backdrop-blur-md shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-md">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white tracking-tight">Герич Prime</span>
              <span className="flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live
              </span>
            </div>
            {activeModelInfo && (
              <p className="text-[10px] text-neutral-400 font-mono">
                {activeModelInfo.model} ({activeModelInfo.provider})
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              type="button"
              onClick={handleClearHistory}
              title="Новий діалог"
              className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label={isExpanded ? 'Згорнути панель' : 'Розгорнути панель'}
            className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors cursor-pointer"
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              onToggle?.();
            }}
            aria-label="Закрити панель"
            className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* 2. Main Body (Hero State OR Chat Messages) */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 ? (
          /* CapCut Hero / Skill Selector Section */
          <div className="flex flex-col justify-center min-h-[360px] animate-in fade-in duration-300">
            <h2 className="text-2xl font-bold text-white tracking-tight leading-snug">
              Що ми створюємо сьогодні?
            </h2>
            <p className="text-sm text-neutral-400 mt-1.5 mb-6 leading-relaxed">
              Поділіться ідеєю, виділіть вузол на полотні або оберіть навичку рою для старту.
            </p>

            {/* Skills Pills */}
            <div className="space-y-2.5">
              <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                Навички рою
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {visibleSkills.map((skill) => (
                  <button
                    key={skill.id}
                    type="button"
                    onClick={() => handleSendMessage(skill.prompt)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium border bg-gradient-to-r transition-all duration-200 shadow-sm ${skill.bgGradient}`}
                  >
                    {skill.icon}
                    <span>{skill.title}</span>
                  </button>
                ))}
              </div>

              {SWARM_SKILLS.length > 5 && (
                <button
                  type="button"
                  onClick={() => setShowAllSkills(!showAllSkills)}
                  className="flex items-center gap-1 text-xs font-medium text-neutral-400 hover:text-white pt-1 transition-colors"
                >
                  {showAllSkills ? (
                    <>
                      <ChevronUp className="w-3.5 h-3.5" />
                      <span>Згорнути</span>
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-3.5 h-3.5" />
                      <span>Показати ще {SWARM_SKILLS.length - 5} навички</span>
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Canvas State Overview Card */}
            <div className="mt-8 p-3.5 rounded-2xl bg-neutral-900/60 border border-white/[0.06] text-xs text-neutral-300 space-y-2">
              <div className="flex items-center justify-between text-neutral-400">
                <span className="font-semibold text-neutral-300">Полотно ThoughtDAG</span>
                <span className="font-mono text-[11px] text-neutral-500">CONTRACT_002</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-neutral-400 pt-1">
                <div className="flex items-center gap-1.5 bg-neutral-800/40 px-2.5 py-1.5 rounded-lg border border-white/[0.04]">
                  <Box className="w-3.5 h-3.5 text-purple-400" />
                  <span>Вузлів: <b className="text-white">{nodes.length}</b></span>
                </div>
                <div className="flex items-center gap-1.5 bg-neutral-800/40 px-2.5 py-1.5 rounded-lg border border-white/[0.04]">
                  <Zap className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Дротів: <b className="text-white">{edges.length}</b></span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Active Chat Thread */
          <div className="space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className="space-y-2">
                {msg.sender === 'user' ? (
                  /* User Bubble */
                  <div className="flex justify-end">
                    <div className="max-w-[85%] px-4 py-2.5 rounded-2xl bg-[#26262b] text-neutral-100 text-sm leading-relaxed border border-white/[0.06] shadow-sm">
                      {msg.text}
                    </div>
                  </div>
                ) : (
                  /* Agent Message */
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between text-xs text-neutral-400">
                      <div className="flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                        <span className="font-semibold text-white">Герич Prime</span>
                        {msg.focusNodeTitle && (
                          <span className="px-1.5 py-0.2 rounded text-[10px] bg-purple-950/80 text-purple-300 border border-purple-800/50">
                            Фокус: {msg.focusNodeTitle}
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] text-neutral-500">{msg.timestamp}</span>
                    </div>

                    {/* Accordion: Thoughts & Tool Invocations */}
                    {((msg.thoughts && msg.thoughts.length > 0) || (msg.toolEvents && msg.toolEvents.length > 0)) && (
                      <div className="border border-white/[0.06] rounded-xl bg-neutral-900/80 overflow-hidden text-xs">
                        <button
                          type="button"
                          onClick={() => toggleAccordion(msg.id)}
                          className="w-full flex items-center justify-between px-3 py-2 bg-neutral-800/30 hover:bg-neutral-800/60 text-neutral-400 font-mono text-[11px] transition-colors"
                        >
                          <span className="flex items-center gap-2">
                            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                            <span>
                              {msg.thoughts?.length || 0} міркування • {msg.toolEvents?.length || 0} інструментів
                            </span>
                          </span>
                          {expandedAccordions[msg.id] ? (
                            <ChevronUp className="w-3.5 h-3.5 text-neutral-400" />
                          ) : (
                            <ChevronDown className="w-3.5 h-3.5 text-neutral-400" />
                          )}
                        </button>
                        {expandedAccordions[msg.id] && (
                          <div className="p-3 space-y-2 border-t border-white/[0.04] font-mono text-[11px]">
                            {msg.thoughts?.map((thought, idx) => (
                              <div
                                key={`th-${idx}`}
                                className="flex items-start gap-2 text-neutral-300 pl-2 border-l-2 border-purple-500/70"
                              >
                                <span className="text-purple-400">💭</span>
                                <span className="leading-relaxed">{thought}</span>
                              </div>
                            ))}
                            {msg.toolEvents?.map((te, idx) => (
                              <div
                                key={`tl-${idx}`}
                                className="flex items-start gap-2 text-emerald-300 pl-2 border-l-2 border-emerald-500/70"
                              >
                                <span className="text-emerald-400">⚡</span>
                                <div className="leading-relaxed">
                                  <span className="font-semibold text-emerald-200">{te.tool}</span>
                                  {te.result && (
                                    <span className="text-neutral-400 ml-1.5">➔ {te.result}</span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Message Body with Astryx Generative UI Synthesis */}
                    <MessageBodyWithGenerativeUI
                      text={msg.text}
                      streaming={msg.streaming}
                      onApplyAction={applyCanvasActions}
                    />

                    {/* Canvas Action Artifacts (Compact Pills) */}
                    {msg.actions && msg.actions.length > 0 && (
                      <div className="pt-2 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] uppercase tracking-wider font-semibold text-neutral-400 mr-1">
                          Артефакти:
                        </span>
                        {msg.actions.map((act, idx) => (
                          <span
                            key={`act-${idx}`}
                            className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-purple-950/70 border border-purple-700/50 text-[11px] text-purple-200 font-medium"
                          >
                            <Box className="w-3 h-3 text-purple-400 shrink-0" />
                            <span className="truncate max-w-[140px]">
                              {act.action_type === 'create_task'
                                ? `Таска: ${act.payload.agent || 'агент'}`
                                : act.action_type === 'create_spec'
                                ? `Спека: ${act.payload.title}`
                                : act.action_type}
                            </span>
                            <span className="text-[10px] text-emerald-400 font-bold">✓</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* 3. Bottom Input Box (CapCut Signature Architecture) */}
      <footer className="p-4 border-t border-white/[0.06] bg-[#121214] shrink-0 space-y-2">
        {/* Spatial Focus Pill */}
        {selectedNode && (
          <div className="flex items-center justify-between px-3 py-1.5 bg-[#1b1928] border border-purple-500/30 rounded-xl text-xs text-purple-200 animate-in fade-in duration-150">
            <div className="flex items-center gap-1.5 truncate">
              <Zap className="w-3.5 h-3.5 text-purple-400 shrink-0 animate-pulse" />
              <span className="font-semibold text-purple-300">Фокус:</span>
              <span className="truncate font-medium">{selectedNodeTitle}</span>
              <span className="px-1.5 py-0.2 rounded text-[10px] bg-purple-900/60 text-purple-300 border border-purple-700/40">
                {selectedNode.type}
              </span>
            </div>
            <button
              type="button"
              onClick={() => selectNode(null)}
              className="text-purple-400 hover:text-white transition-colors p-0.5 rounded-md"
              title="Зняти фокус"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* CapCut Rounded Input Container */}
        <div className="relative rounded-2xl bg-[#1c1c20] border border-white/[0.08] hover:border-white/[0.16] focus-within:border-white/[0.24] transition-all duration-200 p-2.5 shadow-xl">
          <textarea
            ref={textareaRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onInput={(e) => setInputMessage((e.target as HTMLTextAreaElement).value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedNodeTitle
                ? `Запитайте або дайте команду щодо «${selectedNodeTitle}»...`
                : 'Опишіть завдання або ідею (Shift+Enter для нового рядка)...'
            }
            rows={2}
            className="w-full bg-transparent text-sm text-white placeholder-neutral-500 resize-none outline-none px-1 py-1 leading-relaxed"
          />

          {/* Sub-toolbar inside the input container */}
          <div className="flex items-center justify-between pt-1 border-t border-white/[0.04]">
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => handleSendMessage('Створи нову нотатку на полотні ThoughtDAG')}
                title="Додати нотатку"
                className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => handleSendMessage('Створи таску для рою агентів')}
                title="Додати таску рою"
                className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors"
              >
                <Box className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => handleSendMessage('Перевір базу знань SCONES щодо поточного контексту')}
                title="База знань SCONES"
                className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition-colors"
              >
                <BookOpen className="w-4 h-4" />
              </button>
            </div>

            {/* Upward Circular Submit Arrow (CapCut Style) */}
            <button
              type="button"
              disabled={isLoading || (!inputMessage.trim() && !textareaRef.current?.value.trim())}
              onClick={() => handleSendMessage()}
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${
                isLoading
                  ? 'bg-purple-600 text-white animate-pulse'
                  : inputMessage.trim() || textareaRef.current?.value.trim()
                  ? 'bg-white text-black hover:bg-neutral-200 shadow-md cursor-pointer'
                  : 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              }`}
              title="Надіслати (Enter)"
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          </div>
        </div>
      </footer>
    </aside>
  );
};

export default OrchestratorChatPanel;
