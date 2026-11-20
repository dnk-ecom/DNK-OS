// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/video/ShortsKineticPlayer.tsx"
// purpose: "9:16 Vertical Video Shorts Studio with Kinetic Text Preview, Cut Pauses Timeline & Remotion Composer"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (gerych_builder)"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  useVideoShorts,
  HighlightCandidate,
  WordTimestamp,
} from '../../ui/hooks/useVideoShorts';
import {
  Play,
  Pause,
  RotateCcw,
  Scissors,
  Sparkles,
  Download,
  Share2,
  Film,
  Zap,
  CheckCircle,
  Eye,
} from 'lucide-react';

const SAMPLE_WORDS: WordTimestamp[] = [
  { word: 'Це', start: 0.1, end: 0.35 },
  { word: 'революційний', start: 0.38, end: 0.95 },
  { word: 'прорив', start: 0.98, end: 1.4 },
  { word: 'у', start: 1.42, end: 1.55 },
  { word: 'DNK', start: 1.58, end: 2.1 },
  { word: 'Studio', start: 2.15, end: 2.7 },
  { word: 'OS.', start: 2.75, end: 3.2 },
  { word: 'Ми', start: 3.3, end: 3.5 },
  { word: 'вирізаємо', start: 3.55, end: 4.1 },
  { word: 'всі', start: 4.15, end: 4.35 },
  { word: 'паузи', start: 4.4, end: 4.9 },
  { word: 'та', start: 4.95, end: 5.1 },
  { word: 'слова-паразити', start: 5.15, end: 6.0 },
  { word: 'повністю', start: 6.1, end: 6.7 },
  { word: 'автономно!', start: 6.75, end: 7.6 },
];

