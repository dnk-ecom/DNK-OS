#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/sota-repository-assimilation/scripts/sweep_untranslated_chinese.py"
# purpose: "Deterministic scanner for untranslated Chinese strings in assimilated UI/server codebases."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import argparse
import os
import re
import sys

CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
IGNORED_DIRS = {".git", "node_modules", "dist", "build", ".venv", "target", "cache", "coverage"}
VALID_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".html", ".vue", ".svelte", ".py"}

def sweep_directory(target_dir: str):
    matches = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if any(f.endswith(ext) for ext in VALID_EXTS):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                        for idx, line in enumerate(fp, start=1):
                            if CHINESE_PATTERN.search(line):
                                matches.append((path, idx, line.strip()))
                except Exception as e:
                    print(f"Error reading {path}: {e}", file=sys.stderr)
    return matches

def main():
    parser = argparse.ArgumentParser(description="Sweep for untranslated Chinese characters.")
    parser.add_argument("dir", nargs="?", default=".", help="Root directory to scan (default: current dir)")
    parser.add_argument("--fail-on-match", action="store_true", help="Exit with code 1 if matches are found.")
    args = parser.parse_args()

    matches = sweep_directory(args.dir)
    print(f"Total untranslated Chinese lines found: {len(matches)}")
    for path, line_no, content in matches[:50]:
        print(f"{path}:{line_no} -> {content[:100]}")
    if len(matches) > 50:
        print(f"... and {len(matches) - 50} more lines.")

    if args.fail_on_match and matches:
        sys.exit(1)

if __name__ == "__main__":
    main()
