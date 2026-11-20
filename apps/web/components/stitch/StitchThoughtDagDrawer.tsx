// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/stitch/StitchThoughtDagDrawer.tsx"
// purpose: "ThoughtDAG DSL Import/Export, Kahn Cycle Gate & Multi-Parent Synthesis Drawer for DNK Studio."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym & Gerych (Hermes Prime)"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useCallback } from 'react';
import {
  Brain,
  FileCode2,
  GitMerge,
  Cpu,
  Play,
  Download,
  Upload,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Check,
  RefreshCw,
  X,
  Layers
} from 'lucide-react';
import { useCanvasStore } from '../../store/canvasStore';
import type { Node, Edge } from '@xyflow/react';

export interface StitchThoughtDagDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onNotification?: (msg: { text: string; type: 'success' | 'info' | 'warning' | 'error' }) => void;
}

const PRESET_TRIAD = `[hypothesis] H1: RAG з локальною пам'яттю SCONES зменшує галюцинації на 40%
[critique] C1: Високий overhead на холодний старт векторного індексу
[synthesis] S1: Гібридний дворівневий кеш з дедуплікацією спільних предків
H1 -> C1 : перевірка затримки
H1 -> S1 : прямий контекст
C1 -> S1 : врахування ризиків`;

const PRESET_PARALLEL = `[hypothesis] H1: Аналіз ринку: попит на автономні AI студії зріс на 120%
[hypothesis] H2: Фінансовий бюджет: COGS на рівні $0.04 на одиницю контенту
[hypothesis] H3: Технічний стек: Next.js + FastAPI + Web Worker Canvas
[synthesis] S1: Фінальний план запуску продукту
H1 -> S1
H2 -> S1
H3 -> S1`;

const PRESET_CYCLE = `[hypothesis] H1: Перевірка гіпотези A
[critique] C1: Ризик виникнення циклу
H1 -> C1
C1 -> H1`;

