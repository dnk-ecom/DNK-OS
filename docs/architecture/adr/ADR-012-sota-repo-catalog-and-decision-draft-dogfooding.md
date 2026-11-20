---
title: "ADR-012: SOTA Repo Catalog Integration, Decision Draft Verification та Dogfooding-First Product v1"
description: "ADR-012: SOTA Repo Catalog Integration, Epistemic Decision Draft Engine and Dogfooding-First Product v1."
mrh_id: "docs/architecture/adr/ADR-012-sota-repo-catalog-and-decision-draft-dogfooding.md"
status: Active
archetype: ADR
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - adr
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/adr/ADR-012-sota-repo-catalog-and-decision-draft-dogfooding.md"
> purpose: "ADR-012: SOTA Repo Catalog Integration, Epistemic Decision Draft Engine and Dogfooding-First Product v1."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

> [!abstract] 🏛️ АРХІТЕКТУРНЕ РІШЕННЯ: SOTA REPO CATALOG ТА DECISION DRAFT DOGFOODING
> Інтеграція каталогу асимільованих open-source рішень та епістемічного рушія рішень у ядро Product v1 для гарантування Zero Discussion Amnesia.

# ADR-012: SOTA Repo Catalog Integration, Decision Draft Verification та Dogfooding-First Product v1

## 🎯 1. Контекст та Проблематика (Context & Problem Statement)
У процесі розвитку продуктової версії DNK OS (`DNK_OS_APP`) виникла потреба перенести найкращі асимільовані напрацювання з лабораторії знань:
1. Каталог перевірених open-source рішень та архітектурних патернів (80 Golden Core репозиторіїв: ThoughtDAG, Canvas Harness, Tributary, AlgoPipe, Dim0 тощо).
2. Захист від втрати архітектурних домовленостей (Zero Discussion Amnesia) через Epistemic Decision Draft із криптографічними чеками SHA-256.
3. Повну самосвідомість системи: розробник та ШІ-агент мають миттєво знаходити точки модифікації коду (`SelfAwarenessEngine`), не блукаючи деревом каталогів.

## 💡 2. Прийняте Рішення (Decision)
1. **Інтеграція SOTARepoCatalog (`core/registry/repo_catalog.py`)**:
   - Локальна база SQLite WAL (`catalog.db`) з автоматичним fallback на 80 Golden Core інструментів.
   - Миттєвий пошук за доменами, агентами та архітектурними патернами.
2. **Двигун Рішень з Епістемічним Захистом (`core/orchestrator/decision_draft.py`)**:
   - Обов'язковий аналіз 3 прихованих ризиків та скептичної альтернативи для кожного рішення.
   - Канонічне хешування RFC-8785 та генерація квитанцій `RECEIPT-*`.
3. **Реєстрація у FastMCP Ядрі (`core/kernel.py`) та REST API (`apps/api/main.py`)**:
   - Додано інструменти `search_catalog`, `evaluate_decision_receipt` та CLI-команди `catalog`, `decision`.

## ⚖️ 3. Наслідки та Трейд-офи (Consequences & Trade-offs)
- **Позитивні**:
  - Агенти отримують прямий доступ до перевірених архітектурних рішень без повторного винайдення велосипеда.
  - Жодне важливе рішення не губиться між сесіями.
  - Повна відповідність лімітам контексту (контекстні капсули `<= 6000` токенів, `<= 8` інструментів).
- **Негативні / Трейд-офи**:
  - Необхідність періодичної синхронізації каталогу репозиторіїв між R&D базою та продуктом.

## 🔗 4. Пов'язані Документи
- [[ADR-001-microkernel-fastmcp-architecture]]
- [[ADR-002-task-forest-dag-execution]]
- [[ADR-005-thoughtdag-spatial-knowledge-and-agent-interaction]]
- [[ADR-006-agentic-harness-and-spec-kit]]
