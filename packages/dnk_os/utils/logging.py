# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/utils/logging.py"
# purpose: "Structured JSON logging utilities for DNK OS (re-exports from canonical packages.utils.logging)"
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Structured logging utilities for DNK OS (redirects to canonical packages.utils.logging)."""

from packages.utils.logging import JSONFormatter, setup_logging

__all__ = ["JSONFormatter", "setup_logging"]
