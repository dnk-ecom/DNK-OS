// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/taskdna/TaskDNALiveHUD.tsx"
// purpose: "5-Column TaskDNA Live HUD with Founder HITL 1-click Approval Bar & Anti-Poisoning state machine"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (gerych_builder)"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState } from 'react';
import {
  useTaskDNALiveHUD,
  TaskDNASlice,
  TaskDNAPhase,
} from '../../ui/hooks/useTaskDNALiveHUD';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Crown,
  FileText,
  UserCheck,
  Bot,
  PlusCircle,
  ExternalLink,
} from 'lucide-react';

const COLUMNS: { phase: TaskDNAPhase; title: string; color: string; border: string; bg: string; icon: any }[] = [
  {
    phase: 'RESEARCH_RAW',
    title: '1. Research Raw',
    color: 'text-amber-400',
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/10',
    icon: Bot,
  },
  {
    phase: 'AUDIT_GATE',
    title: '2. Audit Gate',
    color: 'text-sky-400',
    border: 'border-sky-500/30',
    bg: 'bg-sky-500/10',
    icon: ShieldAlert,
  },
  {
    phase: 'FOUNDER_APPROVAL',
    title: '3. Founder Approval (HITL)',
    color: 'text-purple-400',
    border: 'border-purple-500/40',
    bg: 'bg-purple-500/15',
    icon: Crown,
  },
  {
    phase: 'LIBRARIAN_INGEST',
    title: '4. Librarian Ingest',
    color: 'text-indigo-400',
    border: 'border-indigo-500/30',
    bg: 'bg-indigo-500/10',
    icon: FileText,
  },
  {
    phase: 'COMPLETED',
    title: '5. Completed (Sealed)',
    color: 'text-emerald-400',
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/10',
    icon: ShieldCheck,
  },
];

