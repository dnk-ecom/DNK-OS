# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/dossier.py"
# purpose: "Deterministic half of the repository dossier: pin a commit, pick and fetch the files worth reading, collect hints and risks, then verify the agent's dossier against what was actually read"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Dossier = the evidence a terminal agent needs to understand one repository without guessing.

prepare():  pin HEAD to a commit sha, read the file tree, choose up to N files within a byte budget,
            fetch exactly those files at that sha, and attach deterministic hints (README claims and
            where the code mentions them, mechanic keywords, risk patterns). Nothing is executed or installed.
check():    verify the agent's finished dossier against the pinned snapshot: every citation must point to a
            file that was read and to lines that exist, and the license must allow the stated action.

The agent does the judging; this module guarantees the facts it judges from, and catches invented ones.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from pydantic import BaseModel, Field

from services.dnk_git_research.src.domain_terms import DOMAINS
from services.dnk_git_research.src.license_policy import ReuseAction, classify_license
from services.dnk_git_research.src.niche_profiles import _EXEC_EXT, _SECRET_EXT, _SECRET_NAMES, _clean, analyse_tree, detect_niches
from services.dnk_git_research.src.repo_signals import RateLimited, _meta, github_full_name

MAX_FILES, MAX_BYTES, PER_FILE = 25, 60_000, 12_000

_BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".zip",
               ".gz", ".tar", ".rar", ".7z", ".mp4", ".mp3", ".wav", ".mov", ".exe", ".dll", ".so", ".dylib", ".bin",
               ".pyc", ".class", ".jar", ".lock", ".map", ".min.js", ".min.css")
_LOCKS = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "cargo.lock", "composer.lock", "gemfile.lock")
_MANIFESTS = ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "cargo.toml", "pom.xml", "build.gradle",
              "composer.json", "gemfile", "setup.py", "deno.json", "bun.lockb")
_ENTRY = ("main", "index", "app", "cli", "server", "__main__", "mod", "lib", "core")
_SRC_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".c", ".cpp", ".h",
            ".swift", ".liquid", ".lua", ".sh", ".rego", ".yar", ".yara", ".sql")
_CODE_DIRS = ("services/", "core/", "src/", "lib/", "pkg/", "internal/", "app/", "server/", "agents/", "skills/")
_ASSET_DIRS = ("prompts/", "templates/", "presets/", "rules/", "policies/", "sections/", "snippets/", "blocks/")
_AGENT_FILES = ("skill.md", "claude.md", "agents.md", ".cursorrules", ".mcp.json")

