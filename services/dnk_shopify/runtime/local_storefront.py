#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/runtime/local_storefront.py"
# purpose: "Sovereign Python harness and daemon manager for 0xtlt/local-storefront (lsf) in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
LocalStorefrontManager: Python Controller for 0xtlt/local-storefront (Rust Headless Runtime).
Enables sub-millisecond offline Liquid rendering, live-reloading, Strict Liquid validation,
and instant store prototype generation in DNK OS.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("dnk_shopify.local_storefront")


class LocalStorefrontManager:
    """Manages local-storefront CLI execution and running daemon processes."""

    def __init__(self, default_port: int = 9292, host: str = "127.0.0.1") -> None:
        self.host = host
        self.port = default_port
        self.base_url = f"http://{self.host}:{self.port}"
        self._process: Optional[subprocess.Popen[Any]] = None

    @staticmethod
    def _find_npx() -> str:
        npx = shutil.which("npx")
        if not npx:
            raise RuntimeError("npx not found in PATH. Node.js runtime is required.")
        return npx

    def run_check(self, theme_dir: str | Path, fix: bool = False) -> Dict[str, Any]:
        """Runs strict Liquid compatibility check on the theme."""
        theme_path = Path(theme_dir).resolve()
        cmd = [self._find_npx(), "--yes", "local-storefront", "check", "--theme", str(theme_path)]
        if fix:
            cmd.append("--fix")

        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def run_validate(self, theme_dir: str | Path, data_dir: Optional[str | Path] = None) -> Dict[str, Any]:
        """Validates theme and store fixtures (JSON schemas and references)."""
        theme_path = Path(theme_dir).resolve()
        cmd = [self._find_npx(), "--yes", "local-storefront", "validate", "--theme", str(theme_path), "--format", "json"]
        if data_dir:
            cmd.extend(["--data", str(Path(data_dir).resolve())])

        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            parsed = json.loads(result.stdout)
            return {"success": result.returncode == 0, "diagnostics": parsed}
        except json.JSONDecodeError:
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "raw_stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }

    def run_profile(self, theme_dir: str | Path, path: str = "/") -> Dict[str, Any]:
        """Profiles rendering time for sections, blocks, and snippets for a given URL."""
        theme_path = Path(theme_dir).resolve()
        cmd = [self._find_npx(), "--yes", "local-storefront", "profile", path, "--theme", str(theme_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
        }

    def run_render(self, theme_dir: str | Path, path: str = "/") -> Dict[str, Any]:
        """Renders a single URL route directly to HTML string."""
        theme_path = Path(theme_dir).resolve()
        cmd = [self._find_npx(), "--yes", "local-storefront", "render", path, "--theme", str(theme_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "html": result.stdout,
            "stderr": result.stderr.strip(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Queries the running daemon for status and active templates."""
        url = f"{self.base_url}/__lsf/status"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {"active": True, "status": data}
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            pass
        return {"active": False, "status": None}

    def reload_data(self) -> Dict[str, Any]:
        """Triggers hot reload of shopify-local/ data files via Control API."""
        url = f"{self.base_url}/__lsf/reload"
        try:
            req = urllib.request.Request(url, data=b"", method="POST")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return {"success": resp.status in (200, 204), "code": resp.status}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def init_demo_data(self, theme_dir: str | Path) -> Dict[str, Any]:
        """Initializes a local editable shopify-local/ fixture directory."""
        theme_path = Path(theme_dir).resolve()
        cmd = [self._find_npx(), "--yes", "local-storefront", "init", "--theme", str(theme_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
        }

    def start_daemon(
        self,
        theme_dir: str | Path,
        data_dir: Optional[str | Path] = None,
        live_reload: bool = True,
        port: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Spawns background local-storefront daemon process."""
        target_port = port or self.port
        theme_path = Path(theme_dir).resolve()

        # Check if already running on that port
        status = self.get_status()
        if status.get("active"):
            return {
                "success": True,
                "message": f"Daemon already active at {self.base_url}",
                "status": status.get("status"),
            }

        cmd = [
            self._find_npx(),
            "--yes",
            "local-storefront",
            "serve",
            "--theme",
            str(theme_path),
            "--port",
            str(target_port),
            "--host",
            self.host,
        ]
        if data_dir:
            cmd.extend(["--data", str(Path(data_dir).resolve())])
        if live_reload:
            cmd.append("--live-reload")

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self._process = proc

        # Wait up to 5 seconds for daemon readiness
        deadline = time.time() + 5.0
        while time.time() < deadline:
            st = self.get_status()
            if st.get("active"):
                return {
                    "success": True,
                    "pid": proc.pid,
                    "url": self.base_url,
                    "status": st.get("status"),
                }
            time.sleep(0.3)

        return {
            "success": False,
            "error": "Daemon started but failed health check within 5s",
            "pid": proc.pid,
        }
