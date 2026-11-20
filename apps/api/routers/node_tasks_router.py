# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/node_tasks_router.py"
# purpose: "FastAPI Router for Node Based Tasks & Ideas System: DAG Dependencies, Stage Gating, and FastMCP Microkernel Integration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.5.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Denchik (Sovereign Builder)"
# --- END DNK-MRH-HEADER ---

"""FastAPI Router module for Node Based Tasks & Ideas System."""
import apps.api.routers.tasks.node as _mod
from apps.api.routers.tasks.node import *  # noqa: F401, F403
from apps.api.routers.tasks.node import router

for _name in dir(_mod):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_mod, _name)
