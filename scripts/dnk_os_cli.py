#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/dnk_os_cli.py"
# purpose: "Unified Sovereign Cockpit CLI for DNK OS Vibe-Coder and Autonomous Swarm."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import json
import os
import sys
from pathlib import Path

# Self-healing runtime re-exec to ~/.dnk_runtime/venv if needed
try:
    import yaml
    import pydantic
except ImportError:
    venv_py = Path.home() / ".dnk_runtime" / "venv" / "bin" / "python"
    if venv_py.exists() and sys.executable != str(venv_py):
        os.execv(str(venv_py), [str(venv_py)] + sys.argv)
    else:
        print("❌ Error: PyYAML and Pydantic are required. Please run inside ~/.dnk_runtime/venv.")
        sys.exit(1)

# Ensure DNK_OS root is in sys.path
DNK_OS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DNK_OS_ROOT))

from core.bricks.registry import DNKBrickRegistry
from core.registry.port_manager import port_manager
from core.sentinel.process_sentinel import process_sentinel
from core.sentinel.hygiene_guard import hygiene_guard
from core.bus.agent_bus import agent_bus
from core.config.settings import settings


def cmd_status(args):
    """Displays an ADHD-compliant 1-screen operational status card."""
    registry = DNKBrickRegistry()
    bricks = registry.list_bricks()
    ports_status = port_manager.audit_status()
    hygiene = hygiene_guard.full_hygiene_check()

    print("\n" + "=" * 65)
    print("🧬  DNK OS — SOVEREIGN AGENTIC CONTROL CENTER")
    print("=" * 65)
    print(f"  ● Status:          ONLINE (FastMCP Core Gateway v1.0.0)")
    print(f"  ● Environment:     {settings.env} (Debug: {settings.debug})")
    print(f"  ● Root Directory:  {settings.root_dir.name}/ (Portable relative)")
    print(f"  ● Runtime:         Python {sys.version.split()[0]} (Shared ~/.dnk_runtime)")
    print("-" * 65)
    print(f"📦  COMPOSABLE BRICKS: {len(bricks)} Mounted")
    for b in sorted(bricks, key=lambda x: x.id):
        print(f"    ├─ [{b.id}] {b.name} ({b.category})")
    print("-" * 65)
    print(f"🌐  PORT GOVERNANCE: {ports_status['currently_listening']} Listening / {ports_status['total_registered']} Registered")
    for p in ports_status["active_services"]:
        print(f"    ├─ Port :{p['port']:<5} -> {p['service_name']} (PID: {p['pid']})")
    print("-" * 65)
    print("🛡️  PORTABILITY & HYGIENE INVARIANTS:")
    top_ok = "PASS (0 leaks)" if hygiene["top_level_audit"]["status"] == "PASS" else "FAIL"
    path_ok = "PASS (0 absolute paths)" if hygiene["absolute_path_audit"]["status"] == "PASS" else "FAIL"
    print(f"    ├─ Canonical 8-Root Dirs:   {top_ok}")
    print(f"    ├─ Zero Hardcoded Paths:    {path_ok}")
    print(f"    └─ Shared Runtime Stores:   {'READY (~/.dnk_runtime)' if hygiene['runtime_audit']['dnk_runtime_exists'] else 'MISSING'}")
    print("=" * 65 + "\n")


def cmd_brick(args):
    registry = DNKBrickRegistry()
    if args.subcommand == "list" or not args.subcommand:
        bricks = registry.list_bricks()
        print(f"\n📦 Registered Bricks ({len(bricks)}):")
        print("-" * 75)
        for b in sorted(bricks, key=lambda x: x.id):
            print(f"• {b.id:<25} v{b.version:<6} [{b.category}]")
            print(f"  {b.description}")
            if b.dependencies.internal:
                print(f"  Internal Deps: {b.dependencies.internal}")
            if b.dependencies.external_python:
                print(f"  Python Deps:   {b.dependencies.external_python}")
            print("-" * 75)
    elif args.subcommand == "resolve":
        if not args.brick_ids:
            print("❌ Error: Specify brick IDs to resolve. E.g.: dnk-os brick resolve brick_01_agentic_brain brick_04_shopify_engine")
            sys.exit(1)
        resolved = registry.resolve_dependencies(args.brick_ids)
        py_deps = registry.get_lean_python_dependencies(args.brick_ids)
        print(f"\n🔗 Topological Resolution DAG:")
        for idx, b_id in enumerate(resolved, 1):
            print(f"  {idx}. {b_id}")
        print(f"\n📦 Lean Python Requirements:")
        for d in py_deps:
            print(f"  - {d}")


