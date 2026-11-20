---
title: "Паспорт Асиміляції Сигналу (SVAE): The Home Repo Pattern"
description: "Sovereign Knowledge Assimilation Passport: The Home Repo Pattern (Matt Pocock / YouTube hWe-j78vNpc)."
mrh_id: "docs/architecture/reports/video_assimilations/ASSIMILATION_2026_11_17_HOME_REPO_PATTERN.md"
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
> mrh_id: "docs/architecture/reports/video_assimilations/ASSIMILATION_2026_11_17_HOME_REPO_PATTERN.md"
> purpose: "Sovereign Knowledge Assimilation Passport: The Home Repo Pattern (Matt Pocock / YouTube hWe-j78vNpc)."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# ⚡ Паспорт Асиміляції Сигналу (SVAE): The Home Repo Pattern

- **Джерело**: [YouTube: hWe-j78vNpc](https://youtu.be/hWe-j78vNpc)
- **Автор**: Matt Pocock (ex-Vercel TurboRepo, AI Engineering Educator)
- **Тривалість / Сегменти**: ~9 хв / 248 сегментів
- **Фільтр шуму (Fluff-Stripping)**: **78% відсіяно** (преамбули про Twitter-хайп, розповіді про консультації, анонси майбутніх відео, самопіар платного курсу з AI-програмування).
- **Чистий сигнал**: **22% технічного екстракту**, з яких **1% — критичний архітектурний інсайт** для multi-repo агентивної взаємодії.

---

## 🎯 1. Цільова Інженерна Проблема (Problem Statement)
**«Як організувати роботу AI-агентів, якщо в бізнесі є 20–40 окремих репозиторіїв (вітрина магазину, API платежів, адмінка, мікросервіси, бази знань), щоб не дублювати скіли, правила `AGENTS.md` та інструменти в кожному з них?»**

### Помилкові / Тупикові Рішення (зафіксовані у відео):
1. *Дублювання скілів і `AGENTS.md` у 30 репозиторіях*: Синхронізаційне пекло; зміни в одному правилі вимагають 30 PR-ів.
2. *Зберігання скілів у домашній директорії користувача (`~/.config` / `~/.gemini`)*: Не відстежується в git; командні правила не оновлюються; розробники розходяться в налаштуваннях; амнезія команди.

---

## 💎 2. 1% Чистого Сигналу (Архітектурні Знахідки)

### Знахідка A: «Home Repo» як єдина база операцій агента
- Агент **завжди запускається в корені Домашнього Репозиторію** (у нас це `DNK_HUB` / `DNK_OS`).
- Репозиторій містить приватні скіли (`.skills`), централізовані правила (`AGENTS.md`), локальну інструментальну вікі (Markdown Karpathy-style) та глобальні налаштування.
- Агент сприймає всі робочі проекти як підлеглі сателіти, а не як ізольовані світи.

### Знахідка B: `AGENTS.md` як Диспетчер-Гіперпосилання (Hyperlink Repo Router)
- Замість монтування важких git-submodules чи копіювання файлів, `AGENTS.md` містить **структуровані відносні шляхи до суміжних репозиторіїв**.
- **Auto-Clone on Demand**: Якщо репозиторій за вказаним шляхом відсутній на новій машині (наприклад, `SHOPIFY/DNKShopify`), агент автоматично клонує його за вказаним URL.
- **Git Worktree Isolation**: Для паралельних агентів використовується `git worktree add`, що дозволяє кільком субагентам працювати над різними фічами в межах одного репозиторію без конфліктів гілок.

### Знахідка C: Прогресивне Розкриття Репозиторіїв (Progressive Disclosure)
- При масштабуванні > 20 репозиторіїв не можна кидати всі шляхи в один промпт (Attention Rot).
- Застосовується дворівневе групування:
  - `Фронтенд-репозиторії` → посилання на файл індексу `docs/repos_frontend.md`
  - `Бекенд/API` → посилання на `docs/repos_backend.md`
  - `Інструменти/Скіли` → посилання на `docs/repos_tooling.md`
- Агент використовує файлову навігацію (`ls`, `cat`) для точкового пошуку потрібного проекту.

---

## ⚔️ 3. Мультикорпоративний Синтез (Multi-Corp Cross-Synthesis)

| Критерій | Рішення Покока (Home Repo) | Підхід Vercel / Google (Monorepo) | Підхід Shopify / Stripe (Multi-Service) | Оптимум для DNK OS |
| :--- | :--- | :--- | :--- | :--- |
| **Топологія сховища** | 1 Home Repo + loose repos через шляхи | Моноліт (TurboRepo / Piper) | Десятки незалежних репозиторіїв + CLI | **Дворівневий хаб (Two-Tier Hub, DEC-117)**: `DNK_OS` (суверенне ядро) + `DNK_HUB` (R&D) |
| **Ізоляція агентів** | Ad-hoc `git worktree` | Trunk-based, черги комітів | Docker/WASM пісочниці | **Git Worktrees + FastMCP in-RAM isolation** (DEC-120) |
| **База знань** | Markdown `wiki/` + bash-утиліти | Внутрішній корпоративний портал | Developer Docs + OpenAPI специфікації | **SCONES FTS5 SQLite WAL + Obsidian Task Forest** |
| **Слабке місце** | Ручне обслуговування шляхів | Важке індексування (IDE lag) | Високий оверхед мережевої взаємодії | Ризик засмічення неперевіреними репо (вирішено карантином `DNK_Vibe`) |

---

## 🎯 4. Тріаж та Рішення для DNK OS (Action Matrix)

### 🟢 ADOPT (Впровадити в DNK OS):
1. **Dynamic Git Worktree для рою (Swarm)**:
   - Всі паралельні агенти (`dnk_dev_fullstack`, `dnk_shopify`), коли працюють з опцією `workspace: "share"`, повинні гарантовано оперувати через `git worktree`, захищаючи робочу директорію від брудних комітів.
2. **Progressive Disclosure для зовнішніх репозиторіїв**:
   - Структурувати наш `docs/architecture/` та каталог репозиторіїв (1,663 репозиторії) через дворівневі індекси категорій (`SHOPIFY`, `MEDIA`, `AGENTS`).

### 🟡 ADAPT (Адаптувати під суверенні інваріанти):
1. **Заміна «Markdown Wiki + Bash scripts» на FastMCP**:
   - Покок використовує простий каталог `wiki/` та купу розрізнених bash-скриптів (`wiki help`).
   - *Адаптація DNK OS*: У нас це реалізовано на рівень вище — через **FastMCP Microkernel (`core/kernel.py`) та SCONES FTS5 BM25**. Агенти мають доступ до інструментів пам'яті через стандартний протокол FastMCP (без необхідності підтримувати bash-аліаси).

### 🔴 REJECT (Відхилити):
1. **Відхилити хаотичне пряме підключення зовнішніх репозиторіїв без карантину**:
   - Покок дозволяє агенту клонувати будь-що прямо поруч із домашнім репо.
   - *Причина відхилення*: Порушує **Інваріант 10 `AGENTS.md` (Foreign Repo Quarantine)**. Будь-який сторонній код повинен жити виключно в ізольованому каталозі `../DNK_Vibe/`, щоб не ламати APFS-гігієну та індексацію `DNK_OS`.

---

## 🔒 Запис до Реєстру Рішень (Decision SSOT):
Буде зафіксовано як **DEC-136: Home Repo Multi-Repo Routing & Dynamic Worktree Isolation Standard**.
