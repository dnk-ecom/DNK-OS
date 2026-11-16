#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/anti_tautology_guard.py"
# purpose: "Adversarial Quality Gate: Detects and rejects tautological assertions, empty tests, and fake compliance in test suites."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym & Antigravity Mentor"
# --- END DNK-MRH-HEADER ---

"""
Anti-Tautology & Fake Test Guard (Zero-Deception Quality Gate).

Detects and rejects deceptive agent testing patterns:
1. Tautological assertions: assert True, assert 1 == 1, assert x == x.
2. Empty test functions: def test_... containing only pass, ..., or docstrings.
3. Assert-free test functions: def test_... with zero assertions or pytest.raises.
4. Unauthorized test skips: @pytest.mark.skip without an authorized ticket reference.
5. Frontend tautologies: expect(true).toBe(true), empty it/test blocks.
"""

import ast
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@dataclass
class TautologyViolation:
    file_path: str
    line_number: int
    test_name: str
    violation_type: str
    description: str
    evidence: str


class PythonTestASTAuditor(ast.NodeVisitor):
    def __init__(self, file_path: str, lines: List[str]):
        self.file_path = file_path
        self.lines = lines
        self.violations: List[TautologyViolation] = []
        self.current_test: Optional[str] = None
        self.current_test_assert_count = 0
        self.current_test_node: Optional[ast.FunctionDef] = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_function(node)

    def _check_function(self, node):
        if not node.name.startswith("test_"):
            self.generic_visit(node)
            return

        # Skip fixtures decorated with @pytest.fixture
        is_fixture = any(
            (isinstance(d, ast.Attribute) and d.attr == "fixture") or
            (isinstance(d, ast.Name) and d.id == "fixture") or
            (isinstance(d, ast.Call) and (
                (isinstance(d.func, ast.Attribute) and d.func.attr == "fixture") or
                (isinstance(d.func, ast.Name) and d.func.id == "fixture")
            ))
            for d in node.decorator_list
        )
        if is_fixture:
            self.generic_visit(node)
            return

        prev_test = self.current_test
        prev_assert_count = self.current_test_assert_count
        prev_node = self.current_test_node

        self.current_test = node.name
        self.current_test_assert_count = 0
        self.current_test_node = node

        # 1. Check for unauthorized skips in decorators
        for decorator in node.decorator_list:
            dec_id = ""
            if isinstance(decorator, ast.Attribute):
                dec_id = f"{getattr(decorator.value, 'id', '')}.{decorator.attr}"
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    dec_id = f"{getattr(decorator.func.value, 'id', '')}.{decorator.func.attr}"

            if "skip" in dec_id or "xfail" in dec_id:
                # Require reason with issue or ticket
                has_valid_reason = False
                if isinstance(decorator, ast.Call):
                    for kw in decorator.keywords:
                        if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                            val = str(kw.value.value)
                            if any(k in val for k in ("DNK-", "TASK-", "ISSUE-", "ADR-", "TODO-")):
                                has_valid_reason = True
                if not has_valid_reason:
                    self.violations.append(TautologyViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        test_name=node.name,
                        violation_type="UNAUTHORIZED_TEST_SKIP",
                        description=f"Test '{node.name}' is skipped without an authorized ticket reference in reason='...'.",
                        evidence=self._get_line(node.lineno)
                    ))

        # 2. Check for empty function body (pass, docstring only, or ellipsis)
        body_non_doc = []
        for stmt in node.body:
            # Skip docstrings
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                continue
            body_non_doc.append(stmt)

        if not body_non_doc:
            self.violations.append(TautologyViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                test_name=node.name,
                violation_type="EMPTY_TEST_BODY",
                description=f"Test '{node.name}' has an empty body (docstring only).",
                evidence=self._get_line(node.lineno)
            ))
        elif len(body_non_doc) == 1 and isinstance(body_non_doc[0], ast.Pass):
            self.violations.append(TautologyViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                test_name=node.name,
                violation_type="EMPTY_TEST_PASS",
                description=f"Test '{node.name}' has no implementation (contains only 'pass').",
                evidence=self._get_line(node.lineno)
            ))

        self.generic_visit(node)

        # 3. Check assert count: At least one assert, pytest.raises, or mock check required
        if self.current_test_assert_count == 0 and body_non_doc:
            # Check if function contains pytest.raises, pytest.warns, pytest.fail, or mock/unittest assertions
            has_exception_guard = False
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.With):
                    for item in stmt.items:
                        if isinstance(item.context_expr, ast.Call):
                            func_str = ast.dump(item.context_expr.func)
                            if "raises" in func_str or "warns" in func_str:
                                has_exception_guard = True
                elif isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Attribute):
                        attr_name = stmt.func.attr
                        # Support assert_*, assertEqual, assertTrue, assertIn, assertCalled, fail, etc.
                        if (
                            attr_name.startswith("assert")
                            or "mock" in attr_name
                            or attr_name in ("fail", "expect", "verify", "step")
                        ):
                            has_exception_guard = True
                    elif isinstance(stmt.func, ast.Name):
                        if stmt.func.id in ("fail", "expect", "verify"):
                            has_exception_guard = True

            if not has_exception_guard:
                self.violations.append(TautologyViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    test_name=node.name,
                    violation_type="NO_ASSERTIONS",
                    description=f"Test '{node.name}' contains zero assertions, pytest.raises, or mock verifications.",
                    evidence=self._get_line(node.lineno)
                ))

        self.current_test = prev_test
        self.current_test_assert_count = prev_assert_count
        self.current_test_node = prev_node

    def visit_Assert(self, node: ast.Assert):
        if self.current_test:
            self.current_test_assert_count += 1
            test_val = node.test

            # Check 1: assert True / assert not False
            if isinstance(test_val, ast.Constant) and test_val.value is True:
                self.violations.append(TautologyViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    test_name=self.current_test,
                    violation_type="TAUTOLOGICAL_ASSERT_TRUE",
                    description="Detected tautological assertion 'assert True'. Test must assert against real code outputs.",
                    evidence=self._get_line(node.lineno)
                ))
            elif isinstance(test_val, ast.UnaryOp) and isinstance(test_val.op, ast.Not):
                if isinstance(test_val.operand, ast.Constant) and test_val.operand.value is False:
                    self.violations.append(TautologyViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        test_name=self.current_test,
                        violation_type="TAUTOLOGICAL_ASSERT_NOT_FALSE",
                        description="Detected tautological assertion 'assert not False'.",
                        evidence=self._get_line(node.lineno)
                    ))

            # Check 2: assert 1 == 1, assert "x" == "x"
            elif isinstance(test_val, ast.Compare) and len(test_val.ops) == 1 and isinstance(test_val.ops[0], ast.Eq):
                left = test_val.left
                right = test_val.comparators[0]
                if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                    if left.value == right.value:
                        self.violations.append(TautologyViolation(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            test_name=self.current_test,
                            violation_type="TAUTOLOGICAL_CONSTANT_COMPARISON",
                            description=f"Detected tautological assertion: literal constant comparison '{left.value} == {right.value}'.",
                            evidence=self._get_line(node.lineno)
                        ))
                # Check 3: assert expr == expr (identical AST nodes, e.g. a.b == a.b)
                elif ast.dump(left) == ast.dump(right):
                    self.violations.append(TautologyViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        test_name=self.current_test,
                        violation_type="TAUTOLOGICAL_SELF_COMPARISON",
                        description="Detected tautological assertion: expression compared to itself (left == right).",
                        evidence=self._get_line(node.lineno)
                    ))

        self.generic_visit(node)

    def _get_line(self, lineno: int) -> str:
        if 0 < lineno <= len(self.lines):
            return self.lines[lineno - 1].strip()
        return ""


