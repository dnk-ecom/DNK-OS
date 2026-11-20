// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/app/shell/page.tsx"
// purpose: "DNK OS Visual Shell route — dynamic import of DNKVisualShell (no SSR)."
// canonical_source: true
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-15"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

import type { Metadata } from 'next';
import dynamic from 'next/dynamic';

export const metadata: Metadata = {
  title: 'DNK OS — Visual Shell | Kernel Dashboard',
  description: 'DNK OS Visual Shell — real-time kernel dashboard. Monitor SaaP services, agent swarms and system events.',
};

const DNKVisualShell = dynamic(
  () => import('../../components/shell/DNKVisualShell'),
  { ssr: false }
);

export default function ShellPage() {
  return <DNKVisualShell />;
}
