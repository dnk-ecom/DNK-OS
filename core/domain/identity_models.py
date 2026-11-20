# --- DNK-MRH-HEADER ---
# mrh_id: "core/domain/identity_models.py"
# purpose: "Pydantic v2 models for User Identity, Project Workspaces, Brand DNA, and Canvas Proposals."
# canonical_source: true
# alters_files: ["core/domain/identity_models.py"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
Identity and Project Workspace Domain Models (Pydantic v2).
Formalizes UserProfile, ProjectWorkspace, BrandDNA, and Live Canvas Proposals
under DNK OS MVP Architecture (specs/02_IDENTITY_AND_PROJECTS_SPEC.md).
"""

from datetime import datetime, timezone
from enum import Enum
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _validate_relative_path(path_str: str) -> str:
    """Ensure path is strictly relative, non-empty, and does not escape root."""
    if not path_str or not path_str.strip():
        raise ValueError("Path cannot be empty.")
    normalized = path_str.strip().replace("\\", "/")
    if normalized.startswith("/") or bool(re.match(r"^[a-zA-Z]:", normalized)):
        raise ValueError(f"Absolute paths are forbidden: '{path_str}'")
    parts = Path(normalized).parts
    if ".." in parts:
        raise ValueError(f"Directory traversal ('..') is forbidden: '{path_str}'")
    return normalized


class CommunicationStyle(BaseModel):
    """User communication and tone preferences."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    conciseness: float = Field(default=0.85, ge=0.0, le=1.0, description="Preference for brevity (0.0 verbose to 1.0 ultra-compact)")
    tone: str = Field(default="direct_technical", description="Stylistic tone e.g. direct_technical, creative, executive")
    language: str = Field(default="uk", description="Communication language code (e.g. 'uk', 'en')")


