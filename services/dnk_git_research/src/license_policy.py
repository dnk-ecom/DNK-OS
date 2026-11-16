# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/license_policy.py"
# purpose: "Single source of truth for license classification and the allowed reuse action (ADOPT / ADAPT / CLEAN_ROOM) in dnk_git_research"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-06"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
License policy.

Replaces three diverging implementations (git_researcher.audit_and_classify,
DNAAssimilationEngine.audit_license, SOTAScoutEngine.audit_license_two_track).

Reuse actions:
  ADOPT       permissive / public domain: depend on it or copy with attribution.
  ADAPT       weak copyleft, or an UNVERIFIED permissive claim: study it and
              reimplement the pattern; do not copy files.
  CLEAN_ROOM  strong/network copyleft, restricted, or no license evidence
              (no license = all rights reserved): write from a mechanics spec
              only, never copy or link the code.

Evidence:
  spdx           an SPDX id was resolved (GitHub API, or an SPDX id in a catalog label)
  catalog_label  only a vague catalog track label such as "Track 1: Permissive"
  none           nothing usable
"""

from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class LicenseClass(str, Enum):
    PUBLIC_DOMAIN = "public_domain"
    PERMISSIVE = "permissive"
    WEAK_COPYLEFT = "weak_copyleft"
    STRONG_COPYLEFT = "strong_copyleft"
    NETWORK_COPYLEFT = "network_copyleft"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


class ReuseAction(str, Enum):
    ADOPT = "ADOPT"
    ADAPT = "ADAPT"
    CLEAN_ROOM = "CLEAN_ROOM"


_RANK = {
    LicenseClass.PUBLIC_DOMAIN: 0,
    LicenseClass.PERMISSIVE: 1,
    LicenseClass.WEAK_COPYLEFT: 2,
    LicenseClass.STRONG_COPYLEFT: 3,
    LicenseClass.NETWORK_COPYLEFT: 4,
    LicenseClass.RESTRICTED: 5,
    LicenseClass.UNKNOWN: 6,
}

_UNKNOWN_TOKENS = {
    "", "NONE", "NULL", "UNKNOWN", "UNSPECIFIED", "NOASSERTION", "OTHER",
    "MULTI-LICENSE", "N/A", "NO-LICENSE", "NOT-SPECIFIED",
}

_PERMISSIVE_EXACT = {
    "MIT", "ISC", "0BSD", "ZLIB", "BSL-1.0", "PYTHON-2.0", "PSF-2.0",
    "X11", "UNICODE-3.0", "BLUEOAK-1.0.0", "WTFPL",
}

_RESTRICTED_PREFIXES = (
    "BUSL", "ELASTIC", "SSPL", "POLYFORM", "COMMONS-CLAUSE", "OPENRAIL",
    "LLAMA", "CC-BY-NC", "CC-BY-ND",
)


class LicenseVerdict(BaseModel):
    raw: str
    spdx: Optional[str] = None
    license_class: LicenseClass
    action: ReuseAction
    can_depend: bool
    can_copy_code: bool
    evidence: str
    notes: List[str] = Field(default_factory=list)

    @property
    def verified(self) -> bool:
        return self.evidence == "spdx"


def _canon(token: str) -> str:
    t = re.sub(r"[\s_]+", "-", token.strip().upper())
    t = t.replace("-LICENSE", "").replace("-LICENCE", "")
    t = re.sub(r"-(ONLY|OR-LATER)$", "", t)
    return t.rstrip("+")


def _class_of(t: str) -> Optional[LicenseClass]:
    if t in _UNKNOWN_TOKENS:
        return None
    if t.startswith("AGPL"):
        return LicenseClass.NETWORK_COPYLEFT
    if t.startswith("LGPL"):
        return LicenseClass.WEAK_COPYLEFT
    if t.startswith(("GPL", "EUPL", "OSL", "CC-BY-SA")):
        return LicenseClass.STRONG_COPYLEFT
    if t.startswith(("MPL", "EPL", "CDDL", "CPL")):
        return LicenseClass.WEAK_COPYLEFT
    if t in ("UNLICENSE", "CC0-1.0", "CC0"):
        return LicenseClass.PUBLIC_DOMAIN
    if (
        t in ("UNLICENSED", "PROPRIETARY", "COMMERCIAL")
        or t.startswith(_RESTRICTED_PREFIXES)
        or "NONCOMMERCIAL" in t
        or "NON-COMMERCIAL" in t
        or t.endswith("-NC")
        or "-NC-" in t
    ):
        return LicenseClass.RESTRICTED
    if t in _PERMISSIVE_EXACT or t.startswith(("MIT-", "APACHE", "BSD")):
        return LicenseClass.PERMISSIVE
    return None


def _resolve(token: str) -> Optional[Tuple[LicenseClass, str]]:
    canon = _canon(token)
    cls = _class_of(canon)
    return (cls, canon) if cls is not None else None


def _eval_expr(expr: str) -> Optional[Tuple[LicenseClass, str]]:
    """Evaluate 'A OR B' (least restrictive wins) and 'A AND B' (most restrictive wins)."""
    cleaned = expr.replace("(", " ").replace(")", " ").strip()
    if not cleaned:
        return None
    options: List[Tuple[LicenseClass, str]] = []
    for part in re.split(r"\s+OR\s+|\s*/\s*", cleaned, flags=re.IGNORECASE):
        if not part.strip():
            continue
        resolved = [_resolve(p) for p in re.split(r"\s+AND\s+", part, flags=re.IGNORECASE) if p.strip()]
        if not resolved or any(r is None for r in resolved):
            continue
        options.append(max(resolved, key=lambda r: _RANK[r[0]]))  # type: ignore[index]
    if not options:
        return None
    return min(options, key=lambda r: _RANK[r[0]])


def _verdict(raw: str, cls: Optional[LicenseClass], spdx: Optional[str], evidence: str, notes: List[str]) -> LicenseVerdict:
    cls = cls or LicenseClass.UNKNOWN
    if evidence == "catalog_label" and cls == LicenseClass.PERMISSIVE:
        action, dep, copy = ReuseAction.ADAPT, False, False
        notes = notes + ["Ліцензію не підтверджено (лише мітка каталогу): копіювати код не можна, спершу перевір LICENSE."]
    elif cls in (LicenseClass.PERMISSIVE, LicenseClass.PUBLIC_DOMAIN):
        action, dep, copy = ReuseAction.ADOPT, True, True
        notes = notes + ["Копіювання дозволене із збереженням атрибуції та тексту ліцензії."]
    elif cls == LicenseClass.WEAK_COPYLEFT:
        action, dep, copy = ReuseAction.ADAPT, True, False
        notes = notes + ["Копілефт на рівні файлів: можна підключати без змін, файли не копіювати; патерни — переписувати."]
    elif cls == LicenseClass.NETWORK_COPYLEFT:
        action, dep, copy = ReuseAction.CLEAN_ROOM, False, False
        notes = notes + ["Мережевий копілефт (AGPL): навіть мережеве використання зобовʼязує відкрити код. Лише clean-room."]
    elif cls == LicenseClass.STRONG_COPYLEFT:
        action, dep, copy = ReuseAction.CLEAN_ROOM, False, False
        notes = notes + ["Сильний копілефт: не копіювати й не лінкувати в комерційний продукт. Лише clean-room."]
    elif cls == LicenseClass.RESTRICTED:
        action, dep, copy = ReuseAction.CLEAN_ROOM, False, False
        notes = notes + ["Обмежувальна ліцензія (комерційне використання може бути заборонене): лише clean-room."]
    else:
        action, dep, copy = ReuseAction.CLEAN_ROOM, False, False
        notes = notes + ["Немає доказів ліцензії: за замовчуванням усі права застережені. Лише clean-room."]
    return LicenseVerdict(
        raw=raw, spdx=spdx, license_class=cls, action=action,
        can_depend=dep, can_copy_code=copy, evidence=evidence, notes=notes,
    )


def classify_license(raw: Optional[str]) -> LicenseVerdict:
    """Classify a license string: SPDX id, SPDX expression, or a messy catalog track label."""
    original = "" if raw is None else str(raw)
    s = original.strip()

    if _canon(s) in _UNKNOWN_TOKENS:
        return _verdict(original, None, None, "none", [])

    if re.match(r"^\s*track\b", s, re.IGNORECASE):
        for m in re.finditer(r"[\[(]([^\])]+)[\])]", s):
            res = _eval_expr(m.group(1))
            if res:
                return _verdict(original, res[0], res[1], "spdx", ["SPDX взято з мітки каталогу."])
        low = s.lower()
        if "permissive" in low and not any(w in low for w in ("clean", "copyleft", "guard")):
            return _verdict(original, LicenseClass.PERMISSIVE, None, "catalog_label", [])
        return _verdict(original, None, None, "catalog_label", ["Мітка каталогу вказує на clean-room трек без SPDX."])

    res = _eval_expr(s)
    if res:
        return _verdict(original, res[0], res[1], "spdx", [])
    return _verdict(original, None, None, "none", [f"Нерозпізнана ліцензія: {original!r}."])
