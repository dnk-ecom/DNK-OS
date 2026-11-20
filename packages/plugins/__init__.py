# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/__init__.py"
# purpose: "DNK OS Canonical User & Ecosystem Plugins Package"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""DNK OS User & Integration Plugins Package.

Architectural Distinction:
- `core.plugins`: Plugin Engine, Lifecycle, Security Sandboxing, Policy & Governance.
- `packages.plugins`: Concrete ecosystem plugins (Slack, Notion, Shopify Sync, Test Health).
"""

from typing import List

AVAILABLE_PLUGINS: List[str] = [
    "slack_plugin",
    "notion_plugin",
    "dnk_test_health",
    "dnk_shopify_sync",
]

__all__ = ["AVAILABLE_PLUGINS"]
