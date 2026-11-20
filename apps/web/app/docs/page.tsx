// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_docs_page_tsx"
// purpose: "Tri-Audience Documentation & Client Delivery Portal UI (Fumadocs UI + Fern RBAC + /llms.txt + TaskDNA Auto-Conversion)"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-23"
// author: "DNK-e.com Maksym & Gerych Prime"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AudienceRole, DocPageItem, PortalWorkspaceBundle } from './types';
import { FumadocsInteractiveBlocks, MilestoneTimelineView } from './components/FumadocsBlocks';
import { TicketCardsList, NewSpecificationForm } from './components/TicketsAndSpecs';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function TriAudienceDocsPortalPage() {
  // Auth & RBAC State
  const [token, setToken] = useState<string>('');
  const [authUser, setAuthUser] = useState<{
    id: string;
    email: string;
    name: string;
    role: AudienceRole;
    project_ids: string[];
  } | null>(null);

  // Login Modal / Form State
  const [loginEmail, setLoginEmail] = useState('maxim@dnk-e.com');
  const [loginPassword, setLoginPassword] = useState('dnk-god-2026');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // God Mode "View As" Context Switcher
  const [viewAsRole, setViewAsRole] = useState<AudienceRole>('god');
  const [activeProjectId, setActiveProjectId] = useState<string>('m-craft-shopify');

  // Portal Data State
  const [portalState, setPortalState] = useState<PortalWorkspaceBundle | null>(null);
  const [selectedSlug, setSelectedSlug] = useState<string>('internal-swarm-sop');
  const [activeLayoutTab, setActiveLayoutTab] = useState<
    'docs' | 'milestones' | 'tickets' | 'builder' | 'agent_feed'
  >('docs');
  const [llmsTxtContent, setLlmsTxtContent] = useState<string>('');
  const [rawPageMd, setRawPageMd] = useState<string>('');
  const [showRawMdModal, setShowRawMdModal] = useState<boolean>(false);

  // Loading & Feedback State
  const [loadingPortal, setLoadingPortal] = useState<boolean>(true);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [submittingSpec, setSubmittingSpec] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((prev) => (prev === msg ? null : prev));
    }, 5000);
  };

  // Perform Login against POST /api/v1/docs/auth/login
  const performLogin = useCallback(async (email: string, password: string) => {
    setIsLoggingIn(true);
    setLoginError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/docs/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
        throw new Error(err.detail || 'Authentication failed');
      }
      const data = await res.json();
      setToken(data.access_token);
      setAuthUser(data.user);
      setViewAsRole(data.user.role as AudienceRole);

      const defaultProj =
        data.user.project_ids &&
        data.user.project_ids.length > 0 &&
        data.user.project_ids[0] !== '*'
          ? data.user.project_ids[0]
          : 'm-craft-shopify';
      setActiveProjectId(defaultProj);
      setShowLoginModal(false);
      showToast(`Authenticated as ${data.user.name} (${data.user.role.toUpperCase()})`);
    } catch (err: any) {
      setLoginError(err.message || 'Login failed');
    } finally {
      setIsLoggingIn(false);
    }
  }, []);

  useEffect(() => {
    performLogin('maxim@dnk-e.com', 'dnk-god-2026');
  }, [performLogin]);

  // Fetch Portal State whenever token, activeProjectId, or viewAsRole changes
  const fetchPortalData = useCallback(async () => {
    if (!token) return;
    setLoadingPortal(true);
    try {
      const params = new URLSearchParams();
      params.set('project_id', activeProjectId);
      if (authUser?.role === 'god') {
        params.set('view_as_role', viewAsRole);
      }

      const res = await fetch(`${API_BASE}/api/v1/docs/portal?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load portal workspace bundle');
      const data: PortalWorkspaceBundle = await res.json();
      setPortalState(data);

      // Keep selectedSlug valid within filtered page_tree
      if (data.page_tree.length > 0) {
        const exists = data.page_tree.some((p) => p.slug === selectedSlug);
        if (!exists) {
          setSelectedSlug(data.page_tree[0].slug);
        }
      }
    } catch (err: any) {
      console.error('Error loading portal:', err);
    } finally {
      setLoadingPortal(false);
    }
  }, [token, authUser, viewAsRole, activeProjectId, selectedSlug]);

  useEffect(() => {
    if (token) {
      fetchPortalData();
    }
  }, [token, viewAsRole, activeProjectId, fetchPortalData]);

  // Fetch /llms.txt whenever Agent Feed tab is active or viewAsRole === 'agent'
  const fetchLlmsTxt = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/docs/llms.txt?project_id=${encodeURIComponent(activeProjectId)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.ok) {
        const txt = await res.text();
        setLlmsTxtContent(txt);
      }
    } catch (e) {
      console.error('Failed to fetch llms.txt:', e);
    }
  }, [token, activeProjectId]);

  useEffect(() => {
    if (activeLayoutTab === 'agent_feed' || viewAsRole === 'agent') {
      fetchLlmsTxt();
    }
  }, [activeLayoutTab, viewAsRole, fetchLlmsTxt]);

  // Fetch single page .md endpoint
  const handleInspectRawMd = async (slug: string, pageProjectId: string) => {
    try {
      const targetProj =
        pageProjectId === 'internal-god' ? activeProjectId : pageProjectId;
      const res = await fetch(
        `${API_BASE}/api/v1/docs/raw/${slug}.md?project_id=${encodeURIComponent(targetProj)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.ok) {
        const txt = await res.text();
        setRawPageMd(txt);
        setShowRawMdModal(true);
      } else {
        showToast('RBAC Access Denied for this Markdown endpoint in current role.');
      }
    } catch (e) {
      showToast('Error fetching raw .md endpoint');
    }
  };

  // Ticket Sign-Off / Convert to TaskDNA
  const handleSignOffTicket = async (
    ticketId: string,
    action: 'approve' | 'request_changes',
    comment?: string
  ) => {
    setActionLoadingId(ticketId);
    try {
      const res = await fetch(`${API_BASE}/api/v1/docs/tickets/${ticketId}/signoff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          action,
          comment,
          auto_convert_taskdna: action === 'approve',
        }),
      });
      if (!res.ok) throw new Error('Failed to sign off ticket');
      const data = await res.json();
      if (action === 'approve' && data.taskdna_conversion) {
        showToast(
          `✓ Approved! Auto-created TaskDNA (${data.taskdna_conversion.taskdna_id}) & TaskForest Node (${data.taskdna_conversion.taskforest_node_id})`
        );
      } else {
        showToast(`Updated ticket ${ticketId}: ${action.toUpperCase()}`);
      }
      await fetchPortalData();
      if (activeLayoutTab === 'agent_feed') {
        await fetchLlmsTxt();
      }
    } catch (e: any) {
      showToast(e.message || 'Error updating ticket');
    } finally {
      setActionLoadingId(null);
    }
  };

  // Create New Specification Ticket
  const handleCreateSpecification = async (payload: {
    project_id: string;
    title: string;
    description: string;
    category: string;
    priority: string;
    estimated_hours: number;
    assigned_agent: string;
    target_file_whitelist: string[];
    negative_scope: string[];
    acceptance_criteria: string[];
    also_create_doc_page: boolean;
  }) => {
    setSubmittingSpec(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/docs/tickets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to create specification ticket');
      const data = await res.json();
      showToast(`✓ Specification & Ticket ${data.ticket.id} created!`);
      await fetchPortalData();
      setActiveLayoutTab('tickets');
    } catch (e: any) {
      showToast(e.message || 'Failed to create specification');
    } finally {
      setSubmittingSpec(false);
    }
  };

  // Complete Swarm Simulation or Live Worker Hook
  const handleCompleteSwarm = async (ticketId: string) => {
    setActionLoadingId(ticketId);
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/docs/tickets/${ticketId}/complete-swarm?commit_sha=feat_${Date.now()}`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (res.ok) {
        showToast(`✓ Swarm completed ticket ${ticketId} (100% Green & Synced to TaskForest + Obsidian)!`);
        await fetchPortalData();
      }
    } catch (e) {
      showToast('Failed to complete swarm ticket');
    } finally {
      setActionLoadingId(null);
    }
  };

  // Manual Obsidian Sync
  const handleSyncObsidian = async (ticketId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/docs/tickets/${ticketId}/sync-obsidian`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`✓ Synced to Obsidian Vault: ${data.obsidian_path}`);
      }
    } catch (e) {
      showToast('Failed to sync to Obsidian');
    }
  };

  // Sign-off Milestone
  const handleSignOffMilestone = async (
    milestoneId: string,
    action: 'approve' | 'request_changes'
  ) => {
    setActionLoadingId(milestoneId);
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/docs/milestones/${milestoneId}/signoff`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ action }),
        }
      );
      if (res.ok) {
        showToast(`✓ Milestone ${milestoneId} ${action.toUpperCase()}!`);
        await fetchPortalData();
      }
    } catch (e) {
      showToast('Failed to update milestone');
    } finally {
      setActionLoadingId(null);
    }
  };

  const currentDocPage: DocPageItem | undefined =
    portalState?.page_tree.find((p) => p.slug === selectedSlug) ||
    portalState?.page_tree[0];

  // Group page tree by category (Fumadocs sidebar style)
  const groupedPages: Record<string, DocPageItem[]> = {};
  (portalState?.page_tree || []).forEach((p) => {
    if (!groupedPages[p.category]) groupedPages[p.category] = [];
    groupedPages[p.category].push(p);
  });

  return (
    <div className="min-h-screen bg-[#1e2022] text-[#d4d8db] flex flex-col font-sans">
      {/* Top Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 rounded-xl bg-[#112224] border-2 border-[#35d5d5] px-4 py-3 text-xs font-bold text-white shadow-2xl flex items-center gap-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#22c55e]" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* TOP BAR: Brand + View As Switcher + Auth Session */}
      <header className="sticky top-0 z-30 border-b border-[#224447] bg-[#112224]/95 backdrop-blur px-6 py-3">
        <div className="max-w-[1600px] mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Left: Title & Fumadocs/Fern Badge */}
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-[#162c2f] border border-[#35d5d5] flex items-center justify-center font-black text-[#35d5d5] text-sm shadow">
              DNK
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm md:text-base font-extrabold text-white tracking-tight">
                  DNK OS · Tri-Audience Docs & Client Delivery Portal
                </h1>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
                  Fumadocs UI + Fern RBAC
                </span>
              </div>
              <p className="text-[11px] text-[#d4d8db]/70">
                Server-Side RBAC Filtered · Native <code className="text-[#35d5d5]">/llms.txt</code> &{' '}
                <code className="text-[#35d5d5]">*.md</code> · Auto TaskDNA Dispatch
              </p>
            </div>
          </div>

          {/* Center: "View As" Switcher (God Mode / Agent Feed / Client Workspaces) */}
          <div className="flex flex-wrap items-center gap-2 bg-[#162c2f] px-3 py-1.5 rounded-xl border border-[#224447]">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#35d5d5]">
              View As:
            </span>

            <button
              type="button"
              onClick={() => {
                if (authUser?.role !== 'god') {
                  performLogin('maxim@dnk-e.com', 'dnk-god-2026');
                } else {
                  setViewAsRole('god');
                }
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                portalState?.effective_role === 'god'
                  ? 'bg-[#35d5d5] text-[#112224] shadow'
                  : 'text-[#d4d8db] hover:text-white'
              }`}
            >
              👑 God Mode
            </button>

            <button
              type="button"
              onClick={() => {
                if (authUser?.role === 'god') {
                  setViewAsRole('agent');
                  setActiveLayoutTab('agent_feed');
                } else {
                  performLogin('agent@dnk-e.com', 'dnk-agent-2026');
                  setActiveLayoutTab('agent_feed');
                }
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                portalState?.effective_role === 'agent'
                  ? 'bg-[#35d5d5] text-[#112224] shadow'
                  : 'text-[#d4d8db] hover:text-white'
              }`}
            >
              🤖 Agent Feed (/llms.txt)
            </button>

            <button
              type="button"
              onClick={() => {
                if (authUser?.role === 'god') {
                  setViewAsRole('client');
                  setActiveProjectId('m-craft-shopify');
                } else {
                  performLogin('client@m-craft.com', 'mcraft-client-2026');
                }
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                portalState?.effective_role === 'client' &&
                activeProjectId === 'm-craft-shopify'
                  ? 'bg-[#22c55e] text-[#112224] shadow'
                  : 'text-[#d4d8db] hover:text-white'
              }`}
            >
              🏢 Client: M-Craft
            </button>

            <button
              type="button"
              onClick={() => {
                if (authUser?.role === 'god') {
                  setViewAsRole('client');
                  setActiveProjectId('ascendify-cro');
                } else {
                  performLogin('client@ascendify.io', 'ascendify-2026');
                }
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                portalState?.effective_role === 'client' &&
                activeProjectId === 'ascendify-cro'
                  ? 'bg-[#22c55e] text-[#112224] shadow'
                  : 'text-[#d4d8db] hover:text-white'
              }`}
            >
              🏢 Client: Ascendify
            </button>
          </div>

          {/* Right: Authenticated User & Login Switch */}
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-white flex items-center gap-1.5 justify-end">
                <span className="h-2 w-2 rounded-full bg-[#22c55e]" />
                <span>{authUser?.name || 'Guest'}</span>
              </div>
              <div className="text-[10px] font-mono text-[#35d5d5]">
                Effective Role: {portalState?.effective_role.toUpperCase()} · Project:{' '}
                {activeProjectId}
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowLoginModal(true)}
              className="px-3 py-1.5 rounded-lg bg-[#162c2f] hover:bg-[#224447] text-xs font-semibold text-[#35d5d5] border border-[#2a6368] transition"
            >
              🔐 Switch Login
            </button>
          </div>
        </div>
      </header>

      {/* SUB-HEADER: Fumadocs Layout Context Tabs */}
      <div className="border-b border-[#224447] bg-[#162c2f]/80 px-6">
        <div className="max-w-[1600px] mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-1 overflow-x-auto py-2">
            <button
              type="button"
              onClick={() => setActiveLayoutTab('docs')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                activeLayoutTab === 'docs'
                  ? 'bg-[#112224] text-[#35d5d5] border border-[#35d5d5]/50'
                  : 'text-[#d4d8db]/80 hover:text-white'
              }`}
            >
              📚 Documentation & Interactive Guides ({portalState?.page_tree.length || 0})
            </button>

            <button
              type="button"
              onClick={() => setActiveLayoutTab('milestones')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                activeLayoutTab === 'milestones'
                  ? 'bg-[#112224] text-[#35d5d5] border border-[#35d5d5]/50'
                  : 'text-[#d4d8db]/80 hover:text-white'
              }`}
            >
              🗺️ Milestone Roadmap ({portalState?.milestones.length || 0})
            </button>

            <button
              type="button"
              onClick={() => setActiveLayoutTab('tickets')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                activeLayoutTab === 'tickets'
                  ? 'bg-[#112224] text-[#35d5d5] border border-[#35d5d5]/50'
                  : 'text-[#d4d8db]/80 hover:text-white'
              }`}
            >
              🎫 Specifications & Sign-Off Tickets ({portalState?.tickets.length || 0})
            </button>

            <button
              type="button"
              onClick={() => setActiveLayoutTab('builder')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                activeLayoutTab === 'builder'
                  ? 'bg-[#22c55e] text-[#112224]'
                  : 'bg-[#112224]/60 text-[#22c55e] border border-[#22c55e]/30 hover:bg-[#112224]'
              }`}
            >
              + New Specification / Ticket
            </button>

            <button
              type="button"
              onClick={() => setActiveLayoutTab('agent_feed')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition ${
                activeLayoutTab === 'agent_feed'
                  ? 'bg-[#112224] text-[#35d5d5] border border-[#35d5d5]/50'
                  : 'text-[#d4d8db]/80 hover:text-white'
              }`}
            >
              🤖 Live /llms.txt Agent Contract
            </button>
          </div>

          <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono text-[#d4d8db]/70">
            <span className="px-2 py-0.5 rounded bg-[#112224] border border-[#224447] text-[#22c55e]">
              RBAC Isolated: {portalState?.rbac_isolation_verified ? 'STRICT CLIENT/AGENT' : 'GOD FULL ACCESS'}
            </span>
          </div>
        </div>
      </div>

      {/* MAIN 3-COLUMN FUMADOCS + FERN PORTAL WORKSPACE */}
      <div className="flex-1 max-w-[1600px] w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 p-6">
        {/* LEFT SIDEBAR: Filtered Page Tree Navigation */}
        <aside className="lg:col-span-3 space-y-5">
          <div className="rounded-xl border border-[#224447] bg-[#162c2f] p-4 shadow-lg">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#224447]">
              <span className="text-xs font-bold uppercase tracking-wider text-[#35d5d5]">
                Page Tree ({portalState?.effective_role.toUpperCase()})
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#112224] text-[#d4d8db]">
                {activeProjectId}
              </span>
            </div>

            {loadingPortal ? (
              <div className="text-xs text-[#d4d8db]/60 py-4">Loading Page Tree...</div>
            ) : (
              <div className="space-y-4">
                {Object.entries(groupedPages).map(([category, pages]) => (
                  <div key={category}>
                    <div className="text-[11px] font-bold uppercase tracking-wider text-[#d4d8db]/50 mb-1.5 px-2">
                      {category}
                    </div>
                    <div className="space-y-1">
                      {pages.map((page) => {
                        const isSelected =
                          page.slug === currentDocPage?.slug && activeLayoutTab === 'docs';
                        return (
                          <button
                            key={page.id}
                            type="button"
                            onClick={() => {
                              setSelectedSlug(page.slug);
                              setActiveLayoutTab('docs');
                            }}
                            className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition flex items-center justify-between gap-2 ${
                              isSelected
                                ? 'bg-[#112224] text-[#35d5d5] border border-[#35d5d5]/50 font-bold'
                                : 'text-[#d4d8db] hover:bg-[#112224]/60 hover:text-white'
                            }`}
                          >
                            <span className="truncate">{page.title}</span>
                            {page.visibility === 'god_only' && (
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                                GOD
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Project Summary Card */}
          <div className="rounded-xl border border-[#224447] bg-[#112224] p-4 space-y-3 text-xs">
            <div className="font-bold text-[#35d5d5] uppercase tracking-wider">
              Project Budget & Telemetry
            </div>
            <div className="flex justify-between">
              <span className="text-[#d4d8db]/70">Hours Spent / Est:</span>
              <strong className="text-white">
                {portalState?.metrics.spent_hours_total || 0}h /{' '}
                {portalState?.metrics.estimated_hours_total || 0}h
              </strong>
            </div>
            <div className="flex justify-between">
              <span className="text-[#d4d8db]/70">Milestones Approved:</span>
              <strong className="text-white">
                {portalState?.metrics.milestones_approved || 0} /{' '}
                {portalState?.metrics.milestones_total || 0}
              </strong>
            </div>
            <div className="flex justify-between">
              <span className="text-[#d4d8db]/70">Tickets Approved:</span>
              <strong className="text-[#35d5d5]">
                {portalState?.metrics.tickets_approved || 0} /{' '}
                {portalState?.metrics.tickets_total || 0}
              </strong>
            </div>
            <div className="flex justify-between">
              <span className="text-[#d4d8db]/70">Active TaskDNA Queue:</span>
              <strong className="text-[#22c55e]">
                {portalState?.metrics.taskdna_ready_count || 0}
              </strong>
            </div>
          </div>
        </aside>

        {/* CENTER CONTENT AREA */}
        <main className="lg:col-span-9 space-y-6">
          {/* TAB 1: DOCUMENTATION & INTERACTIVE BLOCKS */}
          {activeLayoutTab === 'docs' && currentDocPage && (
            <div className="rounded-xl border border-[#224447] bg-[#162c2f] p-6 shadow-xl">
              <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b border-[#224447]">
                <div>
                  <div className="flex items-center gap-2 text-xs text-[#35d5d5] font-mono">
                    <span>{currentDocPage.category}</span>
                    <span>/</span>
                    <span>{currentDocPage.slug}</span>
                  </div>
                  <h2 className="text-xl font-extrabold text-white mt-1">
                    {currentDocPage.title}
                  </h2>
                  <p className="text-xs text-[#d4d8db]/80 mt-1">{currentDocPage.summary}</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() =>
                      handleInspectRawMd(currentDocPage.slug, currentDocPage.project_id)
                    }
                    className="px-3 py-1.5 rounded-lg bg-[#112224] hover:bg-[#224447] text-xs font-mono text-[#35d5d5] border border-[#2a6368] transition"
                  >
                    📄 View /raw/{currentDocPage.slug}.md
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveLayoutTab('builder')}
                    className="px-3 py-1.5 rounded-lg bg-[#22c55e] hover:bg-[#16a34a] text-xs font-bold text-[#112224] transition"
                  >
                    + Create Spec Ticket
                  </button>
                </div>
              </div>

              {/* Rendered Markdown Content */}
              <div className="mt-5">
                <div className="rounded-xl bg-[#112224]/90 border border-[#224447] p-5 text-sm leading-relaxed whitespace-pre-wrap text-[#d4d8db]">
                  {currentDocPage.content_md}
                </div>
              </div>

              {/* Fumadocs Interactive Component Blocks */}
              <FumadocsInteractiveBlocks
                steps={currentDocPage.steps || []}
                callouts={currentDocPage.callouts || []}
              />

              {/* Target File Whitelist & Negative Scope Footer */}
              {(currentDocPage.target_file_whitelist.length > 0 ||
                currentDocPage.negative_scope.length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-5 border-t border-[#224447]">
                  <div className="rounded-xl bg-[#112224] border border-[#224447] p-4">
                    <div className="text-xs font-bold text-[#22c55e] mb-2">
                      ✓ Sanctioned Target File Whitelist
                    </div>
                    <ul className="space-y-1 font-mono text-xs text-[#d4d8db]">
                      {currentDocPage.target_file_whitelist.map((f, i) => (
                        <li key={i}>+ {f}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="rounded-xl bg-[#112224] border border-[#224447] p-4">
                    <div className="text-xs font-bold text-rose-400 mb-2">
                      ✕ Negative Scope (Strictly Protected)
                    </div>
                    <ul className="space-y-1 font-mono text-xs text-[#d4d8db]">
                      {currentDocPage.negative_scope.map((f, i) => (
                        <li key={i}>- {f}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: MILESTONE ROADMAP */}
          {activeLayoutTab === 'milestones' && (
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-extrabold text-white">
                  Interactive Milestone Roadmap & Sign-Off Tracker
                </h2>
                <p className="text-xs text-[#d4d8db]/70">
                  Real-time delivery stages, hours budget, and client approval checkpoints
                </p>
              </div>
              <MilestoneTimelineView
                milestones={portalState?.milestones || []}
                onSignOffMilestone={handleSignOffMilestone}
                approvingId={actionLoadingId}
              />
            </div>
          )}

          {/* TAB 3: CLIENT SPECIFICATION TICKETS & SIGN-OFF */}
          {activeLayoutTab === 'tickets' && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-extrabold text-white">
                    Project Specifications & Swarm Delivery Tickets
                  </h2>
                  <p className="text-xs text-[#d4d8db]/70">
                    Clicking &ldquo;Approve & Launch Swarm&rdquo; automatically synthesizes a TaskDNA contract & TaskForest Flower node
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveLayoutTab('builder')}
                  className="px-4 py-2 rounded-lg bg-[#35d5d5] text-[#112224] font-bold text-xs"
                >
                  + New Specification Ticket
                </button>
              </div>

              <TicketCardsList
                tickets={portalState?.tickets || []}
                onSignOffTicket={handleSignOffTicket}
                onCompleteSwarm={handleCompleteSwarm}
                onSyncObsidian={handleSyncObsidian}
                actionLoadingId={actionLoadingId}
              />
            </div>
          )}

          {/* TAB 4: INTERACTIVE SPECIFICATION BUILDER */}
          {activeLayoutTab === 'builder' && (
            <NewSpecificationForm
              activeProjectId={activeProjectId}
              onCreateTicket={handleCreateSpecification}
              submitting={submittingSpec}
            />
          )}

          {/* TAB 5: AGENT-NATIVE /llms.txt STREAM */}
          {activeLayoutTab === 'agent_feed' && (
            <div className="rounded-xl border border-[#224447] bg-[#162c2f] p-6 shadow-xl space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#224447] pb-3">
                <div>
                  <h2 className="text-base font-extrabold text-white flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#22c55e]" />
                    <span>Agent-Native /llms.txt & TaskDNA Feed (Fern Pattern)</span>
                  </h2>
                  <p className="text-xs text-[#d4d8db]/70">
                    Zero-HTML Markdown index consumed by gerych_builder, dnk_shopify, and dnk_dev_fullstack in &lt;10ms
                  </p>
                </div>
                <button
                  type="button"
                  onClick={fetchLlmsTxt}
                  className="px-3 py-1.5 rounded-lg bg-[#112224] hover:bg-[#224447] text-xs font-mono text-[#35d5d5] border border-[#2a6368]"
                >
                  ↻ Refresh /llms.txt
                </button>
              </div>

              <pre className="rounded-xl bg-[#112224] border border-[#224447] p-4 text-xs font-mono text-[#35d5d5] overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-[640px] overflow-y-auto">
                {llmsTxtContent || 'Loading /api/v1/docs/llms.txt...'}
              </pre>
            </div>
          )}
        </main>
      </div>

      {/* MODAL 1: FULL LOGIN / PASSWORD AUTHENTICATION */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-2xl border border-[#35d5d5] bg-[#112224] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#224447] pb-3">
              <h3 className="text-base font-bold text-white">
                🔐 Portal Login (Full Email + Password RBAC)
              </h3>
              <button
                type="button"
                onClick={() => setShowLoginModal(false)}
                className="text-xs text-[#d4d8db]/70 hover:text-white"
              >
                ✕ Close
              </button>
            </div>

            {loginError && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-500 text-xs text-rose-200">
                {loginError}
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                performLogin(loginEmail, loginPassword);
              }}
              className="space-y-3"
            >
              <div>
                <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full rounded-lg bg-[#162c2f] border border-[#224447] px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full rounded-lg bg-[#162c2f] border border-[#224447] px-3 py-2 text-xs text-white"
                />
              </div>

              <button
                type="submit"
                disabled={isLoggingIn}
                className="w-full py-2 rounded-lg bg-[#35d5d5] text-[#112224] font-bold text-xs hover:bg-[#2bc0c0] transition"
              >
                {isLoggingIn ? 'Signing In...' : 'Sign In'}
              </button>
            </form>

            {/* Quick Fill Presets for Testing */}
            <div className="pt-3 border-t border-[#224447] space-y-2">
              <div className="text-[11px] text-[#d4d8db]/70 font-semibold">
                Quick Credential Presets:
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    setLoginEmail('maxim@dnk-e.com');
                    setLoginPassword('dnk-god-2026');
                  }}
                  className="p-2 rounded bg-[#162c2f] hover:bg-[#224447] text-left border border-[#224447]"
                >
                  <div className="font-bold text-[#35d5d5]">👑 maxim@dnk-e.com</div>
                  <div className="text-[#d4d8db]/60">God Mode (All)</div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setLoginEmail('client@m-craft.com');
                    setLoginPassword('mcraft-client-2026');
                  }}
                  className="p-2 rounded bg-[#162c2f] hover:bg-[#224447] text-left border border-[#224447]"
                >
                  <div className="font-bold text-[#22c55e]">🏢 client@m-craft.com</div>
                  <div className="text-[#d4d8db]/60">Client: m-craft-shopify</div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setLoginEmail('client@ascendify.io');
                    setLoginPassword('ascendify-2026');
                  }}
                  className="p-2 rounded bg-[#162c2f] hover:bg-[#224447] text-left border border-[#224447]"
                >
                  <div className="font-bold text-[#22c55e]">🏢 client@ascendify.io</div>
                  <div className="text-[#d4d8db]/60">Client: ascendify-cro</div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setLoginEmail('agent@dnk-e.com');
                    setLoginPassword('dnk-agent-2026');
                  }}
                  className="p-2 rounded bg-[#162c2f] hover:bg-[#224447] text-left border border-[#224447]"
                >
                  <div className="font-bold text-[#35d5d5]">🤖 agent@dnk-e.com</div>
                  <div className="text-[#d4d8db]/60">Agent Mode (/llms.txt)</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: RAW MARKDOWN (*.md) ENDPOINT VIEWER */}
      {showRawMdModal && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4">
          <div className="w-full max-w-3xl rounded-2xl border border-[#35d5d5] bg-[#112224] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#224447] pb-3">
              <h3 className="text-sm font-bold font-mono text-[#35d5d5]">
                GET /api/v1/docs/raw/{currentDocPage?.slug}.md
              </h3>
              <button
                type="button"
                onClick={() => setShowRawMdModal(false)}
                className="text-xs text-[#d4d8db]/70 hover:text-white"
              >
                ✕ Close
              </button>
            </div>
            <pre className="rounded-xl bg-[#162c2f] border border-[#224447] p-4 text-xs font-mono text-[#d4d8db] overflow-x-auto whitespace-pre-wrap max-h-[500px] overflow-y-auto">
              {rawPageMd}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
