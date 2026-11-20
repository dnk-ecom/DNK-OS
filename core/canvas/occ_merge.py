# --- DNK-MRH-HEADER ---
# mrh_id: "core/canvas/occ_merge.py"
# purpose: "OCC 3-Way Merge MVP for CanvasState updates (CANVAS-002)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "0.1.0"
# updated_at: "2026-09-09"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

# Canonical OCC 3-Way Graph Concurrency Engine symbols
from core.canvas.graph_occ_merge import (
    ConflictType,
    FileMergeStatus,
    MergeConflict,
    OCCConcurrencyEngine,
    OCCFileMergeResolver,
    OCCFileMergeResult,
    OCCGraphMergeResolver,
    OCCMergeResult,
    PositionConflictStrategy,
)


def validate_relative_path(path: Union[str, Path]) -> Path:
    """Validate that a path is strictly relative and contains no traversal or absolute prefixes."""
    path_str = str(path).strip()
    if not path_str:
        raise ValueError("Path cannot be empty")
    if os.path.isabs(path_str) or path_str.startswith("/") or path_str.startswith("\\"):
        raise ValueError(f"Absolute paths are forbidden: '{path_str}'")
    if path_str.startswith("~"):
        raise ValueError(f"User home paths are forbidden: '{path_str}'")
    parts = Path(path_str).parts
    if ".." in parts:
        raise ValueError(f"Path traversal is forbidden: '{path_str}'")
    norm = os.path.normpath(path_str)
    if norm.startswith("..") or norm == "..":
        raise ValueError(f"Path traversal is forbidden: '{path_str}'")
    return Path(path_str)


def is_relative_path(path: Any) -> bool:
    """Check if a path string or Path object is strictly relative without traversal."""
    try:
        validate_relative_path(path)
        return True
    except Exception:
        return False


ResolutionType = Literal["manual", "local", "remote", "base"]


class Conflict(BaseModel):
    """Represents a merge conflict detected during OCC 3-way merge."""
    path: str
    base_value: Optional[Any] = None
    local_value: Optional[Any] = None
    remote_value: Optional[Any] = None
    resolution: ResolutionType = "manual"


class MergeResult(BaseModel):
    """Result of an OCC 3-way merge operation."""
    success: bool = True
    conflicts: List[Conflict] = Field(default_factory=list)
    merged_state: Dict[str, Any] = Field(default_factory=dict)
    version: str = "v0.1"


