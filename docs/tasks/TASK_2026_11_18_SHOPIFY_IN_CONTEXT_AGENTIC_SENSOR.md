---
title: "PSOD DELEGATION CONTRACT: Shopify In-Context Agentic Review Sensor & FastMCP Loop (DEC-147)"
description: "Canonical PSOD Delegation Contract: Shopify In-Context Agentic Review Sensor & FastMCP Dispatch Loop (DEC-147)"
mrh_id: "docs/tasks/TASK_2026_11_18_SHOPIFY_IN_CONTEXT_AGENTIC_SENSOR.md"
status: Active
archetype: TASK_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - task
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tasks/TASK_2026_11_18_SHOPIFY_IN_CONTEXT_AGENTIC_SENSOR.md"
> purpose: "Canonical PSOD Delegation Contract: Shopify In-Context Agentic Review Sensor & FastMCP Dispatch Loop (DEC-147)"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 PSOD DELEGATION CONTRACT: Shopify In-Context Agentic Review Sensor & FastMCP Loop (DEC-147)

### 1. Problem & Context (P):
- **User Intent**: The merchant / client (e.g. Andrii Nikolaiev & partner for NOKU Store) needs the ability to review their Shopify store in real-time, click any visual element or section directly on the storefront, write comments or change requests, and have those tickets routed **directly to the AI developer agent (Antigravity / Denchik / Gerych)** via FastMCP without losing feedback across Telegram chats or messy screenshots.
- **Architectural Solution**:
  1. **Shopify Storefront Sensor (Ring 3)**: A lightweight, seek-safe Liquid snippet `snippets/dnk-in-context-sensor.liquid` and script `assets/dnk-sensor.js` that activates only in `design_mode` or `preview_theme_id`.
  2. **In-Context Inspection**: Hover detects Shopify sections (`data-section-id`, `id="shopify-section-*"`) and blocks (`data-block-id`), displaying a breadcrumb tag. Click opens an in-context review card.
  3. **Direct Agent Channel via FastMCP (Ring 4)**: The sensor dispatches to the FastAPI REST API (`/api/v1/cockpit/{deal_id}/tickets`), which persists into SQLite WAL and emits events to the Agent Action Bus.
  4. **FastMCP Tools**: Exposed in `core/kernel_mcp.py` and `core/kernel_tools.py`:
     - `get_client_tickets(deal_id, status)`: Fetches incoming feedback directly into agent context.
     - `resolve_client_ticket(deal_id, ticket_id, resolution_note, status)`: Marks tickets resolved with commit details.
     - `get_cockpit_status(deal_id)`: Fetches overall deal roadmap and quota state.

### 2. Permitted Files Whitelist (Target Whitelist):
- `services/dnk_shopify/DNK_Sovereign_Apex/snippets/dnk-in-context-sensor.liquid`
- `services/dnk_shopify/DNK_Sovereign_Apex/assets/dnk-sensor.js`
- `core/client_cockpit/engine.py`
- `apps/api/routers/client_cockpit_router.py`
- `core/kernel_mcp.py`
- `core/kernel_tools.py`
- `tests/core/test_client_cockpit_actions.py`
- `docs/projects/dnk_ecom/shopify_sensor/README.md`
- `docs/architecture/DECISION_REGISTRY_ADHD.md`

> ⚠️ ANY WRITE OUTSIDE THIS WHITELIST IS STRICTLY FORBIDDEN.

### 2.1. Negative Scope & Anti-Scope:
- Strictly NO modifications to production storefront checkout or payment pipelines.
- Strictly NO external third-party dependencies (Alpine, React, jQuery) in `dnk-sensor.js`.
- Strictly NO writes outside the permitted files whitelist.
- Strictly NO exposure of sensor overlay to regular shoppers outside design or preview mode.

### 3. Substrate & Rules (S):
- Senior Dev Solution Ladder (DEC-057): Pure DOM APIs and stdlib first. Zero heavy external JS dependencies in `dnk-sensor.js`.
- Security Guard: The review overlay must only be visible to authenticated merchants or staging viewers (`request.design_mode or content_for_header contains 'preview_theme_id'`), never regular shoppers.
- Resilient Offline Fallback: If network connection to the local agent/API drops, store tickets in `localStorage` queue.
- Scope Guard: Automatic triage of tickets into `question`, `in_scope_revision`, or `out_of_scope_upsell`.

### 4. Deterministic Verification Oracle (O):
Execute:
```bash
uv run pytest tests/core/test_client_cockpit_actions.py -v
```
> 🚨 EXIT CODE MUST BE `0`. ALL TESTS MUST PASS.

### 5. Deliverable Format (D):
- Production Liquid snippet & vanilla JS sensor in `services/dnk_shopify/DNK_Sovereign_Apex/`.
- FastMCP tool registration in `core/kernel_mcp.py` and `core/kernel_tools.py`.
- REST API router endpoints in `apps/api/routers/client_cockpit_router.py`.
- 100% green test suite verifying ticket lifecycle (`init -> submit -> list -> resolve`).
