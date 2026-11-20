# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/validate_skill_bundle.py"
# purpose: "Skill Bundle Validator & Core-Size Ratchet Gate (Assimilated from rebelytics/one-skill-to-rule-them-all)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-21"
# author: "DNK Swarm (gerych_builder & Gerych Prime)"
# --- END DNK-MRH-HEADER ---

"""
validate_skill_bundle.py — Validates skill bundles against structural invariants.

Assimilated patterns from rebelytics/one-skill-to-rule-them-all:
1. Core-size ratchet: SKILL.md body line count ceiling (default 750 lines).
2. Clean frontmatter (name, description within character limits).
3. Residue detection: merge conflict markers, unfinished TODO/FIXME placeholders.
4. Reference integrity: validates that referenced supporting files in references/ exist.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

MAX_CORE_LINES = 750
MAX_DESC_CHARS = 1024
NAME_RE = re.compile(r"^[a-z0-9]+([-_][a-z0-9]+)*$")
REF_PATH_RE = re.compile(r"`(references/[a-zA-Z0-9_\-\./]+)`")
CONFLICT_MARKERS = [
    re.compile(r"^<{7}\s+"),
    re.compile(r"^={7}\s*$"),
    re.compile(r"^>{7}\s+"),
]
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX):\s*(fill|replace|write|add details)\b", re.IGNORECASE)


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str, Optional[str]]:
    """
    Extracts YAML frontmatter and markdown body from SKILL.md.
    Supports leading DNK-MRH headers before the YAML frontmatter.
    Returns (frontmatter_dict, body_str, error_msg).
    """
    lines = content.splitlines(keepends=True)
    if not lines:
        return None, "", "File is empty"

    # Skip leading DNK-MRH header comments if present
    idx = 0
    if lines[0].strip().startswith(("# --- DNK-MRH-HEADER ---", "<!-- --- DNK-MRH-HEADER ---")):
        while idx < len(lines):
            line_str = lines[idx].strip()
            idx += 1
            if line_str in ("# --- END DNK-MRH-HEADER ---", "--- END DNK-MRH-HEADER --- -->"):
                break
        # Skip empty lines after MRH header
        while idx < len(lines) and not lines[idx].strip():
            idx += 1

    remaining_lines = lines[idx:]
    if not remaining_lines:
        return None, "", "File has no content after MRH header"

    if remaining_lines[0].strip() != "---":
        return None, "".join(remaining_lines), "Missing starting '---' delimiter for YAML frontmatter"

    # Find closing delimiter
    end_idx = -1
    for i in range(1, len(remaining_lines)):
        if remaining_lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return None, "".join(remaining_lines), "Unclosed YAML frontmatter (missing ending '---')"

    fm_text = "".join(remaining_lines[1:end_idx])
    body_text = "".join(remaining_lines[end_idx + 1:])

    try:
        fm_data = yaml.safe_load(fm_text)
        if not isinstance(fm_data, dict):
            return None, body_text, f"YAML frontmatter must be a mapping, got {type(fm_data).__name__}"
        return fm_data, body_text, None
    except Exception as e:
        return None, body_text, f"YAML parse error: {e}"


def validate_skill_file(skill_path: Path, max_lines: int = MAX_CORE_LINES, hub_root: Optional[Path] = None) -> List[str]:
    """Validates a single SKILL.md file and its bundle directory."""
    errors: List[str] = []

    if not skill_path.exists():
        return [f"File does not exist: {skill_path}"]

    if skill_path.name != "SKILL.md":
        return [f"Expected file named SKILL.md, got {skill_path.name}"]

    skill_dir = skill_path.parent
    if skill_dir.name.startswith("_TEMPLATE"):
        return []  # Skip template definitions

    content = skill_path.read_text(encoding="utf-8", errors="replace")
    total_lines = len(content.splitlines())

    # 1. Core-size ratchet
    if total_lines > max_lines:
        errors.append(
            f"Core-size ratchet breached: {total_lines} lines > ceiling of {max_lines} lines. "
            "Relegate secondary details, prompt catalogs, or APIs into references/."
        )

    # 2. Extract & validate YAML frontmatter
    fm, body, fm_err = extract_frontmatter(content)
    if fm_err or fm is None:
        errors.append(fm_err or "Missing frontmatter")
    else:
        # Validate 'name'
        name = fm.get("name")
        if not name or not isinstance(name, str):
            errors.append("Frontmatter must contain a non-empty string 'name'")
        elif not NAME_RE.match(name):
            errors.append(f"Skill name '{name}' must be kebab-case or snake_case (^[a-z0-9]+([-_][a-z0-9]+)*$)")

        # Validate 'description'
        desc = fm.get("description")
        if not desc or not isinstance(desc, str):
            errors.append("Frontmatter must contain a non-empty string 'description'")
        elif len(desc) > MAX_DESC_CHARS:
            errors.append(f"Skill description exceeds {MAX_DESC_CHARS} characters (got {len(desc)})")

    # 3. Residue checks in body
    for line_num, line in enumerate(body.splitlines(), start=1):
        for marker in CONFLICT_MARKERS:
            if marker.search(line):
                errors.append(f"Line {line_num}: git merge conflict marker detected: {line.strip()}")
                break

        if PLACEHOLDER_RE.search(line):
            errors.append(f"Line {line_num}: placeholder note left in: {line.strip()}")

    # 4. Reference integrity check (explicit references/ relative to skill directory)
    for match in REF_PATH_RE.finditer(body):
        ref_rel = match.group(1)
        ref_file = skill_dir / ref_rel
        if not ref_file.exists():
            errors.append(f"Referenced skill file does not exist: `{ref_rel}` (checked at {ref_file})")

    return errors


def get_affected_skill_files(hub_root: Path) -> List[Path]:
    """Retrieves affected/modified SKILL.md files from git status/diff."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(hub_root),
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                path_str = parts[1]
                if Path(path_str).name == "SKILL.md":
                    full_p = hub_root / path_str
                    if full_p.exists():
                        files.append(full_p)
        return files
    except Exception:
        return []