class TypeScriptTestAuditor:
    """Regex-based scanner for frontend test files (*.test.ts, *.spec.ts, *.test.tsx)."""

    TAUTOLOGY_PATTERNS = [
        (re.compile(r"expect\s*\(\s*true\s*\)\s*\.toBe\s*\(\s*true\s*\)"), "TAUTOLOGICAL_EXPECT_TRUE", "expect(true).toBe(true)"),
        (re.compile(r"expect\s*\(\s*false\s*\)\s*\.toBe\s*\(\s*false\s*\)"), "TAUTOLOGICAL_EXPECT_FALSE", "expect(false).toBe(false)"),
        (re.compile(r"expect\s*\(\s*(\d+)\s*\)\s*\.toBe\s*\(\s*\1\s*\)"), "TAUTOLOGICAL_EXPECT_NUMBER", "expect(N).toBe(N)"),
        (re.compile(r"(?:it|test)\.skip\s*\("), "UNAUTHORIZED_TS_TEST_SKIP", "it.skip / test.skip without ticket"),
        (re.compile(r"(?:it|test)\s*\(\s*['\"][^'\"]+['\"]\s*,\s*(?:async\s*)?\(\s*\)\s*=>\s*\{\s*\}\s*\)"), "EMPTY_TS_TEST_BLOCK", "Empty test block it('...', () => {})"),
    ]

    def __init__(self, file_path: str, lines: List[str]):
        self.file_path = file_path
        self.lines = lines
        self.violations: List[TautologyViolation] = []

    def audit(self) -> List[TautologyViolation]:
        content = "\n".join(self.lines)

        for pat, v_type, desc in self.TAUTOLOGY_PATTERNS:
            for i, line in enumerate(self.lines, 1):
                if pat.search(line):
                    # For skips, allow if line or previous line mentions DNK- / TASK-
                    if v_type == "UNAUTHORIZED_TS_TEST_SKIP":
                        prev_line = self.lines[i - 2] if i >= 2 else ""
                        if any(k in line or k in prev_line for k in ("DNK-", "TASK-", "ISSUE-", "ADR-")):
                            continue

                    self.violations.append(TautologyViolation(
                        file_path=self.file_path,
                        line_number=i,
                        test_name="TypeScript/Vitest",
                        violation_type=v_type,
                        description=desc,
                        evidence=line.strip()
                    ))

        return self.violations


