#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_humanize.py"
# purpose: "Deterministic Ukrainian text humanizer, anti-slop scrubber, and change-rate gate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

"""Deterministic Ukrainian Anti-Slop Scrubber & Change-Rate Gate.

Executes three deterministic passes:
1. INVISIBLE: Strips zero-width spaces, word joiners, soft hyphens, BOMs, and normalizes special spaces.
2. TYPOGRAPHIC: Converts English curly quotes to Ukrainian «лапки», normalizes apostrophes for Ukrainian words,
   and fixes excessive em-dashes when requested.
3. LEXICAL: Replaces Ukrainian AI-slop phrases, translationese calques, and russianisms with natural Ukrainian
   equivalents while preserving URLs, numbers, and capitalization.
4. STRUCTURAL & CHANGE-RATE GATE: Flags structural tells and computes deterministic character/word change rate
   (warns > 30%, flags > 50% per im-not-ai over-edit guard).
"""

import argparse
import difflib
import json
import os
import re
import sys
import unicodedata
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEXICON = os.path.join(os.path.dirname(HERE), "references", "uk_slop_lexicon.json")

URL_RE = re.compile(r"https?://[^\s\"”»'<>]+|www\.[^\s\"”»'<>]+|\S+@\S+\.\S+")
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґA-Za-z0-9'’ʼ-]+")
UKR_APOSTROPHE_RE = re.compile(r"([БПВМФРЖЧШЩКХГҐбпвмфржчшщкхгґЗСзсДТдтНнЛл])['`ʼ]([яюєїЯЮЄЇ])")


def load_lexicon(path: str = DEFAULT_LEXICON) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cp(spec: str) -> Any:
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text: str) -> Tuple[str, List[str]]:
    found: List[str] = []

    def stash(m: re.Match) -> str:
        found.append(m.group(0))
        return f"\x00URL{len(found) - 1}\x00"

    return URL_RE.sub(stash, text), found


def restore_urls(text: str, found: List[str]) -> str:
    for i, url in enumerate(found):
        text = text.replace(f"\x00URL{i}\x00", url)
    return text


def pass_invisible(text: str, lex: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    hits: List[Dict[str, Any]] = []
    for entry in lex.get("invisible", []):
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({
                "name": f"{entry['cp']} {entry['name']}",
                "count": n,
                "action": entry["action"],
            })
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)

    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({
            "name": "other invisible format chars (Cf)",
            "count": len(stray),
            "action": "delete",
        })
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text, hits


