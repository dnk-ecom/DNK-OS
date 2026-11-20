# --- DNK-MRH-HEADER ---
# mrh_id: "packages/utils/__init__.py"
# purpose: "Canonical DNK OS Shared Utilities Package"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""DNK OS Shared Utilities Package."""

from packages.utils.logging import JSONFormatter, setup_logging

__all__ = ["JSONFormatter", "setup_logging"]
