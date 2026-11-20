// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_agent_AgentStreamHUD"
// purpose: "Meta Astryx Command HUD for real-time agent thought streaming, tool execution cards, Web Audio sensory feedback, and HITL approvals."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  Bot,
  Terminal,
  Sparkles,
  Wifi,
  WifiOff,
  ShieldCheck,
  RefreshCw,
  Layers,
  ChevronRight,
  Volume2,
  VolumeX
} from 'lucide-react';
import { ToolCallCard, ToolCallData } from './ToolCallCard';
import { HitlApprovalModal, HitlTicketData } from './HitlApprovalModal';

interface ThoughtItem {
  id: string;
  agent: string;
  content: string;
  thought_type: string;
  step: number;
  timestamp: string;
}

interface AgentStreamHUDProps {
  wsUrl?: string;
  sessionId?: string;
  className?: string;
}

function playAudioChime(type: 'hitl' | 'complete' | 'error') {
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();

    if (type === 'hitl') {
      const now = ctx.currentTime;
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

      osc1.frequency.setValueAtTime(880, now);
      osc1.frequency.exponentialRampToValueAtTime(1174.66, now + 0.15);
      osc2.frequency.setValueAtTime(1318.51, now + 0.15);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(now);
      osc2.start(now + 0.15);
      osc1.stop(now + 0.6);
      osc2.stop(now + 0.6);
    } else if (type === 'complete') {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      gain.gain.setValueAtTime(0.06, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

      osc.frequency.setValueAtTime(1760, now);
      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.12);
    } else if (type === 'error') {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

      osc.frequency.setValueAtTime(260, now);
      osc.frequency.linearRampToValueAtTime(180, now + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.25);
    }
  } catch (e) {
    // Silent fail if audio blocked by browser policy
  }
}

