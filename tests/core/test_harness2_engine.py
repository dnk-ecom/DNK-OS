# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_harness2_engine.py"
# purpose: "Test suite for Google Research Harness2 Engine & Elephant-Goldfish Model (EGM)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import pytest
from core.orchestrator.harness2_engine import (
    CANONICAL_SURFACES,
    BlindTournamentJudge,
    CandidateSolution,
    EGMReviewRubric,
    ProposeProbeComposeEngine,
    SurfaceCategory,
)


def test_harness2_eight_canonical_surfaces():
    """Verify all 8 mutation surfaces (c1..c8) from Harness2 are registered."""
    assert len(CANONICAL_SURFACES) == 8
    expected_categories = {
        SurfaceCategory.SYSTEM_PROMPTS,
        SurfaceCategory.GUARDRAILS,
        SurfaceCategory.MEMORY_STRUCTURES,
        SurfaceCategory.SKILLS,
        SurfaceCategory.TOOL_GUIDANCE,
        SurfaceCategory.SCRIPTS,
        SurfaceCategory.SUBAGENTS,
        SurfaceCategory.PLUGINS_MIDDLEWARE,
    }
    assert set(CANONICAL_SURFACES.keys()) == expected_categories


def test_egm_review_rubric_approval():
    """Verify Elephant-Goldfish Model (EGM) 3-Flaws rubric approval threshold."""
    # Approved: high scores across all 3 vectors, zero blockers
    rubric = EGMReviewRubric(
        zoom_out_score=4.5,
        naive_reader_score=4.0,
        stress_test_score=4.5,
        blockers=[],
        findings=["Clean implementation with zero bloat"]
    )
    assert rubric.overall_score >= 4.0
    assert rubric.is_approved is True


def test_egm_review_rubric_rejection_on_blocker():
    """Verify EGM instantly rejects output if any blocker is detected, even with high scores."""
    rubric = EGMReviewRubric(
        zoom_out_score=5.0,
        naive_reader_score=5.0,
        stress_test_score=5.0,
        blockers=["Security vulnerability: unauthenticated mutating endpoint"],
        findings=["Critical security flaw"]
    )
    assert rubric.overall_score == 5.0
    assert rubric.is_approved is False


def test_egm_review_rubric_rejection_on_low_score():
    """Verify EGM rejects output when overall score is below 4.0."""
    rubric = EGMReviewRubric(
        zoom_out_score=2.0,
        naive_reader_score=3.0,
        stress_test_score=3.0,
        blockers=[],
        findings=["Unnecessary abstraction layers (YAGNI violation)"]
    )
    assert rubric.overall_score < 4.0
    assert rubric.is_approved is False


def test_blind_tournament_judge_anonymization():
    """Verify candidate solutions are anonymized with SHA-1 tokens."""
    c1 = CandidateSolution(
        candidate_id="cand-human-01",
        author_role="human_mentor",
        surface=SurfaceCategory.SCRIPTS,
        target_file="scripts/system/check.py",
        patch_diff="- old\n+ new",
        rationale="Fix exit code"
    )
    c2 = CandidateSolution(
        candidate_id="cand-agent-02",
        author_role="subagent_builder",
        surface=SurfaceCategory.SCRIPTS,
        target_file="scripts/system/check.py",
        patch_diff="- old\n+ new_v2\n+ extra_line",
        rationale="Alternative fix"
    )

    anonymized, token_map = BlindTournamentJudge.anonymize_candidates([c1, c2])

    assert len(anonymized) == 2
    # Verify author identity is stripped from anonymized dict
    for item in anonymized:
        assert "human_mentor" not in str(item)
        assert "subagent_builder" not in str(item)
        assert "cand-human-01" not in str(item)
        assert "token" in item
        assert "Candidate-" in item["token"]

    # Verify token map allows deanonymizing the winner
    tokens = list(token_map.keys())
    assert token_map[tokens[0]] == "cand-human-01"
    assert token_map[tokens[1]] == "cand-agent-02"

    # Verify static ranking prioritizes smaller diffs (DEC-057)
    ranked = BlindTournamentJudge.rank_candidates_statically(anonymized)
    assert ranked[0]["diff_line_count"] <= ranked[1]["diff_line_count"]


def test_propose_probe_compose_lifecycle():
    """Verify Propose-Probe-Compose engine probes an oracle command."""
    engine = ProposeProbeComposeEngine()

    # Test surface validation
    cat = engine.validate_surface("scripts/system/verify_all.sh")
    assert cat == SurfaceCategory.SCRIPTS

    cand = CandidateSolution(
        candidate_id="cand-003",
        author_role="denchik",
        surface=SurfaceCategory.SCRIPTS,
        target_file="scripts/system/verify.py",
        patch_diff="+ print('ok')",
        rationale="Add verification probe"
    )

    # Probe passing command
    probe_pass = engine.probe_patch(cand, oracle_command="python3 -c 'exit(0)'")
    assert probe_pass.passed is True
    assert probe_pass.exit_code == 0

    # Probe failing command
    probe_fail = engine.probe_patch(cand, oracle_command="python3 -c 'exit(42)'")
    assert probe_fail.passed is False
    assert probe_fail.exit_code == 42

    # Reflection generation on failure
    reflection = engine.generate_experience_reflection(cand, probe_fail)
    assert reflection["exit_code"] == 42
    assert "Guard invariant" in reflection["reflection_rule"]
