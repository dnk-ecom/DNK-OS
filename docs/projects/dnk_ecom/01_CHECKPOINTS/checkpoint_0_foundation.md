---
title: "Checkpoint 0: Foundation (Design Tokens & CSSOM Reset)"
description: "Живий лог верифікації Checkpoint 0: дизайн-токени W3C, CSSOM Reset та Subgrid."
mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_0_foundation.md"
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
> mrh_id: "docs/projects/dnk_ecom/01_CHECKPOINTS/checkpoint_0_foundation.md"
> purpose: "Живий лог верифікації Checkpoint 0: дизайн-токени W3C, CSSOM Reset та Subgrid."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧱 Checkpoint 0: Foundation (Design Tokens & CSSOM Reset)

## 1. Контекст та Мета
* **Ціль**: Закласти непорушний візуальний фундамент з нульовим зсувом макета (CLS = 0.00) та повною підтримкою адаптивності на базі стандарту W3C Design Tokens.
* **Цільові файли в гілці `mvp`**:
  - `assets/dnk-tokens.css`
  - `assets/dnk-base.css`

## 2. Аналіз Донорів: Що було не так
* **Dawn / Tinker**: Використовують мішанину жорстко захардкодzone-значень і кольорів, змішаних із Liquid-фільтрами (`color_lighten`), що призводить до дублювання CSS-файлів та повільного парсингу.
* **Sugar / Shrine**: Стилі розкидані по десятках окремих файлів, що створює Layout Shifts (CLS > 0.15) при асинхронному завантаженні.

## 3. Суверенне Рішення DNK (Чому саме так)
* **W3C Design Tokens (`dnk-tokens.css`)**:
  - Чітка 8pt шкала відступів (`--dnk-space-1` .. `--dnk-space-24`).
  - Палітра *Polaris Emerald / Electric Mint / Obsidian* (DEC-139, DEC-145).
  - Підтримка світлої та темної тем через data-атрибути `[data-theme="dark"]` без розриву макета.
* **CSSOM Reset & Subgrid (`dnk-base.css`)**:
  - Сучасний CSS Reset із усуненням зайвих відступів.
  - 12-колонкова Subgrid-сітка для рекурсивних контейнерів Theme Blocks 2.0.
  - Утиліти доступності: `.dnk-visually-hidden`, `.dnk-focus-ring` (WCAG 2.2 AA).

## 4. Машинний Доказ (Machine Proof)
```bash
just shopify-checkpoint 0
```
* **Результат**: `Gate Checkpoint 0: Design Tokens, CSSOM Reset & Typography Scaling -> ✅ PASSED`
* **Коміт у гілці `mvp`**: `2437b73 feat(tokens): complete Checkpoint 0 - Design Tokens, CSSOM Reset & 12-Column Subgrid`
