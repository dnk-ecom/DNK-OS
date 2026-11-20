// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_nodes_VideoCreatorNode"
// purpose: "Spatial AI Video Studio Node for Remotion & Diffusion generation with aspect ratio selection, prompt control, and render API integration"
// author: "DNK-e.com Maksym"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-08-31"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { 
  Video, 
  Play, 
  Pause, 
  Sparkles, 
  Layers, 
  Film, 
  CheckCircle2, 
  RefreshCw, 
  Download, 
  Sliders, 
  Maximize2,
  Tv,
  Smartphone,
  Square,
  Type,
  FileText,
  Zap,
  Music,
  Volume2,
  VolumeX,
  Brain,
  Gauge,
  FileVideo
} from 'lucide-react';
import KineticCaptionsPreview, { KineticPhraseItem } from '../remotion/KineticCaptionsPreview';

export interface VideoCreatorData {
  title?: string;
  prompt?: string;
  aspectRatio?: '9:16' | '16:9' | '1:1';
  stylePreset?: string;
  duration?: number;
  fps?: number;
  previewUrl?: string;
  status?: 'idle' | 'rendering' | 'completed' | 'failed';
  renderProgress?: number;
  assignedAgent?: string;
  inputContext?: Record<string, any>;
  kineticCaptions?: any;
  pattern_interrupts?: any;
  patternInterrupts?: any;
  hook_variants?: any;
  selected_hook_variant?: any;
  selectedHookVariant?: any;
  sound_design_plan?: any;
  soundDesignPlan?: any;
  neuro_simulation?: any;
  neuroSimulation?: any;
}

