# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel/contracts.py"
# purpose: "Unified Pydantic SSOT machine contracts for the DNK OS Agentic Microkernel."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "Antigravity & Gerych Prime & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import hashlib
import time
import uuid
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class KernelTaskRequest(BaseModel):
    """Authoritative task request contract entering the DNK OS Microkernel."""
    task_id: str = Field(default_factory=lambda: f"tsk_{uuid.uuid4().hex[:12]}")
    goal: str = Field(..., description="High-level goal or prompt description")
    workspace_id: str = Field(default="ws-alpha-001", description="Workspace isolation partition")
    target_files: List[str] = Field(default_factory=list, description="Target File Whitelist for MASE boundaries")
    negative_scope: List[str] = Field(default_factory=list, description="Forbidden scopes and non-goals")
    created_at: float = Field(default_factory=time.time)

    def calculate_digest(self) -> str:
        """Computes deterministic digest of task request."""
        payload = f"{self.task_id}:{self.goal}:{','.join(sorted(self.target_files))}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class KernelTriageReceipt(BaseModel):
    """System One sub-second triage receipt routing the task."""
    task_id: str
    mode: Literal["SOLO", "SWARM_PARALLEL", "SWARM_SEQUENTIAL"]
    complexity_score: int = Field(..., ge=0, description="Formula: C = F + 2*D + 3*S")
    files_count: int = Field(default=0, ge=0)
    domains_count: int = Field(default=0, ge=0)
    stages_count: int = Field(default=0, ge=0)
    assigned_agents: List[str] = Field(default_factory=list)
    parallel_groups: List[List[str]] = Field(default_factory=list)
    reason: str = Field(default="")
    timestamp: float = Field(default_factory=time.time)


