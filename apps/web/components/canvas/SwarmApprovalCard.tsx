// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/SwarmApprovalCard.tsx"
// purpose: "Interactive HITL Approval Card for Visual Canvas (SOTA Agent-Native Pattern)"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-21"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Cpu,
  Clock,
  Terminal,
} from 'lucide-react';
import { ApprovalTicket } from '../../ui/hooks/useDualSurfaceActions';

interface SwarmApprovalCardProps {
  ticket: ApprovalTicket;
  onApprove: (ticketId: string) => Promise<boolean>;
  onReject: (ticketId: string, reason: string) => Promise<boolean>;
}

export const SwarmApprovalCard: React.FC<SwarmApprovalCardProps> = ({
  ticket,
  onApprove,
  onReject,
}) => {
  const [showPayload, setShowPayload] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'critical':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded bg-red-950/80 text-red-400 border border-red-700/50">
            <ShieldAlert className="w-3 h-3 text-red-400" /> Critical Risk
          </span>
        );
      case 'high':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded bg-amber-950/80 text-amber-400 border border-amber-700/50">
            <AlertTriangle className="w-3 h-3 text-amber-400" /> High Risk
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded bg-[#162c2f] text-[#35d5d5] border border-[#224447]">
            <ShieldAlert className="w-3 h-3 text-[#35d5d5]" /> Standard Gate
          </span>
        );
    }
  };

  const handleApprove = async () => {
    setIsSubmitting(true);
    await onApprove(ticket.ticket_id);
    setIsSubmitting(false);
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) return;
    setIsSubmitting(true);
    await onReject(ticket.ticket_id, rejectReason);
    setIsSubmitting(false);
    setIsRejecting(false);
  };

  return (
    <div className="w-full max-w-lg rounded-xl bg-[#162c2f] border border-[#224447] shadow-2xl p-4 text-[#d4d8db] flex flex-col gap-3 font-sans transition-all hover:border-[#35d5d5]/50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#224447] pb-2.5">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#22c55e] animate-pulse" />
          <h4 className="text-sm font-semibold tracking-wide text-white uppercase flex items-center gap-1.5">
            <Terminal className="w-4 h-4 text-[#35d5d5]" />
            {ticket.action_id}
          </h4>
        </div>
        {getRiskBadge(ticket.risk_level)}
      </div>

      {/* Description & Agent Meta */}
      <div className="text-xs space-y-1.5">
        <p className="text-gray-300 leading-relaxed">{ticket.description}</p>
        <div className="flex items-center gap-4 text-[11px] text-gray-400 pt-1">
          <span className="flex items-center gap-1">
            <Cpu className="w-3.5 h-3.5 text-[#35d5d5]" /> Agent: <strong className="text-white">{ticket.agent_id}</strong>
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-gray-400" />
            {new Date(ticket.created_at * 1000).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Expandable Payload Inspector */}
      <div className="rounded-lg bg-[#112224] border border-[#224447]/60 overflow-hidden text-xs">
        <button
          onClick={() => setShowPayload(!showPayload)}
          className="w-full flex items-center justify-between px-3 py-1.5 text-gray-300 hover:text-white hover:bg-[#162c2f]/50 transition-colors"
        >
          <span className="font-mono text-[11px] text-gray-400">Payload Parameters</span>
          {showPayload ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
        {showPayload && (
          <pre className="p-2.5 text-[11px] font-mono text-[#35d5d5] overflow-x-auto max-h-40 border-t border-[#224447]/60 bg-[#0d1719]">
            {JSON.stringify(ticket.payload, null, 2)}
          </pre>
        )}
      </div>

      {/* Reject Reason Input (if triggered) */}
      {isRejecting && (
        <div className="space-y-2 pt-1 border-t border-[#224447]">
          <input
            type="text"
            placeholder="Вкажіть причину відхилення..."
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            className="w-full px-3 py-1.5 text-xs rounded bg-[#112224] border border-red-800/60 text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setIsRejecting(false)}
              className="px-2.5 py-1 text-xs rounded hover:bg-white/5 text-gray-400"
            >
              Скасувати
            </button>
            <button
              onClick={handleReject}
              disabled={isSubmitting || !rejectReason.trim()}
              className="px-3 py-1 text-xs rounded bg-red-600 hover:bg-red-500 text-white font-medium disabled:opacity-50"
            >
              Підтвердити відхилення
            </button>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isRejecting && (
        <div className="flex items-center justify-end gap-2.5 pt-1 border-t border-[#224447]">
          <button
            onClick={() => setIsRejecting(true)}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-400 hover:bg-red-950/40 border border-red-800/40 transition-colors disabled:opacity-50"
          >
            <XCircle className="w-3.5 h-3.5" />
            Відхилити
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-semibold text-slate-900 bg-[#35d5d5] hover:bg-[#2bc0c0] shadow-md transition-colors disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-slate-900" />
            Схвалити дію
          </button>
        </div>
      )}
    </div>
  );
};
