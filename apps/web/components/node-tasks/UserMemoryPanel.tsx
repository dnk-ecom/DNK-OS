// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/node-tasks/UserMemoryPanel.tsx"
// purpose: "User memory panel: shows who you are, your projects and social accounts (graph nodes) and lets you add accounts, a profile and facts without touching code"
// author: "DNK-e.com Maksym & Claude"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-10"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { Brain, X, RefreshCw, Plus } from 'lucide-react';

type MemNode = {
  id: string;
  title: string;
  content?: string;
  metadata: { entity_type?: string; platform?: string; handle?: string; project_id?: string | null };
};
type MemGraph = { nodes: MemNode[]; wires: unknown[]; counts: Record<string, number> };

const API = '/api/v3/memory';

async function call(path: string, method: string, body?: unknown) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export function UserMemoryPanel() {
  const [open, setOpen] = useState(false);
  const [graph, setGraph] = useState<MemGraph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [platform, setPlatform] = useState('Instagram');
  const [handle, setHandle] = useState('');
  const [projectId, setProjectId] = useState('');
  const [fact, setFact] = useState('');

  const load = useCallback(async () => {
    try {
      setError(null);
      setGraph(await call('/graph', 'GET'));
    } catch {
      setError('Не вдалося завантажити пам’ять');
    }
  }, []);

  useEffect(() => {
    if (open) void load();
  }, [open, load]);

  const run = async (fn: () => Promise<unknown>) => {
    try {
      setError(null);
      await fn();
      await load();
    } catch {
      setError('Не вдалося зберегти. Перевірте поля й спробуйте ще раз.');
    }
  };

  const byType = (t: string) => (graph?.nodes ?? []).filter((n) => n.metadata.entity_type === t);
  const projects = byType('business_project');
  const owner = byType('person')[0];

  const input = 'w-full rounded-md bg-zinc-800 border border-zinc-700 px-2 py-1.5 text-sm text-zinc-100 placeholder:text-zinc-500';
  const button = 'inline-flex items-center gap-1 rounded-md bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1.5 text-xs font-medium text-white disabled:opacity-40';

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed left-4 bottom-24 z-40 inline-flex items-center gap-2 rounded-full bg-zinc-900/90 border border-zinc-700 px-3 py-2 text-xs text-zinc-100 shadow-lg hover:border-cyan-500"
        aria-label="Відкрити пам’ять про вас"
      >
        <Brain className="h-4 w-4 text-cyan-400" /> Пам’ять
      </button>

      {open && (
        <aside className="fixed left-0 top-0 z-50 h-full w-[360px] overflow-y-auto bg-zinc-950 border-r border-zinc-800 p-4 space-y-5 text-zinc-100">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold flex items-center gap-2"><Brain className="h-4 w-4 text-cyan-400" /> Пам’ять про вас</h2>
            <div className="flex gap-2">
              <button type="button" onClick={() => void load()} aria-label="Оновити"><RefreshCw className="h-4 w-4" /></button>
              <button type="button" onClick={() => setOpen(false)} aria-label="Закрити"><X className="h-4 w-4" /></button>
            </div>
          </div>
          {error && <p className="text-xs text-red-400">{error}</p>}

          <section className="space-y-2">
            <h3 className="text-xs uppercase tracking-wide text-zinc-400">Ви</h3>
            {owner && <p className="text-sm">{owner.title}{owner.content ? ` — ${owner.content.split('\n')[0]}` : ''}</p>}
            <input className={input} placeholder="Ваше ім’я" value={name} onChange={(e) => setName(e.target.value)} />
            <textarea className={input} placeholder="Коротко про себе та бізнес" rows={2} value={bio} onChange={(e) => setBio(e.target.value)} />
            <button type="button" className={button} disabled={!name.trim()} onClick={() => void run(async () => { await call('/profile', 'PUT', { name, bio }); setName(''); setBio(''); })}>
              <Plus className="h-3 w-3" /> Зберегти профіль
            </button>
          </section>

          <section className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs uppercase tracking-wide text-zinc-400">Проєкти ({projects.length})</h3>
              <button type="button" className={button} onClick={() => void run(() => call('/projects/sync', 'POST'))}>Підтягнути проєкти</button>
            </div>
            <ul className="text-sm space-y-1">
              {projects.map((p) => <li key={p.id}>• {p.title}</li>)}
            </ul>
          </section>

          <section className="space-y-2">
            <h3 className="text-xs uppercase tracking-wide text-zinc-400">Соцмережі ({byType('social_account').length})</h3>
            <ul className="text-sm space-y-1">
              {byType('social_account').map((s) => <li key={s.id}>• {s.title}</li>)}
            </ul>
            <div className="grid grid-cols-2 gap-2">
              <input className={input} placeholder="Платформа" value={platform} onChange={(e) => setPlatform(e.target.value)} />
              <input className={input} placeholder="@акаунт" value={handle} onChange={(e) => setHandle(e.target.value)} />
            </div>
            <select className={input} value={projectId} onChange={(e) => setProjectId(e.target.value)}>
              <option value="">Без проєкту (лише ви)</option>
              {projects.map((p) => <option key={p.id} value={p.id.replace(/^proj-/, '')}>{p.title}</option>)}
            </select>
            <button type="button" className={button} disabled={!platform.trim() || !handle.trim()}
              onClick={() => void run(async () => { await call('/social', 'POST', { platform, handle, project_id: projectId || null }); setHandle(''); })}>
              <Plus className="h-3 w-3" /> Додати акаунт
            </button>
          </section>

          <section className="space-y-2">
            <h3 className="text-xs uppercase tracking-wide text-zinc-400">Факти про вас ({byType('fact').length})</h3>
            <ul className="text-sm space-y-1">
              {byType('fact').map((f) => <li key={f.id}>• {f.content || f.title}</li>)}
            </ul>
            <input className={input} placeholder="Наприклад: працюю тільки українською" value={fact} onChange={(e) => setFact(e.target.value)} />
            <button type="button" className={button} disabled={fact.trim().length < 2}
              onClick={() => void run(async () => { await call('/fact', 'POST', { text: fact }); setFact(''); })}>
              <Plus className="h-3 w-3" /> Запам’ятати
            </button>
          </section>
        </aside>
      )}
    </>
  );
}
