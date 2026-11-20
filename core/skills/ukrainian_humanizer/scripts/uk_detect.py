# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_detect.py"
# purpose: "5-check bilingual (UK + EN) AI prose detector (BURSTINESS, SPECIFICITY, SLOP DENSITY, FINGERPRINT, VOICE)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

"""Bilingual (Ukrainian + English) AI Prose Detector (5-Check Scoring Panel).

Scores text on 5 orthogonal signals (0-100, higher = more human):
- BURSTINESS: Coefficient of variation of sentence lengths.
- SPECIFICITY: Numbers, dates, currencies, capitalized proper nouns.
- SLOP DENSITY: Density of AI clichés and calques per 100 words.
- FINGERPRINT: Invisible watermarks, excess em-dashes, foreign quotes.
- VOICE: Personal pronouns vs passive voice + structural AI tells.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.normpath(os.path.join(HERE, "..", "references"))
DEFAULT_LEXICON = os.path.join(REFERENCES_DIR, "uk_slop_lexicon.json")
EN_LEXICON = os.path.join(REFERENCES_DIR, "en_slop_lexicon.json")

SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[А-ЯІЇЄҐA-Z«\"'(0-9—-])")
WORD_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґA-Za-z0-9'’ʼ-]+", re.UNICODE)
CYRILLIC_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґ]")
LATIN_RE = re.compile(r"[A-Za-z]")

PRONOUNS_UK = re.compile(
    r"(?i)\b(я|ми|ти|ви|мій|моя|моє|мої|наш|наша|наше|наші|ваш|ваша|ваше|ваші|мені|нам|вам|мною|нами)\b"
)
PASSIVE_UK = re.compile(
    r"(?i)\b(було\s+\w+(?:но|то)|буде\s+\w+(?:но|то)|здійснюється|забезпечується|виконується|проводиться|реалізується|пропонується|гарантується|створюється|використовується)\b"
)

PRONOUNS_EN = re.compile(
    r"(?i)\b(i|we|you|my|our|your|me|us|myself|ourselves)\b"
)
PASSIVE_EN = re.compile(
    r"(?i)\b(was|were|is|are|been|being)\s+(created|developed|designed|implemented|achieved|established|conducted|utilized|leveraged|performed|made|built|provided|ensured)\b"
)

CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def detect_language(text: str) -> str:
    """Auto-detect language ('uk' or 'en') based on Cyrillic vs Latin character ratio."""
    cyr = len(CYRILLIC_RE.findall(text))
    lat = len(LATIN_RE.findall(text))
    if lat > cyr and cyr < max(3, int(lat * 0.25)):
        return "en"
    return "uk"


def load_lexicon(path: str | None = None, lang: str = "uk") -> Dict[str, Any]:
    if path is None:
        path = EN_LEXICON if lang == "en" else DEFAULT_LEXICON
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def scale(val: float, human: float, machine: float) -> float:
    if human == machine:
        return 50.0
    t = (val - machine) / (human - machine)
    return clamp(t * 100.0)


def sentences(text: str) -> List[str]:
    flat = re.sub(r"\s+", " ", text.strip())
    return [s for s in SENT_SPLIT.split(flat) if len(WORD_RE.findall(s)) >= 2]


def words(text: str) -> List[str]:
    return WORD_RE.findall(text)


def check_burstiness(text: str, lang: str = "uk") -> Tuple[float, str]:
    sents = sentences(text)
    lens = [len(words(s)) for s in sents]
    if len(lens) < 3:
        msg = "too few sentences (<3)" if lang == "en" else "замало речень для оцінки (<3)"
        return 60.0, msg
    mean = statistics.mean(lens)
    sd = statistics.pstdev(lens)
    cv = sd / mean if mean else 0.0
    score = scale(cv, human=0.52, machine=0.18)
    if min(lens) <= 6 and max(lens) >= 18:
        score = clamp(score + 10.0)
    if lang == "en":
        detail = f"CV={cv:.2f}, avg={mean:.1f} words, range={min(lens)}..{max(lens)} ({len(lens)} sents)"
    else:
        detail = f"CV={cv:.2f}, сер.={mean:.1f} слів, розмах={min(lens)}..{max(lens)} ({len(lens)} реч.)"
    return score, detail


def check_specificity(text: str, lang: str = "uk") -> Tuple[float, str]:
    w = words(text)
    if len(w) < 15:
        msg = "text too short for specificity check" if lang == "en" else "текст закороткий для оцінки конкретики"
        return 65.0, msg
    nums = re.findall(r"\b\d[\d.,:%₴$€/-]*\b", text)
    if lang == "en":
        units = re.findall(
            r"(?i)\b(?:usd|eur|uah|gbp|kg|g|mm|cm|m|km|hours?|days?|months?|years?|sec|min|ms|gb|mb|%|pcs)\b",
            text,
        )
    else:
        units = re.findall(
            r"(?i)\b(?:грн|₴|usd|\$|€|кг|г|мм|см|м|км|год|хв|дн\w*|міс\w*|рок\w*|шт|відсотк\w*|%)\b",
            text,
        )
    sents = sentences(text)
    proper = 0
    for s in sents:
        sw = words(s)
        for token in sw[1:]:
            if len(token) > 2 and token[0].isupper() and not token.isupper():
                proper += 1
    quotes = len(re.findall(r"«[^»]{3,120}»|\"[^\"]{3,120}\"", text))
    anchors = len(nums) + len(units) + proper * 0.6 + quotes * 1.5
    density = anchors * 100.0 / len(w)
    score = scale(density, human=5.5, machine=0.4)
    if lang == "en":
        detail = f"{len(nums)} numbers, {len(units)} units, {proper} proper nouns ({density:.1f}/100 words)"
    else:
        detail = f"{len(nums)} чисел, {len(units)} од. виміру, {proper} власних назв ({density:.1f}/100 слів)"
    return score, detail


def check_slop(text: str, lex: Dict[str, Any]) -> Tuple[float, str]:
    w = words(text)
    lang = lex.get("language", "uk")
    if not w:
        return 100.0, "empty" if lang == "en" else "порожньо"
    hits = 0
    found: List[str] = []
    for entry in lex.get("phrases", []) + lex.get("words", []):
        find = entry["find"]
        escaped = re.escape(find).replace(r"\ ", r"\s+").replace(r"\'", "['’ʼ]").replace("’", "['’ʼ]")
        boundary_start = r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
        boundary_end = r"(?![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
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
    if lang == "en":
        detail = f"{hits} AI clichés/slop ({density:.1f} per 100 words)"
    else:
        detail = f"{hits} ШІ-штампів/кальок ({density:.1f} на 100 слів)"
    if found:
        detail += " [" + ", ".join(found[:4]) + (", ..." if len(found) > 4 else "") + "]"
    return score, detail


def check_fingerprint(text: str, lang: str = "uk") -> Tuple[float, str]:
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    eng_curly = sum(text.count(c) for c in "“”„")
    nbsp = sum(text.count(c) for c in "\u00a0\u202f\u2009")
    excess_em = max(0, em - max(1, len(text) // 250))
    quote_penalty = eng_curly * 2 if lang == "uk" else eng_curly
    total = invisible * 5 + excess_em * 2 + quote_penalty + nbsp
    per1k = total * 1000.0 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    if lang == "en":
        detail = f"{invisible} invisible Cf, {em} em-dashes (excess: {excess_em}), {eng_curly} curly quotes"
    else:
        detail = f"{invisible} невидимих Cf, {em} тире (надлишок: {excess_em}), {eng_curly} англ. лапок"
    return score, detail


def check_voice(text: str, lex: Dict[str, Any]) -> Tuple[float, str]:
    w = words(text)
    lang = lex.get("language", "uk")
    if len(w) < 15:
        msg = "text too short for voice check" if lang == "en" else "текст закороткий для оцінки голосу"
        return 65.0, msg
    per100 = 100.0 / len(w)
    if lang == "en":
        person_density = len(PRONOUNS_EN.findall(text)) * per100
        passive_density = len(PASSIVE_EN.findall(text)) * per100
    else:
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

    if lang == "en":
        detail = (
            f"pronouns: {person_density:.1f}/100, passive: {passive_density:.1f}/100, "
            f"structural tells: {tells}"
        )
    else:
        detail = (
            f"займенники: {person_density:.1f}/100, пасив: {passive_density:.1f}/100, "
            f"структурні кліше: {tells}"
        )
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


def evaluate_text(
    text: str,
    lex: Dict[str, Any] | None = None,
    lang: str = "auto",
) -> Dict[str, Any]:
    resolved_lang = detect_language(text) if lang == "auto" else lang
    active_lex: Dict[str, Any] = lex if lex is not None else load_lexicon(lang=resolved_lang)
    lex_lang = active_lex.get("language", resolved_lang)
    results = {
        "BURSTINESS": check_burstiness(text, lang=lex_lang),
        "SPECIFICITY": check_specificity(text, lang=lex_lang),
        "SLOP DENSITY": check_slop(text, active_lex),
        "FINGERPRINT": check_fingerprint(text, lang=lex_lang),
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
        "language": lex_lang,
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
    lang = eval_data.get("language", "uk")
    if lang == "en":
        base_title = "DNK OS AI DETECTION PANEL (EN)"
    else:
        base_title = "ПАНЕЛЬ ДЕТЕКЦІЇ ШІ-МАРКЕРІВ (UK AI DETECTION PANEL)"
    title = base_title + (f" — {label}" if label else "")
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
        if lang == "en":
            print(f"\n  Weakest signal: {eval_data['weakest_signal']}. Address this first.", file=out)
        else:
            print(f"\n  Найслабший сигнал: {eval_data['weakest_signal']}. Виправте його насамперед.", file=out)
    print("", file=out)


def main() -> None:
    ap = argparse.ArgumentParser(description="5-check bilingual (UK + EN) AI prose detector.")
    ap.add_argument("input", nargs="?", default="-", help="File or - for stdin")
    ap.add_argument("compare", nargs="?", help="Second file for Before/After delta comparison")
    ap.add_argument("--lang", choices=["auto", "uk", "en"], default="auto", help="Language mode (default: auto)")
    ap.add_argument("--json", action="store_true", help="Output result as JSON")
    ap.add_argument("--lexicon", default=None, help="Custom path to lexicon JSON")
    args = ap.parse_args()

    read_fn = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read_fn(args.input))]
    if args.compare:
        targets.append((args.compare, read_fn(args.compare)))

    payload = []
    for name, text in targets:
        resolved_lang = detect_language(text) if args.lang == "auto" else args.lang
        lex = load_lexicon(args.lexicon, lang=resolved_lang)
        res = evaluate_text(text, lex=lex, lang=resolved_lang)
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
            f"  DELTA: {a['human_score']:.1f} ({a['verdict']})  ->  "
            f"{b['human_score']:.1f} ({b['verdict']})   [{delta:+.1f} pts]\n"
        )

    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
