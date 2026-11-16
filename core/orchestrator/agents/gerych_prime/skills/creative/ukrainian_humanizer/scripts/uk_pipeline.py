#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/uk_pipeline.py"
# purpose: "One-command Ukrainian Humanizer + 5-Check Detector CLI & macOS Clipboard helper."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

"""One-command runner for Ukrainian text humanizing and AI-slop scoring.

Usage:
  .venv/bin/python3 core/skills/ukrainian_humanizer/scripts/uk_pipeline.py --text "Ваш текст..."
  .venv/bin/python3 core/skills/ukrainian_humanizer/scripts/uk_pipeline.py draft.txt
  .venv/bin/python3 core/skills/ukrainian_humanizer/scripts/uk_pipeline.py --clipboard
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.skills.ukrainian_humanizer.scripts.uk_detect import evaluate_text, load_lexicon, render_panel  # noqa: E402
from core.skills.ukrainian_humanizer.scripts.uk_humanize import humanize_uk, render_report  # noqa: E402


def read_clipboard() -> str:
    return subprocess.check_output(["pbpaste"], text=True)


def write_clipboard(text: str) -> None:
    proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
    proc.communicate(input=text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Єдиний CLI-конвеєр Українського Гуманізатора (Детектор + Авто-очистка).")
    parser.add_argument("input", nargs="?", help="Шлях до файлу з текстом")
    parser.add_argument("--text", "-t", help="Передати текст напряму в лапках")
    parser.add_argument("--clipboard", "-c", action="store_true", help="Взяти текст із буфера обміну macOS (pbpaste) і записати очищений назад (pbcopy)")
    parser.add_argument("--output", "-o", help="Зберегти очищений текст у файл")
    args = parser.parse_args()

    if args.text:
        raw = args.text
        source_label = "Рядок з аргументу --text"
    elif args.clipboard:
        raw = read_clipboard()
        source_label = "Буфер обміну macOS (Clipboard)"
    elif args.input:
        with open(args.input, encoding="utf-8") as fh:
            raw = fh.read()
        source_label = args.input
    else:
        if sys.stdin.isatty():
            parser.print_help()
            return 1
        raw = sys.stdin.read()
        source_label = "stdin"

    if not raw.strip():
        print("Помилка: вхідний текст порожній.", file=sys.stderr)
        return 1

    lex = load_lexicon()
    before_eval = evaluate_text(raw, lex)
    cleaned, report = humanize_uk(raw, lex)
    after_eval = evaluate_text(cleaned, lex)

    render_panel(before_eval, label=f"1. ДО ОЧИЩЕННЯ ({source_label})", out=sys.stdout)
    render_report(report, out=sys.stdout)
    render_panel(after_eval, label="2. ПІСЛЯ АВТО-СКРАБЕРА", out=sys.stdout)
    print("3. ОЧИЩЕНИЙ ТЕКСТ:")
    print("-" * 66)
    print(cleaned.strip())
    print("-" * 66)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(cleaned)
        print(f"\n[Збережено у файл: {args.output}]")

    if args.clipboard:
        write_clipboard(cleaned)
        print("\n[Очищений текст скопійовано назад у буфер обміну macOS (Cmd+V)]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
