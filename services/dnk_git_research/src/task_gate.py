# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/task_gate.py"
# purpose: "Deterministic triage gate: decides whether a task needs JIT prior-art search and assimilation, or is simple/repetitive and must skip it"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Triage gate. Zero tokens, zero network, fully explainable.

  SKIP      simple or repetitive work: write it directly, no search.
  RESEARCH  specific mechanics (interpolation, DAG, CRDT, hybrid retrieval ...):
            find prior art before writing code.
  CACHED    set by the service (not the gate) when a fresh brief for the same
            mechanics already exists: reuse it, search nothing.

Score = 2 per specific mechanic (max 3) + 2 novelty wording + scope bonuses
        - 3 per routine marker (max 2). RESEARCH when score >= THRESHOLD.
Overrides: tags force_research / jit / needs_research  ->  RESEARCH,
           tags skip_research / no_research            ->  SKIP.
"""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from services.dnk_git_research.src.domain_terms import NOVELTY, match_domains, simple_hits

THRESHOLD = 2

_STOP = {
    "this", "that", "with", "from", "into", "should", "would", "make", "implement", "create",
    "build", "задачу", "треба", "потрібно", "зроби", "додай", "створи", "реалізуй",
}


class GateMode(str, Enum):
    SKIP = "SKIP"
    RESEARCH = "RESEARCH"
    CACHED = "CACHED"


class TaskSpec(BaseModel):
    text: str
    target_files: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class GateDecision(BaseModel):
    mode: GateMode
    score: int
    threshold: int = THRESHOLD
    reasons: List[str] = Field(default_factory=list)
    need_keys: List[str] = Field(default_factory=list)
    fingerprint: str


def fingerprint(text: str, keys: List[str]) -> str:
    """Stable id of the *mechanics* in a task, so UA/EN rewordings share one cached brief."""
    if keys:
        basis = "k:" + "|".join(sorted(keys))
    else:
        tokens = sorted({t for t in re.findall(r"[^\W\d_]{4,}", (text or "").lower()) if t not in _STOP})[:12]
        basis = "t:" + "|".join(tokens)
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def decide(spec: TaskSpec, force: bool = False) -> GateDecision:
    text = spec.text or ""
    keys = [d.key for d in match_domains(text)]
    fp = fingerprint(text, keys)
    tags = {t.lower() for t in spec.tags}

    if tags & {"skip_research", "no_research"}:
        return GateDecision(mode=GateMode.SKIP, score=0, reasons=["тег skip_research"], need_keys=keys, fingerprint=fp)
    if force or tags & {"force_research", "jit", "needs_research"}:
        return GateDecision(mode=GateMode.RESEARCH, score=THRESHOLD, reasons=["примусовий пошук"], need_keys=keys, fingerprint=fp)

    score = 0
    reasons: List[str] = []

    if keys:
        score += min(len(keys), 3) * 2
        reasons.append("специфічні механіки: " + ", ".join(keys[:5]))
    if NOVELTY.search(text):
        score += 2
        reasons.append("формулювання новизни (з нуля / SOTA)")
    if score > 0:  # scope only amplifies a task that is already specific
        if len(spec.target_files) >= 4:
            score += 1
            reasons.append("зачіпає 4+ файли")
        if len(text) > 500:
            score += 1
            reasons.append("розгорнутий опис задачі")

    routine = simple_hits(text)
    if routine:
        score -= min(len(routine), 2) * 3
        reasons.append("рутинні ознаки: " + ", ".join(routine[:3]))

    if score >= THRESHOLD:
        mode = GateMode.RESEARCH
    else:
        mode = GateMode.SKIP
        if not keys and not routine:
            reasons.append("немає ознак специфічної механіки")

    return GateDecision(mode=mode, score=score, reasons=reasons, need_keys=keys, fingerprint=fp)
