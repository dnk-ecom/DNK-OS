// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/ui/hooks/useDualSurfaceActions.ts"
// purpose: "React Hook for Dual-Surface Actions and Swarm HITL Approvals (BuilderIO Agent-Native Pattern)"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-21"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import { useState, useEffect, useCallback } from 'react';

export interface DualSurfaceActionMeta {
  id: string;
  title: string;
  description: string;
  is_dangerous: boolean;
  tags: string[];
  service_id: string;
  schema: Record<string, any>;
}

export interface ApprovalTicket {
  ticket_id: string;
  action_id: string;
  payload: Record<string, any>;
  agent_id: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  created_at: number;
  decided_at?: number;
  decided_by?: string;
  rejection_reason?: string;
}

export interface ActionExecutionResponse {
  success: boolean;
  result?: any;
  error?: string;
  requires_approval?: boolean;
  approval_ticket_id?: string;
}

export function useDualSurfaceActions() {
  const [actions, setActions] = useState<Record<string, DualSurfaceActionMeta>>({});
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalTicket[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchManifest = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/actions/manifest');
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setActions(data.actions || {});
    } catch (err: any) {
      console.error('Failed to load dual-surface actions manifest:', err);
    }
  }, []);

  const fetchPendingApprovals = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/approvals?status=pending');
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setPendingApprovals(data.tickets || []);
    } catch (err: any) {
      console.error('Failed to load pending approvals:', err);
    }
  }, []);

  useEffect(() => {
    fetchManifest();
    fetchPendingApprovals();
    const interval = setInterval(fetchPendingApprovals, 5000);
    return () => clearInterval(interval);
  }, [fetchManifest, fetchPendingApprovals]);

  const executeAction = async (
    actionId: string,
    payload: Record<string, any> = {},
    bypassApproval = false
  ): Promise<ActionExecutionResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/actions/execute/${actionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload, bypass_approval: bypassApproval }),
      });
      const data = await res.json();
      if (data.requires_approval) {
        await fetchPendingApprovals();
      }
      return data;
    } catch (err: any) {
      const msg = err.message || 'Execution error';
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setIsLoading(false);
    }
  };

  const approveTicket = async (ticketId: string, decidedBy = 'Maxim') => {
    try {
      const res = await fetch(`/api/v1/approvals/${ticketId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decided_by: decidedBy }),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      await fetchPendingApprovals();
      return true;
    } catch (err: any) {
      console.error(`Failed to approve ticket ${ticketId}:`, err);
      return false;
    }
  };

  const rejectTicket = async (ticketId: string, reason: string, decidedBy = 'Maxim') => {
    try {
      const res = await fetch(`/api/v1/approvals/${ticketId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decided_by: decidedBy, reason }),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      await fetchPendingApprovals();
      return true;
    } catch (err: any) {
      console.error(`Failed to reject ticket ${ticketId}:`, err);
      return false;
    }
  };

  return {
    actions,
    pendingApprovals,
    isLoading,
    error,
    executeAction,
    approveTicket,
    rejectTicket,
    refreshApprovals: fetchPendingApprovals,
    refreshManifest: fetchManifest,
  };
}
