---
title: "Канонічний регламент міграції та авто-гідратації карантинних сервісів (GPL/AGPL Portability Standard)"
description: "Standard Operating Procedure & 1-Click Portability Protocol for Quarantined GPL/External Services (DEC-048, DEC-070)"
mrh_id: "docs/architecture/QUARANTINED_SERVICES_PORTABILITY_GUIDE.md"
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
> mrh_id: "docs/architecture/QUARANTINED_SERVICES_PORTABILITY_GUIDE.md"
> purpose: "Standard Operating Procedure & 1-Click Portability Protocol for Quarantined GPL/External Services (DEC-048, DEC-070)"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/architecture/QUARANTINED_SERVICES_PORTABILITY_GUIDE.md"
purpose: "Standard Operating Procedure & 1-Click Portability Protocol for Quarantined GPL/External Services (DEC-048, DEC-070)"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-11-17"
author: "DNK-e.com Maksym & Antigravity"
--- END DNK-MRH-HEADER --- -->

# 📦 Канонічний регламент міграції та авто-гідратації карантинних сервісів (GPL/AGPL Portability Standard)

> **Золоте правило портативності DNK OS (DEC-070, DEC-071):**  
> *«На Mac — спільні ресурси (Zero-Duplicate), у репозиторії — чисті маніфести, на новому сервері — 1-клік автономне саморозгортання».*

---

## ⚖️ 1. Правова та архітектурна основа: Чому Карантин?

У DNK OS сторонні інструменти з вірусними ліцензіями (**GPL-3.0**, **AGPL-3.0**) суворо заборонено імпортувати всередину кодової бази (`DNK_OS`).

1. **Захист комерційної таємниці:** Прямий імпорт GPL-коду зобов'язує відкрити 100% вихідного коду всіх суміжних систем і комерційних Shopify-тем.
2. **Принцип «дистанції витягнутої руки» (Arm's Length):** GPL-інструменти (такі як **AperiSolve**) розміщуються виключно в ізольованому зовнішньому каталозі `../DNK_Vibe/<Service>/`.
3. **IPC / FastMCP міст:** Ядро DNK OS спілкується з карантинним процесом виключно через стандартизовані потоки введення-виведення (`stdio`) або HTTP-запити. Жоден біт ліцензійного зараження не проникає в наш комерційний контур.

---

## 🚀 2. Швидке відновлення в 1 клік (При переїзді на новий Mac / VPS / CI)

Якщо ви перенесли репозиторій `DNK_OS` на нову машину, де папка `../DNK_Vibe/` ще порожня:

### Команда авто-гідратації:
```bash
just hydrate-vibe
```
*(Або напряму через Python, якщо `just` ще не встановлено):*
```bash
uv run python3 scripts/system/hydrate_quarantined_services.py
```

### Що автоматично робить скрипт:
1. Сканує всі маніфести плагінів `packages/plugins/*/service_manifest.yaml` на наявність блоку `spec.quarantine`.
2. Автоматично робить shallow clone (`git clone --depth 1`) відсутніх репозиторіїв у `../DNK_Vibe/`.
3. Створює локальне віртуальне середовище за допомогою `uv` і встановлює всі необхідні залежності (`uv sync --extra mcp`).
4. Запускає детерміновану діагностику (`verify_command`, exit code 0).
5. Видає звіт готовності: `🟢 STATUS: <Service> is HYDRATED & OPERATIONAL`.

### Перевірка статусу без завантаження (Check-only):
```bash
just check-vibe
```

---

## 🛠️ 3. Покроковий ручний протокол для AperiSolve (Якщо потрібен оффлайн/Docker)

Якщо на машині немає прямого доступу до GitHub або потрібне повністю локальне середовище:

### Крок 1: Ручне клонування в правильну карантинну папку
```bash
# Папка повинна знаходитися на одному рівні з DNK_OS:
mkdir -p ../DNK_Vibe
cd ../DNK_Vibe
git clone --depth 1 https://github.com/Zeecka/AperiSolve.git
cd AperiSolve
```

### Крок 2: Ініціалізація залежностей FastMCP
```bash
# Встановлення потрібних пакетів через uv (включно з mcp-екстрою):
uv sync --extra mcp
```

### Крок 3: Перевірка працездатності сервера
```bash
uv run --extra mcp python -m aperisolve_mcp --help
# Має повернути опис прапорців (--stdio, --host, --port)
```

---

## 📝 4. Регламент додавання НОВИХ сервісів з вірусними ліцензіями (SOP)

Коли в проект додається новий сторонній інструмент (GPL, AGPL, CPAL):

1. **Створення плагіна-адаптера:**
   * Створити теку: `packages/plugins/dnk_<service_name>/`.
   * Написати `adapter.py` — клас-клієнт, який **НЕ імпортує чужу бібліотеку**, а запускає її через `subprocess` або FastMCP Client.

2. **Декларація карантину в `service_manifest.yaml`:**
   Кожен такий плагін зобов'язаний мати блок `quarantine`:
   ```yaml
   spec:
     lifecycle: Active
     domain: security-forensics
     entrypoint: packages.plugins.dnk_new_service.adapter:NewServiceAdapter
     quarantine:
       service_name: "NewService"
       license: "GPL-3.0"
       repo_url: "https://github.com/Vendor/NewService.git"
       target_dir: "../DNK_Vibe/NewService"
       bootstrap_command: "uv sync"
       verify_command: "uv run python -m new_service_cli --version"
       documentation_url: "https://docs.vendor.com"
     transport:
       protocol: fastmcp
       mode: stdio
       command: uv
       args:
         - run
         - --directory
         - ../DNK_Vibe/NewService
         - python
         - -m
         - new_service_mcp
         - --stdio
   ```

3. **Самозахист (Graceful Degradation Invariant):**
   * У класі `adapter.py` метод `is_available()` обов'язково перевіряє фізичну наявність каталогу `../DNK_Vibe/<Service>`.
   * Якщо сервіс не гідратований, адаптер **не викидає критичний Fatal Crash**, а логує зрозумілу інструкцію:
     ```python
     if not self.is_available():
         logger.warning("Service X is not hydrated. Run 'just hydrate-vibe' to provision.")
     ```

---

## 📋 5. Реєстр активних карантинних сервісів

| Сервіс | Репозиторій | Ліцензія | Локація | Протокол зв'язку |
| :--- | :--- | :--- | :--- | :--- |
| **AperiSolve** | `Zeecka/AperiSolve` | GPL-3.0 | `../DNK_Vibe/AperiSolve/` | FastMCP Stdio (`aperisolve_mcp`) |

---

*Цей документ є офіційним обов'язковим стандартом DNK OS для будь-яких зовнішніх розгортань, міграцій на новий Mac або релізів автономних білдів.*
