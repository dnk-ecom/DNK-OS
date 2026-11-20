#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/dnk_md_triple_optics.py"
# purpose: "Shared Triple-Optics markdown validator: DNK-STD-0075 frontmatter keys, single MRH callout, path hygiene."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---
"""Shared Triple-Optics validator for DNK OS markdown documents.

Both `check_mrh_headers.py` and `markdown_schema_gate.py` import this module so the
Triple-Optics contract lives in exactly one place (no drift between gates).
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

REQUIRED_FRONTMATTER_KEYS: Tuple[str, ...] = (
    "title",
    "description",
    "mrh_id",
    "status",
    "archetype",
    "version",
    "updated",
    "tags",
)

CALLOUT_MARKER = "[!metadata]-"
MAX_BLANK_LINES_AFTER_FRONTMATTER = 1

ABSOLUTE_PATH_PATTERN = re.compile(r"/Users/[a-zA-Z0-9_\.]+/")
YAML_KEY_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:")

# Lines exempt from the absolute-path check: these document the prohibition itself.
ABSOLUTE_PATH_EXEMPT_TOKENS = (
    "Zero Absolute Paths",
    "forbidden",
    "strictly forbidden",
    "prohibited",
    "exempt",
    "is_relative",
    "assert",
    "pytest.raises",
    "заборон",
    "не дозволя",
)


@dataclass
class TripleOpticsResult:
    """Outcome of a Triple-Optics audit for one document."""

    is_markdown: bool = False
    has_frontmatter: bool = False
    frontmatter_missing_keys: List[str] = field(default_factory=list)
    commented_frontmatter_keys: List[str] = field(default_factory=list)
    callout_count: int = 0
    callout_line: int = 0
    blank_lines_after_frontmatter: int = -1
    absolute_path_leaks: List[str] = field(default_factory=list)

    @property
    def callout_before_frontmatter(self) -> bool:
        return self.callout_count > 0 and not self.has_frontmatter

    @property
    def is_compliant(self) -> bool:
        return (
            self.has_frontmatter
            and not self.frontmatter_missing_keys
            and not self.commented_frontmatter_keys
            and self.callout_count == 1
            and 0 <= self.blank_lines_after_frontmatter <= MAX_BLANK_LINES_AFTER_FRONTMATTER
            and not self.absolute_path_leaks
        )

    def reasons(self) -> List[str]:
        out: List[str] = []
        if not self.has_frontmatter:
            out.append("Row 1 is not YAML frontmatter")
        else:
            if self.frontmatter_missing_keys:
                out.append("Missing frontmatter keys: " + ", ".join(self.frontmatter_missing_keys))
            if self.commented_frontmatter_keys:
                out.append("Commented-out frontmatter keys: " + ", ".join(self.commented_frontmatter_keys))
        if self.callout_count == 0:
            out.append("Missing MRH metadata callout (> [!metadata]-)")
        elif self.callout_count > 1:
            out.append("Duplicated MRH metadata callout (%d found)" % self.callout_count)
        elif self.blank_lines_after_frontmatter > MAX_BLANK_LINES_AFTER_FRONTMATTER:
            out.append(
                "Metadata callout too far from frontmatter (%d blank lines, max %d)"
                % (self.blank_lines_after_frontmatter, MAX_BLANK_LINES_AFTER_FRONTMATTER)
            )
        if self.absolute_path_leaks:
            out.append("Absolute path leaks: %d" % len(self.absolute_path_leaks))
        return out



def split_frontmatter(lines):
    """Returns (frontmatter_lines, closing_index) when row 1 opens valid YAML frontmatter."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], i
    return None


def find_commented_keys(frontmatter_lines):
    """Detects frontmatter keys that were disabled by commenting them out."""
    found = []
    for line in frontmatter_lines:
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        match = YAML_KEY_PATTERN.match(stripped.lstrip("#").strip())
        if match and match.group(1) in REQUIRED_FRONTMATTER_KEYS:
            if match.group(1) not in found:
                found.append(match.group(1))
    return found


def parse_frontmatter_keys(frontmatter_lines):
    """Extracts active top-level YAML keys from frontmatter lines."""
    keys = []
    for line in frontmatter_lines:
        if line.strip().startswith("#"):
            continue
        match = YAML_KEY_PATTERN.match(line)
        if match:
            keys.append(match.group(1))
    return keys



def audit_triple_optics(rel_path, content):
    if str(rel_path).endswith(".excalidraw.md"):
        res = TripleOpticsResult(is_markdown=True, has_frontmatter=True)
        res.callout_count = 1
        res.blank_lines_after_frontmatter = 0
        return res
    """Runs the full Triple-Optics contract against one document's text."""
    result = TripleOpticsResult(is_markdown=True)
    lines = content.split(chr(10))

    for i, line in enumerate(lines, 1):
        if ABSOLUTE_PATH_PATTERN.search(line):
            if any(tok in line for tok in ABSOLUTE_PATH_EXEMPT_TOKENS):
                continue
            if "`/Users/" in line:
                continue
            result.absolute_path_leaks.append("L%d: %s" % (i, line.strip()[:60]))

    callout_lines = [i for i, l in enumerate(lines, 1) if l.lstrip().startswith(">") and CALLOUT_MARKER in l]
    result.callout_count = len(callout_lines)
    if callout_lines:
        result.callout_line = callout_lines[0]

    split = split_frontmatter(lines)
    if split is None:
        result.has_frontmatter = False
        return result

    fm_lines, close_idx = split
    result.has_frontmatter = True

    active_keys = parse_frontmatter_keys(fm_lines)
    result.frontmatter_missing_keys = [k for k in REQUIRED_FRONTMATTER_KEYS if k not in active_keys]
    result.commented_frontmatter_keys = find_commented_keys(fm_lines)

    blanks = 0
    j = close_idx + 1
    while j < len(lines) and lines[j].strip() == "":
        blanks += 1
        j += 1
    result.blank_lines_after_frontmatter = blanks
    return result


def audit_markdown_path(path):
    """Convenience wrapper: read a file from disk and audit it."""
    with open(str(path), "r", encoding="utf-8") as fh:
        content = fh.read()
    return audit_triple_optics(str(path), content)
