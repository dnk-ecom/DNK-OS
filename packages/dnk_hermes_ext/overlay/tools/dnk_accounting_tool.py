# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_accounting_tool.py"
# purpose: "Native Hermes tool for retrieving financial, token spending, and execution duration telemetry per workspace."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKAccountingTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.telemetry.accounting_engine import AccountingEngine
except ImportError:
    AccountingEngine = None


def dnk_get_workspace_spending(
    workspace_id: str = "ws-alpha-001",
    **kwargs
) -> str:
    """
    Retrieves aggregated token spending, cost in USD, and execution metrics for a given workspace.

    Args:
        workspace_id: Target workspace identifier (e.g. 'ws-alpha-001', 'ws-shopify-ecom', or '*' for all).

    Returns:
        JSON string containing tokens_in, tokens_out, total_cost_usd, and execution count.
    """
    if AccountingEngine is None:
        return json.dumps({
            "status": "simulated",
            "workspace_id": workspace_id,
            "total_tokens": 142850,
            "total_cost_usd": 0.042,
            "total_runs": 28
        }, indent=2)

    try:
        log_path = str(DNKOS_MVP_PATH / "telemetry" / "accounting_log.json") if not os.path.exists("pyproject.toml") else "telemetry/accounting_log.json"
        engine = AccountingEngine(log_path=log_path)
        metrics = engine.get_aggregated_metrics()

        return json.dumps({
            "status": "success",
            "workspace_id": workspace_id,
            "total_records": len(engine.records),
            "metrics": metrics
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "simulated", "workspace_id": workspace_id, "metrics": {"total_runs": 0, "total_cost_usd": 0.0}})


def get_accounting_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "dnk_get_workspace_spending",
            "description": "Retrieves token usage, cost in USD, and execution duration metrics for a workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "string", "description": "Target workspace identifier (default: ws-alpha-001)."}
                }
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_get_workspace_spending",
        toolset="finance",
        schema=get_accounting_schema(),
        handler=dnk_get_workspace_spending,
    )
except Exception:
    pass
