# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/niche_profiles.py"
# purpose: "Niche domain profiles (Shopify themes, coding-agent assets, security/defense) and content-based value scoring from a repository file tree"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Stars measure popularity, not usefulness. A Shopify theme, a coding-agent skill pack or a
defensive rule set usually has 0 stars and can still be exactly what DNK needs. For such
niches the library judges the CONTENT of the repository (its file tree) instead of its fame.

Everything here is pure: given catalog text and a list of file paths it returns facts and a
0..100 value score. No network, no code execution, no file downloads: a tree listing cannot
harm us, and it is enough to tell a real theme from an empty shell.
"""

from __future__ import annotations

import fnmatch
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from pydantic import BaseModel, Field


ANALYSIS_VERSION = 2


class ContentSignals(BaseModel):
    repo_id: str
    fetched_at: str = ""
    status: str = "ok"               # ok | empty | error
    truncated: bool = False          # GitHub cut the tree (huge repo)
    file_count: int = 0
    source_files: int = 0
    niches: List[str] = Field(default_factory=list)
    markers: List[str] = Field(default_factory=list)       # domain markers that are present
    quality: List[str] = Field(default_factory=list)       # README / LICENSE / tests / CI / docs
    risks: List[str] = Field(default_factory=list)         # path-level risk markers
    asset_files: int = 0             # prompt/template/rule data files (a corpus has no source code, and that is fine)
    value: int = 0                   # 0..100
    version: int = 0                 # analysis version: older rows are re-scanned when the rules change


class Niche(BaseModel):
    key: str
    label: str
    catalog_pattern: str
    # marker name -> (weight, glob patterns that prove it, matched against lower-cased paths)
    markers: Dict[str, Any]
    needs: List[str] = Field(default_factory=list)  # markers that must all be present for "real" content


NICHES: List[Niche] = [
    Niche(
        key="shopify_theme",
        label="Shopify-теми та Liquid",
        catalog_pattern=r"shopify|liquid|storefront|polaris|horizon|hydrogen|dawn",
        markers={
            "layout/theme.liquid": (14, ["layout/theme.liquid"]),
            "sections": (14, ["sections/*.liquid"]),
            "templates": (8, ["templates/*.json", "templates/*.liquid"]),
            "settings_schema": (10, ["config/settings_schema.json"]),
            "snippets": (6, ["snippets/*.liquid"]),
            "blocks": (6, ["blocks/*.liquid"]),
            "locales": (3, ["locales/*.json"]),
            "theme_assets": (4, ["assets/*"]),
            "shopify_cli": (3, ["shopify.theme.toml", ".shopifyignore", "shopify.app.toml"]),
        },
        needs=["layout/theme.liquid", "sections"],
    ),
    Niche(
        key="coding_agent",
        label="Кодинг і агентні активи (skills, MCP, промпти, правила)",
        catalog_pattern=r"\bskills?\b|claude code|claude\.md|cursor ?rules|copilot|codex|gemini[- ]cli|mcp server|codegen|vibe[- ]cod|coding agent|code[- ]review|refactor|prompt",
        markers={
            "skill_md": (16, ["skill.md", "*/skill.md", "skills/*/skill.md", ".claude/skills/*/skill.md"]),
            "agent_rules": (12, ["claude.md", "agents.md", ".cursorrules", ".cursor/rules/*", ".github/copilot-instructions.md"]),
            "mcp_config": (12, [".mcp.json", "mcp.json", "mcp_server*", "*mcp*server*", "*mcp-server*"]),
            "agents_dir": (8, [".claude/agents/*", "agents/*", ".claude/commands/*", "commands/*"]),
            "prompts": (8, ["prompts/*", "*.prompt.md", "prompt*.md", "templates/*prompt*"]),
        },
        needs=[],
    ),
    Niche(
        key="security_defense",
        label="Захист, детекція, hardening",
        catalog_pattern=r"defen[cs]e|detection rule|sandbox|harden|sast\b|yara|sigma|semgrep|deobfusc|forensic|waf\b|vuln|threat|firewall|guardrail|injection|malware|secur(?:ity)? (?:scan|rule|audit|policy)",
        markers={
            "rules": (14, ["rules/*", "*.yar", "*.yara", "*.sigma", "sigma/*", ".semgrep/*", "semgrep*/*", "*.rego", "policies/*"]),
            "security_policy": (6, ["security.md", ".github/security.md"]),
            "scanner_config": (8, [".github/workflows/*codeql*", "*.semgrep.yml", ".gitleaks.toml", "trivy*.y*ml", ".snyk"]),
        },
        needs=[],
    ),
    Niche(
        key="media_prompts",
        label="Промпти й шаблони для генерації відео та зображень",
        catalog_pattern=r"\bveo\b|veo[- ]?\d|\bsora\b|runway|kling|midjourney|nano[- ]?banana|seedance|higgsfield|text[- ]to[- ](video|image)|image[- ]to[- ]video|video (gen|prompt)|image (gen|prompt)|stable diffusion|comfyui|prompts? (library|collection|pack|gallery|examples|guide)|cinematic",
        markers={
            "prompt_files": (16, ["prompts/*", "*/prompts/*", "*.prompt", "*.prompt.*", "*prompt*.md", "*prompt*.json",
                                  "*prompt*.txt", "*prompt*.y*ml", "*prompt*.csv"]),
            "templates": (8, ["templates/*", "presets/*", "styles/*"]),
            "examples": (6, ["examples/*", "samples/*", "gallery/*"]),
            "readme_corpus": (16, []),   # set by analyse_tree: a README so large that the prompts live inside it
        },
        needs=[],
    ),
]
_NICHE_BY_KEY = {n.key: n for n in NICHES}

_QUALITY = {
    "README": (8, ["readme*"]),
    "LICENSE": (7, ["license*", "copying*", "unlicense"]),
    "tests": (8, ["tests/*", "test/*", "__tests__/*", "spec/*", "test_*.py", "*_test.go", "*.spec.*", "*.test.*"]),
    "CI": (5, [".github/workflows/*", ".gitlab-ci.yml", ".circleci/*"]),
    "docs": (4, ["docs/*", "doc/*"]),
}
_SOURCE_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".c", ".cpp", ".h",
               ".swift", ".liquid", ".sh", ".lua", ".yar", ".yara", ".rego", ".sql")
_EXEC_EXT = (".exe", ".dll", ".scr", ".bat", ".cmd", ".msi", ".apk", ".com", ".vbs", ".ps1", ".jar")
_ARCHIVE_EXT = (".zip", ".rar", ".7z", ".tar", ".gz")
_SECRET_NAMES = (".env", "id_rsa", "id_ed25519", ".npmrc", ".pypirc", "credentials.json", "secrets.json")
_SECRET_EXT = (".pem", ".p12", ".pfx", ".keystore")
_ASSET_EXT = (".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".prompt", ".toml")
_ASSET_DIRS = ("prompts/", "templates/", "presets/", "styles/", "examples/", "samples/", "gallery/", "skills/", "rules/")
_README_CORPUS_BYTES = 8000
_JUNK_DIRS = ("node_modules/", "vendor/", ".git/", "dist/", "build/", "__pycache__/")


def detect_niches(row: Dict[str, Any], sig: Any = None) -> List[str]:
    """Which niches does the entry belong to. Catalog text is often a generic template ("Specialized research
    solution"), so the real GitHub description and topics (when fetched) are read too."""
    parts = [str(row.get(k) or "") for k in
             ("id", "title", "description", "category", "subcategory", "what_it_gives", "tech_stack")]
    if sig is not None and getattr(sig, "status", "") == "ok":
        parts += [str(getattr(sig, "description", "") or ""), " ".join(getattr(sig, "topics", None) or [])]
    text = " ".join(parts).lower()
    return [n.key for n in NICHES if re.search(n.catalog_pattern, text, re.IGNORECASE)]


def _match(paths: Sequence[str], patterns: Iterable[str]) -> bool:
    for pat in patterns:
        for p in paths:
            if fnmatch.fnmatchcase(p, pat) or fnmatch.fnmatchcase(p.rsplit("/", 1)[-1], pat):
                return True
    return False


def _clean(paths: Iterable[str]) -> List[str]:
    out = []
    for p in paths:
        pl = p.lower().lstrip("/")
        if pl and not any(pl.startswith(j) or f"/{j}" in f"/{pl}" for j in _JUNK_DIRS):
            out.append(pl)
    return out


def analyse_tree(
    repo_id: str,
    niches: Sequence[str],
    paths: Sequence[str],
    truncated: bool = False,
    fetched_at: str = "",
    sizes: Optional[Dict[str, int]] = None,
) -> ContentSignals:
    """Turn a flat file list into content facts and a 0..100 value score."""
    files = _clean(paths)
    sig = ContentSignals(repo_id=repo_id, fetched_at=fetched_at, truncated=truncated,
                         niches=list(niches), file_count=len(files), version=ANALYSIS_VERSION)
    if not files:
        sig.status = "empty"
        return sig
    sig.source_files = sum(1 for f in files if f.endswith(_SOURCE_EXT))

    sig.asset_files = sum(1 for f in files if f.endswith(_ASSET_EXT)
                          and (any(f.startswith(d) or f"/{d}" in f for d in _ASSET_DIRS) or "prompt" in f.rsplit("/", 1)[-1]))
    readme_big = bool(sizes) and any(f.startswith("readme") and (sizes or {}).get(orig, 0) >= _README_CORPUS_BYTES
                                     for f, orig in ((p.lower().lstrip("/"), p) for p in paths))
    corpus_niche = bool({"media_prompts", "coding_agent"} & set(niches))
    # volume of reusable material: source code, or (for corpora) prompt/template/rule files.
    # A prompt library has no source code and is still exactly what we may need.
    value = 0.0
    volume = sig.source_files + (sig.asset_files if corpus_niche else 0)
    for thr, pts in ((1, 8), (5, 15), (15, 20), (40, 25)):
        if volume >= thr:
            value = max(value, pts)
    if readme_big and corpus_niche:
        value = max(value, 15)

    domain_best = 0.0
    for key in niches:
        niche = _NICHE_BY_KEY[key]
        found, pts = [], 0
        for name, (weight, pats) in niche.markers.items():
            if (name == "readme_corpus" and readme_big) or (pats and _match(files, pats)):
                found.append(name)
                pts += weight
        sig.markers += [f"{key}:{m}" for m in found]
        # a theme without its backbone is not a theme, however many assets it has
        if niche.needs and not all(n in found for n in niche.needs):
            pts = min(pts, 12)
        domain_best = max(domain_best, min(pts, 40))
    value += domain_best

    for name, (weight, pats) in _QUALITY.items():
        if _match(files, pats):
            sig.quality.append(name)
            value += weight
    if len({f.split("/")[0] for f in files if "/" in f}) >= 3:
        value += 3

    # risk markers: path-level only, they ask a human to look, they do not convict
    names = [f.rsplit("/", 1)[-1] for f in files]
    if any(f.endswith(_EXEC_EXT) for f in files):
        sig.risks.append("EXECUTABLE_FILES")
    if any(n in _SECRET_NAMES or n.endswith(_SECRET_EXT) for n in names):
        sig.risks.append("COMMITTED_SECRETS")
    if len(files) <= 4 and any(f.endswith(_ARCHIVE_EXT) for f in files):
        sig.risks.append("ARCHIVE_ONLY")
    if sig.source_files == 0 and len(files) <= 3:
        sig.risks.append("NO_SOURCE")

    sig.value = int(max(0, min(100, round(value))))
    return sig
