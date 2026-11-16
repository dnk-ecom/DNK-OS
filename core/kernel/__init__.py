# --- DNK-MRH-HEADER ---
# mrh_id: "core/kernel/__init__.py"
# purpose: "Package entrypoint and public interface for DNK OS Agentic Microkernel."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-13"
# author: "Antigravity & Gerych Prime & DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""DNK OS Agentic Microkernel Package."""

from core.kernel.contracts import (
    AgentCapsuleSpec,
    CompanionCritiqueBlock,
    KernelCompletionReceipt,
    KernelDecisionReceipt,
    KernelTaskRequest,
    KernelTriageReceipt,
    ThoughtCompanionRequest,
    ThoughtCompanionResponse,
)
from core.kernel.thought_companion import (
    ASSIMILATED_GLOBAL_PATTERNS,
    CANONICAL_ROLE_CAPSULES,
    FirstThoughtCompanionAgent,
    get_thought_companion,
)

# Re-export legacy FastMCPKernel for backward compatibility with existing tests
try:
    import importlib.util
    from pathlib import Path
    _legacy_kernel_path = Path(__file__).resolve().parent.parent / "kernel.py"
    if _legacy_kernel_path.exists():
        _spec = importlib.util.spec_from_file_location("core._legacy_kernel", _legacy_kernel_path)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        FastMCPKernel = getattr(_mod, "FastMCPKernel", None)
        run_cli_command = getattr(_mod, "run_cli_command", None)
        create_fastmcp_server = getattr(_mod, "create_fastmcp_server", None)
    else:
        FastMCPKernel = None
        run_cli_command = None
        create_fastmcp_server = None
except Exception:
    FastMCPKernel = None
    run_cli_command = None
    create_fastmcp_server = None

__all__ = [
    "ASSIMILATED_GLOBAL_PATTERNS",
    "AgentCapsuleSpec",
    "CANONICAL_ROLE_CAPSULES",
    "CompanionCritiqueBlock",
    "FirstThoughtCompanionAgent",
    "KernelTaskRequest",
    "KernelTriageReceipt",
    "KernelDecisionReceipt",
    "KernelCompletionReceipt",
    "ThoughtCompanionRequest",
    "ThoughtCompanionResponse",
    "FastMCPKernel",
    "run_cli_command",
    "create_fastmcp_server",
    "get_thought_companion",
]