class KernelDecisionReceipt(BaseModel):
    """Ring 1 Epistemic Armor decision receipt preventing amnesia & sycophancy."""
    decision_id: str = Field(default_factory=lambda: f"jvr_{uuid.uuid4().hex[:16]}")
    subject: str = Field(..., description="Decision topic or architectural question")
    status: Literal["APPROVED", "REJECTED", "CHALLENGED"] = "APPROVED"
    selected_candidate: str
    score: float = Field(..., ge=0.0, le=100.0)
    margin: float = Field(default=0.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    flaws_checked: List[str] = Field(
        default_factory=list,
        description="Mandatory 3-flaws check results (Hidden risks / Boundary failures)"
    )
    integrity_sha256: str = Field(..., description="SHA-256 hash of candidates and rationale")
    timestamp: float = Field(default_factory=time.time)


class KernelCompletionReceipt(BaseModel):
    """Deterministic Master Quality Gate completion receipt."""
    task_id: str
    exit_code: int = Field(..., description="0 indicates 100% green pass")
    tests_passed: int = Field(default=0, ge=0)
    total_tests: int = Field(default=0, ge=0)
    clean_git: bool = Field(default=True, description="Working tree cleanliness check")
    evidence_hash: str = Field(..., description="Cryptographic SHA-256 hash of execution artifacts")
    duration_seconds: float = Field(default=0.0, ge=0.0)
    timestamp: float = Field(default_factory=time.time)

    @property
    def is_green(self) -> bool:
        return self.exit_code == 0 and self.clean_git


class RepoSearchRequest(BaseModel):
    """Pydantic contract for intent-expanded repo catalog search requests."""
    query: Optional[str] = Field(default=None, description="Search terms in Ukrainian or English")
    category: Optional[str] = Field(default=None, description="Domain category filter")
    agent: Optional[str] = Field(default=None, description="Target swarm agent filter")
    domain: Optional[str] = Field(default=None, description="Domain alias or module target")
    maturity_tier: Optional[str] = Field(default=None, description="Maturity tier filter (Tier 1/2/3)")
    limit: int = Field(default=10, ge=1, le=100, description="Max results to return")


class RepoSearchResultItem(BaseModel):
    """Structured search result item for repository catalog."""
    id: str
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    what_it_gives: Optional[str] = None
    assigned_agent: Optional[str] = None
    tech_stack: Optional[str] = None
    maturity_tier: Optional[str] = None
    license_track: Optional[str] = None
    dnk_module_target: Optional[str] = None
    architectural_pattern: Optional[str] = None
    sota_doc_path: Optional[str] = None
    skill_name: Optional[str] = None
    search_score: Optional[float] = None
    url: Optional[str] = None


class RepoSearchResponse(BaseModel):
    """Contract for intent-expanded repo catalog search responses."""
    query: Optional[str] = None
    expanded_query: Optional[str] = None
    is_fallback_relaxed: bool = False
    total_results: int = Field(default=0, ge=0)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    execution_ms: float = Field(default=0.0, ge=0.0)
    timestamp: float = Field(default_factory=time.time)


class AgentCapsuleSpec(BaseModel):
    """
    Role Capsule Contract for DNK Microkernel Harness (ADR-091 / DEC-004).
    Enforces strict tool budget (<= 8 tools), starting token cap (<= 6,000 tokens),
    and file lock boundaries for zero-collision parallel swarm execution.
    """
    model_config = ConfigDict(extra="forbid")

    capsule_id: str = Field(..., min_length=1, description="Unique identifier of the role capsule")
    role_name: str = Field(..., min_length=1, description="Human-readable role title")
    track: str = Field(default="dev", description="'dev' (4 core builders) or 'runtime' (4 business executors)")
    sanctioned_tools: List[str] = Field(default_factory=list, max_length=8, description="Max 8 tools allowed in capsule")
    skills_loaded: List[str] = Field(default_factory=list, description="Attached domain skills")
    max_context_tokens: int = Field(default=4500, ge=500, le=6000, description="Max standing token budget")
    target_files_lock: List[str] = Field(default_factory=list, description="Relative path globs locked by this capsule")
    can_mutate_files: bool = Field(default=False, description="Whether this capsule can write to disk")


class CompanionCritiqueBlock(BaseModel):
    """Epistemic Armor & Mandatory Dissent block generated by First Thought Companion."""
    hidden_risks: List[str] = Field(default_factory=list, description="3 critical hidden risks or failure modes")
    boundary_conditions: List[str] = Field(default_factory=list, description="Where the architecture breaks down")
    skeptic_alternative: str = Field(default="", description="Minimalist, low-overhead alternative")


class ThoughtCompanionRequest(BaseModel):
    """Input contract for the First Thought Companion & Architect Agent."""
    raw_thought: str = Field(..., min_length=1, description="Founder's raw idea, voice note, or ThoughtDSL")
    title: str = Field(default="Нова Архітектурна Ідея", description="Root concept title")
    workspace_id: str = Field(default="ws-alpha-001", description="Target workspace ID")
    existing_graph: Optional[Dict[str, Any]] = Field(default=None, description="Optional existing ThoughtDAG graph to attach to")
    parent_node_ids: List[str] = Field(default_factory=list, description="Optional upstream parent node IDs for context wiring")
    auto_assign_capsules: bool = Field(default=True, description="Automatically assign Role Capsules to task nodes")


class ThoughtCompanionResponse(BaseModel):
    """
    Output contract for the First Thought Companion & Architect Agent.
    Combines 9 global SOTA DAG/Canvas harness patterns into one deterministic response.
    """
    session_receipt_id: str = Field(..., description="Unique receipt ID")
    title: str
    dsl_script: str = Field(..., description="Synthesized ThoughtDAG 2.0 DSL script")
    thought_dag: Dict[str, Any] = Field(..., description="Validated ThoughtDAG graph with SHA-256 fingerprints & cycle check")
    xyflow_canvas: Dict[str, Any] = Field(..., description="ReactFlow / XYFlow ready nodes & edges with causal tree layout")
    obsidian_canvas: Dict[str, Any] = Field(..., description="JSON Canvas 1.0 (Kepano spec) document for Obsidian sync")
    epistemic_critique: CompanionCritiqueBlock = Field(..., description="3 Flaws, Boundary Conditions & Skeptic Alternative")
    assigned_capsules: List[AgentCapsuleSpec] = Field(default_factory=list, description="Role capsules matched to nodes")
    compiled_context_preview: str = Field(default="", description="Compiled upstream context wire prompt")
    assimilated_patterns_applied: List[str] = Field(default_factory=list, description="List of global SOTA patterns applied")


