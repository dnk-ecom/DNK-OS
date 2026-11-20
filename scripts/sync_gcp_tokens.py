#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/sync_gcp_tokens.py"
# purpose: "Autonomous Google Cloud OAuth2 token synchronizer & SOTA Workhorse Model Suite for DNK OS."
# canonical_source: true
# alters_files: ["~/.zettcode/config.toml", "DNK_OS/config/config.toml", "~/.hermes/vertex_token.txt"]
# triggers_tasks: []
# status: "Active"
# version: "4.0.0"
# updated_at: "2026-11-02"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_ACCOUNT = "devagent.dnk@gmail.com"
DEFAULT_PROJECT = "project-2826e39f-abdc-4c1d-8b5"

def run_cmd(cmd: list[str]) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def get_active_account() -> str:
    acc = run_cmd(["gcloud", "config", "get-value", "account"])
    return acc or DEFAULT_ACCOUNT

def get_active_project() -> str:
    proj = run_cmd(["gcloud", "config", "get-value", "project"])
    return proj or DEFAULT_PROJECT

def get_fresh_token(account: str) -> str:
    token = run_cmd(["gcloud", "auth", "print-access-token", account])
    if token.startswith("ya29."):
        return token
    token = run_cmd(["gcloud", "auth", "print-access-token"])
    if token.startswith("ya29."):
        return token
    token = run_cmd(["gcloud", "auth", "application-default", "print-access-token"])
    if token.startswith("ya29."):
        return token
    return ""

def generate_zettcode_config(token: str, project_id: str) -> str:
    global_base_url = f"https://aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/global/endpoints/openapi"
    
    return f"""# Generated automatically by DNK OS GCP Token Synchronizer
# Reliable SOTA Workhorse with Full Function Calling Support

# 1. Primary Workhorse: Gemini 2.5 Flash (Full tool calling & bash support, zero HTTP 400 thought_signature errors)
[[models]]
model = "google/gemini-2.5-flash"
display_model = "Gemini 2.5 Flash (Workhorse)"
token = "{token}"
base_url = "{global_base_url}"
context_window = 1000000
multimodal = true
temperature = 0.2

# 2. Next-Gen Multi-Modal: Gemini 4 Argon (Text queries & reasoning)
[[models]]
model = "google/gemini-4-argon"
display_model = "Gemini 4 Argon (Reasoning)"
token = "{token}"
base_url = "{global_base_url}"
context_window = 2000000
multimodal = true
temperature = 0.1
"""

def sync_auth():
    account = get_active_account()
    project = get_active_project()
    token = get_fresh_token(account)
    
    if not token or not token.startswith("ya29."):
        print(f"❌ Failed to obtain valid Google Cloud OAuth2 token for {account}.", file=sys.stderr)
        print("Run: gcloud auth application-default login", file=sys.stderr)
        sys.exit(1)

    print(f"⚡ [GCP Auth] Valid OAuth2 token refreshed for {account} (project: {project})")
    
    # 1. Update ~/.zettcode/config.toml
    zettcode_dir = Path.home() / ".zettcode"
    zettcode_dir.mkdir(parents=True, exist_ok=True)
    zettcode_config = zettcode_dir / "config.toml"
    
    config_content = generate_zettcode_config(token, project)
    zettcode_config.write_text(config_content, encoding="utf-8")
    print(f"✅ Updated {zettcode_config}")

    # 2. Update DNK_OS/config/config.toml
    script_dir = Path(__file__).resolve().parent
    dnk_os_config = script_dir.parent / "config" / "config.toml"
    dnk_os_config.parent.mkdir(parents=True, exist_ok=True)
    dnk_os_config.write_text(config_content, encoding="utf-8")
    print(f"✅ Updated {dnk_os_config}")

    # 3. Synchronize with Denchik (~/.hermes/vertex_token.txt)
    hermes_dir = Path.home() / ".hermes"
    hermes_dir.mkdir(parents=True, exist_ok=True)
    (hermes_dir / "vertex_token.txt").write_text(token.strip(), encoding="utf-8")
    print(f"✅ Synced token with Denchik ({hermes_dir / 'vertex_token.txt'})")

if __name__ == "__main__":
    sync_auth()
