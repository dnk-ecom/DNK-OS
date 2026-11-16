# 🛍️ Shopify CRO Loyalty, Points Shop & Metered Billing Patterns

---
mrh_id: "skills/software-development/sota-repository-assimilation/references/shopify_cro_loyalty_and_metered_billing_patterns.md"
purpose: "Assimilated patterns for Shopify OS 2.0 CRO app blocks, loyalty engines, and metered billing."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-26"
author: "DNK-e.com Maksym & Gerych Prime"
---

## 📌 Context & Upstream Source
Assimilated from `Omar92953/the-ultimate-cro-app` (commit `41e1680`, live `cro-toolbox-72`).

## 🧱 Key Architectural Patterns

### 1. Theme Block Budget Conservation (30-Block & 100KB Limit)
Shopify Online Store 2.0 enforces strict quotas on app blocks:
- **Max Blocks per Template:** 30 blocks.
- **Max Liquid Size:** 100 KB total per section/block file.

**Solution: Polymorphic Router Block (`ucs-section.liquid`)**:
Instead of publishing 8 individual blocks (countdown timer, sticky ATC, trust badges, bundle widget, social proof, cross-sell carousel, etc.), provide a single polymorphic block with an internal dispatcher:
```liquid
{% case block.settings.widget_type %}
  {% when 'countdown' %}
    {% render 'ucs-countdown', settings: block.settings %}
  {% when 'sticky_atc' %}
    {% render 'ucs-sticky-atc', settings: block.settings %}
  {% when 'loyalty_pill' %}
    {% render 'ucs-loyalty-pill', settings: block.settings %}
  {% else %}
    {% comment %}Default or fallback{% endcomment %}
{% endcase %}
```
This reduces block quota consumption from 8+ down to 1 while keeping snippet files modular and within the 100 KB compile budget.

### 2. Shopify App Events API & Overdraft Metered Billing
Rather than hard plan lockouts when a merchant exceeds thresholds, employ consumption meters via the Shopify App Events API:
- `live-shipments`: $0.04 per shipment above quota.
- `loyalty-orders`: $0.05 per loyalty redemption order.
- `loyalty-emails`: $0.002 per transactional notification email sent.

**Graceful Degradation Invariant**:
- Store plan downgrade status without deleting merchant loyalty ledger or points configuration.
- Automatically re-enable locked features idempotently upon plan re-upgrade.

### 3. Points Shop & Cart Validation Function Guard
When products are flagged as "Points Only" (free with points, non-purchasable via fiat currency):
- **Storefront Display:** Hide from standard product grids and collections; render dedicated Points Shop interface.
- **Shopify Function (Cart & Checkout Validation):** Intercept checkout. If cart contains a points-only item and customer points balance < required points, reject line item with user-facing validation error.
- **Idempotency:** Points deduction must use an idempotent mutation hash (`customer_id + order_id + timestamp_bucket`) to prevent duplicate redemption on webhook replay.

### 4. Guest Checkout Loyalty Reconciliation
- Allow guest checkouts to earn points by recording pending points tied to `order.customer.email`.
- Enforce `LoyaltyProgram.countFrom` cutoff timestamp so retroactive points are not calculated prior to program inception.
- When guest registers an account with the matching email, reconcile pending ledger entries into active balance.

### 5. OS 2.0 Theme Quirks & Dawn Hardening
- **Dawn Installment Forms:** Skip hidden installment forms placed before main purchase buttons when injecting sticky ATC or buy buttons.
- **Header Link Duplication:** Filter out duplicate hidden heading anchors when parsing DOM for sticky headers.
- **RTL & Multi-Language:** Built-in support for RTL scripts (Arabic, Hebrew, Persian, Urdu) using CSS logical properties (`margin-inline-start`, `inset-inline-end`).
