---
title: "Ієрархічний Навігатор Репозиторіїв DNK OS (Progressive Disclosure LOD)"
description: "Two-Level Progressive Disclosure Index (LOD Navigation Standard) for 1,663 Vetted SOTA Repositories in DNK OS."
mrh_id: "docs/architecture/INDEX_REPOSITORIES_PROGRESSIVE.md"
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
> mrh_id: "docs/architecture/INDEX_REPOSITORIES_PROGRESSIVE.md"
> purpose: "Two-Level Progressive Disclosure Index (LOD Navigation Standard) for 1,663 Vetted SOTA Repositories in DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 Ієрархічний Навігатор Репозиторіїв DNK OS (Progressive Disclosure LOD)

> [!IMPORTANT]
> **Принцип Прогресивного Розкриття (Level-of-Detail Navigation)**:
> Агенти рою **ніколи не завантажують весь каталог (1,663 репозиторії) у системний промпт**. 
> Це виключає перевантаження контексту (Attention Rot) і втримує бюджет підказки в межах $\le 1,500$ токенів (DEC-120).
> 
> Навігація відбувається у 2 рівні:
> 1. **Рівень 0 (Root LOD)**: Огляд 3 суверенних стовпів системи ($\le 1,000$ токенів).
> 2. **Рівень 1 (Domain Slice)**: Цільовий зріз обраного домену з Tier 1/2 репозиторіями ($\le 1,500$ токенів).
> 3. **Рівень 2 (JIT Search)**: Точковий FTS5 BM25 пошук через `search_repo_catalog(query, domain)`.

---

## 🏛️ Рівень 0: Огляд 3 Суверенних Стовпів (1,663 Репозиторії)

| Стовп (Domain) | Суверенний Воркхорс | Кількість Репо | Ключові Архітектурні Патерни | Топ-3 Golden Core Репозиторії (Tier 1) |
| :--- | :--- | :--- | :--- | :--- |
| 🛍️ **SHOPIFY & E-COM** | `services/dnk_shopify` | **145** | Theme Blocks 2.0, Liquid AST, No-App CRO, Sidekick AI, Cart Mutation Queue | `shopify-theme-builder`, `shopify-dynamic-pdp-playbook`, `the-ultimate-cro-app` |
| 🎬 **MEDIA & VIDEO** | `services/dnk_media` | **210** | Gemini 3.8 Agentic Video, Kinetic Subtitles, Face Centering, Remotion v5, SVAE | `supoclip`, `auteur`, `hypokiln` |
| 🛡️ **CORE & SWARMS** | `core/`, `apps/` | **1,308** | FastMCP Microkernel (< 400 LOC), SCONES FTS5 WAL, Git Worktrees, RLM Compactor, Epistemic Armor | `ecc`, `open-code-review`, `pr-af` |

---

## 🛍️ Рівень 1: Стовп 1 — Shopify & High-Conversion E-Commerce (`shopify`)

- **Цільовий сервіс**: `services/dnk_shopify/` (флагманська тема `DNK_Sovereign_Apex`).
- **Загальна база**: 145 репозиторіїв (Tier 1: 18, Tier 2: 42, Tier 3: 85).
- **Спеціалізовані Агенти**: `dnk_shopify` (Liquid AST, Sections, Blocks), `denchik` (WASM Functions).

### 🌟 Золоте Ядро (Tier 1: Golden Core):
1. **`movictor99/shopify-theme-builder`**: Модульна архітектура секцій, детермінований бандлінг без Webpack.
2. **`Saabbir/shopify-theme-handbook`**: Канонічний довідник стандартів Shopify Theme Store ($350–$420 MSRP).
3. **`Omar92953/the-ultimate-cro-app`**: Вбудовані механізми Upsell, Sticky ATC, Cart Rewards, Cart Drawer без сторонніх підписок.
4. **`NikoCartin/shopify-dynamic-pdp-playbook`**: SOTA динамічні PDP-шаблони, B2B Volume Pricing, Combined Listings.
5. **`api-evangelist/intelligems`**: A/B тестування цін, доставки та пропозицій.

### 🔍 Як викликати зріз:
```python
# Через FastMCP / Python API:
res = get_repo_progressive_index(domain="shopify")
```

---

## 🎬 Рівень 1: Стовп 2 — Media Studio, Video AI & Kinetic Motion (`media`)

- **Цільовий сервіс**: `services/dnk_media/` (автономна відеостудія, шортси, реклама).
- **Загальна база**: 210 репозиторіїв (Tier 1: 24, Tier 2: 66, Tier 3: 120).
- **Спеціалізовані Агенти**: `dnk_media`, `dnk_video_ai_creator`.

### 🌟 Золоте Ядро (Tier 1: Golden Core):
1. **`zhouxiaoka/supoclip`**: Автоматичний поділ довгих відео на віральні короткі кліпи з детекцією кульмінацій.
2. **`agiwhitelist/auteur`**: Агентивна режисура, динамічний монтаж сценаріїв та компонування планів.
3. **`agiwhitelist/hypokiln`**: Високошвидкісний рендеринг та анімаційні адаптери (GSAP / Three.js).
4. **`remotion-dev/remotion`**: Програмне відео на React/TypeScript (чисті композиції Remotion v5).
5. **`brijr/iris`**: Візуальний зворотний зв'язок через CDP, розумне очікування стабілізації DOM, захоплення кадрів.

### 🔍 Як викликати зріз:
```python
res = get_repo_progressive_index(domain="media")
```

---

## 🛡️ Рівень 1: Стовп 3 — Core Microkernel, Swarms & Agentic Infrastructure (`core`)

- **Цільова зона**: `core/`, `apps/`, `infra/` (суверенне ядро системи).
- **Загальна база**: 1,308 репозиторіїв (Tier 1: 45, Tier 2: 260, Tier 3: 1,003).
- **Спеціалізовані Агенти**: `antigravity` (Mentor / Architect), `denchik` (Builder), `gerych` (Auditor).

### 🌟 Золоте Ядро (Tier 1: Golden Core):
1. **`affaan-m/ECC`**: Enterprise Cognitive Core, детерміновані структури пам'яті та лічильники ентропії.
2. **`alibaba/open-code-review`**: Двофазний аудит коду: детермінований AST-сніффінг + точкові зауваження без галюцинацій.
3. **`Agent-Field/pr-af`**: Adversarial Gate (шлюз перевірки правок: Auditor ⚔️ vs Builder 🛡️) з розрахунком радіуса вибуху (Blast Radius).
4. **`herdrdev/herdr`**: Контролер ройових воркерів, черги повідомлень та консенсус результатів.
5. **`pinkpixel-dev/notification-mcp`**: Нативне сповіщення macOS та ізольовані FastMCP-сервери.

### 🔍 Як викликати зріз:
```python
res = get_repo_progressive_index(domain="core")
```

---

## ⚡ 3. Протокол Викликів для Агентів (Context Diet Summary)

| Дія | Виклик | Споживання контексту |
| :--- | :--- | :--- |
| **Оцінка доступних доменів** | `get_repo_progressive_index()` | **~450 токенів** |
| **Отримання зрізу рішень** | `get_repo_progressive_index("shopify")` | **~1,100 токенів** |
| **Точковий пошук під таску** | `search_repo_catalog("sticky atc", domain="shopify")` | **~350 токенів** |
| **Бриф перед написанням коду** | `get_repo_reuse_brief("cart drawer upsell")` | **~800 токенів** |
