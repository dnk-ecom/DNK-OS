---
title: "State Inventory: Quality States Matrix"
description: "Реєстр якісних станів інтерфейсу (Quality States) та матриця їх реалізації."
mrh_id: "docs/architecture/research/stitch-shell/state-inventory.md"
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
> mrh_id: "docs/architecture/research/stitch-shell/state-inventory.md"
> purpose: "Реєстр якісних станів інтерфейсу (Quality States) та матриця їх реалізації."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# State Inventory: Quality States Matrix

Кожен ключовий молекулярний компонент інтерфейсу Canvas повинен підтримувати 7 базових якісних станів відповідно до специфікації надійності DNK.

| UI Component | Idle | Loading | Success | Empty | Error | Disabled | Offline |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent Panel** | `[x]` | `[x]` | `[x]` | `[x]` | `[x]` | `[x]` | `[x]` |
| **Prompt Dock** | `[x]` | `[x]` | `[x]` | `[-]` | `[x]` | `[x]` | `[-]` |
| **Export Action** | `[x]` | `[x]` | `[x]` | `[-]` | `[x]` | `[-]` | `[-]` |
| **Canvas** | `[x]` | `[-]` | `[x]` | `[-]` | `[-]` | `[-]` | `[-]` |
| **Artifact Preview**| `[-]` | `[x]` | `[x]` | `[x]` | `[-]` | `[-]` | `[-]` |

---

## Детальний опис станів для молекул Canvas

### 1. Agent Panel
- **Idle**: Стендбай стан, готовий до отримання AST-контексту.
- **Loading**: Спінер, відображає процес з'єднання чи завантаження журналів.
- **Success**: Рендеринг списку журналів логів.
- **Empty**: Відображається плашка "Логи відсутні" при новій чистій сесії.
- **Error**: Плашка помилки з червоною рамкою "Failed to parse AST stream".
- **Disabled**: Напівпрозорий заблокований екран "Access Blocked".
- **Offline**: Візуальний індикатор "Standalone Mode" без підключення до Docker-демона.

### 2. Prompt Dock
- **Idle**: Поле введення готове до прийому тексту.
- **Loading**: Стан "Running...", кнопка Run неактивна, щоб запобігти подвійним запитам.
- **Success**: Короткочасна успішна підсвітка рамки вводу чи очищення.
- **Error**: Показ попередження під інпутом (наприклад, червона панель "Not implemented").
- **Disabled**: Поле введення заблоковано `disabled={true}`.

### 3. Artifact Preview
- **Empty**: "No artifacts generated yet". Заохочує відправити промпт.
- **Loading**: "Gerych is compiling artifact..." з анімованим круговим спінером.
- **Success**: Відображення згенерованого Liquid файлу з кодом та мета-даними.