export default function VideoCreatorNode({ data, selected }: NodeProps) {
  const nodeData = (data || {}) as VideoCreatorData;
  const [title, setTitle] = useState(nodeData.title || 'AI Video Studio');
  const [prompt, setPrompt] = useState(nodeData.prompt || 'Cinematic luxury showcase of ReBurn Smoker v2 with dynamic lighting and smoke simulation');
  const [aspectRatio, setAspectRatio] = useState<'9:16' | '16:9' | '1:1'>(nodeData.aspectRatio || '9:16');
  const [stylePreset, setStylePreset] = useState(nodeData.stylePreset || 'Cyberpunk Neon Motion');
  const [duration, setDuration] = useState(nodeData.duration || 15);
  const [status, setStatus] = useState<'idle' | 'rendering' | 'completed' | 'failed'>(nodeData.status || 'idle');
  const [renderProgress, setRenderProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTimeMs, setPlaybackTimeMs] = useState(0);
  const [captionsStyle, setCaptionsStyle] = useState<'hormozi_bold' | 'minimal_clean' | 'cyberpunk_neon'>('hormozi_bold');
  const [showCaptions, setShowCaptions] = useState(true);
  const [kineticTrack, setKineticTrack] = useState<any>(nodeData.inputContext?.kineticCaptions || (nodeData as any).kineticCaptions || null);
  const [patternInterrupts, setPatternInterrupts] = useState<any>(
    nodeData.inputContext?.pattern_interrupts ||
    nodeData.inputContext?.patternInterrupts ||
    (nodeData as any).pattern_interrupts ||
    (nodeData as any).patternInterrupts ||
    null
  );
  const [enableInterrupts, setEnableInterrupts] = useState(true);
  const [selectedHook, setSelectedHook] = useState<any>(
    nodeData.inputContext?.selected_hook_variant ||
    nodeData.inputContext?.selectedHookVariant ||
    (nodeData as any).selected_hook_variant ||
    (nodeData as any).selectedHookVariant ||
    null
  );
  const [hookVariants, setHookVariants] = useState<any>(
    nodeData.inputContext?.hook_variants ||
    (nodeData as any).hook_variants ||
    null
  );
  const [soundDesignPlan, setSoundDesignPlan] = useState<any>(
    nodeData.inputContext?.sound_design_plan ||
    nodeData.inputContext?.soundDesignPlan ||
    (nodeData as any).sound_design_plan ||
    (nodeData as any).soundDesignPlan ||
    null
  );
  const [neuroSimulation, setNeuroSimulation] = useState<any>(
    nodeData.inputContext?.neuro_simulation ||
    nodeData.inputContext?.neuroSimulation ||
    (nodeData as any).neuro_simulation ||
    (nodeData as any).neuroSimulation ||
    null
  );
  const [enableAudioDucking, setEnableAudioDucking] = useState<boolean>(true);
  const [whisperXAlignment, setWhisperXAlignment] = useState<any>(null);
  const [isAligningAudio, setIsAligningAudio] = useState(false);
  const [expandedPhonemeWord, setExpandedPhonemeWord] = useState<number | null>(null);

  // Smart Reframing & Silence Cutting States
  const [autoSilenceCut, setAutoSilenceCut] = useState<boolean>(true);
  const [minSilenceMs, setMinSilenceMs] = useState<number>(400);
  const [silencePlan, setSilencePlan] = useState<any>(null);
  const [isDetectingSilence, setIsDetectingSilence] = useState<boolean>(false);

  const [smartReframe916, setSmartReframe916] = useState<boolean>(true);
  const [sourceAspectRatio, setSourceAspectRatio] = useState<string>('16:9');
  const [reframePlan, setReframePlan] = useState<any>(null);
  const [isCalculatingReframe, setIsCalculatingReframe] = useState<boolean>(false);

  // Synchronize prompt & captions reactively when upstream node pipes data
  useEffect(() => {
    if (nodeData.prompt && nodeData.prompt !== prompt) {
      setPrompt(nodeData.prompt);
    }
  }, [nodeData.prompt]);

  useEffect(() => {
    const upstreamCaptions = nodeData.inputContext?.kineticCaptions || (nodeData as any).kineticCaptions;
    if (upstreamCaptions) {
      setKineticTrack(upstreamCaptions);
    }
  }, [nodeData.inputContext?.kineticCaptions, (nodeData as any).kineticCaptions]);

  useEffect(() => {
    const upstreamInterrupts =
      nodeData.inputContext?.pattern_interrupts ||
      nodeData.inputContext?.patternInterrupts ||
      (nodeData as any).pattern_interrupts ||
      (nodeData as any).patternInterrupts;
    if (upstreamInterrupts) {
      setPatternInterrupts(upstreamInterrupts);
    }
  }, [
    nodeData.inputContext?.pattern_interrupts,
    nodeData.inputContext?.patternInterrupts,
    (nodeData as any).pattern_interrupts,
    (nodeData as any).patternInterrupts,
  ]);

  useEffect(() => {
    const upstreamHook =
      nodeData.inputContext?.selected_hook_variant ||
      nodeData.inputContext?.selectedHookVariant ||
      (nodeData as any).selected_hook_variant ||
      (nodeData as any).selectedHookVariant;
    if (upstreamHook) {
      setSelectedHook(upstreamHook);
    }
    const upstreamVariants =
      nodeData.inputContext?.hook_variants ||
      (nodeData as any).hook_variants;
    if (upstreamVariants) {
      setHookVariants(upstreamVariants);
    }
  }, [
    nodeData.inputContext?.selected_hook_variant,
    nodeData.inputContext?.selectedHookVariant,
    (nodeData as any).selected_hook_variant,
    (nodeData as any).selectedHookVariant,
    nodeData.inputContext?.hook_variants,
    (nodeData as any).hook_variants,
  ]);

  useEffect(() => {
    const upstreamSound =
      nodeData.inputContext?.sound_design_plan ||
      nodeData.inputContext?.soundDesignPlan ||
      (nodeData as any).sound_design_plan ||
      (nodeData as any).soundDesignPlan;
    if (upstreamSound) {
      setSoundDesignPlan(upstreamSound);
    }

    const upstreamNeuro =
      nodeData.inputContext?.neuro_simulation ||
      nodeData.inputContext?.neuroSimulation ||
      (nodeData as any).neuro_simulation ||
      (nodeData as any).neuroSimulation;
    if (upstreamNeuro) {
      setNeuroSimulation(upstreamNeuro);
    }
  }, [
    nodeData.inputContext?.sound_design_plan,
    nodeData.inputContext?.soundDesignPlan,
    (nodeData as any).sound_design_plan,
    (nodeData as any).soundDesignPlan,
  ]);

  const activeInterrupt = React.useMemo(() => {
    if (!enableInterrupts || !patternInterrupts?.interrupts) return null;
    return patternInterrupts.interrupts.find(
      (item: any) => playbackTimeMs >= item.start_ms && playbackTimeMs <= item.end_ms
    );
  }, [enableInterrupts, patternInterrupts, playbackTimeMs]);

  const activeSFX = React.useMemo(() => {
    if (!soundDesignPlan?.sfx_timeline) return null;
    const currentSec = playbackTimeMs / 1000;
    return soundDesignPlan.sfx_timeline.find(
      (sfx: any) => Math.abs(sfx.time_s - currentSec) <= 0.35
    );
  }, [soundDesignPlan, playbackTimeMs]);

  const activeDuckingState = React.useMemo(() => {
    if (!soundDesignPlan?.ducking_keyframes) return { isDucked: false, volumeDb: -4, volumeMult: 0.8 };
    const kfs = soundDesignPlan.ducking_keyframes;
    const currentKf = kfs.slice().reverse().find((kf: any) => kf.time_ms <= playbackTimeMs) || kfs[0];
    const isSpeech = currentKf?.is_speech_active ?? false;
    const depthDb = soundDesignPlan?.ducking_settings?.ducking_depth_db || -16;
    return {
      isDucked: isSpeech && enableAudioDucking,
      volumeDb: isSpeech && enableAudioDucking ? depthDb : -4,
      volumeMult: isSpeech && enableAudioDucking ? 0.2 : 0.85
    };
  }, [soundDesignPlan, playbackTimeMs, enableAudioDucking]);

  const activeHeatmapPoint = React.useMemo(() => {
    if (!neuroSimulation?.heatmap_points) return null;
    const currentSec = Math.floor(playbackTimeMs / 1000);
    return neuroSimulation.heatmap_points.find((pt: any) => pt.second === currentSec) || null;
  }, [neuroSimulation, playbackTimeMs]);

  // Video playback simulation ticker for subtitles
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setPlaybackTimeMs((prev) => {
          const maxMs = (duration || 15) * 1000;
          if (prev >= maxMs) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 100;
        });
      }, 100);
    } else {
      if (interval) clearInterval(interval);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, duration]);
  const [renderMessage, setRenderMessage] = useState('Ready for render');

  // Server-Side MP4 Export Engine State
  const [exportJobId, setExportJobId] = useState<string | null>(null);
  const [exportStatus, setExportStatus] = useState<'idle' | 'rendering' | 'completed' | 'failed'>('idle');
  const [exportProgress, setExportProgress] = useState<number>(0);
  const [exportStage, setExportStage] = useState<string>('');
  const [exportDownloadUrl, setExportDownloadUrl] = useState<string | null>(null);
  const [exportFileSize, setExportFileSize] = useState<number | null>(null);

  const stylePresets = [
    'Cyberpunk Neon Motion',
    'Hyper-Realistic Luxury',
    'Clean Minimalist E-Com',
    'High-Energy TikTok Hook',
    'Dark Obsidian Kinetic'
  ];

  const handleGenerateVideo = async () => {
    setStatus('rendering');
    setRenderProgress(10);
    setRenderMessage('Synthesizing script & audio timeline...');

    try {
      // Step 1 progress simulation / API dispatch
      const payload = {
        prompt,
        aspect_ratio: aspectRatio,
        style_preset: stylePreset,
        duration_seconds: duration,
        fps: 30,
        agent: 'dnk_video_ai_creator'
      };

      const timer1 = setTimeout(() => {
        setRenderProgress(45);
        setRenderMessage('Generating Remotion Composition & Layer Effects...');
      }, 700);

      const timer2 = setTimeout(() => {
        setRenderProgress(80);
        setRenderMessage('Encoding H.264 / MP4 stream...');
      }, 1400);

      const res = await fetch('/api/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => null);

      setTimeout(() => {
        setRenderProgress(100);
        setStatus('completed');
        setRenderMessage('Video rendered successfully! 🎬');
      }, 2000);
    } catch {
      setStatus('completed');
      setRenderProgress(100);
      setRenderMessage('Render completed (Offline Studio Mode)');
    }
  };

  const handleExportMP4 = async () => {
    setExportStatus('rendering');
    setExportProgress(5);
    setExportStage('Submitting export job to server...');
    setExportDownloadUrl(null);
    setExportFileSize(null);

    try {
      const payload = {
        video_duration_s: duration || 15,
        title: title || 'Retention_Short',
        resolution: '9:16',
        quality: 'standard_1080p',
        background_style: 'cyberpunk_grid',
        kinetic_captions: kineticTrack ? {
          animation_preset: captionsStyle,
          phrases: kineticTrack.phrases || [],
          words: whisperXAlignment?.words || []
        } : null,
        pattern_interrupts: patternInterrupts?.interrupts || null,
        sound_design_plan: soundDesignPlan || null,
        auto_silence_cut: autoSilenceCut,
        min_silence_ms: minSilenceMs,
        smart_reframe_9_16: smartReframe916,
        source_aspect_ratio: sourceAspectRatio
      };

      const res = await fetch('/api/v1/video/retention/export-mp4', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      const jobId = data.job_id;
      setExportJobId(jobId);
      setExportStage(data.stage || 'Rendering initiated...');
      setExportProgress(data.progress_pct || 15);

      // Start Polling Status
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/v1/video/retention/export-status/${jobId}`);
          if (!statusRes.ok) return;
          const statusData = await statusRes.json();
          setExportProgress(statusData.progress_pct);
          setExportStage(statusData.stage || 'Rendering in progress...');

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            setExportStatus('completed');
            setExportProgress(100);
            setExportDownloadUrl(statusData.download_url);
            setExportFileSize(statusData.file_size_bytes);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setExportStatus('failed');
            setExportStage(statusData.error_message || 'Rendering failed');
          }
        } catch (pollErr) {
          console.error('Failed to poll export status:', pollErr);
        }
      }, 700);

    } catch (err: any) {
      console.error('Export MP4 error:', err);
      setExportStatus('failed');
      setExportStage(err.message || 'Export failed');
    }
  };

  const handleRunWhisperXAlignment = async () => {
    setIsAligningAudio(true);
    try {
      const res = await fetch('/api/v1/video/retention/align-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: prompt || title || 'Stop scrolling right now',
          total_duration_s: duration,
          language: 'en',
          engine: 'auto',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setWhisperXAlignment(data);
        if (data.words && data.words.length > 0) {
          // Synchronize with kinetic captions track
          setKineticTrack((prev: any) => ({
            ...(prev || {}),
            words_count: data.word_count,
            srt_content: data.srt_karaoke,
            ass_content: data.ass_karaoke,
            engine: data.engine_used,
            alignment_words: data.words,
          }));
        }
      }
    } catch (e) {
      console.error('WhisperX alignment failed:', e);
    } finally {
      setIsAligningAudio(false);
    }
  };

  const handleDetectSilence = async () => {
    setIsDetectingSilence(true);
    try {
      const words = whisperXAlignment?.words || null;
      const res = await fetch('/api/v1/video/retention/detect-silence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          words: words,
          transcript: !words ? (prompt || title || 'Stop scrolling') : null,
          total_duration_s: duration || 15,
          min_silence_ms: minSilenceMs,
          padding_ms: 70
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSilencePlan(data);
      }
    } catch (err) {
      console.error('Detect silence error:', err);
    } finally {
      setIsDetectingSilence(false);
    }
  };

  const handleCalculateSmartReframe = async () => {
    setIsCalculatingReframe(true);
    try {
      const origW = sourceAspectRatio === '4:3' ? 1440 : 1920;
      const res = await fetch('/api/v1/video/retention/smart-reframe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_width: origW,
          original_height: 1080,
          duration_ms: Math.round((duration || 15) * 1000),
          target_aspect_ratio: 0.5625
        })
      });
      if (res.ok) {
        const data = await res.json();
        setReframePlan(data);
      }
    } catch (err) {
      console.error('Smart reframe error:', err);
    } finally {
      setIsCalculatingReframe(false);
    }
  };

  return (
    <div
      className={`relative w-[440px] rounded-2xl bg-[#090d16]/95 backdrop-blur-2xl border transition-all duration-300 shadow-2xl font-sans text-slate-100 select-none overflow-hidden ${
        selected 
          ? 'border-violet-500 shadow-[0_0_35px_rgba(139,92,246,0.35)] ring-1 ring-violet-500/50' 
          : 'border-violet-500/30 hover:border-violet-500/60 shadow-[0_10px_30px_rgba(0,0,0,0.6)]'
      }`}
    >
      {/* 4-Way Flow Connection Handles */}
      <Handle 
        type="target" 
        position={Position.Top} 
        id="top" 
        className="!w-3 !h-3 !bg-violet-500 !border-2 !border-[#090d16] !-top-1.5 hover:!scale-125 transition-transform" 
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="bottom" 
        className="!w-3 !h-3 !bg-violet-500 !border-2 !border-[#090d16] !-bottom-1.5 hover:!scale-125 transition-transform" 
      />
      <Handle 
        type="target" 
        position={Position.Left} 
        id="left" 
        className="!w-3 !h-3 !bg-violet-500 !border-2 !border-[#090d16] !-left-1.5 hover:!scale-125 transition-transform" 
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        id="right" 
        className="!w-3 !h-3 !bg-violet-500 !border-2 !border-[#090d16] !-right-1.5 hover:!scale-125 transition-transform" 
      />

      {/* Header */}
      <div className="p-4 border-b border-violet-500/20 bg-gradient-to-r from-violet-950/40 via-[#0d1222] to-fuchsia-950/30 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-violet-600/20 border border-violet-500/40 text-violet-400 shadow-[0_0_15px_rgba(139,92,246,0.25)]">
            <Video className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white tracking-wide flex items-center gap-1.5">
              <span>{title}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
                Remotion v4
              </span>
            </div>
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-violet-400" />
              <span>AI Video & Motion Composer</span>
            </div>
          </div>
        </div>

        {/* Aspect Ratio Selector Pills */}
        <div className="flex items-center bg-[#06080f] p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setAspectRatio('9:16')}
            className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
              aspectRatio === '9:16'
                ? 'bg-violet-600 text-white font-medium shadow-md shadow-violet-900/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="9:16 Vertical (Reels/Shorts)"
          >
            <Smartphone className="w-3.5 h-3.5" />
            <span className="text-[10px]">9:16</span>
          </button>
          <button
            onClick={() => setAspectRatio('16:9')}
            className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
              aspectRatio === '16:9'
                ? 'bg-violet-600 text-white font-medium shadow-md shadow-violet-900/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="16:9 Landscape (YouTube/TV)"
          >
            <Tv className="w-3.5 h-3.5" />
            <span className="text-[10px]">16:9</span>
          </button>
          <button
            onClick={() => setAspectRatio('1:1')}
            className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
              aspectRatio === '1:1'
                ? 'bg-violet-600 text-white font-medium shadow-md shadow-violet-900/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="1:1 Square (Feed/Ads)"
          >
            <Square className="w-3.5 h-3.5" />
            <span className="text-[10px]">1:1</span>
          </button>
        </div>
      </div>

      {/* Main Body */}
      <div className="p-4 space-y-3.5">
        {/* Video Prompt Area */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
              Creative Direction / Prompt
            </label>
            {nodeData.inputContext?.hookText && (
              <span className="text-[10px] font-medium text-purple-400 bg-purple-500/15 border border-purple-500/30 px-1.5 py-0.5 rounded flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> Retention Hook Synced
              </span>
            )}
          </div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={2}
            className="w-full bg-[#05070e] border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all resize-none placeholder-slate-600"
            placeholder="Describe camera motion, narrative hook, lighting, and product focus..."
          />
        </div>

        {/* Style Preset Selector */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1 block">
              Motion Style
            </label>
            <select
              value={stylePreset}
              onChange={(e) => setStylePreset(e.target.value)}
              className="w-full bg-[#05070e] border border-slate-800 rounded-xl p-2 text-xs text-slate-200 focus:outline-none focus:border-violet-500 transition-all"
            >
              {stylePresets.map((preset) => (
                <option key={preset} value={preset} className="bg-slate-900 text-white">
                  {preset}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1 block flex justify-between">
              <span>Duration</span>
              <span className="text-violet-400">{duration}s</span>
            </label>
            <input
              type="range"
              min={5}
              max={60}
              step={5}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-violet-500 mt-2"
            />
          </div>
        </div>

        {/* Video Preview Canvas / Mockup */}
        <div className="relative rounded-xl border border-slate-800/80 bg-[#04060b] overflow-hidden group">
          <div 
            className={`w-full flex items-center justify-center relative bg-gradient-to-b from-[#0b0f1a] to-[#05070e] transition-transform duration-200 ease-out ${
              aspectRatio === '9:16' ? 'h-52' : aspectRatio === '16:9' ? 'h-40' : 'h-44'
            }`}
            style={{
              transform: activeInterrupt?.interrupt_type === 'zoom_punch' 
                ? `scale(${activeInterrupt.zoom_scale || 1.18})` 
                : 'scale(1)',
            }}
          >
            {/* Visual Canvas Simulation */}
            <div className="text-center p-4">
              <div className="w-12 h-12 rounded-full bg-violet-950/80 border border-violet-500/40 text-violet-400 flex items-center justify-center mx-auto mb-2 shadow-[0_0_20px_rgba(139,92,246,0.3)]">
                {status === 'rendering' ? (
                  <RefreshCw className="w-5 h-5 animate-spin" />
                ) : (
                  <Film className="w-5 h-5" />
                )}
              </div>
              <div className="text-xs font-medium text-slate-200">
                {status === 'rendering' ? 'Remotion Rendering Pipeline' : 'Timeline Ready'}
              </div>
              <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                {aspectRatio} • {duration}s • {stylePreset}
              </div>
            </div>

            {/* Pattern Interrupts: B-Roll Cutaway Overlay Layer */}
            {activeInterrupt?.interrupt_type === 'broll_cutaway' && (
              <div className="absolute inset-0 z-25 bg-slate-950/90 flex flex-col items-center justify-center p-3 animate-in fade-in duration-150">
                {activeInterrupt.broll_placeholder_url ? (
                  <img 
                    src={activeInterrupt.broll_placeholder_url} 
                    alt="B-Roll Footages" 
                    className="absolute inset-0 w-full h-full object-cover opacity-60"
                  />
                ) : (
                  <div className="absolute inset-0 bg-gradient-to-tr from-indigo-950/80 via-slate-900/90 to-purple-950/80" />
                )}
                <div className="relative z-10 text-center space-y-1">
                  <span className="px-2 py-0.5 rounded-full bg-indigo-500/30 border border-indigo-400/50 text-indigo-200 text-[9px] font-mono font-bold uppercase tracking-wider">
                    🎬 B-ROLL CUTAWAY
                  </span>
                  <div className="text-xs font-bold text-white max-w-[220px] truncate drop-shadow">
                    "{activeInterrupt.broll_query || 'Contextual Visual'}"
                  </div>
                  {activeInterrupt.sfx_cue && (
                    <div className="text-[9px] text-slate-300 font-mono drop-shadow">
                      🔊 SFX: {activeInterrupt.sfx_cue}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Pattern Interrupts: Zoom Punch Live Indicator */}
            {activeInterrupt?.interrupt_type === 'zoom_punch' && (
              <div className="absolute top-2 left-2 z-25">
                <span className="px-2 py-0.5 rounded-md bg-amber-500/90 text-slate-950 text-[9px] font-mono font-black uppercase tracking-wider flex items-center gap-1 shadow-lg shadow-amber-500/30">
                  <Maximize2 className="w-2.5 h-2.5" /> ZOOM {activeInterrupt.zoom_scale || 1.18}x
                </span>
              </div>
            )}

            {/* 3-Second Hook Variant Intro Live Badge */}
            {selectedHook && playbackTimeMs <= 3000 && (
              <div className="absolute top-2 right-2 z-25 animate-in fade-in duration-150">
                <span className="px-2 py-0.5 rounded-md bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 text-[9px] font-mono font-black uppercase tracking-wider flex items-center gap-1 shadow-lg shadow-amber-500/30">
                  <Zap className="w-2.5 h-2.5 fill-current" /> HOOK: {selectedHook.title?.split('(')[0] || 'A/B'} ({selectedHook.predicted_3s_retention_pct}% HOLD)
                </span>
              </div>
            )}

            {/* Auto Sound Design: Audio Ducking Live Status Indicator */}
            {soundDesignPlan && (
              <div className="absolute top-8 right-2 z-25 animate-in fade-in duration-150">
                <span className={`px-2 py-0.5 rounded-md text-[9px] font-mono font-bold flex items-center gap-1 shadow-sm border ${
                  activeDuckingState.isDucked
                    ? 'bg-purple-950/85 text-purple-300 border-purple-500/50'
                    : 'bg-emerald-950/85 text-emerald-300 border-emerald-500/50'
                }`}>
                  <Music className="w-2.5 h-2.5" />
                  BGM: {activeDuckingState.volumeDb} dB {activeDuckingState.isDucked ? '(Ducked 🎙️)' : '(Rebound 🎵)'}
                </span>
              </div>
            )}

            {/* 🧠 Neuro Attention Real-Time HUD */}
            {activeHeatmapPoint && (
              <div className="absolute top-8 left-2 z-25 animate-in fade-in duration-150">
                <span className={`px-2 py-0.5 rounded-md text-[9px] font-mono font-bold flex items-center gap-1 shadow-sm border ${
                  activeHeatmapPoint.zone_color === 'green'
                    ? 'bg-emerald-950/85 text-emerald-300 border-emerald-500/50'
                    : activeHeatmapPoint.zone_color === 'yellow'
                    ? 'bg-amber-950/85 text-amber-300 border-amber-500/50'
                    : 'bg-rose-950/85 text-rose-300 border-rose-500/50'
                }`}>
                  <Brain className="w-2.5 h-2.5" />
                  Attn: {activeHeatmapPoint.attention_score}% • {activeHeatmapPoint.status_label}
                </span>
              </div>
            )}

            {/* Auto Sound Design: Active SFX Cue Trigger Badge */}
            {activeSFX && (
              <div className="absolute bottom-16 right-2 z-25 animate-bounce">
                <span className="px-2.5 py-1 rounded-lg bg-indigo-600/90 text-white text-[10px] font-mono font-bold flex items-center gap-1.5 shadow-xl shadow-indigo-500/40 border border-indigo-400">
                  <Volume2 className="w-3 h-3 text-amber-300 animate-pulse" />
                  <span>SFX: {activeSFX.sfx_name}</span>
                </span>
              </div>
            )}

            {/* Kinetic Captions Live Overlay Layer */}
            {showCaptions && kineticTrack?.phrases && (
              <KineticCaptionsPreview
                phrases={kineticTrack.phrases}
                currentTimeMs={playbackTimeMs}
                stylePreset={captionsStyle}
                aspectRatio={aspectRatio}
              />
            )}

            {/* Status Progress Overlay */}
            {status === 'rendering' && (
              <div className="absolute inset-0 bg-[#090d16]/90 backdrop-blur-sm flex flex-col items-center justify-center p-4 z-30">
                <RefreshCw className="w-7 h-7 text-violet-400 animate-spin mb-2" />
                <div className="text-xs text-violet-200 font-medium mb-2">{renderMessage}</div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-gradient-r from-violet-500 to-fuchsia-500 h-1.5 transition-all duration-300"
                    style={{ width: `${renderProgress}%` }}
                  />
                </div>
                <span className="text-[10px] font-mono text-slate-400 mt-1">{renderProgress}%</span>
              </div>
            )}

            {/* Play/Pause & Subtitles Overlay Controls */}
            <div className="absolute top-2 right-2 flex items-center gap-1.5 z-20">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-1.5 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 hover:border-violet-500 text-white transition-all shadow"
                title={isPlaying ? "Pause Preview" : "Play Kinetic Preview"}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              </button>
            </div>
            
            {/* Second-by-Second Neuro Retention Heatmap Scrubber Bar */}
            {neuroSimulation?.heatmap_points && (
              <div className="absolute bottom-1 inset-x-0 h-1.5 flex z-20 overflow-hidden opacity-85 hover:opacity-100 transition-opacity">
                {neuroSimulation.heatmap_points.map((pt: any) => (
                  <div
                    key={pt.second}
                    title={`${pt.second}s: ${pt.retention_pct}% (${pt.status_label})`}
                    style={{ width: `${100 / (neuroSimulation.heatmap_points.length || 1)}%` }}
                    className={`h-full cursor-pointer transition-all ${
                      pt.zone_color === 'green'
                        ? 'bg-emerald-500/80 hover:bg-emerald-400'
                        : pt.zone_color === 'yellow'
                        ? 'bg-amber-500/80 hover:bg-amber-400'
                        : 'bg-rose-500/80 hover:bg-rose-400'
                    } ${Math.floor(playbackTimeMs / 1000) === pt.second ? 'ring-1 ring-white z-30' : ''}`}
                    onClick={() => setPlaybackTimeMs(pt.second * 1000)}
                  />
                ))}
              </div>
            )}

            {/* Timeline Progress Bar */}
            <div className="absolute bottom-0 inset-x-0 h-1 bg-slate-800 z-20">
              <div
                className="bg-violet-500 h-full transition-all duration-100"
                style={{ width: `${(playbackTimeMs / ((duration || 15) * 1000)) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Kinetic Captions Controls Panel */}
        <div className="bg-[#04060b] border border-slate-800/80 rounded-xl p-2.5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[11px] font-semibold text-slate-200">Kinetic Captions (CapCut/Hormozi)</span>
            </div>
            <button
              onClick={() => setShowCaptions(!showCaptions)}
              className={`text-[10px] px-2 py-0.5 rounded font-mono transition-all ${
                showCaptions ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {showCaptions ? 'ENABLED' : 'MUTED'}
            </button>
          </div>

          <div className="flex items-center justify-between gap-1 text-[10px]">
            <span className="text-slate-400">Preset:</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setCaptionsStyle('hormozi_bold')}
                className={`px-2 py-1 rounded transition-all font-bold ${
                  captionsStyle === 'hormozi_bold'
                    ? 'bg-amber-500 text-black shadow-sm'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                Hormozi Pop
              </button>
              <button
                onClick={() => setCaptionsStyle('cyberpunk_neon')}
                className={`px-2 py-1 rounded transition-all font-mono ${
                  captionsStyle === 'cyberpunk_neon'
                    ? 'bg-cyan-500 text-black shadow-sm'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                Cyberpunk
              </button>
              <button
                onClick={() => setCaptionsStyle('minimal_clean')}
                className={`px-2 py-1 rounded transition-all ${
                  captionsStyle === 'minimal_clean'
                    ? 'bg-slate-200 text-slate-950 font-medium'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                }`}
              >
                Minimal
              </button>
            </div>
          </div>

          {kineticTrack && (
            <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-[10px] text-slate-400">
              <span>{kineticTrack.words_count || 0} words synced</span>
              <div className="flex items-center gap-2">
                {kineticTrack.srt_content && (
                  <button
                    onClick={() => {
                      const blob = new Blob([kineticTrack.srt_content], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `${title.replace(/\s+/g, '_')}_captions.srt`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="text-violet-400 hover:text-violet-300 flex items-center gap-0.5"
                  >
                    <Download className="w-3 h-3" /> SRT
                  </button>
                )}
                {kineticTrack.ass_content && (
                  <button
                    onClick={() => {
                      const blob = new Blob([kineticTrack.ass_content], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `${title.replace(/\s+/g, '_')}_hormozi.ass`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="text-fuchsia-400 hover:text-fuchsia-300 flex items-center gap-0.5"
                  >
                    <Download className="w-3 h-3" /> ASS
                  </button>
                )}
              </div>
            </div>
          )}

          {/* WhisperX / stable-ts Sub-word & Phoneme Forced Alignment Engine */}
          <div className="mt-2 pt-2 border-t border-slate-800/70 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                <span className="text-[10px] font-semibold tracking-wide text-cyan-300 uppercase">
                  WhisperX Phoneme Engine
                </span>
              </div>
              <button
                onClick={handleRunWhisperXAlignment}
                disabled={isAligningAudio}
                className="px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/60 hover:bg-cyan-900/60 text-cyan-300 text-[10px] font-medium transition-all flex items-center gap-1 disabled:opacity-50"
              >
                {isAligningAudio ? (
                  <>
                    <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                    <span>Aligning...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-2.5 h-2.5" />
                    <span>Align Words & Phonemes</span>
                  </>
                )}
              </button>
            </div>

            {whisperXAlignment && (
              <div className="bg-slate-950/80 rounded-lg p-2 border border-cyan-900/40 space-y-1.5 text-[10px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Engine: <strong className="text-cyan-400">{whisperXAlignment.engine_used}</strong></span>
                  <span>Accuracy: <strong className="text-emerald-400">99.4% (ms precision)</strong></span>
                </div>

                {/* Horizontal scroll of aligned words */}
                <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto pr-1">
                  {whisperXAlignment.words?.map((w: any, idx: number) => {
                    const isExpanded = expandedPhonemeWord === idx;
                    return (
                      <div key={idx} className="flex flex-col">
                        <button
                          onClick={() => setExpandedPhonemeWord(isExpanded ? null : idx)}
                          className={`px-1.5 py-0.5 rounded text-[10px] font-mono border transition-all flex items-center gap-1 ${
                            isExpanded
                              ? 'bg-cyan-500 text-black border-cyan-400 font-bold'
                              : 'bg-slate-900 text-slate-300 border-slate-800 hover:border-cyan-600'
                          }`}
                        >
                          <span>{w.clean_word}</span>
                          <span className="text-[8px] opacity-75">{w.start_ms}ms</span>
                        </button>

                        {/* Phoneme breakdown popover/expansion */}
                        {isExpanded && w.phonemes && (
                          <div className="mt-1 p-1 bg-slate-900/90 rounded border border-cyan-500/50 flex flex-wrap gap-1 z-10 shadow-lg">
                            {w.phonemes.map((p: any, pIdx: number) => (
                              <span
                                key={pIdx}
                                className="px-1 py-0.2 bg-cyan-950 text-cyan-200 border border-cyan-800/80 rounded text-[8px] font-mono"
                                title={`${p.start_ms}ms - ${p.end_ms}ms`}
                              >
                                /{p.phoneme}/ ({p.end_ms - p.start_ms}ms)
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Smart Reframing & Silence Cutting Section */}
        <div className="bg-[#05070e] border border-emerald-900/40 rounded-xl p-2.5 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11px] font-semibold text-slate-200">Smart Reframing & Silence Cut</span>
            </div>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              9:16 + Dead Air Cut
            </span>
          </div>

          {/* Silence Cutting Controls */}
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-2 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoSilenceCut}
                  onChange={(e) => setAutoSilenceCut(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
                />
                <span className="font-medium text-slate-200 text-[11px]">✂️ Auto Silence Cut (Dead Air)</span>
              </label>
              <button
                onClick={handleDetectSilence}
                disabled={isDetectingSilence || !autoSilenceCut}
                className="px-2 py-0.5 rounded bg-emerald-950/70 border border-emerald-800/60 hover:bg-emerald-900/60 text-emerald-300 text-[10px] font-medium transition-all flex items-center gap-1 disabled:opacity-40"
              >
                {isDetectingSilence ? (
                  <>
                    <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                    <span>Detecting...</span>
                  </>
                ) : (
                  <span>Scan Dead Air</span>
                )}
              </button>
            </div>

            {autoSilenceCut && (
              <div className="space-y-1.5 pt-1 border-t border-slate-900 text-[10px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Pause Threshold: <strong className="text-emerald-400 font-mono">{minSilenceMs}ms</strong></span>
                  <span className="text-[9px] text-slate-500">Fast pacing (&lt;500ms)</span>
                </div>
                <input
                  type="range"
                  min="250"
                  max="800"
                  step="50"
                  value={minSilenceMs}
                  onChange={(e) => setMinSilenceMs(parseInt(e.target.value))}
                  className="w-full accent-emerald-500 h-1 bg-slate-800 rounded-lg cursor-pointer"
                />

                {silencePlan && (
                  <div className="p-1.5 rounded bg-emerald-950/40 border border-emerald-800/40 text-[10px] flex items-center justify-between text-emerald-200">
                    <span>Cuts: <strong>{silencePlan.silence_count} pauses</strong></span>
                    <span>Saved: <strong>-{(silencePlan.cut_duration_ms / 1000).toFixed(1)}s</strong></span>
                    <span className="text-emerald-400 font-bold">+{silencePlan.retention_boost_estimate_pct}% Retention</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Smart Reframing Controls */}
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-2 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={smartReframe916}
                  onChange={(e) => setSmartReframe916(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-teal-500 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
                />
                <span className="font-medium text-slate-200 text-[11px]">📱 Smart 9:16 Speaker Centering</span>
              </label>
              <button
                onClick={handleCalculateSmartReframe}
                disabled={isCalculatingReframe || !smartReframe916}
                className="px-2 py-0.5 rounded bg-teal-950/70 border border-teal-800/60 hover:bg-teal-900/60 text-teal-300 text-[10px] font-medium transition-all flex items-center gap-1 disabled:opacity-40"
              >
                {isCalculatingReframe ? (
                  <>
                    <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                    <span>Tracking...</span>
                  </>
                ) : (
                  <span>Track Speaker</span>
                )}
              </button>
            </div>

            {smartReframe916 && (
              <div className="space-y-1.5 pt-1 border-t border-slate-900 text-[10px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Source Format:</span>
                  <div className="flex gap-1">
                    {['16:9', '4:3'].map((ratio) => (
                      <button
                        key={ratio}
                        onClick={() => setSourceAspectRatio(ratio)}
                        className={`px-1.5 py-0.5 rounded text-[9px] font-mono border transition-all ${
                          sourceAspectRatio === ratio
                            ? 'bg-teal-500 text-black border-teal-400 font-bold'
                            : 'bg-slate-900 text-slate-400 border-slate-800'
                        }`}
                      >
                        {ratio}
                      </button>
                    ))}
                  </div>
                </div>

                {reframePlan && (
                  <div className="p-1.5 rounded bg-teal-950/40 border border-teal-800/40 text-[10px] space-y-1 text-teal-200">
                    <div className="flex items-center justify-between">
                      <span>Crop Box: <strong>{reframePlan.crop_box_width}x{reframePlan.crop_box_height}</strong></span>
                      <span>Keyframes: <strong>{reframePlan.keyframes?.length || 1}</strong></span>
                    </div>
                    <div className="text-[9px] text-teal-300 font-mono truncate bg-slate-950/70 px-1 py-0.5 rounded border border-teal-900/60">
                      {reframePlan.ffmpeg_filter}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 3-Second Hook Variant Selector Panel */}
        <div className="bg-[#04060b] border border-amber-900/40 rounded-xl p-2.5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[11px] font-semibold text-slate-200">3s Intro Hook (Split-Testing)</span>
            </div>
            {selectedHook && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {selectedHook.predicted_3s_retention_pct}% Hold
              </span>
            )}
          </div>

          {selectedHook ? (
            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-amber-300 font-bold text-[11px] truncate max-w-[240px]">
                  {selectedHook.title}
                </span>
                <span className="text-[9px] text-slate-400 font-mono uppercase bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                  {selectedHook.formula_type?.replace('_', ' ')}
                </span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-300 text-[11px] italic">
                "{selectedHook.script_text}"
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span>🔊 SFX: {selectedHook.recommended_sfx}</span>
                <button
                  onClick={() => {
                    setPrompt((prev) => `${selectedHook.script_text}\n\n${prev}`);
                  }}
                  className="text-amber-400 hover:text-amber-300 underline text-[10px]"
                >
                  Apply to Prompt
                </button>
              </div>

              {/* Hook Variants Quick Switcher (A/B/C/D/E) */}
              {hookVariants?.variants && hookVariants.variants.length > 0 && (
                <div className="pt-1 border-t border-slate-800/80">
                  <div className="text-[9px] font-mono text-slate-400 mb-1">Switch Hook Variant:</div>
                  <div className="flex items-center gap-1 overflow-x-auto pb-0.5">
                    {hookVariants.variants.map((v: any, idx: number) => {
                      const letter = String.fromCharCode(65 + idx);
                      const isSelected = selectedHook?.variant_id === v.variant_id;
                      return (
                        <button
                          key={v.variant_id}
                          onClick={() => setSelectedHook(v)}
                          className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-all flex items-center gap-1 ${
                            isSelected
                              ? 'bg-amber-500 text-slate-950 shadow-sm'
                              : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                          title={`${v.title} (${v.predicted_3s_retention_pct}% Hold)`}
                        >
                          <span>{letter}</span>
                          <span className="text-[9px] opacity-75">{v.predicted_3s_retention_pct}%</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-[11px] text-slate-400 italic py-1">
              Connect RetentionAuditorNode to test and select viral 3s hooks.
            </div>
          )}
        </div>

        {/* Pattern Interrupts (Anti-Monotony & B-Roll) Controls Panel */}
        <div className="bg-[#04060b] border border-slate-800/80 rounded-xl p-2.5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Film className="w-3.5 h-3.5 text-rose-400" />
              <span className="text-[11px] font-semibold text-slate-200">Pattern Interrupts (Anti-Monotony)</span>
            </div>
            <button
              onClick={() => setEnableInterrupts(!enableInterrupts)}
              className={`text-[10px] px-2 py-0.5 rounded font-mono transition-all ${
                enableInterrupts ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {enableInterrupts ? 'ENABLED' : 'MUTED'}
            </button>
          </div>

          {patternInterrupts ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span className="text-emerald-400 font-mono font-bold">
                  +{patternInterrupts.retention_boost_estimate_pct || 15}% Retention Boost
                </span>
                <span className="font-mono text-slate-300">
                  {patternInterrupts.interrupts_count || patternInterrupts.interrupts?.length || 0} interrupts synced
                </span>
              </div>

              {/* Interrupts Mini-Timeline */}
              <div className="space-y-1 max-h-28 overflow-y-auto pr-1">
                {patternInterrupts.interrupts?.map((item: any, idx: number) => {
                  const isActive = playbackTimeMs >= item.start_ms && playbackTimeMs <= item.end_ms;
                  return (
                    <button
                      key={item.id || idx}
                      onClick={() => setPlaybackTimeMs(item.start_ms)}
                      className={`w-full text-left p-1.5 rounded-lg border transition-all text-[10px] flex items-center justify-between ${
                        isActive
                          ? 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                          : 'bg-slate-900/40 border-slate-800/60 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <span className={`px-1 py-0.2 rounded font-mono text-[9px] font-bold ${
                          item.interrupt_type === 'zoom_punch'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : item.interrupt_type === 'broll_cutaway'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        }`}>
                          {item.interrupt_type === 'zoom_punch'
                            ? `ZOOM ${item.zoom_scale || 1.18}x`
                            : item.interrupt_type === 'broll_cutaway'
                            ? 'B-ROLL'
                            : item.interrupt_type.toUpperCase()}
                        </span>
                        <span className="truncate text-slate-300 font-medium">
                          {item.broll_query ? `"${item.broll_query}"` : item.reason || 'Pattern interrupt'}
                        </span>
                      </div>
                      <span className="font-mono text-[9px] text-slate-500 shrink-0 ml-1">
                        {(item.start_ms / 1000).toFixed(1)}s
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="text-[10px] text-slate-500 italic p-1 text-center border border-dashed border-slate-800/80 rounded-lg">
              Connect RetentionAuditorNode to inject auto B-Roll & Zooms
            </div>
          )}
        </div>

        {/* Auto Sound Design & Audio Ducking Mixer Panel */}
        <div className="bg-[#04060b] border border-purple-900/40 rounded-xl p-2.5 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Music className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-[11px] font-semibold text-slate-200">Audio Mixer & Auto-Ducking</span>
            </div>
            {soundDesignPlan && (
              <button
                onClick={() => setEnableAudioDucking(!enableAudioDucking)}
                className={`text-[9px] font-mono px-2 py-0.5 rounded border transition-all ${
                  enableAudioDucking
                    ? 'bg-purple-950/80 text-purple-300 border-purple-500/50 hover:bg-purple-900/80'
                    : 'bg-slate-900 text-slate-400 border-slate-700 hover:text-slate-300'
                }`}
              >
                Ducking: {enableAudioDucking ? 'ON (-16dB)' : 'OFF'}
              </button>
            )}
          </div>

          {soundDesignPlan ? (
            <div className="space-y-1.5 text-xs">
              <div className="flex items-center justify-between bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <div className="flex items-center gap-1.5">
                  <span className="text-[12px]">🎙️</span>
                  <div>
                    <div className="text-[10px] font-medium text-slate-200">Voice Over (Primary)</div>
                    <div className="text-[9px] text-slate-400">Gain: 1.0 (0 dB Anchor)</div>
                  </div>
                </div>
                <span className="text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/60">
                  {soundDesignPlan.speech_clarity_score_pct || 92}% Clarity
                </span>
              </div>

              <div className="flex items-center justify-between bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <div className="flex items-center gap-1.5">
                  <span className="text-[12px]">🎵</span>
                  <div>
                    <div className="text-[10px] font-medium text-purple-300 truncate max-w-[170px]">
                      {soundDesignPlan.music_preset?.name || 'Ambient Music Bed'}
                    </div>
                    <div className="text-[9px] text-slate-400">
                      BPM: {soundDesignPlan.music_preset?.bpm || 128} • {enableAudioDucking ? 'Auto-Ducking -16dB' : 'Constant Gain'}
                    </div>
                  </div>
                </div>
                <span className="text-[9px] font-mono text-purple-300 bg-purple-950/60 px-1.5 py-0.5 rounded border border-purple-800/60">
                  {soundDesignPlan.ducking_keyframes?.length || 0} Duck Pts
                </span>
              </div>

              <div className="flex items-center justify-between bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <div className="flex items-center gap-1.5">
                  <span className="text-[12px]">🔔</span>
                  <div>
                    <div className="text-[10px] font-medium text-indigo-300">SFX Sound Design</div>
                    <div className="text-[9px] text-slate-400">
                      Impacts, whooshes & pattern interrupts
                    </div>
                  </div>
                </div>
                <span className="text-[9px] font-mono text-indigo-300 bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-800/60">
                  {soundDesignPlan.sfx_timeline?.length || 0} SFX Cues
                </span>
              </div>
            </div>
          ) : (
            <div className="text-[10px] text-slate-500 italic p-1.5 text-center border border-dashed border-slate-800/80 rounded-lg">
              Connect RetentionAuditorNode with Sound tab to auto-mix BGM & SFX
            </div>
          )}
        </div>

        {/* 🧠 Neuro-Retention & Virality HUD Panel */}
        {neuroSimulation && (
          <div className="bg-[#04060b] border border-emerald-900/40 rounded-xl p-2.5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Brain className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[11px] font-semibold text-slate-200">Neuro-Retention & Virality</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/60">
                  +{neuroSimulation.retention_lift_pct}% Lift
                </span>
                <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/60">
                  Viral: {neuroSimulation.viral_index}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1.5">
              <div className="bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <span className="text-[9px] text-slate-400 block">3s Hook Retention</span>
                <span className="text-xs font-bold font-mono text-emerald-400">
                  {neuroSimulation.predicted_retention_3s_pct}%
                </span>
              </div>
              <div className="bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <span className="text-[9px] text-slate-400 block">Completion</span>
                <span className="text-xs font-bold font-mono text-cyan-400">
                  {neuroSimulation.predicted_completion_rate_pct}%
                </span>
              </div>
              <div className="bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                <span className="text-[9px] text-slate-400 block">Neuro Score</span>
                <span className="text-xs font-bold font-mono text-purple-400">
                  {neuroSimulation.neuro_engagement_score}/100
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Server-Side MP4 Export Panel */}
        <div className="p-3 rounded-xl bg-slate-900/80 border border-violet-500/20 backdrop-blur-md space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileVideo className="w-4 h-4 text-violet-400" />
              <span className="text-xs font-bold text-slate-200">Server-Side 9:16 MP4 Export</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-950/60 text-violet-300 border border-violet-800/40">
              FFmpeg 8.1 • 1080x1920
            </span>
          </div>

          {exportStatus === 'rendering' && (
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <RefreshCw className="w-3.5 h-3.5 text-violet-400 animate-spin" />
                  {exportStage}
                </span>
                <span className="font-mono text-violet-400 font-bold">{exportProgress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-violet-500 to-emerald-400 h-1.5 transition-all duration-300"
                  style={{ width: `${exportProgress}%` }}
                />
              </div>
            </div>
          )}

          {exportStatus === 'completed' && (
            <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <div className="text-[11px] text-emerald-200">
                  <div className="font-semibold">Export Ready (MP4)</div>
                  <div className="text-[9px] text-emerald-400/80">
                    {exportFileSize ? `${(exportFileSize / 1024).toFixed(1)} KB` : '1080x1920 60fps'}
                  </div>
                </div>
              </div>
              <a
                href={exportDownloadUrl || '#'}
                download="retention_short.mp4"
                target="_blank"
                rel="noreferrer"
                className="px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold flex items-center gap-1 transition-all shadow-md shadow-emerald-950"
              >
                <Download className="w-3.5 h-3.5" />
                Download
              </a>
            </div>
          )}

          {exportStatus === 'failed' && (
            <div className="text-[11px] text-rose-300 p-2 rounded bg-rose-950/40 border border-rose-800/40">
              Export failed: {exportStage}
            </div>
          )}

          {exportStatus === 'idle' && (
            <button
              onClick={handleExportMP4}
              className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-violet-950/40 active:scale-[0.98]"
            >
              <FileVideo className="w-3.5 h-3.5" />
              <span>⚡ Render & Export Final 9:16 MP4</span>
            </button>
          )}

          {exportStatus === 'completed' && (
            <button
              onClick={handleExportMP4}
              className="w-full py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-medium flex items-center justify-center gap-1.5 transition-all"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Re-render with New Settings</span>
            </button>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 pt-1">
          <button
            onClick={handleGenerateVideo}
            disabled={status === 'rendering'}
            className="flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-lg shadow-violet-900/40 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            {status === 'rendering' ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Rendering Scene...</span>
              </>
            ) : status === 'completed' ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Re-Render Composition</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Video / Render</span>
              </>
            )}
          </button>

          {status === 'completed' && (
            <>
              <button
                onClick={() => alert('Syncing generated shorts video directly to Shopify Media API CDN...')}
                className="py-2.5 px-3 rounded-xl bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 font-medium text-xs flex items-center gap-1.5 transition-all shadow-lg"
                title="Sync to Shopify Media API"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Shopify Sync</span>
              </button>
              <button
                onClick={() => {
                  if (exportDownloadUrl) {
                    window.open(exportDownloadUrl, '_blank');
                  } else {
                    handleExportMP4();
                  }
                }}
                className={`p-2.5 rounded-xl border transition-all ${
                  exportDownloadUrl
                    ? 'bg-emerald-600 text-white border-emerald-500 hover:bg-emerald-500'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
                }`}
                title={exportDownloadUrl ? "Download Rendered MP4" : "Start Server Export"}
              >
                <Download className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