export function AgentStreamHUD({
  wsUrl = 'ws://localhost:8000/api/v1/swarm/live/ws',
  sessionId,
  className = ''
}: AgentStreamHUDProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [thoughts, setThoughts] = useState<ThoughtItem[]>([]);
  const [toolCalls, setToolCalls] = useState<Record<string, ToolCallData>>({});
  const [pendingTicket, setPendingTicket] = useState<HitlTicketData | null>(null);
  const [activeAgent, setActiveAgent] = useState('denchik');
  const [isSubmittingHitl, setIsSubmittingHitl] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);

  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const isAudioEnabledRef = useRef(isAudioEnabled);

  useEffect(() => {
    isAudioEnabledRef.current = isAudioEnabled;
  }, [isAudioEnabled]);

  const triggerSound = useCallback((type: 'hitl' | 'complete' | 'error') => {
    if (isAudioEnabledRef.current) {
      playAudioChime(type);
    }
  }, []);

  useEffect(() => {
    let reconnectTimeout: any;

    const connect = () => {
      const url = sessionId ? `${wsUrl}?session_id=${sessionId}` : wsUrl;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.warn('Astryx HUD WebSocket error:', err);
        ws.close();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'HYDRATION_SNAPSHOT' && Array.isArray(data.history)) {
            data.history.forEach((env: any) => {
              processEnvelope(env, false);
            });
          } else if (data.type === 'STREAM_EVENT') {
            processEnvelope(data, true);
          }
        } catch (e) {
          console.error('Error processing stream message:', e);
        }
      };
    };

    const processEnvelope = (env: any, isLive: boolean) => {
      const payload = env.payload || {};
      const kind = payload.kind;

      if (env.agent) {
        setActiveAgent(env.agent);
      }

      if (kind === 'thought_stream') {
        setThoughts((prev) => [
          ...prev.slice(-49),
          {
            id: `th_${Date.now()}_${Math.random()}`,
            agent: env.agent || 'denchik',
            content: payload.content || '',
            thought_type: payload.thought_type || 'reasoning',
            step: payload.step || 0,
            timestamp: env.timestamp || new Date().toISOString(),
          },
        ]);
      } else if (kind === 'tool_start') {
        const callId = payload.tool_call_id;
        if (callId) {
          setToolCalls((prev) => ({
            ...prev,
            [callId]: {
              tool_call_id: callId,
              tool_name: payload.tool_name,
              tool_args: payload.tool_args,
              status: 'executing',
              started_at: payload.started_at,
            },
          }));
        }
      } else if (kind === 'tool_complete') {
        const callId = payload.tool_call_id;
        if (callId) {
          setToolCalls((prev) => ({
            ...prev,
            [callId]: {
              ...(prev[callId] || {
                tool_call_id: callId,
                tool_name: payload.tool_name,
                tool_args: {},
              }),
              status: payload.success ? 'completed' : 'failed',
              result: payload.result,
              exit_code: payload.exit_code,
              duration_ms: payload.duration_ms,
              completed_at: payload.completed_at,
            },
          }));
          if (isLive) {
            triggerSound(payload.success ? 'complete' : 'error');
          }
        }
      } else if (kind === 'hitl_approval_request') {
        setPendingTicket({
          ticket_id: payload.ticket_id,
          session_id: payload.session_id,
          agent: payload.agent,
          action_type: payload.action_type,
          details: payload.details,
          options: payload.options,
          timeout_seconds: payload.timeout_seconds,
        });
        if (isLive) {
          triggerSound('hitl');
        }
      } else if (kind === 'hitl_approval_resolved') {
        setPendingTicket((current) =>
          current && current.ticket_id === payload.ticket_id ? null : current
        );
      }
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [wsUrl, sessionId, triggerSound]);

  const handleResolveHitl = (decision: { approved: boolean; reason?: string; modifications?: Record<string, any> }) => {
    if (!pendingTicket || !wsRef.current) return;
    setIsSubmittingHitl(true);

    try {
      wsRef.current.send(
        JSON.stringify({
          action: 'HITL_RESOLVE',
          ticket_id: pendingTicket.ticket_id,
          decision,
        })
      );
      setPendingTicket(null);
    } catch (e) {
      console.error('Failed to send HITL resolution:', e);
    } finally {
      setIsSubmittingHitl(false);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [thoughts, toolCalls]);

  const toolList = Object.values(toolCalls).reverse();

  return (
    <div className={`flex flex-col h-full bg-neutral-950/95 border border-border/50 rounded-2xl overflow-hidden backdrop-blur-md ${className}`}>
      {/* Top Cockpit Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/40 bg-neutral-900/60">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <Bot className="w-5 h-5 text-purple-400" />
            <span
              className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-neutral-950 ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
                }`}
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-xs tracking-wider uppercase text-foreground">
                Swarm HUD
              </span>
              <span className="text-[10px] px-1.5 py-0.2 bg-purple-950/60 border border-purple-500/40 text-purple-300 rounded font-mono">
                {activeAgent}
              </span>
            </div>
            <p className="text-[10px] text-muted-foreground font-mono">
              Hermes ACP & FastMCP Bridge
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Audio Chime Mute/Unmute */}
          <button
            type="button"
            onClick={() => setIsAudioEnabled(!isAudioEnabled)}
            title={isAudioEnabled ? "Sound notifications enabled" : "Sound muted"}
            className={`p-1.5 rounded-lg border text-xs transition-colors ${isAudioEnabled
                ? 'border-purple-500/30 text-purple-300 bg-purple-950/20 hover:bg-purple-950/40'
                : 'border-border/40 text-muted-foreground hover:text-foreground'
              }`}
          >
            {isAudioEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
          </button>

          <span
            className={`flex items-center gap-1.5 text-[11px] font-mono px-2 py-0.5 rounded-full border ${isConnected
                ? 'border-emerald-500/30 bg-emerald-950/30 text-emerald-400'
                : 'border-rose-500/30 bg-rose-950/30 text-rose-400'
              }`}
          >
            {isConnected ? (
              <>
                <Wifi className="w-3 h-3" />
                Live
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3" />
                Offline
              </>
            )}
          </span>
        </div>
      </div>

      {/* Main Stream Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
        {/* Active Tool Calls section */}
        {toolList.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              <span className="flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-amber-400" />
                Tool Executions ({toolList.length})
              </span>
            </div>
            <div className="space-y-2">
              {toolList.map((tool) => (
                <ToolCallCard
                  key={tool.tool_call_id}
                  toolCall={tool}
                  agentName={activeAgent}
                />
              ))}
            </div>
          </div>
        )}

        {/* Thought Stream section */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            Agent Thoughts & Trajectory
          </div>

          {thoughts.length === 0 ? (
            <div className="py-6 px-4 rounded-xl border border-white/[0.06] bg-white/[0.02] space-y-3 font-sans">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Рій готовий до автономного виконання</span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed">
                Тут транслюються живі епістемічні міркування, виклики FastMCP інструментів та HITL-гейти перевірки якості.
              </p>
              <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[10px]">
                <div className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-500">Antigravity</span>
                  <span className="text-emerald-400">Mentor</span>
                </div>
                <div className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-500">Denchik</span>
                  <span className="text-blue-400">Builder</span>
                </div>
                <div className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-500">Gerych Prime</span>
                  <span className="text-purple-400">Auditor</span>
                </div>
                <div className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-500">FastMCP</span>
                  <span className="text-teal-400">&lt; 12ms</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {thoughts.map((th) => (
                <div
                  key={th.id}
                  className="p-3 rounded-xl border border-border/30 bg-black/40 hover:border-purple-500/30 transition-colors"
                >
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
                    <span className="font-semibold text-purple-300">
                      @{th.agent} (step {th.step})
                    </span>
                    <span>{new Date(th.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="whitespace-pre-wrap text-neutral-200 text-xs leading-relaxed font-sans">
                    {th.content}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div ref={bottomRef} />
      </div>

      {/* HITL Gateway Approval Modal Overlay */}
      {pendingTicket && (
        <HitlApprovalModal
          ticket={pendingTicket}
          onResolve={handleResolveHitl}
          isSubmitting={isSubmittingHitl}
        />
      )}
    </div>
  );
}
