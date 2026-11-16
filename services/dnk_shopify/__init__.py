# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/__init__.py"
# purpose: "Sovereign Brick dnk_shopify package root for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

from .runtime.local_storefront import LocalStorefrontManager

__all__ = ["LocalStorefrontManager"]
