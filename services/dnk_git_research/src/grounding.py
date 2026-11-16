# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/src/grounding.py"
# purpose: "Grounding pack: turns gate + ledger + (optional) reuse brief into the block that makes an agent reproduce proven mechanics instead of averaged guesses; records outcomes for measurement"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-07"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---

"""
Pack = what the agent must know BEFORE writing code for a specific task:
  1. Is research needed at all (gate)? Simple tasks get an empty pack and no ceremony.
  2. Where will the code live and run (ledger: module, environments, constraints).
  3. Which proven mechanics apply, from where (donor@sha, file:lines), and HOW they may be used
     (license decides: copy / adapt / clean-room / idea only).
  4. What is already taken, rejected or still unverified, so nothing is done twice or invented.

Everything here is deterministic and offline except the optional reuse brief passed in by the caller.
Outcomes of tasks run with and without a pack are appended to a JSONL file so the benefit is measured,
not assumed.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, Field

from services.dnk_git_research.src.ledger import Ledger, _overlap, _tokens, render_context
from services.dnk_git_research.src.license_policy import classify_license
from services.dnk_git_research.src.task_gate import GateDecision, GateMode, TaskSpec, decide

_HOW = {
    "adopt": "Можна взяти код як є; збережи ліцензійний заголовок і вкажи джерело.",
    "adapt": "Можна адаптувати код; збережи ліцензійні умови донора і вкажи джерело.",
    "clean_room": "Чисте відтворення: пиши за описом нижче, не копіюй код донора й не відкривай його під час написання.",
    "idea": "Бери ідею і порядок кроків, код пиши власний під наш стек.",
    "reference": "Лише довідка: не переноси механіку без окремого рішення.",
}
_ACTIVE = ("candidate", "planned", "in_progress")
MIN_OVERLAP = 2


class PackMechanic(BaseModel):
    assimilation: str
    donor: str
    pinned: str = ""
    license: str = ""
    what: str
    cite: str = ""
    method: str
    how: str
    status: str
    gap: str = ""
    module: str = ""
    score: int = 0


class Pack(BaseModel):
    pack_id: str
    mode: str                                   # SKIP | RESEARCH
    task: str
    module: str = ""
    gate: Dict[str, Any] = Field(default_factory=dict)
    mechanics: List[PackMechanic] = Field(default_factory=list)
    taken: List[str] = Field(default_factory=list)
    rejected: List[str] = Field(default_factory=list)
    unverified: List[str] = Field(default_factory=list)
    markdown: str = ""
    grounded: bool = False                      # at least one verified mechanic found for this task
    generated_at: str = ""


def _infer_module(led: Ledger, tk: set) -> str:
    best = max(((_overlap(tk, _tokens(" ".join(g.terms) + " " + g.need)), g.module) for g in led.gaps if g.status == "open"),
               key=lambda x: x[0], default=(0, ""))
    return best[1] if best[0] >= MIN_OVERLAP else ""


def build_pack(task: str, led: Ledger, module: str = "", target_files: Sequence[str] = (), tags: Sequence[str] = (),
               force: bool = False, brief: Any = None) -> Pack:
    spec = TaskSpec(text=task, target_files=list(target_files), tags=list(tags))
    gate: GateDecision = decide(spec, force=force)
    pid = hashlib.sha1((gate.fingerprint + "|" + module).encode()).hexdigest()[:12]
    now = datetime.now(timezone.utc).isoformat()
    tk0 = _tokens(task)
    if gate.mode == GateMode.SKIP and not {t.lower() for t in tags} & {"skip_research", "no_research"}:
        hit = max(((_overlap(tk0, _tokens(" ".join(g.terms) + " " + g.need)), g) for g in led.gaps if g.status == "open"),
                  key=lambda x: x[0], default=(0, None))
        if hit[0] >= MIN_OVERLAP + 1:       # the ledger knows this is something DNK lacks: the keyword gate is not the last word
            gate = gate.model_copy(update={"mode": GateMode.RESEARCH, "score": gate.threshold,
                                           "reasons": gate.reasons + [f"відкрита прогалина реєстру {hit[1].id}"]})
    if gate.mode == GateMode.SKIP:
        md = "## Обґрунтування\nЗадача проста або повторювана: пошук не потрібен. Пиши за наявними патернами проєкту.\n"
        return Pack(pack_id=pid, mode="SKIP", task=task, gate=gate.model_dump(mode="json"), markdown=md, generated_at=now)

    tk = _tokens(task)
    module = module or _infer_module(led, tk)
    mechs: List[PackMechanic] = []
    taken: List[str] = []
    rejected: List[str] = []
    unverified: List[str] = []
    for d in led.donors:
        for a in d.assimilations:
            sc = _overlap(tk, _tokens(a.what + " " + a.notes))
            gap = next((g for g in led.gaps if g.id == a.gap), None)
            if gap:
                sc += _overlap(tk, _tokens(" ".join(gap.terms)))
            if sc < MIN_OVERLAP or (module and a.module and a.module != module):
                continue
            if a.status == "rejected":
                rejected.append(f"{a.what} ← {d.id}: {a.notes}")
            elif a.status in ("done", "in_progress"):
                taken.append(f"{a.what} ← {d.id} → {a.dnk_path or a.module}")
            elif a.status in _ACTIVE:
                method = a.method
                if method in ("adopt", "adapt") and not classify_license(d.license).can_copy_code:
                    method = "idea"                 # a stale record must never widen what the license allows
                mechs.append(PackMechanic(assimilation=a.id, donor=d.id, pinned=d.pinned, license=d.license, what=a.what,
                                          cite=a.donor_cite, method=method, how=_HOW.get(method, ""), status=a.status,
                                          gap=a.gap, module=a.module or module, score=sc))
            if a.notes and ("не прочитано" in a.notes.lower() or "не читан" in a.notes.lower()):
                unverified.append(f"{a.id}: {a.notes}")
    mechs.sort(key=lambda m: -m.score)
    indexed = [d.id for d in led.donors if d.level == "indexed" and module and module in d.target_hint][:8]

    L = ["## Обґрунтування (пакет)", f"Пошук потрібен: {'; '.join(gate.reasons)}."]
    ctx = render_context(led, module)
    L.append(ctx)
    if mechs:
        L.append("### Перевірені механіки для цієї задачі (відтвори їх, а не вигадуй усереднене)")
        for i, m in enumerate(mechs, 1):
            L.append(f"{i}. **{m.what}**\n   - джерело: `{m.donor}` @ `{m.pinned}`, ліцензія {m.license or 'невідома'}"
                     + (f"; доказ: `{m.cite}`" if m.cite else "") + f"\n   - як користуватись: {m.how}"
                     + (f"\n   - закриває прогалину `{m.gap}`" if m.gap else ""))
    else:
        L.append("### Перевірених механік для цієї задачі в реєстрі немає\nНе вигадуй посилання на джерела. Якщо потрібна світова практика, "
                 "зроби `dossier prepare <репозиторій> --focus … --claim …` і додай результат у реєстр.")
    if taken:
        L.append("### Вже реалізовано (використай, не дублюй)\n" + "\n".join(f"- {t}" for t in taken))
    if rejected:
        L.append("### Відхилено (не пропонуй знову)\n" + "\n".join(f"- {t}" for t in rejected))
    if unverified:
        L.append("### Не доведено (перевір сам перед використанням)\n" + "\n".join(f"- {t}" for t in unverified))
    if indexed:
        L.append("### Заявлені, але не перевірені донори (лише підказка де шукати)\n" + ", ".join(indexed))
    if brief is not None and getattr(brief, "needs", None):
        L.append("### Кандидати з пошуку (не досьє, не доведено)")
        for n in brief.needs:
            for c in n.candidates[:3]:
                L.append(f"- {c.repo_id} [{c.action.value}] ({n.need})")
    L.append("### Правила виконання\n"
             "- У коді залиш коментар з джерелом кожної перенесеної механіки: `donor@sha шлях:рядки`.\n"
             "- Дотримуйся обмежень середовища вище; не імпортуй з core/apps/інших сервісів у services/.\n"
             "- Напиши тест, який перевіряє саме перенесену механіку (ліміт, збій, повторюваність), а не лише щасливий шлях.\n"
             "- Якщо механіки немає в пакеті, скажи про це прямо, а не вигадуй джерело.")
    return Pack(pack_id=pid, mode="RESEARCH", task=task, module=module, gate=gate.model_dump(mode="json"), mechanics=mechs,
                taken=taken, rejected=rejected, unverified=unverified, markdown="\n\n".join(L) + "\n",
                grounded=bool(mechs), generated_at=now)


# ----------------------------------------------------------------------------- measurement
def feedback_path() -> Path:
    base = os.environ.get("DNK_GIT_RESEARCH_STATE_DIR")
    return (Path(base) if base else Path(__file__).resolve().parents[3] / ".data" / "dnk_git_research") / "pack_feedback.jsonl"


def record_outcome(pack_id: str, task_id: str, arm: str, first_pass: bool, fixes: int = 0, notes: str = "",
                   path: Optional[Path] = None) -> Dict[str, Any]:
    if arm not in ("with_pack", "without_pack"):
        raise ValueError("arm must be with_pack or without_pack")
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "pack_id": pack_id, "task_id": task_id, "arm": arm,
           "first_pass": bool(first_pass), "fixes": int(fixes), "notes": notes}
    p = path or feedback_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def report(path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or feedback_path()
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []
    out: Dict[str, Any] = {}
    for arm in ("with_pack", "without_pack"):
        r = [x for x in rows if x["arm"] == arm]
        out[arm] = {"runs": len(r), "first_pass": sum(1 for x in r if x["first_pass"]),
                    "first_pass_rate": round(sum(1 for x in r if x["first_pass"]) / len(r), 2) if r else None,
                    "avg_fixes": round(sum(x["fixes"] for x in r) / len(r), 2) if r else None}
    out["note"] = "Мало запусків: різниця не доведена." if min(out["with_pack"]["runs"], out["without_pack"]["runs"]) < 5 else ""
    return out
