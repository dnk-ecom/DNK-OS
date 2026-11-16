# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/process_sentinel.py"
# purpose: "PID Sentinel & Zombie Process Watchdog for DNK OS (DEC-071)."
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
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class DNKProcessSentinel:
    """
    Guarantees DEC-071: PID Sentinel & Background Process Hygiene.
    Tracks active PID files, reaps orphan processes, and prevents runaway memory leaks.
    """

    def __init__(self, state_dir: Optional[Path] = None):
        if state_dir is None:
            self.state_dir = Path(__file__).resolve().parent.parent.parent / "data" / "pids"
        else:
            self.state_dir = Path(state_dir).resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def write_pid(self, service_name: str, pid: Optional[int] = None) -> Path:
        """Records a process ID in the state directory."""
        if pid is None:
            pid = os.getpid()
        pid_file = self.state_dir / f"{service_name}.pid"
        pid_file.write_text(str(pid), encoding="utf-8")
        return pid_file

    def read_pid(self, service_name: str) -> Optional[int]:
        """Reads a recorded process ID."""
        pid_file = self.state_dir / f"{service_name}.pid"
        if not pid_file.exists():
            return None
        try:
            return int(pid_file.read_text(encoding="utf-8").strip())
        except Exception:
            return None

    def is_pid_alive(self, pid: int) -> bool:
        """Checks if a given PID is currently active."""
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def remove_pid(self, service_name: str) -> None:
        """Removes a recorded PID file."""
        pid_file = self.state_dir / f"{service_name}.pid"
        if pid_file.exists():
            pid_file.unlink()

    def kill_service(self, service_name: str, force: bool = False) -> bool:
        """Terminates a registered service by its PID file."""
        pid = self.read_pid(service_name)
        if not pid:
            return False
        if not self.is_pid_alive(pid):
            self.remove_pid(service_name)
            return False

        try:
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            self.remove_pid(service_name)
            return True
        except Exception as e:
            print(f"⚠️ Failed to kill service '{service_name}' (PID {pid}): {e}")
            return False

    def find_zombie_processes(self) -> List[Dict[str, Any]]:
        """Finds dangling, orphaned dev servers or background workers."""
        zombies = []
        try:
            cmd = ["ps", "-eo", "pid,ppid,command"]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
            for line in output.splitlines()[1:]:
                parts = line.strip().split(None, 2)
                if len(parts) < 3:
                    continue
                pid = int(parts[0])
                ppid = int(parts[1])
                command = parts[2]

                # Identify orphaned python/node dev servers that parented to init/launchd (ppid == 1)
                if ppid == 1 and ("vite" in command or "next-server" in command or "uvicorn" in command):
                    zombies.append({"pid": pid, "ppid": ppid, "command": command})
        except Exception:
            pass
        return zombies

    def reap_zombies(self) -> int:
        """Reaps orphaned dev servers."""
        zombies = self.find_zombie_processes()
        reaped = 0
        for z in zombies:
            try:
                os.kill(z["pid"], signal.SIGKILL)
                reaped += 1
            except Exception:
                pass
        return reaped


# Singleton instance
process_sentinel = DNKProcessSentinel()
