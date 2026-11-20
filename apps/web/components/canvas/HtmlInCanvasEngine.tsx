// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/HtmlInCanvasEngine.tsx"
// purpose: "Hardware-accelerated HTML-in-canvas overlay engine for ultra-high node density rendering at 60+ FPS."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-30"
// author: "Antigravity & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useReactFlow, useViewport } from '@xyflow/react';
import { useCanvasStore } from '../../store/canvasStore';
import { useHtmlInCanvas } from './useHtmlInCanvas';
import { Cpu, Zap } from 'lucide-react';

interface HtmlInCanvasEngineProps {
  enabled: boolean;
}

export const HtmlInCanvasEngine: React.FC<HtmlInCanvasEngineProps> = ({ enabled }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const support = useHtmlInCanvas();
  const { x, y, zoom } = useViewport();
  const nodes = useCanvasStore((s) => s.nodes);
  const { getNodes } = useReactFlow();
  const [fps, setFps] = useState(60);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  // Render loop using requestAnimationFrame or paint events
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !enabled) return;

    const ctx = canvas.getContext('2d') as (CanvasRenderingContext2D & {
      drawElementImage?: (el: HTMLElement, x: number, y: number) => void;
    }) | null;
    if (!ctx) return;

    // Adjust canvas resolution for Retina displays
    const dpr = window.devicePixelRatio || 1;
    const width = window.innerWidth;
    const height = window.innerHeight;

    if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
    }

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, width, height);

    // Apply viewport transform (pan & zoom)
    ctx.translate(x, y);
    ctx.scale(zoom, zoom);

    const liveNodes = getNodes();

    // Render nodes
    for (const node of liveNodes) {
      const nodeX = node.position.x;
      const nodeY = node.position.y;
      const nodeWidth = (node.measured?.width || (node as unknown as { width?: number }).width || 320);
      const nodeHeight = (node.measured?.height || (node as unknown as { height?: number }).height || 180);

      // Frustum culling: skip nodes outside viewport
      const screenX = nodeX * zoom + x;
      const screenY = nodeY * zoom + y;
      const screenW = nodeWidth * zoom;
      const screenH = nodeHeight * zoom;

      if (
        screenX + screenW < -100 ||
        screenX > width + 100 ||
        screenY + screenH < -100 ||
        screenY > height + 100
      ) {
        continue;
      }

      // If native WICG drawElementImage is available, draw DOM directly
      const domElement = document.querySelector(`[data-id="${node.id}"]`) as HTMLElement | null;
      if (support.isNative && domElement && ctx.drawElementImage) {
        try {
          ctx.drawElementImage(domElement, nodeX, nodeY);
          continue;
        } catch {
          // Fall through to hardware acceleration box
        }
      }

      // High-performance hardware-accelerated fallback card rendering
      const isTask = node.type === 'agentTask';
      const nodeColor = (node.data as { color?: string })?.color || (isTask ? '#8b5cf6' : '#3b82f6');

      // Card Background with smooth rounded corners
      ctx.beginPath();
      const radius = 12;
      ctx.roundRect(nodeX, nodeY, nodeWidth, nodeHeight, radius);
      ctx.fillStyle = '#111827ee';
      ctx.fill();

      // Glowing border
      ctx.lineWidth = 2 / zoom;
      ctx.strokeStyle = nodeColor;
      ctx.stroke();

      // Top Header bar
      ctx.fillStyle = `${nodeColor}22`;
      ctx.beginPath();
      ctx.roundRect(nodeX, nodeY, nodeWidth, 36, [radius, radius, 0, 0]);
      ctx.fill();

      // Title
      ctx.font = 'bold 13px system-ui, -apple-system, sans-serif';
      ctx.fillStyle = '#f3f4f6';
      const title = (node.data as { title?: string; label?: string })?.title ||
                    (node.data as { label?: string })?.label ||
                    node.id;
      ctx.fillText(String(title).substring(0, 32), nodeX + 14, nodeY + 23);

      // Status indicator tag
      const status = (node.data as { status?: string })?.status;
      if (status) {
        ctx.font = '10px system-ui, sans-serif';
        ctx.fillStyle = '#9ca3af';
        ctx.fillText(`[${status}]`, nodeX + nodeWidth - 75, nodeY + 23);
      }
    }

    ctx.restore();

    // FPS calculation
    frameCountRef.current++;
    const now = performance.now();
    if (now - lastTimeRef.current >= 1000) {
      setFps(Math.round((frameCountRef.current * 1000) / (now - lastTimeRef.current)));
      frameCountRef.current = 0;
      lastTimeRef.current = now;
    }
  }, [enabled, x, y, zoom, getNodes, support.isNative]);

  useEffect(() => {
    if (!enabled) return;
    let animId: number;

    const loop = () => {
      renderCanvas();
      animId = requestAnimationFrame(loop);
    };

    animId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animId);
  }, [enabled, renderCanvas]);

  if (!enabled) return null;

  return (
    <>
      <canvas
        ref={canvasRef}
        // WICG Chrome 157+ HTML-in-canvas attribute
        {...{ content: 'drawable' }}
        className="pointer-events-none absolute inset-0 z-0"
      />
      {/* Live GPU HUD badge */}
      <div className="pointer-events-none absolute bottom-4 left-4 z-40 flex items-center gap-2 rounded-lg border border-purple-500/30 bg-gray-900/90 px-3 py-1.5 text-xs text-purple-300 shadow-xl backdrop-blur-md">
        <Zap className="h-3.5 w-3.5 text-yellow-400 animate-pulse" />
        <span className="font-semibold">HTML-in-Canvas Turbo</span>
        <span className="rounded bg-purple-950/80 px-1.5 py-0.5 text-[10px] text-purple-200">
          {support.mode === 'native-wicg' ? 'WICG Native' : 'GPU 60+ FPS'}
        </span>
        <span className="flex items-center gap-1 text-emerald-400 font-mono">
          <Cpu className="h-3 w-3" />
          {fps} FPS ({nodes.length} nodes)
        </span>
      </div>
    </>
  );
};
