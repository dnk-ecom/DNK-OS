# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/health_metrics.py"
# purpose: "Plugin Health & Metrics evaluation models and calculation engine for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Plugin Health & Metrics MVP (SLICE PLUGIN-010).

Provides data models, scoring functions, and health aggregation for DNK OS plugins.
Operates strictly via local relative paths without network, secrets, or runtime changes.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field

ALLOWED_LIFECYCLES = ("draft", "sandbox", "evaluated", "active", "deprecated")
ALLOWED_KINDS = ("tool", "memory", "agent", "service_adapter", "ui_node", "workflow")


def validate_relative_path(path: Union[str, Path]) -> Path:
    """Validate that a path is strictly relative and contains no path traversal."""
    path_str = str(path).strip()
    if not path_str:
        raise ValueError("Path cannot be empty")

    if os.path.isabs(path_str) or path_str.startswith("/") or path_str.startswith("\\"):
        raise ValueError(f"Absolute paths are forbidden: '{path_str}'")

    # Reject traversal
    parts = Path(path_str).parts
    if ".." in parts:
        raise ValueError(f"Path traversal is forbidden: '{path_str}'")

    norm = os.path.normpath(path_str)
    if norm.startswith(".."):
        raise ValueError(f"Path traversal is forbidden: '{path_str}'")

    return Path(norm)


def calculate_plugin_health_score(
    valid_card: bool = True,
    green_sandbox_run: bool = False,
    certified: bool = False,
    successful_executions: int = 0,
    failed_executions: int = 0,
    blocked_executions: int = 0,
    base_score: int = 0,
    **kwargs: Any,
) -> int:
    """Calculate the health score of a plugin bounded to [0, 100].

    Rules:
    - +20 for valid Plugin Card;
    - +20 for green sandbox run;
    - +20 for certification;
    - +20 for at least one successful execution;
    - -20 for each failed execution;
    - -20 for each blocked execution;
    - result bounded to [0, 100].
    """
    score = base_score
    if valid_card:
        score += 20
    if green_sandbox_run:
        score += 20
    if certified:
        score += 20
    if successful_executions > 0 or kwargs.get("has_successful_execution", False):
        score += 20

    score -= 20 * failed_executions
    score -= 20 * blocked_executions

    return max(0, min(100, score))


# Alias for convenience
calculate_health_score = calculate_plugin_health_score


class PluginHealthStatus(BaseModel):
    """Health metrics and execution counters for a single plugin."""

    plugin_id: str = ""
    lifecycle: str = "sandbox"
    last_intake_at: Optional[str] = "2026-09-09T20:00:00Z"
    last_sandbox_run_at: Optional[str] = None
    last_certification_at: Optional[str] = None
    last_execution_at: Optional[str] = None
    total_sandbox_runs: int = 0
    total_certifications: int = 0
    total_executions: int = 0
    failed_executions: int = 0
    blocked_executions: int = 0
    health_score: int = Field(default=100, ge=0, le=100)


class SystemHealthReport(BaseModel):
    """Aggregated health report across the DNK OS plugin catalog."""

    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    total_plugins: int = 0
    plugins_by_lifecycle: Dict[str, int] = Field(
        default_factory=lambda: {
            "draft": 0,
            "sandbox": 0,
            "evaluated": 0,
            "active": 0,
            "deprecated": 0,
        }
    )
    plugins_by_kind: Dict[str, int] = Field(
        default_factory=lambda: {
            "tool": 0,
            "memory": 0,
            "agent": 0,
            "service_adapter": 0,
            "ui_node": 0,
            "workflow": 0,
        }
    )
    total_sandbox_runs: int = 0
    total_executions: int = 0
    failed_executions: int = 0
    blocked_executions: int = 0
    average_health_score: float = Field(default=100.0, ge=0.0, le=100.0)


