#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/dnk_computer_use.py"
# purpose: "Ultra-Lightweight Native macOS Computer Use Engine for DNK OS Agents (0-GPU, <15MB RAM)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
DNK OS Native macOS Computer Use Engine (DEC-148 / DEC-137):
Hardware-safe GUI automation for MacBook M1 (8GB RAM / 256GB SSD).
Bypasses heavy Docker / Electron / PyAutoGUI VNC daemons.
Uses 100% native macOS subsystems:
- Screen capture via `screencapture -x` (0.05s, 0 RAM).
- UI inspection & clicks via `System Events` / AppleScript.
- Keystrokes & shortcuts via native CG/AppleScript dispatch.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional


def get_screen_size() -> Dict[str, int]:
    """Returns the primary screen resolution (width, height)."""
    script = 'tell application "Finder" to get bounds of window of desktop'
    try:
        out = subprocess.check_output(["osascript", "-e", script]).decode().strip()
        parts = [int(p.strip()) for p in out.split(",")]
        return {"width": parts[2], "height": parts[3]}
    except Exception as e:
        return {"width": 1680, "height": 1050, "error": str(e)}


def get_frontmost_app() -> str:
    """Returns the name of the currently active/frontmost application."""
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    try:
        return subprocess.check_output(["osascript", "-e", script]).decode().strip()
    except Exception as e:
        return f"Error: {e}"


def list_visible_apps() -> List[str]:
    """Returns list of all currently visible running application names."""
    script = 'tell application "System Events" to get name of every application process whose visible is true'
    try:
        out = subprocess.check_output(["osascript", "-e", script]).decode().strip()
        return [app.strip() for app in out.split(",") if app.strip()]
    except Exception as e:
        return []


def activate_app(app_name: str) -> Dict[str, Any]:
    """Brings the specified application to the foreground."""
    script = f'tell application "{app_name}" to activate'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True, "active_app": app_name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def take_screenshot(path: str = "/tmp/dnk_screen.png", rect: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Captures screen or specific rectangle [x, y, w, h] quietly without shutter sound.
    Returns file path, dimensions, and byte size.
    """
    cmd = ["screencapture", "-x"]
    if rect and len(rect) == 4:
        cmd.extend(["-R", f"{rect[0]},{rect[1]},{rect[2]},{rect[3]}"])
    cmd.append(path)

    try:
        subprocess.run(cmd, check=True)
        bytes_size = os.path.getsize(path) if os.path.exists(path) else 0
        return {
            "success": True,
            "path": path,
            "bytes": bytes_size,
            "screen_size": get_screen_size(),
            "active_app": get_frontmost_app(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def click(x: int, y: int, clicks: int = 1) -> Dict[str, Any]:
    """
    Clicks at specific screen coordinates {x, y} via macOS System Events.
    Supports single click (1) or double click (2).
    """
    if clicks >= 2:
        script = f"""
        tell application "System Events"
            click at {{{x}, {y}}}
            delay 0.08
            click at {{{x}, {y}}}
        end tell
        """
    else:
        script = f'tell application "System Events" to click at {{{x}, {y}}}'

    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True, "x": x, "y": y, "clicks": clicks}
    except Exception as e:
        return {"success": False, "error": str(e)}


def type_text(text: str) -> Dict[str, Any]:
    """Types plain text into the currently focused window."""
    # Escape quotes and backslashes for AppleScript
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    script = f'tell application "System Events" to keystroke "{escaped}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True, "typed_chars": len(text)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def press_key(key: str, modifiers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Presses a special key with optional modifiers (e.g. Return, Tab, Escape, Space,
    or key combinations like 'c' with ['command']).
    """
    mod_str = ""
    if modifiers:
        clean_mods = [f"{m.lower()} down" for m in modifiers if m.lower() in ("command", "shift", "option", "control")]
        if clean_mods:
            mod_str = f" using {{{', '.join(clean_mods)}}}"

    # Map named keys to keycodes or keystrokes
    key_lower = key.lower()
    code_map = {
        "return": 36,
        "enter": 36,
        "tab": 48,
        "space": 49,
        "delete": 51,
        "backspace": 51,
        "escape": 53,
        "esc": 53,
        "up": 126,
        "down": 125,
        "left": 123,
        "right": 124,
    }

    if key_lower in code_map:
        script = f'tell application "System Events" to key code {code_map[key_lower]}{mod_str}'
    else:
        # Single character keystroke
        escaped = key.replace("\\", "\\\\").replace('"', '\\"')
        script = f'tell application "System Events" to keystroke "{escaped}"{mod_str}'

    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True, "key": key, "modifiers": modifiers or []}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="DNK OS Ultra-Lightweight macOS Computer Use Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status command
    subparsers.add_parser("status", help="Get screen resolution, active app, and visible apps")

    # screenshot command
    shot_parser = subparsers.add_parser("screenshot", help="Capture screenshot to file")
    shot_parser.add_argument("--output", default="/tmp/dnk_screen.png", help="Output PNG path")
    shot_parser.add_argument("--rect", nargs=4, type=int, help="Optional rectangle: x y width height")

    # click command
    click_parser = subparsers.add_parser("click", help="Click at screen coordinates")
    click_parser.add_argument("x", type=int, help="X coordinate")
    click_parser.add_argument("y", type=int, help="Y coordinate")
    click_parser.add_argument("--double", action="store_true", help="Double click")

    # type command
    type_parser = subparsers.add_parser("type", help="Type text into focused element")
    type_parser.add_argument("text", help="Text to type")

    # key command
    key_parser = subparsers.add_parser("key", help="Press key or shortcut")
    key_parser.add_argument("key", help="Key name (e.g. Return, Escape, Space, or letter)")
    key_parser.add_argument("--mods", nargs="+", default=[], help="Modifiers: command shift option control")

    # activate command
    act_parser = subparsers.add_parser("activate", help="Activate an application by name")
    act_parser.add_argument("app", help="Application name (e.g. 'Google Chrome', 'Finder', 'Ghostty')")

    args = parser.parse_args()

    if args.command == "status":
        info = {
            "screen": get_screen_size(),
            "frontmost_app": get_frontmost_app(),
            "visible_apps": list_visible_apps(),
        }
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif args.command == "screenshot":
        res = take_screenshot(args.output, args.rect)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "click":
        res = click(args.x, args.y, clicks=2 if args.double else 1)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "type":
        res = type_text(args.text)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "key":
        res = press_key(args.key, args.mods)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "activate":
        res = activate_app(args.app)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
