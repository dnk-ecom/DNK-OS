# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/packet3_theme_settings_and_security_playbook.md"
# purpose: "Playbook for Packet 3: Theme Settings & Security Data (settings_schema, settings_data, Country Blocker, Copy Protection)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Packet 3 Playbook: Theme Settings, Security Data & Country Blocker

## 🎯 Scope & Objectives
1. **`config/settings_schema.json`**: Declare theme-wide settings for `Store Security` and `Currency format` ensuring 100% Shopify OS 2.0 schema validity.
2. **`config/settings_data.json`**: Hydrate default values in `current` and existing theme `presets` (e.g. `presets["Tinker"]`) without deleting or corrupting any theme attributes.
3. **`snippets/disable-copy-protection.liquid`**: Content protection against right-click, image dragging, text selection, and DevTools/Inspect element shortcuts.
4. **`snippets/country-blocker.liquid`**: Hybrid Liquid (server-side `localization.country.iso_code`) and JS (client-side DOM overlay) geoblocking for blocking competitor traffic.
5. **`layout/theme.liquid`**: Clean integration via `{% render %}` right before `</body>`.
6. **Automated Audit Gate**: Verification script (`scripts/validate_shopify_packet3.py`) with `AuditStateMachine` reconciling 0 blocking defects.

---

## 📐 1. `config/settings_schema.json` Structure
Place `Store Security` immediately after `theme_info` for high visibility in Shopify Theme Customizer:

```json
{
  "name": "Store Security",
  "settings": [
    {
      "type": "checkbox",
      "id": "disable_inspect",
      "label": "Disable Inspect / Copy Protection",
      "default": true,
      "info": "Prevents right-click, text selection, image drag, and DevTools shortcuts."
    },
    {
      "type": "select",
      "id": "country_list_function",
      "label": "Country Blocker Mode",
      "options": [
        { "value": "block", "label": "Block countries in list" },
        { "value": "whitelist", "label": "Allow only countries in list" }
      ],
      "default": "block"
    },
    {
      "type": "text",
      "id": "country_list",
      "label": "Country Codes (ISO 3166-1 alpha-2)",
      "default": "",
      "placeholder": "CN, RU, IN",
      "info": "Comma-separated 2-letter uppercase country codes."
    },
    {
      "type": "richtext",
      "id": "country_invalid_error_msg",
      "label": "Access Denied Message",
      "default": "<p>Unfortunately this store is not available in your region.</p>"
    }
  ]
}
```

---

## 💾 2. `config/settings_data.json` Safe Injection Protocol
When updating `settings_data.json`, NEVER overwrite existing dictionaries blindly. Preserve all existing merchant keys and theme preset values:

```python
with open("config/settings_data.json", "r") as f:
    data = json.load(f)

# 1. Update current settings
current = data.setdefault("current", {})
current.setdefault("disable_inspect", True)
current.setdefault("country_list_function", "block")
current.setdefault("country_list", "")
current.setdefault("currency_code_enabled", True)

# 2. Update all presets safely without dropping design tokens
presets = data.setdefault("presets", {})
for preset_name, preset_vals in presets.items():
    preset_vals.setdefault("disable_inspect", True)
    preset_vals.setdefault("country_list_function", "block")
    preset_vals.setdefault("country_list", "")
    preset_vals.setdefault("currency_code_enabled", True)

with open("config/settings_data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 🔒 3. Content Protection (`snippets/disable-copy-protection.liquid`)
### Key Protection Vectors:
1. **CSS Immediate Hardening**:
   ```css
   * { -webkit-user-select: none !important; user-select: none !important; }
   img { pointer-events: none !important; -webkit-user-drag: none !important; }
   input, textarea { -webkit-user-select: text !important; user-select: text !important; }
   ```
2. **Keyboard Event Interception**:
   - `F12`
   - `Ctrl + Shift + I` / `Cmd + Option + I` (DevTools)
   - `Ctrl + Shift + J` / `Cmd + Option + J` (Console)
   - `Ctrl + Shift + C` / `Cmd + Option + C` (Element Inspector)
   - `Ctrl + U` / `Cmd + Option + U` (View Source)
   - `Ctrl + S` / `Cmd + S` (Save Page)
3. **Context Menu Event**:
   - `document.addEventListener('contextmenu', e => e.preventDefault());`

---

## 🌍 4. Country Blocker (`snippets/country-blocker.liquid`)
### Server-Side Evaluation (Liquid):
```liquid
{%- if settings.country_list != blank -%}
  {%- assign raw_list = settings.country_list | upcase | remove: ' ' | split: ',' -%}
  {%- assign current_iso = localization.country.iso_code | upcase -%}
  {%- assign is_matched = false -%}
  {%- for c in raw_list -%}
    {%- if c == current_iso -%}{%- assign is_matched = true -%}{%- break -%}{%- endif -%}
  {%- endfor -%}

  {%- assign should_block = false -%}
  {%- if settings.country_list_function == 'whitelist' -%}
    {%- unless is_matched -%}{%- assign should_block = true -%}{%- endunless -%}
  {%- else -%}
    {%- if is_matched -%}{%- assign should_block = true -%}{%- endif -%}
  {%- endif -%}

  {%- if should_block -%}
    <style>body > *:not(#dnk-country-blocker-screen) { display: none !important; }</style>
    <div id="dnk-country-blocker-screen">
      <div class="dnk-blocker-card">{{ settings.country_invalid_error_msg }}</div>
    </div>
  {%- endif -%}
{%- endif -%}
```

---

## 🧪 5. Programmatic Gate Validation (`AuditStateMachine`)
When constructing test gates via `AuditStateMachine`:
```python
from apps.api.ai_code_review import AuditStateMachine, ReviewFinding, SeverityLevel

state_machine = AuditStateMachine()
findings = []

# Validate findings and reconcile:
state_machine.reconcile_commit("HEAD-PACKET-3", findings)
status = state_machine.get_audit_status()
assert status["blocking_defects_count"] == 0
```
