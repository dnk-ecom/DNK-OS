---
title: "Known Gaps & Capability Map Open Design"
description: "Невідповідності поточного стану Open Design та карта перенесення можливостей."
mrh_id: "docs/architecture/research/stitch-shell/known-gaps.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/research/stitch-shell/known-gaps.md"
> purpose: "Невідповідності поточного стану Open Design та карта перенесення можливостей."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# Known Gaps & Capability Map Open Design

Цей документ фіксує технологічні та функціональні розбіжності між демонстраційним Stitch Shell та повноцінним Canvas Engine, а також містить карту інтеграції можливостей Open Design в архітектуру DNK OS.

---

## 1. Виявлені технологічні гепи (Known Gaps)

1. **Відсутність живого State Sync (SSE)**: Панель логів використовує локальний статичний масив; відсутнє підключення до `EventSource` для прийому живих стрімів від Docker-контейнерів.
2. **Відсутність збереження (Persistence)**: Локальні зміни масштабу, інструментів та промптів зникають після оновлення сторінки. Немає зв'язку з SQLite БД.
3. **Мок-експорт**: Кнопка "Export Code" повертає статус `queued` локально, оскільки backend сервіс компілятора Liquid ще не інтегрований.
4. **Drawing Engine**: Зараз використовується простий CSS-transform зсуву замість повноцінного ReactFlow / Excalidraw рішення.

---

## 2. Capability Map Open Design ➔ DNK OS

| Open Design capability | source module/file | business purpose | DNK equivalent | decision: reuse/reimplement/reference/reject | priority | risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SSE Event Stream** | `packages/contracts/src/sse` | Реальний стрім логів і прогресу запуску агентів | `dnk_sse_service` | **Reimplement** (використовуючи FastAPI SSE) | High | Low |
| **Theme Generator** | `apps/web/src/utils/theme` | Генерація бренд-тем на основі промпту | `dnk_theme_manager` | **Reuse** (з адаптацією під MRH заголовки) | Medium | Med |
| **Liquid Builder** | `apps/daemon/src/runtimes/` | Компільований рендеринг Liquid секцій Shopify | `dnk_shopify_builder`| **Reimplement** (чистий Python/Liquid сервіс) | High | High |
| **Desktop Electron Shell**| `apps/desktop/` | Нативний запуск десктопного додатку з IPC | `dnk_desktop_shell` | **Reference** (вивчити та спростити до TMA/TUI) | Low | Low |
| **Excalidraw Engine** | `apps/web/package.json` | Малювання схем і діаграм на полотні | `dnk_canvas_reactflow` | **Reuse** (ReactFlow / Excalidraw інтеграція) | High | Med |
