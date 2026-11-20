# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_context_diet_guard.py"
# purpose: "Unit tests for Context Diet & Anti-Bloat Pre-Commit Guard (DEC-146 / AGENTS.md Rule 9)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Denchik (Builder)"
# --- END DNK-MRH-HEADER ---

from pathlib import Path
import pytest
from scripts.system.auto_precommit_guard import (
    AutoPreCommitGuard,
    TOTAL_CHECKS,
    MAX_CORE_SKILL_LINES,
    MAX_AGENT_PROMPT_LINES,
)


def test_auto_precommit_guard_constants_and_total_checks():
    assert TOTAL_CHECKS == 8
    assert MAX_CORE_SKILL_LINES == 750
    assert MAX_AGENT_PROMPT_LINES == 400

    guard = AutoPreCommitGuard()
    assert guard.TOTAL_CHECKS == 8
    assert guard.MAX_CORE_SKILL_LINES == 750
    assert guard.MAX_AGENT_PROMPT_LINES == 400
    assert callable(guard.run_all_checks)


def test_skill_hygiene_passes_on_current_repo():
    guard = AutoPreCommitGuard()
    name, passed, err = guard._check_skill_and_context_hygiene()

    assert name == "skill_context_hygiene"
    assert passed is True
    assert err is None


def test_skill_hygiene_synthetic_boundary_pass(tmp_path: Path):
    skill_dir = tmp_path / "packages" / "boundary_skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("\n".join(f"line {i}" for i in range(750)), encoding="utf-8")

    agents_dir = tmp_path / "core" / "orchestrator" / "agents" / "boundary_agent"
    agents_dir.mkdir(parents=True)
    (agents_dir / "SOUL.md").write_text("\n".join(f"prompt {i}" for i in range(400)), encoding="utf-8")

    guard = AutoPreCommitGuard(root_dir=tmp_path)
    name, passed, err = guard._check_skill_and_context_hygiene()

    assert name == "skill_context_hygiene"
    assert passed is True
    assert err is None


def test_skill_hygiene_synthetic_fail_oversized_skill(tmp_path: Path):
    skill_dir = tmp_path / "core" / "skills" / "bloated_skill"
    skill_dir.mkdir(parents=True)
    # 751 lines exceeds MAX_CORE_SKILL_LINES (750)
    (skill_dir / "SKILL.md").write_text("\n".join(f"line {i}" for i in range(751)), encoding="utf-8")

    guard = AutoPreCommitGuard(root_dir=tmp_path)
    name, passed, err = guard._check_skill_and_context_hygiene()

    assert name == "skill_context_hygiene"
    assert passed is False
    assert err is not None
    assert "exceeds 750 lines" in err
    assert "751 lines" in err


def test_skill_hygiene_synthetic_fail_oversized_agent_prompt(tmp_path: Path):
    agent_dir = tmp_path / "core" / "orchestrator" / "agents" / "bloated_agent"
    agent_dir.mkdir(parents=True)
    # 401 lines exceeds MAX_AGENT_PROMPT_LINES (400)
    (agent_dir / "SOUL.md").write_text("\n".join(f"prompt line {i}" for i in range(401)), encoding="utf-8")

    guard = AutoPreCommitGuard(root_dir=tmp_path)
    name, passed, err = guard._check_skill_and_context_hygiene()

    assert name == "skill_context_hygiene"
    assert passed is False
    assert err is not None
    assert "exceeds 400 lines" in err
    assert "401 lines" in err


def test_skill_hygiene_ignores_hidden_and_vendor_dirs(tmp_path: Path):
    hidden_dir = tmp_path / ".hidden_store" / "skills"
    hidden_dir.mkdir(parents=True)
    (hidden_dir / "SKILL.md").write_text("\n".join(f"hidden line {i}" for i in range(1200)), encoding="utf-8")

    node_dir = tmp_path / "node_modules" / "some_dep"
    node_dir.mkdir(parents=True)
    (node_dir / "SKILL.md").write_text("\n".join(f"dep line {i}" for i in range(1200)), encoding="utf-8")

    guard = AutoPreCommitGuard(root_dir=tmp_path)
    name, passed, err = guard._check_skill_and_context_hygiene()

    assert name == "skill_context_hygiene"
    assert passed is True
    assert err is None
