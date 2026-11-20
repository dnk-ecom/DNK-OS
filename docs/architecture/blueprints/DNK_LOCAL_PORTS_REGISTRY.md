---
title: "DNK Local Ports Registry (SSOT)"
description: "Canonical Single Source of Truth (SSOT) Port Allocation Registry for DNK OS, Core Hub, and Vibe Prototypes."
mrh_id: "docs/architecture/blueprints/DNK_LOCAL_PORTS_REGISTRY.md"
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
> mrh_id: "docs/architecture/blueprints/DNK_LOCAL_PORTS_REGISTRY.md"
> purpose: "Canonical Single Source of Truth (SSOT) Port Allocation Registry for DNK OS, Core Hub, and Vibe Prototypes."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌐 DNK Local Ports Registry (SSOT)

Реєстр фіксованих мережевих портів (Port Allocation Registry) для запобігання колізіям між сервісами DNK OS, головним хабом та прототипами у `../DNK_Vibe/`.

## 📌 Золоте правило розподілу портів (Port Isolation Invariant)
1. **Жоден сервіс не повинен використовувати плаваючий дефолтний порт** без директиви `strictPort: true` або явного прапорця `-p <port>`.
2. Кожен додаток має свій виділений порт. При старті заборонено перехоплювати чужий порт чи перескакувати на суміжний.
3. Якщо порт зайнятий, сервер повинен зупинятися з явною помилкою (`strictPort: true`), а не підміняти інший сервіс.

---

## 🗺️ Таблиця виділених портів

| Порт | Додаток / Сервіс | Каталог | Команда запуску | Призначення |
| :--- | :--- | :--- | :--- | :--- |
| **3000** | **DNK Hub Web** | `apps/web` | `pnpm dev` | Головний вебінтерфейс DNK OS Hub |
| **8000** | **DNK Core API** | `apps/api` | `uv run uvicorn main:app --port 8000` | Центральний FastAPI бекенд |
| **3001** | **DNK Media Studio** | `apps/canvas` | `pnpm dev` | Медіа-полотно та нодова студія |
| **3005** | **DNK Video Engine** | `services/dnk_media` | `python3 -m services.dnk_media.server` | Процесинг та експорт MP4/Remotion |
| **5173** | **thoughtdag** | `../DNK_Vibe/thoughtdag` | `pnpm dev` (Vite, port 5173 strict) | DAG мислення та візуальні графи агентів |
| **5174** | **card-news-studio** | `../DNK_Vibe/card-news-studio` | `pnpm dev` (Next.js, port 5174) | Генератор новинних карток |
| **5175** | **nlp-trainer** | `../DNK_Vibe/nlp-trainer` | `pnpm dev` | Тренування та розмітка NLP |
| **5176** | **pmx-canvas** | `../DNK_Vibe/pmx-canvas` | `pnpm dev` | Експериментальне полотно PMX |
| **5177** | **tributary** | `../DNK_Vibe/tributary` | `pnpm dev` | Потоковий процесинг та конвеєри |
| **5180** | **DNK VibeCut** | `../DNK_Vibe/vibecut` | `pnpm dev` (Vite 5180 + Electron) | **Студія запису та відеоредактор VibeCut** |
| **5181** | **agentic-video-editor** | `../DNK_Vibe/agentic-video-editor` | `pnpm dev` | Агентне відеоредагування |
| **5182** | **creator-os-starter** | `../DNK_Vibe/creator-os-starter` | `pnpm dev` | Creator OS прототип |
| **5185** | **roast-room** | `../DNK_Vibe/roast-room` | `pnpm dev` | Рада директорів та бізнес-аудит |
| **5186** | **seos-assistant** | `../DNK_Vibe/seos-assistant` | `pnpm dev` | SEO аналітика та асистент |
| **5188** | **scriptwriter** | `../DNK_Vibe/scriptwriter` | `pnpm dev` | Сценарна студія |
| **5190** | **zclip** | `../DNK_Vibe/zclip` | `pnpm dev` (Next.js, port 5190) | Нарізка та аналіз кліпів |

---

## 🛠️ Перевірка зайнятості портів
Швидка перевірка зайнятих портів перед запуском:
```bash
lsof -i :5180
# або
lsof -iTCP -sTCP:LISTEN -n -P | grep -E "3000|8000|5173|5174|5180|5190"
```
