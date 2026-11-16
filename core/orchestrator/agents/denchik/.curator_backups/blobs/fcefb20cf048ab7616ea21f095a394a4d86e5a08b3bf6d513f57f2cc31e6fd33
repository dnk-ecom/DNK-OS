# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/shopify-theme-ast-engineering/references/shopify_dynamic_pdp_playbook_and_data_contracts.md"
# purpose: "Reference Playbook: Data-Driven Dynamic PDPs, Typed Metafields Contracts, and Zero-Drift Deployment Gates."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-29"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛍️ Dynamic PDP Engineering Playbook & Typed Metafields Contract

This reference captures production-grade patterns distilled from the SOTA Dynamic PDP Playbook (MIT) for replacing fragmented product-specific Liquid templates with a single, high-performance, data-driven Product Detail Page.

---

## 🎯 1. Core Architectural Invariants

1. **Shopify Native Object as SSOT**:
   - Product identity, title, variants, prices, availability, collections, and featured media MUST originate from the native `product` object.
   - Never mirror or hardcode commerce properties in external scripts or theme settings.

2. **Strict Typed Metafield Access**:
   - Always access modern Liquid metafields using `.value` unwrapping (e.g. `product.metafields.custom.parent_collection.value`).
   - Iterate typed `list.product_reference` objects directly without regex parsing or manual handle resolution.

3. **Zero False Fallbacks (Anti-Slop Gating)**:
   - Optional sections (feature video, technical specs, editorial profiles) MUST have a strict presence predicate.
   - A video section MUST disappear entirely if video media is missing — never fall back to the product's primary image or a generic placeholder.

---

## 📋 2. Standard Metafields Data Contract

| Metafield Key | Liquid Type | Purpose | Validation Gate |
| :--- | :--- | :--- | :--- |
| `custom.membership_products` | `list.product_reference` | Optional add-on services or membership plans | Variant available & `service_product != blank` |
| `custom.parent_collection` | `collection_reference` | Preferred family collection for related recommendations | Current product must exist in `parent_collection.products` |
| `custom.content_profile` | `metaobject_reference` | Modular editorial blocks and specs | `profile.content_modules.value` non-empty |
| `custom.finance_months` | `integer` | Divisor for instalment and monthly price calculation | Fallback to `36` if null/invalid |
| `custom.specification_media` | `file_reference` | Blueprint, sizing table, or schematic graphic | Strictly hide container if file is absent |

---

## 🔄 3. Collection Precedence & Family Gating Algorithm

When rendering related products or upsells, avoid cross-pollinating disparate catalog lines:

```liquid
{% liquid
  assign preferred_collection = product.metafields.custom.parent_collection.value
  assign family_collection = blank

  if preferred_collection != blank
    for assigned_collection in product.collections
      if assigned_collection.id == preferred_collection.id
        assign family_collection = assigned_collection
        break
      endif
    endfor
  endif

  if family_collection == blank
    assign family_collection = product.collections.first
  endif
%}

{% if family_collection != blank %}
  <section class="related-products" data-collection="{{ family_collection.handle }}">
    <h2>Other {{ family_collection.title }}</h2>
    <ul>
      {% assign rendered = 0 %}
      {% for related_product in family_collection.products %}
        {% if related_product.id != product.id and related_product.available %}
          <li>
            <a href="{{ related_product.url }}">
              {{ related_product.featured_image | image_url: width: 600 | image_tag: loading: 'lazy', alt: related_product.title }}
              <span>{{ related_product.title }}</span>
              <strong>{{ related_product.price | money }}</strong>
            </a>
          </li>
          {% assign rendered = rendered | plus: 1 %}
          {% if rendered == 4 %}{% break %}{% endif %}
        {% endif %}
      {% endfor %}
    </ul>
  </section>
{% endif %}
```

---

## ⚡ 4. Event-Driven Variant & Financing Synchronization (Vanilla JS)

Avoid heavy frameworks or global state managers. Synchronize prices, compare-at badges, stock status, and finance divisors via clean native CustomEvents:

