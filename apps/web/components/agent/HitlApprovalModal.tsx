// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_agent_HitlApprovalModal"
// purpose: "Meta Astryx 1-Click Human-in-the-Loop (HITL) approval modal for safe agent execution."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  ChevronRight, 
  SlidersHorizontal 
} from 'lucide-react';

export interface HitlTicketData {
  ticket_id: string;
  session_id: string;
  agent: string;
  action_type: string;
  details: Record<string, any>;
  options?: string[];
  timeout_seconds?: number;
}

interface HitlApprovalModalProps {
  ticket: HitlTicketData;
  onResolve: (decision: { approved: boolean; reason?: string; modifications?: Record<string, any> }) => void;
  isSubmitting?: boolean;
}

export function HitlApprovalModal({ ticket, onResolve, isSubmitting = false }: HitlApprovalModalProps) {
  const [reason, setReason] = useState('');
  const [showModifications, setShowModifications] = useState(false);
  const [modsJson, setModsJson] = useState('{}');

  const handleApprove = () => {
    let modifications: Record<string, any> | undefined = undefined;
    if (showModifications) {
      try {
        modifications = JSON.parse(modsJson);
      } catch (e) {
        alert('Invalid JSON in modifications payload');
        return;
      }
    }
    onResolve({ approved: true, modifications });
  };

  const handleReject = () => {
    onResolve({ approved: false, reason: reason || 'Rejected by user via Astryx HUD' });
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in"
      data-agent-target="hitl-approval-modal"
      data-ticket-id={ticket.ticket_id}
    >
      <div className="w-full max-w-lg rounded-2xl border border-amber-500/40 bg-zinc-950 p-6 shadow-2xl shadow-amber-500/10 space-y-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">
                Human-in-the-Loop Gateway
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full border border-border text-muted-foreground">
                {ticket.ticket_id}
              </span>
            </div>
            <h2 className="text-lg font-bold tracking-tight text-foreground mt-0.5">
              Схвалення Дії: {ticket.action_type}
            </h2>
            <p className="text-xs text-muted-foreground">
              Агент <strong className="text-cyan-400 font-mono">{ticket.agent}</strong> запитує підтвердження на виконання.
            </p>
          </div>
        </div>

        {/* Details preview */}
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">
            Параметри операції:
          </span>
          <pre className="p-3 rounded-xl bg-black/60 border border-border/60 text-xs font-mono text-zinc-300 max-h-48 overflow-y-auto">
            {JSON.stringify(ticket.details, null, 2)}
          </pre>
        </div>

        {/* Optional Modifications toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowModifications(!showModifications)}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors font-medium"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            {showModifications ? 'Сховати модифікацію параметрів' : 'Підкоригувати параметри (Advanced)'}
          </button>
          
          {showModifications && (
            <textarea
              value={modsJson}
              onChange={(e) => setModsJson(e.target.value)}
              placeholder="Введіть валідний JSON з переозначенням параметрів..."
              rows={3}
              className="mt-2 w-full p-2.5 rounded-lg bg-black/70 border border-border text-xs font-mono text-emerald-300 focus:outline-none focus:border-emerald-500"
            />
          )}
        </div>

        {/* Rejection reason input */}
        <div>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Причина відхилення або корекція (опціонально)..."
            className="w-full px-3 py-2 rounded-lg bg-black/50 border border-border text-xs text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:border-amber-500/60"
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-border/40">
          <button
            type="button"
            onClick={handleReject}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-xl border border-red-500/40 text-red-400 font-medium text-xs hover:bg-red-950/30 active:scale-95 transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            Відхилити
          </button>

          <button
            type="button"
            onClick={handleApprove}
            disabled={isSubmitting}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-900/30 active:scale-95 transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            {isSubmitting ? 'Схвалення...' : '1-Click Схвалити'}
          </button>
        </div>
      </div>
    </div>
  );
}
