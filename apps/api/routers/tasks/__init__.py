# --- DNK-MRH-HEADER ---
# mrh_id: "apps/api/routers/tasks/__init__.py"
# purpose: "Domain package aggregator for Task routers (TaskDNA, TaskForest, NodeTasks)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "3.1.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from fastapi import APIRouter

try:
    from .dna import router as dna_router, router
except Exception:
    dna_router = None
    router = None

try:
    from .forest import router as forest_router
except Exception:
    forest_router = None

try:
    from .node import router as node_router
    if router is None:
        router = node_router
except Exception:
    node_router = None

try:
    from .dna_v1 import router as dna_v1_router
except Exception:
    dna_v1_router = None

__all__ = [
    "router",
    "dna_router",
    "forest_router",
    "node_router",
    "dna_v1_router",
]
