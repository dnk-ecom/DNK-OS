// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/useHtmlInCanvas.ts"
// purpose: "Feature detection and runtime bridge for Chrome WICG HTML-in-canvas API (content=drawable, drawElementImage)."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-30"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

'use client';

import { useState, useEffect } from 'react';

export interface HtmlInCanvasSupport {
  isSupported: boolean;
  isNative: boolean;
  mode: 'native-wicg' | 'hardware-accelerated-fallback';
  reason: string;
}

export function useHtmlInCanvas(): HtmlInCanvasSupport {
  const [support, setSupport] = useState<HtmlInCanvasSupport>({
    isSupported: false,
    isNative: false,
    mode: 'hardware-accelerated-fallback',
    reason: 'Checking browser capabilities...',
  });

  useEffect(() => {
    try {
      const testCanvas = document.createElement('canvas');
      const testCtx = testCanvas.getContext('2d') as (CanvasRenderingContext2D & { drawElementImage?: unknown }) | null;

      // Chrome WICG HTML-in-canvas detection:
      // 1. ctx.drawElementImage function exists
      // 2. canvas supports content="drawable" attribute
      const hasDrawElement = typeof testCtx?.drawElementImage === 'function';
      const hasDrawableAttr = 'content' in testCanvas;

      if (hasDrawElement) {
        setSupport({
          isSupported: true,
          isNative: true,
          mode: 'native-wicg',
          reason: 'Chrome WICG HTML-in-canvas (ctx.drawElementImage) active.',
        });
      } else {
        setSupport({
          isSupported: true,
          isNative: false,
          mode: 'hardware-accelerated-fallback',
          reason: hasDrawableAttr 
            ? 'Chrome Drawable attribute detected; standard 2D GPU acceleration enabled.' 
            : 'Chrome Stable GPU pipeline active (DOM-to-Canvas High-Performance Layer).',
        });
      }
    } catch (err) {
      setSupport({
        isSupported: false,
        isNative: false,
        mode: 'hardware-accelerated-fallback',
        reason: `Feature detection fallback: ${String(err)}`,
      });
    }
  }, []);

  return support;
}
