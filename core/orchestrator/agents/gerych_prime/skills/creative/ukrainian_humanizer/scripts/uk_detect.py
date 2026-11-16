#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_detect.py"
# purpose: "Five-check Ukrainian AI-slop & translationese detection panel with route_hint classification."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

"""Ukrainian Five-Check AI Detection Panel & Route Classifier.

Evaluates Ukrainian text across 5 deterministic dimensions (0-100, higher is more human):
1. BURSTINESS: Sentence-length variation (CV of word counts across sentences).
2. SPECIFICITY: Density of concrete markers (numbers, percentages, units, capitalized proper nouns).
3. SLOP DENSITY: Frequency of Ukrainian AI stock phrases, calques, and russianisms from uk_slop_lexicon.json.
4. FINGERPRINT: Invisible Unicode watermarks, English curly quotes, and excessive em-dashes per 1,000 chars.
5. VOICE & ACTIVE SYNTAX: Ratio of direct personal pronouns & active verbs vs bureaucratic passive (-ться / було -но)
   and structural AI tells.

Emits:
- human_score (0-100): 60% mean + 40% weakest check (detector-realistic bottleneck weighting).
- verdict: PASS (overall >= 70 and min >= 55) | REVIEW (overall >= 50) | FLAGGED (< 50).
- route_hint: light | standard | heavy (assimilated from epoko77-ai/im-not-ai).
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEXICON = os.path.join(os.path.dirname(HERE), "references", "uk_slop_lexicon.json")

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґA-Za-z0-9'’ʼ-]+")
PRONOUNS_UK = re.compile(
    r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z])(я|ми|ти|ви|мій|моя|моє|мої|наш|наша|наше|наші|ваш|ваша|ваше|ваші|мені|нам|вам|тобі)(?![А-ЯІЇЄҐа-яіїєґA-Za-z])",
    re.IGNORECASE,
)
PASSIVE_UK = re.compile(
    r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z])(було\s+\w+(?:но|то)|буде\s+\w+(?:но|то)|\w+ється|\w+ються)(?![А-ЯІЇЄҐа-яіїєґA-Za-z])",
    re.IGNORECASE,
)
NUMBERS_UNITS_UK = re.compile(
    r"\b\d[\d,.\s]*%?\b|\b\d+\s*(?:грн|₴|\$|€|мм|см|м|км|г|кг|мл|л|год|хв|сек|дн|шт|р\.|років)\b",
    re.IGNORECASE,
)
PROPER_UK = re.compile(r"(?<![.!?]\s)(?<!^)(?<!\n)\b[А-ЯІЇЄҐA-Z][а-яіїєґa-z'’ʼ]{2,}\b")

CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def load_lexicon(path: str = DEFAULT_LEXICON) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def clamp(n: float) -> float:
    return max(0.0, min(100.0, n))


def scale(value: float, human: float, machine: float) -> float:
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100.0)


def sentences(text: str) -> List[str]:
    return [s.strip() for s in SENT_RE.findall(text) if len(WORD_RE.findall(s)) > 2]


def words(text: str) -> List[str]:
    return WORD_RE.findall(text)


def check_burstiness(text: str) -> Tuple[float, str]:
    sents = sentences(text)
    lens = [len(WORD_RE.findall(s)) for s in sents]
    if len(lens) < 4:
        return 65.0, f"замало речень ({len(lens)}) для оцінки дисперсії"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0.0
    score = scale(cv, human=0.65, machine=0.20)
    return score, f"варіативність CV={cv:.2f} на {len(lens)} реченнях (норма людини: 0.45+)"


def check_specificity(text: str) -> Tuple[float, str]:
    w = words(text)
    if len(w) < 15:
        return 65.0, "текст закороткий для оцінки конкретики"
    per100 = 100.0 / len(w)
    num_hits = len(NUMBERS_UNITS_UK.findall(text))
    proper_hits = len(set(PROPER_UK.findall(text)))
    hits = num_hits + proper_hits
    density = hits * per100
    score = scale(density, human=5.5, machine=0.4)
    return score, f"{hits} маркерів конкретики ({density:.1f} на 100 слів; ціль: 3.5+)"


def check_slop(text: str, lex: Dict[str, Any]) -> Tuple[float, str]:
    w = words(text)
    if not w:
        return 50.0, "порожній текст"
    hits = 0
    found: List[str] = []
    boundary_start = r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
    boundary_end = r"(?![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
    for entry in lex.get("phrases", []) + lex.get("words", []):
        find = entry["find"]
        escaped = re.escape(find).replace(r"\ ", r"\s+").replace(r"\'", "['’ʼ]").replace("’", "['’ʼ]")
        if find[-1] in ",.;:!?":
            pattern = re.compile(boundary_start + escaped, re.IGNORECASE)
        else:
            pattern = re.compile(boundary_start + escaped + boundary_end, re.IGNORECASE)
        n = len(pattern.findall(text))
        if n:
            hits += n
            found.append(find)
    density = hits * 100.0 / len(w)
    score = scale(density, human=0.0, machine=4.5)
    detail = f"{hits} ШІ-штампів/кальок ({density:.1f} на 100 слів)"
    if found:
        detail += " [" + ", ".join(found[:4]) + (", ..." if len(found) > 4 else "") + "]"
    return score, detail


def check_fingerprint(text: str) -> Tuple[float, str]:
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    eng_curly = sum(text.count(c) for c in "“”„")
    nbsp = sum(text.count(c) for c in "\u00a0\u202f\u2009")
    # In Ukrainian, 1 em-dash per ~250 chars is normal; penalize excess em-dashes above baseline
    excess_em = max(0, em - max(1, len(text) // 250))
    total = invisible * 5 + excess_em * 2 + eng_curly * 2 + nbsp
    per1k = total * 1000.0 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = f"{invisible} невидимих Cf, {em} тире (надлишок: {excess_em}), {eng_curly} англ. лапок"
    return score, detail


def check_voice(text: str, lex: Dict[str, Any]) -> Tuple[float, str]:
    w = words(text)
    if len(w) < 15:
        return 65.0, "текст закороткий для оцінки голосу"
    per100 = 100.0 / len(w)
    person_density = len(PRONOUNS_UK.findall(text)) * per100
    passive_density = len(PASSIVE_UK.findall(text)) * per100

    tells = 0
    names: List[str] = []
    for s in lex.get("structures", []):
        if s["id"] == "em-dash-overload":
            continue
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])

    bullets = [len(WORD_RE.findall(b)) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform_bullets = len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6

    person_score = scale(person_density, human=3.5, machine=0.0)
    active_score = scale(passive_density, human=0.5, machine=5.0)
    struct_score = clamp(100.0 - tells * 22.0)

    score = person_score * 0.30 + active_score * 0.35 + struct_score * 0.35
    if uniform_bullets:
        score -= 12.0
        names.append("uniform-bullets")

    detail = (
        f"займенники: {person_density:.1f}/100, пасив: {passive_density:.1f}/100, "
        f"структурні кліше: {tells}"
    )
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


def evaluate_text(text: str, lex: Dict[str, Any] | None = None) -> Dict[str, Any]:
    active_lex: Dict[str, Any] = lex if lex is not None else load_lexicon()
    results = {
        "BURSTINESS": check_burstiness(text),
        "SPECIFICITY": check_specificity(text),
        "SLOP DENSITY": check_slop(text, active_lex),
        "FINGERPRINT": check_fingerprint(text),
        "VOICE": check_voice(text, active_lex),
    }
    scores = [results[c][0] for c in CHECKS]
    overall = round(statistics.mean(scores) * 0.6 + min(scores) * 0.4, 1)
    min_score = round(min(scores), 1)
    weakest = min(CHECKS, key=lambda c: results[c][0])

    if overall >= 70.0 and min_score >= 55.0:
        verdict = "PASS"
        route_hint = "light"
    elif overall >= 50.0:
        verdict = "REVIEW"
        route_hint = "standard"
    else:
        verdict = "FLAGGED"
        route_hint = "heavy"

    return {
        "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
        "human_score": overall,
        "min_score": min_score,
        "weakest_signal": weakest,
        "verdict": verdict,
        "route_hint": route_hint,
    }


def bar(score: float, width: int = 24) -> str:
    filled = round(score / 100.0 * width)
    return "#" * filled + "." * (width - filled)


def render_panel(eval_data: Dict[str, Any], label: str | None = None, out=sys.stdout) -> None:
    title = "ПАНЕЛЬ ДЕТЕКЦІЇ ШІ-МАРКЕРІВ (UK AI DETECTION PANEL)" + (f" — {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 66), file=out)
    for name in CHECKS:
        c = eval_data["checks"][name]
        print(f"  {name:<13} {bar(c['score'])} {c['score']:5.1f}", file=out)
        print(f"  {'':<13} {c['detail']}", file=out)
    print("-" * 66, file=out)
    print(
        f"  {'HUMAN SCORE':<13} {bar(eval_data['human_score'])} {eval_data['human_score']:5.1f}   "
        f"{eval_data['verdict']} (route: {eval_data['route_hint']})",
        file=out,
    )
    if eval_data["verdict"] != "PASS":
        print(f"\n  Найслабший сигнал: {eval_data['weakest_signal']}. Виправте його насамперед.", file=out)
    print("", file=out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Оцінка українського тексту за 5 критеріями природності.")
    ap.add_argument("input", nargs="?", default="-", help="Файл або - для stdin")
    ap.add_argument("compare", nargs="?", help="Другий файл для порівняння До/Після")
    ap.add_argument("--json", action="store_true", help="Вивести результат у JSON")
    ap.add_argument("--lexicon", default=DEFAULT_LEXICON, help="Шлях до uk_slop_lexicon.json")
    args = ap.parse_args()

    lex = load_lexicon(args.lexicon)
    read_fn = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read_fn(args.input))]
    if args.compare:
        targets.append((args.compare, read_fn(args.compare)))

    payload = []
    for name, text in targets:
        res = evaluate_text(text, lex)
        res["source"] = name
        payload.append(res)

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for p in payload:
        render_panel(p, label=os.path.basename(p["source"]) if args.compare else None)

    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(
            f"  ДЕЛЬТА: {a['human_score']:.1f} ({a['verdict']})  ->  "
            f"{b['human_score']:.1f} ({b['verdict']})   [{delta:+.1f} балів]\n"
        )

    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
