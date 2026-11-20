// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/app/agents/page.tsx"
// purpose: "DNK OS Swarm & Agent Monitoring Console route"
// canonical_source: true
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

import type { Metadata } from 'next';
import dynamic from 'next/dynamic';

export const metadata: Metadata = {
  title: 'DNK OS — Agent Swarm & Orchestration Hub',
  description: 'Monitor Gerych Prime, subagent swarms, MASE execution slices, and adversarial quality gates.',
};

const DNKVisualShell = dynamic(
  () => import('../../components/shell/DNKVisualShell'),
  { ssr: false }
);

export default function AgentsPage() {
  return <DNKVisualShell />;
}
