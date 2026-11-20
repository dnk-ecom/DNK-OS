// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_nodes_CustomerSwarmNode"
// purpose: "Visual Canvas Spatial Node for SAAP v1.0 Synthetic Customer Swarm & Live Funnel Simulation HUD"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (Gerych Prime & Antigravity)"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  Users,
  Play,
  RotateCcw,
  Sparkles,
  ShieldAlert,
  AlertCircle,
  TrendingDown,
  TrendingUp,
  CheckCircle2,
  DollarSign,
  Activity,
  Layers,
  ChevronDown,
  ChevronUp,
  Sliders,
  Cpu
} from 'lucide-react';
import {
  ProductSeed,
  StepEvaluationSummary,
  streamFunnelSimulation,
  runFunnelSimulation,
  RunFunnelResponse,
} from '../../../lib/api/simulation_client';

export interface CustomerSwarmNodeData {
  title?: string;
  productTitle?: string;
  priceUsd?: number;
  socialProofLevel?: number;
  cohortSize?: number;
  includeDissentSeats?: boolean;
  status?: 'idle' | 'simulating' | 'completed' | 'error';
  funnelSteps?: StepEvaluationSummary[];
  overallConversionPct?: number;
  topObjections?: string[];
  recommendations?: string[];
  dissentSeatSummary?: {
    name: string;
    hesitation: string;
    objection: string;
  };
}

