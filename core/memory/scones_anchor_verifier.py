# --- DNK-MRH-HEADER ---
# mrh_id: "core/memory/scones_anchor_verifier.py"
# purpose: "Anchor Verification Engine for SCONES memory facts, SKILL.md files, and ADRs."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

"""
SCONES Anchor Verification Engine (DEC-045 / entire-brain pattern).

Prevents agent memory drift and hallucinations:
Validates whether physical files and AST symbols referenced in:
1. SCONES Durable Facts
2. SKILL.md and reference cards
3. Architecture Decision Records (ADRs)
actually exist on disk and in the current AST graph.
Categorizes anchors as:
- VERIFIED: File exists AND symbol exists in file.
- STALE: File exists, but symbol was renamed or deleted.
- BROKEN: Referenced file does not exist.
"""

from __future__ import annotations

import ast
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.memory.scones_overlay import ASTSymbolExtractor

logger = logging.getLogger("dnk.core.memory.anchor_verifier")


class AnchorStatus(str, Enum):
    VERIFIED = "verified"
    STALE = "stale"
    BROKEN = "broken"


@dataclass
class AnchorRef:
    """A reference to a source file and optional symbol/line."""
    file_path: str
    symbol: Optional[str] = None
    line: Optional[int] = None
    source_doc: Optional[str] = None
    raw_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "symbol": self.symbol,
            "line": self.line,
            "source_doc": self.source_doc,
            "raw_reference": self.raw_reference,
        }


@dataclass
class VerificationResult:
    """Outcome of verifying an anchor against disk and AST."""
    anchor: AnchorRef
    status: AnchorStatus
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.anchor.file_path,
            "symbol": self.anchor.symbol,
            "line": self.anchor.line,
            "source_doc": self.anchor.source_doc,
            "status": self.status.value,
            "message": self.message,
        }


