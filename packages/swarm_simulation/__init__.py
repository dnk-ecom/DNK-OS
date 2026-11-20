# --- DNK-MRH-HEADER ---
# mrh_id: "packages/swarm_simulation/__init__.py"
# purpose: "Root package entrypoint for DNK OS Swarm Simulation and Synthetic Customer Engine."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "Gerych Prime & Antigravity"
# --- END DNK-MRH-HEADER ---

"""DNK OS Swarm Simulation Package.

Provides high-velocity, clean-room synthetic customer cohort generation,
psychographic profiling, and multi-step e-commerce/marketing funnel simulation.
"""

from packages.swarm_simulation.models import (
    BuyerMindset,
    CohortReport,
    CustomerPersona,
    FunnelStep,
    FunnelStepType,
    ObjectionType,
    ProductSeed,
    PsychographicProfile,
    StepResult,
)
from packages.swarm_simulation.generator import SyntheticCustomerGenerator
from packages.swarm_simulation.funnel_simulator import FunnelSimulationEngine

__all__ = [
    "BuyerMindset",
    "ObjectionType",
    "FunnelStepType",
    "PsychographicProfile",
    "CustomerPersona",
    "FunnelStep",
    "StepResult",
    "ProductSeed",
    "CohortReport",
    "SyntheticCustomerGenerator",
    "FunnelSimulationEngine",
]