export const StitchThoughtDagDrawer: React.FC<StitchThoughtDagDrawerProps> = ({
  isOpen = true,
  onClose,
  onNotification,
}) => {
  const [activeTab, setActiveTab] = useState<'dsl' | 'merge' | 'compile'>('dsl');
  const [dslInput, setDslInput] = useState<string>(PRESET_TRIAD);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [cycleError, setCycleError] = useState<string[] | null>(null);

  // Multi-parent state
  const [selectedParents, setSelectedParents] = useState<string[]>([]);
  const [synthesisTitle, setSynthesisTitle] = useState<string>('Синтез рішень');
  const [mergeResult, setMergeResult] = useState<any | null>(null);

  // Compile context state
  const [selectedTargetNode, setSelectedTargetNode] = useState<string>('');
  const [compiledContext, setCompiledContext] = useState<any | null>(null);

  const { nodes, edges, setNodes, setEdges } = useCanvasStore();

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onNotification?.({ text: 'Скопійовано в буфер обміну', type: 'success' });
  };

  // 1. Parse DSL & Import to Canvas
  const handleImportDSL = async () => {
    if (!dslInput.trim()) return;
    setIsLoading(true);
    setCycleError(null);

    try {
      const res = await fetch('/api/v1/thoughtdag/dsl/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dsl_text: dslInput,
          graph_id: `graph_${Date.now()}`,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        if (res.status === 422 && errData.detail?.cycle_nodes) {
          setCycleError(errData.detail.cycle_nodes);
          onNotification?.({
            text: `Детектовано цикл: ${errData.detail.cycle_nodes.join(' <-> ')}`,
            type: 'error',
          });
          return;
        }
        throw new Error(errData.detail?.message || `HTTP ${res.status}`);
      }

      const data = await res.json();
      if (data.has_cycles) {
        setCycleError(data.cycle_nodes);
        onNotification?.({
          text: `Граф містить зациклені залежності: ${data.cycle_nodes.join(', ')}`,
          type: 'error',
        });
        return;
      }

      // Map parsed nodes to ReactFlow nodes
      const parsedNodes = data.graph.nodes || [];
      const parsedWires = data.graph.wires || [];

      // Auto-layout in grid/columns
      const newRfNodes: Node[] = parsedNodes.map((n: any, idx: number) => {
        const col = idx % 3;
        const row = Math.floor(idx / 3);
        return {
          id: n.id,
          type: 'thoughtDagNote',
          position: { x: 100 + col * 320, y: 150 + row * 240 },
          data: {
            title: n.title || n.id,
            content: n.content || n.title,
            highlightMode: 'all',
            isLiving: true,
            updatedAt: new Date().toISOString(),
          },
        };
      });

      const newRfEdges: Edge[] = parsedWires.map((w: any) => ({
        id: w.id || `wire_${w.source}_${w.target}`,
        source: w.source,
        target: w.target,
        type: 'context-wire',
        animated: true,
        data: {
          scope: w.scope || 'all',
          isBlocked: false,
        },
      }));

      setNodes(newRfNodes);
      setEdges(newRfEdges);

      onNotification?.({
        text: `Успішно імпортовано: ${newRfNodes.length} нод, ${newRfEdges.length} зв'язків`,
        type: 'success',
      });
    } catch (err: any) {
      onNotification?.({ text: `Помилка імпорту: ${err.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Export Canvas to DSL
  const handleExportDSL = async () => {
    setIsLoading(true);
    try {
      const graphPayload = {
        graph_id: 'canvas_export',
        nodes: nodes.map((n) => ({
          id: n.id,
          title: (n.data as any)?.title || n.id,
          kind: 'note',
          status: 'ready',
          content: (n.data as any)?.content || '',
          tags: [(n.data as any)?.thought_type || 'hypothesis'],
          metadata: { thought_type: (n.data as any)?.thought_type || 'hypothesis' },
        })),
        wires: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          wire_type: 'context-wire',
          scope: (e.data as any)?.scope || 'all',
        })),
      };

      const res = await fetch('/api/v1/thoughtdag/dsl/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph: graphPayload }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDslInput(data.dsl_text);
      setActiveTab('dsl');
      onNotification?.({
        text: 'Граф канвасу успішно експортовано у DSL',
        type: 'success',
      });
    } catch (err: any) {
      onNotification?.({ text: `Помилка експорту: ${err.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Multi-Parent Context Merge
  const handleMergeContext = async () => {
    if (selectedParents.length < 2) {
      onNotification?.({
        text: 'Оберіть щонайменше 2 батьківські ноди для злиття',
        type: 'warning',
      });
      return;
    }
    setIsLoading(true);

    try {
      const graphPayload = {
        graph_id: 'canvas_merge_target',
        nodes: nodes.map((n) => ({
          id: n.id,
          title: (n.data as any)?.title || n.id,
          kind: 'note',
          status: 'ready',
          content: (n.data as any)?.content || '',
          tags: [],
          metadata: {},
        })),
        wires: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          wire_type: 'context-wire',
          scope: 'all',
        })),
      };

      const res = await fetch('/api/v1/thoughtdag/merge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          graph: graphPayload,
          parent_node_ids: selectedParents,
          target_title: synthesisTitle,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setMergeResult(data);
      onNotification?.({
        text: `Злиття завершено: об'єднано ${data.ancestors_deduped_count} предків`,
        type: 'success',
      });
    } catch (err: any) {
      onNotification?.({ text: `Помилка злиття: ${err.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // 4. Create Synthesized Node on Canvas
  const handleSpawnSynthesisNode = () => {
    if (!mergeResult) return;
    const synthId = mergeResult.target_node_id || `synthesis_${Date.now()}`;
    const newSynthNode: Node = {
      id: synthId,
      type: 'thoughtDagNote',
      position: { x: 450, y: 400 },
      data: {
        title: synthesisTitle,
        content: mergeResult.synthesized_content,
        highlightMode: 'all',
        isLiving: true,
        updatedAt: new Date().toISOString(),
      },
    };

    const newWires: Edge[] = selectedParents.map((parentId) => ({
      id: `wire_${parentId}_${synthId}`,
      source: parentId,
      target: synthId,
      type: 'context-wire',
      animated: true,
      data: { scope: 'all', isBlocked: false },
    }));

    setNodes([...nodes, newSynthNode]);
    setEdges([...edges, ...newWires]);
    onNotification?.({
      text: `Створено ноду синтезу [${synthesisTitle}] з ${newWires.length} зв'язками`,
      type: 'success',
    });
  };

  // 5. Compile Target Context
  const handleCompileTarget = async () => {
    if (!selectedTargetNode) return;
    setIsLoading(true);

    try {
      const graphPayload = {
        graph_id: 'canvas_compile_target',
        nodes: nodes.map((n) => ({
          id: n.id,
          title: (n.data as any)?.title || n.id,
          kind: 'note',
          status: 'ready',
          content: (n.data as any)?.content || '',
          tags: [],
          metadata: {},
        })),
        wires: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          wire_type: 'context-wire',
          scope: 'all',
        })),
      };

      const res = await fetch(`/api/v1/thoughtdag/context/${selectedTargetNode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(graphPayload),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setCompiledContext(data);
      onNotification?.({
        text: `Контекст скомпільовано (~${data.estimated_tokens} токенів)`,
        type: 'success',
      });
    } catch (err: any) {
      onNotification?.({ text: `Помилка компіляції: ${err.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-[540px] z-50 flex flex-col bg-[#1e2022] border-l border-[#224447] shadow-2xl text-[#d4d8db] animate-in slide-in-from-right duration-200">
      {/* Top Header */}
      <div className="flex items-center justify-between px-5 py-3.5 bg-[#112224] border-b border-[#224447]">
        <div className="flex items-center gap-2.5">
          <Brain className="w-5 h-5 text-[#35d5d5]" />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-[#35d5d5] tracking-wide">
                ThoughtDAG Studio
              </span>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#162c2f] border border-[#224447] text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e]" />
                KAHN GATE ACTIVE
              </span>
            </div>
            <p className="text-[11px] text-zinc-400">
              Clean-room DSL, детекція циклів та злиття контексту
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/5 text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center px-4 pt-3 bg-[#162c2f] border-b border-[#224447] gap-2">
        <button
          onClick={() => setActiveTab('dsl')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-b-2 cursor-pointer ${
            activeTab === 'dsl'
              ? 'border-[#35d5d5] text-[#35d5d5] bg-[#1e2022]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <FileCode2 className="w-3.5 h-3.5" />
          <span>Thought DSL</span>
        </button>

        <button
          onClick={() => setActiveTab('merge')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-b-2 cursor-pointer ${
            activeTab === 'merge'
              ? 'border-[#35d5d5] text-[#35d5d5] bg-[#1e2022]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <GitMerge className="w-3.5 h-3.5" />
          <span>Multi-Parent Merge</span>
        </button>

        <button
          onClick={() => setActiveTab('compile')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-b-2 cursor-pointer ${
            activeTab === 'compile'
              ? 'border-[#35d5d5] text-[#35d5d5] bg-[#1e2022]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>Compile Context</span>
        </button>
      </div>

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {activeTab === 'dsl' && (
          <div className="space-y-4">
            {/* Presets Bar */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                Швидкі Пресети:
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setDslInput(PRESET_TRIAD)}
                  className="px-2.5 py-1 text-xs rounded bg-[#162c2f] hover:bg-[#1f3f44] border border-[#224447] text-cyan-300 transition-colors"
                >
                  Тріада Дослідження
                </button>
                <button
                  onClick={() => setDslInput(PRESET_PARALLEL)}
                  className="px-2.5 py-1 text-xs rounded bg-[#162c2f] hover:bg-[#1f3f44] border border-[#224447] text-emerald-300 transition-colors"
                >
                  Паралельне Дослідження
                </button>
                <button
                  onClick={() => setDslInput(PRESET_CYCLE)}
                  className="px-2.5 py-1 text-xs rounded bg-[#162c2f] hover:bg-[#1f3f44] border border-[#224447] text-rose-300 transition-colors"
                >
                  Тест Циклу (Кана)
                </button>
              </div>
            </div>

            {/* Cycle Error Banner */}
            {cycleError && (
              <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold">Помилка валідації графа (Kahn's Gate):</div>
                  <div className="text-[11px] mt-0.5">
                    Виявлено замкнений цикл залежностей серед вузлів:{' '}
                    <span className="font-mono font-bold text-rose-200">
                      {cycleError.join(' ↔ ')}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* DSL Textarea */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                  Текстовий DSL Код:
                </label>
                <button
                  onClick={() => handleCopy(dslInput)}
                  className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-cyan-300"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Скопійовано' : 'Копіювати'}</span>
                </button>
              </div>
              <textarea
                value={dslInput}
                onChange={(e) => setDslInput(e.target.value)}
                rows={12}
                placeholder="[hypothesis] H1: ...&#10;[critique] C1: ...&#10;H1 -> C1"
                className="w-full font-mono text-xs bg-[#162c2f] border border-[#224447] rounded-lg p-3 text-zinc-200 focus:outline-none focus:border-[#35d5d5] leading-relaxed resize-none"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={handleImportDSL}
                disabled={isLoading}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-[#35d5d5] text-[#112224] font-medium text-xs hover:bg-[#46e0e0] transition-colors cursor-pointer shadow-lg shadow-cyan-950/30 disabled:opacity-50"
              >
                {isLoading ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Upload className="w-3.5 h-3.5" />
                )}
                <span>Імпортувати на Канвас</span>
              </button>

              <button
                onClick={handleExportDSL}
                disabled={isLoading}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-[#162c2f] border border-[#224447] text-zinc-200 font-medium text-xs hover:bg-[#1f3f44] hover:text-[#35d5d5] transition-colors cursor-pointer disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Експортувати з Канвасу</span>
              </button>
            </div>
          </div>
        )}

        {activeTab === 'merge' && (
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-[#162c2f] border border-[#224447] text-xs">
              <div className="font-semibold text-[#35d5d5] mb-1">
                Селективна Мульти-Батьківська Агрегація
              </div>
              <p className="text-zinc-400 text-[11px] leading-relaxed">
                Об'єднує контекст від кількох незалежних гілок дослідження із дедуплікацією спільних предків
                та обчисленням SHA-256 відбитка upstream-стану.
              </p>
            </div>

            {/* Target Title Input */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                Заголовок Синтезу:
              </label>
              <input
                type="text"
                value={synthesisTitle}
                onChange={(e) => setSynthesisTitle(e.target.value)}
                className="w-full text-xs bg-[#162c2f] border border-[#224447] rounded-lg px-3 py-2 text-zinc-200 focus:outline-none focus:border-[#35d5d5]"
              />
            </div>

            {/* Node Checklist */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                Оберіть Батьківські Ноди ({selectedParents.length} обрано):
              </label>
              <div className="max-h-48 overflow-y-auto space-y-1.5 p-2 bg-[#162c2f] border border-[#224447] rounded-lg">
                {nodes.length === 0 ? (
                  <div className="text-xs text-zinc-500 py-2 text-center">
                    Канвас порожній. Імпортуйте DSL спочатку.
                  </div>
                ) : (
                  nodes.map((n) => {
                    const isChecked = selectedParents.includes(n.id);
                    const title = (n.data as any)?.title || n.id;
                    return (
                      <label
                        key={n.id}
                        className={`flex items-center gap-2.5 p-2 rounded cursor-pointer transition-colors text-xs ${
                          isChecked ? 'bg-[#1f3f44] text-cyan-200' : 'hover:bg-white/5 text-zinc-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedParents([...selectedParents, n.id]);
                            } else {
                              setSelectedParents(selectedParents.filter((id) => id !== n.id));
                            }
                          }}
                          className="rounded border-[#224447] bg-[#112224] text-[#35d5d5] focus:ring-0"
                        />
                        <span className="font-mono text-[10px] text-zinc-400">[{n.id}]</span>
                        <span className="truncate flex-1">{title}</span>
                      </label>
                    );
                  })
                )}
              </div>
            </div>

            {/* Merge Action Button */}
            <button
              onClick={handleMergeContext}
              disabled={isLoading || selectedParents.length < 2}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-[#35d5d5] text-[#112224] font-medium text-xs hover:bg-[#46e0e0] transition-colors cursor-pointer disabled:opacity-50"
            >
              <GitMerge className="w-3.5 h-3.5" />
              <span>Виконати Злиття Контексту</span>
            </button>

            {/* Merge Preview Card */}
            {mergeResult && (
              <div className="p-4 rounded-lg bg-[#162c2f] border border-[#224447] space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Злиття успішне
                  </span>
                  <span className="font-mono text-[10px] text-zinc-400">
                    Дедупліковано предків: {mergeResult.ancestors_deduped_count}
                  </span>
                </div>

                <div className="text-[11px] font-mono text-zinc-400 break-all bg-[#112224] p-2 rounded border border-[#224447]">
                  <span className="text-cyan-400">Fingerprint:</span> {mergeResult.upstream_fingerprint}
                </div>

                <div className="max-h-36 overflow-y-auto text-xs text-zinc-300 bg-[#112224] p-2.5 rounded border border-[#224447] font-mono whitespace-pre-wrap">
                  {mergeResult.synthesized_content}
                </div>

                <button
                  onClick={handleSpawnSynthesisNode}
                  className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs font-medium transition-colors"
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Розмістити Ноду Синтезу на Канвасі</span>
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'compile' && (
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-[#162c2f] border border-[#224447] text-xs">
              <div className="font-semibold text-[#35d5d5] mb-1">
                Топологічна Компіляція Промпт-Контексту
              </div>
              <p className="text-zinc-400 text-[11px] leading-relaxed">
                Формує чистий контекст для виконання роєм агентів із топологічним впорядкуванням усіх батьківських вузлів.
              </p>
            </div>

            {/* Select Target Node */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                Цільовий Вузол:
              </label>
              <select
                value={selectedTargetNode}
                onChange={(e) => setSelectedTargetNode(e.target.value)}
                className="w-full text-xs bg-[#162c2f] border border-[#224447] rounded-lg px-3 py-2 text-zinc-200 focus:outline-none focus:border-[#35d5d5]"
              >
                <option value="">-- Оберіть ноду для компіляції --</option>
                {nodes.map((n) => (
                  <option key={n.id} value={n.id}>
                    [{n.id}] {(n.data as any)?.title || n.id}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleCompileTarget}
              disabled={isLoading || !selectedTargetNode}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-[#35d5d5] text-[#112224] font-medium text-xs hover:bg-[#46e0e0] transition-colors cursor-pointer disabled:opacity-50"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>Скомпілювати Контекст</span>
            </button>

            {/* Compiled Result */}
            {compiledContext && (
              <div className="p-4 rounded-lg bg-[#162c2f] border border-[#224447] space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#35d5d5]">
                    Оцінка токенів: ~{compiledContext.estimated_tokens}
                  </span>
                  <button
                    onClick={() => handleCopy(compiledContext.context_text)}
                    className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-cyan-300"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? 'Скопійовано' : 'Копіювати Промпт'}</span>
                  </button>
                </div>

                <div className="text-[11px] font-mono text-zinc-400 break-all bg-[#112224] p-2 rounded border border-[#224447]">
                  <span className="text-cyan-400">SHA-256:</span> {compiledContext.upstream_fingerprint}
                </div>

                <div className="max-h-48 overflow-y-auto text-xs text-zinc-300 bg-[#112224] p-2.5 rounded border border-[#224447] font-mono whitespace-pre-wrap">
                  {compiledContext.context_text}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StitchThoughtDagDrawer;