class PluginHealthManager:
    """Evaluates individual plugin health and compiles system-wide reports."""

    def __init__(
        self,
        index_path: str = "templates/plugin/plugins_index.json",
        audit_log_path: str = "templates/plugin/audit/audit_log.jsonl",
        plugins_root: str = "templates/plugin",
    ) -> None:
        self.index_path = validate_relative_path(index_path)
        if not self.index_path.exists() and (Path("core") / self.index_path).exists():
            self.index_path = Path("core") / self.index_path

        self.audit_log_path = validate_relative_path(audit_log_path)
        if not self.audit_log_path.exists() and (Path("core") / self.audit_log_path).exists():
            self.audit_log_path = Path("core") / self.audit_log_path

        self.plugins_root = validate_relative_path(plugins_root)
        if not self.plugins_root.exists() and (Path("core") / self.plugins_root).exists():
            self.plugins_root = Path("core") / self.plugins_root

    def _read_audit_events(self, plugin_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read and optionally filter audit events from the audit log JSONL."""
        if not self.audit_log_path.exists():
            return []

        events: List[Dict[str, Any]] = []
        with open(self.audit_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    ev = json.loads(line_str)
                    if plugin_id is None or ev.get("plugin_id") == plugin_id:
                        events.append(ev)
                except json.JSONDecodeError:
                    continue
        return events

    def _load_index_entries(self) -> List[Dict[str, Any]]:
        """Load registered plugin cards from the index JSON if it exists."""
        if not self.index_path.exists():
            return []
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return data.get("entries", [])
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def _find_card_file(self, plugin_id: str, card_path_hint: Optional[str] = None) -> Optional[Path]:
        """Find the on-disk YAML card file for a given plugin ID."""
        if card_path_hint:
            try:
                candidate = validate_relative_path(card_path_hint)
                if candidate.exists():
                    return candidate
                if (Path("core") / candidate).exists():
                    return Path("core") / candidate
            except ValueError:
                pass

        # Scan under plugins_root
        if self.plugins_root.exists():
            for root, _, files in os.walk(self.plugins_root):
                for fname in files:
                    if fname.endswith(".yaml") or fname.endswith(".yml"):
                        fpath = Path(root) / fname
                        try:
                            with open(fpath, "r", encoding="utf-8") as yf:
                                card_data = yaml.safe_load(yf)
                                if isinstance(card_data, dict) and card_data.get("id") == plugin_id:
                                    return fpath
                        except Exception:
                            continue
        return None

    def get_plugin_health(self, plugin_id: str) -> PluginHealthStatus:
        """Calculate and return health metrics for a specific plugin."""
        if not plugin_id:
            raise ValueError("plugin_id cannot be empty")

        entries = self._load_index_entries()
        entry = next((e for e in entries if e.get("plugin_id") == plugin_id), None)

        card_path_hint = entry.get("card_path") if entry else None
        card_file = self._find_card_file(plugin_id, card_path_hint)

        if not entry and not card_file:
            raise KeyError(f"Plugin '{plugin_id}' not found in registry index or card files")

        # Load card data if file exists
        card_data: Dict[str, Any] = {}
        valid_card = False
        if card_file and card_file.exists():
            try:
                with open(card_file, "r", encoding="utf-8") as cf:
                    parsed = yaml.safe_load(cf)
                    if isinstance(parsed, dict):
                        card_data = parsed
                        # Minimal sanity check for valid card
                        if card_data.get("id") and card_data.get("name") and card_data.get("kind"):
                            valid_card = True
            except Exception:
                valid_card = False

        lifecycle = (
            (entry.get("lifecycle") if entry else None)
            or (card_data.get("lifecycle") if card_data else None)
            or "sandbox"
        )
        if lifecycle not in ALLOWED_LIFECYCLES:
            lifecycle = "sandbox"

        # Read audit events
        events = self._read_audit_events(plugin_id)

        last_intake_at: Optional[str] = None
        last_sandbox_run_at: Optional[str] = None
        last_certification_at: Optional[str] = None
        last_execution_at: Optional[str] = None

        total_sandbox_runs = 0
        total_certifications = 0
        total_executions = 0
        failed_executions = 0
        blocked_executions = 0
        successful_executions = 0

        green_sandbox_run = False
        certified = False

        for ev in events:
            ev_type = ev.get("event_type")
            ts = ev.get("timestamp")
            details = ev.get("details", {}) or {}

            if ev_type == "plugin.intake":
                last_intake_at = ts
            elif ev_type == "plugin.sandbox_run":
                last_sandbox_run_at = ts
                total_sandbox_runs += 1
                status = str(details.get("status", "")).lower()
                if status in ("success", "green", "passed", "pass", "ok") or details.get("success") is True:
                    green_sandbox_run = True
            elif ev_type == "plugin.certification":
                last_certification_at = ts
                total_certifications += 1
                status = str(details.get("status", "")).lower()
                if status in ("certified", "green", "passed", "pass", "ok") or details.get("certified") is True:
                    certified = True
            elif ev_type == "plugin.execution_run":
                last_execution_at = ts
                total_executions += 1
                status = str(details.get("status", "")).lower()
                if status == "failed" or details.get("success") is False:
                    failed_executions += 1
                elif status == "blocked" or details.get("blocked") is True:
                    blocked_executions += 1
                elif status in ("success", "passed", "ok") or details.get("success") is True:
                    successful_executions += 1
                else:
                    successful_executions += 1

        # Fallbacks for timestamps
        if not last_intake_at:
            last_intake_at = entry.get("updated_at") if entry else card_data.get("updated_at", "2026-09-09T20:00:00Z")

        # Lifecycle heuristics for certification/sandbox
        if lifecycle in ("evaluated", "active"):
            certified = True
        if lifecycle in ("evaluated", "active", "sandbox") and total_sandbox_runs > 0 and not green_sandbox_run:
            green_sandbox_run = True

        health_score = calculate_plugin_health_score(
            valid_card=valid_card,
            green_sandbox_run=green_sandbox_run,
            certified=certified,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            blocked_executions=blocked_executions,
        )

        return PluginHealthStatus(
            plugin_id=plugin_id,
            lifecycle=lifecycle,
            last_intake_at=last_intake_at,
            last_sandbox_run_at=last_sandbox_run_at,
            last_certification_at=last_certification_at,
            last_execution_at=last_execution_at,
            total_sandbox_runs=total_sandbox_runs,
            total_certifications=total_certifications,
            total_executions=total_executions,
            failed_executions=failed_executions,
            blocked_executions=blocked_executions,
            health_score=health_score,
        )

    def get_system_health(self) -> SystemHealthReport:
        """Aggregate health metrics across all registered or discovered plugins."""
        entries = self._load_index_entries()
        seen_plugin_ids = {e.get("plugin_id") for e in entries if e.get("plugin_id")}

        # If index was not present or empty, discover any card files in plugins_root
        if not entries and self.plugins_root.exists():
            for root, _, files in os.walk(self.plugins_root):
                for fname in files:
                    if fname.endswith(".yaml") or fname.endswith(".yml"):
                        try:
                            fpath = Path(root) / fname
                            with open(fpath, "r", encoding="utf-8") as yf:
                                cdata = yaml.safe_load(yf)
                                if isinstance(cdata, dict) and cdata.get("id"):
                                    pid = cdata["id"]
                                    if pid not in seen_plugin_ids:
                                        entries.append(
                                            {
                                                "plugin_id": pid,
                                                "name": cdata.get("name", pid),
                                                "version": cdata.get("version", "0.1.0"),
                                                "kind": cdata.get("kind", "tool"),
                                                "lifecycle": cdata.get("lifecycle", "sandbox"),
                                                "card_path": str(fpath),
                                            }
                                        )
                                        seen_plugin_ids.add(pid)
                        except Exception:
                            continue

        total_plugins = len(entries)
        lifecycle_counts: Dict[str, int] = {k: 0 for k in ALLOWED_LIFECYCLES}
        kind_counts: Dict[str, int] = {k: 0 for k in ALLOWED_KINDS}

        total_sandbox_runs = 0
        total_executions = 0
        failed_executions = 0
        blocked_executions = 0
        health_scores: List[int] = []

        for entry in entries:
            pid = entry.get("plugin_id")
            if not pid:
                continue

            lc = entry.get("lifecycle", "sandbox")
            if lc in lifecycle_counts:
                lifecycle_counts[lc] += 1
            else:
                lifecycle_counts["sandbox"] += 1

            kd = entry.get("kind", "tool")
            if kd in kind_counts:
                kind_counts[kd] += 1
            else:
                kind_counts["tool"] += 1

            try:
                status = self.get_plugin_health(pid)
                total_sandbox_runs += status.total_sandbox_runs
                total_executions += status.total_executions
                failed_executions += status.failed_executions
                blocked_executions += status.blocked_executions
                health_scores.append(status.health_score)
            except Exception:
                # If health computation fails for an entry, record default baseline score 20
                health_scores.append(20)

        average_health = (
            round(sum(health_scores) / len(health_scores), 2)
            if health_scores
            else 100.0
        )

        return SystemHealthReport(
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            total_plugins=total_plugins,
            plugins_by_lifecycle=lifecycle_counts,
            plugins_by_kind=kind_counts,
            total_sandbox_runs=total_sandbox_runs,
            total_executions=total_executions,
            failed_executions=failed_executions,
            blocked_executions=blocked_executions,
            average_health_score=average_health,
        )

    def export_system_health(self, output_path: str = "templates/plugin/metrics/health_report.json") -> SystemHealthReport:
        """Export the system health report to a specified JSON file."""
        out_path = validate_relative_path(output_path)
        report = self.get_system_health()

        # Ensure parent directory exists
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

        return report
