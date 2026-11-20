# --- DNK-MRH-HEADER ---
# mrh_id: "core/client_cockpit/__init__.py"
# purpose: "Client Cockpit package root."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from core.client_cockpit.engine import ClientCockpitEngine, ClientTicket

__all__ = ["ClientCockpitEngine", "ClientTicket"]
