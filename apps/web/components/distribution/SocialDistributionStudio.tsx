// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_distribution_SocialDistributionStudio"
// purpose: "Unified DNK OS Social Media Distribution Studio with On-Demand Postiz Lifecycle Management & Embedded Setup"
// canonical_source: true
// alters_files: []
// triggers_tasks: ["DNK-MEDIA-PHASE-4-005"]
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// author: "DNK-e.com Maksym & Gerych Builder"
// --- END DNK-MRH-HEADER ---

import React, { useState, useEffect } from 'react';
import {
  Share2,
  Power,
  RotateCcw,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  Layers,
  Cpu,
  Video,
  Send,
  Eye,
  RefreshCw,
} from 'lucide-react';

interface ChannelStatus {
  platform: string;
  name: string;
  connected: boolean;
  auto_publish_enabled: boolean;
  requires_video: boolean;
  max_caption_length: number;
}

interface PostizHealth {
  running: boolean;
  healthy: boolean;
  status_code: number;
  url: string;
  mode: string;
}

export const SocialDistributionStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'channels' | 'embedded_cabinet' | 'rlsf'>('channels');
  const [health, setHealth] = useState<PostizHealth>({
    running: false,
    healthy: false,
    status_code: 0,
    url: 'http://localhost:5000',
    mode: 'stopped',
  });
  const [channels, setChannels] = useState<ChannelStatus[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/v1/content/distribution/status');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch {
      // offline or mock fallback
      setHealth({
        running: false,
        healthy: false,
        status_code: 0,
        url: 'http://localhost:5000',
        mode: 'offline',
      });
    }
  };

  const fetchChannels = async () => {
    try {
      const res = await fetch('/api/v1/content/distribution/channels');
      if (res.ok) {
        const data = await res.json();
        setChannels(data);
      }
    } catch {
      // default list
      setChannels([
        { platform: 'tiktok', name: 'TikTok', connected: false, auto_publish_enabled: true, requires_video: true, max_caption_length: 2200 },
        { platform: 'youtube_shorts', name: 'YouTube Shorts', connected: false, auto_publish_enabled: true, requires_video: true, max_caption_length: 5000 },
        { platform: 'instagram_reels', name: 'Instagram Reels', connected: false, auto_publish_enabled: true, requires_video: true, max_caption_length: 2200 },
        { platform: 'x_twitter', name: 'X / Twitter', connected: false, auto_publish_enabled: true, requires_video: false, max_caption_length: 280 },
        { platform: 'linkedin', name: 'LinkedIn', connected: false, auto_publish_enabled: true, requires_video: false, max_caption_length: 3000 },
      ]);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchChannels();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleStartOnDemand = async () => {
    setLoading(true);
    setActionMessage('Запуск контейнерів Postiz On-Demand (підняття Postgres, Redis, App)...');
    try {
      const res = await fetch('/api/v1/content/distribution/lifecycle/start', { method: 'POST' });
      if (res.ok) {
        const result = await res.json();
        setHealth(result.status);
        setActionMessage('Postiz успішно запущено та готовий до роботи!');
      } else {
        setActionMessage('Помилка під час запуску Postiz.');
      }
    } catch (e: any) {
      setActionMessage(`Помилка запиту: ${e.message}`);
    } finally {
      setLoading(false);
      setTimeout(() => setActionMessage(null), 5000);
    }
  };

  const handleStopOnDemand = async () => {
    setLoading(true);
    setActionMessage('Зупинка контейнерів Postiz для звільнення RAM та процесора...');
    try {
      const res = await fetch('/api/v1/content/distribution/lifecycle/stop', { method: 'POST' });
      if (res.ok) {
        const result = await res.json();
        setHealth(result.status);
        setActionMessage('Postiz зупинено. 0 МБ споживання памʼяті.');
      } else {
        setActionMessage('Помилка під час зупинки.');
      }
    } catch (e: any) {
      setActionMessage(`Помилка запиту: ${e.message}`);
    } finally {
      setLoading(false);
      setTimeout(() => setActionMessage(null), 5000);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6 space-y-6 overflow-y-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
              <Share2 className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                DNK Social Distribution Studio
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                  Postiz Headless Engine
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                Автономна мультиканальна публікація з адаптацією форматів та навчанням RLSF
              </p>
            </div>
          </div>
        </div>

        {/* On-Demand Lifecycle Widget */}
        <div className="flex items-center space-x-3 bg-slate-900 border border-slate-800 rounded-xl p-2.5">
          <div className="flex items-center space-x-2 mr-2">
            <div
              className={`w-3 h-3 rounded-full ${
                health.running
                  ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                  : 'bg-slate-600'
              }`}
            />
            <div className="text-xs">
              <span className="text-slate-400">Стек: </span>
              <span className="font-semibold text-slate-200">
                {health.running ? 'Активний (On-Demand)' : 'Зупинений (0 MB RAM)'}
              </span>
            </div>
          </div>

          {!health.running ? (
            <button
              onClick={handleStartOnDemand}
              disabled={loading}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium transition disabled:opacity-50"
            >
              <Power className="w-3.5 h-3.5" />
              <span>{loading ? 'Запуск...' : 'Запустити стек'}</span>
            </button>
          ) : (
            <button
              onClick={handleStopOnDemand}
              disabled={loading}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-rose-600/80 hover:bg-rose-500 text-white rounded-lg text-xs font-medium transition disabled:opacity-50"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>{loading ? 'Зупинка...' : 'Зупинити (Save RAM)'}</span>
            </button>
          )}

          <button
            onClick={() => {
              fetchStatus();
              fetchChannels();
            }}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-800 transition"
            title="Оновити статус"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="bg-indigo-950/60 border border-indigo-700/50 text-indigo-200 text-xs px-4 py-2.5 rounded-lg flex items-center space-x-2 animate-fadeIn">
          <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-4">
        <button
          onClick={() => setActiveTab('channels')}
          className={`pb-3 text-sm font-medium transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'channels'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Канали публікації</span>
        </button>
        <button
          onClick={() => setActiveTab('embedded_cabinet')}
          className={`pb-3 text-sm font-medium transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'embedded_cabinet'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ExternalLink className="w-4 h-4" />
          <span>Вбудований кабінет Postiz</span>
        </button>
      </div>

      {/* TAB CONTENT: CHANNELS OVERVIEW */}
      {activeTab === 'channels' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {channels.map((ch) => (
              <div
                key={ch.platform}
                className="bg-slate-900 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-4 hover:border-slate-700 transition"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-white text-base flex items-center space-x-2">
                      <span>{ch.name}</span>
                    </h3>
                    {ch.connected ? (
                      <span className="flex items-center space-x-1 text-emerald-400 text-xs bg-emerald-950/50 border border-emerald-800/50 px-2 py-0.5 rounded-md">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Підключено</span>
                      </span>
                    ) : (
                      <span className="flex items-center space-x-1 text-amber-400 text-xs bg-amber-950/50 border border-amber-800/50 px-2 py-0.5 rounded-md">
                        <AlertCircle className="w-3 h-3" />
                        <span>Потрібна привʼязка</span>
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 mb-3">
                    {ch.requires_video
                      ? 'Обовʼязковий формат 9:16 Shorts/Reels з кінетичними субтитрами'
                      : 'Підтримка коротких текстових тез, посилань та медіа-вкладень'}
                  </p>

                  <div className="text-[11px] text-slate-500 space-y-1">
                    <div>Ліміт опису: {ch.max_caption_length} символів</div>
                    <div>Авто-публікація: {ch.auto_publish_enabled ? 'Увімкнено (HITL Approved)' : 'Вимкнено'}</div>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                  <button
                    onClick={() => {
                      if (!health.running) {
                        handleStartOnDemand();
                      }
                      setActiveTab('embedded_cabinet');
                    }}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
                  >
                    <span>{ch.connected ? 'Налаштування каналу' : 'Підключити акаунт'}</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Explanatory Banner */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-start space-x-3">
            <Sparkles className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300 space-y-1">
              <span className="font-semibold text-white">Як працює On-Demand публікація:</span>
              <p>
                Вам не потрібно тримати Postiz увімкненим. Коли агент генерує контент і ви натискаєте{' '}
                <code className="text-indigo-300">Approve</code>, бекенд автоматично піднімає Docker-контейнери Postiz,
                відправляє публікацію згідно з правилами платформи і після завершення черги повертає ресурси компʼютеру.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: EMBEDDED POSTIZ CABINET */}
      {activeTab === 'embedded_cabinet' && (
        <div className="flex-1 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[600px]">
          {health.running ? (
            <div className="flex-1 flex flex-col">
              <div className="bg-slate-950 px-4 py-2 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Вбудований інтерфейс Postiz ({health.url})</span>
                </span>
                <a
                  href={health.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-400 hover:underline flex items-center space-x-1"
                >
                  <span>Відкрити в новому вікні</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <iframe
                src={health.url}
                className="w-full flex-1 border-0 bg-white"
                title="Postiz Studio Embedded"
              />
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center space-y-4">
              <div className="p-4 bg-slate-800/80 rounded-2xl text-slate-400 border border-slate-700">
                <Power className="w-8 h-8" />
              </div>
              <div className="max-w-md space-y-2">
                <h3 className="text-lg font-bold text-white">Стек Postiz наразі зупинено</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Щоб відкрити кабінет авторизації соцмереж та привʼязати ваші акаунти (YouTube, TikTok, Reels),
                  запустіть Postiz On-Demand в один клік.
                </p>
              </div>
              <button
                onClick={handleStartOnDemand}
                disabled={loading}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg transition flex items-center space-x-2 disabled:opacity-50"
              >
                <Power className="w-4 h-4" />
                <span>{loading ? 'Запуск контейнерів...' : 'Запустити Postiz для налаштування'}</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
