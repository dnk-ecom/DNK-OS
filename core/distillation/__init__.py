# --- DNK-MRH-HEADER ---
# mrh_id: "core/distillation/__init__.py"
# purpose: "Package init for DNK OS Knowledge Distillation subsystem."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-28"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

"""
DNK OS Knowledge Distillation Subsystem.

Combines Google Elephant-Goldfish Model (EGM), Harness² Recursive Tuning,
and EntireIO AST change-impact analysis into a zero-waste knowledge refinery.
"""

from .egm_distiller import (
    EGMDistiller,
    DistillationCandidate,
    DistillationResult,
    ElephantHarvester,
    GoldfishAuditor,
    HarnessComposer,
)

__all__ = [
    "EGMDistiller",
    "DistillationCandidate",
    "DistillationResult",
    "ElephantHarvester",
    "GoldfishAuditor",
    "HarnessComposer",
]
