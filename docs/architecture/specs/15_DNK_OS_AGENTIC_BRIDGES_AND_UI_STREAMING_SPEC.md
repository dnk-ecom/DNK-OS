---
title: "DNK OS Agentic Bridges & UI Streaming Specification"
description: "Technical Specification for HermesUIBridge, TaskboardCanvasBridge, and Real-Time Event Bus."
mrh_id: "docs/architecture/specs/15_DNK_OS_AGENTIC_BRIDGES_AND_UI_STREAMING_SPEC.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/15_DNK_OS_AGENTIC_BRIDGES_AND_UI_STREAMING_SPEC.md"
> purpose: "Technical Specification for HermesUIBridge, TaskboardCanvasBridge, and Real-Time Event Bus."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌉 DNK OS Agentic Bridges & UI Streaming Specification

---

## 📌 1. Scope & Purpose

Ця специфікація визначає технічні контракти, схеми даних та протоколи взаємодії між автономним агентним ядром DNK OS, базою даних задач `tasks.sqlite` та фронтенд-кокпітом Meta Astryx Generative UI.

---

## 📡 2. HermesUIBridge Protocol (`core/adapters/hermes_ui_bridge.py`)

### 2.1. 100-Event Ring Buffer & ActionBus
- **Ємність буфера**: Останні 100 подій (`deque(maxlen=100)`).
- **Призначення**: Забезпечує миттєве відновлення контексту для браузерних клієнтів при перезавантаженні сторінки або тимчасовому розриві WebSocket-з'єднання.
- **Подієва модель (`HermesEvent`)**:
  ```python
  class HermesEvent(BaseModel):
      event_id: str
      event_type: str  # 'thought' | 'tool_start' | 'tool_complete' | 'plan_update' | 'hitl_request' | 'hitl_response' | 'error'
      agent_role: str  # 'antigravity' | 'denchik' | 'gerych_prime' | 'goldfish'
      timestamp: float
      payload: Dict[str, Any]
  ```

### 2.2. Streaming Endpoints
- **WebSocket Gateway**: `/api/v1/swarm/live/ws`
  - Двосторонній потік: broadcast подій ядра у браузер + прийом HITL-рішень клієнта.
- **Server-Sent Events (SSE)**: `/api/v1/swarm/live/stream`
  - Односторонній стрімінг для легковажних віджетів та фонового моніторингу.

### 2.3. Non-Blocking HITL Approval Gateway
- **Метод**: `HermesUIBridge.request_hitl_approval_async(ticket_id, prompt, timeout_seconds=300)`
- **Поведінка**: Асинхронний `asyncio.Future`. Не блокує подієвий цикл сервера; у разі таймауту повертає детермінований відкат `timeout_auto_reject`.
- **Резолюція**: Ендпоінт `POST /api/v1/swarm/live/hitl/resolve` із корисним навантаженням `{ ticket_id, decision: 'approved' | 'rejected', params_override }`.

---

## 🗺️ 3. TaskboardCanvasBridge (`core/adapters/taskboard_canvas_bridge.py`)

### 3.1. SQLite to XYFlow v12 Mapping
- **Джерело даних**: `.agents/taskboard/tasks.sqlite` (таблиці `agent_tasks`, `task_subtasks`, `task_comments`).
- **Схема ноди (`CanvasNode`)**:
  - `id`: `task.id` (наприклад, `task-mwjumozp-7g3q`).
  - `type`: `agentTask`.
  - `position`: Координати колонки (Lane) за статусом та порядковим індексом:
    - `todo`: $X = 50.0$
    - `planned`: $X = 380.0$
    - `in_progress`: $X = 710.0$
    - `verification`: $X = 1040.0$
    - `done`: $X = 1370.0$
    - `failed`: $X = 1700.0$
    - $Y = 80.0 + \text{order\_index} \times 220.0$
  - `data`: Об'єкт `CanvasTaskNodeData` (назва, опис, статус, пріоритет, призначений агент, прогрес у %, лічильники підзадач та коментарів).

### 3.2. Typed Wires & Topological Edges
- **Послідовні ребра (`CanvasEdge`)**:
  - З'єднують попередню задачу з наступною в межах послідовності (`source: task_A`, `target: task_B`).
  - **Тип дроту**:
    - `CONTEXT` (Cyan `#06b6d4`): Зв'язок передачі технічного контексту та вимог.
    - `DIFF` (Emerald `#10b981`): Потік згенерованих файлів та валідованих патчів.

### 3.3. REST API Contracts
- `GET /api/v1/taskboard/canvas`: Повертає повний граф `{ nodes: [...], edges: [...], total_tasks: N, active_tasks: M }`.
- `POST /api/v1/taskboard/node/status`: Оновлює статус та логи задачі з клієнтського канвасу із записом у SQLite.
