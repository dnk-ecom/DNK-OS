#!/usr/bin/env python3
"""
Verify No Unicode/ASCII Box Characters in Vault Notes.
Scans markdown files for characters from the box-drawing set to ensure full Dual-Optics migration.
"""
import sys
import argparse
from pathlib import Path

BOX_CHARS = set("┌┐└┘├┤┬┴┼─│═║╔╗╚╝╠╣╦╩╬")

def scan_files(directory: Path, allowed_files: set = None) -> dict:
    violations = {}
    allowed = allowed_files or set()
    for md_file in sorted(directory.glob("**/*.md")):
        if md_file.name in allowed:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        lines_with_boxes = [
            (i + 1, line)
            for i, line in enumerate(content.splitlines())
            if any(ch in BOX_CHARS for ch in line)
        ]
        if lines_with_boxes:
            violations[str(md_file)] = lines_with_boxes
    return violations

def main():
    parser = argparse.ArgumentParser(description="Scan markdown files for box-drawing characters.")
    parser.add_argument("--path", default="docs/notes", help="Directory to scan")
    parser.add_argument("--strict", action="store_true", help="Exit code 1 on any violation")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Directory {target} not found.")
        sys.exit(0)

    violations = scan_files(target)
    if not violations:
        print(f"✅ Clean! 0 box-drawing characters found in {target}.")
        sys.exit(0)

    print(f"❌ Found {len(violations)} files with box-drawing characters:")
    for path, lines in violations.items():
        print(f"\n📄 {path} ({len(lines)} lines):")
        for line_num, line in lines[:5]:
            print(f"  Line {line_num}: {line[:80]}")
        if len(lines) > 5:
            print(f"  ... and {len(lines) - 5} more lines.")

    if args.strict:
        sys.exit(1)

if __name__ == "__main__":
    main()
