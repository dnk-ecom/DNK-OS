# --- DNK-MRH-HEADER ---
# mrh_id: "core/project/__init__.py"
# purpose: "DNK Core Project Management Control Plane package."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

from core.project.project_engine import ProjectEngine, ProjectSummary

__all__ = ["ProjectEngine", "ProjectSummary"]
