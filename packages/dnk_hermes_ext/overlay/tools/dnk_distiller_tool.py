# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_distiller_tool.py"
# purpose: "Native Hermes tool for querying and recording Error Distillation solutions and self-healing fixes."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-08-28"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKDistillerTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DISTILLATION_FILE = HUB_ROOT / "docs" / "scones" / "error_distillations.json"

DEFAULT_DISTILLATIONS = [
    {
        "pattern": r"(socket|network|egress|getaddrinfo|connection refused|block_network)",
        "category": "NETWORK_SOCKET_EGRESS",
        "root_cause": "Outbound socket call during isolated test environment violating zero egress invariant.",
        "solution": "Set FIXTURE_MODE=true or implement mock transport override in service constructor (_is_test_mode)."
    },
    {
        "pattern": r"(ModuleNotFoundError|No module named 'apps\.)",
        "category": "MODULE_IMPORT_PATH",
        "root_cause": "Module exists in apps/ but was not synced to root apps/ or PYTHONPATH.",
        "solution": "Sync the service/router from apps to root apps/ using cp, or ensure rootdir pytest config includes both."
    },
    {
        "pattern": r"(404|Not Found.*router|router.*404)",
        "category": "FASTAPI_ROUTER_UNMOUNTED",
        "root_cause": "FastAPI router was created but not registered via app.include_router() in apps/api/main.py.",
        "solution": "Import the router in apps/api/main.py and add app.include_router(module.router, prefix='/api/...')."
    },
    {
        "pattern": r"(Redis.*connection|ConnectionRefusedError.*6379|redis\.exceptions)",
        "category": "REDIS_FALLBACK_MISCONFIGURATION",
        "root_cause": "Redis live client attempted connection to localhost:6379 during unit tests.",
        "solution": "Use InMemoryRedisFallback when _is_test_mode() is True, and ensure is_connected returns True in fallback."
    },
    {
        "pattern": r"(Vault.*8200|is_authenticated.*live)",
        "category": "VAULT_HEALTHCHECK_LIVE_HTTP",
        "root_cause": "VaultClient is_healthy() made a live network call to port 8200 instead of checking cached status.",
        "solution": "Return self._is_vault_connected cached boolean rather than calling self._client.is_authenticated()."
    },
    {
        "pattern": r"(AttributeError:.*model_dump|\.dict\(\))",
        "category": "PYDANTIC_V2_MIGRATION",
        "root_cause": "Using legacy Pydantic v1 .dict() method instead of v2 .model_dump().",
        "solution": "Replace .dict() with .model_dump() across all domain model calls."
    }
]


def _load_knowledge_base() -> List[Dict[str, Any]]:
    if not DISTILLATION_FILE.exists():
        DISTILLATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        DISTILLATION_FILE.write_text(json.dumps(DEFAULT_DISTILLATIONS, indent=2), encoding="utf-8")
        return DEFAULT_DISTILLATIONS
    try:
        return json.loads(DISTILLATION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_DISTILLATIONS


def _save_knowledge_base(kb: List[Dict[str, Any]]) -> None:
    DISTILLATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    DISTILLATION_FILE.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")


def dnk_query_error_solutions(
    error_text: str,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Queries the Error Distillation database for known workarounds or distilled solutions matching an error.
    """
    kb = _load_knowledge_base()
    matched_solutions = []

    for item in kb:
        pat = item.get("pattern", "")
        if pat and re.search(pat, error_text, re.IGNORECASE):
            matched_solutions.append(item)

    if matched_solutions:
        best = matched_solutions[0]
        return json.dumps({
            "status": "success",
            "has_known_solution": True,
            "category": best.get("category", "MATCHED_DISTILLATION"),
            "root_cause": best.get("root_cause"),
            "recommended_action": best.get("solution"),
            "all_matches": len(matched_solutions),
            "workspace_id": workspace_id,
        }, indent=2, ensure_ascii=False)

    return json.dumps({
        "status": "not_found",
        "has_known_solution": False,
        "category": "UNKNOWN_ERROR",
        "workspace_id": workspace_id,
        "recommended_action": "Inspect traceback carefully. Check AST syntax and relative imports.",
        "distilled_advice": "No exact pattern match in SCONES memory. After resolving, please call dnk_record_error_solution."
    }, indent=2, ensure_ascii=False)


def dnk_record_error_solution(
    error_text: str,
    solution_text: str,
    root_cause: str,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Stores a validated error fix into the Error Distillation long-term database for self-healing in future runs.
    """
    kb = _load_knowledge_base()
    new_entry = {
        "pattern": error_text[:80].strip(),
        "category": "DYNAMIC_AGENT_DISTILLED",
        "root_cause": root_cause,
        "solution": solution_text,
        "recorded_at": int(time.time()),
        "workspace_id": workspace_id
    }
    kb.append(new_entry)
    _save_knowledge_base(kb)

    return json.dumps({
        "status": "success",
        "root_cause": root_cause,
        "workspace_id": workspace_id,
        "message": "Successfully recorded distilled error resolution in Self-Healing SCONES database."
    }, indent=2, ensure_ascii=False)


def get_distiller_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "dnk_query_error_solutions",
                "description": "Queries the Error Distillation database to find known fixes and workarounds for a given error or exception.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "error_text": {"type": "string", "description": "Error traceback or failure log."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["error_text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dnk_record_error_solution",
                "description": "Records a solved error and its fix into the long-term Self-Healing database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "error_text": {"type": "string", "description": "Error that was encountered."},
                        "solution_text": {"type": "string", "description": "How the error was resolved."},
                        "root_cause": {"type": "string", "description": "Underlying root cause."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["error_text", "solution_text", "root_cause"]
                }
            }
        }
    ]


try:
    from tools import registry
    for schema in get_distiller_schemas():
        name = schema["function"]["name"]
        handler = dnk_query_error_solutions if name == "dnk_query_error_solutions" else dnk_record_error_solution
        registry.register(
            name=name,
            toolset="healing",
            schema=schema,
            handler=handler,
        )
except Exception:
    pass
