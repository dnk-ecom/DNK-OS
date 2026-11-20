// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_docs_components_fumadocs_blocks_tsx"
// purpose: "Fumadocs-inspired Dark Teal interactive components (Steps, Callouts, MilestoneTimeline)"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-23"
// author: "DNK-e.com Maksym & Gerych Prime"
// --- END DNK-MRH-HEADER ---

'use client';

import React from 'react';
import { DocCalloutBlock, DocStepItem, MilestoneItem } from '../types';

export function FumadocsInteractiveBlocks({
  steps,
  callouts,
}: {
  steps: DocStepItem[];
  callouts: DocCalloutBlock[];
}) {
  return (
    <div className="space-y-6 mt-6">
      {/* Callouts */}
      {callouts && callouts.length > 0 && (
        <div className="space-y-3">
          {callouts.map((c, idx) => {
            const borderColors: Record<string, string> = {
              info: 'border-[#35d5d5] bg-[#162c2f]/90 text-[#d4d8db]',
              warning: 'border-amber-400 bg-amber-950/30 text-amber-100',
              success: 'border-[#22c55e] bg-emerald-950/30 text-emerald-100',
              danger: 'border-rose-500 bg-rose-950/30 text-rose-100',
            };
            const styleClass = borderColors[c.type] || borderColors.info;

            return (
              <div
                key={idx}
                className={`rounded-xl border-l-4 border border-[#224447] p-4 shadow-md ${styleClass}`}
              >
                <div className="flex items-center gap-2 font-bold text-sm mb-1">
                  <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#35d5d5]" />
                  <span>{c.title}</span>
                </div>
                <p className="text-xs leading-relaxed text-[#d4d8db]/90">{c.body}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Steps */}
      {steps && steps.length > 0 && (
        <div className="rounded-xl border border-[#224447] bg-[#112224] p-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[#35d5d5] mb-4">
            Interactive Execution Steps (Fumadocs Steps Pattern)
          </h4>
          <div className="relative pl-6 border-l-2 border-[#2a6368] space-y-5">
            {steps.map((s, idx) => (
              <div key={idx} className="relative">
                <span
                  className={`absolute -left-[33px] top-0.5 flex h-6 w-6 items-center justify-center rounded-full border text-xs font-bold ${
                    s.status === 'completed'
                      ? 'bg-[#22c55e] text-[#112224] border-[#22c55e]'
                      : s.status === 'active'
                      ? 'bg-[#112224] text-[#35d5d5] border-[#35d5d5]'
                      : 'bg-[#162c2f] text-[#d4d8db]/60 border-[#224447]'
                  }`}
                >
                  {s.step_number}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">{s.title}</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
                    {s.status}
                  </span>
                </div>
                <div className="text-xs text-[#d4d8db]/80 mt-1">{s.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function MilestoneTimelineView({
  milestones,
  onSignOffMilestone,
  approvingId,
}: {
  milestones: MilestoneItem[];
  onSignOffMilestone: (milestoneId: string, action: 'approve' | 'request_changes') => void;
  approvingId: string | null;
}) {
  if (!milestones || milestones.length === 0) {
    return (
      <div className="p-6 rounded-xl border border-[#224447] bg-[#162c2f] text-sm text-[#d4d8db]/70">
        No milestones found for this project scope.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {milestones.map((ms) => {
        const isApproved = ms.status === 'approved' || ms.status === 'completed';
        const progressPct =
          ms.estimated_hours > 0
            ? Math.min(100, Math.round((ms.spent_hours / ms.estimated_hours) * 100))
            : 0;

        return (
          <div
            key={ms.id}
            className="rounded-xl border border-[#224447] bg-[#162c2f] p-5 shadow-lg transition hover:border-[#2a6368]"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-0.5 text-xs font-bold rounded-md bg-[#112224] text-[#35d5d5] border border-[#224447]">
                    Stage #{ms.stage_number}
                  </span>
                  <h3 className="text-base font-bold text-white">{ms.title}</h3>
                  <span
                    className={`px-2.5 py-0.5 text-[11px] font-semibold rounded-full ${
                      isApproved
                        ? 'bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/40'
                        : ms.status === 'in_progress'
                        ? 'bg-[#35d5d5]/20 text-[#35d5d5] border border-[#35d5d5]/40'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {ms.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-[#d4d8db]/80 mt-1.5">{ms.description}</p>
                <p className="text-xs text-[#d4d8db]/70 mt-1">
                  Hours Budget:{' '}
                  <strong className="text-[#35d5d5]">
                    {ms.spent_hours}h spent / {ms.estimated_hours}h estimated
                  </strong>
                </p>
              </div>

              <div className="flex items-center gap-2">
                {ms.approved_by ? (
                  <span className="text-xs text-[#22c55e] bg-[#112224] px-3 py-1.5 rounded-lg border border-[#22c55e]/30">
                    ✓ Signed Off by {ms.approved_by}
                  </span>
                ) : (
                  <>
                    <button
                      type="button"
                      disabled={approvingId === ms.id}
                      onClick={() => onSignOffMilestone(ms.id, 'approve')}
                      className="px-3.5 py-1.5 rounded-lg bg-[#22c55e] hover:bg-[#16a34a] text-[#112224] font-bold text-xs transition shadow"
                    >
                      {approvingId === ms.id ? 'Signing Off...' : '✓ Sign-Off Stage'}
                    </button>
                    <button
                      type="button"
                      disabled={approvingId === ms.id}
                      onClick={() => onSignOffMilestone(ms.id, 'request_changes')}
                      className="px-3 py-1.5 rounded-lg bg-[#112224] hover:bg-rose-950/60 text-rose-300 border border-rose-500/40 font-semibold text-xs transition"
                    >
                      Request Changes
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-[#d4d8db]/80">Hours Utilization / Stage Progress</span>
                <span className="font-bold text-[#35d5d5]">{progressPct}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#112224] overflow-hidden border border-[#224447]">
                <div
                  className="h-full bg-gradient-to-r from-[#35d5d5] to-[#22c55e] transition-all duration-300"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>

            {/* Deliverables */}
            <div className="mt-4 pt-3 border-t border-[#224447]/80 flex flex-wrap gap-2">
              {(ms.deliverables || []).map((deliv, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2.5 py-1 rounded-md bg-[#112224] text-[#d4d8db] border border-[#224447]"
                >
                  • {deliv}
                </span>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
