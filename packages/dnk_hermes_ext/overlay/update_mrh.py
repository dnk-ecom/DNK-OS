import os
import re

def update_mrh_header(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find the start and end of the MRH header
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == '# --- DNK-MRH-HEADER ---':
            start_idx = i
            break
    if start_idx is None:
        # No MRH header found, we will add one at the top? But the task assumes it exists.
        # According to the task, we are to supplement existing headers.
        # If there's no header, we skip? But the context says all files have MRH headers.
        # We'll skip for now.
        return False

    for i in range(start_idx, len(lines)):
        if lines[i].strip() == '# --- END DNK-MRH-HEADER ---':
            end_idx = i
            break
    if end_idx is None:
        return False

    # Extract the header lines (including the start and end markers)
    header_lines = lines[start_idx:end_idx+1]

    # We'll look for author and license lines in the header
    author_line_idx = None
    license_line_idx = None
    for i, line in enumerate(header_lines):
        stripped = line.strip()
        if stripped.startswith('# author:'):
            author_line_idx = i
        elif stripped.startswith('# license:'):
            license_line_idx = i

    # If we found them, update the values
    changed = False
    if author_line_idx is not None:
        # Replace the line
        old_line = header_lines[author_line_idx]
        new_line = '# author: "DNK-e.com Maksym"\n'
        if old_line != new_line:
            header_lines[author_line_idx] = new_line
            changed = True
    else:
        # Insert after the purpose line? We'll insert after the line that starts with '# purpose:'
        # Find the purpose line
        for i, line in enumerate(header_lines):
            if line.strip().startswith('# purpose:'):
                # Insert after this line
                header_lines.insert(i+1, '# author: "DNK-e.com Maksym"\n')
                changed = True
                break
        else:
            # If no purpose line, insert at the end (before the END line)
            header_lines.insert(-1, '# author: "DNK-e.com Maksym"\n')
            changed = True

    if license_line_idx is not None:
        old_line = header_lines[license_line_idx]
        new_line = '# license: "MIT"\n'
        if old_line != new_line:
            header_lines[license_line_idx] = new_line
            changed = True
    else:
        # Insert after the author line (if we just added it) or after purpose line
        # We'll re-scan the header_lines for author line.
        for i, line in enumerate(header_lines):
            if line.strip().startswith('# author:'):
                header_lines.insert(i+1, '# license: "MIT"\n')
                changed = True
                break
        else:
            # No author line, insert after purpose line
            for i, line in enumerate(header_lines):
                if line.strip().startswith('# purpose:'):
                    header_lines.insert(i+1, '# license: "MIT"\n')
                    changed = True
                    break
            else:
                # Still not found, insert before the END line
                header_lines.insert(-1, '# license: "MIT"\n')
                changed = True

    if changed:
        # Replace the header in the lines
        lines[start_idx:end_idx+1] = header_lines
        with open(filepath, 'w') as f:
            f.writelines(lines)
        return True
    else:
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Find all .py files
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip hidden directories and __pycache__, node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    # Find dnk_manifest.yaml files
    manifest_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        for file in files:
            if file == 'dnk_manifest.yaml':
                manifest_files.append(os.path.join(root, file))

    all_files = py_files + manifest_files
    updated = []
    for f in all_files:
        if update_mrh_header(f):
            updated.append(f)
            print(f"Updated: {f}")
        else:
            print(f"No change or no header: {f}")

    print(f"\nUpdated {len(updated)} files.")

if __name__ == '__main__':
    main()
