# --- DNK-MRH-HEADER ---
# mrh_id: "core/plugins/__init__.py"
# purpose: "Unified export package for DNK OS Plugin Governance, Engine, and Security Gate"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""DNK OS Plugin Governance, Execution Engine, and Security Sandboxing.

Architectural Distinction:
- `core.plugins`: Plugin Engine, Lifecycle, Security Sandboxing, Policy & Governance.
- `packages.plugins`: Concrete ecosystem plugins (Slack, Notion, Shopify Sync, Test Health).
"""

from core.plugins.models import (
    PluginCard,
    PluginKind,
    PluginLifecycle,
    OriginType,
    EntrypointType,
    RiskLevel,
    OriginInfo,
    EntrypointInfo,
    CapabilitiesInfo,
    PermissionsInfo,
    GovernanceInfo,
    ApprovalRecord,
    CompatibilityInfo,
)
from core.plugins.policy import (
    validate_plugin_card_data,
    validate_plugin_card_file,
    check_lifecycle_transition,
    PluginPolicyError,
)
from core.plugins.plugin_manager import PluginManager, PluginState

__all__ = [
    "PluginCard",
    "PluginKind",
    "PluginLifecycle",
    "OriginType",
    "EntrypointType",
    "RiskLevel",
    "OriginInfo",
    "EntrypointInfo",
    "CapabilitiesInfo",
    "PermissionsInfo",
    "GovernanceInfo",
    "ApprovalRecord",
    "CompatibilityInfo",
    "validate_plugin_card_data",
    "validate_plugin_card_file",
    "check_lifecycle_transition",
    "PluginPolicyError",
    "PluginManager",
    "PluginState",
]
