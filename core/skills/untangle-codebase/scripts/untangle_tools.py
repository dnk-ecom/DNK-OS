# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/untangle-codebase/scripts/untangle_tools.py"
# purpose: "Evidence tools for the untangle-codebase skill: code skeleton, import graph with volatility, git co-change pairs"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-07"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---
"""Read-only evidence for the untangle-codebase skill. Stdlib only.

  skeleton  <scope>                      Python signatures + docstring first lines, bodies stripped
  imports   <scope> [--root R]           who imports whom inside the repo, with git volatility per file;
                                         flags edges where a stable file imports a more volatile one
  cochange  <scope> [--since 6.months]   file pairs that change together in git, and whether they share a folder

<scope> is a file or folder path relative to the repo root (run from the repo root).
Python is parsed with ast; .ts/.tsx/.js/.jsx/.mjs imports are read with a regex (relative imports only).
"""
from __future__ import annotations

import argparse
import ast
import itertools
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".pytest_cache", "cache"}
PY = {".py"}
JS = {".ts", ".tsx", ".js", ".jsx", ".mjs"}
JS_IMPORT = re.compile(r"""(?:import|export)\s[^'"]*?from\s*['"](\.[^'"]+)['"]|require\(\s*['"](\.[^'"]+)['"]\s*\)|import\(\s*['"](\.[^'"]+)['"]\s*\)""")


def iter_files(scope: Path, exts: set[str]):
    if scope.is_file():
        if scope.suffix in exts:
            yield scope
        return
    for dirpath, dirnames, filenames in os.walk(scope):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.suffix in exts:
                yield p


# ---------- skeleton ----------
def _sig(node: ast.AST, src: str) -> str:
    seg = ast.get_source_segment(src, node) or ""
    head = seg.split(":\n", 1)[0] if ":\n" in seg else seg.splitlines()[0]
    return " ".join(head.split()) + ":"


def skeleton(scope: Path) -> int:
    for f in iter_files(scope, PY):
        try:
            src = f.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"# {f}: skipped ({type(e).__name__})")
            continue
        print(f"# ===== {f}")

        def walk(body, indent=""):
            for n in body:
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    print(indent + " ".join((ast.get_source_segment(src, n) or "").split()))
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    for d in n.decorator_list:
                        print(f"{indent}@{ast.get_source_segment(src, d)}")
                    print(indent + _sig(n, src))
                    doc = ast.get_docstring(n)
                    if doc:
                        print(f'{indent}    """{doc.strip().splitlines()[0]}"""')
                    if isinstance(n, ast.ClassDef):
                        walk(n.body, indent + "    ")
                    else:
                        print(indent + "    ...")
                elif isinstance(n, (ast.Assign, ast.AnnAssign)) and not indent:
                    line = (ast.get_source_segment(src, n) or "").splitlines()[0]
                    print(line[:160])
        walk(tree.body)
    return 0


# ---------- git helpers ----------
def git_lines(args: list[str]) -> list[str]:
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"# git unavailable, churn/co-change empty: {getattr(e, 'stderr', '') or e}".strip(), file=sys.stderr)
        return []
    return out.splitlines()


def commit_files(scope: Path, since: str) -> list[list[str]]:
    commits, cur = [], []
    for line in git_lines(["log", f"--since={since}", "--no-merges", "--name-only", "--format=format:@@C", "--", str(scope)]):
        if line == "@@C":
            if cur:
                commits.append(cur)
            cur = []
        elif line.strip():
            cur.append(line.strip())
    if cur:
        commits.append(cur)
    return commits


# ---------- imports ----------
def py_module_index(root: Path) -> dict[str, Path]:
    idx = {}
    for f in iter_files(root, PY):
        rel = f.relative_to(root).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            idx[".".join(parts)] = f.relative_to(root)
    return idx


