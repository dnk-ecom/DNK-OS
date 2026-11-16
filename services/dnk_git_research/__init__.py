# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_git_research/__init__.py"
# purpose: "Init file for dnk_git_research service"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-11-04"
# author: "DNK-e.com Maksym & Denchik Prime"
# --- END DNK-MRH-HEADER ---

from services.dnk_git_research.src.git_researcher import GitResearchEngine

__all__ = ["GitResearchEngine"]