class CanvasOCCMergeEngine:
    """Deterministic OCC 3-Way Merge Engine for CanvasState graphs."""

    def __init__(self, default_resolution: ResolutionType = "manual") -> None:
        self.default_resolution = default_resolution

    def merge_states(
        self,
        base: Union[Dict[str, Any], BaseModel],
        local: Union[Dict[str, Any], BaseModel],
        remote: Union[Dict[str, Any], BaseModel],
    ) -> MergeResult:
        """Merge base, local, and remote CanvasState representations."""
        base_dict = self._to_dict(base)
        local_dict = self._to_dict(local)
        remote_dict = self._to_dict(remote)

        # 11. If base == local == remote, return base directly as merged without conflicts
        if base_dict == local_dict == remote_dict:
            version = base_dict.get("version", "v0.1")
            return MergeResult(
                success=True,
                conflicts=[],
                merged_state=copy.deepcopy(base_dict),
                version=version,
            )

        conflicts: List[Conflict] = []
        merged_state = self._merge_dict_recursive(base_dict, local_dict, remote_dict, path="", conflicts=conflicts)

        # 10. Ensure version invariant is preserved
        if "version" not in merged_state or not merged_state["version"]:
            merged_state["version"] = base_dict.get("version") or local_dict.get("version") or remote_dict.get("version") or "v0.1"

        # Update last_updated_at if missing
        if "last_updated_at" not in merged_state:
            merged_state["last_updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        success = len(conflicts) == 0
        return MergeResult(
            success=success,
            conflicts=conflicts,
            merged_state=merged_state,
            version=merged_state.get("version", "v0.1"),
        )

    def merge_files(
        self,
        base_path: Union[str, Path],
        local_path: Union[str, Path],
        remote_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
    ) -> MergeResult:
        """Read states from relative JSON file paths, merge, and optionally write output."""
        base_p = validate_relative_path(base_path)
        local_p = validate_relative_path(local_path)
        remote_p = validate_relative_path(remote_path)

        with open(base_p, "r", encoding="utf-8") as f:
            base_data = json.load(f)
        with open(local_p, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        with open(remote_p, "r", encoding="utf-8") as f:
            remote_data = json.load(f)

        result = self.merge_states(base_data, local_data, remote_data)

        if output_path is not None:
            out_p = validate_relative_path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

        return result

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if isinstance(obj, dict):
            return copy.deepcopy(obj)
        if isinstance(obj, str):
            return json.loads(obj)
        raise ValueError(f"Cannot convert object of type {type(obj)} to dict")

    def _merge_dict_recursive(
        self,
        base: Optional[Dict[str, Any]],
        local: Optional[Dict[str, Any]],
        remote: Optional[Dict[str, Any]],
        path: str,
        conflicts: List[Conflict],
    ) -> Dict[str, Any]:
        base = base or {}
        local = local or {}
        remote = remote or {}

        all_keys: Set[str] = set(base.keys()) | set(local.keys()) | set(remote.keys())
        merged: Dict[str, Any] = {}

        # Preserve deterministic ordering for common canvas keys
        ordered_keys = [k for k in ("version", "nodes", "edges", "last_updated_at") if k in all_keys]
        remaining_keys = sorted(all_keys - set(ordered_keys))
        key_list = ordered_keys + remaining_keys

        for k in key_list:
            field_path = f"{path}.{k}" if path else k
            in_base = k in base
            in_local = k in local
            in_remote = k in remote

            # Special collection handling for nodes and edges
            if k in ("nodes", "edges"):
                b_list = base.get(k, []) if in_base else []
                l_list = local.get(k, []) if in_local else []
                r_list = remote.get(k, []) if in_remote else []
                id_key = "node_id" if k == "nodes" else "edge_id"
                merged[k] = self._merge_entity_list(b_list, l_list, r_list, field_path, id_key, conflicts)
                continue

            # Special timestamp handling: take newest or remote timestamp without triggering conflict
            if k == "last_updated_at":
                if in_local and in_remote:
                    # Prefer local if modified, or latest
                    merged[k] = local[k] if local[k] != base.get(k) else remote[k]
                elif in_local:
                    merged[k] = local[k]
                elif in_remote:
                    merged[k] = remote[k]
                elif in_base:
                    merged[k] = base[k]
                continue

            # Key present in all three
            if in_base and in_local and in_remote:
                b_val = base[k]
                l_val = local[k]
                r_val = remote[k]
                merged[k] = self._merge_value(b_val, l_val, r_val, field_path, conflicts)

            # Key added in local and/or remote (not in base)
            elif not in_base:
                if in_local and in_remote:
                    l_val = local[k]
                    r_val = remote[k]
                    merged[k] = self._merge_value(None, l_val, r_val, field_path, conflicts)
                elif in_local:
                    merged[k] = copy.deepcopy(local[k])
                elif in_remote:
                    merged[k] = copy.deepcopy(remote[k])

            # Key present in base but deleted in local or remote
            else:
                b_val = base[k]
                if not in_local and not in_remote:
                    # Both deleted it
                    continue
                elif not in_local and in_remote:
                    r_val = remote[k]
                    if r_val == b_val:
                        # Remote did not modify it, local deletion takes precedence
                        continue
                    else:
                        # Conflict: remote modified, local deleted
                        conflicts.append(
                            Conflict(
                                path=field_path,
                                base_value=b_val,
                                local_value=None,
                                remote_value=r_val,
                                resolution=self.default_resolution,
                            )
                        )
                        merged[k] = copy.deepcopy(r_val)
                elif in_local and not in_remote:
                    l_val = local[k]
                    if l_val == b_val:
                        # Local did not modify it, remote deletion takes precedence
                        continue
                    else:
                        # Conflict: local modified, remote deleted
                        conflicts.append(
                            Conflict(
                                path=field_path,
                                base_value=b_val,
                                local_value=l_val,
                                remote_value=None,
                                resolution=self.default_resolution,
                            )
                        )
                        merged[k] = copy.deepcopy(l_val)

        return merged

    def _merge_value(
        self,
        base: Any,
        local: Any,
        remote: Any,
        path: str,
        conflicts: List[Conflict],
    ) -> Any:
        # Rule 1: local == remote -> no conflict
        if local == remote:
            return copy.deepcopy(local)

        # Rule 2: recursive merge for nested dicts
        if isinstance(local, dict) and isinstance(remote, dict) and (base is None or isinstance(base, dict)):
            return self._merge_dict_recursive(base, local, remote, path, conflicts)

        # Rule 3: local != remote
        # If local matches base, remote changed it -> accept remote
        if base is not None and local == base:
            return copy.deepcopy(remote)

        # If remote matches base, local changed it -> accept local
        if base is not None and remote == base:
            return copy.deepcopy(local)

        # Rule 4: Both local and remote changed to different values -> conflict!
        conflicts.append(
            Conflict(
                path=path,
                base_value=copy.deepcopy(base),
                local_value=copy.deepcopy(local),
                remote_value=copy.deepcopy(remote),
                resolution=self.default_resolution,
            )
        )
        # Default to local value in merged representation
        return copy.deepcopy(local)

    def _merge_entity_list(
        self,
        base_list: List[Dict[str, Any]],
        local_list: List[Dict[str, Any]],
        remote_list: List[Dict[str, Any]],
        path: str,
        id_key: str,
        conflicts: List[Conflict],
    ) -> List[Dict[str, Any]]:
        """3-way merge for lists of entities identified by node_id or edge_id."""
        base_map: Dict[str, Tuple[int, Dict[str, Any]]] = {}
        for idx, item in enumerate(base_list):
            if isinstance(item, dict) and id_key in item:
                base_map[item[id_key]] = (idx, item)

        local_map: Dict[str, Tuple[int, Dict[str, Any]]] = {}
        for idx, item in enumerate(local_list):
            if isinstance(item, dict) and id_key in item:
                local_map[item[id_key]] = (idx, item)

        remote_map: Dict[str, Tuple[int, Dict[str, Any]]] = {}
        for idx, item in enumerate(remote_list):
            if isinstance(item, dict) and id_key in item:
                remote_map[item[id_key]] = (idx, item)

        all_ids: List[str] = []
        # Preserve order: base IDs first, then new local IDs, then new remote IDs
        for item in base_list:
            if isinstance(item, dict) and id_key in item and item[id_key] not in all_ids:
                all_ids.append(item[id_key])
        for item in local_list:
            if isinstance(item, dict) and id_key in item and item[id_key] not in all_ids:
                all_ids.append(item[id_key])
        for item in remote_list:
            if isinstance(item, dict) and id_key in item and item[id_key] not in all_ids:
                all_ids.append(item[id_key])

        merged_list: List[Dict[str, Any]] = []

        for entity_id in all_ids:
            in_b = entity_id in base_map
            in_l = entity_id in local_map
            in_r = entity_id in remote_map

            # Determine stable index for conflict path reporting (base index, local index, or remote index)
            if in_b:
                display_idx = base_map[entity_id][0]
            elif in_l:
                display_idx = local_map[entity_id][0]
            else:
                display_idx = remote_map[entity_id][0]

            entity_path = f"{path}.{display_idx}"

            if in_b and in_l and in_r:
                b_item = base_map[entity_id][1]
                l_item = local_map[entity_id][1]
                r_item = remote_map[entity_id][1]
                merged_item = self._merge_dict_recursive(b_item, l_item, r_item, entity_path, conflicts)
                merged_list.append(merged_item)

            elif not in_b:
                # Added in local or remote
                if in_l and in_r:
                    l_item = local_map[entity_id][1]
                    r_item = remote_map[entity_id][1]
                    merged_item = self._merge_dict_recursive(None, l_item, r_item, entity_path, conflicts)
                    merged_list.append(merged_item)
                elif in_l:
                    merged_list.append(copy.deepcopy(local_map[entity_id][1]))
                elif in_r:
                    merged_list.append(copy.deepcopy(remote_map[entity_id][1]))

            else:
                # Present in base, check deletions
                b_item = base_map[entity_id][1]
                if not in_l and not in_r:
                    # Both deleted
                    continue
                elif not in_l and in_r:
                    r_item = remote_map[entity_id][1]
                    if r_item == b_item:
                        # Remote unmodified, local deleted
                        continue
                    else:
                        conflicts.append(
                            Conflict(
                                path=entity_path,
                                base_value=b_item,
                                local_value=None,
                                remote_value=r_item,
                                resolution=self.default_resolution,
                            )
                        )
                        merged_list.append(copy.deepcopy(r_item))
                elif in_l and not in_r:
                    l_item = local_map[entity_id][1]
                    if l_item == b_item:
                        # Local unmodified, remote deleted
                        continue
                    else:
                        conflicts.append(
                            Conflict(
                                path=entity_path,
                                base_value=b_item,
                                local_value=l_item,
                                remote_value=None,
                                resolution=self.default_resolution,
                            )
                        )
                        merged_list.append(copy.deepcopy(l_item))

        return merged_list


def merge_canvas_states(
    base: Union[Dict[str, Any], BaseModel],
    local: Union[Dict[str, Any], BaseModel],
    remote: Union[Dict[str, Any], BaseModel],
) -> MergeResult:
    """Convenience functional interface for OCC 3-way merge."""
    engine = CanvasOCCMergeEngine()
    return engine.merge_states(base, local, remote)


def merge_files(
    base_path: Union[str, Path],
    local_path: Union[str, Path],
    remote_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> MergeResult:
    """Convenience functional interface to merge states directly from files."""
    engine = CanvasOCCMergeEngine()
    return engine.merge_files(base_path, local_path, remote_path, output_path)


__all__ = [
    "Conflict",
    "MergeResult",
    "CanvasOCCMergeEngine",
    "merge_canvas_states",
    "merge_files",
    "validate_relative_path",
    "is_relative_path",
    "ConflictType",
    "FileMergeStatus",
    "MergeConflict",
    "OCCConcurrencyEngine",
    "OCCFileMergeResolver",
    "OCCFileMergeResult",
    "OCCGraphMergeResolver",
    "OCCMergeResult",
    "PositionConflictStrategy",
]

