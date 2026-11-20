# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/hydrate_quarantined_services.py"
# purpose: "Autonomous Hydration, Clone & Bootstrap Engine for Quarantined GPL/External Services (DEC-048, DEC-070)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dnk.vibe.hydrator")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class QuarantinedServiceSpec:
    def __init__(self, manifest_path: Path, data: Dict[str, Any]):
        self.manifest_path = manifest_path
        self.plugin_id = data.get("metadata", {}).get("service_id", manifest_path.parent.name)
        spec = data.get("spec", {})
        q = spec.get("quarantine", {})
        self.service_name = q.get("service_name", self.plugin_id)
        self.license = q.get("license", "GPL-3.0")
        self.repo_url = q.get("repo_url")
        target_dir_rel = q.get("target_dir", f"../DNK_Vibe/{self.service_name}")
        self.target_dir = (WORKSPACE_ROOT / target_dir_rel).resolve()
        self.bootstrap_command = q.get("bootstrap_command", "uv sync")
        self.verify_command = q.get("verify_command")
        self.documentation_url = q.get("documentation_url", "")


def discover_quarantined_services() -> List[QuarantinedServiceSpec]:
    """Finds all plugins with a declarative quarantine spec."""
    services: List[QuarantinedServiceSpec] = []
    plugins_dir = WORKSPACE_ROOT / "packages" / "plugins"
    if not plugins_dir.exists():
        return services

    for manifest_path in plugins_dir.glob("*/service_manifest.yaml"):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "spec" in data and "quarantine" in data["spec"]:
                services.append(QuarantinedServiceSpec(manifest_path, data))
        except Exception as e:
            logger.warning(f"Failed parsing manifest {manifest_path}: {e}")

    return services


def run_cmd(command_str: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Executes a shell command cleanly inside a target directory."""
    return subprocess.run(
        command_str,
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=180,
    )


def hydrate_service(svc: QuarantinedServiceSpec, check_only: bool = False) -> bool:
    """Clones, bootstraps and verifies an isolated quarantined service."""
    print(f"\n=======================================================")
    print(f"📦 Service: {svc.service_name} (License: {svc.license})")
    print(f"   Target Dir: {svc.target_dir}")
    print(f"   Upstream:   {svc.repo_url or 'Local'}")
    print(f"=======================================================")

    # 1. Existence Check
    is_present = svc.target_dir.exists() and (svc.target_dir / ".git").exists()
    if check_only:
        if not is_present:
            print(f"   ✗ Missing repository in {svc.target_dir}")
            return False
        print(f"   ✓ Repository present.")
    else:
        if not is_present:
            if not svc.repo_url:
                print(f"   ✗ Target missing and no repo_url specified.")
                return False
            print(f"   ⬇️ Cloning repository ({svc.repo_url}) into {svc.target_dir}...")
            svc.target_dir.parent.mkdir(parents=True, exist_ok=True)
            clone_cmd = f"git clone --depth 1 {svc.repo_url} {svc.target_dir}"
            res = run_cmd(clone_cmd, WORKSPACE_ROOT)
            if res.returncode != 0:
                print(f"   ✗ Git clone failed:\n{res.stderr}")
                return False
            print(f"   ✓ Clone successful.")
        else:
            print(f"   ✓ Repository already cloned.")

        # 2. Bootstrap Dependencies
        if svc.bootstrap_command:
            print(f"   ⚙️ Running bootstrap: '{svc.bootstrap_command}'...")
            res = run_cmd(svc.bootstrap_command, svc.target_dir)
            if res.returncode != 0:
                print(f"   ✗ Bootstrap failed:\n{res.stderr}")
                return False
            print(f"   ✓ Bootstrap completed successfully.")

    # 3. Verification Command
    if svc.verify_command:
        print(f"   🧪 Running health check: '{svc.verify_command}'...")
        res = run_cmd(svc.verify_command, svc.target_dir)
        if res.returncode != 0:
            print(f"   ✗ Verification failed:\n{res.stderr}")
            return False
        print(f"   ✓ Health check passed (Exit Code 0).")

    print(f"   🟢 STATUS: {svc.service_name} is HYDRATED & OPERATIONAL")
    return True


def main():
    parser = argparse.ArgumentParser(description="Hydrate and verify quarantined external services.")
    parser.add_argument("--check-only", action="store_true", help="Only check status without cloning or installing")
    parser.add_argument("--service", type=str, help="Target specific service by name")
    args = parser.parse_args()

    services = discover_quarantined_services()
    if not services:
        print("No quarantined services declared in packages/plugins/*/service_manifest.yaml.")
        sys.exit(0)

    if args.service:
        services = [s for s in services if s.service_name.lower() == args.service.lower()]
        if not services:
            print(f"Service '{args.service}' not found.")
            sys.exit(1)

    print(f"🔍 Discovered {len(services)} quarantined service(s). Starting processing...")
    successes = 0
    for svc in services:
        ok = hydrate_service(svc, check_only=args.check_only)
        if ok:
            successes += 1

    print("\n-------------------------------------------------------")
    print(f"📊 Summary: {successes}/{len(services)} services ready.")
    print("-------------------------------------------------------")

    if successes != len(services):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