export default function TaskDNALiveHUD() {
  const {
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
  } = useTaskDNALiveHUD(4000);

  const [actingTaskId, setActingTaskId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newContent, setNewContent] = useState<string>('');

  const handleFounderDecision = async (taskId: string, approved: boolean) => {
    setActingTaskId(taskId);
    try {
      await submitFounderDecision(
        taskId,
        approved,
        approved ? 'Approved by Founder Maxim' : 'Rejected: needs revision'
      );
    } catch (err) {
      console.error(err);
    } finally {
      setActingTaskId(null);
    }
  };

  const handleAuditAction = async (taskId: string, pass: boolean) => {
    setActingTaskId(taskId);
    try {
      await submitAuditVerdict(taskId, pass, pass ? 0.99 : 0.45, pass ? [] : ['Detected potential Hallucination']);
    } catch (err) {
      console.error(err);
    } finally {
      setActingTaskId(null);
    }
  };

  const handleCompleteIngest = async (taskId: string) => {
    setActingTaskId(taskId);
    try {
      await completeIngest(taskId);
    } catch (err) {
      console.error(err);
    } finally {
      setActingTaskId(null);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      await createSampleTask(newTitle, newContent);
      setNewTitle('');
      setNewContent('');
      setShowCreateModal(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* HUD Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
            <Crown className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white">
                TaskDNA Swarm Live HUD
              </h1>
              <span className="px-2 py-0.5 rounded-full text-xs font-mono font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Anti-Poisoning v2.5
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Zero Direct Memory Poisoning Protocol • Mandatory Founder HITL Verification Gate
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {lastSyncedAt && (
            <span className="text-xs font-mono text-slate-400 hidden sm:inline">
              HUD Synced: {new Date(lastSyncedAt).toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={() => syncHUD()}
            disabled={syncingHUD}
            className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
            title="Update Obsidian Canvas file: docs/notes/Canvas/Swarm_Live_HUD.canvas"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncingHUD ? 'animate-spin text-purple-400' : ''}`} />
            <span>{syncingHUD ? 'Syncing...' : 'Sync Canvas HUD'}</span>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-3.5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium rounded-xl shadow-lg shadow-purple-600/20 transition"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Research Task</span>
          </button>
        </div>
      </div>

      {/* Error notification */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs px-4 py-3 rounded-xl flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => fetchTasks()} className="underline hover:text-white">Retry</button>
        </div>
      )}

      {/* 5-Column Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 flex-1 items-start">
        {COLUMNS.map((col) => {
          const colTasks = tasks.filter((t) => t.phase === col.phase);
          const ColIcon = col.icon;

          return (
            <div
              key={col.phase}
              className={`flex flex-col rounded-2xl border ${col.border} ${col.bg} backdrop-blur-sm min-h-[560px] p-3.5 space-y-3`}
            >
              {/* Column Header */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                <div className="flex items-center space-x-2">
                  <ColIcon className={`w-4 h-4 ${col.color}`} />
                  <h3 className={`text-xs font-semibold ${col.color}`}>{col.title}</h3>
                </div>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                  {colTasks.length}
                </span>
              </div>

              {/* Tasks List */}
              <div className="flex-1 space-y-3 overflow-y-auto max-h-[700px] pr-1">
                {colTasks.length === 0 ? (
                  <div className="h-32 flex flex-col items-center justify-center text-slate-500 text-xs italic">
                    Немає задач у цій фазі
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      className="bg-slate-900/90 hover:bg-slate-900 border border-slate-800 rounded-xl p-3.5 shadow-md space-y-3 transition group"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-mono text-purple-400 font-medium">
                          #{task.id.slice(0, 8)}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
                          {task.assigned_agent}
                        </span>
                      </div>

                      <h4 className="text-sm font-medium text-slate-100 leading-snug">
                        {task.title}
                      </h4>

                      {task.content && (
                        <p className="text-xs text-slate-400 line-clamp-3 font-normal leading-relaxed">
                          {task.content}
                        </p>
                      )}

                      {/* Audit details badge if present */}
                      {task.audit_report && (
                        <div className="bg-slate-950/60 rounded-lg p-2 border border-slate-800 text-[11px] space-y-1">
                          <div className="flex justify-between items-center text-slate-400">
                            <span>Auditor Score:</span>
                            <span className="font-mono font-bold text-sky-400">
                              {(task.audit_report.security_score * 100).toFixed(0)}%
                            </span>
                          </div>
                          {task.audit_report.critical_issues.length > 0 && (
                            <div className="text-red-400 font-mono text-[10px]">
                              Issues: {task.audit_report.critical_issues.join(', ')}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Ingest Path if completed */}
                      {task.ingest_path && (
                        <div className="flex items-center space-x-1 text-[10px] font-mono text-emerald-400 bg-emerald-950/40 p-1.5 rounded border border-emerald-800/40">
                          <FileText className="w-3 h-3 flex-shrink-0" />
                          <span className="truncate">{task.ingest_path}</span>
                        </div>
                      )}

                      {/* ================= ACTIONS PER PHASE ================= */}

                      {/* 1. Research Raw Action: Dispatch to Auditor */}
                      {task.phase === 'RESEARCH_RAW' && (
                        <button
                          onClick={() => handleAuditAction(task.id, true)}
                          disabled={actingTaskId === task.id}
                          className="w-full flex items-center justify-center space-x-1.5 py-1.5 bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 rounded-lg text-xs font-medium transition"
                        >
                          <ShieldAlert className="w-3 h-3" />
                          <span>Передати на аудит</span>
                        </button>
                      )}

                      {/* 2. Audit Gate Actions */}
                      {task.phase === 'AUDIT_GATE' && (
                        <div className="grid grid-cols-2 gap-2 pt-1">
                          <button
                            onClick={() => handleAuditAction(task.id, true)}
                            disabled={actingTaskId === task.id}
                            className="flex items-center justify-center space-x-1 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-medium transition"
                          >
                            <ShieldCheck className="w-3 h-3" />
                            <span>Audit Pass</span>
                          </button>
                          <button
                            onClick={() => handleAuditAction(task.id, false)}
                            disabled={actingTaskId === task.id}
                            className="flex items-center justify-center space-x-1 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-300 border border-red-500/30 rounded-lg text-xs font-medium transition"
                          >
                            <XCircle className="w-3 h-3" />
                            <span>Fail</span>
                          </button>
                        </div>
                      )}

                      {/* 3. FOUNDER APPROVAL (HITL ACTION BAR) */}
                      {task.phase === 'FOUNDER_APPROVAL' && (
                        <div className="bg-purple-950/40 border border-purple-500/40 rounded-xl p-2.5 space-y-2 mt-2">
                          <div className="flex items-center space-x-1.5 text-purple-300 text-[11px] font-semibold">
                            <Crown className="w-3.5 h-3.5 text-purple-400" />
                            <span>Рішення Засновника (Максим)</span>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              onClick={() => handleFounderDecision(task.id, true)}
                              disabled={actingTaskId === task.id}
                              className="flex items-center justify-center space-x-1 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-700/20 transition active:scale-95"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Схвалити</span>
                            </button>
                            <button
                              onClick={() => handleFounderDecision(task.id, false)}
                              disabled={actingTaskId === task.id}
                              className="flex items-center justify-center space-x-1 py-1.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-medium transition"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              <span>Відхилити</span>
                            </button>
                          </div>
                        </div>
                      )}

                      {/* 4. Librarian Ingest Action */}
                      {task.phase === 'LIBRARIAN_INGEST' && (
                        <button
                          onClick={() => handleCompleteIngest(task.id)}
                          disabled={actingTaskId === task.id}
                          className="w-full flex items-center justify-center space-x-1.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium shadow transition"
                        >
                          <FileText className="w-3 h-3" />
                          <span>Зафіксувати в Obsidian PKM</span>
                        </button>
                      )}

                      {/* 5. Completed: view receipt */}
                      {task.phase === 'COMPLETED' && (
                        <div className="flex items-center justify-between text-[11px] text-emerald-400 font-mono pt-1">
                          <span className="flex items-center space-x-1">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Vault Protected</span>
                          </span>
                          <span className="text-slate-500">Anti-Poisoned</span>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal for Creating Sample Research Task */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Bot className="w-5 h-5 text-purple-400" />
                <span>Створити дослідницьку задачу (TaskDNA)</span>
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Назва задачі / Тема дослідження
                </label>
                <input
                  type="text"
                  required
                  placeholder="напр., Асиміляція SOTA Whisper Hallucination Filter"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Опис або дослідницький вміст
                </label>
                <textarea
                  rows={4}
                  placeholder="Вкажіть гіпотезу, посилання на репозиторій або ключові архітектурні інваріанти..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-medium"
                >
                  Скасувати
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-purple-600/30"
                >
                  Запустити через Pipeline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
