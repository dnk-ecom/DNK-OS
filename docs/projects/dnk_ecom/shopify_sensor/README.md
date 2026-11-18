<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/projects/dnk_ecom/shopify_sensor/README.md"
purpose: "Drop-in Shopify In-Context Review Sensor for Instant Agent Dispatch via FastMCP & REST."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-11-18"
author: "DNK-e.com Maksym & Antigravity"
--- END DNK-MRH-HEADER --- -->

# ⚡ Shopify In-Context Agentic Review Sensor

Універсальний автономний віджет для будь-якої теми Shopify (Online Store 2.0 / Dawn / Horizon / Minimog / Prestige), який дозволяє клієнту або власнику магазину виділяти будь-який елемент на сторінці кліком та надсилати правку **напряму в мозок агента DNK OS** через FastMCP та REST API.

---

### 🚀 Інструкція зі встановлення (2 кроки):

#### 1. Додати файли у тему:
- Скопіювати `dnk-in-context-sensor.liquid` у папку `snippets/` вашої теми Shopify.
- Скопіювати `dnk-sensor.js` у папку `assets/` вашої теми Shopify.

#### 2. Підключити у `layout/theme.liquid`:
Перед закриваючим тегом `</body>` додати один рядок:
```liquid
{%- if request.design_mode or content_for_header contains 'preview_theme_id' or settings.enable_client_sensor -%}
  {% render 'dnk-in-context-sensor', deal_id: 'deal_noku_2026' %}
{%- endif -%}
```

> **Безпека**: Завдяки умові `request.design_mode or content_for_header contains 'preview_theme_id'`, віджет показується **виключно** у передперегляді теми (Preview Link) або у редакторі теми (Theme Customizer). Звичайні покупці магазину його ніколи не бачать!

---

### 🛠️ Як агент отримує правки через FastMCP:

Агент у середовищі DNK OS має 3 нативні FastMCP інструменти у `dnk-kernel`:

1. `get_client_tickets(deal_id, status)`:
   - Запитує всі відкриті правки клієнта зі сторінки магазину (селектор, секція, блок, коментар).
2. `resolve_client_ticket(deal_id, ticket_id, resolution_note)`:
   - Закриває тікет, записує commit sha або опис фіксу, оновлює статус у Client Cockpit.
3. `get_cockpit_status(deal_id)`:
   - Повертає повну аналітику: 6 етапів дорожньої карти, ліміти правок та артефакти.
