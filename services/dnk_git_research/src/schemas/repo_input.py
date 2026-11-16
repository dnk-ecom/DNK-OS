# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/schemas/repo_input.py"
# purpose: "Pydantic Schemas for Git Research, Input Validation, and Assimilation Contracts"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-04"
# author: "DNK-e.com Maksym & Denchik Prime"
# --- END DNK-MRH-HEADER ---

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RepoSearchQuery(BaseModel):
    query: str = Field(..., description="Semantic search query for GitHub repositories")
    sort: str = Field("stars", description="Sort criteria: stars, forks, updated")
    order: str = Field("desc", description="Order: desc or asc")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of repositories to return")


class RepoMetadata(BaseModel):
    full_name: str
    name: str
    owner: str
    description: str = ""
    stars: int = 0
    forks: int = 0
    language: str = "Unknown"
    license: str = "None"
    url: str
    topics: List[str] = Field(default_factory=list)
    updated_at: Optional[str] = None


class RepoAuditResult(BaseModel):
    source_id: str
    full_name: str
    stars: int
    license: str
    assimilation_level: str
    classification_reason: str
    license_approved: bool
    url: str
    dnk_module_target: str = "core/engine"
    maturity_tier: str = "Tier 3: Discovery Radar"


class AssimilationOutput(BaseModel):
    spec_path: str
    source_id: str
    full_name: str
    status: str = "ASSIMILATED"
    target_module: str