class AntiTautologyGuard:
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or _ROOT

    def get_affected_test_files(self) -> List[Path]:
        """Gathers git-modified, staged, and untracked test files."""
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain", "-u"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                check=True
            )
        except Exception:
            return []

        affected = []
        for line in res.stdout.splitlines():
            if len(line) >= 4:
                raw_path = line[3:].strip()
                if " -> " in raw_path:
                    raw_path = raw_path.split(" -> ")[1].strip()
                p = self.repo_root / raw_path
                if self._is_test_file(p) and p.exists():
                    affected.append(p)
        return affected

    def get_all_test_files(self) -> List[Path]:
        """Finds all test files in the workspace."""
        test_files = []
        for p in self.repo_root.glob("tests/**/*.py"):
            if p.is_file() and not any(part in p.parts for part in (".venv", "node_modules", ".git")):
                test_files.append(p)
        for p in self.repo_root.glob("apps/**/__tests__/**/*.ts*"):
            if p.is_file() and not any(part in p.parts for part in (".venv", "node_modules", ".git")):
                test_files.append(p)
        for p in self.repo_root.glob("apps/**/*.test.ts*"):
            if p.is_file() and not any(part in p.parts for part in (".venv", "node_modules", ".git")):
                test_files.append(p)
        return test_files

    def _is_test_file(self, path: Path) -> bool:
        name = path.name.lower()
        parts = [p.lower() for p in path.parts]
        if any(part in parts for part in (".venv", "node_modules", ".git", "artifacts", "cache")):
            return False
        if "tests" in parts and path.suffix == ".py":
            return True
        if (name.endswith(".test.ts") or name.endswith(".test.tsx") or
            name.endswith(".spec.ts") or name.endswith(".spec.tsx")):
            return True
        return False

    def audit_file(self, path: Path) -> List[TautologyViolation]:
        rel_path = str(path.relative_to(self.repo_root))
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()
        except Exception as err:
            return [TautologyViolation(
                file_path=rel_path,
                line_number=1,
                test_name="<read_error>",
                violation_type="FILE_READ_ERROR",
                description=f"Cannot read file: {err}",
                evidence=""
            )]

        if path.suffix == ".py":
            try:
                tree = ast.parse(content, filename=str(path))
                auditor = PythonTestASTAuditor(rel_path, lines)
                auditor.visit(tree)
                return auditor.violations
            except SyntaxError as se:
                return [TautologyViolation(
                    file_path=rel_path,
                    line_number=se.lineno or 1,
                    test_name="<syntax_error>",
                    violation_type="SYNTAX_ERROR",
                    description=f"SyntaxError in test file: {se.msg}",
                    evidence=se.text or ""
                )]
        elif path.suffix in (".ts", ".tsx", ".js", ".jsx"):
            ts_auditor = TypeScriptTestAuditor(rel_path, lines)
            return ts_auditor.audit()

        return []

    def run(self, files: Optional[List[Path]] = None) -> Tuple[bool, List[TautologyViolation]]:
        target_files = files if files is not None else self.get_affected_test_files()
        all_violations: List[TautologyViolation] = []

        for f in target_files:
            if f.is_file():
                violations = self.audit_file(f)
                all_violations.extend(violations)

        passed = len(all_violations) == 0
        return passed, all_violations


def main():
    parser = argparse.ArgumentParser(description="Anti-Tautology & Fake Test Guard for DNK OS")
    parser.add_argument("--all", action="store_true", help="Audit all test files in the workspace")
    parser.add_argument("--affected", action="store_true", help="Audit only affected/modified test files (default)")
    parser.add_argument("files", nargs="*", help="Explicit test files to audit")
    args = parser.parse_args()

    guard = AntiTautologyGuard(_ROOT)

    if args.files:
        files = [Path(f).resolve() for f in args.files]
    elif args.all:
        files = guard.get_all_test_files()
    else:
        files = guard.get_affected_test_files()

    print(f"🛡️ [Anti-Tautology Guard] Inspecting {len(files)} test file(s)...")
    passed, violations = guard.run(files)

    if not passed:
        print("\n❌ ANTI-TAUTOLOGY GATE BREACH: Fake or tautological tests detected!\n")
        for v in violations:
            print(f"  🚨 [{v.violation_type}] {v.file_path}:{v.line_number} (in {v.test_name})")
            print(f"     Description: {v.description}")
            if v.evidence:
                print(f"     Evidence:    {v.evidence}")
            print()
        print("💡 REMEDY: Tests must execute actual application code and assert against real outputs.")
        sys.exit(1)

    print(f"✅ Anti-Tautology Guard Passed: 0 tautologies or empty tests in {len(files)} file(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
