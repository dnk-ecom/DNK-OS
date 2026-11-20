// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/lib/api/simulation_client.ts"
// purpose: "Client API & SSE Stream adapter for SAAP v1.0 Synthetic Customer Swarm Engine"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (Gerych Prime & Antigravity)"
// --- END DNK-MRH-HEADER ---

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    return window.location.origin.replace(':3000', ':8000');
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export interface ProductSeed {
  title: string;
  price_usd: number;
  description?: string;
  category?: string;
  social_proof_level?: number;
}

export interface FunnelStep {
  step_id: string;
  name: string;
  friction_coefficient?: number;
  trust_requirement?: number;
  required_impulse?: number;
}

export interface GenerateCohortRequest {
  product_seed: ProductSeed;
  cohort_size?: number;
  include_dissent_seats?: boolean;
  target_market?: string;
  seed?: number;
}

export interface CustomerPersonaSummary {
  persona_id: string;
  name: string;
  archetype: string;
  openness_to_buy: number;
  price_elasticity: number;
  skepticism_level: number;
  is_dissent_seat: boolean;
  top_hesitation?: string;
}

export interface GenerateCohortResponse {
  cohort_id: string;
  total_personas: number;
  personas: CustomerPersonaSummary[];
  archetype_breakdown: Record<string, number>;
  generated_at: string;
}

export interface StepEvaluationSummary {
  step_id: string;
  name: string;
  reached_count: number;
  reached_pct: number;
  converted_count: number;
  step_conversion_pct: number;
  drop_off_count: number;
  drop_off_pct: number;
  primary_objections: string[];
}

export interface RunFunnelRequest {
  product_seed: ProductSeed;
  cohort_size?: number;
  include_dissent_seats?: boolean;
  custom_steps?: FunnelStep[];
  seed?: number;
}

export interface RunFunnelResponse {
  simulation_id: string;
  product_title: string;
  cohort_size: number;
  overall_conversion_pct: number;
  final_conversions: number;
  biggest_dropoff_step: string;
  top_objections: string[];
  recommendations: string[];
  step_details: StepEvaluationSummary[];
  created_at: string;
}

export interface SimulationHealthResponse {
  status: string;
  service_id: string;
  version: string;
  engine: string;
  active_simulations: number;
}

export async function getSimulationHealth(): Promise<SimulationHealthResponse> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/v1/simulation/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function generateCohort(req: GenerateCohortRequest): Promise<GenerateCohortResponse> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/v1/simulation/cohort/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Cohort generation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function runFunnelSimulation(req: RunFunnelRequest): Promise<RunFunnelResponse> {
  const base = getApiBaseUrl();
  const res = await fetch(`${base}/api/v1/simulation/funnel/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Funnel simulation failed: ${res.statusText}`);
  }
  return res.json();
}

export interface StreamCallbacks {
  onStarted?: (data: { simulation_id: string; product: string; cohort_size: number; steps_count: number }) => void;
  onStep?: (data: StepEvaluationSummary) => void;
  onCompleted?: (data: { simulation_id: string; overall_conversion_pct: number; top_objections: string[]; recommendations: string[] }) => void;
  onError?: (error: Error) => void;
}

/**
 * Streams funnel simulation steps via SSE from FastAPI backend.
 * Returns an abort function to cancel stream.
 */
export function streamFunnelSimulation(req: RunFunnelRequest, callbacks: StreamCallbacks): () => void {
  const controller = new AbortController();
  const base = getApiBaseUrl();
  const url = `${base}/api/v1/simulation/funnel/stream`;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(req),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`SSE stream request failed: ${response.statusText}`);
      }
      if (!response.body) {
        throw new Error('ReadableStream not supported on response');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          if (!block.trim()) continue;
          let eventType = 'message';
          let eventData = '';

          const rawLines = block.split('\n');
          for (const line of rawLines) {
            if (line.startsWith('event:')) {
              eventType = line.replace('event:', '').trim();
            } else if (line.startsWith('data:')) {
              eventData = line.replace('data:', '').trim();
            }
          }

          if (!eventData) continue;
          try {
            const parsed = JSON.parse(eventData);
            if (eventType === 'started') {
              callbacks.onStarted?.(parsed);
            } else if (eventType === 'step_eval') {
              callbacks.onStep?.(parsed);
            } else if (eventType === 'completed') {
              callbacks.onCompleted?.(parsed);
            }
          } catch (e) {
            console.error('Failed to parse SSE payload', e, eventData);
          }
        }
      }
    })
    .catch((err) => {
      if (err.name === 'AbortError') return;
      callbacks.onError?.(err);
    });

  return () => {
    controller.abort();
  };
}
