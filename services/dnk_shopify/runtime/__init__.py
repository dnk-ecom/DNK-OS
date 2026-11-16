# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/runtime/__init__.py"
# purpose: "Runtime package initialization for dnk_shopify Sovereign Brick."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from .local_storefront import LocalStorefrontManager

__all__ = ["LocalStorefrontManager"]
