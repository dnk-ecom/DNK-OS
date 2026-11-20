---
title: "DNK OS — Єдине Суверенне Ядро та Кабінет Розробки"
description: "Unified Sovereign Cockpit & Microkernel Documentation for DNK OS."
mrh_id: "README.md"
status: Active
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
  - cockpit
  - microkernel
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "README.md"
> purpose: "Unified Sovereign Cockpit & Microkernel Documentation for DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 DNK OS — Єдине Суверенне Ядро та Кабінет Розробки

> **Суверенне Ядро (Kernel) та Робочий Кабінет Вайбкодера (Максима) і Команди Агентів**  
> Побудовано за **Стандартом 100% Портативності** (DEC-070, DEC-071) та архітектурою **Система як плагін** (DEC-072, DEC-073).

---

## 🏛️ Архітектурна Модель

```
┌────────────────────────────────────────────────────────┐
│               DNK_OS (Sovereign Core & Cockpit)        │
│                                                        │
│  🧠 Microkernel Host:   FastMCP Gateway (Порт :8080)   │
│  🧱 Composable Bricks:  6 базових LEGO-цеглин          │
│  🌐 Port Governance:    Реєстр 32 портів (54100-54999) │
│  🛡️ Process Sentinel:   PID Watchdog & Zombie Reaper   │
│  📋 Agent Bus:          SQLite WAL TaskDNA Dispatcher  │
└──────────────────────────┬─────────────────────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
[DNK_GitHub_Vibe]  [DNK_Vibe_Coding]        [DNKEcom]
(R&D Лабораторія)   (Бізнес-сервіси)    (Shopify Імперія)
```

---

## 🚀 Швидкий Старт та Команди Кабінету (`dnk-os`)

Команда `dnk-os` доступна глобально в терміналі на вашому Mac:

```bash
# 1. Вивести 1-екранну панель стану системи (ADHD Card)
dnk-os status

# 2. Керування LEGO-цеглинами
dnk-os brick list
dnk-os brick resolve brick_01_agentic_brain brick_04_shopify_engine

# 3. Моніторинг та звільнення портів
dnk-os port list
dnk-os port free 8000

# 4. Очищення зомбі-процесів та тимчасового сміття
dnk-os clean

# 5. Перевірка Шлюзу 100% Портативності
dnk-os verify
```

---

## 🌐 100% Портативність та Розгортання

- **Локальний запуск на Mac**:
  ```bash
  ./bootstrap.sh --local
  ```
- **Автономний запуск у Docker (Linux VPS або Mac)**:
  ```bash
  ./bootstrap.sh
  ```
  Контейнер автоматично враховує Linux UID 1000, монтує ізольовані томи `./data` і `./logs`, та ротує логи (максимум 50MB на файл).
