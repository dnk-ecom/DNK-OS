# --- DNK-MRH-HEADER ---
# mrh_id: "references/packet2_monolith_decomposition_playbook.md"
# purpose: "Playbook for Packet 2: Shopify PDP Monolith Decomposition into Modular OS 2.0 Tinker Blocks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🧱 Packet 2: Product Monolith Decomposition & Theme Blocks Playbook

This reference provides the battle-tested methodology for decomposing massive monolithic Liquid product templates (e.g., 20,000+ line `sections/main-product.liquid`) into modular, high-performance Online Store 2.0 Theme Blocks.

---

## 🎯 Architecture Goals & Invariants

1. **Size Target**: Monolithic `sections/main-product.liquid` reduced from >20,000 lines to <300 lines.
2. **Atomic Units**: Extract independent features into `blocks/tinker-dnk-*.liquid`:
   - `tinker-dnk-bundle-offer.liquid`
   - `tinker-dnk-countdown-timer.liquid`
   - `tinker-dnk-delivery-estimator.liquid`
   - `tinker-dnk-guarantee-benefits.liquid`
   - `tinker-dnk-hero-banner.liquid`
   - `tinker-dnk-quantity-breaks.liquid`
   - `tinker-dnk-scrolling-ticker.liquid`
   - `tinker-dnk-sticky-atc.liquid`
3. **Editor Selection Invariant**: Every block root container MUST include `{{ block.shopify_attributes }}`.
4. **Scope Isolation**: 0 `{% include %}` tags; strictly `{% render 'snippet-name', param: value %}`.
5. **Schema Synchronization**: Section schema must explicitly declare allowable block types:
   ```json
   "blocks": [
     { "type": "@theme" },
     { "type": "@app" },
     { "type": "tinker-dnk-countdown-timer" },
     { "type": "tinker-dnk-trust-badges" }
   ]
   ```
6. **Template Integration**: Connect blocks inside `templates/product.json` under `"sections"` -> `"main"` (or `"product-information"`) -> `"blocks"`, updating `"block_order"` array deterministically.

---

## 🧪 Automated Verification Script Recipe

When validating Packet 2 completion, execute programmatic audit using `CodeReviewRuleSniffer` and `AuditStateMachine`:

```python
from pathlib import Path
from core.orchestrator.code_review_rules import CodeReviewRuleSniffer
from core.orchestrator.audit_state_machine import AuditStateMachine, ReviewFinding

# 1. Check monolith line count
pdp_path = Path("services/dnk_shopify/DNK-e.com/sections/main-product.liquid")
lines = pdp_path.read_text(encoding="utf-8").splitlines()
assert len(lines) < 500, f"Monolith too large: {len(lines)} lines"

# 2. Check Theme Blocks
blocks_dir = Path("services/dnk_shopify/DNK-e.com/blocks")
sniffer = CodeReviewRuleSniffer()
for block_path in blocks_dir.glob("tinker-*.liquid"):
    content = block_path.read_text(encoding="utf-8")
    assert "{{ block.shopify_attributes }}" in content or "{{block.shopify_attributes}}" in content
    assert "{% include" not in content
    # Note: sniffer requires Path object, not str
    rules = sniffer.sniff_rules_for_file(block_path)

# 3. Reconcile with AuditStateMachine
state_machine = AuditStateMachine()
reconciled = state_machine.reconcile_commit("HEAD-PACKET-2", findings=[])
assert reconciled.total_open == 0
```
