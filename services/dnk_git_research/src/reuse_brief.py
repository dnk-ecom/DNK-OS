# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/reuse_brief.py"
# purpose: "Reuse Brief pipeline: gate -> needs -> catalog + live GitHub prior-art search -> license verdicts -> brief returned to an agent before it writes code"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Before an agent writes specific code, ask: has the world already solved this?

  1. task_gate decides: SKIP (simple/repetitive) | RESEARCH (specific mechanics).
  2. A fresh brief for the same mechanics is served from cache (CACHED), no search.
  3. Otherwise each mechanic becomes a "need"; candidates come from the local
     catalog (read-only) and, when enabled, from live GitHub search.
  4. Every candidate carries a license verdict from license_policy; each need gets
     ADOPT | ADAPT | CLEAN_ROOM | BUILD plus a concrete next step.

Nothing here invents data: a candidate is listed only if its own text matches the
need's terms, license evidence is labelled, and a failed live search is reported,
never replaced with placeholders.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from services.dnk_git_research.src.brief_store import BriefStore
from services.dnk_git_research.src.catalog_reader import HUB_ROOT, CatalogReader
from services.dnk_git_research.src.domain_terms import match_domains
from services.dnk_git_research.src.git_researcher import GitHubSearchError, GitResearchEngine
from services.dnk_git_research.src.license_policy import LicenseVerdict, ReuseAction, classify_license
from services.dnk_git_research.src.schemas.brief import CandidateOut, NeedResult, ReuseBrief, Verdict
from services.dnk_git_research.src.schemas.repo_input import RepoMetadata
from services.dnk_git_research.src.task_gate import GateMode, TaskSpec, decide

logger = logging.getLogger("dnk.git_research.brief")

LiveSearcher = Callable[[List[str], int], Sequence[RepoMetadata]]
LicenseProbe = Callable[[str], Optional[str]]

_JUNK = re.compile(r"\b(tutorial|course|homework|awesome|cheat ?sheet|leetcode|interview|bootcamp)\b", re.IGNORECASE)
_STOP = {
    "this", "that", "with", "from", "into", "should", "would", "make", "using", "module",
    "function", "class", "file", "service", "support", "feature", "implement", "create",
    "build", "add", "new",
}
_ACTION_RANK = {ReuseAction.ADOPT: 0, ReuseAction.ADAPT: 1, ReuseAction.CLEAN_ROOM: 2}


@dataclass
class Need:
    key: str
    text: str
    terms: List[str]


def extract_needs(text: str, max_needs: int = 4) -> List[Need]:
    """Needs = specific mechanics found in the task; free-form English words only as a fallback."""
    needs = [Need(d.key, d.label, list(d.terms)) for d in match_domains(text)[:max_needs]]
    if needs:
        return needs
    words: List[str] = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{3,}", text or ""):
        lw = w.lower()
        if lw not in _STOP and lw not in words:
            words.append(lw)
    return [Need("freeform", " ".join(words[:5]), words[:5])] if words else []


def _term_in(term: str, hay: str) -> bool:
    t = term.lower()
    for v in {t, t.replace("-", " "), t.replace("-", "")}:
        pat = r"(?<![a-z0-9])" + re.escape(v) + (r"(?![a-z0-9])" if len(v) <= 3 else "")
        if re.search(pat, hay):
            return True
    return False


def _min_hits(n_terms: int) -> int:
    return 1 if n_terms <= 2 else 2


def _norm_tier(tier: Optional[str]) -> str:
    if not tier:
        return "Tier 3: Discovery Radar"
    if tier.startswith("Tier 2"):
        return "Tier 2: SOTA Blueprint"
    return tier


def _tier_from_stars(stars: int) -> str:
    if stars >= 5000:
        return "Tier 1: Golden Core"
    if stars >= 500:
        return "Tier 2: SOTA Blueprint"
    return "Tier 3: Discovery Radar"


