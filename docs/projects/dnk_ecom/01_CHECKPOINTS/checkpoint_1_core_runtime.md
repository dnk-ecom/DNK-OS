---
title: "Checkpoint 1: Core Runtime — W3C Custom Elements, Event Bus & Cart Mutation Queue"
description: "Живий лог верифікації Checkpoint 1: W3C мікроядро dnk-core.js та черга кошика."
mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_1_core_runtime.md"
status: passed
type: checkpoint_log
gate_id: 1
theme_branch: mvp
date: 2026-11-17
verified_by: "just shopify-checkpoint 1"
---

> [!metadata]- ⚙️ Системні метадані (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_1_core_runtime.md"
> purpose: "Живий лог верифікації Checkpoint 1: W3C мікроядро dnk-core.js та черга кошика."
> canonical_source: true
> alters_files:
>   - "mvp/assets/dnk-core.js"
> triggers_tasks: []
> status: "Passed"
> version: "1.0.0"
> updated_at: "2026-11-17"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# ⚙️ Checkpoint 1: Core Runtime (`dnk-core.js`)

## 1. Контекст та Мета
* **Ціль**: Створити надлегкий, автономний рантайм на чистих Web Components без жодної важкої сторонньої бібліотеки (React, Alpine, jQuery, Lodash). Забезпечити стабільну чергу мутацій кошика та захист рекламних пікселів.
* **Цільові файли в гілці `mvp`**:
  - `assets/dnk-core.js`

## 2. Аналіз Донорів: Що було не так
* **Sugar (`__sugarGiftLinesSplit`)**: Механіка розділення рядків і виклику нативного fetch через чистий iframe була ефективною, АЛЕ вона була жорстко прив'язана до Alpine.js (`x-data`, `$store`). Alpine додає 15 КБ зайвого коду і викликає зауваження модераторів Theme Store.
* **Dawn / Tinker**: Не мають централізованої послідовної черги мутацій. Якщо покупець швидко клікає "Додати в кошик" 3 рази або змінює кількість у Drawer, виникає race condition (запити перехрещуються, кошик підвисає або втрачає товари).

## 3. Суверенне Рішення DNK (Чому саме так)
* **W3C Базовий Клас `DnkElement`**:
  - Автоматичне підключення та відключення обробників подій (`listen`, `dispatch`).
  - Гарантоване очищення пам'яті в `disconnectedCallback` (усунення витоків пам'яті).
* **Глобальна Шина Подій (`window.DNK.events`)**:
  - Типізовані події `dnk:cart:updated`, `dnk:variant:changed`, `dnk:drawer:opened`.
  - Повне відокремлення кошика від кнопок покупки (Loose Coupling).
* **Послідовна Черга Мутацій (`CartMutationQueue`)**:
  - Будь-який запит (`/cart/add.js`, `/cart/change.js`) стає в чергу і виконується послідовно.
  - Оптимістичний стан `data-dnk-loading="true"` блокує інтерфейс від подвійних кліків.
* **Cleanroom Attribution Fetch**:
  - Виконання через невидимий iframe (`about:blank`) захищає тему від монкі-патчингу сторонніми скриптами відстеження.
  - Готовність до розбиття пакетів на primary + rider gift для 100% збереження ROAS у Meta/TikTok/Google Ads.

## 4. Машинний Доказ (Machine Proof)
```bash
just shopify-checkpoint 1
```
* **Результат**: `Gate Checkpoint 1: Unified Core Runtime, Custom Element Base & Cart Mutation Queue -> ✅ PASSED`
* **Коміт у гілці `mvp`**: `b2950c0 feat(runtime): complete Checkpoint 1 - W3C Custom Elements, Event Bus & Cart Mutation Queue`
