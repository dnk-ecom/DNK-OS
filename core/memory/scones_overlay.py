# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_overlay.py"
# purpose: "SCONES Working-Tree Diff Overlay (Baseline ⊕ Fresh-Parse) for AST symbols and git-native agent memory."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
SCONES Working-Tree Diff Overlay Engine (DEC-045 / entire-brain pattern).

Solves the agent staleness dilemma:
When an agent mutates code in the working tree, the commit-level index becomes stale,
but full repository reindexing after every tool call is prohibitively slow.

Solution:
Effective Symbol Graph = Baseline(Index(HEAD)) ⊕ Fresh-Parse(Working-Tree Diff)
Asymmetric Edge Rule:
- Changed files are freshly parsed on the fly (instant definitions & outbound calls).
- Unchanged files preserve their immutable baseline graph and inbound links.
"""

from __future__ import annotations

import ast
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("dnk.core.memory.overlay")


@dataclass
class ASTSymbol:
    """Represents an AST symbol extracted from source code."""
    name: str
    symbol_type: str  # "class", "function", "async_function", "method"
    file_path: str
    line: int
    end_line: int
    parent: Optional[str] = None
    docstring: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "symbol_type": self.symbol_type,
            "file_path": self.file_path,
            "line": self.line,
            "end_line": self.end_line,
            "parent": self.parent,
            "docstring": self.docstring,
        }


class ASTSymbolExtractor:
    """Extracts top-level and class-level symbols from Python source code."""

    @staticmethod
    def extract_from_source(source: str, file_path: str) -> Dict[str, ASTSymbol]:
        """Parses Python source code and extracts functions, classes, and methods."""
        symbols: Dict[str, ASTSymbol] = {}
        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError as e:
            logger.debug("Syntax error parsing %s for overlay: %s", file_path, e)
            return symbols

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                end_lineno = getattr(node, "end_lineno", node.lineno)
                symbols[node.name] = ASTSymbol(
                    name=node.name,
                    symbol_type="class",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=end_lineno,
                    docstring=doc,
                )
                # Extract methods within class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_type = "method"
                        method_doc = ast.get_docstring(item)
                        m_end = getattr(item, "end_lineno", item.lineno)
                        qualified_name = f"{node.name}.{item.name}"
                        symbols[qualified_name] = ASTSymbol(
                            name=item.name,
                            symbol_type=method_type,
                            file_path=file_path,
                            line=item.lineno,
                            end_line=m_end,
                            parent=node.name,
                            docstring=method_doc,
                        )
            elif isinstance(node, ast.AsyncFunctionDef):
                doc = ast.get_docstring(node)
                end_lineno = getattr(node, "end_lineno", node.lineno)
                symbols[node.name] = ASTSymbol(
                    name=node.name,
                    symbol_type="async_function",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=end_lineno,
                    docstring=doc,
                )
            elif isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node)
                end_lineno = getattr(node, "end_lineno", node.lineno)
                symbols[node.name] = ASTSymbol(
                    name=node.name,
                    symbol_type="function",
                    file_path=file_path,
                    line=node.lineno,
                    end_line=end_lineno,
                    docstring=doc,
                )

        return symbols

    @classmethod
    def extract_from_file(cls, path: Path, repo_root: Path) -> Dict[str, ASTSymbol]:
        """Reads file from disk and extracts symbols."""
        if not path.is_file():
            return {}
        try:
            rel_path = str(path.relative_to(repo_root))
        except ValueError:
            rel_path = str(path)

        if not path.suffix.lower() == ".py":
            return {}

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return cls.extract_from_source(content, rel_path)
        except Exception as e:
            logger.debug("Failed reading file %s: %s", path, e)
            return {}


class SconesOverlayEngine:
    """
    SCONES Working-Tree Diff Overlay Engine.

    Maintains:
    1. Baseline index: AST symbols from baseline commit/files.
    2. Dynamic Overlay: Fast fresh-parse of modified and untracked files in working tree.
    3. Merged Effective View: Baseline ⊕ Overlay without global reindexing.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self._lock = threading.RLock()
        self._baseline_symbols: Dict[str, Dict[str, ASTSymbol]] = {}  # {rel_path: {sym_name: ASTSymbol}}
        self._baseline_commit: Optional[str] = None
        self._last_baseline_scan: float = 0.0

    def get_current_commit_sha(self) -> Optional[str]:
        """Returns the current Git HEAD commit SHA, or None if not a git repo."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=5.0,
            )
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception as e:
            logger.debug("Could not determine git HEAD: %s", e)
        return None

    def get_working_tree_changes(self) -> Dict[str, str]:
        """
        Returns map of changed files in working tree: {rel_path: status_code}.
        status_code: 'M' (modified), 'A' (added/untracked), 'D' (deleted).
        """
        changes: Dict[str, str] = {}
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=5.0,
            )
            if res.returncode != 0:
                return changes

            for line in res.stdout.splitlines():
                if len(line) < 4:
                    continue
                code = line[:2]
                raw_path = line[3:].strip()
                if " -> " in raw_path:  # Rename
                    raw_path = raw_path.split(" -> ")[1].strip()

                clean_path = raw_path.strip('"')
                if "D" in code:
                    changes[clean_path] = "D"
                elif "?" in code or "A" in code:
                    changes[clean_path] = "A"
                elif "M" in code:
                    changes[clean_path] = "M"
        except Exception as e:
            logger.debug("Error checking git status: %s", e)
        return changes

    def build_baseline_index(self, paths: Optional[List[str]] = None) -> int:
        """
        Indexes baseline symbols for target paths or critical core directories.
        Returns total number of indexed symbols.
        """
        with self._lock:
            self._baseline_commit = self.get_current_commit_sha()
            target_dirs = paths or ["core", "services", "apps"]
            total_symbols = 0

            for rel_dir in target_dirs:
                dir_path = self.repo_root / rel_dir
                if not dir_path.is_dir():
                    continue

                for py_file in dir_path.rglob("*.py"):
                    if ".venv" in py_file.parts or "__pycache__" in py_file.parts:
                        continue
                    try:
                        rel = str(py_file.relative_to(self.repo_root))
                    except ValueError:
                        rel = str(py_file)

                    syms = ASTSymbolExtractor.extract_from_file(py_file, self.repo_root)
                    if syms:
                        self._baseline_symbols[rel] = syms
                        total_symbols += len(syms)

            self._last_baseline_scan = time.time()
            logger.info("Baseline symbol index built: %d symbols across %d files.", total_symbols, len(self._baseline_symbols))
            return total_symbols

    def get_effective_symbols(self, file_path: Optional[str] = None) -> Dict[str, ASTSymbol]:
        """
        Computes effective symbols via Baseline ⊕ Diff Overlay.
        If file_path is specified, returns symbols for that specific file.
        Otherwise returns all active symbols across indexed files.
        """
        with self._lock:
            changes = self.get_working_tree_changes()
            effective: Dict[str, ASTSymbol] = {}

            # Case 1: Specific file requested
            if file_path:
                norm_path = str(file_path).lstrip("./")
                change_status = changes.get(norm_path)

                if change_status == "D":
                    # File deleted in working tree
                    return {}

                if change_status in ("M", "A") or norm_path not in self._baseline_symbols:
                    # Fresh parse of changed or untracked file
                    full_path = self.repo_root / norm_path
                    return ASTSymbolExtractor.extract_from_file(full_path, self.repo_root)

                # Unchanged file: return from baseline
                return self._baseline_symbols.get(norm_path, {}).copy()

            # Case 2: Full graph requested
            # 1. Start with baseline for all non-deleted files
            for rel_file, syms in self._baseline_symbols.items():
                if changes.get(rel_file) == "D":
                    continue
                if changes.get(rel_file) in ("M", "A"):
                    continue  # Will be overlaid next
                effective.update(syms)

            # 2. Overlay modified or added files
            for rel_file, status in changes.items():
                if status == "D" or not rel_file.endswith(".py"):
                    continue
                full_path = self.repo_root / rel_file
                fresh_syms = ASTSymbolExtractor.extract_from_file(full_path, self.repo_root)
                effective.update(fresh_syms)

            return effective

    def resolve_symbol(self, symbol_name: str, file_hint: Optional[str] = None) -> Optional[ASTSymbol]:
        """
        Resolves a symbol by name, incorporating working-tree changes immediately.
        """
        symbols = self.get_effective_symbols(file_path=file_hint)
        if symbol_name in symbols:
            return symbols[symbol_name]

        # If not found in file_hint or no hint provided, search full effective graph
        if file_hint:
            all_symbols = self.get_effective_symbols(file_path=None)
            if symbol_name in all_symbols:
                return all_symbols[symbol_name]

        return None
