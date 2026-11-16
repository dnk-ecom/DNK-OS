# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/ledger.py"
# purpose: "Assimilation ledger: runtime environments, DNK modules, donors (repo/site/doc/video) and per-mechanic provenance, so the researcher knows what DNK OS already has, what it lacks and what a new find can fill"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
The ledger answers three questions for an agent that has just found something on the web:
  1. What do we already have, and where did it come from?     (donors -> assimilations -> modules)
  2. What is missing in DNK OS right now?                     (gaps per module)
  3. Where will it run, under which constraints?              (environments)

Truth levels, so that old claims are not mistaken for verified facts:
  indexed   - read automatically from existing records (core/skills/*_assimilated, docs/notes/sota_audits).
              These are somebody's CLAIMS; nothing says the code exists.
  verified  - a hand-kept YAML record with a pinned donor commit, a citation into the donor and a
              DNK path that exists on disk.

Curated records live in YAML next to the service (git-reviewable). Modules are never typed by hand:
they are read from services/*/service_manifest.yaml.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml
from pydantic import BaseModel, Field

from services.dnk_git_research.src.license_policy import classify_license

HUB_ROOT = Path(__file__).resolve().parents[3]
LEDGER_ENV = "DNK_LEDGER_DIR"

METHODS = ("adopt", "adapt", "clean_room", "idea", "reference")
STATUSES = ("candidate", "planned", "in_progress", "done", "rejected")
DONOR_KINDS = ("repo", "org", "site", "doc", "video", "prompt_corpus")
_CITE = re.compile(r"^[0-9a-f]{7,40}:[^:\s]+:L\d+(-L\d+)?$")
_COPY_METHODS = ("adopt", "adapt")

_STOP = set("the a an and or of to in for on with from by is are be as at it its this that into use using via per "
            "та і й або для з із до на по від як що це цей ця які який коли якщо не при про без над під між".split())


def default_ledger_dir() -> Path:
    env = os.environ.get(LEDGER_ENV)
    return Path(env) if env else Path(__file__).resolve().parents[1] / "ledger"


class Environment(BaseModel):
    id: str
    kind: str = "runtime"            # runtime | host | platform | ci
    name: str = ""
    stack: Dict[str, str] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    verify: str = ""                 # how to prove the environment is what we say


class Module(BaseModel):
    id: str
    path: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class Gap(BaseModel):
    id: str
    module: str
    need: str
    terms: List[str] = Field(default_factory=list)
    priority: int = 2                # 1 high .. 3 low
    status: str = "open"             # open | filled | dropped


class Assimilation(BaseModel):
    id: str
    module: str = ""
    what: str = ""                   # the mechanic that was taken, one line
    method: str = "reference"
    status: str = "candidate"
    gap: str = ""
    donor_cite: str = ""             # sha:path:Lstart-Lend inside the donor
    dnk_path: str = ""               # where it lives in DNK_HUB
    env: List[str] = Field(default_factory=list)
    verified: str = ""               # how it was proven to work (test, command)
    date: str = ""
    notes: str = ""


class Donor(BaseModel):
    id: str                          # owner/repo, or a slug for non-repo sources
    kind: str = "repo"
    url: str = ""
    title: str = ""
    pinned: str = ""                 # commit sha (repo) or access date (site/doc/video)
    license: str = "unknown"
    track: str = ""
    dossier: str = ""
    level: str = "verified"          # indexed | verified
    source: str = "manual"           # auto | manual
    worker: str = ""
    target_hint: str = ""
    summary: str = ""
    assimilations: List[Assimilation] = Field(default_factory=list)


class Ledger(BaseModel):
    environments: List[Environment] = Field(default_factory=list)
    modules: List[Module] = Field(default_factory=list)
    gaps: List[Gap] = Field(default_factory=list)
    donors: List[Donor] = Field(default_factory=list)


# --------------------------------------------------------------------------- loading

def _yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def discover_modules(hub_root: Path = HUB_ROOT) -> List[Module]:
    out = []
    for f in sorted((hub_root / "services").glob("*/service_manifest.yaml")):
        d = _yaml(f)
        if not isinstance(d, dict):
            continue
        meta, spec = d.get("metadata") or {}, d.get("spec") or {}
        sid = meta.get("service_id") or f.parent.name
        tools = [t.get("name", "") for t in spec.get("fastmcp_tools") or [] if isinstance(t, dict)]
        out.append(Module(id=sid, path=f"services/{f.parent.name}", description=str(meta.get("description") or "").replace("\n", " "),
                          tags=[str(t) for t in meta.get("tags") or []], tools=[t for t in tools if t]))
    return out


_FM = re.compile(r"^---\n(.*?)\n---", re.S)
_REPO_LINE = re.compile(r"\*\*Repository\*\*:\s*`?([\w.\-]+/[\w.\-]+)`?")
_TARGET_LINE = re.compile(r"\*\*Target Component Target\*\*:\s*`([^`]+)`")
_PURPOSE_LINE = re.compile(r"\*\*High-Level Purpose\*\*:\s*(.+)")
_SPDX_LIKE = re.compile(r"^[A-Za-z0-9.\-+ ()]+$")


def index_existing(hub_root: Path = HUB_ROOT) -> List[Donor]:
    """Donors already claimed by core/skills/*_assimilated and docs/notes/sota_audits. Level = indexed."""
    donors: Dict[str, Donor] = {}
    for f in sorted((hub_root / "core" / "skills").glob("*_assimilated/SKILL.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _FM.match(text)
        fm = yaml.safe_load(m.group(1)) if m else {}
        fm = fm if isinstance(fm, dict) else {}
        r = _REPO_LINE.search(text)
        if not r:
            continue
        rid = r.group(1).lower()
        tgt, pur = _TARGET_LINE.search(text), _PURPOSE_LINE.search(text)
        donors[rid] = Donor(
            id=rid, url=f"https://github.com/{r.group(1)}", title=r.group(1), license=str(fm.get("license") or "unknown"),
            track=str(fm.get("track") or ""), level="indexed", source="auto", worker=str(fm.get("target_worker") or ""),
            target_hint=tgt.group(1) if tgt else "", summary=(pur.group(1).strip() if pur else str(fm.get("description") or ""))[:240],
            pinned=str(fm.get("assimilated_at") or ""), dossier=str(f.relative_to(hub_root)))
    for f in sorted((hub_root / "docs" / "notes").glob("**/*sota*assimilation_audit*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        r = re.search(r"SOTA Assimilation:\s*([\w.\-]+/[\w.\-]+)", text)
        if not r:
            continue
        rid = r.group(1).lower()
        lic = re.search(r"\*\*License\*\*:\s*`([^`]+)`", text)
        dest = re.search(r"\*\*Component Destination\*\*:\s*`([^`]+)`", text)
        d = donors.get(rid) or Donor(id=rid, url=f"https://github.com/{r.group(1)}", title=r.group(1), level="indexed", source="auto")
        if not d.license or d.license == "unknown":
            d.license = lic.group(1) if lic else d.license
        d.target_hint = d.target_hint or (dest.group(1) if dest else "")
        d.dossier = d.dossier or str(f.relative_to(hub_root))
        donors[rid] = d
    return list(donors.values())


def load_ledger(ledger_dir: Optional[Path] = None, hub_root: Path = HUB_ROOT, with_index: bool = True) -> Ledger:
    base = Path(ledger_dir) if ledger_dir else default_ledger_dir()
    led = Ledger(modules=discover_modules(hub_root))
    for key, model, bucket in (("environments", Environment, led.environments), ("gaps", Gap, led.gaps)):
        d = _yaml(base / f"{key}.yaml")
        for item in (d or {}).get(key, []) if isinstance(d, dict) else []:
            bucket.append(model.model_validate(item))
    manual: Dict[str, Donor] = {}
    for f in sorted((base / "donors").glob("*.yaml")) if (base / "donors").is_dir() else []:
        d = _yaml(f)
        if isinstance(d, dict):
            dn = Donor.model_validate(d)
            manual[dn.id.lower()] = dn
    donors = dict(manual)
    if with_index:
        for dn in index_existing(hub_root):
            if dn.id.lower() in donors:      # curated record wins, keep the old skill as pointer
                donors[dn.id.lower()].dossier = donors[dn.id.lower()].dossier or dn.dossier
            else:
                donors[dn.id.lower()] = dn
    led.donors = list(donors.values())
    return led


# --------------------------------------------------------------------------- validation

def check_ledger(led: Ledger, hub_root: Path = HUB_ROOT) -> List[str]:
    """Problems in curated records. Indexed donors are not errors, they are claims."""
    issues: List[str] = []
    mod_ids = {m.id for m in led.modules}
    env_ids = {e.id for e in led.environments}
    gap_ids = {g.id for g in led.gaps}

    def dup(kind: str, ids: Iterable[str]) -> None:
        seen = set()
        for i in ids:
            if i in seen:
                issues.append(f"{kind} «{i}» повторюється")
            seen.add(i)

    dup("середовище", (e.id for e in led.environments))
    dup("прогалина", (g.id for g in led.gaps))
    dup("донор", (d.id.lower() for d in led.donors))
    all_as = [a for d in led.donors if d.source == "manual" for a in d.assimilations]
    dup("асиміляція", (a.id for a in all_as))

    def module_ok(mid: str) -> bool:
        return mid in mod_ids or (bool(mid) and (hub_root / mid).exists())

    for g in led.gaps:
        if not module_ok(g.module):
            issues.append(f"gap {g.id}: невідомий модуль «{g.module}»")
        if not g.terms:
            issues.append(f"gap {g.id}: без terms його неможливо знайти під час сканування")
        if g.priority not in (1, 2, 3):
            issues.append(f"gap {g.id}: priority має бути 1..3")
    for d in led.donors:
        if d.source != "manual":
            continue
        if d.kind not in DONOR_KINDS:
            issues.append(f"донор {d.id}: невідомий kind «{d.kind}»")
        if d.kind == "repo" and not re.fullmatch(r"[0-9a-f]{7,40}", d.pinned or ""):
            issues.append(f"донор {d.id}: для репозиторію потрібен pinned = sha коміту")
        v = classify_license(d.license)
        for a in d.assimilations:
            p = f"{d.id}/{a.id}"
            if a.method not in METHODS:
                issues.append(f"{p}: невідомий method «{a.method}»")
            if a.status not in STATUSES:
                issues.append(f"{p}: невідомий status «{a.status}»")
            if a.module and not module_ok(a.module):
                issues.append(f"{p}: невідомий модуль «{a.module}»")
            if a.gap and a.gap not in gap_ids:
                issues.append(f"{p}: невідомий gap «{a.gap}»")
            for e in a.env:
                if e not in env_ids:
                    issues.append(f"{p}: невідоме середовище «{e}»")
            if a.method in _COPY_METHODS and not v.can_copy_code:
                issues.append(f"{p}: ліцензія «{d.license}» ({v.license_class.value}) не дозволяє {a.method}; потрібен clean_room, idea або reference")
            if a.donor_cite and not _CITE.match(a.donor_cite):
                issues.append(f"{p}: donor_cite має формат sha:шлях:Lпочаток-Lкінець")
            if a.status == "done":
                if not a.dnk_path or not (hub_root / a.dnk_path).exists():
                    issues.append(f"{p}: done, але dnk_path «{a.dnk_path}» не існує")
                if not a.verified:
                    issues.append(f"{p}: done без поля verified (чим доведено, що працює)")
                if d.kind == "repo" and not a.donor_cite:
                    issues.append(f"{p}: done без donor_cite, невідомо, що саме взято")
    return issues


# --------------------------------------------------------------------------- matching

def _tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-zа-яіїєґ0-9][a-zа-яіїєґ0-9_\-]{2,}", (text or "").lower()) if w not in _STOP}


def _same(x: str, y: str) -> bool:
    """Equal, one inside the other, or the same stem (inflected Ukrainian: залежних / залежностей)."""
    if x == y or (len(x) > 4 and (x in y or y in x)):
        return True
    n = 0
    for cx, cy in zip(x, y):
        if cx != cy:
            break
        n += 1
    return n >= 5


def _overlap(a: set, b: set) -> int:
    return len({x for x in a if any(_same(x, y) for y in b)})


class FitItem(BaseModel):
    text: str
    verdict: str                      # FILLS_GAP | ALREADY_HAVE | ADJACENT | NO_MATCH
    gap: str = ""
    module: str = ""
    have_from: str = ""
    note: str = ""


class FitReport(BaseModel):
    items: List[FitItem] = Field(default_factory=list)
    donor_known: str = ""             # indexed | verified | ""
    summary: str = ""


def _terms_hit(tk: set, terms: Sequence[str]) -> int:
    """How many of the gap's explicit keyword phrases appear in the text (>= 60% of a phrase's words)."""
    n = 0
    for t in terms:
        tt = _tokens(t)
        if tt and _overlap(tt, tk) >= max(1, -(-len(tt) * 3 // 5)):
            n += 1
    return n


def _coverage(a: set, b: set) -> float:
    """Share of the smaller word set that the other contains; stops long generic texts from matching by chance."""
    return _overlap(a, b) / max(1, min(len(a), len(b)))


def fit(led: Ledger, mechanics: Sequence[str], donor_id: str = "") -> FitReport:
    """Classify each mechanic found in a repo/site/doc/video against what DNK has and lacks.

    Precision over recall: ALREADY_HAVE needs 3+ shared words AND 40% coverage of the shorter text;
    FILLS_GAP needs one of the gap's own keyword phrases, not loose overlap with its prose."""
    rep = FitReport()
    known = next((d for d in led.donors if donor_id and d.id.lower() == donor_id.lower()), None)
    if known:
        rep.donor_known = known.level
    done = [(d, a) for d in led.donors for a in d.assimilations if a.status in ("done", "in_progress", "planned")]
    modules = [(m, _tokens(f"{m.id} {m.description} {' '.join(m.tags)} {' '.join(m.tools)}")) for m in led.modules]
    for text in mechanics:
        tk = _tokens(text)
        item = FitItem(text=text, verdict="NO_MATCH")
        have = max(((_overlap(tk, _tokens(a.what)), _coverage(tk, _tokens(a.what)), d, a) for d, a in done),
                   key=lambda x: (x[1], x[0]), default=(0, 0.0, None, None))
        gap = max(((_terms_hit(tk, g.terms), -g.priority, g) for g in led.gaps if g.status == "open"),
                  key=lambda x: (x[0], x[1]), default=(0, 0, None))
        mod = max(((_overlap(tk, mt), m) for m, mt in modules), key=lambda x: x[0], default=(0, None))
        if have[0] >= 3 and have[1] >= 0.4:
            item.verdict, item.have_from, item.module = "ALREADY_HAVE", f"{have[2].id}/{have[3].id}", have[3].module
            item.note = f"вже є ({have[3].status}): {have[3].what}"
        elif gap[0] >= 1:
            item.verdict, item.gap, item.module = "FILLS_GAP", gap[2].id, gap[2].module
            item.note = f"закриває прогалину: {gap[2].need}"
        elif mod[0] >= 2:
            item.verdict, item.module = "ADJACENT", mod[1].id
            item.note = f"поруч із модулем {mod[1].id}, але прогалини немає"
        rep.items.append(item)
    n = {v: sum(1 for i in rep.items if i.verdict == v) for v in ("FILLS_GAP", "ALREADY_HAVE", "ADJACENT", "NO_MATCH")}
    rep.summary = ", ".join(f"{k}={v}" for k, v in n.items())
    return rep


def mechanics_from_dossier(d: Dict[str, Any]) -> List[str]:
    return [" ".join(str(m.get(k) or "") for k in ("name", "what", "purpose", "spec")).strip() for m in d.get("mechanics", []) if isinstance(m, dict)]


# --------------------------------------------------------------------------- context for the agent

def render_context(led: Ledger, module: str = "", max_donors: int = 12) -> str:
    """Compact block for the agent prompt: where it runs, what exists, what is missing, what not to take twice."""
    L: List[str] = ["## Контекст DNK OS (з реєстру асиміляцій)"]
    if led.environments:
        L.append("### Середовища виконання")
        for e in led.environments:
            L.append(f"- {e.id} ({e.kind}): " + "; ".join(f"{k} {v}" for k, v in e.stack.items()) +
                     ("; обмеження: " + "; ".join(e.constraints) if e.constraints else ""))
    mods = [m for m in led.modules if not module or m.id == module]
    for m in mods[:1] if module else []:
        L.append(f"### Модуль {m.id} ({m.path})\n{m.description}")
    gaps = [g for g in led.gaps if g.status == "open" and (not module or g.module == module)]
    if gaps:
        L.append("### Відкриті прогалини (це шукаємо)")
        for g in sorted(gaps, key=lambda g: g.priority):
            L.append(f"- [{g.id}] p{g.priority} {g.need}")
    taken = [(d, a) for d in led.donors for a in d.assimilations if (not module or a.module == module) and a.status in ("done", "in_progress", "planned")]
    if taken:
        L.append("### Вже взято (не брати вдруге)")
        for d, a in taken:
            L.append(f"- {a.what} ← {d.id} [{a.method}, {a.status}] → {a.dnk_path or a.module}")
    rej = [(d, a) for d in led.donors for a in d.assimilations if a.status == "rejected" and (not module or a.module == module)]
    if rej:
        L.append("### Відхилено (не пропонувати знову)")
        for d, a in rej:
            L.append(f"- {a.what} ← {d.id}: {a.notes}")
    ix = [d for d in led.donors if d.level == "indexed" and module and (module in d.target_hint)]
    if ix:
        L.append(f"### Заявлені (не перевірені) донори для {module}: " + ", ".join(d.id for d in ix[:max_donors]))
    return "\n".join(L)


def stats(led: Ledger) -> Dict[str, Any]:
    by_lic: Dict[str, int] = {}
    for d in led.donors:
        c = classify_license(d.license).license_class.value
        by_lic[c] = by_lic.get(c, 0) + 1
    return {"modules": len(led.modules), "environments": len(led.environments), "gaps_open": sum(1 for g in led.gaps if g.status == "open"),
            "donors": len(led.donors), "donors_indexed": sum(1 for d in led.donors if d.level == "indexed"),
            "donors_verified": sum(1 for d in led.donors if d.level == "verified"), "donor_license_classes": by_lic}
