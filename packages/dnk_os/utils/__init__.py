# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/utils/__init__.py"
# purpose: "Utility modules initialization for DNK OS"
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""DNK OS Utilities (forwards to canonical packages.utils)."""

from packages.utils.logging import JSONFormatter, setup_logging

__all__ = ["JSONFormatter", "setup_logging"]
