// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/hooks/useDualSurfaceAction.ts"
// purpose: "React Hook for invoking Dual-Surface actions from Astryx UI with optimistic UI updates and HITL approval states."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
// --- END DNK-MRH-HEADER ---

'use client';

import { useState, useCallback, useEffect } from 'react';

export interface DualSurfaceActionSpec {
  action_id: string;
  label_uk: string;
  description_en: string;
  surface_mode: 'dual' | 'agent' | 'human';
  mcp_brick: string;
  mcp_tool_name: string;
  input_json_schema: Record<string, any>;
  ui_widget: 'button' | 'approve_reject' | 'diff_viewer' | 'checklist' | 'form_drawer';
  ui_tone: 'primary' | 'secondary' | 'danger' | 'approve';
  requires_human_confirmation: boolean;
  idempotent: boolean;
}

export interface ActionDispatchResult<T = any> {
  action_id: string;
  success: boolean;
  result?: T;
  error?: string;
  requires_approval: boolean;
  ticket_id?: string;
  actor: string;
  origin: string;
  timestamp_epoch: number;
}

export interface UseDualSurfaceActionOptions<T = any> {
  actionId: string;
  apiBaseUrl?: string;
  defaultActor?: string;
  onSuccess?: (result: ActionDispatchResult<T>) => void;
  onError?: (error: string) => void;
}

export function useDualSurfaceAction<T = any>({
  actionId,
  apiBaseUrl = '',
  defaultActor = 'Maksym (Astryx UI)',
  onSuccess,
  onError,
}: UseDualSurfaceActionOptions<T>) {
  const [isPending, setIsPending] = useState(false);
  const [isAwaitingApproval, setIsAwaitingApproval] = useState(false);
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const execute = useCallback(
    async (payload: Record<string, any> = {}, actor = defaultActor, sessionId = 'sess_ui_default') => {
      setIsPending(true);
      setError(null);
      setIsAwaitingApproval(false);
      setTicketId(null);

      try {
        const response = await fetch(`${apiBaseUrl}/api/v1/actions/dispatch`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action_id: actionId,
            payload,
            actor,
            session_id: sessionId,
          }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: 'Network error' }));
          throw new Error(errData.detail || `Action dispatch failed with HTTP ${response.status}`);
        }

        const dispatchResult: ActionDispatchResult<T> = await response.json();

        if (dispatchResult.requires_approval) {
          setIsAwaitingApproval(true);
          setTicketId(dispatchResult.ticket_id || null);
        } else if (dispatchResult.success) {
          setData(dispatchResult.result ?? null);
          onSuccess?.(dispatchResult);
        } else {
          throw new Error(dispatchResult.error || 'Action execution failed');
        }

        return dispatchResult;
      } catch (err: any) {
        const msg = err.message || 'Unknown action execution error';
        setError(msg);
        onError?.(msg);
        return null;
      } finally {
        setIsPending(false);
      }
    },
    [actionId, apiBaseUrl, defaultActor, onSuccess, onError]
  );

  return {
    execute,
    isPending,
    isAwaitingApproval,
    ticketId,
    error,
    data,
  };
}

export function useDualSurfaceActionCatalog(apiBaseUrl = '') {
  const [actions, setActions] = useState<DualSurfaceActionSpec[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadCatalog() {
      setLoading(true);
      try {
        const res = await fetch(`${apiBaseUrl}/api/v1/actions`);
        if (!res.ok) throw new Error(`Failed to fetch catalog: ${res.status}`);
        const data = await res.json();
        if (!cancelled) setActions(data);
      } catch (e: any) {
        if (!cancelled) setError(e.message || 'Error loading action catalog');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadCatalog();
    return () => {
      cancelled = true;
    };
  }, [apiBaseUrl]);

  return { actions, loading, error };
}
