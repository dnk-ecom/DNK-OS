# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_humanize.py"
# purpose: "Deterministic bilingual (UK + EN) AI-slop scrubber, typographic normalizer, and change-rate gate."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

"""Deterministic Bilingual (Ukrainian + English) AI-Slop Scrubber & Typographic Normalizer.

Performs 4 deterministic passes on Ukrainian or English text:
1. Invisible Unicode watermark removal (U+200B..U+200F, U+FEFF, U+00AD, Tag chars).
2. Language-aware typography normalization:
   - UK: English curly quotes -> «ялинки», apostrophes -> ’ (U+2019).
   - EN: Curly smart quotes -> straight ASCII quotes.
3. Lexical slop & calque replacement (longest-match first, case-preserving).
4. Structural tell scanning + Change-Rate Gate (30% soft warning, 50% hard stop).
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.normpath(os.path.join(HERE, "..", "references"))
DEFAULT_LEXICON = os.path.join(REFERENCES_DIR, "uk_slop_lexicon.json")
EN_LEXICON = os.path.join(REFERENCES_DIR, "en_slop_lexicon.json")

URL_RE = re.compile(r"https?://\S+|www\.\S+")
SENT_RE = re.compile(r"[^.!?…]+[.!?…]+", re.UNICODE)
WORD_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґA-Za-z0-9'’ʼ-]+", re.UNICODE)
CYRILLIC_RE = re.compile(r"[А-ЯІЇЄҐа-яіїєґ]")
LATIN_RE = re.compile(r"[A-Za-z]")

INVISIBLE_DELETE = {
    "\u200b": "ZERO WIDTH SPACE (U+200B)",
    "\u200c": "ZERO WIDTH NON-JOINER (U+200C)",
    "\u200d": "ZERO WIDTH JOINER (U+200D)",
    "\u2060": "WORD JOINER (U+2060)",
    "\ufeff": "BOM / ZERO WIDTH NO-BREAK SPACE (U+FEFF)",
    "\u00ad": "SOFT HYPHEN (U+00AD)",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR (U+180E)",
    "\u061c": "ARABIC LETTER MARK (U+061C)",
    "\u200e": "LEFT-TO-RIGHT MARK (U+200E)",
    "\u200f": "RIGHT-TO-LEFT MARK (U+200F)",
}

INVISIBLE_SPACE = {
    "\u00a0": "NO-BREAK SPACE (U+00A0)",
    "\u202f": "NARROW NO-BREAK SPACE (U+202F)",
    "\u2009": "THIN SPACE (U+2009)",
    "\u2007": "FIGURE SPACE (U+2007)",
    "\u2003": "EM SPACE (U+2003)",
    "\u2002": "EN SPACE (U+2002)",
}

UKR_APOSTROPHE_RE = re.compile(
    r"([бпвмфгґкхжчшщрБПВМФГҐКХЖЧШЩР])['`*]([яюєїЯЮЄЇ])"
)


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


def protect_urls(text: str) -> Tuple[str, List[str]]:
    stash: List[str] = []

    def sub(m: re.Match) -> str:
        stash.append(m.group(0))
        return f"\x00URL{len(stash) - 1}\x00"

    return URL_RE.sub(sub, text), stash


def restore_urls(text: str, stash: List[str]) -> str:
    for idx, url in enumerate(stash):
        text = text.replace(f"\x00URL{idx}\x00", url)
    return text


def pass_invisible(text: str, lex: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    _ = lex
    hits: List[Dict[str, Any]] = []
    for ch, name in INVISIBLE_DELETE.items():
        cnt = text.count(ch)
        if cnt:
            hits.append({"name": name, "count": cnt, "action": "deleted"})
            text = text.replace(ch, "")

    tag_chars = [c for c in text if 0xE0000 <= ord(c) <= 0xE007F]
    if tag_chars:
        hits.append({
            "name": "TAG CHARACTERS U+E0000..U+E007F (ASCII smuggling)",
            "count": len(tag_chars),
            "action": "deleted",
        })
        text = "".join(c for c in text if not (0xE0000 <= ord(c) <= 0xE007F))

    for ch, name in INVISIBLE_SPACE.items():
        cnt = text.count(ch)
        if cnt:
            hits.append({"name": name, "count": cnt, "action": "-> ASCII space"})
            text = text.replace(ch, " ")

    return text, hits


def pass_typographic(text: str, lex: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    hits: List[Dict[str, Any]] = []
    lang = lex.get("language", "uk")
    for rule in lex.get("typographic", []):
        cnt = text.count(rule["from"])
        if cnt:
            hits.append({"name": rule["name"], "count": cnt, "to": rule["to"]})
            text = text.replace(rule["from"], rule["to"])

    if lang == "uk":
        # Convert straight ASCII double quotes wrapping text into Ukrainian «guillemets»
        straight_quotes_re = re.compile(r'"([^"\n]{1,140})"')
        sq_matches = straight_quotes_re.findall(text)
        if sq_matches:
            hits.append({
                "name": 'STRAIGHT DOUBLE QUOTES ("..." -> «...»)',
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
    lang = lex.get("language", "uk")
    deleted_label = "(deleted)" if lang == "en" else "(видалено)"
    entries = sorted(
        lex.get("phrases", []) + lex.get("words", []),
        key=lambda e: len(e["find"]),
        reverse=True,
    )
    for entry in entries:
        find = entry["find"]
        escaped = re.escape(find).replace(r"\ ", r"\s+")
        escaped = escaped.replace(r"\'", "['’ʼ]").replace("’", "['’ʼ]")
        boundary_start = r"(?<![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
        boundary_end = r"(?![А-ЯІЇЄҐа-яіїєґA-Za-z0-9])"
        if find[-1] in ",.;:!?":
            pattern = re.compile(boundary_start + escaped, re.IGNORECASE)
        else:
            pattern = re.compile(boundary_start + escaped + boundary_end, re.IGNORECASE)

        found = pattern.findall(text)
        if not found:
            continue
        hits.append({
            "find": find,
            "replace": entry["replace"] if entry["replace"] else deleted_label,
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
    lang = lex.get("language", "uk")
    for s in lex.get("structures", []):
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
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
            if lang == "en":
                flags.append({
                    "id": "uniform-sentence-length",
                    "name": f"Monotonous sentence length (CV={cv:.2f} < 0.35)",
                    "count": len(lens),
                    "fix": "Mix short punchy sentences (3-6 words) with longer clauses (15-22 words).",
                })
            else:
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


def humanize_text(
    text: str,
    lex: Dict[str, Any] | None = None,
    lang: str = "auto",
) -> Tuple[str, Dict[str, Any]]:
    resolved_lang = detect_language(text) if lang == "auto" else lang
    if lex is None:
        lex = load_lexicon(lang=resolved_lang)
    raw = text
    protected, urls = protect_urls(text)
    step1, inv = pass_invisible(protected, lex)
    step2, typo = pass_typographic(step1, lex)
    step3, lexi = pass_lexical(step2, lex)
    final_text = restore_urls(step3, urls).strip() + "\n"
    change_gate = compute_change_rate(raw, final_text)

    report = {
        "language": lex.get("language", resolved_lang),
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "structures": scan_structures(final_text, lex),
        "change_gate": change_gate,
    }
    return final_text, report


def humanize_uk(text: str, lex: Dict[str, Any] | None = None) -> Tuple[str, Dict[str, Any]]:
    """Backwards-compatible entry point for Ukrainian or explicitly supplied lexicon."""
    if lex is not None:
        return humanize_text(text, lex=lex, lang=lex.get("language", "uk"))
    return humanize_text(text, lex=None, lang="uk")


def render_report(report: Dict[str, Any], out=sys.stderr) -> None:
    lang = report.get("language", "uk")
    total = (
        sum(h["count"] for h in report["invisible"])
        + sum(h["count"] for h in report["typographic"])
        + sum(h["count"] for h in report["lexical"])
    )
    if lang == "en":
        print("\nDNK OS HUMANIZE REPORT (EN)", file=out)
        print("=" * 55, file=out)
        print(
            f"Auto-scrubbed: {total} markers | "
            f"Structural warnings: {len(report['structures'])} | "
            f"Change Rate: {report['change_gate']['change_rate_pct']}% ({report['change_gate']['status']})",
            file=out,
        )
    else:
        print("\nЗВІТ УКРАЇНСЬКОГО ГУМАНІЗАТОРА (UK HUMANIZE REPORT)", file=out)
        print("=" * 55, file=out)
        print(
            f"Виправлено автоматично: {total} маркерів | "
            f"Структурних попереджень: {len(report['structures'])} | "
            f"Change Rate: {report['change_gate']['change_rate_pct']}% ({report['change_gate']['status']})",
            file=out,
        )
    if report["invisible"]:
        hdr = "\n1. INVISIBLE CHARACTERS (Watermarks):" if lang == "en" else "\n1. НЕВИДИМІ СИМВОЛИ (Watermark / Format):"
        print(hdr, file=out)
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']} -> {h['action']}", file=out)
    if report["typographic"]:
        hdr = "\n2. TYPOGRAPHY (Quotes & Apostrophes):" if lang == "en" else "\n2. ТИПОГРАФІКА (Лапки та апострофи):"
        print(hdr, file=out)
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']} -> {h['to']}", file=out)
    if report["lexical"]:
        hdr = "\n3. AI SLOP & CLICHES:" if lang == "en" else "\n3. СЛОВНИК ШІ-ШТАМПІВ ТА КАЛЬОК:"
        print(hdr, file=out)
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  «{h['find']}» -> «{h['replace']}» [{h['family']}]", file=out)
    if report["structures"]:
        hdr = "\n4. STRUCTURAL AI TELLS (require rewrite):" if lang == "en" else "\n4. СТРУКТУРНІ МАРКЕРИ ШІ (потребують переписування речення):"
        tip_lbl = "Fix" if lang == "en" else "Порада"
        print(hdr, file=out)
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        {tip_lbl}: {h['fix']}", file=out)
    print("", file=out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Bilingual (UK + EN) AI-slop scrubber and normalizer.")
    ap.add_argument("input", nargs="?", default="-", help="Input file or - for stdin")
    ap.add_argument("-o", "--out", help="Output file path")
    ap.add_argument("--lang", choices=["auto", "uk", "en"], default="auto", help="Language mode (default: auto)")
    ap.add_argument("--report", action="store_true", help="Print detailed report to stderr")
    ap.add_argument("--json", action="store_true", help="Output JSON with text and report")
    ap.add_argument("--lexicon", default=None, help="Custom path to lexicon JSON")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    resolved_lang = detect_language(raw) if args.lang == "auto" else args.lang
    lex = load_lexicon(args.lexicon, lang=resolved_lang)
    clean, report = humanize_text(raw, lex=lex, lang=resolved_lang)

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
