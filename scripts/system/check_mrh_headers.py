#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/check_mrh_headers.py"
# purpose: "Unified MRH & Relative Path Auditor & Normalizer for DNK OS codebase (DNK-STD-0075)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-13"
# author: "Antigravity (Mentor & Chief Architect) & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dnk_md_triple_optics import TripleOpticsResult, audit_triple_optics  # noqa: E402

# Supported extensions for MRH auditing
EXTENSIONS: Set[str] = {".py", ".ts", ".js", ".sh", ".md", ".yaml", ".yml"}

# Directories excluded from repository scans
EXCLUDE_DIRS: Set[str] = {
    "node_modules", ".venv", ".git", ".next", "dist", "build",
    "__pycache__", ".pytest_cache", "coverage", "vendor", "cache",
    "sessions", "artifacts", ".data", ".od", ".worktrees", "archive", "decisions", "distillations"
}

# Regex patterns for MRH delimiters
START_PATTERN = re.compile(r'^(?:>\s*)?(?:<!--\s*)?(?:#|//)?\s*---\s*DNK-MRH-HEADER\s*---\s*$')
END_PATTERN = re.compile(r'^(?:>\s*)?(?:#|//)?\s*---\s*END DNK-MRH-HEADER(?:\s*---)?\s*(?:-->)?$')

# Pattern for mrh_id extraction and replacement
MRH_ID_PATTERN = re.compile(r'^(?:\s*>\s*)?(\s*(?:#|//)?\s*mrh_id\s*:\s*[\"\x27]?)([^\"\x27\r\n]+)([\"\x27]?.*)$')

# Required fields inside the MRH block
FIELD_PATTERNS: Dict[str, re.Pattern] = {
    "mrh_id": re.compile(r'^(?:\s*>\s*)?\s*(?:#|//)?\s*mrh_id\s*:'),
    "purpose": re.compile(r'^(?:\s*>\s*)?\s*(?:#|//)?\s*purpose\s*:'),
    "date": re.compile(r'^(?:\s*>\s*)?\s*(?:#|//)?\s*(date|updated_at)\s*:'),
}

# Forbidden absolute path leak pattern
ABSOLUTE_PATH_PATTERN = re.compile(r'/Users/[a-zA-Z0-9_\.]+/')


@dataclass
class FileAuditResult:
    rel_path: str
    has_mrh: bool = False
    is_markdown_dual_reader: bool = False
    mrh_id_value: Optional[str] = None
    mrh_id_matches_path: bool = False
    missing_fields: List[str] = field(default_factory=list)
    absolute_path_leaks: List[str] = field(default_factory=list)
    fixed: bool = False
    triple_optics: Optional[TripleOpticsResult] = None

    @property
    def is_compliant(self) -> bool:
        dual = self.is_markdown_dual_reader if self.rel_path.endswith('.md') else True
        triple = True
        if self.rel_path.endswith('.md') and self.triple_optics is not None:
            triple = self.triple_optics.is_compliant
        return (
            self.has_mrh
            and self.mrh_id_matches_path
            and len(self.missing_fields) == 0
            and len(self.absolute_path_leaks) == 0
            and dual
            and triple
        )


