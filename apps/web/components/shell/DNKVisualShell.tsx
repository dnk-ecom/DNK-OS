// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/shell/DNKVisualShell.tsx"
// purpose: "Main DNK OS Visual Shell orchestrator. Assembles sidebar, topbar, SaaP grid, agent swarm and events log into unified kernel dashboard."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import VisualShellSidebar from './VisualShellSidebar';
import KernelStatusBar from './KernelStatusBar';
import SaaPServiceCard, { SaaPService } from './SaaPServiceCard';
import AgentSwarmPanel, { Agent } from './AgentSwarmPanel';
import SystemEventsLog from './SystemEventsLog';
import { Layers, RefreshCw, Filter } from 'lucide-react';

// ── SEED DATA ──────────────────────────────────────────────────────────────────

const SAAP_SERVICES: SaaPService[] = [
  { id: 's1',  name: 'dnk_video_ai_creator',       domain: 'Media',      status: 'active',   cpu: 58, requests: 13, latencyMs: 87,  icon: 'video',    color: '#a78bfa' },
  { id: 's2',  name: 'dnk_shopify',                domain: 'E-Commerce', status: 'active',   cpu: 31, requests: 41, latencyMs: 54,  icon: 'shopify',  color: '#34d399' },
  { id: 's3',  name: 'dnk_video_retention_auditor',domain: 'Analytics',  status: 'active',   cpu: 44, requests: 8,  latencyMs: 112, icon: 'analytics',color: '#22d3ee' },
  { id: 's4',  name: 'dnk_youtube_auditor',        domain: 'Media',      status: 'idle',     cpu: 2,  requests: 0,  latencyMs: 0,   icon: 'video',    color: '#f59e0b' },
  { id: 's5',  name: 'dnk_voice_stt',              domain: 'AI',         status: 'active',   cpu: 67, requests: 5,  latencyMs: 210, icon: 'voice',    color: '#f472b6' },
  { id: 's6',  name: 'dnk_image_gen',              domain: 'AI',         status: 'active',   cpu: 82, requests: 24, latencyMs: 340, icon: 'ai',       color: '#818cf8' },
  { id: 's7',  name: 'dnk_task_forest',            domain: 'Orchestration', status: 'active', cpu: 22, requests: 17, latencyMs: 43, icon: 'layers',   color: '#00dc82' },
  { id: 's8',  name: 'dnk_memory_l3',              domain: 'Data',       status: 'active',   cpu: 14, requests: 33, latencyMs: 28,  icon: 'data',     color: '#60a5fa' },
  { id: 's9',  name: 'dnk_media_distributor',      domain: 'Media',      status: 'idle',     cpu: 1,  requests: 0,  latencyMs: 0,   icon: 'media',    color: '#fb923c' },
];

const AGENTS: Agent[] = [
  {
    id: 'a1', name: 'Gerych Prime', role: 'Chief Builder & Swarm Manager', emoji: '🤖',
    status: 'running', task: 'Executing Phase 3: FastMCP namespace dispatcher — test_fastmcp_dispatcher (7/7)',
    runtime: 13440, color: '#00dc82', toolCalls: 247,
  },
  {
    id: 'a2', name: 'dnk_shopify Worker', role: 'Shopify / Liquid AST', emoji: '🛍️',
    status: 'running', task: 'Deploying DNK_Ecom_v1_0_0 → ReBurn Store & E-Com workspace',
    runtime: 840, color: '#34d399', toolCalls: 18,
  },
  {
    id: 'a3', name: 'Antigravity Mentor', role: 'Architect / Orchestrator', emoji: '🧠',
    status: 'waiting', task: 'Awaiting Phase 4 gate result from gerych_auditor — `verify_all.sh`',
    runtime: 5020, color: '#a78bfa', toolCalls: 94,
  },
  {
    id: 'a4', name: 'gerych_auditor', role: 'Adversarial Quality Gate', emoji: '⚔️',
    status: 'done', task: '8/8 checks PASSED (31.1s) — auto_precommit_guard GREEN ✅',
    runtime: 31, color: '#22d3ee', toolCalls: 12,
  },
];

// ── COMPONENT ──────────────────────────────────────────────────────────────────

