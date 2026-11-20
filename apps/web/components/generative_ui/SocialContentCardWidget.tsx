// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_generative_ui_SocialContentCardWidget"
// purpose: "Astryx Generative UI: Visual Social Media & Short-Form Video Card for TikTok, IG, X, and Shorts"
// author: "DNK-e.com Maksym & Denchik"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// --- END DNK-MRH-HEADER ---

"use client";

import React, { useState } from "react";
import {
  Film,
  Music,
  Heart,
  MessageSquare,
  Bookmark,
  Share2,
  Copy,
  Check,
  Play,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp,
  Volume2,
  ExternalLink,
  ArrowRight,
} from "lucide-react";

export interface SocialContentCardWidgetProps {
  platform: "tiktok" | "instagram" | "x" | "youtube_shorts";
  hook: string;
  caption: string;
  audioTrack?: string;
  scenesCount?: number;
  cta: string;
  className?: string;
  onExportScript?: () => void;
  onRenderVideo?: () => void;
}

export const SocialContentCardWidget: React.FC<SocialContentCardWidgetProps> = ({
  platform,
  hook,
  caption,
  audioTrack = "Trending Viral Audio • Beat Drops at 0:03",
  scenesCount = 4,
  cta,
  className = "",
  onExportScript,
  onRenderVideo,
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [isLiked, setIsLiked] = useState<boolean>(false);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [showScenes, setShowScenes] = useState<boolean>(false);
  const [isRendering, setIsRendering] = useState<boolean>(false);

  const handleCopyScript = () => {
    const fullScript = `[HOOK]: ${hook}\n\n[CAPTION]: ${caption}\n\n[AUDIO]: ${audioTrack}\n\n[CTA]: ${cta}`;
    navigator.clipboard.writeText(fullScript);
    setCopied(true);
    if (onExportScript) {
      onExportScript();
    }
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRender = () => {
    setIsRendering(true);
    if (onRenderVideo) {
      onRenderVideo();
    }
    setTimeout(() => setIsRendering(false), 2500);
  };

  // Platform styling & metadata
  const getPlatformDetails = () => {
    switch (platform) {
      case "tiktok":
        return {
          name: "TikTok 9:16",
          badgeColor: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
          accentColor: "#06b6d4",
          indicator: "TikTok Vertical Engine",
        };
      case "instagram":
        return {
          name: "Instagram Reels",
          badgeColor: "bg-gradient-to-r from-pink-500/10 to-amber-500/10 text-pink-400 border-pink-500/20",
          accentColor: "#ec4899",
          indicator: "Meta Reels 9:16",
        };
      case "youtube_shorts":
        return {
          name: "YouTube Shorts",
          badgeColor: "bg-rose-500/10 text-rose-400 border-rose-500/20",
          accentColor: "#f43f5e",
          indicator: "Shorts High Retention",
        };
      case "x":
        return {
          name: "X (Twitter) Post",
          badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
          accentColor: "#3b82f6",
          indicator: "Viral Post Framework",
        };
    }
  };

  const platformInfo = getPlatformDetails();

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-[#16181d] text-zinc-100 p-5 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-emerald-500/30 ${className}`}
      data-agent-target="social-content-card-widget"
    >
      {/* Astryx Header Navigation */}
      <div className="flex items-center justify-between pb-3.5 mb-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <span
            className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${platformInfo.badgeColor}`}
          >
            {platformInfo.name}
          </span>
          <span className="flex items-center gap-1 text-[11px] font-mono text-zinc-400">
            <Film className="h-3 w-3 text-emerald-400" />
            {scenesCount} Scenes (Seek-Safe)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyScript}
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
              copied
                ? "bg-emerald-500 text-zinc-950 font-bold"
                : "border border-white/10 bg-zinc-900 text-zinc-300 hover:bg-zinc-800"
            }`}
          >
            {copied ? (
              <>
                <Check className="h-3 w-3" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 text-zinc-400" />
                Copy Script
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleRender}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all ${
              isRendering
                ? "bg-emerald-400 text-zinc-950 animate-pulse"
                : "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500 hover:text-zinc-950"
            }`}
          >
            <Play className="h-3 w-3 fill-current" />
            {isRendering ? "Rendering..." : "Render Video"}
          </button>
        </div>
      </div>

      {/* Main Content Layout */}
      {platform !== "x" ? (
        /* Vertical 9:16 Video Canvas Simulation (TikTok, Reels, Shorts) */
        <div className="relative mx-auto flex flex-col justify-between overflow-hidden rounded-xl border border-white/10 bg-gradient-to-b from-zinc-950 via-zinc-900 to-black p-4 shadow-2xl min-h-[340px]">
          {/* Subtle Video Grid & Waveform Ambient Glow */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.15),transparent_60%)] pointer-events-none" />

          {/* Top Audio Bar */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black/60 px-3 py-1 text-[11px] text-zinc-300 backdrop-blur-md">
              <Music className="h-3 w-3 text-emerald-400 animate-spin" />
              <span className="line-clamp-1 max-w-[190px] font-mono">{audioTrack}</span>
            </div>
            <div className="rounded-full bg-emerald-500/20 p-1.5 text-emerald-400 border border-emerald-500/30">
              <Volume2 className="h-3 w-3" />
            </div>
          </div>

          {/* Center: Punchy Visual Hook Banner */}
          <div className="relative z-10 my-4 flex flex-col items-center justify-center text-center px-3">
            <div className="mb-2 rounded-md bg-emerald-500/20 border border-emerald-400/40 px-2 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-300">
              Pattern Interrupt • Hook (0-3s)
            </div>
            <h2 className="text-base sm:text-lg font-black tracking-tight text-white drop-shadow-md leading-snug">
              &ldquo;{hook}&rdquo;
            </h2>
          </div>

          {/* Bottom Overlay & Right Floating Engagement Sidebar */}
          <div className="relative z-10 flex items-end justify-between gap-3">
            {/* Left Bottom: Account, Caption, CTA */}
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-1.5">
                <div className="h-5 w-5 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-[10px] font-black text-black">
                  A
                </div>
                <span className="text-xs font-bold text-zinc-200">@astryx.studio</span>
                <span className="rounded-full bg-emerald-500/30 p-0.5 text-emerald-300">
                  <Check className="h-2 w-2" />
                </span>
              </div>

              <p className="text-xs text-zinc-300 line-clamp-2 leading-relaxed">
                {caption}
              </p>

              {/* High-Converting CTA Pill */}
              <div className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-bold text-black shadow-lg shadow-emerald-500/25 animate-pulse-subtle">
                <span>{cta}</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </div>

            {/* Right Action Icons Column */}
            <div className="flex flex-col items-center gap-3">
              <button
                type="button"
                onClick={() => setIsLiked(!isLiked)}
                className="flex flex-col items-center gap-0.5"
              >
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full backdrop-blur-md transition-colors ${
                    isLiked
                      ? "bg-rose-500 text-white"
                      : "bg-white/10 text-white hover:bg-white/20"
                  }`}
                >
                  <Heart className={`h-4 w-4 ${isLiked ? "fill-current" : ""}`} />
                </div>
                <span className="text-[10px] font-mono text-zinc-300">
                  {isLiked ? "24.9k" : "24.8k"}
                </span>
              </button>

              <div className="flex flex-col items-center gap-0.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 backdrop-blur-md">
                  <MessageSquare className="h-4 w-4" />
                </div>
                <span className="text-[10px] font-mono text-zinc-300">612</span>
              </div>

              <button
                type="button"
                onClick={() => setIsSaved(!isSaved)}
                className="flex flex-col items-center gap-0.5"
              >
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full backdrop-blur-md transition-colors ${
                    isSaved
                      ? "bg-amber-500 text-black"
                      : "bg-white/10 text-white hover:bg-white/20"
                  }`}
                >
                  <Bookmark className={`h-4 w-4 ${isSaved ? "fill-current" : ""}`} />
                </div>
                <span className="text-[10px] font-mono text-zinc-300">4.2k</span>
              </button>

              <div className="flex flex-col items-center gap-0.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 backdrop-blur-md">
                  <Share2 className="h-4 w-4" />
                </div>
                <span className="text-[10px] font-mono text-zinc-300">Share</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* X (Twitter) Post Simulation */
        <div className="rounded-xl border border-white/10 bg-[#111317] p-4 space-y-3">
          {/* Post Header */}
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-blue-500 to-emerald-500 flex items-center justify-center text-xs font-black text-black">
              𝕏
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-zinc-100">Astryx Autonomous</span>
                <span className="text-blue-400">✓</span>
                <span className="text-[11px] text-zinc-500">@astryx_os • 2m</span>
              </div>
              <span className="text-[10px] text-zinc-400 font-mono">Verified Growth Agent</span>
            </div>
          </div>

          {/* Hook & Caption */}
          <div className="space-y-2 text-sm text-zinc-200">
            <p className="font-bold text-white leading-snug">{hook}</p>
            <p className="text-xs text-zinc-300 whitespace-pre-line leading-relaxed">
              {caption}
            </p>
          </div>

          {/* CTA Box Preview */}
          <div className="rounded-lg border border-white/10 bg-zinc-900/80 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-emerald-400" />
              <span className="text-xs font-semibold text-zinc-200">{cta}</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-mono">astryx.link/boost</span>
          </div>

          {/* Engagement Footer */}
          <div className="flex justify-between pt-2 border-t border-white/5 text-xs text-zinc-400 font-mono">
            <span className="flex items-center gap-1 hover:text-blue-400 cursor-pointer">
              <MessageSquare className="h-3.5 w-3.5" /> 84
            </span>
            <span className="flex items-center gap-1 hover:text-emerald-400 cursor-pointer">
              <Share2 className="h-3.5 w-3.5" /> 312
            </span>
            <span className="flex items-center gap-1 hover:text-rose-400 cursor-pointer">
              <Heart className="h-3.5 w-3.5" /> 1.9k
            </span>
            <span className="flex items-center gap-1 hover:text-amber-400 cursor-pointer">
              <Bookmark className="h-3.5 w-3.5" /> 450
            </span>
          </div>
        </div>
      )}

      {/* Expandable Scene Breakdown */}
      <div className="mt-3 pt-3 border-t border-white/5">
        <button
          type="button"
          onClick={() => setShowScenes(!showScenes)}
          className="flex items-center justify-between w-full text-xs text-zinc-400 hover:text-zinc-200"
        >
          <span className="flex items-center gap-1.5 font-mono">
            <Layers className="h-3.5 w-3.5 text-emerald-400" />
            HyperFrames Video Scene Breakdown ({scenesCount} blocks)
          </span>
          {showScenes ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
        </button>

        {showScenes && (
          <div className="mt-2.5 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
            <div className="rounded-lg border border-white/5 bg-zinc-900/60 p-2.5">
              <span className="text-emerald-400 font-bold">Scene 1 (0-3s):</span> Pattern Interrupt & Hook overlay
            </div>
            <div className="rounded-lg border border-white/5 bg-zinc-900/60 p-2.5">
              <span className="text-cyan-400 font-bold">Scene 2 (3-8s):</span> Agitation & High-friction problem demo
            </div>
            <div className="rounded-lg border border-white/5 bg-zinc-900/60 p-2.5">
              <span className="text-purple-400 font-bold">Scene 3 (8-18s):</span> Product transformation & proof
            </div>
            <div className="rounded-lg border border-white/5 bg-zinc-900/60 p-2.5">
              <span className="text-amber-400 font-bold">Scene 4 (18-24s):</span> Urgent CTA & link in bio trigger
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
