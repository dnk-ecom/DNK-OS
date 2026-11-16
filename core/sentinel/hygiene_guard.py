# --- DNK-MRH-HEADER ---
# mrh_id: "core/sentinel/hygiene_guard.py"
# purpose: "Filesystem & Zero-Duplicate Storage Sentinel for DNK OS (DEC-070, DEC-071)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class DNKHygieneGuard:
    """
    Enforces DEC-070 & DEC-071 Invariants:
    1. Zero hardcoded absolute paths in manifests and configs.
    2. Zero foreign repositories cloned directly into repository root.
    3. Proper pnpm store & uv runtime shared usage (Zero-Duplicate).
    """

    CANONICAL_ROOT_DIRS = {
        "apps", "core", "services", "packages", "infra", "docs", "tests", "scripts",
        "data", "logs", "config", ".agents", ".git", ".github", "cockpit"
    }

    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            self.root_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.root_dir = Path(root_dir).resolve()

    def audit_top_level_directories(self) -> Dict[str, Any]:
        """Checks for unapproved non-canonical top-level directories."""
        violations = []
        for item in self.root_dir.iterdir():
            if item.is_dir() and item.name not in self.CANONICAL_ROOT_DIRS and not item.name.startswith("."):
                violations.append(item.name)
        return {
            "status": "PASS" if not violations else "FAIL",
            "violations": violations,
        }

    def audit_absolute_paths_in_file(self, file_path: Path) -> List[str]:
        """Detects hardcoded user home paths (/Users/...) in a specific file."""
        findings = []
        if not file_path.exists() or file_path.is_dir():
            return findings

        # Check only text manifests and config files
        if file_path.suffix not in {".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".env", ".example"}:
            return findings

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"/(?:Users|home)/[a-zA-Z0-9_\.\-]+/[^\s\"\'\)\>]+", content)
            for m in matches:
                # Exclude harmless examples or comments if needed
                if not m.startswith("/Users/<username>"):
                    findings.append(m)
        except Exception:
            pass
        return findings

    def audit_manifests_for_absolute_paths(self) -> Dict[str, Any]:
        """Audits all critical configuration files for portability leaks."""
        leaks: Dict[str, List[str]] = {}
        files_to_check = [
            self.root_dir / "pyproject.toml",
            self.root_dir / "package.json",
            self.root_dir / ".env",
            self.root_dir / ".env.example",
            self.root_dir / "Dockerfile",
            self.root_dir / "compose.yaml",
            self.root_dir / "bootstrap.sh",
            self.root_dir / "core" / "config" / "settings.py",
        ]
        for f in files_to_check:
            if f.exists():
                res = self.audit_absolute_paths_in_file(f)
                if res:
                    rel_p = str(f.relative_to(self.root_dir))
                    leaks[rel_p] = res

        return {
            "status": "PASS" if not leaks else "FAIL",
            "leaks": leaks,
        }

    def audit_shared_runtime(self) -> Dict[str, Any]:
        """Checks whether global runtime stores (uv and pnpm) are accessible."""
        home = Path.home()
        dnk_runtime = home / ".dnk_runtime"
        pnpm_store = home / ".pnpm-store"
        uv_cache = home / ".cache" / "uv"

        return {
            "dnk_runtime_exists": dnk_runtime.exists(),
            "pnpm_store_accessible": pnpm_store.exists() or (home / "Library" / "pnpm").exists(),
            "uv_cache_accessible": uv_cache.exists() or (home / ".local" / "share" / "uv").exists(),
        }

    def full_hygiene_check(self) -> Dict[str, Any]:
        top = self.audit_top_level_directories()
        abs_paths = self.audit_manifests_for_absolute_paths()
        runtime = self.audit_shared_runtime()

        is_clean = (top["status"] == "PASS") and (abs_paths["status"] == "PASS")
        return {
            "healthy": is_clean,
            "top_level_audit": top,
            "absolute_path_audit": abs_paths,
            "runtime_audit": runtime,
        }


# Singleton instance
hygiene_guard = DNKHygieneGuard()
