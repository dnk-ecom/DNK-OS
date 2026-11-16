#!/usr/bin/env python3
import os
import pathlib
import re
import sys

# Configuration: Resolve root dynamically relative to this script
root_dir = pathlib.Path(__file__).resolve().parents[2]
extensions = {'.js', '.ts', '.py', '.html', '.css'}
exclude_dirs = {'node_modules', 'dist', 'build', '.git', '.venv', '.next', '__pycache__', 'vendor', 'coverage', 'visual_shell', 'assets', 'cache', 'logs'}

# Regular expressions for MRH block
start_pattern = re.compile(r'^#\s*--- DNK-MRH-HEADER ---\s*$')
end_pattern = re.compile(r'^#\s*--- END DNK-MRH-HEADER ---\s*$')

# Patterns for required fields inside the MRH block
field_patterns = {
    'mrh_id': re.compile(r'^\s*#\s*mrh_id\s*:'),
    'purpose': re.compile(r'^\s*#\s*purpose\s*:'),
    'date': re.compile(r'^\s*#\s*(date|updated_at)\s*:'),
}

def is_excluded(filepath):
    """Check if file is in excluded directories."""
    parts = os.path.normpath(filepath).split(os.sep)
    return any(part in exclude_dirs for part in parts)

def get_source_files():
    """Yield paths of source files with given extensions, excluding certain dirs."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for f in filenames:
            if any(f.endswith(ext) for ext in extensions):
                yield os.path.join(dirpath, f)

def check_mrh_header(filepath):
    """Check if file has a valid MRH header.
    Returns (bool, list of missing fields)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    # Find the MRH block
    in_block = False
    block_lines = []
    for line in lines:
        stripped = line.rstrip()
        if start_pattern.match(stripped):
            in_block = True
            continue  # skip the start line
        if end_pattern.match(stripped):
            in_block = False
            break  # stop at end line
        if in_block:
            block_lines.append(stripped)

    if not block_lines:
        return False, ["No MRH block found"]

    # Check for each required field in the block
    missing = []
    for field, pattern in field_patterns.items():
        if not any(pattern.match(line) for line in block_lines):
            missing.append(field)

    return len(missing) == 0, missing

def main():
    errors = []
    files_checked = 0
    for filepath in get_source_files():
        if is_excluded(filepath):
            continue
        files_checked += 1
        valid, missing = check_mrh_header(filepath)
        if not valid:
            errors.append((filepath, missing))

    print(f"Checked {files_checked} source files.")
    if errors:
        print(f"\nFound {len(errors)} files with missing or malformed MRH headers:")
        for filepath, missing in errors:
            print(f"  {filepath}: missing fields: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("\nAll source files have valid MRH headers.")
        sys.exit(0)

if __name__ == '__main__':
    main()