class UserProfile(BaseModel):
    """User profile representing human founder or operator in DNK OS."""
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(..., description="Unique user identifier prefixed with 'usr_'")
    email: EmailStr = Field(..., description="Canonical email address")
    name: str = Field(..., min_length=1, description="Display name of the user")
    locale: str = Field(default="uk-UA", description="Locale tag for formatting and language")
    default_llm_provider: str = Field(default="vertex/gemini-2.5-pro", description="Default model routing target")
    system_role: str = Field(default="Founder / Creative Director", description="Role definition inside DNK OS")
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        if not re.match(r"^usr_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"user_id must match pattern '^usr_[a-zA-Z0-9_-]+$', got '{v}'")
        return v


class VisualStyle(BaseModel):
    """Visual aesthetic constraints of Brand DNA."""
    model_config = ConfigDict(extra="forbid")

    palette: List[str] = Field(..., min_length=1, description="Hex color codes in brand palette")
    typography: str = Field(..., min_length=1, description="Primary and secondary fonts")
    moodboard_tags: List[str] = Field(default_factory=list, description="Descriptive moodboard tags")

    @field_validator("palette")
    @classmethod
    def validate_palette(cls, colors: List[str]) -> List[str]:
        hex_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
        for color in colors:
            if not hex_pattern.match(color):
                raise ValueError(f"Invalid hex color format: '{color}'")
        return colors


class BrandDNA(BaseModel):
    """Brand identity specification governing AI worker outputs."""
    model_config = ConfigDict(extra="forbid")

    mission: str = Field(..., min_length=1, description="Core purpose and brand mission")
    target_audience: str = Field(..., min_length=1, description="Primary customer demographic and psychographic")
    visual_style: VisualStyle = Field(..., description="Visual styling constraints")
    tone_of_voice: str = Field(..., min_length=1, description="Verbal brand persona")
    negative_constraints: List[str] = Field(default_factory=list, description="Strict prohibitions (Negative Scope)")

    def extract_lod_slice(self, lod_type: str) -> Dict[str, Any]:
        """
        LOD Context Extraction helper.
        Extracts bounded prompt context (<1500 tokens) tailored to specific domain tasks.
        """
        lod_norm = lod_type.lower().strip()
        if lod_norm in ("copywriting", "text", "copy"):
            return {
                "mission": self.mission,
                "target_audience": self.target_audience,
                "tone_of_voice": self.tone_of_voice,
                "negative_constraints": self.negative_constraints,
            }
        elif lod_norm in ("visual", "image", "media", "video"):
            return {
                "visual_style": self.visual_style.model_dump(),
                "negative_constraints": self.negative_constraints,
            }
        elif lod_norm in ("minimal", "summary"):
            return {
                "mission": self.mission,
                "tone_of_voice": self.tone_of_voice,
            }
        return self.model_dump()


class AssetManifestItem(BaseModel):
    """Registered project asset with relative workspace path."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique asset identifier prefixed with 'ast_'")
    type: str = Field(..., min_length=1, description="Asset classification e.g. 'logo_svg', 'catalog_csv'")
    path: str = Field(..., description="Strictly relative path within workspace")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary asset metadata")

    @field_validator("id")
    @classmethod
    def validate_asset_id(cls, v: str) -> str:
        if not re.match(r"^ast_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"asset id must match pattern '^ast_[a-zA-Z0-9_-]+$', got '{v}'")
        return v

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        return _validate_relative_path(v)


class ProjectWorkspace(BaseModel):
    """Isolated tenant project workspace with bound Brand DNA and assets."""
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(..., description="Unique workspace ID prefixed with 'prj_'")
    owner_id: str = Field(..., description="Owner user ID prefixed with 'usr_'")
    title: str = Field(..., min_length=1, description="Project title")
    slug: str = Field(..., description="URL and directory-safe slug identifier")
    description: str = Field(default="", description="Workspace narrative summary")
    brand_dna: BrandDNA = Field(..., description="Bound Brand DNA manifest")
    assets_manifest: List[AssetManifestItem] = Field(default_factory=list, description="Air-gapped asset registry")
    enabled_plugins: List[str] = Field(
        default_factory=lambda: ["dnk_media", "dnk_commerce", "dnk_distribution"],
        description="Active FastMCP plugin workhorses",
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not re.match(r"^prj_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"project_id must match pattern '^prj_[a-zA-Z0-9_-]+$', got '{v}'")
        return v

    @field_validator("owner_id")
    @classmethod
    def validate_owner_id(cls, v: str) -> str:
        if not re.match(r"^usr_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"owner_id must match pattern '^usr_[a-zA-Z0-9_-]+$', got '{v}'")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(f"slug must be lowercase alphanumeric with hyphens, got '{v}'")
        return v

    def get_asset(self, asset_id: str) -> Optional[AssetManifestItem]:
        """Find an asset by ID within workspace boundaries."""
        for item in self.assets_manifest:
            if item.id == asset_id:
                return item
        return None


class ProposalStatus(str, Enum):
    """State machine status of a Live Canvas proposal."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFINED = "refined"
    REJECTED = "rejected"


class Proposal(BaseModel):
    """
    Live Canvas Generative Proposal presented to founder.
    Enables interactive human-in-the-loop 'Accept / Refine / Reject' feedback loop.
    """
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(..., description="Unique proposal identifier prefixed with 'prp_'")
    task_id: str = Field(..., min_length=1, description="Associated TaskTree node ID")
    project_id: str = Field(..., description="Target workspace ID")
    author_agent: str = Field(..., min_length=1, description="Agent worker that produced proposal e.g. 'dnk_commerce'")
    title: str = Field(..., min_length=1, description="Clear descriptive headline of the proposal")
    summary: str = Field(..., min_length=1, description="Detailed explanation of proposed output")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="Generated artifacts (diffs, URLs, ASTs, code)")
    status: ProposalStatus = Field(default=ProposalStatus.PENDING, description="Current approval status")
    feedback_history: List[str] = Field(default_factory=list, description="Chronological feedback iterations")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None, description="Timestamp of resolution")

    @field_validator("proposal_id")
    @classmethod
    def validate_proposal_id(cls, v: str) -> str:
        if not re.match(r"^prp_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"proposal_id must match pattern '^prp_[a-zA-Z0-9_-]+$', got '{v}'")
        return v

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not re.match(r"^prj_[a-zA-Z0-9_\-]+$", v):
            raise ValueError(f"project_id must match pattern '^prj_[a-zA-Z0-9_-]+$', got '{v}'")
        return v

    def accept(self, comment: Optional[str] = None) -> None:
        """Mark proposal as accepted by founder."""
        if self.status in (ProposalStatus.ACCEPTED, ProposalStatus.REJECTED):
            raise ValueError(f"Cannot accept proposal in terminal status '{self.status.value}'")
        self.status = ProposalStatus.ACCEPTED
        self.resolved_at = datetime.now(timezone.utc)
        if comment:
            self.feedback_history.append(f"ACCEPTED: {comment}")

    def refine(self, instruction: str) -> None:
        """Request iterative refinement with guidance."""
        if not instruction or not instruction.strip():
            raise ValueError("Refinement instruction cannot be empty.")
        if self.status == ProposalStatus.ACCEPTED:
            raise ValueError("Cannot refine an already accepted proposal.")
        self.status = ProposalStatus.REFINED
        self.feedback_history.append(f"REFINE: {instruction.strip()}")

    def reject(self, reason: str) -> None:
        """Reject proposal with stated rationale."""
        if not reason or not reason.strip():
            raise ValueError("Rejection reason cannot be empty.")
        if self.status == ProposalStatus.ACCEPTED:
            raise ValueError("Cannot reject an already accepted proposal.")
        self.status = ProposalStatus.REJECTED
        self.resolved_at = datetime.now(timezone.utc)
        self.feedback_history.append(f"REJECTED: {reason.strip()}")
