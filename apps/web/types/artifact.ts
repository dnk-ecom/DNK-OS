// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/types/artifact.ts"
// purpose: "Type definitions for DNK Live Web Component Artifacts, sandbox viewports, and export formats."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-30"
// author: "Denchik (Master Developer) & Antigravity (Mentor)"
// --- END DNK-MRH-HEADER ---

export type ArtifactKind = 'html_tailwind' | 'react_component' | 'shopify_liquid' | 'slide_deck';

export type ArtifactViewport = 'mobile' | 'tablet' | 'desktop' | 'inline';

export interface ViewportDimension {
  width: number | string;
  height: number | string;
  label: string;
}

export const VIEWPORT_DIMENSIONS: Record<ArtifactViewport, ViewportDimension> = {
  inline: { width: '100%', height: 320, label: 'Inline Auto' },
  mobile: { width: 375, height: 667, label: 'Mobile (375x667)' },
  tablet: { width: 768, height: 520, label: 'Tablet (768x520)' },
  desktop: { width: '100%', height: 580, label: 'Desktop 100%' },
};

export interface ArtifactNodeData {
  title: string;
  kind: ArtifactKind;
  code: string;
  viewport: ArtifactViewport;
  data?: Record<string, unknown>;
  author?: string;
  tags?: string[];
  lastModified?: string;
  [key: string]: unknown;
}
