# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/tools/dnk_shopify_tool.py"
# purpose: "Native Hermes tool for Shopify theme inspection, Liquid AST parsing, and section decomposition."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKShopifyTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except ImportError:
    RuntimeEvent = None
    RuntimeEventBus = None


def dnk_shopify_validate_liquid(content_or_path: str) -> str:
    """
    Validates Liquid syntax, checking for schema validity, balanced tags, and missing closing blocks.

    Args:
        content_or_path: Raw Liquid source code or relative path to a .liquid file.

    Returns:
        JSON string containing validation status, errors, warnings, and schema details.
    """
    code = content_or_path
    file_path = None
    if os.path.exists(content_or_path) and os.path.isfile(content_or_path):
        file_path = content_or_path
        try:
            with open(content_or_path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Could not read file: {e}"})

    errors = []
    warnings = []

    # Check balanced blocks
    tags_to_check = ["if", "for", "unless", "case", "form", "paginate", "capture", "schema", "javascript", "stylesheet"]
    for tag in tags_to_check:
        open_count = len(re.findall(r"\{%-?\s*" + tag + r"\b", code))
        close_count = len(re.findall(r"\{%-?\s*end" + tag + r"\b", code))
        if open_count != close_count:
            errors.append(f"Unbalanced '{tag}' tag: {open_count} open vs {close_count} close (end{tag}).")

    # Extract schema if present
    schema_data = None
    schema_match = re.search(r"\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}", code, re.DOTALL)
    if schema_match:
        raw_schema = schema_match.group(1).strip()
        try:
            schema_data = json.loads(raw_schema)
        except json.JSONDecodeError as jde:
            errors.append(f"Invalid JSON in {{% schema %}}: {jde}")

    # Emit event to Visual Canvas
    if RuntimeEvent and RuntimeEventBus:
        try:
            bus = RuntimeEventBus.get_instance()
            bus.publish(RuntimeEvent(
                tenant_id="tenant-alpha-001",
                workspace_id="ws-shopify-ecom",
                canvas_id="canvas-main-001",
                graph_id="graph-swarm-001",
                thread_id="thread-shopify-validation",
                execution_id="exec-shopify-val",
                node_id="dnk_shopify",
                event_type="artifact.validated",
                sequence_number=1,
                payload={
                    "valid": len(errors) == 0,
                    "errors_count": len(errors),
                    "file_path": file_path or "inline_liquid"
                }
            ))
        except Exception:
            pass

    return json.dumps({
        "status": "success" if len(errors) == 0 else "invalid",
        "file_path": file_path,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "has_schema": schema_data is not None,
        "schema": schema_data
    }, indent=2, ensure_ascii=False)


def dnk_shopify_inspect_theme(theme_path: Optional[str] = None) -> str:
    """
    Scans and summarizes the file hierarchy and architecture of a Shopify theme directory.

    Args:
        theme_path: Path to the theme folder (defaults to 'services/dnk_shopify/DNK-e.com').

    Returns:
        JSON string listing total sections, snippets, templates, and config files.
    """
    target = Path(theme_path) if theme_path else HUB_ROOT / "services" / "dnk_shopify" / "DNK-e.com"
    if not target.exists():
        target = HUB_ROOT / "services" / "dnk_shopify"

    sections = list(target.glob("sections/*.liquid")) + list(target.glob("**/sections/*.liquid"))
    snippets = list(target.glob("snippets/*.liquid")) + list(target.glob("**/snippets/*.liquid"))
    templates = list(target.glob("templates/**/*.liquid")) + list(target.glob("**/templates/**/*.json"))
    assets = list(target.glob("assets/*")) + list(target.glob("**/assets/*"))

    return json.dumps({
        "status": "success",
        "theme_root": str(target.relative_to(HUB_ROOT) if HUB_ROOT in target.parents else target),
        "counts": {
            "sections": len(sections),
            "snippets": len(snippets),
            "templates": len(templates),
            "assets": len(assets)
        },
        "sample_sections": [str(s.name) for s in sections[:5]],
        "sample_snippets": [str(s.name) for s in snippets[:5]]
    }, indent=2, ensure_ascii=False)


def get_dnk_shopify_schema() -> Dict[str, Any]:
    """Returns OpenAI/Hermes tool schema for dnk_shopify_validate_liquid."""
    return {
        "type": "function",
        "function": {
            "name": "dnk_shopify_validate_liquid",
            "description": "Validates Liquid template code or file syntax for Shopify themes, checking schema JSON and tag balance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_or_path": {
                        "type": "string",
                        "description": "Liquid source code or relative path to a .liquid file."
                    }
                },
                "required": ["content_or_path"]
            }
        }
    }


try:
    from tools import registry
    registry.register(
        name="dnk_shopify_validate_liquid",
        toolset="shopify",
        schema=get_dnk_shopify_schema(),
        handler=dnk_shopify_validate_liquid,
    )
except Exception:
    pass
