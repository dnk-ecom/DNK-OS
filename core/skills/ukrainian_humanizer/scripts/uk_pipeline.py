# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_pipeline.py"
# purpose: "One-command bilingual (UK + EN) CLI & macOS Clipboard pipeline combining uk_humanize.py and uk_detect.py."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

"""One-Command Bilingual (Ukrainian + English) Humanizer Pipeline (CLI + macOS Clipboard).

Usage:
  # Process text directly from macOS clipboard (pbpaste -> humanize -> pbcopy)
  python core/skills/ukrainian_humanizer/scripts/uk_pipeline.py --clipboard

  # Process a file and print Before/After 5-Check Score Delta (auto-detects UK or EN)
  python core/skills/ukrainian_humanizer/scripts/uk_pipeline.py input.txt -o clean.txt

  # Explicit English mode
  python core/skills/ukrainian_humanizer/scripts/uk_pipeline.py input_en.txt --lang en
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import uk_detect  # noqa: E402
import uk_humanize  # noqa: E402


def read_clipboard() -> str:
    res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
    return res.stdout


def write_clipboard(text: str) -> None:
    subprocess.run(["pbcopy"], input=text, text=True, check=True)


def run_pipeline(
    raw_text: str,
    lexicon_path: str | None = None,
    lang: str = "auto",
) -> dict:
    resolved_lang = uk_humanize.detect_language(raw_text) if lang == "auto" else lang
    lex = uk_humanize.load_lexicon(lexicon_path, lang=resolved_lang)
    before_eval = uk_detect.evaluate_text(raw_text, lex=lex, lang=resolved_lang)
    clean_text, scrub_report = uk_humanize.humanize_text(raw_text, lex=lex, lang=resolved_lang)
    after_eval = uk_detect.evaluate_text(clean_text, lex=lex, lang=resolved_lang)
    delta = round(after_eval["human_score"] - before_eval["human_score"], 1)
    return {
        "language": resolved_lang,
        "clean_text": clean_text,
        "scrub_report": scrub_report,
        "before": before_eval,
        "after": after_eval,
        "delta": delta,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="One-command Bilingual (UK + EN) Humanizer + Detector Pipeline.")
    ap.add_argument("input", nargs="?", default="-", help="Input file or - for stdin")
    ap.add_argument("-o", "--out", help="Output file path")
    ap.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Read from macOS clipboard (pbpaste) and write cleaned text back (pbcopy)",
    )
    ap.add_argument("--lang", choices=["auto", "uk", "en"], default="auto", help="Language mode (default: auto)")
    ap.add_argument("--json", action="store_true", help="Output full pipeline result as JSON")
    ap.add_argument("--quiet", action="store_true", help="Only output cleaned text (no diagnostic panel)")
    ap.add_argument("--lexicon", default=None, help="Custom path to lexicon JSON")
    args = ap.parse_args()

    if args.clipboard:
        raw = read_clipboard()
        if not raw.strip():
            print("Помилка / Error: буфер обміну порожній (Clipboard is empty).", file=sys.stderr)
            sys.exit(1)
    elif args.input == "-":
        raw = sys.stdin.read()
    else:
        with open(args.input, encoding="utf-8") as fh:
            raw = fh.read()

    result = run_pipeline(raw, args.lexicon, lang=args.lang)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.clipboard:
        write_clipboard(result["clean_text"])
    elif args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(result["clean_text"])
    else:
        sys.stdout.write(result["clean_text"])

    if not args.quiet:
        lang = result["language"]
        uk_humanize.render_report(result["scrub_report"], out=sys.stderr)
        lbl_before = "BEFORE" if lang == "en" else "ДО ОЧИЩЕННЯ (BEFORE)"
        lbl_after = "AFTER PASS 1" if lang == "en" else "ПІСЛЯ ДЕ-СЛОПУ (AFTER PASS 1)"
        uk_detect.render_panel(result["before"], label=lbl_before, out=sys.stderr)
        uk_detect.render_panel(result["after"], label=lbl_after, out=sys.stderr)
        print(
            f"  SCORE DELTA ({lang.upper()}): {result['before']['human_score']:.1f} ({result['before']['verdict']})  ->  "
            f"{result['after']['human_score']:.1f} ({result['after']['verdict']})   "
            f"[{result['delta']:+.1f} pts]\n",
            file=sys.stderr,
        )
        if args.clipboard:
            msg = (
                "  [OK] Cleaned text copied to macOS clipboard (Cmd+V)!\n"
                if lang == "en"
                else "  [OK] Очищений текст автоматично скопійовано у буфер обміну (Cmd+V)!\n"
            )
            print(msg, file=sys.stderr)


if __name__ == "__main__":
    main()
