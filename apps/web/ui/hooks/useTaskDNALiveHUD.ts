// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/ui/hooks/useTaskDNALiveHUD.ts"
// purpose: "React hook for TaskDNA Anti-Poisoning lifecycle and Live Canvas HUD interactions"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (dnk_dev_fullstack & gerych_builder)"
// --- END DNK-MRH-HEADER ---

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../lib/api';

export type TaskDNAPhase =
  | 'RESEARCH_RAW'
  | 'AUDIT_GATE'
  | 'FOUNDER_APPROVAL'
  | 'LIBRARIAN_INGEST'
  | 'COMPLETED'
  | 'REJECTED';

export interface AuditReport {
  auditor: string;
  security_score: number;
  critical_issues: string[];
  notes?: string;
}

export interface FounderDecision {
  approved: boolean;
  feedback?: string;
  decided_at: string;
}

export interface TaskDNASlice {
  id: string;
  title: string;
  content: string;
  phase: TaskDNAPhase;
  assigned_agent: string;
  depends_on: string[];
  canvas_node_id: string;
  created_at: string;
  updated_at: string;
  audit_report?: AuditReport;
  founder_decision?: FounderDecision;
  ingest_path?: string;
}

export interface TaskDNAListResponse {
  total: number;
  tasks: TaskDNASlice[];
  by_phase: Record<TaskDNAPhase, number>;
}

export interface SyncHUDResponse {
  status: string;
  canvas_file: string;
  nodes_count: number;
  edges_count: number;
  sync_timestamp: string;
}

export function useTaskDNALiveHUD(pollIntervalMs = 5000) {
  const [tasks, setTasks] = useState<TaskDNASlice[]>([]);
  const [byPhase, setByPhase] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [syncingHUD, setSyncingHUD] = useState<boolean>(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setError(null);
      const data = await apiClient.get<TaskDNAListResponse>('/api/v1/taskdna/tasks');
      setTasks(data.tasks);
      setByPhase(data.by_phase);
    } catch (err: any) {
      console.error('Failed to fetch TaskDNA tasks:', err);
      setError(err?.message || 'Error fetching tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
    if (pollIntervalMs > 0) {
      const interval = setInterval(fetchTasks, pollIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchTasks, pollIntervalMs]);

  const submitFounderDecision = async (
    taskId: string,
    approved: boolean,
    feedback?: string
  ): Promise<TaskDNASlice> => {
    try {
      const updated = await apiClient.post<TaskDNASlice>(
        `/api/v1/taskdna/tasks/${taskId}/founder-decision`,
        {
          approved,
          feedback: feedback || (approved ? 'Approved by Founder Maxim' : 'Rejected by Founder Maxim'),
          actor_role: 'maxim_founder',
        }
      );
      // Optimistic state update
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      return updated;
    } catch (err: any) {
      setError(err?.message || 'Failed to submit founder decision');
      throw err;
    }
  };

  const submitAuditVerdict = async (
    taskId: string,
    passed: boolean,
    securityScore = 0.98,
    issues: string[] = []
  ): Promise<TaskDNASlice> => {
    try {
      const updated = await apiClient.post<TaskDNASlice>(
        `/api/v1/taskdna/tasks/${taskId}/audit-verdict`,
        {
          passed,
          security_score: securityScore,
          critical_issues: issues,
          auditor: 'gerych_auditor',
        }
      );
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      return updated;
    } catch (err: any) {
      setError(err?.message || 'Failed to submit audit verdict');
      throw err;
    }
  };

  const completeIngest = async (taskId: string): Promise<TaskDNASlice> => {
    try {
      const updated = await apiClient.post<TaskDNASlice>(
        `/api/v1/taskdna/tasks/${taskId}/complete-ingest`,
        {
          actor_role: 'herich_librarian',
          target_path: `docs/notes/Knowledge/Task_${taskId}.md`,
        }
      );
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      return updated;
    } catch (err: any) {
      setError(err?.message || 'Failed to complete ingest');
      throw err;
    }
  };

  const syncHUD = async (): Promise<SyncHUDResponse> => {
    setSyncingHUD(true);
    try {
      const res = await apiClient.post<SyncHUDResponse>('/api/v1/taskdna/sync-hud', {});
      setLastSyncedAt(res.sync_timestamp);
      await fetchTasks();
      return res;
    } catch (err: any) {
      setError(err?.message || 'Failed to sync HUD');
      throw err;
    } finally {
      setSyncingHUD(false);
    }
  };

  const createSampleTask = async (title: string, content: string): Promise<TaskDNASlice> => {
    try {
      const created = await apiClient.post<TaskDNASlice>('/api/v1/taskdna/tasks', {
        title,
        content,
        creator_role: 'gerych_researcher',
      });
      setTasks((prev) => [created, ...prev]);
      return created;
    } catch (err: any) {
      setError(err?.message || 'Failed to create task');
      throw err;
    }
  };

  return {
    tasks,
    byPhase,
    loading,
    error,
    syncingHUD,
    lastSyncedAt,
    fetchTasks,
    submitFounderDecision,
    submitAuditVerdict,
    completeIngest,
    syncHUD,
    createSampleTask,
  };
}
