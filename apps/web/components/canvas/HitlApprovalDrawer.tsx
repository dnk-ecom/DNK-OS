// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_HitlApprovalDrawer"
// purpose: "Operator Cockpit Drawer for reviewing pending HITL approval requests, inspecting blast radius diffs, and 1-Click execution"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  FileCode2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';
import { useMvrCanvasStore } from '../../store/mvrCanvasStore';
import { HitlApprovalRequest } from '../../types/mvrTypes';
import { useDualSurfaceActions } from '../../ui/hooks/useDualSurfaceActions';
import { SwarmApprovalCard } from './SwarmApprovalCard';

interface HitlApprovalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HitlApprovalDrawer: React.FC<HitlApprovalDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  const { pendingApprovals: mvrApprovals, approveRequest, rejectRequest, isSubmittingDecision } =
    useMvrCanvasStore();
  const {
    pendingApprovals: swarmApprovals,
    approveTicket,
    rejectTicket,
  } = useDualSurfaceActions();
  const [expandedDiffs, setExpandedDiffs] = useState<Record<string, boolean>>({});
  const [rejectReasons, setRejectReasons] = useState<Record<string, string>>({});
  const [activeRejectingId, setActiveRejectingId] = useState<string | null>(null);

  if (!isOpen) return null;

  const totalPending = mvrApprovals.length + swarmApprovals.length;

  const toggleDiff = (requestId: string) => {
    setExpandedDiffs((prev) => ({
      ...prev,
      [requestId]: !prev[requestId],
    }));
  };

  const handleApprove = async (requestId: string) => {
    try {
      await approveRequest(requestId);
    } catch (err) {
      console.error('[HitlDrawer] Approve error:', err);
    }
  };

  const handleConfirmReject = async (requestId: string) => {
    const reason = rejectReasons[requestId] || 'Rejected by Operator via Cockpit Drawer';
    try {
      await rejectRequest(requestId, reason);
      setActiveRejectingId(null);
    } catch (err) {
      console.error('[HitlDrawer] Reject error:', err);
    }
  };

  return (
    <aside
      aria-label="HITL Approval Gateway Drawer"
      className="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-slate-800 bg-slate-950/95 shadow-2xl backdrop-blur-xl transition-all duration-300 ease-in-out"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 px-5 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/40">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">HITL Gateway</h3>
            <p className="text-xs text-slate-400">
              {totalPending}{' '}
              {totalPending === 1 ? 'action requires' : 'actions require'} verification
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* List of Pending Approvals */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {/* Render Swarm Dual-Surface Tickets */}
        {swarmApprovals.map((ticket) => (
          <SwarmApprovalCard
            key={ticket.ticket_id}
            ticket={ticket}
            onApprove={approveTicket}
            onReject={rejectTicket}
          />
        ))}

        {totalPending === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-3">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h4 className="text-sm font-medium text-slate-200">All Systems Clear</h4>
            <p className="mt-1 text-xs text-slate-400 max-w-xs">
              No pending swarm actions require human-in-the-loop intervention.
            </p>
          </div>
        ) : (
          mvrApprovals.map((req: HitlApprovalRequest) => (
            <div
              key={req.request_id}
              className="rounded-xl border border-slate-800/90 bg-slate-900/80 p-4 shadow-lg transition-all"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold border ${
                      req.risk_level === 'critical'
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                        : req.risk_level === 'high'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                    }`}
                  >
                    <AlertTriangle className="h-3 w-3" />
                    {req.risk_level.toUpperCase()} RISK
                  </span>
                  <h4 className="mt-2 text-sm font-medium text-slate-100">
                    {req.description}
                  </h4>
                </div>
              </div>

              {/* Action ID & Timestamp */}
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-3">
                <span>Action: {req.action_id.slice(0, 12)}</span>
                <span>{new Date(req.created_at).toLocaleTimeString()}</span>
              </div>

              {/* Affected Files */}
              {req.affected_files && req.affected_files.length > 0 && (
                <div className="mb-3">
                  <div className="text-[11px] font-medium text-slate-400 mb-1.5 flex items-center gap-1">
                    <FileCode2 className="h-3 w-3 text-indigo-400" />
                    Blast Radius ({req.affected_files.length} files):
                  </div>
                  <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
                    {req.affected_files.map((file, idx) => (
                      <span
                        key={idx}
                        className="rounded bg-slate-800/80 px-2 py-0.5 text-[11px] font-mono text-slate-300 border border-slate-700/50"
                      >
                        {file}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Diff Preview Accordion */}
              {req.diff_preview && (
                <div className="mb-3">
                  <button
                    onClick={() => toggleDiff(req.request_id)}
                    className="flex w-full items-center justify-between rounded bg-slate-950/60 px-2.5 py-1.5 text-xs text-slate-400 hover:text-slate-200 border border-slate-800/80"
                  >
                    <span>Inspect Code Diff</span>
                    {expandedDiffs[req.request_id] ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                  </button>
                  {expandedDiffs[req.request_id] && (
                    <pre className="mt-1.5 max-h-48 overflow-x-auto rounded bg-slate-950 p-2.5 font-mono text-[11px] text-slate-300 border border-slate-800/80">
                      {req.diff_preview}
                    </pre>
                  )}
                </div>
              )}

              {/* Rejection Reason Form */}
              {activeRejectingId === req.request_id && (
                <div className="mb-3 rounded-lg bg-slate-950/80 p-2.5 border border-rose-900/40">
                  <label className="block text-[11px] font-medium text-rose-300 mb-1">
                    Reason for rejection:
                  </label>
                  <input
                    type="text"
                    value={rejectReasons[req.request_id] || ''}
                    onChange={(e) =>
                      setRejectReasons((prev) => ({
                        ...prev,
                        [req.request_id]: e.target.value,
                      }))
                    }
                    placeholder="E.g., Potential security vulnerability in query"
                    className="w-full rounded bg-slate-900 border border-slate-700 px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                  />
                  <div className="mt-2 flex justify-end gap-2">
                    <button
                      onClick={() => setActiveRejectingId(null)}
                      className="px-2 py-1 text-xs text-slate-400 hover:text-slate-200"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleConfirmReject(req.request_id)}
                      disabled={isSubmittingDecision}
                      className="rounded bg-rose-600 px-3 py-1 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
                    >
                      Confirm Reject
                    </button>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              {activeRejectingId !== req.request_id && (
                <div className="flex gap-2 pt-2 border-t border-slate-800/60">
                  <button
                    onClick={() => handleApprove(req.request_id)}
                    disabled={isSubmittingDecision}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3 py-2 text-xs font-semibold text-white shadow-lg shadow-emerald-950/40 transition-all disabled:opacity-50"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    Approve Action
                  </button>
                  <button
                    onClick={() => setActiveRejectingId(req.request_id)}
                    disabled={isSubmittingDecision}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-rose-950/50 hover:bg-rose-900/60 border border-rose-800/60 px-3 py-2 text-xs font-semibold text-rose-300 transition-all disabled:opacity-50"
                  >
                    <XCircle className="h-4 w-4" />
                    Reject
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </aside>
  );
};