def cmd_port(args):
    if args.subcommand == "list" or not args.subcommand:
        ports = port_manager.list_registered_ports()
        print("\n🌐 DNK OS Port Registry & Listener Table:")
        print("-" * 80)
        print(f"{'PORT':<8} {'STATUS':<12} {'PID':<8} {'ROLE':<12} {'SERVICE'}")
        print("-" * 80)
        for p in ports:
            pid_str = str(p['pid']) if p['pid'] else "-"
            status_symbol = "🟢 LISTEN" if p['status'] == "LISTENING" else "⚪ FREE"
            print(f"{p['port']:<8} {status_symbol:<12} {pid_str:<8} {p['role']:<12} {p['service_name']}")
        print("-" * 80)
    elif args.subcommand == "free":
        if not args.target_port:
            print("❌ Error: Specify port number to free. E.g.: dnk-os port free 8000")
            sys.exit(1)
        killed = port_manager.kill_process_on_port(args.target_port, force=args.force)
        if killed:
            print(f"✅ Process on port {args.target_port} terminated successfully.")
        else:
            print(f"ℹ️ No active process listening on port {args.target_port}.")


def cmd_clean(args):
    print("🧹 Running DNK OS Process & Filesystem Hygiene Sweep...")
    reaped = process_sentinel.reap_zombies()
    print(f"  ● Reaped zombie dev processes: {reaped}")

    cleaned_files = 0
    for root, dirs, files in os.walk(DNK_OS_ROOT):
        for f in files:
            if f == ".DS_Store":
                try:
                    os.remove(os.path.join(root, f))
                    cleaned_files += 1
                except Exception:
                    pass
    print(f"  ● Cleaned junk files (.DS_Store): {cleaned_files}")
    print("✅ Hygiene sweep completed.")


def cmd_verify(args):
    print("🛡️ Executing 100% Portability & Hygiene Gate...")
    hygiene = hygiene_guard.full_hygiene_check()

    fail = False
    if hygiene["top_level_audit"]["status"] != "PASS":
        print(f"❌ Violation: Unsanctioned top-level folders: {hygiene['top_level_audit']['violations']}")
        fail = True
    else:
        print("  ✓ Canonical 8-Root directories verified")

    if hygiene["absolute_path_audit"]["status"] != "PASS":
        print(f"❌ Violation: Absolute path leaks detected: {hygiene['absolute_path_audit']['leaks']}")
        fail = True
    else:
        print("  ✓ Pure manifests verified (Zero hardcoded /Users/... paths)")

    if not hygiene["runtime_audit"]["dnk_runtime_exists"]:
        print("⚠️ Warning: ~/.dnk_runtime not found. Run scripts/system/setup_mac_agent_workspace.sh to link shared runtime.")
    else:
        print("  ✓ Shared Zero-Duplicate runtime verified")

    if fail:
        print("\n❌ Portability Gate: REJECTED")
        sys.exit(1)
    else:
        print("\n✅ Portability Gate: 100% COMPLIANT & VERIFIED")


def main():
    parser = argparse.ArgumentParser(
        prog="dnk-os",
        description="DNK OS Sovereign Cockpit CLI for Vibe-Coder & Autonomous Swarm"
    )
    subparsers = parser.add_subparsers(dest="command")

    # status
    p_status = subparsers.add_parser("status", help="Display 1-screen status dashboard")

    # brick
    p_brick = subparsers.add_parser("brick", help="Inspect and manage LEGO bricks")
    p_brick.add_argument("subcommand", nargs="?", default="list", choices=["list", "resolve"])
    p_brick.add_argument("brick_ids", nargs="*", help="Brick IDs for resolution")

    # port
    p_port = subparsers.add_parser("port", help="Port registry and sentinel")
    p_port.add_argument("subcommand", nargs="?", default="list", choices=["list", "free"])
    p_port.add_argument("target_port", nargs="?", type=int, help="Target port number")
    p_port.add_argument("-f", "--force", action="store_true", help="Force SIGKILL")

    # clean
    p_clean = subparsers.add_parser("clean", help="Prune zombie processes and temporary artifacts")

    # verify
    p_verify = subparsers.add_parser("verify", help="Run 100%% Portability & Hygiene Gate")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        cmd_status(args)
    elif args.command == "brick":
        cmd_brick(args)
    elif args.command == "port":
        cmd_port(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "verify":
        cmd_verify(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
