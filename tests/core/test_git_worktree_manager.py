# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_git_worktree_manager.py"
# purpose: "Comprehensive unit test suite for GitWorktreeManager verifying isolation, lifecycle, and pruning"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import shutil
import subprocess
from pathlib import Path

import pytest
from core.orchestrator.git_worktree_manager import GitWorktreeManager


def _init_test_git_repo(repo_path: Path) -> Path:
    repo_path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TestAgent"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@dnk-e.com"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo_path, check=True, capture_output=True)
    init_file = repo_path / "README.md"
    init_file.write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)
    return repo_path


def test_create_and_isolate_worktree(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "main_repo")
    manager = GitWorktreeManager()

    wt = manager.create_agent_worktree(repo, "agent_alpha")
    assert wt.exists()
    assert wt.is_dir()

    # Isolation check: write file to worktree
    agent_file = wt / "alpha_output.json"
    agent_file.write_text('{"status": "ok"}', encoding="utf-8")
    assert agent_file.exists()
    assert not (repo / "alpha_output.json").exists()

    # Verify list_active_worktrees
    active = manager.list_active_worktrees(repo)
    assert len(active) == 2
    wt_paths = [Path(w["worktree"]).resolve() for w in active if "worktree" in w]
    assert wt.resolve() in wt_paths
    assert repo.resolve() in wt_paths

    # Teardown
    success = manager.teardown_worktree(wt, delete_branch=True)
    assert success is True
    assert not wt.exists()

    active_after = manager.list_active_worktrees(repo)
    assert len(active_after) == 1


def test_worktree_custom_branch_and_commit_isolation(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "branch_repo")
    custom_dir = tmp_path / "custom_wts"
    manager = GitWorktreeManager(base_dir=custom_dir)

    wt = manager.create_agent_worktree(repo, "agent_beta", branch_name="feature-beta")
    assert custom_dir.exists()
    assert wt.exists()

    # Create file and commit in worktree
    new_file = wt / "beta.py"
    new_file.write_text("print('beta')", encoding="utf-8")
    subprocess.run(["git", "add", "beta.py"], cwd=wt, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Commit from beta"], cwd=wt, check=True, capture_output=True)

    # Verify commits in worktree vs main repo
    log_wt = subprocess.run(["git", "log", "-1", "--oneline"], cwd=wt, capture_output=True, text=True).stdout
    assert "Commit from beta" in log_wt

    log_main = subprocess.run(["git", "log", "-1", "--oneline"], cwd=repo, capture_output=True, text=True).stdout
    assert "Commit from beta" not in log_main
    assert "Initial commit" in log_main

    # Teardown without deleting branch
    success = manager.teardown_worktree(wt, delete_branch=False, repo_path=repo)
    assert success is True
    assert not wt.exists()

    # Branch still exists in main repo
    chk_branch = subprocess.run(["git", "rev-parse", "--verify", "refs/heads/feature-beta"], cwd=repo, capture_output=True)
    assert chk_branch.returncode == 0


def test_worktree_existing_branch(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "existing_branch_repo")
    subprocess.run(["git", "branch", "pre-existing-feature"], cwd=repo, check=True, capture_output=True)

    manager = GitWorktreeManager()
    wt = manager.create_agent_worktree(repo, "agent_gamma", branch_name="pre-existing-feature")
    assert wt.exists()

    active = manager.list_active_worktrees(repo)
    assert any("pre-existing-feature" in w.get("branch", "") for w in active)

    success = manager.teardown_worktree(wt, delete_branch=True, repo_path=repo)
    assert success is True
    assert not wt.exists()


def test_prune_stale_worktrees(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "prune_repo")
    manager = GitWorktreeManager()

    wt = manager.create_agent_worktree(repo, "agent_stale")
    assert wt.exists()

    # Ungraceful deletion of worktree folder
    shutil.rmtree(wt)
    assert not wt.exists()

    pruned = manager.prune_stale_worktrees(repo)
    assert pruned == 1

    second_prune = manager.prune_stale_worktrees(repo)
    assert second_prune == 0


def test_teardown_nonexistent_worktree(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "empty_repo")
    manager = GitWorktreeManager()
    res = manager.teardown_worktree(tmp_path / "nonexistent_dir", repo_path=repo)
    assert res is True


def test_rollback_worktree_discards_uncommitted_changes(tmp_path: Path):
    repo = _init_test_git_repo(tmp_path / "rollback_repo")
    manager = GitWorktreeManager()
    wt = manager.create_agent_worktree(repo, "agent_rollback")

    # Simulate dirty failed edits by an agent
    dirty_file = wt / "dirty_script.py"
    dirty_file.write_text("broken syntax !!!", encoding="utf-8")
    readme = wt / "README.md"
    readme.write_text("# Corrupted Content\n", encoding="utf-8")

    assert dirty_file.exists()
    assert readme.read_text(encoding="utf-8") == "# Corrupted Content\n"

    # Execute rollback
    rolled_back = manager.rollback_worktree(wt)
    assert rolled_back is True

    # Dirty untracked file is removed, modified file is restored to HEAD
    assert not dirty_file.exists()
    assert readme.read_text(encoding="utf-8") == "# Test Repo\n"

    # Cleanup
    manager.teardown_worktree(wt, delete_branch=True, repo_path=repo)

