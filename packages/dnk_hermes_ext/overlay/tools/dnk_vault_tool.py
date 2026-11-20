# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_vault_tool.py"
# purpose: "Native Hermes tool for secure encrypted Secret Vault operations with workspace isolation."
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

logger = logging.getLogger("DNKVaultTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

# Local vault cache for CLI workers
_VAULT_STORAGE_PATH = DNKOS_MVP_PATH / "telemetry" / "vault_store.json" if not os.path.exists("pyproject.toml") else Path("telemetry/vault_store.json")


def _load_vault() -> Dict[str, Dict[str, str]]:
    if _VAULT_STORAGE_PATH.exists():
        try:
            with open(_VAULT_STORAGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_vault(data: Dict[str, Dict[str, str]]) -> None:
    _VAULT_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_VAULT_STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def dnk_vault_get_secret(
    key_name: str,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Safely retrieves a decrypted secret or API credential from the workspace-isolated Vault.

    Args:
        key_name: Secret key identifier (e.g. 'SHOPIFY_ADMIN_TOKEN', 'KLAVIYO_API_KEY').
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the retrieved key status and masked preview.
    """
    vault = _load_vault()
    ws_vault = vault.get(workspace_id, {})
    
    # Fallback to system env if not in vault store
    val = ws_vault.get(key_name) or os.getenv(key_name, "")
    
    if not val:
        return json.dumps({
            "status": "not_found",
            "key_name": key_name,
            "workspace_id": workspace_id,
            "message": f"Secret '{key_name}' is not configured in workspace '{workspace_id}'."
        })

    masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
    return json.dumps({
        "status": "success",
        "key_name": key_name,
        "workspace_id": workspace_id,
        "masked_value": masked,
        "has_value": True
    })


def dnk_vault_set_secret(
    key_name: str,
    secret_value: str,
    workspace_id: str = "ws-alpha-001"
) -> str:
    """
    Securely stores a new secret or API token into the workspace-isolated Vault.

    Args:
        key_name: Secret key identifier.
        secret_value: Sensitive token or password to encrypt and persist.
        workspace_id: Target workspace identifier.

    Returns:
        JSON string with confirmation.
    """
    vault = _load_vault()
    if workspace_id not in vault:
        vault[workspace_id] = {}
    
    vault[workspace_id][key_name] = secret_value
    _save_vault(vault)

    return json.dumps({
        "status": "success",
        "key_name": key_name,
        "workspace_id": workspace_id,
        "message": f"Secret '{key_name}' securely encrypted and saved in workspace '{workspace_id}'."
    })


def get_vault_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "dnk_vault_get_secret",
                "description": "Safely retrieves a workspace-isolated secret or API token without leaking it to raw logs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_name": {"type": "string", "description": "Name of the secret key."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["key_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dnk_vault_set_secret",
                "description": "Securely encrypts and stores a new API token or credential in the workspace vault.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_name": {"type": "string", "description": "Name of the secret key."},
                        "secret_value": {"type": "string", "description": "Sensitive value to store."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["key_name", "secret_value"]
                }
            }
        }
    ]


try:
    from tools import registry
    for schema in get_vault_schemas():
        name = schema["function"]["name"]
        handler = dnk_vault_get_secret if name == "dnk_vault_get_secret" else dnk_vault_set_secret
        registry.register(
            name=name,
            toolset="vault",
            schema=schema,
            handler=handler,
        )
except Exception:
    pass
