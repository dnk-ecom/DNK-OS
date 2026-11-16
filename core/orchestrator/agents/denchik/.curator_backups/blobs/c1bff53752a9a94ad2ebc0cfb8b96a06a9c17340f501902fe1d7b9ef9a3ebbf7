---
title: "Synthesis Matrix Template"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/obsidian-vault-hygiene/templates/synthesis_matrix_template.md"
> purpose: "Document: Synthesis Matrix Template"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/note-taking/obsidian-vault-hygiene/templates/synthesis_matrix_template.md"
# purpose: "Canonical Callout-First Decision & Synthesis Matrix template for Obsidian notes and ADRs."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-07"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

## ⚖️ Матриця синтезу: Що залишаємо → Що додаємо → Що відкидаємо

> [!check] **1. Що залишаємо (Базовий перевірений фундамент)**
> - **[Ключовий принцип/компонент]**: Чітке обґрунтування, чому це залишається (наприклад, автономія домену, Pydantic SSOT, Zero-Bloat Core).
> - **[Файлова структура/контракти]**: Перелік стабільних артефактів, які не потребують змін.

> [!tip] **2. Що додаємо (Нові архітектурні можливості / Платформна інженерія)**
> - **[Новий стандарт/маніфест]**: Що саме інтегрується (наприклад, Service Card, Contract Gates, SRE-ендпоінти).
> - **[Автоматизація/шаблонізація]**: Які інструменти чи генератори створюються для прискорення розробки.

> [!danger] **3. Що відкидаємо (Overengineering / Непотрібна складність)**
> - **[Зайва залежність / складний патерн]**: Чому це відхилено на даному етапі (наприклад, важкі сервіс-меші, розподілений консенсус).
> - **[Анахронізми]**: Ручна синхронізація, захардкоджені конфігурації чи застарілі формати.

---

### 📊 Альтернативне представлення: Компактна порівняльна таблиця

| Напрямок | Компонент / Рішення | Статус | Обґрунтування / Rationale |
| :--- | :--- | :---: | :--- |
| **Фундамент** | Domain Autonomy | 🟢 Залишаємо | Гарантує Zero-Bloat Core та незалежність доменів |
| **Еволюція** | DNK Service Card | 🚀 Додаємо | Єдиний паспорт сервісу з валідацією контрактів |
| **Спрощення** | Heavy Service Meshes | 🔴 Відкидаємо | Overengineering: достатньо HTTP/in-process роутингу |