def audit_file(file_path: Path, repo_root: Path) -> FileAuditResult:
    """Audits a single file for MRH structure, canonical relative mrh_id, and path hygiene."""
    try:
        rel_str = str(file_path.relative_to(repo_root))
    except ValueError:
        rel_str = str(file_path)

    result = FileAuditResult(rel_path=rel_str)
    if not file_path.is_file():
        result.missing_fields.append("File not found")
        return result

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        result.missing_fields.append(f"Read error: {e}")
        return result

    lines = content.splitlines()

    if rel_str.endswith(".md"):
        result.triple_optics = audit_triple_optics(rel_str, content)

    in_block = False
    block_lines: List[str] = []
    block_start_idx = -1
    block_end_idx = -1

    for idx, line in enumerate(lines[:120]):
        stripped = line.strip()
        if not in_block and START_PATTERN.match(stripped):
            in_block = True
            block_start_idx = idx
            continue
        if in_block and END_PATTERN.match(stripped):
            in_block = False
            block_end_idx = idx
            break
        if in_block:
            block_lines.append(stripped)

    if block_start_idx != -1 and block_end_idx != -1:
        result.has_mrh = True

        # Check Markdown Dual-Reader HTML comment encapsulation or Obsidian collapsible callout
        if rel_str.endswith(".md"):
            start_line = lines[block_start_idx].strip()
            end_line = lines[block_end_idx].strip()
            has_html = ("<!--" in start_line or (block_start_idx > 0 and "<!--" in lines[block_start_idx - 1])) and ("-->" in end_line or (block_end_idx + 1 < len(lines) and "-->" in lines[block_end_idx + 1]))
            has_callout = any("[!metadata]-" in line for line in lines[max(0, block_start_idx - 5):block_start_idx])
            if has_html or has_callout:
                result.is_markdown_dual_reader = True

        # Check required fields and mrh_id value
        for field_name, pattern in FIELD_PATTERNS.items():
            found = False
            for bline in block_lines:
                if pattern.match(bline):
                    found = True
                    if field_name == "mrh_id":
                        m = MRH_ID_PATTERN.match(bline)
                        if m:
                            val = m.group(2).strip()
                            result.mrh_id_value = val
                            if val == rel_str:
                                result.mrh_id_matches_path = True
                    break
            if not found:
                result.missing_fields.append(field_name)
    elif rel_str.endswith(".json"):
        try:
            jdata = json.loads(content)
            mrh = jdata.get("_mrh") or jdata.get("_mrh_header") or jdata.get("mrh_header")
            if not mrh and "mrh_id" in jdata:
                mrh = jdata
            if mrh and isinstance(mrh, dict):
                result.has_mrh = True
                val = mrh.get("mrh_id")
                result.mrh_id_value = val
                if val == rel_str:
                    result.mrh_id_matches_path = True
                for field_name in ["mrh_id", "purpose"]:
                    if field_name not in mrh:
                        result.missing_fields.append(field_name)
                if not any(k in mrh for k in ["date", "updated_at"]):
                    result.missing_fields.append("date")
        except Exception as e:
            result.missing_fields.append(f"JSON read error: {e}")

    # Check for hardcoded absolute paths (excluding self-documenting negative rules)
    for line_idx, line in enumerate(lines, start=1):
        if ABSOLUTE_PATH_PATTERN.search(line):
            # Ignore comments/rules that explicitly document forbidding absolute paths
            if any(exempt in line for exempt in [
                "Zero Absolute Paths", "forbidden", "strictly forbidden", "exempt",
                "is_relative", "assert", "pytest.raises"
            ]):
                continue
            result.absolute_path_leaks.append(f"L{line_idx}: {line.strip()[:60]}")

    return result


def fix_file(file_path: Path, repo_root: Path, audit: FileAuditResult, dry_run: bool = False) -> bool:
    """Safely normalizes mrh_id to match relative path and wraps Markdown MRH in Dual-Reader format."""
    if not audit.has_mrh:
        return False

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    modified = False
    lines = content.splitlines()

    # 1. Align mrh_id to exact relative path
    if not audit.mrh_id_matches_path:
        new_lines = []
        for line in lines:
            if re.search(r'^(?:\s*>\s*)?\s*(?:#|//)?\s*mrh_id\s*:', line):
                line = re.sub(r'^((?:\s*>\s*)?\s*(?:#|//)?\s*mrh_id\s*:\s*).*$', rf'\g<1>"{audit.rel_path}"', line)
                modified = True
            new_lines.append(line)
        lines = new_lines

    # 2. Encapsulate Markdown MRH in Dual-Reader comments if missing
    if audit.rel_path.endswith(".md") and not audit.is_markdown_dual_reader:
        new_lines = []
        in_mrh = False
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not in_mrh and START_PATTERN.match(stripped):
                in_mrh = True
                if not stripped.startswith("<!--"):
                    new_lines.append("<!--")
                new_lines.append(line)
                continue
            if in_mrh and END_PATTERN.match(stripped):
                in_mrh = False
                new_lines.append(line)
                if not stripped.endswith("-->"):
                    new_lines.append("-->")
                modified = True
                continue
            new_lines.append(line)
        lines = new_lines

    if modified and not dry_run:
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        audit.fixed = True
        return True

    return modified


