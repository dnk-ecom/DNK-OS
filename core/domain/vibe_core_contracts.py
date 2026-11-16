# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/vibe_core_contracts.py"
# purpose: "Canonical Pydantic v2 contracts for DNK Core v1 Vibe-Coder Model (Account, ProjectDNA, Track, SubtaskNode, DualSurfaceAction)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentRole(str, Enum):
    STRATEGIST = "strategist"
    ARCHITECT = "architect"
    BUILDER_DENCHIK = "denchik"
    AUDITOR_GERYСH = "gerych"
    DOMAIN_SHOPIFY = "dnk_shopify"
    DOMAIN_MEDIA = "dnk_media"
    DOMAIN_DISTRIBUTION = "dnk_distribution"


class TrackKind(str, Enum):
    CORE_RND = "core_rnd"               # Track 1: Product Foundry
    MARKETING_SALES = "marketing_sales" # Track 2: Funnels, PDP, Lead Magnets
    DONOR_AUDIT = "donor_audit"         # Track 3: Reverse-Engineering & Benchmarks


class NodeLifecycleState(str, Enum):
    CHAT_DRAFT = "chat_draft"
    DECOMPOSED = "decomposed"
    AUDIT_GATE = "audit_gate"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    VERIFIED = "verified"
    FAILED = "failed"
    CRYSTALLIZED = "crystallized"


class ActionSurfaceMode(str, Enum):
    DUAL = "dual"           # Exposed both to LLM FastMCP & React UI
    AGENT_ONLY = "agent"    # Internal automated step
    HUMAN_ONLY = "human"    # Final founder sign-off / destructive action


class DualSurfaceActionSpec(BaseModel):
    """Unified Action Contract (BuilderIO/agent-native parity for FastMCP + React UI)."""
    model_config = ConfigDict(extra="ignore")

    action_id: str = Field(..., pattern=r"^[a-z0-9_]+\.[a-z0-9_]+$", description="e.g. 'shopify.run_theme_check'")
    label_uk: str = Field(..., description="UI button label in Ukrainian for Vibe-Coder")
    description_en: str = Field(..., description="Semantic description for LLM tool selection")
    surface_mode: ActionSurfaceMode = Field(default=ActionSurfaceMode.DUAL)
    mcp_brick: str = Field(..., description="Target FastMCP brick or kernel endpoint")
    mcp_tool_name: str = Field(..., description="Exact FastMCP tool name")
    input_json_schema: Dict[str, Any] = Field(default_factory=dict, description="Shared JSON Schema for tool & UI form")
    ui_widget: Literal["button", "approve_reject", "diff_viewer", "checklist", "form_drawer"] = "button"
    ui_tone: Literal["primary", "secondary", "danger", "approve"] = "secondary"
    requires_human_confirmation: bool = Field(default=False)
    idempotent: bool = Field(default=True)
    allowed_states: List[NodeLifecycleState] = Field(
        default_factory=lambda: [NodeLifecycleState.DECOMPOSED, NodeLifecycleState.AWAITING_APPROVAL]
    )


class AccountServiceBinding(BaseModel):
    model_config = ConfigDict(extra="ignore")

    service_id: str
    mount_mode: Literal["in_ram_fastmcp", "apfs_worktree_pool", "sqlite_wal_bus"]
    endpoint_or_module: str
    healthcheck_cmd: str


class GoldenRecipeRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recipe_id: str
    title: str
    version: str = "1.0.0"
    source_project_id: str
    required_dna_fields: List[str] = Field(default_factory=list)
    canvas_template_path: str = Field(..., description="Relative path e.g. ./templates/recipes/shopify_launch.canvas")
    verified_runs_count: int = Field(default=0, ge=0)


class AccountSpec(BaseModel):
    """L1 Account Level: Sovereign Vibe-Coder Workstation & Global Memory."""
    model_config = ConfigDict(extra="ignore")

    account_id: str = Field(..., description="e.g. 'acct-dnk-maksym'")
    owner_name: str
    comms_language: Literal["uk"] = "uk"
    code_language: Literal["en"] = "en"
    tone_of_voice: str = Field(..., description="Global founder communication & UX voice principles")
    system_invariants: List[str] = Field(default_factory=list, description="L1 SCONES immutable rules")
    system_services: List[AccountServiceBinding] = Field(default_factory=list)
    sovereign_team: List[AgentRole] = Field(
        default_factory=lambda: [
            AgentRole.STRATEGIST,
            AgentRole.ARCHITECT,
            AgentRole.BUILDER_DENCHIK,
            AgentRole.AUDITOR_GERYСH,
        ]
    )
    sanctioned_skill_catalog: List[str] = Field(default_factory=list)
    golden_recipes: List[GoldenRecipeRef] = Field(default_factory=list)
    sacred_prompt_budget_tokens: int = Field(default=6000, le=6000)