def pass_typographic(text: str, lex: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    hits: List[Dict[str, Any]] = []
    for entry in lex.get("typographic", []):
        ch = entry["from"]
        n = text.count(ch)
        if not n:
            continue
        hits.append({
            "name": f"{ch} {entry['name']}",
            "count": n,
            "to": entry["to"],
        })
        text = text.replace(ch, entry["to"])

    # Convert straight double quotes wrapping Ukrainian words into «лапки»
    straight_quotes_re = re.compile(r'"([^"\n]+)"')
    sq_matches = straight_quotes_re.findall(text)
    if sq_matches:
        hits.append({
            "name": 'Straight double quotes "..." -> «...»',
            "count": len(sq_matches),
            "to": "«...»",
        })
        text = straight_quotes_re.sub(r"«\1»", text)

    # Normalize Ukrainian apostrophes to standard ’ (U+2019)
    ap_matches = UKR_APOSTROPHE_RE.findall(text)
    if ap_matches:
        hits.append({
            "name": "Ukrainian apostrophe normalization (' -> ’)",
            "count": len(ap_matches),
            "to": "’",
        })
        text = UKR_APOSTROPHE_RE.sub(r"\1’\2", text)

    return text, hits


def _match_case(src: str, repl: str) -> str:
    if not repl:
        return ""
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def _capitalize_after_sentence_start(text: str) -> str:
    """Ensure sentences remain capitalized if an opener phrase was stripped."""
    text = re.sub(r"([«(\[])\s+", r"\1", text)

    def cap_match(m: re.Match) -> str:
        prefix = m.group(1)
        ch = m.group(2)
        return prefix + ch.upper()

    text = re.sub(r"(^|[.!?]\s+|\n\s*|[«(\[])([а-яіїєґa-z])", cap_match, text)
    return text


def pass_lexical(text: str, lex: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    hits: List[Dict[str, Any]] = []
    entries = sorted(
        lex.get("phrases", []) + lex.get("words", []),
        key=lambda e: len(e["find"]),
        reverse=True,
    )
    for entry in entries:
        find = entry["find"]
        # Normalize apostrophes in pattern so both ' and ’ match
        escaped = re.escape(find).replace(r"\ ", r"\s+")
        escaped = escaped.replace(r"\'", "['’ʼ]").replace("’", "['’ʼ]")
        boundary_start = r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
        boundary_end = r"(?![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
        # If find ends with punctuation (like a comma), don't require word boundary after it
        if find[-1] in ",.;:!?":
            pattern = re.compile(boundary_start + escaped, re.IGNORECASE)
        else:
            pattern = re.compile(boundary_start + escaped + boundary_end, re.IGNORECASE)

        found = pattern.findall(text)
        if not found:
            continue
        hits.append({
            "find": find,
            "replace": entry["replace"] if entry["replace"] else "(видалено)",
            "count": len(found),
            "family": entry["family"],
        })
        text = pattern.sub(lambda m: _match_case(m.group(0), entry["replace"]), text)

    # Clean up whitespace & orphan commas after phrase deletion
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*[,.;:]\s*", "", text)
    text = re.sub(r"([.!?]\s+),\s*", r"\1", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"(?m)^[ \t]+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = _capitalize_after_sentence_start(text)
    return text, hits


def scan_structures(text: str, lex: Dict[str, Any]) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []
    for s in lex.get("structures", []):
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
            # For em-dash, only flag if density is high (> 1 per 100 words or >= 3 total)
            if s["id"] == "em-dash-overload" and len(found) < 3:
                continue
            flags.append({
                "id": s["id"],
                "name": s["name"],
                "count": len(found),
                "fix": s["fix"],
            })

    lens = [len(WORD_RE.findall(s)) for s in SENT_RE.findall(text) if len(WORD_RE.findall(s)) > 2]
    if len(lens) >= 4:
        mean = sum(lens) / len(lens)
        var = sum((n - mean) ** 2 for n in lens) / len(lens)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            flags.append({
                "id": "uniform-sentence-length",
                "name": f"Монотонна довжина речень (коефіцієнт варіації CV={cv:.2f} < 0.35)",
                "count": len(lens),
                "fix": "Чергуйте короткі ударні речення (3–6 слів) із розгорнутими (15–22 слова).",
            })
    return flags


def compute_change_rate(original: str, modified: str) -> Dict[str, Any]:
    """Compute deterministic change rate and enforce im-not-ai over-edit guard."""
    orig_clean = original.strip()
    mod_clean = modified.strip()
    if not orig_clean:
        return {"change_rate_pct": 0.0, "status": "OK"}
    ratio = difflib.SequenceMatcher(None, orig_clean, mod_clean).ratio()
    change_pct = round((1.0 - ratio) * 100.0, 1)
    if change_pct > 50.0:
        status = "HARD_STOP_OVER_EDIT"
    elif change_pct > 30.0:
        status = "WARNING_HIGH_EDIT"
    else:
        status = "OK"
    return {
        "change_rate_pct": change_pct,
        "status": status,
    }


def humanize_uk(text: str, lex: Dict[str, Any] | None = None) -> Tuple[str, Dict[str, Any]]:
    if lex is None:
        lex = load_lexicon()
    raw = text
    protected, urls = protect_urls(text)
    step1, inv = pass_invisible(protected, lex)
    step2, typo = pass_typographic(step1, lex)
    step3, lexi = pass_lexical(step2, lex)
    final_text = restore_urls(step3, urls).strip() + "\n"
    change_gate = compute_change_rate(raw, final_text)

    report = {
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "structures": scan_structures(final_text, lex),
        "change_gate": change_gate,
    }
    return final_text, report


def render_report(report: Dict[str, Any], out=sys.stderr) -> None:
    total = (
        sum(h["count"] for h in report["invisible"])
        + sum(h["count"] for h in report["typographic"])
        + sum(h["count"] for h in report["lexical"])
    )
    print("\nЗВІТ УКРАЇНСЬКОГО ГУМАНІЗАТОРА (UK HUMANIZE REPORT)", file=out)
    print("=" * 55, file=out)
    print(
        f"Виправлено автоматично: {total} маркерів | "
        f"Структурних попереджень: {len(report['structures'])} | "
        f"Change Rate: {report['change_gate']['change_rate_pct']}% ({report['change_gate']['status']})",
        file=out,
    )
    if report["invisible"]:
        print("\n1. НЕВИДИМІ СИМВОЛИ (Watermark / Format):", file=out)
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']} -> {h['action']}", file=out)
    if report["typographic"]:
        print("\n2. ТИПОГРАФІКА (Лапки та апострофи):", file=out)
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']} -> {h['to']}", file=out)
    if report["lexical"]:
        print("\n3. СЛОВНИК ШІ-ШТАМПІВ ТА КАЛЬОК:", file=out)
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  «{h['find']}» -> «{h['replace']}» [{h['family']}]", file=out)
    if report["structures"]:
        print("\n4. СТРУКТУРНІ МАРКЕРИ ШІ (потребують переписування речення):", file=out)
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        Порада: {h['fix']}", file=out)
    print("", file=out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Очищення українського тексту від ШІ-штампів та кальок.")
    ap.add_argument("input", nargs="?", default="-", help="Вхідний файл або - для stdin")
    ap.add_argument("-o", "--out", help="Файл для збереження результату")
    ap.add_argument("--report", action="store_true", help="Вивести детальний звіт у stderr")
    ap.add_argument("--json", action="store_true", help="Вивести результат і звіт у форматі JSON")
    ap.add_argument("--lexicon", default=DEFAULT_LEXICON, help="Шлях до uk_slop_lexicon.json")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    lex = load_lexicon(args.lexicon)
    clean, report = humanize_uk(raw, lex)

    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report)


if __name__ == "__main__":
    main()