def gather_files(repo_root: Path, targets: List[str], domain: Optional[str] = None) -> List[Path]:
    """Collects candidate files for inspection based on paths or domain filters."""
    collected: List[Path] = []
    if targets:
        for t in targets:
            p = Path(t)
            if not p.is_absolute():
                p = repo_root / p
            if p.is_file():
                collected.append(p)
            elif p.is_dir():
                for root, dirs, files in os.walk(p):
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    for f in files:
                        fp = Path(root) / f
                        if fp.suffix in EXTENSIONS:
                            collected.append(fp)
        return collected

    scan_roots = [repo_root / domain] if domain else [repo_root]
    for base in scan_roots:
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                fp = Path(root) / f
                if fp.suffix in EXTENSIONS:
                    collected.append(fp)
    return collected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified MRH Header & Relative Path Hygiene Auditor for DNK OS."
    )
    parser.add_argument("files", nargs="*", help="Specific files or directories to inspect.")
    parser.add_argument("--domain", "-d", help="Filter by canonical domain (e.g., docs, core, services).")
    parser.add_argument("--audit", action="store_true", help="Run deep audit with summary metrics.")
    parser.add_argument("--fix", action="store_true", help="Auto-remediate divergent mrh_id and dual-reader formatting.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate fixes without modifying files.")
    parser.add_argument("--json", action="store_true", dest="json_mode", help="Output results in JSON format.")

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    files = gather_files(repo_root, args.files, args.domain)

    results: List[FileAuditResult] = []
    for fp in files:
        res = audit_file(fp, repo_root)
        if args.fix:
            fix_file(fp, repo_root, res, dry_run=args.dry_run)
        results.append(res)

    compliant = [r for r in results if r.is_compliant]
    non_compliant = [r for r in results if not r.is_compliant]
    fixed = [r for r in results if r.fixed]

    if args.json_mode:
        data = {
            "total": len(results),
            "compliant": len(compliant),
            "non_compliant": len(non_compliant),
            "fixed": len(fixed),
            "results": [asdict(r) for r in results if not r.is_compliant or args.audit]
        }
        print(json.dumps(data, indent=2))
        return 1 if non_compliant and not args.fix else 0

    print("================================================================================")
    print("🛡️ DNK OS UNIFIED MRH & RELATIVE PATH AUDITOR (DNK-STD-0075)")
    print("================================================================================")
    print(f"📁 Files Scanned: {len(results)}")
    print(f"✅ 100% Compliant: {len(compliant)}")
    print(f"⚠️ Non-Compliant: {len(non_compliant)}")
    if args.fix:
        print(f"🔧 Automatically Fixed: {len(fixed)}")
    print("================================================================================")

    if non_compliant and (args.audit or not args.fix):
        print("\n🔍 Breakdown of Issues:")
        for r in non_compliant[:30]:  # Show top 30
            reasons = []
            if not r.has_mrh:
                reasons.append("Missing MRH header")
            elif not r.mrh_id_matches_path:
                reasons.append(f"mrh_id mismatch: '{r.mrh_id_value}' != '{r.rel_path}'")
            if r.missing_fields:
                reasons.append(f"Missing fields: {', '.join(r.missing_fields)}")
            if r.rel_path.endswith('.md') and not r.is_markdown_dual_reader:
                reasons.append("Markdown MRH not encapsulated in <!-- ... -->")
            if r.rel_path.endswith('.md') and r.triple_optics is not None:
                reasons.extend(r.triple_optics.reasons())
            if r.absolute_path_leaks:
                reasons.append(f"Absolute path leaks: {len(r.absolute_path_leaks)}")

            status_icon = "🔧" if r.fixed else "❌"
            print(f"  {status_icon} {r.rel_path} ➔ {'; '.join(reasons)}")

        if len(non_compliant) > 30:
            print(f"  ... and {len(non_compliant) - 30} more non-compliant files.")

    print("\n💡 Run with '--fix' to automatically normalize mrh_id and dual-reader comments.")
    return 1 if non_compliant and not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