def py_imports(f: Path, root: Path, idx: dict[str, Path]) -> set[Path]:
    try:
        tree = ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    rel = f.relative_to(root).with_suffix("")
    pkg = list(rel.parts[:-1]) if rel.name != "__init__" else list(rel.parts[:-1])
    names = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            base = n.module or ""
            if n.level:
                up = pkg[: len(pkg) - (n.level - 1)] if n.level > 1 else pkg
                base = ".".join([*up, base] if base else up)
            names.append(base)
            names += [f"{base}.{a.name}" for a in n.names]
    hits = set()
    for name in names:
        while name:
            if name in idx:
                hits.add(idx[name])
                break
            name = name.rpartition(".")[0]
    hits.discard(f.relative_to(root))
    return hits


def js_imports(f: Path, root: Path) -> set[Path]:
    try:
        text = f.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    hits = set()
    for m in JS_IMPORT.finditer(text):
        spec = next(g for g in m.groups() if g)
        base = (f.parent / spec).resolve()
        for cand in [base, *(base.with_suffix(e) for e in JS), *(base / f"index{e}" for e in JS)]:
            if cand.is_file():
                try:
                    hits.add(cand.relative_to(root.resolve()))
                except ValueError:
                    pass
                break
    return hits


def imports(scope: Path, root: Path, since: str) -> int:
    idx = py_module_index(root)
    edges: dict[Path, set[Path]] = {}
    for f in iter_files(scope, PY | JS):
        edges[f.relative_to(root) if f.is_absolute() else f] = (
            py_imports(f, root, idx) if f.suffix in PY else js_imports(f, root))
    churn = Counter(p for c in commit_files(scope, since) for p in c)
    fan_in = Counter(t for ts in edges.values() for t in ts)
    print(f"# import graph: {len(edges)} files, {sum(len(v) for v in edges.values())} edges, churn window {since}")
    for src in sorted(edges, key=str):
        for dst in sorted(edges[src], key=str):
            print(f"{src} -> {dst}")
    print("\n# volatility inversions (importer changed less often than what it imports)")
    found = 0
    for src, ts in sorted(edges.items(), key=lambda kv: str(kv[0])):
        for dst in ts:
            cs, cd = churn.get(str(src), 0), churn.get(str(dst), 0)
            if cd > cs * 2 and cd >= 3:
                found += 1
                print(f"{src} (churn {cs}) -> {dst} (churn {cd})")
    if not found:
        print("none")
    print("# highest fan-in (most depended on)")
    for p, n in fan_in.most_common(15):
        print(f"{n:4d}  {p}  churn={churn.get(str(p), 0)}")
    return 0


# ---------- cochange ----------
def cochange(scope: Path, since: str, top: int) -> int:
    commits = [c for c in commit_files(scope, since) if 2 <= len(c) <= 30]
    pairs, single = Counter(), Counter()
    for c in commits:
        files = sorted(set(c))
        single.update(files)
        pairs.update(itertools.combinations(files, 2))
    print(f"# co-change: {len(commits)} commits (2..30 files) since {since} under {scope}")
    print("# count  confidence  same_dir  a  <->  b")
    for (a, b), n in pairs.most_common(top):
        if n < 2:
            break
        conf = n / min(single[a], single[b])
        same = os.path.dirname(a) == os.path.dirname(b)
        flag = "" if same else "  <-- split across folders"
        print(f"{n:5d}  {conf:9.2f}  {str(same):8s}  {a}  <->  {b}{flag}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("skeleton"); s.add_argument("scope")
    i = sub.add_parser("imports"); i.add_argument("scope"); i.add_argument("--root", default="."); i.add_argument("--since", default="6.months")
    c = sub.add_parser("cochange"); c.add_argument("scope"); c.add_argument("--since", default="6.months"); c.add_argument("--top", type=int, default=40)
    a = ap.parse_args(argv)
    scope = Path(a.scope)
    if not scope.exists():
        print(f"scope not found: {scope}", file=sys.stderr)
        return 2
    if a.cmd == "skeleton":
        return skeleton(scope)
    if a.cmd == "imports":
        return imports(scope, Path(a.root), a.since)
    return cochange(scope, a.since, a.top)


if __name__ == "__main__":
    sys.exit(main())
