// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_canvas_swarm_page"
// purpose: "Dedicated Multi-Agent Swarm Canvas Test & Verification Page"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-20"
// author: "DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

'use client';

import React from 'react';
import dynamic from 'next/dynamic';

const MultiAgentSwarmCanvas = dynamic(
  () => import('../../../components/canvas/MultiAgentSwarmCanvas'),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-screen w-full items-center justify-center bg-[#111315] text-[#35d5d5] font-mono text-sm">
        <div className="flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-[#35d5d5] animate-ping" />
          <span>Ініціалізація Multi-Agent Swarm Canvas...</span>
        </div>
      </div>
    ),
  }
);

export default function SwarmCanvasPage() {
  return (
    <main className="h-screen w-screen overflow-hidden bg-[#111315]">
      <MultiAgentSwarmCanvas />
    </main>
  );
}
