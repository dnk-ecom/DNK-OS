# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/shopify_custom_price_colors_and_schema_settings_playbook.md"
# purpose: "Playbook for native schema settings injection (color pickers, custom price styling) across Collection Grids and Featured Collections in Shopify OS 2.0."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🎨 Shopify OS 2.0 Native Section Schema Settings Injection (Custom Price Colors & Swatches)

## 📌 Context & Problem
When migrating between Shopify themes (e.g., Shrine Pro 1.9.0 vs legacy/modified themes), custom styling features present in older versions (like custom card price colors, compare-at price colors, badge overrides) may be missing from newer upstream section schemas.

Relying exclusively on hardcoded CSS or theme custom CSS fields is suboptimal because:
1. Merchants lose the intuitive visual color-picker UI in Shopify Theme Editor.
2. Custom styles may not automatically propagate across dynamic collection templates (`collection.json`, `collection.*.json`, `index.json`).

---

## 🛠️ Canonical Solution Pattern

### 1. Section Liquid Style Block (`sections/main-collection-product-grid.liquid` & `sections/featured-collection.liquid`)
Inject conditional styling in the section's `{%- style -%}` block:

```liquid
{% if section.settings.custompricecolors %}
  .collection-{{ section.id }} .price .price-item,
  #ProductGridContainer .price .price-item {
    color: {{ section.settings.main-pricecolor }};
  }
  .collection-{{ section.id }} s.price-item.price-item--regular,
  #ProductGridContainer s.price-item.price-item--regular {
    color: {{ section.settings.maincompare-pricecolor }};
  }
{% endif %}
```

### 2. Schema Settings Injection (`{% schema %}`)
Under the `"Product card"` / `"Product cards"` header in the section schema, add:

```json
{
  "type": "checkbox",
  "id": "custompricecolors",
  "label": "Enable custom price colors",
  "default": true
},
{
  "type": "color",
  "id": "main-pricecolor",
  "default": "#1F853E",
  "label": "Main price color"
},
{
  "type": "color",
  "id": "maincompare-pricecolor",
  "default": "#000000",
  "label": "Compare price color"
}
```

### 3. Template JSON Propagation
Ensure JSON templates (`templates/collection.json`, `templates/collection.*.json`, `templates/index.json`) contain the matching section settings:

```json
"settings": {
  "custompricecolors": true,
  "main-pricecolor": "#1F853E",
  "maincompare-pricecolor": "#000000"
}
```

---

## 🚀 Live Verification & Deployment via Theme Access API
Upload the modified sections and JSON templates via Theme Access API asset endpoints:
```python
import urllib.request, json

theme_id = "208039182674"
asset_key = "sections/main-collection-product-grid.liquid"
url = f"https://theme-kit-access.shopifyapps.com/cli/admin/api/unstable/themes/{theme_id}/assets.json"
payload = json.dumps({"asset": {"key": asset_key, "value": liquid_content}}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"}, method="PUT")
urllib.request.urlopen(req)
```
Verify live in Shopify Theme Editor that the color picker inputs appear in the right-hand settings panel and reflect immediately in the live preview.