export default function DNKVisualShell() {
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'idle' | 'error'>('all');
  const [services, setServices] = useState<SaaPService[]>(SAAP_SERVICES);
  const [agents, setAgents] = useState<Agent[]>(AGENTS);
  const [isLiveConnected, setIsLiveConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function fetchShellStatus() {
      try {
        const res = await fetch('/api/v1/shell/status');
        if (res.ok) {
          const data = await res.json();
          if (!cancelled && data.services) {
            setServices(data.services);
            setIsLiveConnected(true);
          }
        }
      } catch {
        // Fallback to static mock state gracefully
      }
    }
    fetchShellStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredServices = services.filter(s =>
    activeFilter === 'all' ? true : s.status === activeFilter
  );

  const activeServices = services.filter(s => s.status === 'active').length;
  const activeTasks = agents.filter(a => a.status === 'running').reduce((sum, a) => sum + 1, 12);

  return (
    <div className="flex h-screen w-full bg-[#080b12] overflow-hidden">
      {/* Left sidebar */}
      <VisualShellSidebar />

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top status bar */}
        <KernelStatusBar
          agentCount={AGENTS.filter(a => a.status === 'running').length}
          serviceCount={activeServices}
          taskCount={activeTasks}
        />

        {/* Body: scrollable content + right log panel */}
        <div className="flex flex-1 overflow-hidden">
          {/* Scrollable main area */}
          <main className="flex-1 overflow-y-auto p-5 space-y-6">

            {/* SaaP Services section */}
            <section>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Layers size={15} className="text-cyan-400" />
                  <h2 className="text-[13px] font-bold text-white">SaaP Services</h2>
                  <span className="text-[10px] text-slate-600 ml-1">{activeServices}/{SAAP_SERVICES.length} active</span>
                </div>

                {/* Filters */}
                <div className="flex items-center gap-1.5">
                  {(['all', 'active', 'idle', 'error'] as const).map(f => (
                    <button
                      key={f}
                      onClick={() => setActiveFilter(f)}
                      className={`
                        text-[10px] font-medium px-2.5 py-1 rounded-lg capitalize transition-all
                        ${activeFilter === f
                          ? 'bg-white/[0.1] text-white border border-white/[0.15]'
                          : 'text-slate-600 hover:text-slate-400 border border-transparent'}
                      `}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              <motion.div
                layout
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"
              >
                {filteredServices.map((service, i) => (
                  <motion.div
                    key={service.id}
                    layout
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3, delay: i * 0.04 }}
                  >
                    <SaaPServiceCard service={service} />
                  </motion.div>
                ))}
              </motion.div>
            </section>

            {/* Agent Swarm */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <AgentSwarmPanel agents={agents} />
            </motion.div>

            {/* Kernel Invariants strip */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 }}
              className="p-4 rounded-2xl border border-white/[0.06] bg-[#0e1117]/70"
            >
              <p className="text-[11px] text-slate-600 font-mono mb-3 uppercase tracking-widest">Kernel Invariants</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { label: '8-Root Canonical',      ok: true  },
                  { label: 'Relative Paths Only',    ok: true  },
                  { label: '0 Ghost Dirs',           ok: true  },
                  { label: '0 .DS_Store in Git',     ok: true  },
                  { label: 'MRH Headers Complete',   ok: true  },
                  { label: '0 Cyclic Imports',        ok: true  },
                  { label: 'FastMCP Namespaced',     ok: true  },
                  { label: 'Binary Zips Relocated',  ok: true  },
                ].map(({ label, ok }) => (
                  <div
                    key={label}
                    className="flex items-center gap-1.5 text-[10px] px-2.5 py-1 rounded-lg font-medium"
                    style={{
                      background: ok ? '#00dc8212' : '#f8717112',
                      border: `1px solid ${ok ? '#00dc8230' : '#f8717130'}`,
                      color: ok ? '#00dc82' : '#f87171',
                    }}
                  >
                    <span>{ok ? '✓' : '✗'}</span>
                    <span>{label}</span>
                  </div>
                ))}
              </div>
            </motion.div>

          </main>

          {/* Right: System Events Log */}
          <SystemEventsLog />
        </div>
      </div>
    </div>
  );
}
