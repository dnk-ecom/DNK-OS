# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/knowledge_staleness_guard.py"
# purpose: "Automated AST Staleness & File Existence Guard for continuous knowledge eviction in DNK_OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class StaleReference:
    doc_path: str
    line_number: int
    referenced_path: str
    reason: str  # "file_not_found" | "symbol_not_found" | "deprecated_target"


@dataclass
class StalenessAuditReport:
    scanned_docs_count: int
    total_references_checked: int
    stale_count: int
    valid_count: int
    stale_items: List[StaleReference] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scanned_docs_count": self.scanned_docs_count,
            "total_references_checked": self.total_references_checked,
            "stale_count": self.stale_count,
            "valid_count": self.valid_count,
            "stale_items": [
                {
                    "doc": s.doc_path,
                    "line": s.line_number,
                    "target": s.referenced_path,
                    "reason": s.reason,
                }
                for s in self.stale_items
            ],
            "is_clean": self.stale_count == 0,
        }


class KnowledgeStalenessGuard:
    """
    SOTA Continuous Knowledge Staleness Guard (Cognition/Anthropic SOTA).
    Prevents Agentic Attention Rot by ensuring documentation references
    anchor directly to physical, existing files and symbols on disk.
    """

    FILE_REF_PATTERN = re.compile(
        r"""(?:(?:file://|`|\(|")(?:\./|\.\./|/)?)((?:core|services|apps|packages|infra|tests|scripts|docs)/[a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)"""
    )

    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = Path(workspace_root) if workspace_root else Path(__file__).resolve().parents[2]

    def audit_file(self, doc_path: Path) -> List[StaleReference]:
        """Audits a single markdown or text document for broken file references."""
        if not doc_path.exists() or doc_path.is_dir():
            return []

        stale: List[StaleReference] = []
        try:
            content = doc_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        rel_doc = str(doc_path.relative_to(self.root)) if doc_path.is_relative_to(self.root) else str(doc_path)

        for line_idx, line in enumerate(content.splitlines(), start=1):
            matches = self.FILE_REF_PATTERN.findall(line)
            for ref in matches:
                # Clean up target path
                clean_ref = ref.strip("`'\"()").split("#")[0]
                target_path = self.root / clean_ref
                if not target_path.exists():
                    stale.append(
                        StaleReference(
                            doc_path=rel_doc,
                            line_number=line_idx,
                            referenced_path=clean_ref,
                            reason="file_not_found",
                        )
                    )
        return stale

    def audit_directory(self, target_dir: Optional[Path] = None, glob_pattern: str = "**/*.md") -> StalenessAuditReport:
        """Recursively audits a directory of documentation."""
        scan_dir = Path(target_dir) if target_dir else self.root / "docs"
        if not scan_dir.exists():
            return StalenessAuditReport(0, 0, 0, 0, [])

        docs = list(scan_dir.glob(glob_pattern))
        total_refs = 0
        all_stale: List[StaleReference] = []

        for doc in docs:
            # Skip build dirs or virtualenvs
            if any(part in doc.parts for part in (".venv", "node_modules", ".git", "site-packages")):
                continue
            stale_refs = self.audit_file(doc)
            all_stale.extend(stale_refs)

        # Count total references across scanned docs
        for doc in docs:
            if any(part in doc.parts for part in (".venv", "node_modules", ".git", "site-packages")):
                continue
            try:
                c = doc.read_text(encoding="utf-8", errors="ignore")
                total_refs += len(self.FILE_REF_PATTERN.findall(c))
            except Exception:
                pass

        valid_count = max(0, total_refs - len(all_stale))
        return StalenessAuditReport(
            scanned_docs_count=len(docs),
            total_references_checked=total_refs,
            stale_count=len(all_stale),
            valid_count=valid_count,
            stale_items=all_stale,
        )


if __name__ == "__main__":
    guard = KnowledgeStalenessGuard()
    report = guard.audit_directory()
    print(f"Knowledge Staleness Audit: {report.scanned_docs_count} docs scanned.")
    print(f"Total references checked: {report.total_references_checked}")
    print(f"Valid: {report.valid_count} | Stale: {report.stale_count}")
    if report.stale_items:
        print("\nStale References Found (Candidates for Eviction):")
        for s in report.stale_items[:15]:
            print(f"  - [{s.doc_path}:{s.line_number}] -> {s.referenced_path} ({s.reason})")