_SECRETS = (
    ("AWS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GITHUB_TOKEN", re.compile(r"\b(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GENERIC_SECRET", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]")),
)
_RISK_PATTERNS = (
    ("DYNAMIC_EXEC", re.compile(r"\beval\s*\(|\bexec\s*\(|new Function\s*\(|child_process|subprocess\.(?:Popen|call|run)|os\.system")),
    ("OBFUSCATION", re.compile(r"atob\s*\(|base64\.b64decode|fromCharCode|\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){7,}")),
    ("INSTALL_HOOK", re.compile(r"\"(?:pre|post)?install\"\s*:|\"prepare\"\s*:")),
)
_URL = re.compile(r"https?://([A-Za-z0-9.\-]+)")
_COMMON_HOSTS = ("github.com", "githubusercontent.com", "localhost", "example.com", "w3.org", "npmjs.com", "googleapis.com",
                 "fonts.gstatic.com", "schema.org", "apache.org", "mozilla.org", "reactjs.org", "tailwindcss.com")


class FileSnapshot(BaseModel):
    path: str
    size: int
    lines: int
    truncated: bool = False
    text: str
    ranges: List[List[int]] = Field(default_factory=list)   # [] = whole text shown; otherwise only these line ranges are shown to the agent


class Hit(BaseModel):
    path: str
    line: int
    text: str


class DossierInput(BaseModel):
    repo: str
    url: str = ""
    sha: str
    fetched_at: str
    meta: Dict[str, Any] = Field(default_factory=dict)
    license: Dict[str, Any] = Field(default_factory=dict)
    niches: List[str] = Field(default_factory=list)
    content: Dict[str, Any] = Field(default_factory=dict)
    catalog: Dict[str, Any] = Field(default_factory=dict)
    curation: Optional[Dict[str, Any]] = None
    tree_files: int = 0
    files: List[FileSnapshot] = Field(default_factory=list)
    skipped: List[str] = Field(default_factory=list)
    claim_hints: List[Dict[str, Any]] = Field(default_factory=list)
    mechanic_hints: Dict[str, List[Hit]] = Field(default_factory=dict)
    risk_hints: List[Dict[str, Any]] = Field(default_factory=list)
    budget: Dict[str, int] = Field(default_factory=dict)
    scan: Dict[str, Any] = Field(default_factory=dict)      # whole-repo scan: counts per class, skipped examples, logic_loc
    repo_map: str = ""                                      # Aider-style outline of the most relevant files and symbols
    assets: List[Dict[str, Any]] = Field(default_factory=list)   # agents / skills / commands / prompts / MCP tools found in the repo
    tests: List[str] = Field(default_factory=list)          # test names next to the chosen files = behaviour spec


# ----------------------------------------------------------------------------- choose what to read
_NOISE = re.compile(r"(^|/)(testdata|fixtures?|__snapshots__|vendor|third_party|node_modules|\.git)/")


def _focus_hits(pl: str, focus: Sequence[str]) -> int:
    toks = [t for t in re.split(r"[/_.\-]+", pl) if t]
    flat = re.sub(r"[_\-]", "", pl)
    n = 0
    for f in focus:
        if not f:
            continue
        if any(t == f or t.startswith(f) for t in toks) or (re.search(r"[_\-]", f) and re.sub(r"[_\-]", "", f) in flat):
            n += 1                                   # «task_runner» must find task_runners.py: multiword focus matches the flattened path
    return n


def _score(path: str, size: int, focus: Sequence[str] = ()) -> int:
    pl = path.lower()
    base = pl.rsplit("/", 1)[-1]
    stem = base.rsplit(".", 1)[0]
    if base in _LOCKS or pl.endswith(_BINARY_EXT) or _NOISE.search(pl):
        return -1
    n = _focus_hits(pl, focus)
    if size is not None and 0 <= size < 30 and pl.endswith(_SRC_EXT) and base not in _MANIFESTS:
        return -1                                        # empty __init__.py and one-line stubs carry no mechanics
    is_test = bool(re.search(r"(test|spec|__tests__|mock)", pl))
    if n and pl.endswith(_SRC_EXT + (".md",)):          # the task names this area: read it before anything generic
        if size and size < 400:                          # doc.go / meta.go stubs carry no mechanics
            return 40
        return min(99, (50 if is_test else 90) + 3 * n)
    if base.startswith("readme"):
        return 100 if pl.count("/") == 0 else 24         # a nested README describes some other sub-project
    if pl.endswith((".rules", ".rego")):                     # access rules decide who may read what: always worth reading
        return 75
    if base in ("dockerfile", "render.yaml", "vercel.json", "netlify.toml", ".env.example", "fly.toml") or base.startswith("docker-compose") or pl.endswith(".tf"):
        return 45
    if base in _AGENT_FILES or pl.endswith("/skill.md"):
        return 85
    if base in _MANIFESTS and pl.count("/") <= 1:
        return 90
    is_src = pl.endswith(_SRC_EXT)
    if any(pl.startswith(d) for d in _ASSET_DIRS) and pl.endswith((".md", ".txt", ".json", ".yaml", ".yml", ".liquid", ".rego", ".yar")):
        return 65
    if is_src and any(pl.startswith(d) for d in _CODE_DIRS):
        return 60 + (5 if stem in _ENTRY else 0)
    if is_src and stem in _ENTRY and pl.count("/") <= 1:
        return 70
    if pl.startswith(".github/workflows/"):
        return 40
    if is_src:
        return 30 if not re.search(r"(test|spec|__tests__|mock)", pl) else 15
    if pl.endswith(".md") and pl.startswith("docs/"):
        return 25
    return 5


def plan_reads(paths: Sequence[str], sizes: Dict[str, int], max_files: int = MAX_FILES, max_bytes: int = MAX_BYTES,
               per_file: int = PER_FILE, focus: Sequence[str] = ()) -> Tuple[List[str], List[str]]:
    """Files to fetch within the budget, best first, and the notable ones left out."""
    ok = set(_clean(paths))
    keep = [p for p in paths if p.lower().lstrip("/") in ok]
    focus = [f.lower() for f in focus]
    def _key(p: str):
        sc, sz = _score(p, sizes.get(p, 0), focus), min(sizes.get(p, 0), per_file)
        return (sc, sz if sc >= 90 else -sz, p)      # the area in focus: the substantial file first; otherwise cheap files first

    ranked = sorted(((*_key(p)[:2], p) for p in keep), reverse=True)
    chosen, left, spent = [], [], 0
    for score, _, p in ranked:
        if score < 25:
            continue
        cost = min(sizes.get(p, 0), per_file)
        if len(chosen) >= max_files or spent + cost > max_bytes:
            left.append(p)
            continue
        chosen.append(p)
        spent += cost
    return chosen, left[:40]


# ----------------------------------------------------------------------------- deterministic hints (pure)
def readme_claims(text: str, limit: int = 12) -> List[str]:
    """Feature claims: bullet lines of the README, cleaned of markdown."""
    out = []
    for line in text.split("\n"):
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*\S)", line)
        if not m:
            continue
        c = re.sub(r"[*_`]|\[([^\]]*)\]\([^)]*\)", lambda x: x.group(1) or "", m.group(1)).strip()
        if 12 <= len(c) <= 220 and not re.match(r"(?i)(clone|install|run|create|refer|npm|pip|git)\b", c):
            out.append(c)
    return out[:limit]