export default function ShortsKineticPlayer() {
  const {
    loading,
    error,
    highlightData,
    composedData,
    extractHighlights,
    composeShort,
    exportEdl,
  } = useVideoShorts();

  const [activeWords, setActiveWords] = useState<WordTimestamp[]>(SAMPLE_WORDS);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [accentColor, setAccentColor] = useState<string>('#06B6D4');
  const [selectedCandidate, setSelectedCandidate] = useState<HighlightCandidate | null>(null);
  const [edlJson, setEdlJson] = useState<string | null>(null);

  const duration = activeWords.length > 0 ? activeWords[activeWords.length - 1].end : 10;
  const timerRef = useRef<any>(null);

  // Auto playback ticker
  useEffect(() => {
    if (isPlaying) {
      const step = 0.05;
      timerRef.current = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= duration) {
            setIsPlaying(false);
            return 0;
          }
          return prev + step;
        });
      }, 50);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, duration]);

  // Extract highlights on mount if none
  const handleRunExtraction = async () => {
    try {
      const res = await extractHighlights(SAMPLE_WORDS, 'demo_podcast_ep1', 3);
      if (res.candidates.length > 0) {
        setSelectedCandidate(res.candidates[0]);
        setActiveWords(res.candidates[0].words);
        setCurrentTime(0);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleComposeRemotion = async () => {
    try {
      await composeShort({
        candidate: selectedCandidate || undefined,
        words: activeWords,
        accentColor,
        title: 'DNK OS • OpenMontage Kinetic Short',
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleExportEdl = async () => {
    try {
      const res = await exportEdl(
        'podcast_master_cut.mp4',
        selectedCandidate ? [selectedCandidate] : undefined,
        activeWords
      );
      setEdlJson(JSON.stringify(res, null, 2));
    } catch (e) {
      console.error(e);
    }
  };

  // Find current active word index
  const currentWordIndex = activeWords.findIndex(
    (w) => currentTime >= w.start && currentTime <= w.end
  );

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-full w-full bg-slate-950 text-slate-100 p-6">
      {/* LEFT: 9:16 Vertical Video Frame (Kinetic Player) */}
      <div className="flex flex-col items-center justify-center flex-shrink-0 w-full lg:w-[420px] bg-slate-900/60 p-6 rounded-3xl border border-slate-800 backdrop-blur-md">
        <div className="w-full flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Film className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-bold text-slate-300">
              9:16 Vertical Stage
            </span>
          </div>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            Remotion 1080x1920
          </span>
        </div>

        {/* 9:16 Mobile Viewport Frame */}
        <div className="relative w-[280px] h-[497px] sm:w-[320px] sm:h-[568px] bg-gradient-to-b from-slate-900 via-slate-950 to-black rounded-[36px] border-4 border-slate-700 shadow-2xl overflow-hidden flex flex-col justify-between p-5 select-none">
          {/* Top Info Bar */}
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center space-x-2 bg-black/40 backdrop-blur-md px-2.5 py-1 rounded-full border border-white/10">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-[10px] font-mono font-bold text-white tracking-wider">
                @dnk_os
              </span>
            </div>
            <div className="bg-black/40 backdrop-blur-md px-2 py-0.5 rounded-full border border-white/10 text-[10px] font-mono text-cyan-300">
              {currentTime.toFixed(1)}s / {duration.toFixed(1)}s
            </div>
          </div>

          {/* Central Animated Kinetic Captions */}
          <div className="flex flex-col items-center justify-center z-10 px-2 text-center my-auto">
            <div className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1">
              {activeWords.map((w, idx) => {
                const isActive = idx === currentWordIndex;
                const isPast = currentTime > w.end;

                return (
                  <span
                    key={`${w.word}-${idx}`}
                    style={{
                      color: isActive ? '#FFFFFF' : isPast ? '#94A3B8' : '#475569',
                      transform: isActive ? 'scale(1.15)' : 'scale(1)',
                      backgroundColor: isActive ? accentColor : 'transparent',
                    }}
                    className={`transition-all duration-150 px-1.5 py-0.5 rounded-md font-black tracking-tight text-lg sm:text-xl uppercase drop-shadow-md`}
                  >
                    {w.word}
                  </span>
                );
              })}
            </div>
          </div>

          {/* Bottom Audio/Progress Indicator */}
          <div className="space-y-3 z-10">
            {/* Cut Pauses Indicator Bar */}
            <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 px-1">
              <span className="flex items-center space-x-1">
                <Scissors className="w-3 h-3 text-rose-400" />
                <span>Auto-cut Pauses: -0.8s</span>
              </span>
              <span className="text-emerald-400 font-bold">Retention: 94%</span>
            </div>

            {/* Video Progress Bar */}
            <div className="w-full bg-white/20 h-1.5 rounded-full overflow-hidden">
              <div
                style={{
                  width: `${(currentTime / duration) * 100}%`,
                  backgroundColor: accentColor,
                }}
                className="h-full transition-all duration-75"
              />
            </div>
          </div>
        </div>

        {/* Player Transport Controls */}
        <div className="flex items-center space-x-4 mt-5">
          <button
            onClick={() => setCurrentTime(0)}
            className="p-2.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            style={{ backgroundColor: accentColor }}
            className="p-3.5 rounded-full text-black hover:opacity-90 font-bold shadow-lg transition active:scale-95"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-5 h-5 fill-current" />
            ) : (
              <Play className="w-5 h-5 fill-current ml-0.5" />
            )}
          </button>

          <button
            onClick={handleRunExtraction}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 text-xs font-mono flex items-center space-x-1.5 transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Extract</span>
          </button>
        </div>
      </div>

      {/* RIGHT: Studio Control Center & Remotion Pipeline */}
      <div className="flex-1 flex flex-col space-y-5">
        {/* Header summary */}
        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <span>OpenMontage Video Shorts Studio</span>
            </h2>
            <span className="text-xs font-mono bg-cyan-950 text-cyan-400 px-2.5 py-1 rounded-full border border-cyan-800/60">
              Vite + Remotion Engine v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Видобування вірусних фрагментів, очищення від filler words («е-е-е», довгі паузи) та генерація кінетичних титрів із сертифікованим чеком цілісності (VideoReceipt).
          </p>
        </div>

        {/* Highlight Candidates & Metrics */}
        <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">
              Хайлайт-кандидати (Viral Score Ranked)
            </h3>
            {highlightData && (
              <span className="text-xs font-mono text-slate-400">
                Знайдено: {highlightData.total_candidates}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              onClick={() => {
                setActiveWords(SAMPLE_WORDS);
                setCurrentTime(0);
              }}
              className="p-3.5 rounded-xl border border-cyan-500/40 bg-cyan-950/20 cursor-pointer hover:border-cyan-400 transition space-y-2"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-mono text-cyan-300 font-bold">Кліп #1 (Top Hook)</span>
                <span className="bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded text-[10px] font-mono">
                  Virality: 96%
                </span>
              </div>
              <p className="text-xs text-slate-300 line-clamp-2">
                "Це революційний прорив у DNK Studio OS. Ми вирізаємо всі паузи..."
              </p>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>Hook: 0.95</span>
                <span>Слів: {SAMPLE_WORDS.length}</span>
                <span>Таймінг: 0.0s - 7.6s</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-950/40 opacity-70 hover:opacity-100 transition space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="font-mono text-slate-300 font-bold">Кліп #2 (Deep Insight)</span>
                <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded text-[10px] font-mono">
                  Virality: 88%
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2">
                "Архітектура TaskDNA повністю унеможливлює отруєння довготривалої пам'яті..."
              </p>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span>Hook: 0.88</span>
                <span>Слів: 12</span>
                <span>Таймінг: 14.2s - 21.0s</span>
              </div>
            </div>
          </div>
        </div>

        {/* Styling & Composition Action Bar */}
        <div className="bg-slate-900/40 p-5 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200">
            Параметри Remotion Композиції
          </h3>

          <div className="flex flex-wrap items-center gap-4">
            <div className="space-y-1">
              <label className="text-[11px] font-mono text-slate-400">Акцентний колір титрів</label>
              <div className="flex items-center space-x-2">
                {['#06B6D4', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'].map((c) => (
                  <button
                    key={c}
                    onClick={() => setAccentColor(c)}
                    style={{ backgroundColor: c }}
                    className={`w-6 h-6 rounded-full border-2 transition ${
                      accentColor === c ? 'border-white scale-110 shadow-lg' : 'border-transparent'
                    }`}
                  />
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-3 ml-auto pt-3">
              <button
                onClick={handleComposeRemotion}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-cyan-600/30 transition"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Зібрати Remotion Short</span>
              </button>

              <button
                onClick={handleExportEdl}
                disabled={loading}
                className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-medium border border-slate-700 transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Експорт EDL (FCP / Premiere)</span>
              </button>
            </div>
          </div>

          {/* Composed Status / Receipt */}
          {composedData && (
            <div className="mt-4 p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/40 space-y-2">
              <div className="flex items-center space-x-2 text-cyan-300 text-xs font-bold">
                <CheckCircle className="w-4 h-4 text-cyan-400" />
                <span>Remotion Short успішно згенеровано!</span>
              </div>
              <div className="text-[11px] font-mono text-slate-300 space-y-1">
                <div>ID: {composedData.composition.composition_id}</div>
                <div>Роздільна здатність: {composedData.composition.width}x{composedData.composition.height} @ {composedData.composition.fps}fps</div>
                <div>Тривалість: {composedData.composition.duration_in_frames} кадрів</div>
              </div>
            </div>
          )}

          {/* Exported EDL Viewer */}
          {edlJson && (
            <div className="mt-4 space-y-1.5">
              <span className="text-xs font-mono text-slate-400">Згенерований монтажний список EDL:</span>
              <pre className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[10px] font-mono text-cyan-400 max-h-40 overflow-y-auto">
                {edlJson}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
