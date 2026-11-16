# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/schemas/brief.py"
# purpose: "Pydantic contracts for the Reuse Brief returned to an agent before it writes code"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from services.dnk_git_research.src.license_policy import LicenseClass, ReuseAction
from services.dnk_git_research.src.task_gate import GateDecision, GateMode


class Verdict(str, Enum):
    ADOPT = "ADOPT"
    ADAPT = "ADAPT"
    CLEAN_ROOM = "CLEAN_ROOM"
    BUILD = "BUILD"


class CandidateOut(BaseModel):
    repo_id: str
    url: str
    source: str  # "catalog" | "github"
    title: str = ""
    why: str = ""
    tier: str = "Tier 3: Discovery Radar"
    stars: Optional[int] = None
    relevance: float = 0.0  # share of the need's terms found in the repo text
    matched_terms: List[str] = Field(default_factory=list)
    license_raw: str = ""
    license_spdx: Optional[str] = None
    license_class: LicenseClass = LicenseClass.UNKNOWN
    license_evidence: str = "none"
    action: ReuseAction = ReuseAction.CLEAN_ROOM
    can_depend: bool = False
    can_copy_code: bool = False
    existing_doc: Optional[str] = None
    assimilation_status: Optional[str] = None


class NeedResult(BaseModel):
    key: str
    need: str
    terms: List[str] = Field(default_factory=list)
    verdict: Verdict
    candidates: List[CandidateOut] = Field(default_factory=list)
    next_step: str = ""
    notes: List[str] = Field(default_factory=list)


class ReuseBrief(BaseModel):
    mode: GateMode
    source: str  # "gate" | "fresh" | "cache"
    fingerprint: str
    gate: GateDecision
    needs: List[NeedResult] = Field(default_factory=list)
    summary: str = ""
    notes: List[str] = Field(default_factory=list)
    generated_at: str = ""