def audit_skills(
    skill_paths: List[Path],
    max_lines: int = MAX_CORE_LINES,
    hub_root: Optional[Path] = None,
    ratchet_warn: bool = False,
) -> Tuple[int, int, List[Tuple[Path, List[str]]], List[Tuple[Path, str]]]:
    failures = []
    warnings = []
    passed = 0
    for p in skill_paths:
        errs = validate_skill_file(p, max_lines=max_lines, hub_root=hub_root)
        if errs:
            fatal_errs = []
            for e in errs:
                if "Core-size ratchet breached" in e and ratchet_warn:
                    warnings.append((p, e))
                else:
                    fatal_errs.append(e)
            if fatal_errs:
                failures.append((p, fatal_errs))
            else:
                passed += 1
        else:
            passed += 1
    return passed, len(failures), failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="DNK OS Skill Bundle Validator & Ratchet Gate")
    parser.add_argument("path", nargs="?", help="Specific SKILL.md file or skill directory to validate")
    parser.add_argument("--all", action="store_true", help="Audit all skills in the repository")
    parser.add_argument("--affected", action="store_true", help="Audit only modified/staged skills from git")
    parser.add_argument("--max-lines", type=int, default=MAX_CORE_LINES, help=f"Line ratchet limit (default: {MAX_CORE_LINES})")
    parser.add_argument("--ratchet-warn", action="store_true", help="Treat core-size ratchet breaches as warnings instead of fatal errors")
    args = parser.parse_args()

    hub_root = Path(__file__).resolve().parent.parent.parent

    target_files: List[Path] = []

    if args.path:
        p = Path(args.path).resolve()
        if p.is_dir():
            target_files.append(p / "SKILL.md")
        else:
            target_files.append(p)
    elif args.affected:
        target_files = get_affected_skill_files(hub_root)
        if not target_files:
            print("✅ No modified SKILL.md files detected in git status.")
            return 0
    elif args.all:
        search_dirs = [
            hub_root / "core" / "orchestrator" / "agents" / "gerych_prime" / "skills",
            hub_root / "core" / "skills",
        ]
        for sdir in search_dirs:
            if sdir.exists():
                for found in sdir.rglob("SKILL.md"):
                    if "_TEMPLATE" not in str(found):
                        target_files.append(found)

    if not target_files:
        parser.print_help()
        return 1

    print(f"🔍 Auditing {len(target_files)} skill bundle(s) (Ratchet ceiling: {args.max_lines} lines)...")
    passed, failed, failures, warnings = audit_skills(
        target_files,
        max_lines=args.max_lines,
        hub_root=hub_root,
        ratchet_warn=args.ratchet_warn,
    )

    if warnings:
        print()
        for path, w in warnings:
            print(f"⚠️ WARN: {path.relative_to(hub_root) if path.is_relative_to(hub_root) else path}")
            print(f"   - {w}")

    if failures:
        print()
        for path, errs in failures:
            print(f"❌ FAIL: {path.relative_to(hub_root) if path.is_relative_to(hub_root) else path}")
            for err in errs:
                print(f"   - {err}")
            print()
        print(f"💥 Validation failed: {failed}/{len(target_files)} skills had errors.")
        return 1

    print(f"✅ 100% PASS: All {passed} skill bundle(s) compliant with core-size ratchet and bundle invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
