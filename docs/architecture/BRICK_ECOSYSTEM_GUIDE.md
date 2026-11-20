---
title: "Керівництво по Екосистемі Цеглин DNK OS (Composable Bricks Guide)"
description: "Architecture Guide for Composable LEGO Bricks in DNK OS (DEC-072, DEC-073)."
mrh_id: "docs/architecture/BRICK_ECOSYSTEM_GUIDE.md"
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
> mrh_id: "docs/architecture/BRICK_ECOSYSTEM_GUIDE.md"
> purpose: "Architecture Guide for Composable LEGO Bricks in DNK OS (DEC-072, DEC-073)."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧱 Керівництво по Екосистемі Цеглин DNK OS (Composable Bricks Guide)

> **Концепція:**  
> «Система як плагін» (System-as-a-Plugin, натхненна DeepSeek Harness).  
> Кожен сервіс або підсистема — це незалежна, вимірювана Цеглина (`core/bricks/`), що найкраще у світі виконує свою конкретну задачу.

---

## 🏛️ 1. Анатомія Цеглини

Кожна цеглина розташована у папці `core/bricks/<brick_id>/` і складається з трьох обов'язкових елементів:

1. **`brick.manifest.yaml`**: Маніфест цеглини з описом, категорією, списком шляхів, внутрішніми залежностями (`dependencies.internal`) та зовнішніми пакетами (`external_python`, `external_npm`).
2. **`contracts/`**: Pydantic моделі та схеми типізації для строгої валідації вхідних та вихідних даних.
3. **`mcp_server.py`**: FastMCP сервер, що експортує інструменти (`@mcp.tool()`) у протокол MCP для взаємодії з агентами та іншими сервісами.

---

## 📦 2. Каталог Базових Цеглин DNK OS

| ID | Назва | Категорія | Опис |
| :--- | :--- | :--- | :--- |
| `brick_01_agentic_brain` | Agentic Brain & Swarm Core | `agentic_core` | Оркестратор Hermes, TaskDNA декомпозиція задач, circuit breakers, моделі. |
| `brick_02_scones_memory` | SCONES Memory & Knowledge Hub | `knowledge_memory` | Багаторівнева векторна пам'ять, дистиляція помилок, SQLite WAL. |
| `brick_03_spatial_canvas` | Spatial Canvas V3 Engine | `spatial_ui` | Безкінечний просторовий граф, трансляція ThoughtDAG, проекція агентів. |
| `brick_04_shopify_engine` | Shopify 3.0 Engine & Liquid AST | `ecommerce_engine` | Liquid AST парсер, генератор Theme Blocks 2.0, CRO аудит. |
| `brick_05_video_ai` | Video AI UGC Pipeline | `video_generation` | Remotion таймлайн синтез, покадрова анімація, генерація вірусних відео. |
| `brick_06_web_api_shell` | Command Center Web UI & Gateway Shell | `gateway_shell` | Next.js 14 кабінет, FastAPI динамічний роутер, вебсокети, сесії. |

---

## 🚀 3. Керування Цеглинами через CLI

- Перегляд каталогу:
  ```bash
  dnk-os brick list
  ```
- Обчислення DAG залежностей та генерація lean-маніфесту:
  ```bash
  dnk-os brick resolve brick_01_agentic_brain brick_04_shopify_engine
  ```
