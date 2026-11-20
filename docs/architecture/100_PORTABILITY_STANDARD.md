---
title: "Стандарт 100% Портативності DNK OS (100% Portability Standard)"
description: "Comprehensive Specification of the 100% Portability Standard for DNK OS."
mrh_id: "docs/architecture/100_PORTABILITY_STANDARD.md"
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
> mrh_id: "docs/architecture/100_PORTABILITY_STANDARD.md"
> purpose: "Comprehensive Specification of the 100% Portability Standard for DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🌐 Стандарт 100% Портативності DNK OS (100% Portability Standard)

> **Золоте правило:**  
> «На Mac — спільні ресурси (Zero-Duplicate), у репозиторії — чисті маніфести, на сервері — автономне саморозгортання».

---

## 🏛️ 1. Три Стовпи Стандарту

### Стовп 1: Mac Zero-Duplicate (Спільний Runtime)
- **Проблема:** Кожен новий агент чи склонований сервіс завантажує власні гігабайти `node_modules` та віртуальних оточень Python, швидко забиваючи SSD.
- **Рішення:**
  - `pnpm` з єдиним сховищем контенту (`~/.dnk_runtime/pnpm_virtual_store` / `~/.pnpm-store`).
  - `uv` з використанням Apple Silicon APFS Copy-on-Write (CoW).
  - Спільне runtime оточення в `~/.dnk_runtime`.
  - Заборона жорстких дублікатів залежностей.

### Стовп 2: Чисті Маніфести у Репозиторії (Zero Absolute Paths)
- **Проблема:** Абсолютні шляхи виду `/Users/<username>/...` у конфігах чи скриптах ламають виконання на будь-якому іншому комп'ютері чи в контейнері.
- **Рішення:**
  - Тільки відносні шляхи (`./`, `../`) або динамічне визначення через `Path(__file__).resolve().parent`.
  - Відсутність вендорських прив'язок у `pyproject.toml` та `package.json`.
  - Автоматичний передекспортний аудит скриптом `verify_portability.sh`.

### Стовп 3: Автономне Саморозгортання на Сервері (One-Click Autonomous Deploy)
- **Проблема:** Розгортання на Linux VPS часто падає через конфлікти UID/GID (501 на Mac проти 1000 на Linux), відсутність зовнішніх утиліт ОС (`ripgrep`, `git`, `curl`), або блокування SQLite при паралельному доступі.
- **Рішення:**
  - Багатоетапний `Dockerfile` з користувачем `UID 1000 (dnk)` та встановленими утилітами.
  - `compose.yaml` з ротацією логів (50MB, max 3 файли) та ізольованими томами `./data` і `./logs`.
  - `bootstrap.sh` із самодіагностикою, налаштуванням прав та автоматичним запуском.
  - Обов'язковий режим `PRAGMA journal_mode=WAL;` для всіх SQLite баз даних.

---

## 🛠️ 2. Інструменти Перевірки

- `dnk-os verify`: Перевіряє відсутність абсолютних шляхів, канонічні директорії та стан спільних ресурсів.
- `dnk-os status`: Виводить ADHD 1-екранну панель стану системи.
- `dnk-build <app_id>`: Збирає автономний переносний архів без локального сміття.
