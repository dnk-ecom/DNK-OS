#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/tmp_normalize_arch.py"
# purpose: "Stage C batch normalizer: bring docs/architecture markdown to Triple-Optics compliance."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Transient"
# version: "1.0.0"
# updated_at: "2026-11-18"
# --- END DNK-MRH-HEADER ---
import argparse
import os
import re
import sys

sys.path.insert(0, 'scripts/system')
from dnk_md_triple_optics import (
    REQUIRED_FRONTMATTER_KEYS, MAX_BLANK_LINES_AFTER_FRONTMATTER,
    audit_triple_optics, split_frontmatter, parse_frontmatter_keys,
)

ROOT = 'docs/architecture'
EXCALIDRAW_MARKER = '"type": "excalidraw"'


def infer_archetype(rel_path, content):
    lp = rel_path.lower()
    fn = os.path.basename(lp)
    head = content[:3000].lower()
    if 'contracts/' in lp or fn.startswith('contract'):
        return 'CONTRACT'
    if '/adr/' in lp or fn.startswith('adr-') or fn.startswith('adr_'):
        return 'ADR'
    if 'sota' in fn or 'sota' in head or 'assimilation' in fn:
        return 'SOTA_AUDIT'
    if fn.endswith('_spec.md') or 'spec' in fn or 'blueprint' in fn or '/blueprints/' in lp:
        return 'DEV_SPEC'
    return 'GENERAL_DOC'


def derive_title(rel_path, content, fm_lines):
    for line in fm_lines:
        m = re.match(r'^\s*title\s*:\s*[\"\']?(.+?)[\"\']?\s*$', line)
        if m:
            return m.group(1).strip()
    for line in content.split(chr(10)):
        if line.startswith('# '):
            return line[2:].strip()
    base = os.path.basename(rel_path)[:-3]
    return base.replace('_', ' ').replace('-', ' ').strip()


def derive_description(rel_path, archetype):
    kind = {
        'ADR': 'Architecture Decision Record',
        'CONTRACT': 'Interface contract',
        'SOTA_AUDIT': 'SOTA assimilation audit',
        'DEV_SPEC': 'Architecture specification',
        'GENERAL_DOC': 'Architecture document',
    }[archetype]
    stem = os.path.basename(rel_path)[:-3].replace('_', ' ').replace('-', ' ')
    return '%s for DNK OS: %s.' % (kind, stem)



def derive_tags(rel_path, archetype):
    parts = rel_path.replace('\\', '/').split('/')
    tags = ['dnk-os', 'dnk/architecture']
    if archetype != 'GENERAL_DOC':
        tags.append('dnk/' + archetype.lower().replace('_', '-'))
    if 'adr' in parts:
        tags.append('dnk/adr')
    if 'reports' in parts:
        tags.append('dnk/report')
    if 'specs' in parts or 'blueprints' in parts:
        tags.append('dnk/spec')
    seen = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    return seen


def render_frontmatter(rel_path, content, archetype, existing_keys, fm_lines):
    title = derive_title(rel_path, content, fm_lines).replace('"', "'")
    desc = derive_description(rel_path, archetype).replace('"', "'")
    out = []
    out.append('---')
    out.append('title: "%s"' % title)
    out.append('description: "%s"' % desc)
    out.append('mrh_id: "%s"' % rel_path)
    out.append('status: Active')
    out.append('archetype: %s' % archetype)
    out.append('version: "2.0.0"')
    out.append('updated: 2026-11-18')
    out.append('tags:')
    for t in derive_tags(rel_path, archetype):
        out.append('  - %s' % t)
    out.append('---')
    return out



def render_callout(rel_path, archetype, purpose):
    return [
        "> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)",
        "> ```yaml",
        "> # --- DNK-MRH-HEADER ---",
        "> mrh_id: \"%s\"" % rel_path,
        "> purpose: \"%s\"" % purpose.replace('"', "'"),
        "> canonical_source: false",
        "> alters_files: []",
        "> triggers_tasks: []",
        "> status: \"Active\"",
        "> version: \"2.0.0\"",
        "> updated_at: \"2026-11-18\"",
        "> # --- END DNK-MRH-HEADER ---",
        "> ```",
    ]


def strip_leading_mrh_block(lines):
    """Removes an existing legacy DNK-MRH-HEADER block (raw or HTML-wrapped)."""
    out = list(lines)
    start = None
    for i, l in enumerate(out[:40]):
        if '--- DNK-MRH-HEADER ---' in l:
            start = i
            break
    if start is None:
        return out
    end = None
    for j in range(start, min(len(out), start + 40)):
        if '--- END DNK-MRH-HEADER' in out[j]:
            end = j
            break
    if end is None:
        return out
    lo, hi = start, end
    if lo > 0 and out[lo - 1].strip() == '<!--':
        lo -= 1
    if hi + 1 < len(out) and out[hi + 1].strip() == '-->':
        hi += 1
    while hi + 1 < len(out) and out[hi + 1].strip() == '':
        hi += 1
    return out[:lo] + out[hi + 1:]


def drop_leading_callouts(lines):
    """Removes existing MRH metadata callouts (and their fenced yaml) from the head."""
    out = list(lines)
    while True:
        idx = None
        for i, l in enumerate(out[:60]):
            if l.strip().startswith('> [!metadata]-'):
                idx = i
                break
        if idx is None:
            return out
        hi = idx
        for j in range(idx, min(len(out), idx + 40)):
            if out[j].strip() in ('> ```', '>```'):
                hi = j
                break
        else:
            hi = idx
        while hi + 1 < len(out) and out[hi + 1].strip() == '':
            hi += 1
        out = out[:idx] + out[hi + 1:]


def normalize_document(rel_path, content):
    lines = content.split(chr(10))
    split = split_frontmatter(lines)
    if split is not None:
        fm_lines, close_idx = split
        body = lines[close_idx + 1:]
    else:
        fm_lines, body = [], lines
    body = strip_leading_mrh_block(body)
    body = drop_leading_callouts(body)
    while body and body[0].strip() == '':
        body.pop(0)
    archetype = infer_archetype(rel_path, content)
    existing = set(parse_frontmatter_keys(fm_lines))
    purpose = derive_description(rel_path, archetype)
    new = render_frontmatter(rel_path, content, archetype, existing, fm_lines)
    new.append('')
    new.extend(render_callout(rel_path, archetype, purpose))
    new.append('')
    new.extend(body)
    text = chr(10).join(new)
    if not text.endswith(chr(10)):
        text += chr(10)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    files = []
    for root, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != 'archive']
        for n in names:
            if n.endswith('.md'):
                files.append(os.path.join(root, n))
    files.sort()
    changed = skipped = failed = 0
    compl = 0
    for rel in files:
        content = open(rel, encoding='utf-8').read()
        if EXCALIDRAW_MARKER in content:
            skipped += 1
            continue
        before = audit_triple_optics(rel, content)
        if before.is_compliant:
            compl += 1
            continue
        after_text = normalize_document(rel, content)
        verdict = audit_triple_optics(rel, after_text)
        if not verdict.is_compliant:
            failed += 1
            print('STILL-BAD %s -> %s' % (rel, verdict.reasons()))
            continue
        if args.write:
            open(rel, 'w', encoding='utf-8', newline=chr(10)).write(after_text)
        changed += 1
    print('files=%d changed=%d compliant=%d skipped_excalidraw=%d failed=%d' % (len(files), changed, compl, skipped, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
