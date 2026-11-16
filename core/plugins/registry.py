# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/registry.py"
# purpose: "DNK OS Plugin Discovery & Registry MVP Engine v0.1"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import glob
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field


def is_relative_path(path: Optional[str]) -> bool:
    """Check if a path is strictly relative and contains no unsafe escapes."""
    if not path or not isinstance(path, str):
        return False
    if os.path.isabs(path):
        return False
    if path.startswith("/") or path.startswith("\\") or path.startswith("~"):
        return False
    norm = os.path.normpath(path)
    if norm == ".." or norm.startswith("../") or norm.startswith("..\\"):
        return False
    return True


class PluginIndexEntry(BaseModel):
    """Entry within the Plugin Index representing a single discovered plugin card."""

    plugin_id: str
    name: str
    version: str
    kind: str = "tool"
    lifecycle: str = "sandbox"
    origin_type: str = "open_source"
    license_spdx: str = "MIT"
    card_path: str
    updated_at: str


class PluginIndex(BaseModel):
    """Aggregate index representation stored in plugins_index.json."""

    schema_version: str = "dnk-plugin-index/v1.0"
    plugins_root: str = "core/templates/plugin"
    index_path: str = "core/templates/plugin/plugins_index.json"
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    entries: List[PluginIndexEntry] = Field(default_factory=list)


class PluginRegistry:
    """Core engine for plugin discovery, index compilation, filtering, and inspection."""

    def __init__(
        self,
        plugins_root: str = "core/templates/plugin",
        index_path: str = "core/templates/plugin/plugins_index.json",
    ):
        if not is_relative_path(plugins_root):
            raise ValueError(f"plugins_root must be a relative path: {plugins_root}")
        if not is_relative_path(index_path):
            raise ValueError(f"index_path must be a relative path: {index_path}")

        norm_root = os.path.normpath(plugins_root)
        if not os.path.exists(norm_root) and os.path.exists(os.path.join("core", norm_root)):
            norm_root = os.path.normpath(os.path.join("core", norm_root))
        self.plugins_root = norm_root

        norm_index = os.path.normpath(index_path)
        if not os.path.exists(norm_index) and os.path.exists(os.path.join("core", norm_index)):
            norm_index = os.path.normpath(os.path.join("core", norm_index))
        self.index_path = norm_index

    def scan(self) -> PluginIndex:
        """Scan candidate plugin card YAML files and compile plugins_index.json."""
        pattern_root = os.path.join(self.plugins_root, "*.yaml")
        pattern_github = os.path.join(self.plugins_root, "github", "*_card.yaml")

        discovered_paths = set(glob.glob(pattern_root) + glob.glob(pattern_github))
        sorted_paths = sorted(discovered_paths)

        entries: List[PluginIndexEntry] = []

        for path in sorted_paths:
            entry = self._parse_card_file(path)
            if entry is not None:
                entries.append(entry)

        # Sort entries deterministically by plugin_id
        entries.sort(key=lambda e: e.plugin_id)

        index = PluginIndex(
            plugins_root=self.plugins_root,
            index_path=self.index_path,
            updated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            entries=entries,
        )

        self.save_index(index)
        return index

    def _parse_card_file(self, file_path: str) -> Optional[PluginIndexEntry]:
        """Parse and validate candidate card file into PluginIndexEntry, returning None if invalid."""
        if not os.path.isfile(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        plugin_id = data.get("id")
        name = data.get("name")
        version = data.get("version")
        kind = data.get("kind")
        lifecycle = data.get("lifecycle")

        if not plugin_id or not isinstance(plugin_id, str):
            return None
        if not name or not isinstance(name, str):
            return None
        if not version or not isinstance(version, str):
            return None
        if not kind or not isinstance(kind, str):
            return None
        if not lifecycle or not isinstance(lifecycle, str):
            return None

        origin = data.get("origin")
        if not isinstance(origin, dict):
            origin = {}

        origin_type = origin.get("type", "open_source")
        license_spdx = origin.get("license_spdx", "UNKNOWN")

        # Determine timestamp: use card's updated_at if valid, else file mtime
        updated_at = data.get("updated_at")
        if not updated_at or not isinstance(updated_at, str):
            try:
                mtime = os.path.getmtime(file_path)
                updated_at = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            except Exception:
                updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        rel_card_path = os.path.normpath(file_path)

        try:
            return PluginIndexEntry(
                plugin_id=plugin_id,
                name=name,
                version=version,
                kind=kind,
                lifecycle=lifecycle,
                origin_type=str(origin_type),
                license_spdx=str(license_spdx),
                card_path=rel_card_path,
                updated_at=updated_at,
            )
        except Exception:
            return None

    def save_index(self, index: PluginIndex) -> str:
        """Persist index to index_path in pretty JSON format."""
        if not is_relative_path(self.index_path):
            raise ValueError(f"index_path must be a relative path: {self.index_path}")

        parent_dir = os.path.dirname(self.index_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write(index.model_dump_json(indent=2))
            f.write("\n")

        return self.index_path

    def load_index(self) -> PluginIndex:
        """Load index from index_path. If missing, scan first."""
        if not os.path.exists(self.index_path):
            return self.scan()

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PluginIndex.model_validate(data)
        except Exception:
            return self.scan()

    def list_plugins(
        self, lifecycle: Optional[str] = None, kind: Optional[str] = None
    ) -> List[PluginIndexEntry]:
        """List registered plugin entries with optional lifecycle and kind filtering."""
        index = self.load_index()
        results = index.entries

        if lifecycle is not None:
            target_lc = lifecycle.strip().lower()
            results = [e for e in results if e.lifecycle.lower() == target_lc]

        if kind is not None:
            target_kind = kind.strip().lower()
            results = [e for e in results if e.kind.lower() == target_kind]

        return results

    def get_plugin(self, plugin_id: str) -> Optional[PluginIndexEntry]:
        """Retrieve a specific plugin entry by plugin_id."""
        index = self.load_index()
        for entry in index.entries:
            if entry.plugin_id == plugin_id:
                return entry
        return None

    def get_card_content(self, plugin_id: str) -> Optional[str]:
        """Retrieve raw card YAML content for a given plugin_id."""
        entry = self.get_plugin(plugin_id)
        if not entry:
            return None

        if not os.path.exists(entry.card_path):
            return None

        with open(entry.card_path, "r", encoding="utf-8") as f:
            return f.read()
