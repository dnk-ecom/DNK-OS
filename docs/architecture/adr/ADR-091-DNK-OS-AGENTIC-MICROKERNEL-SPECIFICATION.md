---
title: "ADR-091: DNK OS Agentic Microkernel Specification & Harness Blueprint"
description: "Architecture Decision Record and Formal Specification for DNK OS Agentic Microkernel."
mrh_id: "docs/architecture/adr/ADR-091-DNK-OS-AGENTIC-MICROKERNEL-SPECIFICATION.md"
status: Active
archetype: ADR
version: "2.0.0"
updated: 2026-11-18
tags:
  - adr
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/adr/ADR-091-DNK-OS-AGENTIC-MICROKERNEL-SPECIFICATION.md"
> purpose: "Architecture Decision Record and Formal Specification for DNK OS Agentic Microkernel."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ ADR-091: DNK OS Agentic Microkernel Specification & Harness Blueprint

## 1. Context & Problem Statement

У міру масштабування DNK OS (1950+ проаналізованих репозиторіїв у `catalog.db`, 195 SOTA звітів, 55 скілів та 14 swarm-агентів) виникла загроза монолітної ентропії:
1. **Неконтрольоване розростання контексту (Context Bloat)**: спроба завантажувати всі інструменти та правила в універсального агента витрачає 30–40k токенів на старті.
2. **Змішування рівнів рефлексії (System 1 vs System 2)**: використання дорогих і повільних текстових LLM (2–5 с, $0.02) для детермінованого тріажу, маршрутизації та перевірки шляхів замість суб-секундних типізованих предикатів (<50-100 мс, $0.0008).
3. **Відсутність єдиного машинного контракту ядра**: модулі взаємодіяли через ad-hoc словники без жорсткої типізації, що збільшувало ризик регресій при зміні окремих компонентів.

## 2. Decision: Agentic Microkernel Architecture

Ми фіксуємо перехід до **Agentic Microkernel Architecture** (Мікроядро агентної ОС):
Ядро DNK OS містить виключно мінімальний набір механізмів, необхідних для координації, безпеки, пам'яті та планування задач. Будь-яка бізнес-логіка виноситься у воркхорси (`services/dnk_*`) та спеціалізовані swarm-агенти.

### 2.1. Чотиришарова архітектура мікроядра

```
+-------------------------------------------------------------------------+
|                        DNK OS AGENTIC MICROKERNEL                       |
+-------------------------------------------------------------------------+
| 1. KERNEL SCHEDULER & TRIAGE (System One)                               |
|    - Complexity Metric: C = F_files + 2*D_domains + 3*S_stages         |
|    - Fast Decision Dispatch (<50ms): SOLO | SWARM_PARALLEL | SEQUENTIAL |
|    - TaskDNA Evolutionary DAG & OCC 3-Way Merge                         |
+-------------------------------------------------------------------------+
| 2. SWARM ORCHESTRATION & HARNESS (System Two)                           |
|    - Gerych Prime (Co-Architect / Swarm Manager)                        |
|    - Domain Workers: Builder, Researcher, Shopify, Fullstack, Video     |
|    - Epistemic Armor & Decision Receipts (Zero Amnesia)                 |
+-------------------------------------------------------------------------+
| 3. MEMORY & RETRIEVAL HIERARCHY (L1 - L4)                              |
|    - L1: Active Working Context (Target File Whitelist, <20k tokens)    |
|    - L2: SCONES Episodic Memory + Distiller (Error Self-Healing)        |
|    - L3: SOTA Repo Catalog (catalog.db, 1950+ curated repos)           |
|    - L4: Obsidian Knowledge Vault (MOCs, ADRs, Architectural Notes)     |
+-------------------------------------------------------------------------+
| 4. SECURITY, IPC & QUALITY GATES (Ring 0 - Ring 2)                      |
|    - Ring 0: Pre-Tool Hook (Anti-Absolute-Path, Anti-Read-Loop)         |
|    - Ring 1: Decision Receipts & Cross-Repo Synthesizer Gate            |
|    - Ring 2: Adversarial Audit (Builder vs Auditor) + verify_all.sh     |
+-------------------------------------------------------------------------+
```

## 3. Strict Machine Contracts (Pydantic SSOT)

Ядро оперує чотирма незмінними машиночитаними структурами даних:

1. **`KernelTaskRequest`**:
   - `task_id`: Унікальний UUID задачі.
   - `goal`: Текстова ціль або запит користувача.
   - `workspace_id`: Робочий простір (`ws-alpha-001`).
   - `target_files`: Білий список цільових файлів (Negative Scope захист).

2. **`KernelTriageReceipt`**:
   - `mode`: `SOLO` | `SWARM_PARALLEL` | `SWARM_SEQUENTIAL`.
   - `complexity_score`: Числове значення за формулою $C = F + 2D + 3S$.
   - `assigned_agents`: Список призначених воркерів.
   - `execution_plan`: Послідовність або паралельні батчі задач.

3. **`KernelDecisionReceipt`**:
   - `decision_id`: Хеш рішення.
   - `verdict`: `APPROVED` | `REJECTED` | `CHALLENGED`.
   - `flaws_checked`: Перевірка за правилом 3-х прихованих ризиків.
   - `evidence_hash`: Детермінований хеш артефактів/тестів.

4. **`KernelCompletionReceipt`**:
   - `task_id`: Посилання на запит.
   - `exit_code`: Код повернення виконання (0 = Green).
   - `tests_passed`: Кількість успішних тестів.
   - `clean_git`: Підтвердження чистоти робочого дерева.

## 4. Boundaries, Negative Scope & Target File Whitelist

### 4.1. Target File Whitelist (Дозволені файли ядра)
- `core/kernel/contracts.py`: Pydantic схеми контракту мікроядра.
- `core/kernel/__init__.py`: Експорт контрактів ядра.
- `tests/core/test_kernel_contract.py`: Детерміновані тести контрактів.
- `docs/architecture/adr/ADR-091-DNK-OS-AGENTIC-MICROKERNEL-SPECIFICATION.md`: Цей документ.
- `docs/architecture/DECISION_REGISTRY_ADHD.md`: Реєстр заблокованих рішень.

### 4.2. Negative Scope (Що ядра НЕ стосується)
- ❌ Жодних прямих змін у бізнес-логіці `services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution`.
- ❌ Жодних змін у UI-компонентах `apps/web/` у межах цього зрізу.
- ❌ Заборона створення нових кореневих папок або несанкціонованих сервісів.

## 5. Наслідки та Компроміси (Consequences & Trade-offs)

### Позитивні наслідки
- **Зниження Context Bloat**: стоячий контекст мікроядра тримається в межах ≤ 6,000 токенів.
- **Швидкість тріажу**: System 1 (<50 мс) замінює повільні LLM-виклики.
- **Стабільність контрактів**: Pydantic SSOT гарантує сумісність модулів.

### Компроміси та ризики
- **Необхідність строгої схематизації**: кожен новий тип запиту повинен проходити валідацію.
- **Підвищені вимоги до архітектурних тестів**: тести контрактів ядра є блокуючими.

## 6. Verification & Implementation Plan (MASE)

* **Slice 1 (Contract & TDD Red-Gate)**: Зафіксувати `core/kernel/contracts.py` та `tests/core/test_kernel_contract.py`.
* **Slice 2 (Integration & Triage Routing)**: Зв'язати контракти ядра з `core/system_one/triage.py` та `core/orchestrator/decision_draft.py`.
* **Slice 3 (Gate Certification)**: Повний запуск `scripts/verify_all.sh` та оновлення реєстру рішень.
