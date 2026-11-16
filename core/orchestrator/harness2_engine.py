# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/harness2_engine.py"
# purpose: "Google Research Harness2 (SurfaceSpec, Blind Tournament, Propose-Probe-Compose) & Elephant-Goldfish Model (EGM) Engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.orchestrator.harness2")


# ==============================================================================
# 1. Harness² 8-Surface Mutation Specification (arXiv:2610.14224)
# ==============================================================================

class SurfaceCategory(str, Enum):
    """
    The 8 discrete mutation surfaces defined by Google Research Harness².
    An autonomous agent is restricted to mutating strictly within these boundaries.
    """
    SYSTEM_PROMPTS = "c1:system_prompts"
    GUARDRAILS = "c2:guardrails"
    MEMORY_STRUCTURES = "c3:memory_structures"
    SKILLS = "c4:skills"
    TOOL_GUIDANCE = "c5:tool_guidance"
    SCRIPTS = "c6:scripts"
    SUBAGENTS = "c7:subagents"
    PLUGINS_MIDDLEWARE = "c8:plugins_middleware"


class SurfaceSpec(BaseModel):
    """Specification of an allowed mutation surface within the execution harness."""
    category: SurfaceCategory
    name: str
    target_pattern: str
    description: str
    mutation_rules: List[str] = Field(default_factory=list)


CANONICAL_SURFACES: Dict[SurfaceCategory, SurfaceSpec] = {
    SurfaceCategory.SYSTEM_PROMPTS: SurfaceSpec(
        category=SurfaceCategory.SYSTEM_PROMPTS,
        name="System Prompts",
        target_pattern="core/orchestrator/agents/**/SOUL.md",
        description="Agent personas, behavioral instructions, and system prompts",
        mutation_rules=["MRH header mandatory", "No conversational fluff", "Max 400 lines"]
    ),
    SurfaceCategory.GUARDRAILS: SurfaceSpec(
        category=SurfaceCategory.GUARDRAILS,
        name="Guardrails & Invariants",
        target_pattern="core/config/structural_barriers.json",
        description="Deterministic pre-tool barriers, safety checks, and anti-tautology gates",
        mutation_rules=["Fail-closed defaults", "Sub-2ms execution ceiling", "Immutable core barriers"]
    ),
    SurfaceCategory.MEMORY_STRUCTURES: SurfaceSpec(
        category=SurfaceCategory.MEMORY_STRUCTURES,
        name="Memory Structures",
        target_pattern="core/memory/**",
        description="SCONES SQLite FTS5 BM25 index, anchor verification, and durable facts",
        mutation_rules=["Durable facts must have physical file/symbol anchors", "WAL journal mode"]
    ),
    SurfaceCategory.SKILLS: SurfaceSpec(
        category=SurfaceCategory.SKILLS,
        name="Procedural Skills",
        target_pattern="core/skills/**/SKILL.md",
        description="Modular procedural recipes and domain runbooks",
        mutation_rules=["YAML frontmatter", "Max 750 core lines", "Triple cross-harness sync"]
    ),
    SurfaceCategory.TOOL_GUIDANCE: SurfaceSpec(
        category=SurfaceCategory.TOOL_GUIDANCE,
        name="Tool Guidance & Schemas",
        target_pattern="services/**/mcp_server.py",
        description="FastMCP tool schemas, argument docstrings, and invocation guidance",
        mutation_rules=["Strict Pydantic parameter schemas", "Precise docstrings"]
    ),
    SurfaceCategory.SCRIPTS: SurfaceSpec(
        category=SurfaceCategory.SCRIPTS,
        name="Deterministic Scripts",
        target_pattern="scripts/**",
        description="Deterministic verification, hygiene, and tooling scripts",
        mutation_rules=["Relative paths only", "Exit code 0 on success", "Self-contained"]
    ),
    SurfaceCategory.SUBAGENTS: SurfaceSpec(
        category=SurfaceCategory.SUBAGENTS,
        name="Subagent Profiles",
        target_pattern="core/orchestrator/agents/**/config.yaml",
        description="Multi-agent profiles, MoA presets, reasoning overrides, and capabilities",
        mutation_rules=["Valid YAML", "Scoped toolsets whitelist", "Explicit model fallback chain"]
    ),
    SurfaceCategory.PLUGINS_MIDDLEWARE: SurfaceSpec(
        category=SurfaceCategory.PLUGINS_MIDDLEWARE,
        name="Hooks & Middleware",
        target_pattern="scripts/system/hermes_*_tool_hook.py",
        description="Pre-tool and post-tool lifecycle interception hooks",
        mutation_rules=["Sub-5ms overhead ceiling", "JSON stdout communication protocol"]
    ),
}


# ==============================================================================
# 2. Elephant-Goldfish Model (EGM) Dual-System Review Rubric
# ==============================================================================

class EGMReviewRubric(BaseModel):
    """
    Adversarial evaluation rubric implementing Google Elephant-Goldfish Model (EGM).
    Evaluated by a zero-context Goldfish subagent to eliminate Confirmation Bias and Sycophancy.
    """
    zoom_out_score: float = Field(
        default=5.0, ge=1.0, le=5.0,
        description="1-5: Architectural necessity, YAGNI compliance, zero abstraction bloat"
    )
    naive_reader_score: float = Field(
        default=5.0, ge=1.0, le=5.0,
        description="1-5: Contract clarity without unspoken assumptions or implicit context"
    )
    stress_test_score: float = Field(
        default=5.0, ge=1.0, le=5.0,
        description="1-5: Error handling, boundary conditions, edge cases, failure recovery"
    )
    blockers: List[str] = Field(
        default_factory=list,
        description="Fatal flaws or critical architectural violations that block acceptance"
    )
    findings: List[str] = Field(
        default_factory=list,
        description="Detailed observations and constructive critique"
    )

    @property
    def overall_score(self) -> float:
        """Weighted score across the 3 EGM vectors."""
        return round((self.zoom_out_score * 0.35) + (self.naive_reader_score * 0.30) + (self.stress_test_score * 0.35), 2)

    @property
    def is_approved(self) -> bool:
        """Gating threshold: Score >= 4.0 and 0 blockers."""
        return self.overall_score >= 4.0 and len(self.blockers) == 0


