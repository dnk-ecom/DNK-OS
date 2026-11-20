// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_canvas_remotion_KineticCaptionsPreview"
// purpose: "Kinetic Word-Level Subtitles Component (CapCut / Hormozi / Cyberpunk styles) with active word bounce and stroke"
// author: "DNK-e.com Maksym"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useMemo } from 'react';

export interface KineticWordItem {
  word: string;
  start_ms: number;
  end_ms: number;
  emphasis: 'NORMAL' | 'MEDIUM' | 'STRONG';
  color: string;
  emoji?: string | null;
  scale_factor: number;
}

export interface KineticPhraseItem {
  phrase_id: number;
  text: string;
  start_ms: number;
  end_ms: number;
  words: KineticWordItem[];
  dominant_color: string;
  lead_emoji?: string | null;
}

interface KineticCaptionsPreviewProps {
  phrases?: KineticPhraseItem[];
  currentTimeMs: number;
  stylePreset?: 'hormozi_bold' | 'minimal_clean' | 'cyberpunk_neon';
  aspectRatio?: '9:16' | '16:9' | '1:1';
}

export default function KineticCaptionsPreview({
  phrases = [],
  currentTimeMs = 0,
  stylePreset = 'hormozi_bold',
  aspectRatio = '9:16',
}: KineticCaptionsPreviewProps) {
  // Find current active phrase based on currentTimeMs
  const activePhrase = useMemo(() => {
    if (!phrases || phrases.length === 0) return null;
    return phrases.find(
      (p) => currentTimeMs >= p.start_ms && currentTimeMs <= p.end_ms
    ) || null;
  }, [phrases, currentTimeMs]);

  if (!activePhrase) {
    return null;
  }

  // Preset styles
  const isHormozi = stylePreset === 'hormozi_bold';
  const isCyberpunk = stylePreset === 'cyberpunk_neon';
  const isMinimal = stylePreset === 'minimal_clean';

  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-end items-center pb-12 px-4 z-20 overflow-hidden">
      {/* Lead Emoji Pop */}
      {activePhrase.lead_emoji && (
        <div className="text-3xl mb-1 animate-bounce drop-shadow-[0_4px_12px_rgba(0,0,0,0.8)]">
          {activePhrase.lead_emoji}
        </div>
      )}

      {/* Words Container */}
      <div className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-center max-w-[90%]">
        {activePhrase.words.map((w, idx) => {
          const isWordActive =
            currentTimeMs >= w.start_ms && currentTimeMs <= w.end_ms;

          // Compute style specifics per preset
          let textColor = w.color || '#FFFFFF';
          let strokeStyle = '2px 2px 0px #000, -2px -2px 0px #000, 2px -2px 0px #000, -2px 2px 0px #000';
          let glowEffect = '';
          let fontFamily = 'font-black tracking-tight uppercase';

          if (isHormozi) {
            textColor = isWordActive ? (w.color || '#FACC15') : '#FFFFFF';
            strokeStyle = '3px 3px 0 #000, -3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 0 4px 8px rgba(0,0,0,0.8)';
          } else if (isCyberpunk) {
            textColor = isWordActive ? '#22D3EE' : '#F43F5E';
            strokeStyle = 'none';
            glowEffect = isWordActive
              ? '0 0 16px rgba(34, 211, 238, 0.9), 0 0 32px rgba(6, 182, 212, 0.6)'
              : '0 0 8px rgba(244, 63, 94, 0.5)';
            fontFamily = 'font-extrabold tracking-wider uppercase font-mono';
          } else if (isMinimal) {
            textColor = isWordActive ? '#F8FAFC' : '#94A3B8';
            strokeStyle = 'none';
            fontFamily = 'font-semibold tracking-normal normal-case';
          }

          const scale = isWordActive
            ? (w.scale_factor || 1.15) * 1.1
            : 1.0;

          return (
            <span
              key={`${activePhrase.phrase_id}-${idx}-${w.word}`}
              className={`inline-block transition-transform duration-75 text-xl sm:text-2xl ${fontFamily}`}
              style={{
                color: textColor,
                textShadow: strokeStyle !== 'none' ? strokeStyle : glowEffect,
                transform: `scale(${scale})`,
                filter: isWordActive && isCyberpunk ? 'brightness(1.2)' : undefined,
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </div>
  );
}
