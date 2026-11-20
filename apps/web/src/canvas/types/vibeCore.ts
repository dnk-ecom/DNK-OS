// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/src/canvas/types/vibeCore.ts"
// purpose: "Canonical TypeScript interfaces mirroring Python Pydantic v2 contracts for DNK Canvas UI."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-16"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

export type AgentRole =
  | 'strategist'
  | 'architect'
  | 'denchik'
  | 'gerych'
  | 'dnk_shopify'
  | 'dnk_media'
  | 'dnk_distribution';

export type TrackKind = 'core_rnd' | 'marketing_sales' | 'donor_audit';

export type NodeLifecycleState =
  | 'chat_draft'
  | 'decomposed'
  | 'audit_gate'
  | 'running'
  | 'awaiting_approval'
  | 'verified'
  | 'failed'
  | 'crystallized';

export type ActionSurfaceMode = 'dual' | 'agent' | 'human';

export type ActionUIWidget =
  | 'button'
  | 'approve_reject'
  | 'diff_viewer'
  | 'checklist'
  | 'form_drawer';

export interface DualSurfaceActionSpec {
  action_id: string;
  label_uk: string;
  description_en: string;
  surface_mode: ActionSurfaceMode;
  mcp_brick: string;
  mcp_tool_name: string;
  input_json_schema?: Record<string, unknown>;
  ui_widget?: ActionUIWidget;
  ui_tone?: 'primary' | 'secondary' | 'danger' | 'approve';
  requires_human_confirmation?: boolean;
  idempotent?: boolean;
  allowed_states?: NodeLifecycleState[];
}

export interface AccountServiceBinding {
  service_id: string;
  mount_mode: 'in_ram_fastmcp' | 'apfs_worktree_pool' | 'sqlite_wal_bus';
  endpoint_or_module: string;
  healthcheck_cmd: string;
}

export interface GoldenRecipeRef {
  recipe_id: string;
  title: string;
  version: string;
  source_project_id: string;
  required_dna_fields: string[];
  canvas_template_path: string;
  verified_runs_count: number;
}

export interface AccountSpec {
  account_id: string;
  owner_name: string;
  comms_language: 'uk';
  code_language: 'en';
  tone_of_voice: string;
  system_invariants: string[];
  system_services: AccountServiceBinding[];
  sovereign_team: AgentRole[];
  sanctioned_skill_catalog: string[];
  golden_recipes: GoldenRecipeRef[];
  sacred_prompt_budget_tokens: number;
}

export interface DesignSystemTokens {
  primary_colors: Record<string, string>;
  typography: Record<string, string>;
  spacing_unit_px: number;
  border_radius_px: number;
  component_rules: string[];
}

export interface ICPProfile {
  segment_name: string;
  pain_points: string[];
  value_proposition: string;
  brand_voice_rules: string[];
  forbidden_cliches: string[];
}

export interface TrackSpec {
  track_id: string;
  project_id: string;
  kind: TrackKind;
  title: string;
  mission: string;
  assigned_workhorse: 'dnk_shopify' | 'dnk_media' | 'dnk_distribution' | 'core';
  repo_root_rel: string;
  root_canvas_path: string;
  default_actions: DualSurfaceActionSpec[];
  deterministic_gates: string[];
}

export interface ProjectDNA {
  project_id: string;
  account_id: string;
  project_name: string;
  domain_type: 'shopify_theme' | 'saas_app' | 'agency_pipeline' | 'media_product';
  design_system: DesignSystemTokens;
  icp: ICPProfile;
  business_rules: string[];
  technical_constraints: string[];
  tracks: TrackSpec[];
  system_inside_system_mode: boolean;
  dna_version: string;
  updated_at: string;
}

export interface VerificationCriteria {
  command: string;
  expected_exit_code: number;
  required_artifacts: string[];
  anti_mock_live_check?: string;
}

export interface SubtaskNodeSpec {
  node_id: string;
  canvas_id: string;
  project_id: string;
  track_id: string;
  parent_node_id?: string;
  session_id: string;
  title: string;
  goal: string;
  assigned_agent: AgentRole;
  state: NodeLifecycleState;
  target_file_whitelist: string[];
  negative_scope: string[];
  sanctioned_skills: string[];
  max_tool_calls: number;
  worktree_branch?: string;
  inherited_parent_contract: Record<string, unknown>;
  actions: DualSurfaceActionSpec[];
  verification: VerificationCriteria;
  crystallized_output?: Record<string, unknown>;
  receipt_sha256?: string;
}