```javascript
(() => {
  'use strict';

  const root = document.querySelector('[data-dynamic-pdp]');
  if (!root) return;

  const variants = JSON.parse(root.querySelector('[data-variants-json]').textContent);
  const variantInput = root.querySelector('[name="id"]');
  const price = root.querySelector('[data-price]');
  const compare = root.querySelector('[data-compare-price]');
  const availability = root.querySelector('[data-availability]');
  const financeNodes = document.querySelectorAll('[data-finance-monthly]');
  const financeMonths = Number(root.dataset.financeMonths) || 36;

  const money = cents => new Intl.NumberFormat(document.documentElement.lang || 'en-GB', {
    style: 'currency',
    currency: root.dataset.currency || 'GBP'
  }).format(cents / 100);

  function applyVariant(variant) {
    if (!variant) return;

    variantInput.value = variant.id;
    price.textContent = money(variant.price);

    const onSale = Number(variant.compare_at_price || 0) > Number(variant.price || 0);
    compare.hidden = !onSale;
    if (onSale) compare.textContent = money(variant.compare_at_price);

    availability.textContent = variant.available ? 'In stock' : 'Sold out';
    financeNodes.forEach(node => {
      node.textContent = money(Math.ceil(Number(variant.price) / financeMonths));
    });

    root.dispatchEvent(new CustomEvent('pdp:variant-change', {
      bubbles: true,
      detail: { variant }
    }));
  }

  root.addEventListener('change', event => {
    if (!event.target.matches('[data-option-value]')) return;
    const selectedId = Number(root.querySelector('[data-variant-select]').value);
    applyVariant(variants.find(v => v.id === selectedId));
  });
})();
```

---

## 🛡️ 5. Zero-Drift Deployment Protocol (QA & Release Gate)

1. **Static Pre-Flight**:
   ```bash
   node --check assets/*.js
   shopify theme check --fail-level error
   ```
2. **Explicit Allowlist Deploy**:
   - Always push feature files with `--only` and `--nodelete` to an unpublished staging theme duplicate:
   ```bash
   shopify theme push --theme <DRAFT_THEME_ID> --only "sections/dynamic-pdp.liquid,assets/pdp.js,assets/pdp.css" --nodelete
   ```
3. **Layout Hash Guard**:
   - Check the SHA-256 hash of `layout/theme.liquid` before and after deployment. If the layout hash changes during a template-level release, trigger immediate rollback.
4. **Reversible Rollback**:
   - Restore only backed-up feature files from the allowlist. Never push an uninspected full-theme archive to fix a localized snippet error.

---

## 🧩 6. Static Clone to Native Customizer Block Conversion (Zero-Trash Protocol)

When converting cloned or static HTML PDP funnels into native 100% Theme Customizer-ready Shopify OS 2.0 templates:

1. **Purge Parasitic Base Blocks from `sections.main`**:
   - Base themes (Shrine, Dawn, Tinker) often retain legacy blocks (`sticky_atc`, `media_slider`, `justtext`, `judge_me_reviews_preview_badge`, duplicate `collapsible_tab` accordions) inside `templates/product.*.json`.
   - Remove both the keys in `sections.main.blocks` and their IDs in `sections.main.block_order` when bespoke PDP sections (`sticky-cta`, custom review carousels, custom hero highlights) are active.
2. **Convert Custom `@liquid` Escape Blocks into Native `main-product.liquid` Blocks**:
   - Never leave `{"type": "custom_liquid", "settings": {"custom_liquid": "{% render 'my-snippet' %}"}}` in production templates — merchants cannot edit text, badges, or images inside `custom_liquid`.
   - Register dedicated block types in `sections/main-product.liquid` (both in the `{%- case block.type -%}` switch with `{{ block.shopify_attributes }}` and in the `{% schema %}` `"blocks"` array) and pass `block: block, product: product` to the snippet.
   - Note: Inspect `sections/main-product.liquid` for pre-existing trailing commas before the closing `]` of `"blocks"` before parsing or appending with `json.loads()`.
3. **Dual-Source Image Fallback (`image_picker` + Theme Asset Filename)**:
   - In customizer blocks (trust cards, video posters, anatomy zones, bundle gifts), support both `block.settings.image` (`type: "image_picker"`, rendered via `image_url: width: ...`) and a fallback `block.settings.image_asset` (`type: "text"`, rendered via `asset_url`) so existing local theme assets render out-of-the-box before a merchant uploads custom media in the Theme Editor.
4. **Template-to-Schema Cross-Validation Script**:
   - Before committing, parse `templates/product.*.json` alongside every referenced `sections/<type>.liquid` `{% schema %}` to assert:
     - Every section ID in `order` exists in `sections`.
     - Every block `type` in `sections.<id>.blocks` is declared in that section's schema `"blocks"` array.
     - Every block ID in `block_order` exists in `blocks` (and vice versa).
     - All `text`/`textarea` schema settings omit `"default": ""` (Shopify rejects empty string defaults).
5. **GitHub Integration Auto-Sync Verification**:
   - When Shopify CLI (`shopify theme push`) lacks an active interactive session, pushing to the connected GitHub branch (e.g. `origin/Dev`) triggers Shopify's native GitHub Theme Sync within 3–5 seconds. Verify live deployment directly via headless browser against `?preview_theme_id=<THEME_ID>&view=<template_suffix>` across `375px`, `390px`, `768px`, and `1280px` viewports (`document.documentElement.scrollWidth <= window.innerWidth`).

