# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/repo_map.py"
# purpose: "Smart repository scan: classify every path, skip environments/generated/vendored code, index symbols, rank files by import centrality, logic density and task relevance, inventory agent assets"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-08"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Reading the first 12 KB of a few README-adjacent files tells nothing about a 5000-file repository.
The map is built from the WHOLE checkout, offline, nothing is executed:

  1. every path gets a class: logic | agent_asset | test | doc | ui | example | data | infra | vendor | generated
     Environments (venv, node_modules, site-packages), build output, lockfiles, generated code are counted and skipped.
  2. logic and asset files are parsed into symbols (Python via ast, other languages via regex + brace matching)
     with line ranges, signature, first docstring line and cheap logic metrics (branches, arithmetic, algorithm words).
  3. internal imports form a graph; PageRank marks the architectural core.
  4. every file/symbol is scored: task relevance (English terms from task, focus, registry gaps), centrality, logic density.
  5. agent assets (SKILL.md, agents, commands, prompts, MCP tools, rules) are inventoried with their own descriptions.

The agent then receives an outline of the whole repo plus the BODIES of the most relevant symbols, not file heads.
"""

from __future__ import annotations

import ast
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from pydantic import BaseModel, Field

MAX_FILE_BYTES = 400_000
_VENDOR_DIRS = {"node_modules", "venv", ".venv", "env", "site-packages", "vendor", "vendors", "third_party", "third-party", "bower_components",
                ".git", "__pycache__", "dist", "build", "target", "out", ".next", ".nuxt", "coverage", ".tox", ".mypy_cache", ".pytest_cache",
                "pods", ".gradle", ".idea", ".vscode", ".terraform", "bin", "obj", ".cache", "htmlcov"}
_LOCKS = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "cargo.lock", "composer.lock", "gemfile.lock", "uv.lock", "go.sum", "bun.lockb"}
_BINARY = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".zip", ".gz", ".tar", ".mp4", ".mp3",
           ".wav", ".mov", ".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".class", ".jar", ".map", ".parquet", ".onnx", ".pt", ".safetensors")
_GENERATED_NAME = re.compile(r"(_pb2(_grpc)?\.py|\.pb\.go|_grpc\.pb\.go|\.min\.(js|css)|\.generated\.\w+|\.g\.dart|_generated\.\w+|\.d\.ts)$")
_GENERATED_HEAD = re.compile(r"DO NOT EDIT|Code generated|auto-?generated|@generated", re.I)
_SRC = {".py": "python", ".js": "js", ".mjs": "js", ".cjs": "js", ".ts": "js", ".go": "go", ".rs": "rust", ".java": "java", ".kt": "java",
        ".cs": "java", ".rb": "ruby", ".php": "php", ".swift": "java", ".lua": "lua", ".c": "c", ".h": "c", ".cc": "c", ".cpp": "c", ".hpp": "c"}
_UI_EXT = (".css", ".scss", ".less", ".html", ".vue", ".svelte", ".tsx", ".jsx", ".astro")
_UI_DIRS = {"ui", "ui-v2", "frontend", "web", "webapp", "components", "public", "static", "assets", "storybook", ".storybook", "site", "website"}
_TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs", "e2e", "testing", "benchmarks", "benches", "load_testing"}
_DOC_DIRS = {"docs", "doc", "documentation", "docs-site"}
_INFRA_DIRS = {".github", ".circleci", ".gitlab", "helm", "charts", "deploy", "deployment", "k8s", "kubernetes", ".devcontainer", "terraform", "ansible", "scripts", "ci"}
_DATA_DIRS = {"testdata", "fixtures", "fixture", "__snapshots__", "snapshots", "samples", "data", "datasets", "migrations"}
_EXAMPLE_DIRS = {"examples", "example", "demo", "demos", "cookbook", "recipes", "tutorials"}
_ASSET_DIRS = {"skills", "agents", "commands", "prompts", "rules", "policies", "playbooks", "personas"}
_ASSET_FILES = {"skill.md", "agents.md", "claude.md", "gemini.md", ".cursorrules", ".mcp.json", "mcp.json", "server.json", "copilot-instructions.md"}
_ALGO = re.compile(r"heap|semaphore|topolog|backoff|retry|jitter|hash|checksum|lease|lock|queue|graph|dag|schedul|throttle|debounce|window|bucket|"
                   r"interpol|lerp|ease|bezier|matrix|vector|embedding|cosine|tfidf|bm25|rank|score|sort|merge|diff|patch|crdt|vector.?clock|"
                   r"consensus|quorum|shard|partition|cache|evict|ttl|bloom|trie|tree|parse|tokeniz|lex|encode|decode|compress|crypt|sign|verify", re.I)


class Symbol(BaseModel):
    name: str
    kind: str                      # class | function | method
    line: int
    end: int
    sig: str = ""
    doc: str = ""
    branches: int = 0
    arith: int = 0
    algo: int = 0
    score: float = 0.0


class FileInfo(BaseModel):
    path: str
    cls: str
    lang: str = ""
    loc: int = 0
    size: int = 0
    doc: str = ""
    symbols: List[Symbol] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)       # resolved internal file paths
    rank: float = 0.0              # PageRank, 0..1 after normalisation
    density: float = 0.0           # logic density 0..1
    relevance: float = 0.0         # task relevance 0..1
    score: float = 0.0


class Asset(BaseModel):
    kind: str                      # skill | agent | command | prompt | rules | mcp_tool | instructions | mcp_config
    path: str
    name: str = ""
    description: str = ""
    tools: List[str] = Field(default_factory=list)


class RepoMap(BaseModel):
    root: str = ""
    files: Dict[str, FileInfo] = Field(default_factory=dict)
    counts: Dict[str, int] = Field(default_factory=dict)             # per class
    skipped_examples: Dict[str, List[str]] = Field(default_factory=dict)
    assets: List[Asset] = Field(default_factory=list)
    query_terms: List[str] = Field(default_factory=list)
    logic_loc: int = 0


# ------------------------------------------------------------------------------------------------ classification
def classify(path: str, head: str = "") -> str:
    pl = path.lower()
    parts = pl.split("/")
    base, dirs = parts[-1], set(parts[:-1])
    stem, ext = os.path.splitext(base)
    if dirs & _VENDOR_DIRS or base in _LOCKS or pl.endswith(_BINARY):
        return "vendor"
    if _GENERATED_NAME.search(base) or (head and _GENERATED_HEAD.search(head[:400])):
        return "generated"
    if base in _ASSET_FILES or base.endswith((".prompt.md", ".prompt.yaml", ".prompt.yml")) or ".cursor/rules/" in pl or ".claude/" in pl:
        return "agent_asset"
    if dirs & _ASSET_DIRS and ext in (".md", ".yaml", ".yml", ".json", ".txt", ".yar", ".yara", ".rego", ".toml", ".mdc", ".prompt"):
        return "agent_asset"
    if dirs & _DATA_DIRS:
        return "data"
    if dirs & _TEST_DIRS or re.match(r"test_.*\.py$|.*_test\.(go|py|rs)$|.*\.(test|spec)\.[jt]sx?$", base):
        return "test"
    if dirs & _DOC_DIRS or ext in (".md", ".rst", ".mdx", ".txt", ".ipynb", ".adoc") or base.startswith(("changelog", "license", "contributing", "readme")):
        return "doc"
    if dirs & _EXAMPLE_DIRS:
        return "example"
    if dirs & _INFRA_DIRS or base in ("dockerfile", "makefile", "justfile", ".gitignore", ".dockerignore", ".editorconfig") or base.startswith(("docker-compose", ".env", ".pre-commit")):
        return "infra"
    if ext in _UI_EXT or dirs & _UI_DIRS:
        return "ui" if ext in _UI_EXT or ext in (".ts", ".js") else "ui"
    if ext in _SRC:
        return "logic"
    if ext in (".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".xml", ".csv", ".tsv", ".lock"):
        return "data"
    return "other"


def _mark_venvs(rel_paths: Sequence[str]) -> Set[str]:
    """Any directory containing pyvenv.cfg is a virtual environment, whatever it is called."""
    return {p.rsplit("/", 1)[0] + "/" for p in rel_paths if p.lower().endswith("pyvenv.cfg") and "/" in p} | (
        {""} if any(p.lower() == "pyvenv.cfg" for p in rel_paths) else set())


# ------------------------------------------------------------------------------------------------ parsing
def _py_symbols(text: str) -> Tuple[List[Symbol], str, List[str]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError):
        return [], "", []
    mod_doc = (ast.get_docstring(tree) or "").split("\n")[0][:140]
    imps: List[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imps += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            base = ("." * n.level) + (n.module or "")
            imps.append(base)
            imps += [(base + "." + a.name) if not base.endswith(".") else base + a.name for a in n.names if a.name != "*"]   # may be a submodule
    syms: List[Symbol] = []

    def metrics(node: ast.AST) -> Tuple[int, int, int]:
        br = ar = al = 0
        for x in ast.walk(node):
            if isinstance(x, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.BoolOp, ast.IfExp, ast.comprehension, ast.With, ast.Assert)):
                br += 1
            elif isinstance(x, ast.BinOp) and isinstance(x.op, (ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)):
                ar += 1
            elif isinstance(x, ast.Name) and _ALGO.search(x.id):
                al += 1
            elif isinstance(x, ast.Attribute) and _ALGO.search(x.attr):
                al += 1
        return br, ar, al

    def visit(body: Sequence[ast.stmt], owner: str = "") -> None:
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(n, ast.ClassDef) else ("method" if owner else "function")
                name = f"{owner}.{n.name}" if owner else n.name
                args = ""
                if not isinstance(n, ast.ClassDef):
                    a = n.args
                    names = [x.arg for x in a.posonlyargs + a.args] + (["*" + a.vararg.arg] if a.vararg else []) + [x.arg for x in a.kwonlyargs] + (["**" + a.kwarg.arg] if a.kwarg else [])
                    args = "(" + ", ".join(names[:7]) + (", …" if len(names) > 7 else "") + ")"
                br, ar, al = metrics(n)
                syms.append(Symbol(name=name, kind=kind, line=n.lineno, end=getattr(n, "end_lineno", n.lineno) or n.lineno,
                                   sig=("async " if isinstance(n, ast.AsyncFunctionDef) else "") + n.name + args,
                                   doc=(ast.get_docstring(n) or "").split("\n")[0][:140], branches=br, arith=ar, algo=al))
                if isinstance(n, ast.ClassDef):
                    visit(n.body, n.name)

    visit(tree.body)
    return syms, mod_doc, imps


_RX = {
    "js": [(re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\("), "function"),
           (re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)"), "class"),
           (re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?\([^)]*\)\s*(?::[^=]+)?=>"), "function")],
    "go": [(re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*[\[(]"), "function"), (re.compile(r"^type\s+([A-Za-z_]\w*)\s+(?:struct|interface)"), "class")],
    "rust": [(re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)"), "function"),
             (re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:struct|enum|trait)\s+([A-Za-z_]\w*)"), "class")],
    "java": [(re.compile(r"^\s*(?:public|private|protected|internal|abstract|final|static|sealed|open|data|\s)*(?:class|interface|enum|object|record)\s+([A-Za-z_]\w*)"), "class"),
             (re.compile(r"^\s*(?:public|private|protected|internal|static|final|override|suspend|\s)+[\w<>\[\],.? ]+\s+([a-z]\w*)\s*\([^;{)]*\)?\s*(?:throws [\w, .]+)?\s*\{?\s*$"), "method")],
    "ruby": [(re.compile(r"^\s*def\s+(?:self\.)?([A-Za-z_]\w*[?!]?)"), "function"), (re.compile(r"^\s*(?:class|module)\s+([A-Z]\w*)"), "class")],
    "php": [(re.compile(r"^\s*(?:public|private|protected|static|\s)*function\s+([A-Za-z_]\w*)"), "function"), (re.compile(r"^\s*(?:abstract\s+)?class\s+([A-Za-z_]\w*)"), "class")],
    "lua": [(re.compile(r"^\s*(?:local\s+)?function\s+([\w.:]+)"), "function")],
    "c": [(re.compile(r"^[A-Za-z_][\w\s\*]+?\s+\**([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$"), "function"), (re.compile(r"^\s*(?:class|struct)\s+([A-Za-z_]\w*)"), "class")],
}
_KW_NOT_FUNC = {"if", "for", "while", "switch", "return", "catch", "else", "sizeof", "do"}


def _brace_end(lines: List[str], start: int) -> int:
    depth, seen = 0, False
    for i in range(start - 1, min(len(lines), start + 600)):
        for ch in re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", "", lines[i]):
            if ch == "{":
                depth += 1
                seen = True
            elif ch == "}":
                depth -= 1
        if seen and depth <= 0:
            return i + 1
    return min(len(lines), start + 40)


def _generic_symbols(text: str, lang: str) -> Tuple[List[Symbol], str, List[str]]:
    lines = text.split("\n")
    rxs = _RX.get(lang, [])
    syms: List[Symbol] = []
    for i, ln in enumerate(lines, 1):
        if len(ln) > 220:
            continue
        for rx, kind in rxs:
            m = rx.match(ln)
            if m and m.group(1) not in _KW_NOT_FUNC:
                end = _brace_end(lines, i) if lang != "ruby" and lang != "lua" else min(len(lines), i + 30)
                body = "\n".join(lines[i - 1:end])
                doc = ""
                for j in range(i - 2, max(-1, i - 5), -1):               # a comment directly above
                    c = lines[j].strip()
                    if c.startswith(("//", "///", "#", "*", "/**")):
                        doc = c.lstrip("/#* ").strip()[:140]
                    else:
                        break
                syms.append(Symbol(name=m.group(1), kind=kind, line=i, end=end, sig=ln.strip()[:100], doc=doc,
                                   branches=len(re.findall(r"\b(if|for|while|switch|match|case|catch|&&|\|\|)\b|&&|\|\|", body)),
                                   arith=len(re.findall(r"[^/*+\-=<>!]\s[*/%]\s|<<|>>|\*\*", body)), algo=len(_ALGO.findall(body))))
                break
    imps = re.findall(r"""(?:from\s+|require\(\s*|import\s+(?:[\w*{}\s,]+\s+from\s+)?)['"]([^'"]+)['"]""", text) if lang == "js" else \
        re.findall(r'^\s*"([\w./\-]+)"\s*$|^import\s+"([\w./\-]+)"', text, re.M) if lang == "go" else []
    imps = [x if isinstance(x, str) else (x[0] or x[1]) for x in imps]
    return syms, "", imps


def _resolve_imports(path: str, lang: str, imps: Sequence[str], all_py: Dict[str, str], by_dir: Dict[str, List[str]], all_paths: Set[str]) -> List[str]:
    out: List[str] = []
    base = path.rsplit("/", 1)[0] if "/" in path else ""
    for imp in imps:
        if lang == "python":
            if imp.startswith("."):
                lvl = len(imp) - len(imp.lstrip("."))
                parent = "/".join(base.split("/")[:len(base.split("/")) - (lvl - 1)] if base else [])
                mod = imp.lstrip(".").replace(".", "/")
                cand = [f"{parent}/{mod}".strip("/")]
            else:
                cand = [imp.replace(".", "/")]
            for c in cand:
                for hit in (f"{c}.py", f"{c}/__init__.py"):
                    for k in all_py.get(hit, []) if hit in all_py else ([hit] if hit in all_paths else []):
                        out.append(k)
                if not any(h in all_paths for h in (f"{c}.py", f"{c}/__init__.py")):
                    for pref in ("src/", "lib/", ""):
                        for hit in (f"{pref}{c}.py", f"{pref}{c}/__init__.py"):
                            if hit in all_paths:
                                out.append(hit)
        elif lang == "js" and imp.startswith("."):
            c = os.path.normpath(os.path.join(base, imp)).replace("\\", "/")
            for ext in ("", ".ts", ".js", ".mjs", "/index.ts", "/index.js", ".tsx"):
                if c + ext in all_paths:
                    out.append(c + ext)
                    break
        elif lang == "go":
            d = imp.split("/")
            for n in range(min(4, len(d)), 0, -1):
                tail = "/".join(d[-n:])
                if tail in by_dir:
                    out += by_dir[tail][:20]
                    break
    return list(dict.fromkeys(out))


def _pagerank(nodes: Sequence[str], edges: Dict[str, List[str]], iters: int = 30, d: float = 0.85) -> Dict[str, float]:
    n = len(nodes)
    if not n:
        return {}
    pr = {k: 1.0 / n for k in nodes}
    out_deg = {k: len(edges.get(k, [])) for k in nodes}
    for _ in range(iters):
        new = {k: (1 - d) / n for k in nodes}
        dangling = sum(pr[k] for k in nodes if out_deg[k] == 0)
        for k in nodes:
            for t in edges.get(k, []):
                if t in new:
                    new[t] += d * pr[k] / out_deg[k]
            new[k] += d * dangling / n
        pr = new
    mx = max(pr.values()) or 1.0
    return {k: v / mx for k, v in pr.items()}


# ------------------------------------------------------------------------------------------------ assets
def _front(text: str) -> Dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out: Dict[str, str] = {}
    if m:
        for ln in m.group(1).split("\n"):
            k, _, v = ln.partition(":")
            if v.strip() and not ln.startswith(" "):
                out[k.strip().lower()] = v.strip().strip("\"'")[:300]
    return out


def inventory_assets(root: Path, files: Dict[str, FileInfo]) -> List[Asset]:
    out: List[Asset] = []
    for p, fi in files.items():
        full = root / p
        try:
            text = full.read_text(encoding="utf-8", errors="replace")[:20000] if full.stat().st_size < MAX_FILE_BYTES else ""
        except OSError:
            continue
        base = p.lower().rsplit("/", 1)[-1]
        if fi.cls == "agent_asset":
            fm = _front(text)
            first = next((l.strip("# ").strip() for l in text.split("\n") if l.strip() and not l.startswith("---")), "")
            if base == "skill.md":
                kind = "skill"
            elif base in ("agents.md", "claude.md", "gemini.md", ".cursorrules", "copilot-instructions.md") or ".cursor/rules/" in p.lower():
                kind = "instructions"
            elif base in (".mcp.json", "mcp.json", "server.json"):
                kind = "mcp_config"
            elif "/agents/" in "/" + p.lower():
                kind = "agent"
            elif "/commands/" in "/" + p.lower():
                kind = "command"
            elif "/prompts/" in "/" + p.lower() or ".prompt." in base:
                kind = "prompt"
            else:
                kind = "rules"
            tools = [t.strip() for t in re.split(r"[,\[\]]", fm.get("tools", fm.get("allowed-tools", ""))) if t.strip()][:10]
            out.append(Asset(kind=kind, path=p, name=fm.get("name", base), description=(fm.get("description") or first)[:240], tools=tools))
        elif fi.lang == "python" and re.search(r"@(?:\w+\.)?(?:tool|mcp\.tool|server\.tool)\b|FastMCP\(", text):
            for s in fi.symbols:
                if s.kind == "function" and re.search(r"@(?:\w+\.)?tool", "\n".join(text.split("\n")[max(0, s.line - 4):s.line])):
                    out.append(Asset(kind="mcp_tool", path=p, name=s.name, description=s.doc or s.sig))
        elif fi.lang == "js" and re.search(r"server\.tool\(|\.registerTool\(|setRequestHandler\(\s*ListToolsRequestSchema", text):
            for m in re.finditer(r"""(?:server\.tool|registerTool)\(\s*['"]([\w\-.]+)['"]""", text):
                out.append(Asset(kind="mcp_tool", path=p, name=m.group(1), description="MCP-інструмент (TypeScript)"))
    return out[:200]


# ------------------------------------------------------------------------------------------------ scan
def walk(root: Path) -> List[Tuple[str, int]]:
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            fp = os.path.join(dp, f)
            try:
                out.append((os.path.relpath(fp, root).replace("\\", "/"), os.path.getsize(fp)))
            except OSError:
                pass
    return out


def clone(name: str, dest: Path, token: Optional[str] = None, timeout: int = 240) -> Path:
    """Shallow clone of the default branch. The token goes in a header, never in the URL or on disk."""
    import base64
    import shutil
    import subprocess
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git"]
    if token:
        cmd += ["-c", "http.extraheader=Authorization: Basic " + base64.b64encode(f"x-access-token:{token}".encode()).decode()]
    cmd += ["clone", "--depth", "1", "--quiet", "--no-tags", f"https://github.com/{name}.git", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("git clone failed: " + (r.stderr or "")[-300:].replace(token or "\0", "***"))
    return dest


def query_terms(task: str = "", focus: Sequence[str] = (), extra: Sequence[str] = ()) -> List[str]:
    """English search words: focus + English words of the task + terms the registry/domain tables attach to it."""
    from services.dnk_git_research.src.domain_terms import match_domains
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z_]{2,}", task or "")]
    for d in match_domains(task or ""):
        words += [t.lower() for t in d.terms]
    words += [f.lower() for f in focus] + [e.lower() for e in extra]
    stop = {"the", "and", "for", "with", "from", "dnk", "node", "tasks", "task"}
    return list(dict.fromkeys(w for w in words if w not in stop and len(w) > 2))


def _tok(s: str) -> Set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1_\2", s).lower()) if len(t) > 2}


def scan(root: Path, terms: Sequence[str] = (), ui_task: bool = False, max_files: int = 20000) -> RepoMap:
    root = Path(root)
    rels: List[str] = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            rels.append(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/"))
            if len(rels) >= max_files:
                break
    venvs = _mark_venvs(rels)
    rm = RepoMap(root=str(root), query_terms=list(terms))
    files: Dict[str, FileInfo] = {}
    skipped: Dict[str, List[str]] = defaultdict(list)
    counts: Dict[str, int] = defaultdict(int)
    all_paths = set(rels)
    for p in rels:
        full = root / p
        try:
            size = full.stat().st_size
        except OSError:
            continue
        in_venv = any(p.startswith(v) for v in venvs) if venvs else False
        head = ""
        ext = os.path.splitext(p)[1].lower()
        if not in_venv and ext in _SRC and size < MAX_FILE_BYTES:
            try:
                head = full.open("r", encoding="utf-8", errors="replace").read(400)
            except OSError:
                pass
        cls = "vendor" if in_venv else classify(p, head)
        if size > MAX_FILE_BYTES and cls in ("logic", "agent_asset"):
            cls = "generated"
        counts[cls] += 1
        if cls in ("vendor", "generated", "data", "infra", "other") or (cls == "ui" and not ui_task) or cls == "doc" and not p.lower().endswith("readme.md"):
            if len(skipped[cls]) < 5:
                skipped[cls].append(p)
            if cls != "doc":
                continue
        files[p] = FileInfo(path=p, cls=cls, lang=_SRC.get(ext, ""), size=size)
    rm.counts, rm.skipped_examples = dict(counts), dict(skipped)

    py_index = {p: [p] for p in files if p.endswith(".py")}
    by_dir: Dict[str, List[str]] = defaultdict(list)
    for p, fi in files.items():
        if fi.lang == "go":
            by_dir["/".join(p.split("/")[:-1][-3:])].append(p)
            by_dir[p.split("/")[-2] if "/" in p else ""].append(p)
    raw_imports: Dict[str, List[str]] = {}
    for p, fi in files.items():
        if fi.cls not in ("logic", "agent_asset", "test", "example", "ui") or not fi.lang:
            if fi.cls in ("logic", "agent_asset", "test", "example", "ui") and fi.lang == "":
                pass
            continue
        try:
            text = (root / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fi.loc = text.count("\n") + 1
        syms, mdoc, imps = _py_symbols(text) if fi.lang == "python" else _generic_symbols(text, fi.lang)
        fi.symbols, fi.doc, raw_imports[p] = syms, mdoc, imps
    for p, imps in raw_imports.items():
        files[p].imports = [x for x in _resolve_imports(p, files[p].lang, imps, py_index, by_dir, all_paths) if x != p and x in files]

    logic = [p for p, fi in files.items() if fi.cls == "logic"]
    rm.logic_loc = sum(files[p].loc for p in logic)
    pr = _pagerank(logic, {p: [x for x in files[p].imports if files[p_x := x].cls == "logic"] for p in logic}) if logic else {}
    tset = {t for term in terms for t in _tok(term)}
    for p, fi in files.items():
        fi.rank = pr.get(p, 0.0)
        if fi.symbols:
            tot = sum(s.branches + 2 * s.arith + 3 * s.algo for s in fi.symbols)
            fi.density = min(1.0, tot / max(10.0, fi.loc / 4.0) / 3.0)
        ptoks = _tok(p)
        for s in fi.symbols:
            st = _tok(s.name) | _tok(s.sig)
            dt = _tok(s.doc)
            s.score = (3.0 * len(tset & st) + 1.5 * len(tset & dt) + 0.5 * len(tset & ptoks)) / max(1.0, len(tset)) if tset else 0.0
            s.score = min(1.0, s.score + 0.02 * min(5, s.branches + s.algo))
        best = max((s.score for s in fi.symbols), default=0.0)
        fi.relevance = min(1.0, (2.5 * len(tset & ptoks) + 3 * best * len(tset)) / max(1.0, 3.0 * len(tset))) if tset else 0.0
    cls_w = {"logic": 1.0, "agent_asset": 1.15, "test": 0.3, "example": 0.35, "ui": 1.0 if ui_task else 0.1, "doc": 0.1}
    for fi in files.values():
        base = 0.45 * fi.relevance + 0.25 * fi.rank * min(1.0, 2 * fi.relevance) + 0.25 * fi.density + (0.05 if fi.loc >= 40 else 0.0)
        if fi.cls == "agent_asset":
            base = max(base, 0.35 + 0.4 * fi.relevance)
        sat = 0.6 if re.search(r"(^|/)(integrations|plugins|contrib|extensions|adapters)/", fi.path) else 1.0   # the core outranks its satellites
        fi.score = round(base * cls_w.get(fi.cls, 0.1) * sat, 4)
    rm.files = files
    rm.assets = inventory_assets(root, files)
    return rm


# ------------------------------------------------------------------------------------------------ views for the agent
def top_files(rm: RepoMap, n: int = 25, classes: Sequence[str] = ("logic", "agent_asset")) -> List[FileInfo]:
    return sorted((f for f in rm.files.values() if f.cls in classes), key=lambda f: -f.score)[:n]


def outline(rm: RepoMap, n_files: int = 25, per_file: int = 8) -> str:
    """Aider-style map: the whole architecture in a few hundred lines, not file heads."""
    L = []
    for f in top_files(rm, n_files):
        syms = sorted(f.symbols, key=lambda s: -(s.score + 0.001 * (s.end - s.line)))[:per_file]
        L.append(f"{f.path}  [{f.cls}, {f.loc} рядків, ядро {f.rank:.2f}, логіка {f.density:.2f}, релевантність {f.relevance:.2f}]" + (f"  — {f.doc}" if f.doc else ""))
        for s in sorted(syms, key=lambda s: s.line):
            L.append(f"  L{s.line}-{s.end} {s.kind} {s.sig}" + (f" — {s.doc}" if s.doc else ""))
    return "\n".join(L)


def tests_outline(rm: RepoMap, for_files: Sequence[str], n: int = 12) -> List[str]:
    """Names of tests next to the chosen files: they are a free specification of behaviour and edge cases."""
    stems = {os.path.splitext(p.rsplit("/", 1)[-1])[0].lower().replace("test_", "").replace("_test", "") for p in for_files}
    out = []
    for f in rm.files.values():
        if f.cls != "test":
            continue
        fstem = os.path.splitext(f.path.rsplit("/", 1)[-1])[0].lower().replace("test_", "").replace("_test", "").replace(".test", "").replace(".spec", "")
        if fstem in stems:
            names = [s.name for s in f.symbols if s.kind in ("function", "method") and s.name.split(".")[-1].startswith(("test", "Test", "it", "should"))][:8]
            if names:
                out.append(f"{f.path}: " + "; ".join(names))
    return out[:n]


def pick_ranges(rm: RepoMap, budget_chars: int = 40000, max_symbol_lines: int = 90, min_score: float = 0.0) -> Dict[str, List[Tuple[int, int]]]:
    """Choose the BODIES to show: best symbols of best files, greedy by value per size, until the budget is spent."""
    cands = []
    for f in top_files(rm, 30):
        for s in f.symbols:
            span = s.end - s.line + 1
            if span < 4 or (kind_is_class := s.kind == "class") and span > max_symbol_lines:
                continue                      # a huge class is represented by its methods, a stub by nothing
            value = f.score * (0.4 + s.score) * (1 + 0.15 * min(6, s.branches + s.algo))
            if value <= min_score:
                continue
            cands.append((value / (min(span, max_symbol_lines) ** 0.3), f.path, s.line, min(s.end, s.line + max_symbol_lines - 1), s.kind))
    cands.sort(reverse=True)
    chosen: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    spent = 0
    for _, p, a, b, kind in cands:
        cost = (b - a + 1) * 60
        if spent + cost > budget_chars:
            continue
        if any(not (b < x or a > y) for x, y in chosen[p]) and kind != "method":
            continue
        chosen[p].append((a, b))
        spent += cost
        if spent >= budget_chars * 0.97:
            break
    return {p: sorted(set(r)) for p, r in chosen.items()}


def assets_block(rm: RepoMap, limit: int = 40) -> str:
    return "\n".join(f"- [{a.kind}] `{a.path}` {a.name}: {a.description}" + (f" (інструменти: {', '.join(a.tools)})" if a.tools else "") for a in rm.assets[:limit])