export default function CustomerSwarmNode({ data, selected }: NodeProps) {
  const initialData = (data || {}) as CustomerSwarmNodeData;

  const [productTitle, setProductTitle] = useState(initialData.productTitle || 'Minimalist Titanium Watch');
  const [priceUsd, setPriceUsd] = useState(initialData.priceUsd ?? 120.0);
  const [cohortSize, setCohortSize] = useState(initialData.cohortSize ?? 50);
  const [includeDissentSeats, setIncludeDissentSeats] = useState(initialData.includeDissentSeats ?? true);

  const [status, setStatus] = useState<'idle' | 'simulating' | 'completed' | 'error'>(initialData.status || 'idle');
  const [steps, setSteps] = useState<StepEvaluationSummary[]>(initialData.funnelSteps || []);
  const [overallConversion, setOverallConversion] = useState<number | null>(initialData.overallConversionPct ?? null);
  const [topObjections, setTopObjections] = useState<string[]>(initialData.topObjections || []);
  const [recommendations, setRecommendations] = useState<string[]>(initialData.recommendations || []);
  const [activeTab, setActiveTab] = useState<'funnel' | 'objections' | 'settings'>('funnel');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const abortStreamRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    return () => {
      if (abortStreamRef.current) {
        abortStreamRef.current();
      }
    };
  }, []);

  const handleRunSimulation = useCallback(() => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
    }

    setStatus('simulating');
    setSteps([]);
    setOverallConversion(null);
    setTopObjections([]);
    setRecommendations([]);
    setErrorMessage(null);

    const productSeed: ProductSeed = {
      title: productTitle,
      price_usd: Number(priceUsd),
      social_proof_level: 0.85,
    };

    const stopStream = streamFunnelSimulation(
      {
        product_seed: productSeed,
        cohort_size: Number(cohortSize),
        include_dissent_seats: includeDissentSeats,
      },
      {
        onStarted: (startData) => {
          setStatus('simulating');
        },
        onStep: (stepData) => {
          setSteps((prev) => {
            const idx = prev.findIndex((s) => s.step_id === stepData.step_id);
            if (idx >= 0) {
              const updated = [...prev];
              updated[idx] = stepData;
              return updated;
            }
            return [...prev, stepData];
          });
        },
        onCompleted: (summary) => {
          setStatus('completed');
          setOverallConversion(summary.overall_conversion_pct);
          setTopObjections(summary.top_objections);
          setRecommendations(summary.recommendations);
        },
        onError: async (err) => {
          console.warn('SSE stream fallback to batch REST call:', err);
          // Fallback to direct REST run if SSE fails
          try {
            const res = await runFunnelSimulation({
              product_seed: productSeed,
              cohort_size: Number(cohortSize),
              include_dissent_seats: includeDissentSeats,
            });
            setSteps(res.step_details || []);
            setOverallConversion(res.overall_conversion_pct);
            setTopObjections(res.top_objections);
            setRecommendations(res.recommendations);
            setStatus('completed');
          } catch (restErr: any) {
            setStatus('error');
            setErrorMessage(restErr.message || 'Simulation execution failed');
          }
        },
      }
    );

    abortStreamRef.current = stopStream;
  }, [productTitle, priceUsd, cohortSize, includeDissentSeats]);

  const handleReset = () => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
    }
    setStatus('idle');
    setSteps([]);
    setOverallConversion(null);
    setTopObjections([]);
    setRecommendations([]);
    setErrorMessage(null);
  };

  return (
    <div
      className={`relative w-[440px] rounded-2xl border transition-all duration-300 shadow-2xl backdrop-blur-md ${
        selected
          ? 'border-emerald-500 shadow-emerald-500/20 ring-2 ring-emerald-500/30'
          : status === 'simulating'
          ? 'border-emerald-400/60 shadow-emerald-500/10 animate-pulse'
          : 'border-slate-800 hover:border-slate-700'
      } bg-slate-950/95 text-slate-100 overflow-hidden font-sans`}
    >
      {/* ReactFlow Handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-slate-900"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="in-left"
        className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-slate-900"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="out-right"
        className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-slate-900"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-slate-900"
      />

      {/* Header Banner */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-slate-800 bg-slate-900/60">
        <div className="flex items-center space-x-2.5">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Users className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-semibold tracking-wider uppercase text-emerald-400">
                SAAP v1.0
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {cohortSize} Personas
              </span>
            </div>
            <h3 className="text-sm font-bold text-white truncate max-w-[220px]">
              {productTitle}
            </h3>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center space-x-2">
          {status === 'simulating' && (
            <span className="flex items-center space-x-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping mr-1" />
              Live SSE
            </span>
          )}
          {status === 'completed' && (
            <span className="flex items-center space-x-1 text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              <CheckCircle2 className="w-3 h-3 mr-0.5" />
              {overallConversion !== null ? `${overallConversion}% CR` : 'Done'}
            </span>
          )}
          {status === 'idle' && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
              Ready
            </span>
          )}
          {status === 'error' && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Error
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800/80 bg-slate-900/30 text-xs font-medium">
        <button
          onClick={() => setActiveTab('funnel')}
          className={`flex-1 py-2 text-center transition-colors border-b-2 ${
            activeTab === 'funnel'
              ? 'border-emerald-400 text-emerald-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Funnel HUD
        </button>
        <button
          onClick={() => setActiveTab('objections')}
          className={`flex-1 py-2 text-center transition-colors border-b-2 ${
            activeTab === 'objections'
              ? 'border-emerald-400 text-emerald-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Hard-No Dissent ({topObjections.length})
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 py-2 text-center transition-colors border-b-2 ${
            activeTab === 'settings'
              ? 'border-emerald-400 text-emerald-400 font-semibold'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Parameters
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="p-4 space-y-4 max-h-[360px] overflow-y-auto custom-scrollbar">
        {errorMessage && (
          <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Tab 1: Funnel HUD */}
        {activeTab === 'funnel' && (
          <div className="space-y-3">
            {steps.length === 0 ? (
              <div className="py-8 text-center text-slate-500 space-y-2">
                <Activity className="w-8 h-8 mx-auto opacity-40 text-emerald-400" />
                <p className="text-xs">Натисніть "Run Swarm Simulation", щоб запустити ройовий тест</p>
              </div>
            ) : (
              steps.map((st, i) => (
                <div
                  key={st.step_id}
                  className="p-2.5 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200 flex items-center space-x-1.5">
                      <span className="w-4 h-4 rounded-full bg-slate-800 text-[10px] flex items-center justify-center text-slate-400">
                        {i + 1}
                      </span>
                      <span>{st.name}</span>
                    </span>
                    <span className="text-emerald-400 font-bold">
                      {st.converted_count} / {st.reached_count} ({st.step_conversion_pct}%)
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden flex">
                    <div
                      className="bg-emerald-400 h-full rounded-full transition-all duration-500"
                      style={{ width: `${st.step_conversion_pct}%` }}
                    />
                  </div>

                  {/* Drop-off stat */}
                  {st.drop_off_count > 0 && (
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span className="flex items-center text-rose-400">
                        <TrendingDown className="w-3 h-3 mr-1" />
                        Drop-off: {st.drop_off_count} ({st.drop_off_pct}%)
                      </span>
                      {st.primary_objections && st.primary_objections.length > 0 && (
                        <span className="text-slate-400 truncate max-w-[200px]">
                          Заперечення: {st.primary_objections[0]}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}

            {overallConversion !== null && (
              <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-slate-300 font-medium">Final Funnel Conversion</span>
                </div>
                <span className="text-sm font-bold text-emerald-400">
                  {overallConversion}%
                </span>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Hard-No Dissent & Objections */}
        {activeTab === 'objections' && (
          <div className="space-y-3">
            {/* Dissent Seat Badge */}
            <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1.5">
              <div className="flex items-center space-x-2 text-amber-400 text-xs font-semibold">
                <ShieldAlert className="w-4 h-4" />
                <span>Mandatory Dissent Seat (Evidence-Grounded)</span>
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed">
                Скептик запобігає Yes-man bias моделі та виявляє критичні заперечення покупців щодо довіри, вартості чи користі.
              </p>
            </div>

            {/* Objections List */}
            {topObjections.length > 0 ? (
              <div className="space-y-2">
                <span className="text-xs font-medium text-slate-400">Топ заперечень когорти:</span>
                <div className="flex flex-wrap gap-1.5">
                  {topObjections.map((obj, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2.5 py-1 rounded-lg bg-rose-900/30 text-rose-300 border border-rose-700/40"
                    >
                      {obj}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 text-center py-4">Заперечення ще не виявлено</p>
            )}

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-xs font-medium text-slate-400">Рекомендації для оферу:</span>
                <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                  {recommendations.map((rec, idx) => (
                    <li key={idx} className="leading-snug text-emerald-300">
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Settings */}
        {activeTab === 'settings' && (
          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Product Title</label>
              <input
                type="text"
                value={productTitle}
                onChange={(e) => setProductTitle(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-400 mb-1">Price (USD)</label>
                <div className="relative">
                  <DollarSign className="w-3.5 h-3.5 absolute left-2 top-2 text-slate-500" />
                  <input
                    type="number"
                    value={priceUsd}
                    onChange={(e) => setPriceUsd(Number(e.target.value))}
                    className="w-full pl-7 pr-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Cohort Size</label>
                <input
                  type="number"
                  min={5}
                  max={200}
                  value={cohortSize}
                  onChange={(e) => setCohortSize(Number(e.target.value))}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="text-slate-300">Include "Hard-No" Skeptic Seat</span>
              <input
                type="checkbox"
                checked={includeDissentSeats}
                onChange={(e) => setIncludeDissentSeats(e.target.checked)}
                className="w-4 h-4 rounded text-emerald-500 bg-slate-900 border-slate-700 focus:ring-emerald-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/60 flex items-center space-x-2">
        <button
          onClick={handleRunSimulation}
          disabled={status === 'simulating'}
          className={`flex-1 py-2 px-3 rounded-xl font-medium text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md ${
            status === 'simulating'
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold'
          }`}
        >
          {status === 'simulating' ? (
            <>
              <Activity className="w-3.5 h-3.5 animate-spin" />
              <span>Simulating Swarm...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Run Swarm Simulation</span>
            </>
          )}
        </button>

        <button
          onClick={handleReset}
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
          title="Скинути результати"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