class DesignSystemTokens(BaseModel):
    model_config = ConfigDict(extra="ignore")

    primary_colors: Dict[str, str] = Field(default_factory=dict, description="Hex tokens e.g. {'bg': '#0B0F17', 'accent': '#10B981'}")
    typography: Dict[str, str] = Field(default_factory=dict, description="Heading/body font families and scale")
    spacing_unit_px: int = Field(default=4, ge=1)
    border_radius_px: int = Field(default=8, ge=0)
    component_rules: List[str] = Field(default_factory=list)


class ICPProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    segment_name: str
    pain_points: List[str] = Field(min_length=1)
    value_proposition: str
    brand_voice_rules: List[str] = Field(default_factory=list)
    forbidden_cliches: List[str] = Field(default_factory=list)


class TrackSpec(BaseModel):
    """Functional Workstream inside a Business Project (1..N)."""
    model_config = ConfigDict(extra="ignore")

    track_id: str
    project_id: str
    kind: TrackKind
    title: str
    mission: str
    assigned_workhorse: Literal["dnk_shopify", "dnk_media", "dnk_distribution", "core"]
    repo_root_rel: str = Field(..., description="Strictly relative path e.g. ./services/dnk_shopify/DNK_Horizon_Tinker")
    root_canvas_path: str
    default_actions: List[DualSurfaceActionSpec] = Field(default_factory=list)
    deterministic_gates: List[str] = Field(default_factory=list, description="CLI commands that must return exit 0")


class ProjectDNA(BaseModel):
    """L2 Business Project Memory: Filled ONCE, auto-inherited by all Tracks & Nodes."""
    model_config = ConfigDict(extra="ignore")

    project_id: str = Field(..., pattern=r"^proj-[a-z0-9-]+$")
    account_id: str
    project_name: str
    domain_type: Literal["shopify_theme", "saas_app", "agency_pipeline", "media_product"]
    design_system: DesignSystemTokens
    icp: ICPProfile
    business_rules: List[str] = Field(default_factory=list)
    technical_constraints: List[str] = Field(default_factory=list)
    tracks: List[TrackSpec] = Field(..., min_length=1)
    system_inside_system_mode: bool = Field(
        default=True,
        description="Separates Base Core Foundry from Client Deployment Presets"
    )
    dna_version: str = "1.0.0"
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("tracks")
    @classmethod
    def ensure_unique_track_ids(cls, tracks: List[TrackSpec]) -> List[TrackSpec]:
        ids = [t.track_id for t in tracks]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate track_id detected in ProjectDNA")
        return tracks


class VerificationCriteria(BaseModel):
    model_config = ConfigDict(extra="ignore")

    command: str = Field(..., description="Deterministic verification command e.g. 'shopify theme check --fail-level error'")
    expected_exit_code: int = 0
    required_artifacts: List[str] = Field(default_factory=list)
    anti_mock_live_check: Optional[str] = Field(default=None, description="Live HTTP/DOM/FastMCP assertion")


class SubtaskNodeSpec(BaseModel):
    """L3 Task/Subtask Node on ThoughtDAG Canvas with Dual-Surface Actions."""
    model_config = ConfigDict(extra="ignore")

    node_id: str
    canvas_id: str
    project_id: str
    track_id: str
    parent_node_id: Optional[str] = None
    session_id: str = Field(..., description="Isolated SQLite WAL thread: 'node:{canvas_id}:{node_id}'")
    title: str
    goal: str
    assigned_agent: AgentRole
    state: NodeLifecycleState = NodeLifecycleState.CHAT_DRAFT

    # Anti-degradation & Zero-Waste MASE boundaries
    target_file_whitelist: List[str] = Field(default_factory=list)
    negative_scope: List[str] = Field(default_factory=list)
    sanctioned_skills: List[str] = Field(default_factory=list, max_length=5)
    max_tool_calls: int = Field(default=25, ge=1, le=25)
    worktree_branch: Optional[str] = None

    # Context Wire Inheritance (Artifacts only, zero raw parent chat logs)
    inherited_parent_contract: Dict[str, Any] = Field(default_factory=dict)
    actions: List[DualSurfaceActionSpec] = Field(default_factory=list)
    verification: VerificationCriteria

    # Crystallization output
    crystallized_output: Optional[Dict[str, Any]] = None
    receipt_sha256: Optional[str] = None