def _tier_rank(tier: str) -> int:
    return 1 if tier.startswith("Tier 1") else 2 if tier.startswith("Tier 2") else 3


def _license_fields(v: LicenseVerdict) -> dict:
    return {
        "license_raw": v.raw,
        "license_spdx": v.spdx,
        "license_class": v.license_class,
        "license_evidence": v.evidence,
        "action": v.action,
        "can_depend": v.can_depend,
        "can_copy_code": v.can_copy_code,
    }


def _apply_license(c: CandidateOut, v: LicenseVerdict) -> None:
    for k, val in _license_fields(v).items():
        setattr(c, k, val)


def default_live_searcher(engine: Optional[GitResearchEngine] = None) -> LiveSearcher:
    eng = engine or GitResearchEngine()

    def _search(terms: List[str], limit: int) -> Sequence[RepoMetadata]:
        # GitHub ANDs every word, so three terms usually match nothing. Start with two
        # and widen to one only if needed (at most 2 requests per need).
        for n in (2, 1):
            if n > len(terms) and n != 1:
                continue
            query = " ".join(terms[:n]) + " archived:false fork:false stars:>=20"
            found = eng.search_repositories(query, sort="stars", order="desc", limit=limit, allow_fallback=False)
            if found:
                return found
        return []

    return _search


def github_license_probe(full_name: str, timeout: float = 5.0) -> Optional[str]:
    """SPDX id as detected by GitHub, or None when unavailable (never guesses)."""
    if not re.fullmatch(r"[\w.\-]+/[\w.\-]+", full_name or ""):
        return None
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DNK-OS-GitResearcher/2.6"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{full_name}/license", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("license") or {}).get("spdx_id") or None
    except Exception:
        return None


