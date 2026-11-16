# --- DNK-MRH-HEADER ---
# mrh_id: "core/registry/port_manager.py"
# purpose: "Port Manager & Collision Sentinel for DNK OS Sovereign Architecture."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import signal
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


class DNKPortManager:
    """
    Sovereign Port Governance and Sentinel for DNK OS.
    Prevents port collisions on MacBook and Linux hosts.
    """

    def __init__(self, registry_file: Optional[Path] = None):
        if registry_file is None:
            self.registry_file = Path(__file__).resolve().parent / "port_registry.yaml"
        else:
            self.registry_file = Path(registry_file).resolve()
        self.data: Dict[str, Any] = {}
        self.load_registry()

    def load_registry(self) -> Dict[str, Any]:
        if self.registry_file.exists():
            with open(self.registry_file, "r", encoding="utf-8") as f:
                self.data = yaml.safe_load(f) or {}
        return self.data

    def is_port_in_use(self, port: int, host: str = "127.0.0.1") -> bool:
        """Tests whether a TCP port is currently open and listening."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0

    def get_process_on_port(self, port: int) -> Optional[Dict[str, Any]]:
        """Returns PID, process name, and command for process listening on port."""
        try:
            cmd = ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
            lines = output.splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    "command": parts[0],
                    "pid": int(parts[1]),
                    "user": parts[2],
                    "port": port,
                }
        except Exception:
            pass
        return None

    def kill_process_on_port(self, port: int, force: bool = False) -> bool:
        """Terminates process listening on port."""
        proc = self.get_process_on_port(port)
        if not proc:
            return False
        pid = proc["pid"]
        try:
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            return True
        except Exception as e:
            print(f"⚠️ Failed to kill process {pid} on port {port}: {e}")
            return False

    def list_registered_ports(self) -> List[Dict[str, Any]]:
        """Extracts all registered port mappings from port_registry.yaml."""
        results = []
        entries = self.data.get("port_registry", {}).get("entries", {})
        for key, entry in entries.items():
            name = entry.get("name", key)
            ports = entry.get("ports", {})
            for role, port_num in ports.items():
                if isinstance(port_num, int):
                    in_use = self.is_port_in_use(port_num)
                    proc = self.get_process_on_port(port_num) if in_use else None
                    results.append({
                        "key": key,
                        "service_name": name,
                        "role": role,
                        "port": port_num,
                        "status": "LISTENING" if in_use else "AVAILABLE",
                        "pid": proc["pid"] if proc else None,
                        "command": proc["command"] if proc else None,
                    })
        return sorted(results, key=lambda x: x["port"])

    def find_free_port(self, start: int = 54100, end: int = 54999) -> int:
        """Finds the first available port in the isolated range."""
        for port in range(start, end + 1):
            if not self.is_port_in_use(port):
                return port
        raise RuntimeError(f"No free ports available in range {start}-{end}")

    def audit_status(self) -> Dict[str, Any]:
        """Audits all registered and common ports for status and policy violations."""
        ports = self.list_registered_ports()
        active = [p for p in ports if p["status"] == "LISTENING"]
        return {
            "total_registered": len(ports),
            "currently_listening": len(active),
            "active_services": active,
        }


# Singleton instance
port_manager = DNKPortManager()
