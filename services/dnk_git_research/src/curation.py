# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/curation.py"
# purpose: "Library curation: explainable health score, structural and risk checks, removal plan, and reversible apply/restore for the repository catalog"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Curation = decide which of the ~2300 repositories deserve to stay in the library.

Tiers
  KEEP        healthy, useful.
  WATCH       usable but has a weakness (stale, small, unverified) or needs a human look.
  QUARANTINE  low value or a risk sign; hidden from the library until reviewed.
  REMOVE      gone, disabled, duplicate, or no value left.
  UNSCORED    no real signals fetched yet (only structural/keyword checks ran).

Principles
  * Facts first: the score uses fetched GitHub signals; without them a repo is UNSCORED,
    never "healthy" by default.
  * Protected: anything we already assimilated (card, skill, non-radar status) is never
    auto-removed; at worst it is WATCH, because our knowledge of it is worth more than upstream.
  * Old is not bad: a famous, stable library is kept even without recent commits
    (mechanics do not expire the way frameworks do).
  * Risk flags cannot prove malice and absence of flags does not prove safety. They only send
    a repo to quarantine for a human, and everything is reversible (restore).
  * Nothing is deleted from the catalog without apply(confirm=True), and a backup comes first.
"""

from __future__ import annotations

import json
import math
import re
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from pydantic import BaseModel, Field

from services.dnk_git_research.src.health_store import HealthStore
from services.dnk_git_research.src.niche_profiles import ContentSignals, NICHES, detect_niches
from services.dnk_git_research.src.license_policy import ReuseAction, classify_license
from services.dnk_git_research.src.repo_signals import RepoSignals, github_full_name, github_org_login

KEEP_MIN, WATCH_MIN, QUARANTINE_MIN = 55, 35, 15

_RISK = re.compile(
    r"\b(stealer|token[- ]?grabber|keylogger|botnet|ddos|ransomware|exploit[- ]?kit|malware|rootkit|"
    r"cryptojack\w*|keygen|cracked|spammer|credential[- ]?harvest\w*)\b", re.IGNORECASE)
_STUDENT = re.compile(
    r"(homework|assignment|coursework|course[-_ ]?project|tutorial|my[-_ ]first|hello[-_ ]world|"
    r"todo[-_ ]?app|\blab\d|lecture|bootcamp|test[-_ ]repo|demo[-_ ]?project)", re.IGNORECASE)
_ASSIMILATED_STATUS_PREFIX = ("INDEXED",)
_DOC_PLACEHOLDERS = {"repo", "mono", "my-plugin", "project", "example", "name", "my-repo", "my-project"}


class Tier(str, Enum):
    KEEP = "KEEP"
    WATCH = "WATCH"
    QUARANTINE = "QUARANTINE"
    REMOVE = "REMOVE"
    UNSCORED = "UNSCORED"


class Assessment(BaseModel):
    repo_id: str
    tier: Tier
    score: Optional[int] = None
    protected: bool = False
    flags: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)


class Plan(BaseModel):
    generated_at: str
    total: int
    counts: Dict[str, int]
    items: List[Assessment]


def _parse(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _months_since(ts: Optional[str], now: datetime) -> Optional[float]:
    d = _parse(ts)
    return None if d is None else (now - d).days / 30.4


def is_protected(row: Dict[str, Any]) -> bool:
    """We hold knowledge about it (card/skill) or it was assimilated: never auto-remove."""
    status = (row.get("assimilation_status") or "INDEXED_RADAR").upper().lstrip("✅🧬 ").strip()
    return bool(row.get("sota_doc_path") or row.get("skill_name")
                or not status.startswith(_ASSIMILATED_STATUS_PREFIX))


def _levenshtein_le1(a: str, b: str) -> bool:
    if a == b:
        return False
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    i = 0
    while i < len(short) and short[i] == long_[i]:
        i += 1
    return short[i:] == long_[i + 1:]


def structural_flags(row: Dict[str, Any], all_ids: Set[str]) -> Dict[str, Any]:
    """Offline checks that need no network. Returns flags, reasons and an optional forced tier."""
    flags: List[str] = []
    reasons: List[str] = []
    forced: Optional[Tier] = None
    rid = (row.get("id") or "").lower()

    if not re.fullmatch(r"[\w.\-]+/[\w.\-]+", rid):
        flags.append("PORTAL_OR_NONSTANDARD_ID")
    name = github_full_name(row.get("url"))
    owner_l = rid.split("/")[0]
    if owner_l == "owner" and rid.split("/")[-1] in _DOC_PLACEHOLDERS:
        flags.append("PLACEHOLDER_ID")
        reasons.append("Це приклад із документації (owner/repo), а не реальний репозиторій.")
        forced = Tier.REMOVE
    elif github_org_login(row.get("url")):
        flags.append("ORG_ENTRY")        # an organization/user page: a source of repositories, not a repository
    elif "/topics/" in (row.get("url") or ""):
        flags.append("TOPIC_PAGE")
    elif name is None:
        flags.append("NOT_A_GITHUB_REPO")
        reasons.append("URL не вказує на репозиторій GitHub (портал, профіль або інший хост).")
    elif name.lower() != rid and "/" in rid:
        flags.append("URL_ID_MISMATCH")
        reasons.append(f"id «{row.get('id')}» не збігається з URL «{name}».")

    # Truncation signature: the id lost exactly its LAST character (rag-anythin / rag-anything).
    # Longer gaps are legitimate sibling repos (langchain / langchain-mcp-adapters) and are NOT flagged.
    if "/" in rid and len(rid) >= 10:
        owner = rid.split("/")[0]
        for other in all_ids:
            if (
                len(other) == len(rid) + 1
                and other.startswith(rid)
                and other.split("/")[0] == owner
                and other[-1].isalnum()
            ):
                flags.append(f"DUPLICATE_OF:{other}")
                reasons.append(f"Обрізаний дубль запису «{other}» (втрачено останній символ).")
                forced = Tier.REMOVE
                break

    desc = (row.get("description") or "").strip()
    if len(desc) < 10:
        flags.append("NO_DESCRIPTION")
    text = f"{row.get('id', '')} {row.get('title', '')} {desc}"
    if _RISK.search(text):
        flags.append("RISK_KEYWORD")
        reasons.append("У назві чи описі є ознака шкідливого призначення (потрібна ручна перевірка: це може бути захисний інструмент).")
    return {"flags": flags, "reasons": reasons, "forced": forced}


def assess(
    row: Dict[str, Any],
    sig: Optional[RepoSignals],
    dup_context: Optional[Set[str]] = None,
    popular: Optional[Dict[str, Any]] = None,
    now: Optional[datetime] = None,
    content: Optional[ContentSignals] = None,
) -> Assessment:
    now = now or datetime.now(timezone.utc)
    rid = row["id"]
    protected = is_protected(row)
    st = structural_flags(row, dup_context or set())
    flags, reasons = list(st["flags"]), list(st["reasons"])
    risk = "RISK_KEYWORD" in flags

    # typosquat: one edit away from a much more popular repo of a different owner
    name_l = rid.split("/")[-1].lower()
    owner_l = rid.split("/")[0].lower()
    if popular and len(name_l) >= 6 and sig is not None and sig.status == "ok":
        for pname, (powner, pstars) in popular.items():
            if powner != owner_l and _levenshtein_le1(name_l, pname) and sig.stars * 20 < pstars:
                flags.append(f"TYPOSQUAT_OF:{powner}/{pname}")
                reasons.append(f"Назва на одну літеру відрізняється від популярного «{powner}/{pname}» ({pstars}★).")
                risk = True
                break

    def finish(tier: Tier, score: Optional[int]) -> Assessment:
        if protected and tier in (Tier.QUARANTINE, Tier.REMOVE):
            flags.append("PROTECTED_REVIEW")
            reasons.append("Захищено: запис асимільовано або має картку/навичку, автоматично не видаляється.")
            tier = Tier.WATCH
        return Assessment(repo_id=rid, tier=tier, score=score, protected=protected,
                          flags=flags, reasons=reasons)

    if st["forced"] == Tier.REMOVE:
        return finish(Tier.REMOVE, None)

    if "TOPIC_PAGE" in flags:      # a GitHub topic listing is neither a repository nor a source: never judged by the API
        return finish(Tier.UNSCORED, None)

    if sig is None or sig.status in ("not_github", "invalid", "error"):
        if risk:
            return finish(Tier.QUARANTINE, None)
        return finish(Tier.UNSCORED, None)

    if "ORG_ENTRY" in flags:
        # An organization is a source of ready-made services to study and assimilate. Fame is irrelevant;
        # only its existence matters, and a missing one goes to a human (it may have been renamed).
        if sig.status == "gone":
            flags.append("ORG_NOT_FOUND")
            reasons.append("Організацію не знайдено на GitHub (HTTP %s): перевірити, чи її не перейменовано." % sig.http_status)
            return finish(Tier.WATCH, None)
        if sig.kind != "org":
            return finish(Tier.UNSCORED, None)
        months = _months_since(sig.pushed_at, now)
        reasons.insert(0, f"Організація-джерело: {sig.public_repos} публічних репозиторіїв"
                          + (f", профіль оновлено {months:.0f} міс. тому." if months is not None else "."))
        if sig.public_repos == 0:
            flags.append("ORG_NO_PUBLIC_REPOS")
            return finish(Tier.WATCH, None)
        return finish(Tier.KEEP, None)

    if sig.status == "gone":
        flags.append("UPSTREAM_GONE")
        reasons.append("Репозиторій більше не існує або став приватним (HTTP %s)." % sig.http_status)
        return finish(Tier.REMOVE, 0)
    if sig.disabled:
        flags.append("DISABLED")
        reasons.append("Репозиторій вимкнено на GitHub.")
        return finish(Tier.REMOVE, 0)

    score = 0.0
    score += min(35.0, 10.0 * math.log10(sig.stars + 1))
    score += min(10.0, 5.0 * math.log10(sig.forks + 1))

    months = _months_since(sig.pushed_at, now)
    legacy_stable = sig.stars >= 1000
    if months is None:
        flags.append("NO_PUSH_DATE")
    elif months <= 3:
        score += 25
    elif months <= 6:
        score += 20
    elif months <= 12:
        score += 12
    elif months <= 24:
        score += 4
    else:
        if legacy_stable:
            flags.append("LEGACY_STABLE")
            reasons.append(f"Давно без змін ({months/12:.1f} р.), але визнана ({sig.stars}★): механіки не застарівають.")
        else:
            score -= 15
            flags.append("STALE")
            reasons.append(f"Остання активність {months/12:.1f} р. тому, мало визнання ({sig.stars}★).")

    if sig.owner_type == "Organization":
        score += 5
    if sig.license_spdx and classify_license(sig.license_spdx).action == ReuseAction.ADOPT:
        score += 5
    if not sig.license_spdx:
        flags.append("NO_LICENSE")
    if sig.topics:
        score += 3
    if len(sig.description or row.get("description") or "") >= 30:
        score += 3
    tier_label = row.get("maturity_tier") or ""
    score += 5 if tier_label.startswith("Tier 1") else 3 if tier_label.startswith("Tier 2") else 0

    if sig.archived:
        score -= 10 if legacy_stable else 25
        flags.append("ARCHIVED")
        reasons.append("Репозиторій заархівовано автором.")
    if sig.fork and not sig.is_template:
        score -= 10
        flags.append("FORK")

    created_months = _months_since(sig.created_at, now)
    low_signal = (
        _STUDENT.search(f"{rid} {row.get('title', '')}")
        or (sig.stars < 5 and sig.forks < 2 and sig.owner_type == "User" and not sig.license_spdx
            and (created_months or 0) > 6)
    )
    if low_signal:
        score -= 15
        flags.append("LOW_SIGNAL")
        reasons.append("Схоже на навчальний або покинутий проєкт (мало уваги, без ліцензії, навчальна назва).")
    if sig.size_kb < 30 and sig.stars < 10:
        score -= 10
        flags.append("TINY")
    if created_months is not None and created_months < 2 and sig.stars >= 500 and sig.forks <= 2:
        flags.append("SUSPICIOUS_METRICS")
        reasons.append("Дуже молодий репозиторій із великою кількістю зірок і майже без форків (можлива накрутка).")
        risk = True

    final = int(max(0, min(100, round(score))))
    age = "невідомо" if months is None else f"{months:.0f} міс. тому"
    reasons.insert(0, f"Оцінка {final}/100: {sig.stars}★, {sig.forks} форків, остання активність {age}"
                      + (", ліцензії немає" if "NO_LICENSE" in flags else "") + ".")
    niches = detect_niches(row, sig)
    fame_tier = (Tier.QUARANTINE if risk else Tier.KEEP if final >= KEEP_MIN else Tier.WATCH if final >= WATCH_MIN
                 else Tier.QUARANTINE if final >= QUARANTINE_MIN else Tier.REMOVE)
    # Niche repositories (Shopify themes, coding assets, defense) are rarely popular and can still be
    # exactly what we need, so low fame alone never sends them away: judge the content instead.
    hard_risk = risk or any(f.startswith(("TYPOSQUAT", "SUSPICIOUS")) for f in flags)
    if niches and fame_tier in (Tier.QUARANTINE, Tier.REMOVE) and not hard_risk:
        labels = ", ".join(n.label for n in NICHES if n.key in niches)
        if content is None or content.status == "error":
            flags.append("NICHE_PENDING_DEEP_SCAN")
            reasons.append(f"Ніша: {labels}. Популярність тут не критерій, потрібне глибоке сканування вмісту (curate deepscan).")
            return finish(Tier.WATCH, final)
        flags.append("NICHE_" + "_".join(sorted(niches)).upper())
        reasons.append(f"Ніша: {labels}. Оцінка за вмістом {content.value}/100, файлів {content.file_count}, "
                       f"маркери: {', '.join(m.split(':')[1] for m in content.markers) or 'немає'}.")
        bad_risks = [r for r in content.risks if r in ("COMMITTED_SECRETS", "EXECUTABLE_FILES", "ARCHIVE_ONLY")]
        if bad_risks and "security_defense" not in niches:
            flags += [f"CONTENT_RISK:{r}" for r in bad_risks]
            reasons.append("У дереві файлів є підозрілі елементи: " + ", ".join(bad_risks) + ". Потрібен огляд людиною.")
            return finish(Tier.QUARANTINE, content.value)
        if content.status == "empty" or content.value < 15:
            flags.append("NICHE_EMPTY")
            return finish(Tier.REMOVE, content.value)
        if content.value >= 60:
            return finish(Tier.KEEP, content.value)
        return finish(Tier.WATCH if content.value >= 35 else Tier.QUARANTINE, content.value)
    if risk:
        tier = Tier.QUARANTINE
    elif final >= KEEP_MIN:
        tier = Tier.KEEP
    elif final >= WATCH_MIN:
        tier = Tier.WATCH
    elif final >= QUARANTINE_MIN:
        tier = Tier.QUARANTINE
    else:
        tier = Tier.REMOVE
    return finish(tier, final)


def build_plan(rows: Sequence[Dict[str, Any]], signals: Dict[str, RepoSignals], now: Optional[datetime] = None,
               content: Optional[Dict[str, ContentSignals]] = None) -> Plan:
    now = now or datetime.now(timezone.utc)
    all_ids = {r["id"].lower() for r in rows}
    popular: Dict[str, Any] = {}
    for r in rows:
        s = signals.get(r["id"].lower())
        if s and s.status == "ok" and s.stars >= 1000 and "/" in r["id"]:
            owner, name = r["id"].lower().split("/", 1)
            popular[name] = (owner, s.stars)
    content = content or {}
    items = [assess(r, signals.get(r["id"].lower()), all_ids, popular, now, content.get(r["id"].lower())) for r in rows]
    order = {Tier.REMOVE: 0, Tier.QUARANTINE: 1, Tier.WATCH: 2, Tier.UNSCORED: 3, Tier.KEEP: 4}
    items.sort(key=lambda a: (order[a.tier], a.score if a.score is not None else -1, a.repo_id))
    counts: Dict[str, int] = {t.value: 0 for t in Tier}
    for a in items:
        counts[a.tier.value] += 1
    return Plan(generated_at=now.isoformat(), total=len(items), counts=counts, items=items)


# --------------------------------------------------------------------------- apply / restore
_FTS_COLS = ("title", "description", "category", "subcategory", "what_it_gives", "assigned_agent",
             "tech_stack", "maturity_tier", "dnk_module_target", "architectural_pattern")


def load_rows(catalog_path: Path) -> List[Dict[str, Any]]:
    con = sqlite3.connect(catalog_path.resolve().as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT * FROM repositories")]
    finally:
        con.close()


def apply_plan(
    plan: Plan,
    catalog_path: Path,
    store: HealthStore,
    tiers: Sequence[Tier] = (Tier.REMOVE, Tier.QUARANTINE),
    confirm: bool = False,
) -> Dict[str, Any]:
    """Move selected repos out of the catalog into the quarantine table. Dry run unless confirm=True."""
    chosen = [a for a in plan.items if a.tier in tiers and not a.protected]
    summary: Dict[str, Any] = {"selected": len(chosen), "applied": 0, "dry_run": not confirm,
                               "by_tier": {t.value: sum(1 for a in chosen if a.tier == t) for t in tiers}}
    if not confirm or not chosen:
        return summary

    store.backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup = store.backups_dir / f"catalog-{stamp}.db"
    src = sqlite3.connect(str(catalog_path))
    try:
        dst = sqlite3.connect(str(backup))
        try:
            src.backup(dst)
        finally:
            dst.close()
        summary["backup"] = str(backup)

        src.row_factory = sqlite3.Row
        qcon = store.connect()
        try:
            src.execute("BEGIN")
            for a in chosen:
                row = src.execute("SELECT * FROM repositories WHERE id = ?", (a.repo_id,)).fetchone()
                if row is None:
                    continue
                store.quarantine_add(qcon, a.repo_id, a.tier.value, a.flags + a.reasons, dict(row))
                src.execute("DELETE FROM repositories WHERE id = ?", (a.repo_id,))
                src.execute("DELETE FROM repositories_fts WHERE id = ?", (a.repo_id,))
                summary["applied"] += 1
            qcon.commit()
            src.commit()
        except Exception:
            src.rollback()
            qcon.rollback()
            raise
        finally:
            qcon.close()
    finally:
        src.close()
    return summary


def restore(repo_id: str, catalog_path: Path, store: HealthStore) -> bool:
    item = store.quarantine_get(repo_id)
    if not item:
        return False
    row = item["row"]
    cols = list(row.keys())
    con = sqlite3.connect(str(catalog_path))
    qcon = store.connect()
    try:
        con.execute(
            f"INSERT OR REPLACE INTO repositories ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})",
            [row[c] for c in cols],
        )
        con.execute("DELETE FROM repositories_fts WHERE id = ?", (row["id"],))
        con.execute(
            f"INSERT INTO repositories_fts (id, {', '.join(_FTS_COLS)}) VALUES (?, {', '.join('?' for _ in _FTS_COLS)})",
            [row["id"]] + [row.get(c) or "" for c in _FTS_COLS],
        )
        con.commit()
        store.quarantine_remove(qcon, repo_id)
        qcon.commit()
    finally:
        con.close()
        qcon.close()
    return True