class ReuseBriefService:
    def __init__(
        self,
        catalog: Optional[CatalogReader] = None,
        store: Optional[BriefStore] = None,
        live_searcher: Optional[LiveSearcher] = None,
        license_probe: Optional[LicenseProbe] = None,
        hub_root: Optional[Path] = None,
        live: bool = True,
        max_needs: int = 4,
    ):
        self.catalog = catalog or CatalogReader()
        self.store = store or BriefStore()
        self.live = live
        self.live_searcher = live_searcher if live_searcher is not None else (default_live_searcher() if live else None)
        self.license_probe = license_probe or github_license_probe
        self.hub_root = Path(hub_root) if hub_root else HUB_ROOT
        self.max_needs = max_needs

    # ------------------------------------------------------------------ public
    def build(
        self,
        text: str,
        target_files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        force: bool = False,
        refresh: bool = False,
        verify_licenses: bool = False,
    ) -> ReuseBrief:
        spec = TaskSpec(text=text, target_files=list(target_files or []), tags=list(tags or []))
        decision = decide(spec, force=force)
        now = datetime.now(timezone.utc).isoformat()

        if decision.mode == GateMode.SKIP:
            return ReuseBrief(
                mode=GateMode.SKIP, source="gate", fingerprint=decision.fingerprint, gate=decision,
                summary="Задача проста або повторювана: JIT-пошук не потрібен, пиши за наявними патернами проєкту.",
                generated_at=now,
            )

        if not refresh:
            cached = self.store.get(decision.fingerprint)
            if cached:
                try:
                    brief = ReuseBrief.model_validate_json(cached)
                    brief.mode, brief.source, brief.gate = GateMode.CACHED, "cache", decision
                    return brief
                except ValueError:
                    logger.warning("discarding unreadable cached brief %s", decision.fingerprint)

        needs = extract_needs(text, self.max_needs)
        results = [self._research_need(n, verify_licenses) for n in needs]
        notes: List[str] = []
        if not needs:
            notes.append("Не вдалося виділити конкретні механіки: уточни задачу або додай тег force_research з англійськими термінами.")
        if not self.catalog.available():
            notes.append("Локальний каталог недоступний: використано лише живий пошук.")

        brief = ReuseBrief(
            mode=GateMode.RESEARCH, source="fresh", fingerprint=decision.fingerprint, gate=decision,
            needs=results, summary=self._summary(results), notes=notes, generated_at=now,
        )
        if results:
            self.store.put(decision.fingerprint, brief.model_dump_json())
        return brief

    # ----------------------------------------------------------------- internal
    def _research_need(self, need: Need, verify_licenses: bool) -> NeedResult:
        cands: List[CandidateOut] = []
        notes: List[str] = []

        if self.catalog.available():
            for row in self.catalog.search(need.terms, limit=12):
                c = self._from_row(row, need)
                if c:
                    cands.append(c)

        if self.live and self.live_searcher:
            try:
                for repo in self.live_searcher(need.terms, 6):
                    self._merge(cands, self._from_repo(repo, need))
            except GitHubSearchError as exc:
                notes.append(f"Живий пошук GitHub не вдався ({exc}); результат лише з каталогу.")
            except Exception as exc:  # defensive: never break the brief over the network
                notes.append(f"Живий пошук GitHub недоступний ({type(exc).__name__}).")

        cands = sorted(
            cands,
            key=lambda c: (-c.relevance, _tier_rank(c.tier), 0 if c.source == "catalog" else 1, -(c.stars or 0)),
        )[:4]

        if verify_licenses:
            for c in cands[:3]:
                if c.source == "catalog" and c.license_evidence != "spdx":
                    spdx = self.license_probe(c.repo_id)
                    if spdx:
                        _apply_license(c, classify_license(spdx))
                    else:
                        notes.append(f"Ліцензію {c.repo_id} не вдалося підтвердити через GitHub.")

        verdict, vnotes = self._verdict(cands)
        notes.extend(vnotes)
        return NeedResult(
            key=need.key, need=need.text, terms=need.terms, verdict=verdict, candidates=cands,
            next_step=self._next_step(verdict, cands[0] if cands else None, need), notes=notes,
        )

    def _from_row(self, row: dict, need: Need) -> Optional[CandidateOut]:
        hay = " ".join(
            str(row.get(k) or "")
            for k in ("id", "title", "description", "what_it_gives", "tech_stack", "category", "architectural_pattern")
        ).lower()
        matched = [t for t in need.terms if _term_in(t, hay)]
        if len(matched) < _min_hits(len(need.terms)):
            return None
        doc = row.get("sota_doc_path")
        existing = doc if doc and (self.hub_root / doc).exists() else None
        return CandidateOut(
            repo_id=row["id"],
            url=row.get("url") or f"https://github.com/{row['id']}",
            source="catalog",
            title=row.get("title") or row["id"],
            why=(row.get("what_it_gives") or row.get("description") or "")[:240],
            tier=_norm_tier(row.get("maturity_tier")),
            relevance=round(len(matched) / len(need.terms), 2),
            matched_terms=matched,
            existing_doc=existing,
            assimilation_status=row.get("assimilation_status"),
            **_license_fields(classify_license(row.get("license_track"))),
        )

    def _from_repo(self, repo: RepoMetadata, need: Need) -> Optional[CandidateOut]:
        hay = f"{repo.full_name} {repo.description} {' '.join(repo.topics)}".lower()
        if _JUNK.search(hay):
            return None
        matched = [t for t in need.terms if _term_in(t, hay)]
        return CandidateOut(
            repo_id=repo.full_name,
            url=repo.url,
            source="github",
            title=repo.name,
            why=(repo.description or "")[:240],
            tier=_tier_from_stars(repo.stars),
            stars=repo.stars,
            relevance=round(len(matched) / len(need.terms), 2) if need.terms else 0.0,
            matched_terms=matched,
            **_license_fields(classify_license(repo.license)),
        )

    @staticmethod
    def _merge(cands: List[CandidateOut], new: Optional[CandidateOut]) -> None:
        if new is None:
            return
        for c in cands:
            if c.repo_id.lower() == new.repo_id.lower():
                if new.license_evidence == "spdx" and c.license_evidence != "spdx":
                    _apply_license(c, classify_license(new.license_spdx or new.license_raw))
                c.stars = c.stars or new.stars
                return
        cands.append(new)

    @staticmethod
    def _verdict(cands: List[CandidateOut]):
        if not cands:
            return Verdict.BUILD, []
        primary, notes = cands[0], []
        if primary.action == ReuseAction.ADOPT:
            why_not = []
            if primary.license_evidence != "spdx":
                why_not.append("ліцензію не підтверджено")
            if _tier_rank(primary.tier) == 3:
                why_not.append("репозиторій не зрілий (Tier 3)")
            if why_not:
                verdict = Verdict.ADAPT
                notes.append("ADOPT знижено до ADAPT: " + ", ".join(why_not) + ".")
            else:
                verdict = Verdict.ADOPT
        elif primary.action == ReuseAction.ADAPT:
            verdict = Verdict.ADAPT
        else:
            verdict = Verdict.CLEAN_ROOM
        better = [c for c in cands[1:] if _ACTION_RANK[c.action] < _ACTION_RANK[primary.action]]
        if better:
            notes.append(f"Є менш обмежувальна альтернатива: {better[0].repo_id} ({better[0].action.value}).")
        return verdict, notes

    def _next_step(self, verdict: Verdict, p: Optional[CandidateOut], need: Need) -> str:
        doc = f" Наявна картка: {p.existing_doc}." if p and p.existing_doc else ""
        if verdict == Verdict.BUILD or p is None:
            where = "каталог і GitHub" if (self.live and self.live_searcher) else "каталог"
            return f"Готових рішень не знайдено ({where}). Пиши власну реалізацію й зазнач у задачі, що пошук виконано."
        if verdict == Verdict.ADOPT:
            return (f"Підключи {p.repo_id} як залежність або перенеси потрібне з атрибуцією ({p.license_spdx}); "
                    f"перевір API та версію.{doc}")
        if verdict == Verdict.ADAPT:
            extra = "" if p.license_evidence == "spdx" else " Спершу підтверди ліцензію (LICENSE у репозиторії)."
            return f"Вивчи механіку «{need.text}» у {p.url} і перепиши власну реалізацію; файли не копіюй.{extra}{doc}"
        return (f"Опиши механіку «{need.text}» (формули, структури даних, потік виконання) зі {p.url} "
                f"у специфікацію й реалізуй за нею; код не копіюй і не підключай.{doc}")

    @staticmethod
    def _summary(results: List[NeedResult]) -> str:
        if not results:
            return "Потреб не виділено."
        counts = Counter(r.verdict.value for r in results)
        return f"Потреб: {len(results)}. " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))


def format_brief_text(brief: ReuseBrief) -> str:
    lines = [f"[{brief.mode.value}] {brief.summary}  (джерело: {brief.source}, відбиток: {brief.fingerprint})"]
    if brief.gate.reasons:
        lines.append("Гейт: " + "; ".join(brief.gate.reasons))
    for n in brief.needs:
        lines.append(f"\n● {n.need}  →  {n.verdict.value}")
        for c in n.candidates:
            stars = f" ★{c.stars}" if c.stars is not None else ""
            lines.append(
                f"    - {c.repo_id}{stars} [{c.source}, {c.tier.split(':')[0]}] "
                f"{c.action.value} (ліцензія: {c.license_spdx or c.license_raw or 'невідомо'}, {c.license_evidence}) "
                f"збіг: {', '.join(c.matched_terms) or '—'}"
            )
        lines.append(f"    ↳ {n.next_step}")
        for note in n.notes:
            lines.append(f"    ! {note}")
    for note in brief.notes:
        lines.append(f"! {note}")
    return "\n".join(lines)