def _tokens(claim: str) -> List[str]:
    toks = re.findall(r"[A-Za-z][A-Za-z0-9_.\-]{3,}", claim)
    stop = {"with", "that", "this", "your", "from", "using", "into", "based", "powered", "features", "feature", "users",
            "support", "built", "easy", "high", "quality", "simple", "allows", "provides", "through", "their", "which"}
    return [t for t in dict.fromkeys(toks) if t.lower() not in stop][:6]


def find_hits(files: Iterable[FileSnapshot], tokens: Sequence[str], per_token: int = 2, skip_readme: bool = True) -> List[Hit]:
    hits: List[Hit] = []
    for tok in tokens:
        rx = re.compile(re.escape(tok), re.IGNORECASE)
        n = 0
        for f in files:
            if skip_readme and f.path.lower().rsplit("/", 1)[-1].startswith("readme"):
                continue
            for i, line in enumerate(f.text.split("\n"), 1):
                if rx.search(line):
                    hits.append(Hit(path=f.path, line=i, text=line.strip()[:160]))
                    n += 1
                    break
            if n >= per_token:
                break
    return hits


def mechanic_hints(files: Sequence[FileSnapshot], per_domain: int = 3) -> Dict[str, List[Hit]]:
    out: Dict[str, List[Hit]] = {}
    for d in DOMAINS:
        for f in files:
            if f.path.lower().endswith((".md", ".json", ".lock")):
                continue
            for i, line in enumerate(f.text.split("\n"), 1):
                if d.pattern.search(line) and len(line) < 300:
                    out.setdefault(d.key, []).append(Hit(path=f.path, line=i, text=line.strip()[:160]))
                    if len(out[d.key]) >= per_domain:
                        break
            if len(out.get(d.key, [])) >= per_domain:
                break
    return out


