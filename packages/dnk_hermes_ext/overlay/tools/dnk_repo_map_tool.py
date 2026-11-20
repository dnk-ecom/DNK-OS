# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_repo_map_tool.py"
# purpose: "Native Hermes tool for ultra-fast symbol resolution, file location, and monorepo architecture mapping."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-05"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKRepoMapTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(HUB_ROOT))

try:
    from scripts.system.repo_map import find_symbol, find_files, STRUCTURE_INDEX, find_callers, resolve_symbol_graph
except Exception as exc:
    logger.warning("Could not import repo_map from scripts/system: %s", exc)
    find_symbol = None
    find_files = None
    find_callers = None
    resolve_symbol_graph = None
    STRUCTURE_INDEX = {}


def dnk_resolve_symbol(symbol: str, include_calls: bool = False, **kwargs: Any) -> str:
    """
    Instantly locate where a class, function, interface, type, or constant is defined in the repository.
    Optionally retrieves call sites and reference counts.

    Args:
        symbol: The name or substring of the class, function, or interface (e.g. 'TaskForest', 'CanvasEngine').
        include_calls: If True, also includes call sites and references across the codebase.

    Returns:
        JSON string containing matching definitions, file paths, line numbers, and code snippets.
    """
    if not symbol or not isinstance(symbol, str):
        return json.dumps({
            "status": "error",
            "message": "Symbol name must be a non-empty string."
        }, ensure_ascii=False)

    if find_symbol is None:
        return json.dumps({
            "status": "error",
            "message": "repo_map module unavailable in scripts/system."
        }, ensure_ascii=False)

    try:
        if include_calls and resolve_symbol_graph is not None:
            graph = resolve_symbol_graph(symbol.strip(), root=HUB_ROOT)
            return json.dumps({
                "status": "success",
                "query": symbol,
                "graph": graph,
                "hint": "Definitions and call sites resolved instantly without multi-file scanning."
            }, indent=2, ensure_ascii=False)

        results = find_symbol(symbol.strip(), root=HUB_ROOT)
        return json.dumps({
            "status": "success",
            "query": symbol,
            "count": len(results),
            "results": results[:50],
            "hint": "Use view_file(file, StartLine, EndLine) around the line number to read implementation details."
        }, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({
            "status": "error",
            "message": f"Failed to resolve symbol '{symbol}': {exc}"
        }, ensure_ascii=False)


def dnk_find_files(pattern: str, **kwargs: Any) -> str:
    """
    Locate repository files matching a path or name fragment (e.g. 'router', 'obsidian', 'canvas').

    Args:
        pattern: Substring or fragment of the file path.

    Returns:
        JSON string containing matched relative file paths.
    """
    if not pattern or not isinstance(pattern, str):
        return json.dumps({
            "status": "error",
            "message": "Pattern must be a non-empty string."
        }, ensure_ascii=False)

    if find_files is None:
        return json.dumps({
            "status": "error",
            "message": "repo_map module unavailable in scripts/system."
        }, ensure_ascii=False)

    try:
        matched = find_files(pattern.strip(), root=HUB_ROOT)
        return json.dumps({
            "status": "success",
            "pattern": pattern,
            "count": len(matched),
            "files": matched[:100]
        }, indent=2, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({
            "status": "error",
            "message": f"Failed to find files matching '{pattern}': {exc}"
        }, ensure_ascii=False)


def dnk_get_architecture_map(**kwargs: Any) -> str:
    """
    Returns the SSOT structural architecture map of DNK OS monorepo (apps, services, core, scripts).

    Returns:
        JSON string containing the architecture breakdown and key entrypoints.
    """
    return json.dumps({
        "status": "success",
        "architecture_map": STRUCTURE_INDEX
    }, indent=2, ensure_ascii=False)


def get_resolve_symbol_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_resolve_symbol",
            "description": "Instantly locate where any class, function, interface, type, or constant is defined in the repository (<20ms).",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Symbol name or substring to search for (e.g. 'TaskForestNode', 'CanvasEngine', 'TaskDNA')."
                    }
                },
                "required": ["symbol"]
            }
        }
    }


def get_find_files_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_find_files",
            "description": "Quickly search for repository files matching a path or name fragment without running find.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Path fragment to search (e.g. 'task_forest', 'canvas', 'sync')."
                    }
                },
                "required": ["pattern"]
            }
        }
    }


def get_architecture_map_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_get_architecture_map",
            "description": "Get the SSOT architecture map of apps, services, core engines, and canonical scripts.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_resolve_symbol",
        toolset="architecture",
        schema=get_resolve_symbol_schema(),
        handler=dnk_resolve_symbol,
        emoji="🔍"
    )
    registry.register(
        name="dnk_find_files",
        toolset="architecture",
        schema=get_find_files_schema(),
        handler=dnk_find_files,
        emoji="📁"
    )
    registry.register(
        name="dnk_get_architecture_map",
        toolset="architecture",
        schema=get_architecture_map_schema(),
        handler=dnk_get_architecture_map,
        emoji="🗺️"
    )
except Exception:
    pass
