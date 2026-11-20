// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/app/docs/types.ts"
// purpose: "TypeScript types for Tri-Audience Documentation & Client Delivery Portal"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-23"
// author: "DNK-e.com Maksym & Gerych Prime"
// --- END DNK-MRH-HEADER ---

export type AudienceRole = 'god' | 'agent' | 'client';

export interface DocStepItem {
  step_number: number;
  title: string;
  description: string;
  status: 'completed' | 'active' | 'upcoming' | string;
}

export interface DocCalloutBlock {
  type: 'info' | 'warning' | 'success' | 'danger' | string;
  title: string;
  body: string;
}

export interface DocPageItem {
  id: string;
  project_id: string;
  slug: string;
  title: string;
  category: string;
  visibility: 'god_only' | 'agent_visible' | 'client' | string;
  summary: string;
  content_md: string;
  steps: DocStepItem[];
  callouts: DocCalloutBlock[];
  target_file_whitelist: string[];
  negative_scope: string[];
  updated_at: string;
}

export interface MilestoneItem {
  id: string;
  project_id: string;
  stage_number: number;
  title: string;
  description: string;
  status: 'completed' | 'in_progress' | 'pending' | 'approved' | 'changes_requested' | string;
  estimated_hours: number;
  spent_hours: number;
  deliverables: string[];
  approved_by?: string | null;
  approved_at?: string | null;
}

export interface TicketComment {
  id: string;
  author: string;
  role: string;
  text: string;
  created_at: string;
}

export interface ClientTicketItem {
  id: string;
  project_id: string;
  milestone_id?: string | null;
  title: string;
  description: string;
  category: string;
  status: 'draft' | 'pending_review' | 'approved' | 'in_progress' | 'completed' | 'changes_requested' | string;
  priority: string;
  estimated_hours: number;
  spent_hours: number;
  assigned_agent: string;
  target_file_whitelist: string[];
  negative_scope: string[];
  acceptance_criteria: string[];
  taskdna_id?: string | null;
  taskforest_node_id?: string | null;
  obsidian_note_path?: string | null;
  created_by: string;
  approved_by?: string | null;
  approved_at?: string | null;
  comments: TicketComment[];
  created_at: string;
  updated_at: string;
}

export interface PortalWorkspaceBundle {
  project: {
    id: string;
    name: string;
    client_name?: string;
    brand_color?: string;
    budget_hours_total?: number;
    status?: string;
  };
  subject: {
    id: string;
    email: string;
    name: string;
    role: AudienceRole;
    project_ids: string[];
  };
  effective_role: AudienceRole;
  rbac_isolation_verified: boolean;
  metrics: {
    estimated_hours_total: number;
    spent_hours_total: number;
    budget_hours_cap: number;
    milestones_total: number;
    milestones_approved: number;
    tickets_total: number;
    tickets_approved: number;
    taskdna_ready_count: number;
  };
  page_tree: DocPageItem[];
  milestones: MilestoneItem[];
  tickets: ClientTicketItem[];
  taskdna_queue: Array<Record<string, any>>;
}
