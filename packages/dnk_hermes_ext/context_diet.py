#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/context_diet.py"
# purpose: "Merge context_diet.yaml into a Hermes config.yaml (default ~/.hermes/config.yaml) with a timestamped backup; prints only changed keys, never values of other sections."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-08"
# author: "DNK-e.com Maksym & Claude"
# --- END DNK-MRH-HEADER ---
"""Usage: python context_diet.py [--config PATH] [--dry-run]

Run with the Hermes venv python (needs PyYAML). Only keys present in
context_diet.yaml are touched; providers, keys and everything else stay as is.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

import yaml

DIET = Path(__file__).with_name("context_diet.yaml")
UNION_LISTS = {("agent", "disabled_toolsets")}


def merge(dst: dict, src: dict, path: tuple = (), changes: list | None = None) -> list:
    changes = [] if changes is None else changes
    for key, val in src.items():
        here = path + (key,)
        if isinstance(val, dict):
            node = dst.get(key)
            if not isinstance(node, dict):
                node = {}
                dst[key] = node
            merge(node, val, here, changes)
        elif here in UNION_LISTS:
            old = list(dst.get(key) or [])
            new = old + [v for v in val if v not in old]
            if new != old:
                changes.append((".".join(here), old, new))
                dst[key] = new
        elif dst.get(key) != val:
            changes.append((".".join(here), dst.get(key), val))
            dst[key] = val
    return changes


def main() -> int:
    ap = argparse.ArgumentParser()
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    ap.add_argument("--config", type=Path, default=home / "config.yaml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg_path: Path = args.config
    if not cfg_path.exists():
        print(f"❌ {cfg_path} не знайдено", file=sys.stderr)
        return 2
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    diet = yaml.safe_load(DIET.read_text(encoding="utf-8"))

    changes = merge(cfg, diet)
    if not changes:
        print("✅ Вже застосовано, змін немає.")
        return 0
    for key, old, new in changes:
        print(f"  {key}: {old!r} -> {new!r}")
    if args.dry_run:
        print("(dry-run: файл не змінено)")
        return 0

    backup = cfg_path.with_name(f"{cfg_path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(cfg_path, backup)
    cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"✅ Застосовано {len(changes)} змін. Резервна копія: {backup}")
    print("   Перезапусти Герича (gerych23), щоб налаштування підхопились.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