def scan_risks(files: Sequence[FileSnapshot]) -> List[Dict[str, Any]]:
    """Path:line risk hints. A secret's value is never copied into the output."""
    out: List[Dict[str, Any]] = []
    hosts: Dict[str, Tuple[str, int]] = {}
    for f in files:
        for i, line in enumerate(f.text.split("\n"), 1):
            for kind, rx in _SECRETS:
                if rx.search(line):
                    out.append({"type": "SECRET_IN_CODE:" + kind, "path": f.path, "line": i})
            if f.path.lower().endswith(_SRC_EXT + (".json",)):
                for kind, rx in _RISK_PATTERNS:
                    if rx.search(line) and not (kind == "INSTALL_HOOK" and not f.path.lower().endswith("package.json")):
                        out.append({"type": kind, "path": f.path, "line": i, "text": line.strip()[:120]})
            for h in _URL.findall(line):
                h = h.lower()
                if not any(h == c or h.endswith("." + c) for c in _COMMON_HOSTS):
                    hosts.setdefault(h, (f.path, i))
    for h, (p, i) in list(hosts.items())[:15]:
        out.append({"type": "EXTERNAL_HOST", "host": h, "path": p, "line": i})
    seen, uniq = set(), []
    for r in out:
        k = (r["type"], r["path"], r["line"]) if "path" in r else json.dumps(r, sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq[:60]


# ----------------------------------------------------------------------------- network
_HDR = {"User-Agent": "DNK-OS-GitResearcher/2.7"}


def _get(url: str, token: Optional[str], accept: str, urlopen: Callable[..., Any], timeout: float = 20.0,
         limit: Optional[int] = None) -> Tuple[bytes, Any]:
    headers = dict(_HDR, Accept=accept)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as resp:
            body = resp.read(limit) if limit else resp.read()
            return body, getattr(resp, "headers", None)
    except urllib.error.HTTPError as exc:
        meta = _meta(exc.headers, exc.code)
        if exc.code in (403, 429) and (meta.remaining == 0 or exc.code == 429):
            raise RateLimited(meta.reset) from exc
        raise


def collect(repo_url_or_id: str, row: Optional[Dict[str, Any]] = None, token: Optional[str] = None,
            curation: Optional[Dict[str, Any]] = None, focus: Sequence[str] = (), claims_in: Sequence[str] = (), urlopen: Callable[..., Any] = urllib.request.urlopen,
            local: Optional[Any] = None, task: str = "", budget_chars: int = 60_000) -> DossierInput:
    """Pin a commit and fetch the evidence. With `local` (a shallow clone) the WHOLE repository is scanned offline
    (repo_map) and symbol-level excerpts are chosen; otherwise about 3 + N API requests (N = files read)."""
    name = github_full_name(repo_url_or_id if "github.com" in repo_url_or_id else f"https://github.com/{repo_url_or_id}")
    if not name:
        raise ValueError(f"not a GitHub repository: {repo_url_or_id}")
    api = f"https://api.github.com/repos/{name}"
    meta = json.loads(_get(api, token, "application/vnd.github+json", urlopen)[0])
    if local is not None:
        from pathlib import Path as _P
        from services.dnk_git_research.src import repo_map as rmap
        import subprocess
        sha = subprocess.run(["git", "-C", str(local), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        tree = {"tree": [{"type": "blob", "path": r, "size": sz} for r, sz in rmap.walk(_P(local))], "truncated": False}
    else:
        sha = _get(f"{api}/commits/HEAD", token, "application/vnd.github.sha", urlopen)[0].decode().strip()
        tree = json.loads(_get(f"{api}/git/trees/{sha}?recursive=1", token, "application/vnd.github+json", urlopen)[0])
    blobs = [t for t in tree.get("tree", []) if t.get("type") == "blob"]
    paths = [t["path"] for t in blobs]
    sizes = {t["path"]: int(t.get("size") or 0) for t in blobs}

    row = row or {"id": name, "url": f"https://github.com/{name}", "description": meta.get("description") or ""}
    spdx = (meta.get("license") or {}).get("spdx_id")
    verdict = classify_license(None if spdx in (None, "NOASSERTION") else spdx)
    niches = detect_niches(row)
    content = analyse_tree(name.lower(), niches, paths, truncated=bool(tree.get("truncated")), sizes=sizes)

    risk_paths = [p for p in paths if (p.lower().rsplit("/", 1)[-1] in _SECRET_NAMES or p.lower().endswith(_SECRET_EXT + _EXEC_EXT))
                  and p.lower().lstrip("/") in set(_clean([p]))][:12]
    content_d = dict(content.model_dump(), risk_paths=risk_paths)
    chosen, left = plan_reads(paths, sizes, focus=focus, max_bytes=MAX_BYTES * 2 if focus else MAX_BYTES, per_file=PER_FILE)   # a named area deserves a deeper read
    files: List[FileSnapshot] = []
    scan_d: Dict[str, Any] = {}
    map_txt, assets_d, tests_l = "", [], []
    if local is not None:
        from pathlib import Path as _P
        from services.dnk_git_research.src import repo_map as rmap
        root = _P(local)
        terms = rmap.query_terms(task, focus)
        rm = rmap.scan(root, terms)
        ranges = rmap.pick_ranges(rm, budget_chars=budget_chars)
        for p, rs in ranges.items():
            text = (root / p).read_text(encoding="utf-8", errors="replace")
            files.append(FileSnapshot(path=p, size=sizes.get(p, len(text)), lines=text.count("\n") + 1, text=text, ranges=[list(r) for r in _merge(rs)]))
        for p in sorted(paths):                                   # README at the root and manifests give identity; shown whole (capped)
            b = p.lower().rsplit("/", 1)[-1]
            if "/" not in p and (b.startswith("readme") or b in _MANIFESTS) and all(f.path != p for f in files):
                text = (root / p).read_text(encoding="utf-8", errors="replace")[:PER_FILE]
                files.append(FileSnapshot(path=p, size=sizes.get(p, len(text)), lines=text.count("\n") + 1, text=text, truncated=sizes.get(p, 0) > len(text)))
        map_txt, assets_d = rmap.outline(rm), [a.model_dump() for a in rm.assets]
        tests_l = rmap.tests_outline(rm, [f.path for f in files if f.ranges])
        scan_d = {"counts": rm.counts, "skipped_examples": rm.skipped_examples, "logic_loc": rm.logic_loc, "terms": terms,
                  "files_with_symbols": sum(1 for f in rm.files.values() if f.symbols), "symbols": sum(len(f.symbols) for f in rm.files.values())}
        chosen = []
    for p in chosen:
        try:
            body, _ = _get(f"{api}/contents/{urllib.parse.quote(p)}?ref={sha}", token, "application/vnd.github.raw", urlopen,
                           limit=PER_FILE)
        except urllib.error.HTTPError:
            left.append(p)
            continue
        text = body.decode("utf-8", "replace")
        files.append(FileSnapshot(path=p, size=sizes.get(p, len(body)), lines=text.count("\n") + 1,
                                  truncated=sizes.get(p, 0) > len(body), text=text))

    readme = next((f for f in files if f.path.lower().rsplit("/", 1)[-1].startswith("readme")), None)
    claims = [{"claim": c, "hits": [h.model_dump() for h in find_hits(files, _tokens(c))]}
              for c in (list(claims_in) or (readme_claims(readme.text) if readme else []))]
    tmpl = meta.get("template_repository") or {}
    return DossierInput(
        repo=name, url=f"https://github.com/{name}", sha=sha, fetched_at=datetime.now(timezone.utc).isoformat(),
        meta={"description": meta.get("description"), "created_at": meta.get("created_at"), "pushed_at": meta.get("pushed_at"),
              "stars": meta.get("stargazers_count"), "forks": meta.get("forks_count"), "archived": meta.get("archived"),
              "fork": meta.get("fork"), "topics": meta.get("topics") or [], "default_branch": meta.get("default_branch"),
              "owner_type": (meta.get("owner") or {}).get("type"), "derived_from": tmpl.get("full_name"),
              "size_kb": meta.get("size")},
        license=verdict.model_dump(mode="json"), niches=niches, content=content_d,
        catalog={k: row.get(k) for k in ("description", "category", "dnk_module_target", "assimilation_status", "license_track") if row.get(k)},
        curation=curation, tree_files=len(paths), files=files, skipped=left,
        claim_hints=claims, mechanic_hints=mechanic_hints(files), risk_hints=scan_risks(files),
        scan=scan_d, repo_map=map_txt, assets=assets_d, tests=tests_l,
        budget={"files": len(files), "bytes": sum(len(f.text) for f in files), "max_files": MAX_FILES, "max_bytes": MAX_BYTES * 2 if focus else MAX_BYTES},
    )


def _merge(rs: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    out: List[List[int]] = []
    for a, b in sorted(rs):
        if out and a <= out[-1][1] + 3:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def render_workorder(inp: DossierInput, prompt_text: str) -> str:
    """One markdown file to hand to the agent: instruction, pinned facts, file index."""
    idx = "\n".join(f"- `{f.path}` ({f.lines} рядків{', обрізано' if f.truncated else ''})" for f in inp.files)
    return (f"# Завдання: досьє `{inp.repo}` @ `{inp.sha[:7]}`\n\n"
            f"Файли вже завантажено на цьому коміті в `dossier_input.json` (поле `files[].text`). "
            f"Цитуй лише їх, у форматі `{inp.sha[:7]}:шлях:Lпочаток-Lкінець`.\n\n"
            f"Ліцензія: `{inp.license.get('spdx') or 'немає'}` → дія `{inp.license.get('action')}`; "
            f"ніші: {', '.join(inp.niches) or 'немає'}; прочитано {len(inp.files)} із {inp.tree_files} файлів.\n\n"
            f"## Прочитані файли\n{idx}\n\n## Не прочитано (за бюджетом)\n" + ("\n".join(f"- `{p}`" for p in inp.skipped[:20]) or "- немає")
            + f"\n\n---\n\n{prompt_text}\n")


# ----------------------------------------------------------------------------- verification of the agent's dossier
_CITE = re.compile(r"(?:[\w.\-]+/[\w.\-]+@)?([0-9a-f]{7,40}):([^\s:,;()]+)(?::L(\d+)(?:-L?(\d+))?)?")
_TIERS = ("KEEP", "WATCH", "REMOVE")
_ACTIONS = ("ADOPT", "ADAPT", "CLEAN_ROOM")
_REQUIRED = ("repo", "sha", "identity", "claims", "mechanics", "risks", "verdict", "unverified")


def _cites(text: str) -> List[Tuple[str, str, Optional[int], Optional[int]]]:
    return [(m.group(1), m.group(2), int(m.group(3)) if m.group(3) else None, int(m.group(4)) if m.group(4) else None)
            for m in _CITE.finditer(text or "")]


def _check_cite(text: str, inp: DossierInput, label: str, issues: List[str], need: bool = True) -> int:
    by_path = {f.path: f for f in inp.files}
    cites, ok = _cites(text), 0
    for sha, path, a, b in cites:
        if not inp.sha.startswith(sha):
            issues.append(f"{label}: sha {sha} не збігається із закріпленим {inp.sha[:7]}")
            continue
        f = by_path.get(path)
        if f is None:
            issues.append(f"{label}: файл {path} не було прочитано")
            continue
        if a is not None:
            hi = b if b is not None else a
            if a < 1 or hi < a or hi > f.lines:
                issues.append(f"{label}: рядки {a}-{hi} поза файлом {path} ({f.lines} рядків)")
                continue
            if f.ranges and not any(r[0] <= a and hi <= r[1] for r in f.ranges):
                shown = ", ".join(f"L{r[0]}-{r[1]}" for r in f.ranges)
                issues.append(f"{label}: рядки {a}-{hi} у {path} не були показані (показано: {shown})")
                continue
        ok += 1
    if need and not cites:
        issues.append(f"{label}: немає цитати у форматі sha:шлях:Lпочаток-Lкінець")
    return ok


def check_dossier(d: Dict[str, Any], inp: DossierInput) -> List[str]:
    """Empty list = the dossier is consistent with what was actually read."""
    issues: List[str] = []
    for k in _REQUIRED:
        if k not in d:
            issues.append(f"немає поля {k}")
    if issues:
        return issues
    if not inp.sha.startswith(str(d["sha"])[:7]):
        issues.append(f"sha досьє {d['sha']} не збігається із закріпленим {inp.sha[:7]}")
    allowed = {"ADOPT": _ACTIONS, "ADAPT": ("ADAPT", "CLEAN_ROOM"), "CLEAN_ROOM": ("CLEAN_ROOM",)}.get(
        str(inp.license.get("action")), ("CLEAN_ROOM",))
    for i, m in enumerate(d["mechanics"]):
        label = f"mechanics[{i}] «{m.get('name', '?')}»"
        if m.get("action") not in _ACTIONS:
            issues.append(f"{label}: невідома дія {m.get('action')!r}")
        elif m["action"] not in allowed:
            issues.append(f"{label}: дія {m['action']} заборонена ліцензією ({inp.license.get('spdx') or 'немає'} → дозволено {', '.join(allowed)})")
        _check_cite(str(m.get("where", "")), inp, label, issues)
    for i, c in enumerate(d["claims"]):
        label = f"claims[{i}] «{str(c.get('claim', ''))[:40]}»"
        status = c.get("status")
        if status not in ("CONFIRMED", "PARTIAL", "NOT_FOUND"):
            issues.append(f"{label}: невідомий статус {status!r}")
        elif status == "CONFIRMED":
            if _check_cite(str(c.get("evidence", "")), inp, label, issues) == 0:
                issues.append(f"{label}: CONFIRMED без жодної дійсної цитати")
        elif c.get("evidence"):
            _check_cite(str(c["evidence"]), inp, label, issues, need=False)
    v = d["verdict"]
    if v.get("tier") not in _TIERS:
        issues.append(f"verdict.tier має бути одним із {_TIERS}")
    if v.get("confidence") not in ("low", "medium", "high"):
        issues.append("verdict.confidence має бути low, medium або high")
    if v.get("confidence") == "high" and len(inp.files) < min(5, inp.tree_files):
        issues.append("verdict.confidence=high при менш ніж 5 прочитаних файлах")
    if not isinstance(d["unverified"], list):
        issues.append("unverified має бути списком")
    for i, r in enumerate(d["risks"]):
        if not r.get("evidence"):
            issues.append(f"risks[{i}]: немає evidence")
        else:
            _check_cite(str(r["evidence"]), inp, f"risks[{i}]", issues, need=False)
    return issues
