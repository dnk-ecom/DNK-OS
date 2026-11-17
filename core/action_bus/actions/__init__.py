# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/actions/__init__.py"
# purpose: "Standard Dual-Surface Action definitions and bootstrap loaders for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
# --- END DNK-MRH-HEADER ---

from core.action_bus.actions.canvas_actions import register_canvas_actions

def register_all_standard_actions() -> None:
    """Bootstrap and register all standard domain actions into the shared registry."""
    register_canvas_actions()

__all__ = ["register_all_standard_actions", "register_canvas_actions"]
