// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/lib/api/mvr_stream_client.ts"
// purpose: "SSOT W3C Resilient SSE Stream Client & REST API for MVR Core, Last-Event-ID catch-up, and HITL"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-12"
// author: "Gerych Builder & dnk_dev_fullstack"
// --- END DNK-MRH-HEADER ---

import { useEffect, useRef, useState, useCallback } from 'react';
import {
  StreamEnvelope,
  MvrStreamClientOptions,
  HitlApprovalRequest,
  HitlApprovalDecisionPayload,
  CanvasNodeMovePayload,
  CanvasBatchMutationPayload,
} from '../../types/mvrTypes';

const STORAGE_KEY_LAST_EVENT_ID = 'dnk_mvr_last_event_id';

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    return window.location.origin.replace(':3000', ':8000');
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export class MvrStreamClient {
  private baseUrl: string;
  private lastEventId: string | null = null;
  private eventSource: EventSource | null = null;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private currentBackoffMs: number = 1000;
  private maxBackoffMs: number = 10000;
  private isManuallyClosed: boolean = false;
  private options: MvrStreamClientOptions;

  constructor(options: MvrStreamClientOptions = {}) {
    this.options = options;
    this.baseUrl = options.baseUrl || getApiBaseUrl();
    this.maxBackoffMs = options.maxReconnectIntervalMs || 10000;
    this.currentBackoffMs = options.reconnectIntervalMs || 1000;

    if (options.lastEventId) {
      this.lastEventId = options.lastEventId;
    } else if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        this.lastEventId = sessionStorage.getItem(STORAGE_KEY_LAST_EVENT_ID);
      } catch (e) {
        // Ignore session storage errors
      }
    }
  }

  public getLastEventId(): string | null {
    return this.lastEventId;
  }

  public setLastEventId(id: string): void {
    this.lastEventId = id;
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        sessionStorage.setItem(STORAGE_KEY_LAST_EVENT_ID, id);
      } catch (e) {
        // Ignore session storage errors
      }
    }
  }

  public connect(): void {
    if (typeof window === 'undefined') return;
    this.isManuallyClosed = false;

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    const query = this.lastEventId ? `?last_event_id=${encodeURIComponent(this.lastEventId)}` : '';
    const url = `${this.baseUrl}/api/v1/mvr/events/sse${query}`;

    try {
      this.eventSource = new EventSource(url);

      this.eventSource.onopen = () => {
        this.currentBackoffMs = this.options.reconnectIntervalMs || 1000;
        if (this.options.onConnect) {
          this.options.onConnect();
        }
      };

      this.eventSource.onmessage = (event: MessageEvent) => {
        if (!event.data) return;
        try {
          const envelope: StreamEnvelope = JSON.parse(event.data);
          if (envelope && envelope.event_id) {
            this.setLastEventId(envelope.event_id);
          }
          if (this.options.onEvent) {
            this.options.onEvent(envelope);
          }
        } catch (err) {
          // Non-JSON comments (like keep-alives) are ignored
        }
      };

      this.eventSource.onerror = (err: Event) => {
        if (this.options.onError) {
          this.options.onError(err);
        }
        if (this.options.onDisconnect) {
          this.options.onDisconnect();
        }
        if (!this.isManuallyClosed) {
          this.scheduleReconnect();
        }
      };
    } catch (e) {
      if (this.options.onError && e instanceof Error) {
        this.options.onError(e);
      }
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.isManuallyClosed) return;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      this.currentBackoffMs = Math.min(this.currentBackoffMs * 1.5, this.maxBackoffMs);
      this.connect();
    }, this.currentBackoffMs);
  }

  public disconnect(): void {
    this.isManuallyClosed = true;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.options.onDisconnect) {
      this.options.onDisconnect();
    }
  }
}

// REST API Helpers
export async function fetchPendingApprovals(baseUrl: string = getApiBaseUrl()): Promise<HitlApprovalRequest[]> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/approvals/pending`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch pending approvals: ${res.statusText}`);
  }
  const data = await res.json();
  return data.pending_approvals || [];
}

export async function submitApprovalDecision(
  requestId: string,
  payload: HitlApprovalDecisionPayload,
  baseUrl: string = getApiBaseUrl()
): Promise<any> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/approvals/${encodeURIComponent(requestId)}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to submit approval decision: ${res.statusText}`);
  }
  return res.json();
}

export async function sendCanvasNodeMove(
  payload: CanvasNodeMovePayload,
  baseUrl: string = getApiBaseUrl()
): Promise<any> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/canvas/node-move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to send node move: ${res.statusText}`);
  }
  return res.json();
}

export async function sendCanvasBatchMutation(
  payload: CanvasBatchMutationPayload,
  baseUrl: string = getApiBaseUrl()
): Promise<any> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/canvas/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to send canvas batch mutation: ${res.statusText}`);
  }
  return res.json();
}

export async function pruneMvrArtifacts(
  maxAgeSeconds: number = 14 * 86400,
  baseUrl: string = getApiBaseUrl()
): Promise<{ pruned_count: number }> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/artifacts/prune?max_age_seconds=${maxAgeSeconds}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to prune artifacts: ${res.statusText}`);
  }
  return res.json();
}

export interface LaunchSimulationPayload {
  scenario?: string;
  canvas_id?: string;
  target_audience?: string;
  step_delay_seconds?: number;
  auto_approve_after_seconds?: number;
}

export async function launchSwarmSimulation(
  payload: LaunchSimulationPayload = {},
  baseUrl: string = getApiBaseUrl()
): Promise<any> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/simulation/launch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to launch simulation: ${res.statusText}`);
  }
  return res.json();
}

export async function abortSwarmSimulation(
  simulationId: string,
  baseUrl: string = getApiBaseUrl()
): Promise<any> {
  const res = await fetch(`${baseUrl}/api/v1/mvr/simulation/${simulationId}/abort`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to abort simulation: ${res.statusText}`);
  }
  return res.json();
}

// React Hook for SSE
export function useMvrStream(options: MvrStreamClientOptions = {}) {
  const [connected, setConnected] = useState<boolean>(false);
  const [lastEnvelope, setLastEnvelope] = useState<StreamEnvelope | null>(null);
  const clientRef = useRef<MvrStreamClient | null>(null);

  useEffect(() => {
    const client = new MvrStreamClient({
      ...options,
      onConnect: () => {
        setConnected(true);
        if (options.onConnect) options.onConnect();
      },
      onDisconnect: () => {
        setConnected(false);
        if (options.onDisconnect) options.onDisconnect();
      },
      onEvent: (envelope) => {
        setLastEnvelope(envelope);
        if (options.onEvent) options.onEvent(envelope);
      },
    });

    clientRef.current = client;
    client.connect();

    return () => {
      client.disconnect();
    };
  }, [options.baseUrl, options.lastEventId]);

  return {
    connected,
    lastEnvelope,
    client: clientRef.current,
  };
}
