# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/git_worktree_manager.py"
# purpose: "Ephemeral isolated git worktree manager for concurrent swarm agents"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def _clean_git_env() -> Dict[str, str]:
    env = os.environ.copy()
    for k in ["GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX"]:
        env.pop(k, None)
    return env


class GitWorktreeManager:
    """Manages ephemeral, isolated Git worktrees for concurrent swarm agents."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir).resolve() if base_dir else None

    def create_agent_worktree(
        self,
        repo_path: Path,
        agent_id: str,
        branch_name: Optional[str] = None,
        target_dir: Optional[Path] = None,
    ) -> Path:
        """Creates an isolated git worktree for an agent."""
        repo = Path(repo_path).resolve()
        branch = branch_name or f"agent/{agent_id}-{int(time.time() * 1000)}"
        if target_dir:
            wt = Path(target_dir).resolve()
        elif self.base_dir:
            wt = (self.base_dir / f"wt_{agent_id}_{int(time.time() * 1000)}").resolve()
        else:
            wt = (repo.parent / f"{repo.name}_wt_{agent_id}_{int(time.time() * 1000)}").resolve()
        wt.parent.mkdir(parents=True, exist_ok=True)

        chk = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=repo, capture_output=True, env=_clean_git_env(),
        )
        cmd = ["git", "worktree", "add"] + ([str(wt), branch] if chk.returncode == 0 else ["-b", branch, str(wt)])
        res = subprocess.run(cmd, cwd=repo, capture_output=True, env=_clean_git_env(), text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to create worktree: {res.stderr.strip()}")
        return wt

    def teardown_worktree(
        self,
        worktree_path: Path,
        delete_branch: bool = False,
        repo_path: Optional[Path] = None,
    ) -> bool:
        """Removes a worktree and optionally deletes its branch."""
        wt = Path(worktree_path).resolve()
        if not wt.exists():
            return True
        branch, repo_dir = None, Path(repo_path).resolve() if repo_path else None
        try:
            res_b = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wt, capture_output=True, text=True)
            if res_b.returncode == 0:
                branch = res_b.stdout.strip()
            if not repo_dir:
                res_c = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=wt, capture_output=True, text=True)
                if res_c.returncode == 0:
                    common = Path(res_c.stdout.strip()).resolve()
                    repo_dir = common.parent if common.name == ".git" else common
        except Exception as err:
            logger.debug("Failed resolving worktree git metadata: %s", err)

        cwd = repo_dir if (repo_dir and repo_dir.exists()) else (wt.parent if wt.parent.exists() else None)
        if cwd:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=cwd, capture_output=True)
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)
        if delete_branch and branch and repo_dir and branch not in ("HEAD", "main", "master"):
            subprocess.run(["git", "branch", "-D", branch], cwd=repo_dir, capture_output=True)
        if repo_dir:
            subprocess.run(["git", "worktree", "prune"], cwd=repo_dir, capture_output=True)
        return not wt.exists()

    def list_active_worktrees(self, repo_path: Path) -> List[Dict[str, str]]:
        """Parses git worktree list --porcelain into structured dictionaries."""
        res = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=Path(repo_path).resolve(), capture_output=True, text=True
        )
        if res.returncode != 0:
            return []
        worktrees: List[Dict[str, str]] = []
        current: Dict[str, str] = {}
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue
            parts = line.split(" ", 1)
            current[parts[0]] = parts[1] if len(parts) > 1 else "true"
        if current:
            worktrees.append(current)
        return worktrees

    def prune_stale_worktrees(self, repo_path: Path) -> int:
        """Prunes stale worktrees and returns count of removed entries."""
        res = subprocess.run(
            ["git", "worktree", "prune", "-v"],
            cwd=Path(repo_path).resolve(), capture_output=True, text=True
        )
        if res.returncode != 0:
            return 0
        return len([l for l in (res.stdout + "\n" + res.stderr).splitlines() if "Removing " in l])

    def rollback_worktree(self, worktree_path: Path) -> bool:
        """
        Rolls back all uncommitted or failed changes in a worktree,
        returning it to a clean state matching HEAD (git reset --hard && git clean -fd).
        Used when an agent's edit slice fails automated verification (Cognition/Devin pattern).
        """
        wt = Path(worktree_path).resolve()
        if not wt.exists():
            return False
        res_reset = subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=wt, capture_output=True, text=True)
        res_clean = subprocess.run(["git", "clean", "-fd"], cwd=wt, capture_output=True, text=True)
        return res_reset.returncode == 0 and res_clean.returncode == 0

