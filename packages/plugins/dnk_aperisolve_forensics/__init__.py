# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk_aperisolve_forensics/__init__.py"
# purpose: "Package entrypoint for AperiSolve Image Forensics & Steganalysis Plugin"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from .adapter import AperiSolveAdapter

__all__ = ["AperiSolveAdapter"]