class SconesAnchorVerifier:
    """
    Validates physical existence and AST symbol validity of anchors.
    """

    # Regex patterns for markdown references
    _FILE_SYMBOL_REGEX = re.compile(
        r"(?:file:\s*|`)?([a-zA-Z0-9_\-/\\]+\.(?:py|ts|tsx|js|json|yaml|yml|md|liquid|sh))(?:#([a-zA-Z0-9_\.]+)|:(\d+))?`?"
    )

    def __init__(self, repo_root: Optional[Union[str, Path]] = None) -> None:
        self.repo_root = Path(repo_root or Path.cwd()).resolve()

    def verify_anchor(self, anchor: AnchorRef) -> VerificationResult:
        """
        Validates an individual anchor against the repository.
        """
        clean_rel_path = anchor.file_path.strip().lstrip("./").lstrip("/")
        full_path = self.repo_root / clean_rel_path

        # 1. File existence check
        if not full_path.exists() or not full_path.is_file():
            return VerificationResult(
                anchor=anchor,
                status=AnchorStatus.BROKEN,
                message=f"Target file does not exist: {clean_rel_path}",
            )

        # 2. Line number check (if specified)
        if anchor.line is not None and anchor.line > 0:
            try:
                line_count = len(full_path.read_text(encoding="utf-8", errors="replace").splitlines())
                if anchor.line > line_count:
                    return VerificationResult(
                        anchor=anchor,
                        status=AnchorStatus.STALE,
                        message=f"Line {anchor.line} exceeds file length ({line_count} lines) in {clean_rel_path}",
                    )
            except Exception as e:
                logger.debug("Failed reading file %s for line check: %s", full_path, e)

        # 3. Symbol verification
        if anchor.symbol:
            sym_name = anchor.symbol.strip()
            if full_path.suffix.lower() == ".py":
                # AST parse for python
                symbols = ASTSymbolExtractor.extract_from_file(full_path, self.repo_root)
                # Allow direct name or class.method matching
                if sym_name not in symbols and not any(s.name == sym_name for s in symbols.values()):
                    return VerificationResult(
                        anchor=anchor,
                        status=AnchorStatus.STALE,
                        message=f"Symbol '{sym_name}' not found in AST of {clean_rel_path}",
                    )
            else:
                # Text/regex pattern check for non-python files
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                    if sym_name not in content:
                        return VerificationResult(
                            anchor=anchor,
                            status=AnchorStatus.STALE,
                            message=f"Token '{sym_name}' not found in text of {clean_rel_path}",
                        )
                except Exception as e:
                    logger.debug("Failed checking text in %s: %s", full_path, e)

        return VerificationResult(
            anchor=anchor,
            status=AnchorStatus.VERIFIED,
            message=f"Anchor verified: {clean_rel_path}" + (f" #{anchor.symbol}" if anchor.symbol else ""),
        )

    def extract_anchors_from_markdown(self, markdown_text: str, source_doc: str = "") -> List[AnchorRef]:
        """
        Extracts anchor references from markdown text.
        Supports structured JSON blocks and markdown code/link patterns.
        """
        anchors: List[AnchorRef] = []
        seen: Set[Tuple[str, Optional[str], Optional[int]]] = set()

        # Check for JSON anchors block: {"anchors": [...]}
        for json_match in re.finditer(r"```json\s*(\{[\s\S]*?\})\s*```", markdown_text):
            try:
                data = json.loads(json_match.group(1))
                if isinstance(data, dict) and "anchors" in data and isinstance(data["anchors"], list):
                    for item in data["anchors"]:
                        f = item.get("file")
                        if f:
                            s = item.get("symbol")
                            l = item.get("line")
                            key = (f, s, l)
                            if key not in seen:
                                seen.add(key)
                                anchors.append(
                                    AnchorRef(
                                        file_path=f,
                                        symbol=s,
                                        line=l,
                                        source_doc=source_doc,
                                        raw_reference=json_match.group(0),
                                    )
                                )
            except Exception:
                pass

        # Regex scan for file paths, symbol fragments, and line anchors
        for match in self._FILE_SYMBOL_REGEX.finditer(markdown_text):
            raw_path = match.group(1)
            # Skip URLs and common false positives
            if "http://" in raw_path or "https://" in raw_path or raw_path.startswith("node_modules/"):
                continue

            symbol = match.group(2)
            line = int(match.group(3)) if match.group(3) else None

            # Only retain if the file path has valid directory structure
            if "/" in raw_path or raw_path.endswith((".py", ".ts", ".tsx", ".yaml", ".yml")):
                key = (raw_path, symbol, line)
                if key not in seen:
                    seen.add(key)
                    anchors.append(
                        AnchorRef(
                            file_path=raw_path,
                            symbol=symbol,
                            line=line,
                            source_doc=source_doc,
                            raw_reference=match.group(0),
                        )
                    )

        return anchors

    def audit_file(self, file_path: Union[str, Path]) -> List[VerificationResult]:
        """Audits all anchors in a single markdown file."""
        p = Path(file_path)
        if not p.is_file():
            return []
        try:
            rel = str(p.relative_to(self.repo_root))
        except ValueError:
            rel = str(p)

        content = p.read_text(encoding="utf-8", errors="replace")
        anchors = self.extract_anchors_from_markdown(content, source_doc=rel)
        return [self.verify_anchor(a) for a in anchors]

    def audit_directory(
        self,
        target_dir: Union[str, Path],
        file_glob: str = "*.md",
    ) -> Dict[str, Any]:
        """
        Audits all markdown files in target directory.
        Returns aggregated summary and broken/stale details.
        """
        dir_p = self.repo_root / str(target_dir).lstrip("./")
        if not dir_p.is_dir():
            return {
                "total_anchors": 0,
                "verified": 0,
                "stale": 0,
                "broken": 0,
                "results": [],
            }

        all_results: List[VerificationResult] = []
        for doc in dir_p.rglob(file_glob):
            results = self.audit_file(doc)
            all_results.extend(results)

        verified = sum(1 for r in all_results if r.status == AnchorStatus.VERIFIED)
        stale = sum(1 for r in all_results if r.status == AnchorStatus.STALE)
        broken = sum(1 for r in all_results if r.status == AnchorStatus.BROKEN)

        return {
            "total_anchors": len(all_results),
            "verified": verified,
            "stale": stale,
            "broken": broken,
            "results": [r.to_dict() for r in all_results],
        }
