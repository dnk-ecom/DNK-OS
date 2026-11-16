#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/auto_precommit_guard.py"
# purpose: "Autonomous Pre-Commit Guard and Quality Gate for Gerych sessions with instant error capture and regression verification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-08-28"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


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
    Autonomous Pre-Commit Quality Guard.
    Executes:
      1. Preflight sanitizer (GCP token & stray cleanup)
      2. Fast AST syntax check across all 5,800+ Python files
      3. Relative path hygiene validation (0 absolute violations)
      3.1 Git workspace hygiene validation (no untracked tests/routers)
      4. Targeted regression test suites (pytest)
      5. Frontend TypeScript integrity (npm run type-check)
    """

    def __init__(self, hub_root: Optional[Path] = None):
        self.hub_root = hub_root or Path(__file__).resolve().parent.parent.parent
        self.mvp_root = self.hub_root

    def _check_fast_syntax(self) -> Tuple[str, bool, Optional[str]]:
        try:
            fast_syntax = self.hub_root / "scripts" / "system" / "fast_compile_check.py"
            if fast_syntax.exists():
                res = subprocess.run([sys.executable, str(fast_syntax)], capture_output=True, text=True, check=True)
                return "fast_syntax_check", True, None
            return "fast_syntax_check", True, None
        except subprocess.CalledProcessError as exc:
            return "fast_syntax_check", False, f"Fast Syntax Check failed: {exc.stderr or exc.stdout}"
        except Exception as exc:
            return "fast_syntax_check", False, f"Fast Syntax Check error: {exc}"

    def _check_path_hygiene(self) -> Tuple[str, bool, Optional[str]]:
        try:
            python_bin = self.mvp_root / ".venv" / "bin" / "python"
            py_exec = str(python_bin) if python_bin.exists() else sys.executable
            code = "from core.playbooks.scripts.enforce_relative_paths import audit_relative_paths\nviolations = audit_relative_paths()\nif violations > 0: exit(1)"
            res = subprocess.run(
                [py_exec, "-c", code],
                cwd=str(self.mvp_root),
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return "path_hygiene", True, None
            return "path_hygiene", False, f"Path hygiene check failed: Absolute path violations detected ({res.stderr})."
        except Exception as exc:
            return "path_hygiene", False, f"Path hygiene check error: {exc}"

    def _check_git_hygiene(self) -> Tuple[str, bool, Optional[str]]:
        try:
            git_hygiene = self.hub_root / "scripts" / "system" / "git_hygiene_guard.py"
            if git_hygiene.exists():
                res = subprocess.run([sys.executable, str(git_hygiene)], capture_output=True, text=True)
                if res.returncode == 0:
                    return "git_hygiene", True, None
                return "git_hygiene", False, f"Git hygiene check failed:\n{res.stdout or res.stderr}"
            return "git_hygiene", True, None
        except Exception as exc:
            return "git_hygiene", False, f"Git hygiene check error: {exc}"

    def _check_blob_size_guard(self) -> Tuple[str, bool, Optional[str]]:
        try:
            guard_script = self.hub_root / "scripts" / "system" / "git_blob_size_guard.py"
            if guard_script.exists():
                res = subprocess.run([sys.executable, str(guard_script)], capture_output=True, text=True)
                if res.returncode == 0:
                    return "blob_size_guard", True, None
                return "blob_size_guard", False, f"Git Blob Size & Binary Guard failed:\n{res.stdout or res.stderr}"
            return "blob_size_guard", True, None
        except Exception as exc:
            return "blob_size_guard", False, f"Blob size guard error: {exc}"

    def _check_architecture_guard(self) -> Tuple[str, bool, Optional[str]]:
        try:
            arch_guard = self.hub_root / "scripts" / "system" / "architecture_and_cycle_guard.py"
            if arch_guard.exists():
                venv_python = self.hub_root / ".venv" / "bin" / "python3"
                py_exec = str(venv_python) if venv_python.exists() else sys.executable
                res = subprocess.run([py_exec, str(arch_guard)], capture_output=True, text=True)
                if res.returncode == 0:
                    return "architecture_guard", True, None
                return "architecture_guard", False, f"Architecture & Cycle Guard failed:\n{res.stdout or res.stderr}"
            return "architecture_guard", True, None
        except Exception as exc:
            return "architecture_guard", False, f"Architecture guard check error: {exc}"

    def _check_blast_radius(self) -> Tuple[str, bool, Optional[str]]:
        try:
            blast_tool = self.hub_root / "scripts" / "system" / "blast_radius_analyzer.py"
            if blast_tool.exists():
                venv_python = self.hub_root / ".venv" / "bin" / "python3"
                py_exec = str(venv_python) if venv_python.exists() else sys.executable
                res = subprocess.run([py_exec, str(blast_tool), "--staged"], capture_output=True, text=True)
                if res.returncode == 0:
                    return "blast_radius", True, None
                return "blast_radius", False, f"Blast radius assessment failed:\n{res.stdout or res.stderr}"
            return "blast_radius", True, None
        except Exception as exc:
            return "blast_radius", False, f"Blast radius check error: {exc}"

    def _check_regression_tests(self) -> Tuple[str, bool, Optional[str]]:
        try:
            # Check for stray nested directories (e.g. apps/web/apps)
            stray_dirs = [
                self.hub_root / "apps" / "web" / "apps",
                self.hub_root / "services" / "services",
            ]
            for stray in stray_dirs:
                if stray.exists():
                    shutil.rmtree(stray, ignore_errors=True)

            venv_python = self.hub_root / ".venv" / "bin" / "python3"
            py_exec = str(venv_python) if venv_python.exists() else sys.executable
            cmd = [
                py_exec,
                "-m",
                "pytest",
                "tests/shopify/test_liquid_compiler.py",
                "tests/shopify/test_shopify_vite_pipeline.py",
                "tests/swarm/test_swarm_daemon.py",
                "tests/verification/test_remotion_renderer.py",
                "tests/verification/test_product_launch_flow.py",
                "tests/canvas/test_canvas_ai_actions.py",
                "tests/contracts/test_service_card_contract.py",
                "tests/core/test_scones_decisions_sync.py",
                "tests/core/test_iron_man_denchik.py",
                "tests/core/test_skills_bridge.py",
                "tests/core/test_blast_radius_radar.py",
                "-q",
            ]
            res = subprocess.run(
                cmd,
                cwd=str(self.hub_root),
                capture_output=True,
                text=True,
            )
            if res.returncode == 0:
                return "regression_tests", True, None
            return "regression_tests", False, f"Regression tests failed:\n{res.stdout or res.stderr}"
        except Exception as exc:
            return "regression_tests", False, f"Pytest execution error: {exc}"

    def _check_frontend_typecheck(self) -> Tuple[str, bool, Optional[str]]:
        try:
            web_pkg = self.hub_root / "apps" / "web" / "package.json"
            if web_pkg.exists():
                cmd = ["pnpm", "--dir", str(self.hub_root / "apps" / "web"), "type-check"]
                if not shutil.which("pnpm"):
                    cmd = ["npm", "--prefix", str(self.hub_root / "apps" / "web"), "run", "type-check"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    return "frontend_typecheck", True, None
                return "frontend_typecheck", False, f"Frontend type-check failed:\n{res.stdout or res.stderr}"
            return "frontend_typecheck", True, None
        except Exception as exc:
            return "frontend_typecheck", False, f"Frontend typecheck error: {exc}"

    def run_guard(self) -> GuardCheckResult:
        start_t = time.time()
        results: Dict[str, bool] = {}
        errors: List[str] = []

        # Barrier 1: Preflight Sanitizer (Serial, synchronous 0.2s)
        try:
            sanitizer = self.hub_root / "scripts" / "system" / "preflight_sanitizer.py"
            if sanitizer.exists():
                subprocess.run([sys.executable, str(sanitizer)], capture_output=True, text=True, check=True)
            results["preflight_sanitizer"] = True
        except subprocess.CalledProcessError as exc:
            results["preflight_sanitizer"] = False
            errors.append(f"Preflight Sanitizer failed: {exc.stderr}")
            return GuardCheckResult(
                passed=False,
                total_checks=1,
                passed_checks=0,
                elapsed_seconds=round(time.time() - start_t, 3),
                check_results=results,
                errors=errors,
            )

        # Barrier 2: Concurrent Execution of Independent Checks (ThreadPoolExecutor)
        parallel_checks: List[Callable[[], Tuple[str, bool, Optional[str]]]] = [
            self._check_fast_syntax,
            self._check_path_hygiene,
            self._check_git_hygiene,
            self._check_blob_size_guard,
            self._check_architecture_guard,
            self._check_blast_radius,
            self._check_regression_tests,
            self._check_frontend_typecheck,
        ]

        max_workers = min(6, len(parallel_checks))
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