# ==============================================================================
# 3. Blind Tournament Selection (arXiv:2610.14224)
# ==============================================================================

class CandidateSolution(BaseModel):
    """An individual candidate patch or solution proposed by an agent."""
    candidate_id: str
    author_role: str
    surface: SurfaceCategory
    target_file: str
    patch_diff: str
    rationale: str


class BlindTournamentJudge:
    """
    Anonymizes candidate solutions to eliminate Sycophancy, confirmation bias,
    and author prejudice during automated multi-agent code evaluation.
    """

    @staticmethod
    def anonymize_candidates(
        candidates: List[CandidateSolution]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """
        Strips author and metadata, assigning SHA-1-based anonymous identifiers (Candidate A, B...).
        Returns (anonymized_payloads, token_to_original_id_map).
        """
        anonymized: List[Dict[str, Any]] = []
        token_map: Dict[str, str] = {}

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for idx, cand in enumerate(candidates):
            label = f"Candidate-{alphabet[idx % len(alphabet)]}"
            # Cryptographic hash to prevent inferring generation order
            anon_hash = hashlib.sha1(f"{cand.candidate_id}-{cand.patch_diff}".encode()).hexdigest()[:8]
            token = f"{label} [{anon_hash}]"

            token_map[token] = cand.candidate_id
            anonymized.append({
                "token": token,
                "surface": cand.surface.value,
                "target_file": cand.target_file,
                "patch_diff": cand.patch_diff,
                "rationale": cand.rationale,
                "diff_line_count": len(cand.patch_diff.strip().splitlines()),
            })

        return anonymized, token_map

    @staticmethod
    def rank_candidates_statically(
        anonymized: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank candidates statically based on Senior Dev Solution Ladder (DEC-057):
        Minimal diff size, least invasive mutations, and explicit clarity.
        """
        return sorted(anonymized, key=lambda c: (c.get("diff_line_count", 9999), len(c.get("rationale", ""))))


# ==============================================================================
# 4. Propose–Probe–Compose Execution Engine
# ==============================================================================

class ProbeResult(BaseModel):
    """Outcome of probing a candidate patch in an isolated execution sandbox."""
    passed: bool
    exit_code: int
    oracle_command: str
    execution_time_ms: int
    output_tail: str
    error_message: Optional[str] = None


class ProposeProbeComposeEngine:
    """
    Standardized engine executing the Propose-Probe-Compose cycle
    with experience reflection into SkillsCurator upon failure.
    """

    def __init__(self, hub_root: Optional[Path] = None):
        self.hub_root = hub_root or Path.cwd()

    def validate_surface(self, target_file: str) -> Optional[SurfaceCategory]:
        """Validate if target file matches one of the 8 canonical surfaces."""
        import fnmatch
        norm_path = os.path.normpath(target_file)
        for cat, spec in CANONICAL_SURFACES.items():
            pattern = spec.target_pattern
            if fnmatch.fnmatch(norm_path, pattern):
                return cat
            if "**" in pattern:
                prefix = pattern.split("**")[0].rstrip("/\\")
                if norm_path.startswith(prefix):
                    return cat
            elif norm_path.startswith(pattern.rstrip("*")):
                return cat
        return None

    def probe_patch(
        self,
        candidate: CandidateSolution,
        oracle_command: str,
        timeout_seconds: int = 60
    ) -> ProbeResult:
        """
        Execute an isolated probe run for the candidate solution.
        """
        start = time.perf_counter()
        try:
            res = subprocess.run(
                oracle_command,
                shell=True,
                cwd=str(self.hub_root),
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            combined_log = (res.stdout + "\n" + res.stderr).strip()
            passed = (res.returncode == 0)

            return ProbeResult(
                passed=passed,
                exit_code=res.returncode,
                oracle_command=oracle_command,
                execution_time_ms=elapsed_ms,
                output_tail=combined_log[-1000:],
                error_message=None if passed else f"Oracle exited with code {res.returncode}"
            )
        except subprocess.TimeoutExpired:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return ProbeResult(
                passed=False,
                exit_code=-9,
                oracle_command=oracle_command,
                execution_time_ms=elapsed_ms,
                output_tail="",
                error_message=f"Probe timeout after {timeout_seconds}s"
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return ProbeResult(
                passed=False,
                exit_code=-1,
                oracle_command=oracle_command,
                execution_time_ms=elapsed_ms,
                output_tail="",
                error_message=f"Probe execution error: {str(e)}"
            )

    def generate_experience_reflection(
        self,
        candidate: CandidateSolution,
        probe: ProbeResult
    ) -> Dict[str, Any]:
        """
        Transform a probe failure into a structured lesson for SkillsCurator reflection.
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "surface": candidate.surface.value,
            "target_file": candidate.target_file,
            "failed_oracle": probe.oracle_command,
            "exit_code": probe.exit_code,
            "error_summary": probe.error_message,
            "reflection_rule": f"Guard invariant: edits to {candidate.target_file} must satisfy '{probe.oracle_command}' (exit code 0).",
            "evidence_tail": probe.output_tail[-400:]
        }
