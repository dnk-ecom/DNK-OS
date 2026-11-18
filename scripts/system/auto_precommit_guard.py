#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/auto_precommit_guard.py"
# purpose: "Autonomous Pre-Commit Guard and Quality Gate for DNK_OS with instant error capture and regression verification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.1.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Denchik (Builder)"
# --- END DNK-MRH-HEADER ---

import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import os

def _get_clean_env() -> dict:
    env = os.environ.copy()
    for k in ["GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX"]:
        env.pop(k, None)
    return env
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

TOTAL_CHECKS: int = 8
MAX_CORE_SKILL_LINES: int = 750
MAX_AGENT_PROMPT_LINES: int = 400


@dataclass
class GuardCheckResult:
    passed: bool
    total_checks: int
    passed_checks: int
    elapsed_seconds: float
    check_results: Dict[str, bool]
    errors: List[str] = field(default_factory=list)


class AutoPreCommitGuard:
    """
    Autonomous Pre-Commit Quality Guard for Sovereign DNK_OS.
    Executes:
      1. Fast AST syntax compilation check across all Python files
      2. Relative path & portability hygiene (0 absolute /Users/ leaks)
      3. Anti-Tautology & Fake Test Guard (Zero deceptive assertions)
      4. Universal Guard & Structural Barrier verification
      5. Core Regression Test Suites (tests/core/)
      6. Frontend TypeScript integrity (if package.json present)
      7. Git Worktree hygiene & stale metadata pruning (DEC-137 / TASK-02)
      8. Skill & Context Diet Hygiene (MAX_CORE_LINES <= 750, DEC-146)
    """

    TOTAL_CHECKS = TOTAL_CHECKS
    MAX_CORE_SKILL_LINES = MAX_CORE_SKILL_LINES
    MAX_AGENT_PROMPT_LINES = MAX_AGENT_PROMPT_LINES

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.mvp_root = self.root_dir
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))

    def _check_fast_syntax(self) -> Tuple[str, bool, Optional[str]]:
        try:
            fast_syntax = self.root_dir / "scripts" / "system" / "fast_compile_check.py"
            if fast_syntax.exists():
                res = subprocess.run([sys.executable, str(fast_syntax)], capture_output=True, text=True)
                if res.returncode == 0:
                    return "fast_syntax_check", True, None
                return "fast_syntax_check", False, f"Fast Syntax Check failed: {res.stdout or res.stderr}"
            return "fast_syntax_check", True, None
        except Exception as exc:
            return "fast_syntax_check", False, f"Fast Syntax Check error: {exc}"

    def _check_path_hygiene(self) -> Tuple[str, bool, Optional[str]]:
        try:
            from core.sentinel.hygiene_guard import DNKHygieneGuard
            guard = DNKHygieneGuard(root_dir=self.mvp_root)
            res = guard.audit_manifests_for_absolute_paths()
            if res.get("status") == "PASS":
                return "path_hygiene", True, None
            leaks = res.get("leaks", {})
            return "path_hygiene", False, f"Path hygiene check failed: Absolute paths detected in manifests: {leaks}"
        except Exception as exc:
            return "path_hygiene", False, f"Path hygiene check error: {exc}"

    def _check_anti_tautology(self) -> Tuple[str, bool, Optional[str]]:
        try:
            venv_python = self.root_dir / ".venv" / "bin" / "python3"
            py_exec = str(venv_python) if venv_python.exists() else sys.executable
            script = self.root_dir / "scripts" / "system" / "anti_tautology_guard.py"
            if not script.exists():
                return "anti_tautology", True, None
            res = subprocess.run([py_exec, str(script), "--all"], cwd=str(self.root_dir), capture_output=True, text=True)
            if res.returncode == 0:
                return "anti_tautology", True, None
            return "anti_tautology", False, f"Anti-tautology guard failed:\n{res.stdout or res.stderr}"
        except Exception as exc:
            return "anti_tautology", False, f"Anti-tautology check error: {exc}"

    def _check_universal_guard(self) -> Tuple[str, bool, Optional[str]]:
        try:
            venv_python = self.root_dir / ".venv" / "bin" / "python3"
            py_exec = str(venv_python) if venv_python.exists() else sys.executable
            cmd = [py_exec, "-m", "pytest", "tests/core/test_universal_guard.py", "-q"]
            res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True, env=_get_clean_env())
            if res.returncode == 0:
                return "universal_guard", True, None
            return "universal_guard", False, f"Universal Guard test failed:\n{res.stdout or res.stderr}"
        except Exception as exc:
            return "universal_guard", False, f"Universal Guard test error: {exc}"

    def _check_regression_tests(self) -> Tuple[str, bool, Optional[str]]:
        try:
            venv_python = self.root_dir / ".venv" / "bin" / "python3"
            py_exec = str(venv_python) if venv_python.exists() else sys.executable
            cmd = [
                py_exec,
                "-m",
                "pytest",
                "tests/core/",
                "-q",
            ]
            res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True, env=_get_clean_env())
            if res.returncode == 0:
                return "regression_tests", True, None
            return "regression_tests", False, f"Regression tests failed:\n{res.stdout or res.stderr}"
        except Exception as exc:
            return "regression_tests", False, f"Pytest execution error: {exc}"

    def _check_frontend_typecheck(self) -> Tuple[str, bool, Optional[str]]:
        try:
            web_pkg = self.root_dir / "apps" / "web" / "package.json"
            if web_pkg.exists():
                cmd = ["pnpm", "--dir", str(self.root_dir / "apps" / "web"), "type-check"]
                if not shutil.which("pnpm"):
                    cmd = ["npm", "--prefix", str(self.root_dir / "apps" / "web"), "run", "type-check"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    return "frontend_typecheck", True, None
                return "frontend_typecheck", False, f"Frontend type-check failed:\n{res.stdout or res.stderr}"
            return "frontend_typecheck", True, None
        except Exception as exc:
            return "frontend_typecheck", False, f"Frontend typecheck error: {exc}"

    def _check_worktree_hygiene(self) -> Tuple[str, bool, Optional[str]]:
        """
        Verifies Git Worktree hygiene (DEC-137 / TASK-02):
        1. Prunes stale worktree references from git metadata.
        2. Inspects active worktrees; verifies no orphaned agent worktrees exist
           outside the main checkout.
        """
        try:
            from core.orchestrator.git_worktree_manager import GitWorktreeManager
            manager = GitWorktreeManager()
            manager.prune_stale_worktrees(self.root_dir)
            active_trees = manager.list_active_worktrees(self.root_dir)

            for tree in active_trees:
                wt_str = tree.get("worktree", "")
                if wt_str:
                    wt_path = Path(wt_str)
                    if not wt_path.exists():
                        return "worktree_hygiene", False, f"Orphaned worktree detected without physical directory: {wt_str}"

            return "worktree_hygiene", True, None
        except Exception as exc:
            return "worktree_hygiene", False, f"Worktree hygiene check error: {exc}"

    def _check_skill_and_context_hygiene(self) -> Tuple[str, bool, Optional[str]]:
        """
        Validates context diet and anti-bloat invariants (DEC-146 / AGENTS.md Rule 9):
        1. All active SKILL.md files must have <= MAX_CORE_SKILL_LINES (750 lines).
        2. Agent base prompts (SOUL.md) in core/orchestrator/agents/ must have <= MAX_AGENT_PROMPT_LINES (400 lines).
        """
        try:
            violations: List[str] = []
            # 1. Audit active SKILL.md files
            for path in self.root_dir.rglob("SKILL.md"):
                rel_parts = path.relative_to(self.root_dir).parts
                if any(p.startswith(".") or p in ("node_modules", "dist", "build", "site-packages") for p in rel_parts):
                    continue
                try:
                    line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
                    if line_count > self.MAX_CORE_SKILL_LINES:
                        rel = path.relative_to(self.root_dir)
                        violations.append(
                            f"Skill {rel} exceeds {self.MAX_CORE_SKILL_LINES} lines ({line_count} lines)"
                        )
                except Exception as exc:
                    violations.append(f"Failed reading skill {path}: {exc}")

            # 2. Audit agent SOUL.md base prompts
            agents_dir = self.root_dir / "core" / "orchestrator" / "agents"
            if agents_dir.exists():
                for soul_path in agents_dir.glob("*/SOUL.md"):
                    try:
                        line_count = len(soul_path.read_text(encoding="utf-8", errors="ignore").splitlines())
                        if line_count > self.MAX_AGENT_PROMPT_LINES:
                            rel = soul_path.relative_to(self.root_dir)
                            violations.append(
                                f"Agent prompt {rel} exceeds {self.MAX_AGENT_PROMPT_LINES} lines ({line_count} lines)"
                            )
                    except Exception as exc:
                        violations.append(f"Failed reading prompt {soul_path}: {exc}")

            if violations:
                return "skill_context_hygiene", False, "Context Diet Violations:\n  • " + "\n  • ".join(violations)
            return "skill_context_hygiene", True, None
        except Exception as exc:
            return "skill_context_hygiene", False, f"Skill/context hygiene check error: {exc}"

    def run_all_checks(self) -> GuardCheckResult:
        """Alias to execute all deterministic checks."""
        return self.run_guard()

    def run_guard(self) -> GuardCheckResult:
        start_t = time.time()
        results: Dict[str, bool] = {}
        errors: List[str] = []

        parallel_checks: List[Callable[[], Tuple[str, bool, Optional[str]]]] = [
            self._check_fast_syntax,
            self._check_path_hygiene,
            self._check_anti_tautology,
            self._check_universal_guard,
            self._check_regression_tests,
            self._check_frontend_typecheck,
            self._check_worktree_hygiene,
            self._check_skill_and_context_hygiene,
        ]

        max_workers = min(8, len(parallel_checks))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_check = {executor.submit(fn): fn for fn in parallel_checks}
            for future in concurrent.futures.as_completed(future_to_check):
                name, passed, err = future.result()
                results[name] = passed
                if not passed and err:
                    errors.append(err)

        elapsed = round(time.time() - start_t, 3)
        passed_count = sum(1 for v in results.values() if v)
        all_passed = (passed_count == len(results))

        return GuardCheckResult(
            passed=all_passed,
            total_checks=len(results),
            passed_checks=passed_count,
            elapsed_seconds=elapsed,
            check_results=results,
            errors=errors,
        )


auto_guard = AutoPreCommitGuard()

if __name__ == "__main__":
    guard_res = auto_guard.run_guard()
    if guard_res.passed:
        print(f"🛡️  [PRE-COMMIT GUARD] ALL {guard_res.passed_checks}/{guard_res.total_checks} CHECKS PASSED in {guard_res.elapsed_seconds}s ✅")
        sys.exit(0)
    else:
        print(f"❌ [PRE-COMMIT GUARD] FAILED ({guard_res.passed_checks}/{guard_res.total_checks} passed in {guard_res.elapsed_seconds}s):")
        for err in guard_res.errors:
            print(f"  • {err}")
        sys.exit(1)
