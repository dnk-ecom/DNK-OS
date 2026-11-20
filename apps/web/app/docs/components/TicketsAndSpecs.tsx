// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_docs_components_tickets_and_specs_tsx"
// purpose: "Interactive Client Specification Builder & Ticket Sign-Off Cards with TaskDNA Auto-Conversion"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-23"
// author: "DNK-e.com Maksym & Gerych Prime"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState } from 'react';
import { ClientTicketItem } from '../types';

export function TicketCardsList({
  tickets,
  onSignOffTicket,
  onCompleteSwarm,
  onSyncObsidian,
  actionLoadingId,
}: {
  tickets: ClientTicketItem[];
  onSignOffTicket: (
    ticketId: string,
    action: 'approve' | 'request_changes',
    comment?: string
  ) => void;
  onCompleteSwarm: (ticketId: string) => void;
  onSyncObsidian: (ticketId: string) => void;
  actionLoadingId: string | null;
}) {
  const [commentInputs, setCommentInputs] = useState<Record<string, string>>({});

  if (!tickets || tickets.length === 0) {
    return (
      <div className="p-6 rounded-xl border border-[#224447] bg-[#162c2f] text-sm text-[#d4d8db]/70">
        No specification tickets found for this workspace. Create one using the Specification Builder!
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {tickets.map((t) => {
        const isApproved = t.status === 'approved' || t.status === 'completed';
        const isChangesRequested = t.status === 'changes_requested';

        return (
          <div
            key={t.id}
            className="rounded-xl border border-[#224447] bg-[#162c2f] p-5 shadow-lg transition hover:border-[#35d5d5]/50"
          >
            {/* Header */}
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-[#112224] text-[#35d5d5] border border-[#224447]">
                    {t.id}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#112224] text-amber-300 border border-amber-500/30 font-bold uppercase">
                    {t.priority}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#112224] text-[#d4d8db] border border-[#224447]">
                    {t.category}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#112224] text-[#35d5d5] border border-[#2a6368]">
                    Agent: {t.assigned_agent}
                  </span>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                      isApproved
                        ? 'bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/40'
                        : isChangesRequested
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                        : 'bg-[#35d5d5]/20 text-[#35d5d5] border border-[#35d5d5]/40'
                    }`}
                  >
                    {t.status.toUpperCase()}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mt-2">{t.title}</h3>
              </div>

              {/* Time & Sign-Off Controls */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="text-xs bg-[#112224] px-3 py-1.5 rounded-lg border border-[#224447] text-[#d4d8db]">
                  ⏱ <strong className="text-[#35d5d5]">{t.spent_hours}h</strong> / {t.estimated_hours}h est.
                </div>
                <button
                  type="button"
                  disabled={actionLoadingId === t.id}
                  onClick={() => {
                    onSignOffTicket(t.id, 'approve', commentInputs[t.id] || undefined);
                    setCommentInputs({ ...commentInputs, [t.id]: '' });
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-[#22c55e] hover:bg-[#16a34a] text-[#112224] font-bold text-xs transition shadow"
                >
                  {actionLoadingId === t.id
                    ? 'Converting...'
                    : isApproved
                    ? '✓ Re-Sync Swarm DNA'
                    : '✓ Approve & Launch Swarm'}
                </button>
                <button
                  type="button"
                  disabled={actionLoadingId === t.id}
                  onClick={() => {
                    onSignOffTicket(
                      t.id,
                      'request_changes',
                      commentInputs[t.id] || 'Requested adjustments to specification scope.'
                    );
                    setCommentInputs({ ...commentInputs, [t.id]: '' });
                  }}
                  className="px-3 py-1.5 rounded-lg bg-[#112224] hover:bg-rose-950/60 text-rose-300 border border-rose-500/40 font-semibold text-xs transition"
                >
                  Request Changes
                </button>
              </div>
            </div>

            {/* Description / Business Goal */}
            <p className="text-sm text-[#d4d8db]/90 mt-3 bg-[#112224]/70 p-3 rounded-lg border border-[#224447]">
              <strong className="text-[#35d5d5]">Specification Scope: </strong>
              {t.description}
            </p>

            {/* TaskDNA / TaskForest Link Badge when approved */}
            {(t.taskdna_id || t.taskforest_node_id) && (
              <div className="mt-3 flex flex-wrap items-center gap-3 p-2.5 rounded-lg bg-[#112224] border border-[#22c55e]/40 text-xs">
                <span className="inline-block w-2 h-2 rounded-full bg-[#22c55e]" />
                <span className="text-[#22c55e] font-semibold">
                  Swarm Auto-Converted:
                </span>
                {t.taskdna_id && (
                  <span className="font-mono px-2 py-0.5 rounded bg-[#162c2f] text-[#35d5d5]">
                    TaskDNA: {t.taskdna_id}
                  </span>
                )}
                {t.taskforest_node_id && (
                  <span className="font-mono px-2 py-0.5 rounded bg-[#162c2f] text-[#22c55e]">
                    Node: {t.taskforest_node_id}
                  </span>
                )}
                <span className="font-mono px-2 py-0.5 rounded bg-[#162c2f] text-[#d4d8db]/80 text-[11px]">
                  Obsidian: docs/notes/projects/{t.project_id}/{t.id}.md
                </span>

                <div className="ml-auto flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onSyncObsidian(t.id)}
                    className="px-2.5 py-1 rounded bg-[#2a6368] hover:bg-[#35d5d5] hover:text-[#112224] text-white text-[11px] font-semibold transition"
                  >
                    Sync Obsidian
                  </button>
                  {t.status !== 'completed' && (
                    <button
                      type="button"
                      disabled={actionLoadingId === t.id}
                      onClick={() => onCompleteSwarm(t.id)}
                      className="px-2.5 py-1 rounded bg-[#22c55e] hover:bg-[#16a34a] text-[#112224] text-[11px] font-bold transition shadow"
                    >
                      ✓ Complete Swarm (100%)
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Acceptance Criteria & Scope Grids */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 text-xs">
              <div className="p-3 rounded-lg bg-[#112224] border border-[#224447]">
                <div className="font-bold text-[#35d5d5] mb-1.5">
                  ✓ Acceptance Criteria (DoD)
                </div>
                <ul className="space-y-1 text-[#d4d8db]/90 list-disc list-inside">
                  {(t.acceptance_criteria || []).map((ac, idx) => (
                    <li key={idx}>{ac}</li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-lg bg-[#112224] border border-[#224447]">
                <div className="font-bold text-[#22c55e] mb-1.5">
                  Target File Whitelist
                </div>
                <ul className="space-y-1 font-mono text-[11px] text-[#d4d8db]/90">
                  {(t.target_file_whitelist || []).map((f, idx) => (
                    <li key={idx} className="truncate">
                      + {f}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-lg bg-[#112224] border border-[#224447]">
                <div className="font-bold text-rose-400 mb-1.5">
                  Negative Scope (Do NOT Touch)
                </div>
                <ul className="space-y-1 font-mono text-[11px] text-[#d4d8db]/90">
                  {(t.negative_scope || []).map((ns, idx) => (
                    <li key={idx} className="truncate">
                      - {ns}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Comments & Feedback Input */}
            <div className="mt-4 pt-3 border-t border-[#224447]">
              {t.comments && t.comments.length > 0 && (
                <div className="space-y-2 mb-3">
                  {t.comments.map((c) => (
                    <div
                      key={c.id}
                      className="text-xs bg-[#112224] px-3 py-2 rounded-lg border border-[#224447] flex items-start justify-between gap-2"
                    >
                      <div>
                        <span className="font-bold text-[#35d5d5]">{c.author}</span>{' '}
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#162c2f] text-[#d4d8db]/70">
                          {c.role}
                        </span>
                        : <span className="text-[#d4d8db] ml-1">{c.text}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="text"
                  value={commentInputs[t.id] || ''}
                  onChange={(e) =>
                    setCommentInputs({ ...commentInputs, [t.id]: e.target.value })
                  }
                  placeholder="Optional sign-off note or change request comment..."
                  className="flex-1 rounded-lg bg-[#112224] border border-[#224447] px-3 py-1.5 text-xs text-white placeholder-[#d4d8db]/40 focus:outline-none focus:border-[#35d5d5]"
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function NewSpecificationForm({
  activeProjectId,
  onCreateTicket,
  submitting,
}: {
  activeProjectId: string;
  onCreateTicket: (payload: {
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
  }) => void;
  submitting: boolean;
}) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('specification');
  const [priority, setPriority] = useState('high');
  const [estimatedHours, setEstimatedHours] = useState(6);
  const [assignedAgent, setAssignedAgent] = useState('dnk_shopify');
  const [description, setDescription] = useState('');
  const [acText, setAcText] = useState(
    'Mobile sticky CTA renders under 50ms\nZero CLS layout shift on Dawn/Horizon\nVerified 100% Green in verify_all.sh'
  );
  const [whitelistText, setWhitelistText] = useState(
    'services/dnk_shopify/DNK-e.com/blocks/_custom-feature.liquid\nservices/dnk_shopify/DNK-e.com/templates/product.json'
  );
  const [negativeScopeText, setNegativeScopeText] = useState(
    'Do not modify core checkout logic\nDo not install paid third-party scripts'
  );
  const [alsoCreateDocPage, setAlsoCreateDocPage] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    onCreateTicket({
      project_id: activeProjectId,
      title: title.trim(),
      description: description.trim(),
      category,
      priority,
      estimated_hours: Number(estimatedHours) || 4,
      assigned_agent: assignedAgent,
      acceptance_criteria: acText
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      target_file_whitelist: whitelistText
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      negative_scope: negativeScopeText
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      also_create_doc_page: alsoCreateDocPage,
    });
    setTitle('');
    setDescription('');
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-xl border border-[#224447] bg-[#162c2f] p-6 shadow-lg space-y-4"
    >
      <div className="flex items-center justify-between border-b border-[#224447] pb-3">
        <div>
          <h3 className="text-base font-bold text-white">
            Interactive Client Specification & Ticket Builder
          </h3>
          <p className="text-xs text-[#d4d8db]/70">
            Structured GERYCH_TASK_TEMPLATE v2.5 builder · Persists to apps/api JSON SSOT & Page Tree
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-[#112224] text-[#35d5d5] border border-[#224447]">
          Project: {activeProjectId}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
            Feature / Specification Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Native 3-Tier Bundle & Save PDP Widget"
            className="w-full rounded-lg bg-[#112224] border border-[#224447] px-3 py-2 text-sm text-white focus:outline-none focus:border-[#35d5d5]"
          />
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full rounded-lg bg-[#112224] border border-[#224447] px-2.5 py-2 text-xs text-white"
            >
              <option value="specification">Specification</option>
              <option value="cro_block">CRO Block</option>
              <option value="feature">Feature</option>
              <option value="integration">Integration</option>
              <option value="bugfix">Bugfix</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full rounded-lg bg-[#112224] border border-[#224447] px-2.5 py-2 text-xs text-white"
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
              Est. Hours
            </label>
            <input
              type="number"
              min={1}
              max={200}
              value={estimatedHours}
              onChange={(e) => setEstimatedHours(Number(e.target.value))}
              className="w-full rounded-lg bg-[#112224] border border-[#224447] px-2.5 py-2 text-xs text-white"
            />
          </div>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
          Business Goal & Specification Description (Why & What) *
        </label>
        <textarea
          rows={2}
          required
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what conversion metric or user workflow this specification improves..."
          className="w-full rounded-lg bg-[#112224] border border-[#224447] px-3 py-2 text-sm text-white focus:outline-none focus:border-[#35d5d5]"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-[#35d5d5] mb-1">
            Acceptance Criteria (1 per line)
          </label>
          <textarea
            rows={3}
            value={acText}
            onChange={(e) => setAcText(e.target.value)}
            className="w-full rounded-lg bg-[#112224] border border-[#224447] p-2.5 text-xs font-mono text-[#d4d8db]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#22c55e] mb-1">
            Target File Whitelist (1 per line)
          </label>
          <textarea
            rows={3}
            value={whitelistText}
            onChange={(e) => setWhitelistText(e.target.value)}
            className="w-full rounded-lg bg-[#112224] border border-[#224447] p-2.5 text-xs font-mono text-[#d4d8db]"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-rose-400 mb-1">
            Negative Scope (Do NOT touch)
          </label>
          <textarea
            rows={3}
            value={negativeScopeText}
            onChange={(e) => setNegativeScopeText(e.target.value)}
            className="w-full rounded-lg bg-[#112224] border border-[#224447] p-2.5 text-xs font-mono text-[#d4d8db]"
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-[#224447]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#d4d8db]">Swarm Worker:</span>
            <select
              value={assignedAgent}
              onChange={(e) => setAssignedAgent(e.target.value)}
              className="rounded bg-[#112224] border border-[#224447] px-2.5 py-1 text-xs text-[#35d5d5] font-mono"
            >
              <option value="dnk_shopify">dnk_shopify (Liquid/CRO)</option>
              <option value="gerych_builder">gerych_builder (React/UI)</option>
              <option value="dnk_dev_fullstack">dnk_dev_fullstack (FastAPI/DB)</option>
              <option value="dnk_video_ai_creator">dnk_video_ai_creator (Media)</option>
            </select>
          </div>

          <label className="flex items-center gap-2 text-xs text-[#d4d8db] cursor-pointer">
            <input
              type="checkbox"
              checked={alsoCreateDocPage}
              onChange={(e) => setAlsoCreateDocPage(e.target.checked)}
              className="h-4 w-4 accent-[#22c55e]"
            />
            <span>Also publish interactive Fumadocs Spec Page (.md) in Page Tree</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="px-5 py-2 rounded-lg bg-[#35d5d5] hover:bg-[#2bc0c0] text-[#112224] font-bold text-xs transition shadow-md"
        >
          {submitting
            ? 'Creating Specification...'
            : '+ Create Specification & Ticket'}
        </button>
      </div>
    </form>
  );
}
