// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/components/canvas/ComponentSandbox.tsx"
// purpose: "Ultra-fast, isolated Component Sandbox iframe for live HTML/Tailwind, React, and Liquid previews."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-30"
// author: "Denchik (Master Developer) & Antigravity (Mentor)"
// --- END DNK-MRH-HEADER ---

import React, { useMemo, useState } from 'react';
import type { ArtifactKind, ArtifactViewport } from '../../types/artifact';
import { VIEWPORT_DIMENSIONS } from '../../types/artifact';
import { RotateCw, Smartphone, Tablet, Monitor, Layout, Copy, Check } from 'lucide-react';

interface ComponentSandboxProps {
  code: string;
  kind: ArtifactKind;
  viewport: ArtifactViewport;
  onViewportChange?: (viewport: ArtifactViewport) => void;
  className?: string;
}

export const ComponentSandbox: React.FC<ComponentSandboxProps> = ({
  code,
  kind,
  viewport,
  onViewportChange,
  className = '',
}) => {
  const [reloadKey, setReloadKey] = useState(0);
  const [copied, setCopied] = useState(false);

  const dimension = VIEWPORT_DIMENSIONS[viewport] || VIEWPORT_DIMENSIONS.inline;

  // Construct self-contained srcDoc iframe markup with Tailwind CSS CDN and Dark Teal DNK theme
  const srcDoc = useMemo(() => {
    let renderedBody = code;

    // If Shopify Liquid snippet, provide clean preview shell
    if (kind === 'shopify_liquid') {
      renderedBody = `
        <div class="shopify-section p-4">
          <div class="border border-dashed border-teal-500/40 rounded-xl p-4 bg-[#112224]/80 text-teal-200">
            <span class="text-xs uppercase font-mono tracking-wider bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded">
              Shopify Liquid Simulation
            </span>
            <div class="mt-3">
              ${code.replace(/{%\s*comment\s*%}[\s\S]*?{%\s*endcomment\s*%}/g, '')}
            </div>
          </div>
        </div>
      `;
    }

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            tealAccent: '#35d5d5',
            darkTealBg: '#1e2022',
            darkTealCard: '#162c2f',
            darkTealBorder: '#224447',
          }
        }
      }
    }
  </script>
  <style>
    body {
      margin: 0;
      padding: 16px;
      background-color: #1e2022;
      color: #d4d8db;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow-x: hidden;
      min-height: 100vh;
      box-sizing: border-box;
    }
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-thumb {
      background: #224447;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #35d5d5;
    }
  </style>
</head>
<body>
  ${renderedBody}
</body>
</html>`;
  }, [code, kind]);

  const handleCopyCode = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex flex-col rounded-lg overflow-hidden border border-[#224447] bg-[#112224]/90 ${className}`}>
      {/* Sandbox Controls Toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#112224] border-b border-[#224447] text-xs text-slate-400 select-none">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[10px] uppercase tracking-wider text-[#35d5d5] bg-[#35d5d5]/10 px-1.5 py-0.5 rounded">
            {kind}
          </span>
          <span className="text-slate-400 font-mono text-[11px]">{dimension.label}</span>
        </div>

        <div className="flex items-center gap-1">
          {/* Viewport switchers */}
          {onViewportChange && (
            <div className="flex items-center bg-[#162c2f] p-0.5 rounded border border-[#224447]/60">
              <button
                type="button"
                onClick={() => onViewportChange('mobile')}
                className={`p-1 rounded transition-colors ${
                  viewport === 'mobile' ? 'bg-[#35d5d5]/20 text-[#35d5d5]' : 'hover:text-slate-200'
                }`}
                title="Mobile Viewport (375px)"
              >
                <Smartphone className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => onViewportChange('tablet')}
                className={`p-1 rounded transition-colors ${
                  viewport === 'tablet' ? 'bg-[#35d5d5]/20 text-[#35d5d5]' : 'hover:text-slate-200'
                }`}
                title="Tablet Viewport (768px)"
              >
                <Tablet className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => onViewportChange('desktop')}
                className={`p-1 rounded transition-colors ${
                  viewport === 'desktop' ? 'bg-[#35d5d5]/20 text-[#35d5d5]' : 'hover:text-slate-200'
                }`}
                title="Desktop Viewport (100%)"
              >
                <Monitor className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => onViewportChange('inline')}
                className={`p-1 rounded transition-colors ${
                  viewport === 'inline' ? 'bg-[#35d5d5]/20 text-[#35d5d5]' : 'hover:text-slate-200'
                }`}
                title="Inline Auto"
              >
                <Layout className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Copy button */}
          <button
            type="button"
            onClick={handleCopyCode}
            className="p-1 rounded bg-[#162c2f] border border-[#224447]/60 hover:text-slate-200 hover:border-[#35d5d5]/40 transition-colors"
            title="Copy Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          {/* Reload button */}
          <button
            type="button"
            onClick={() => setReloadKey((k) => k + 1)}
            className="p-1 rounded bg-[#162c2f] border border-[#224447]/60 hover:text-slate-200 hover:border-[#35d5d5]/40 transition-colors"
            title="Reload Sandbox"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Frame Container */}
      <div className="flex justify-center items-center bg-[#1e2022] p-2 overflow-auto">
        <iframe
          key={reloadKey}
          title="Component Sandbox Preview"
          srcDoc={srcDoc}
          sandbox="allow-scripts allow-forms"
          className="border border-[#224447]/70 rounded-md shadow-inner bg-[#1e2022] transition-all duration-300"
          style={{
            width: dimension.width,
            height: dimension.height,
            maxWidth: '100%',
          }}
        />
      </div>
    </div>
  );
};
