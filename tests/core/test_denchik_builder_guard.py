# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_denchik_builder_guard.py"
# purpose: "Unit tests for Denchik Builder Mandate Guard and ToolGuardPipeline Integration (DEC-151)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "Antigravity & Denchik Builder & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import pytest
from pathlib import Path
from core.domain.mandate_contracts import Mandate, MandateScope, MandateViolationError, Strength
from core.orchestrator.agents.denchik.builder_guard import DenchikMandateGuard
from core.security.tool_guard_pipeline import ToolExecutionContext, ToolGuardPipeline


@pytest.fixture
def clean_guard():
    DenchikMandateGuard.unbind_mandate()
    yield
    DenchikMandateGuard.unbind_mandate()


@pytest.fixture
def sample_mandate(tmp_path):
    scope = MandateScope(
        allowed_paths=["services/dnk_media/**", "docs/**"],
        negative_scope=["**/.env*", "**/secrets.yaml", "core/kernel.py"],
        allowed_tools=["write_file", "patch", "read_file"]
    )
    return Mandate(
        policy_version="pol-2026-v1",
        scope=scope,
        strength=Strength.EXPLICIT,
        actor_id="maxim",
        source_id="cli"
    )


def test_builder_guard_allows_scoped_mutation(clean_guard, sample_mandate, tmp_path):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    target_file = tmp_path / "services" / "dnk_media" / "test_module.py"

    # Use relative path representation
    rel_path = "services/dnk_media/test_module.py"

    # Validate does not raise and active mandate remains bound
    DenchikMandateGuard.validate_mutation(rel_path, tool_name="write_file")
    assert DenchikMandateGuard.get_active_mandate() == sample_mandate


def test_builder_guard_blocks_unscoped_mutation(clean_guard, sample_mandate):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    forbidden_path = "services/dnk_shopify/unauthorized.liquid"

    with pytest.raises(MandateViolationError) as exc_info:
        DenchikMandateGuard.validate_mutation(forbidden_path, tool_name="write_file")

    assert "violates MandateScope" in str(exc_info.value)


def test_builder_guard_blocks_negative_scope(clean_guard, sample_mandate):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    negative_path = "services/dnk_media/.env.production"

    with pytest.raises(MandateViolationError):
        DenchikMandateGuard.validate_mutation(negative_path, tool_name="write_file")

    kernel_path = "core/kernel.py"
    with pytest.raises(MandateViolationError):
        DenchikMandateGuard.validate_mutation(kernel_path, tool_name="write_file")


def test_builder_guard_blocks_absolute_paths(clean_guard, sample_mandate):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    abs_path = "/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_OS/services/dnk_media/test.py"

    with pytest.raises(MandateViolationError) as exc_info:
        DenchikMandateGuard.validate_mutation(abs_path, tool_name="write_file")

    assert "Absolute path" in str(exc_info.value)


def test_builder_guard_safe_write_and_patch(clean_guard, sample_mandate, tmp_path, monkeypatch):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    monkeypatch.chdir(tmp_path)

    rel_path = "docs/release_notes.md"
    written = DenchikMandateGuard.safe_write_file(
        path=rel_path,
        content="# Release 1.0\nInitial release note."
    )
    assert written is True
    assert (tmp_path / rel_path).exists()

    patched = DenchikMandateGuard.safe_patch_file(
        path=rel_path,
        target_str="1.0",
        replacement="1.1"
    )
    assert patched is True
    assert "Release 1.1" in (tmp_path / rel_path).read_text(encoding="utf-8")


def test_tool_guard_pipeline_integration(clean_guard, sample_mandate):
    DenchikMandateGuard.bind_mandate(sample_mandate)
    pipeline = ToolGuardPipeline()

    # Allowed tool & path
    ctx_allowed = ToolExecutionContext(
        tool_name="write_file",
        arguments={"path": "services/dnk_media/src/transcribe.py", "content": "print('ok')"},
        caller_agent="denchik"
    )
    res_allowed = pipeline.guard(ctx_allowed)
    assert res_allowed.allowed is True

    # Disallowed path
    ctx_disallowed = ToolExecutionContext(
        tool_name="write_file",
        arguments={"path": "core/kernel.py", "content": "# rogue"},
        caller_agent="denchik"
    )
    res_disallowed = pipeline.guard(ctx_disallowed)
    assert res_disallowed.allowed is False
    assert "MandateViolation" in res_disallowed.reason

    # Disallowed tool
    ctx_bad_tool = ToolExecutionContext(
        tool_name="delete_database",
        arguments={"path": "services/dnk_media/src/transcribe.py"},
        caller_agent="denchik"
    )
    # If delete_database is in mutating or checked by mandate
    DenchikMandateGuard.validate_mutation("services/dnk_media/src/transcribe.py", tool_name="write_file")
    with pytest.raises(MandateViolationError):
        sample_mandate.assert_tool_allowed("delete_database")
