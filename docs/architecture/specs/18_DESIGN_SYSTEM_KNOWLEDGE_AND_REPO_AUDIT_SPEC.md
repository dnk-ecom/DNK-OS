---
title: "Бойове ТЗ: Комплексний інженерний аудит бази знань та репозиторіїв для розширення можливостей Дизайн-Системи (Shopify E-Commerce + Social Media Motion)"
description: "Canonical Technical Task Specification for Auditing Knowledge Base and Repository Catalog to Supercharge Shopify and Social Media Design Systems."
mrh_id: "docs/architecture/specs/18_DESIGN_SYSTEM_KNOWLEDGE_AND_REPO_AUDIT_SPEC.md"
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
> mrh_id: "docs/architecture/specs/18_DESIGN_SYSTEM_KNOWLEDGE_AND_REPO_AUDIT_SPEC.md"
> purpose: "Canonical Technical Task Specification for Auditing Knowledge Base and Repository Catalog to Supercharge Shopify and Social Media Design Systems."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 Бойове ТЗ: Комплексний інженерний аудит бази знань та репозиторіїв для розширення можливостей Дизайн-Системи (Shopify E-Commerce + Social Media Motion)

> **ID Задачі**: `TASK-DNK-DS-AUDIT-20261117-001`  
> **Клас**: SOTA 2026 Deep Knowledge Mining & Repo Intelligence  
> **Виконавці**: `denchik` (Chief Autonomous Builder), `gerych_auditor` (Cold Knowledge Archivist), `dnk_git_research` (Scout)  
> **Оркестратор**: `Antigravity` (System Architect & Head of Orchestration)  
> **Стандарт виконання**: PSOD (Problem, Substrate, Oracle, Deliverable) + MASE (зрізи $\le 25$ дій)  
> **Нормативні рішення**: `DEC-009`, `DEC-015` (Horizon 5-Year), `DEC-057` (Senior Dev Ladder), `DEC-139` (Polaris Core), `DEC-142` (Dual-Target DS)

---

## 🎯 1. Ціль Місії (Executive Summary & Mission Objective)

### 1.1. Проблематика (Problem)
На сьогодні в проекті накопичено гігантський інтелектуальний капітал:
1. **1 663 перевірені репозиторії світового рівня** в локальному каталозі `catalog.db` (FTS5).
2. **70+ комерційних Shopify-тем та додатків** у дзеркалах `DNK-Ecom_git_mirrow` та `GitHub_Shopify_Themes` (Sugar, Shrine Pro, Story, Casaio, Ella, Impact, Prestige).
3. **90+ асимільованих скілів та SCONES-пам'ять** (`shopify_cro_blocks`, `hyperframes*`, `social_media_research_skills`, `webtwin`, `rynix_studio`).
4. **Медіа-рушій `services/dnk_media`** (FFmpeg, M2 протокол, Chirp3 TTS, Remotion/HyperFrames).

**Дефіцит**: Ці активи досі існують у роздільних силосах. Немає єдиного систематизованого реєстру готових дизайн-компонентів, токенів та motion-патернів, які можна автоматично дистилювати у нашу безголову дизайн-систему (W3C DTCG 2025.10 / `DEC-139`, `DEC-142`) для:
* **Shopify E-Commerce**: миттєва збірка ультра-швидких тем Horizon / Theme Blocks 2.0 із 100/100 Core Web Vitals.
* **Social Media & Marketing**: автоматична генерація брендованого контенту (9:16 Instagram Reels, TikTok, рекламні каруселі Meta Ads) за тими самими дизайн-токенами бренду.

### 1.2. Субстрат та Цільовий Результат (Substrate & Deliverable)
Провести повномасштабний детермінований аудит та вилучити "золоті молекули" у структурований звіт-каталог з готовими рецептами графтингу, що подвоїть швидкість розробки магазинів та виробництва контенту.

---

## 🛡️ 2. Білий список файлів та Негативний скоуп

### 2.1. Білий список файлів (Target Whitelist)
Агенти мають право створювати та модифікувати виключно такі файли:
* `docs/architecture/specs/18_DESIGN_SYSTEM_KNOWLEDGE_AND_REPO_AUDIT_SPEC.md` (це ТЗ)
* `docs/projects/dnk_ecom/audits/AUDIT_DESIGN_SYSTEM_KNOWLEDGE_AND_REPOS.md` (Головний аналітичний звіт)
* `docs/projects/dnk_ecom/audits/GENOME_DESIGN_SYSTEM_RECIPES.yaml` (Машиночитаний каталог молекул)
* `core/design_system/templates/` (Додавання нових галузевих шаблонів токенів)
* `core/design_system/recipes/` (Канонічні рецепти компонентів)
* `tests/core/test_design_system_recipes.py` (Автотести на валідність вилучених рецептів)

### 2.2. Негативний скоуп (Negative Scope — СУВОРО ЗАБОРОНЕНО)
* ❌ **Заборонено клонувати зовнішні репозиторії** у робоче дерево `DNK_OS` (тільки `catalog.db` або ізольований `../DNK_Vibe/` через `safe_repo_clone.py`).
* ❌ **Заборонено модифікувати вихідні коди тем-донорів** у `GitHub_Shopify_Themes/` чи `DNK-Ecom_git_mirrow/`.
* ❌ **Заборонено вигадувати "гіпотетичні" CSS/JS патерни з пам'яті LLM**: кожен патерн має посилатися на фізичний файл репозиторію або конкретний скіл.
* ❌ **Заборонено впроваджувати сторонні важкі UI-бібліотеки** (Chakra, Ant Design, MUI). Виключно W3C DTCG токени, нативний Liquid CSS та Meta Astryx `@layer astryx-theme`.

---

## 🔍 3. Чотири Вектори Аудиту (4-Track Audit Architecture)

```
┌────────────────────────────────────────────────────────────────────────┐
│         TASK-DNK-DS-AUDIT-20261117-001: 4 ВЕКТОРИ РОЗВІДКИ             │
├───────────────────────────────────┬────────────────────────────────────┤
│ 🛍️ TRACK 1: SHOPIFY E-COMMERCE    │ 🎬 TRACK 2: SOCIAL MEDIA & MOTION  │
│  - 70+ тем (Sugar, Shrine, Impact)│  - HyperFrames / Remotion патерни  │
│  - Theme Blocks 2.0 (Horizon)     │  - 9:16 Reels/TikTok Safe Zones    │
│  - Fluid 8pt Grid & Typography    │  - Kinetic Typography & SFX        │
│  - Cart Drawer & PDP CRO Blocks   │  - Auto-generated Ad Carousels     │
├───────────────────────────────────┼────────────────────────────────────┤
│ 🧠 TRACK 3: SCONES & SKILLS       │ 🔗 TRACK 4: CROSS-CHANNEL TOKEN MESH│
│  - 90+ асимільованих скілів       │  - Єдиний W3C DTCG маніфест бренду │
│  - shopify_cro_blocks             │  - Токен ➔ Liquid CSS (:root)      │
│  - social_media_research_skills   │  - Токен ➔ 9:16 Video JSON         │
│  - ukrainian-humanizer (anti-slop)│  - Токен ➔ Tailwind v4 @theme      │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Вектор 1: Shopify E-Commerce Store Design Systems (Horizon / Blocks 2.0)
Дослідити теми-донори на наявність передових технічних рішень:
1. **Топологія токенів у Liquid**:
   * Організація `:root` змінних (кольори, поверхні, RGB-тріплети для `rgba(var(--color-accent-rgb), 0.12)`).
   * Fluid типографіка через `clamp()` без стрибків макету (Zero-CLS).
   * 8pt просторова сітка (`--space-100: 4px`, `--space-200: 8px` ... `--space-800: 32px`).
2. **Конверсійні Theme Blocks 2.0 (`blocks/*.liquid`)**:
   * `_product-main-sticky-atc.liquid`: мобільна закріплена плашка покупки з розкриттям варіантів.
   * `cart-drawer.liquid`: кошик з прогрес-баром безкоштовної доставки, таймером утримання товару та in-cart апселами.
   * `before-after-slider.liquid`: інтерактивне порівняння результатів «до/після».
   * `comparison-table.liquid`: матриця «Наш бренд vs Конкуренти».
   * `bento-grid.liquid`: модульна сітка переваг продукту.
3. **Кастомайзер (`config/settings_schema.json`)**:
   * Архітектура груп налаштувань для мерчанта (Typography, Colors, Layout, Badges).
   * Локалізація налаштувань (`locales/uk.schema.json`, `en.default.schema.json`).

### Вектор 2: Social Media & Motion Design Systems (HyperFrames / Remotion)
Дослідити медіа-репозиторії та скіли для переносу ДНК бренду в соцмережі:
1. **Шкала кінетичної типографіки та анімації**:
   * Пружинні фізичні токени (`spring(tension, friction)` / `cubic-bezier(0.16, 1, 0.3, 1)`).
   * Послівна анімація субтитрів (Word-level karaoke highlighting за таймкодами Whisper).
   * Акцентні спалахи важливих слів у фірмовому кольорі бренду (`var(--color-accent)`).
2. **Вертикальні композиційні сітки (9:16 Mobile Safe Zones)**:
   * Зони безпеки для TikTok / Instagram Reels (1080x1920):
     - Верхній відступ: 120px (хедер соцмережі).
     - Нижній відступ: 340px (опис, кнопки взаємодії, звук).
     - Бічні поля: 48px.
3. **Модульні сцени для промо-відео**:
   * Hook Scene (0–3 сек): потужний заголовок + візуальний стопер.
   * Problem/Pain Agitation (3–7 сек): спліт-скрін або бліц-титри.
   * Product Solution Showcase (7–12 сек): 3D-обертання або bento-розбір продукту.
   * Social Proof / Trust (12–17 сек): зірки відгуків + цитата клієнта.
   * Focal CTA (17–20 сек): фінальний заклик із фірмовою кнопкою вітрини.

### Вектор 3: База Знань SCONES та Асимільовані Скіли
Проіндексувати та витягнути інженерні рецепти з таких джерел:
* `skills/shopify_cro_blocks/SKILL.md`: правила синтезу Dual-Ready CRO блоків.
* `skills/shopify_dynamic_pdp_playbook_assimilated/SKILL.md`: структура високоефективної картки товару.
* `skills/the_ultimate_cro_app_assimilated/SKILL.md`: алгоритми A/B спліт-тестування та таймерів.
* `skills/social_media_research_skills_assimilated/SKILL.md`: скрапінг вірусних хуків та трендів.
* `skills/hyperframes*/SKILL.md`: стандарти детермінованого рендерингу відео через headless-браузер.
* `skills/ukrainian_humanizer/SKILL.md`: усунення AI-slop та кальок у маркетингових текстах і PDP.

### Вектор 4: Cross-Channel Token Mesh Bridge (Shopify ➔ Social)
Спроєктувати механіку «One Spec — Omnichannel Delivery»:
* Як файл `brand_tokens_spec.json` (або `spec.yaml`) автоматично компілює:
  1. `assets/dnk-tokens.css` (для теми магазину)
  2. `tailwind-theme.css` (для веб-додатку)
  3. `hyperframes-tokens.json` (для рендерингу Reels/Stories)
  4. `meta-ads-spec.json` (для генератора статичних банерів 1:1 та 4:5)

---

## 🛠️ 4. Санкціоновані Інструменти (Sanctioned Tools & Whitelist)

1. **Repo Intelligence CLI**:
   ```bash
   .venv/bin/python3 -m services.dnk_git_research.cli search "<query>" --limit 20
   .venv/bin/python3 -m services.dnk_git_research.cli brief "<query>"
   ```
2. **FastMCP Design System Tools**:
   * `distill_brand_design_system`
   * `compile_brand_design_tokens`
   * `lint_brand_design_tokens`
3. **Локальні інструменти коду**:
   * `read_file`, `write_file`, `edit_file`, `run_command` (grep, find, wc).
4. **Якісні гейти**:
   * `./scripts/verify_all.sh`
   * `~/.dnk_runtime/venv/bin/pytest tests/core/test_design_system*`

---

## 🪜 5. Покроковий План Виконання (5 MASE-Зрізів по $\le 25$ дій)

### 🔹 Зріз 1: Пошук та розвідка в базі 1 663 репозиторіїв (`dnk_git_research`)
1. Виконати FTS5-запити в `catalog.db` за категоріями:
   * `"shopify design system theme tokens"`
   * `"remotion kinetic typography video motion"`
   * `"social media reels video creator generator"`
   * `"ecommerce cro blocks conversion"`
2. Сформувати список Топ-15 найцінніших репозиторіїв-донорів з оцінкою ліцензій (MIT/Apache-2.0).

### 🔹 Зріз 2: Аудит локальних Shopify тем та екстракція Liquid-молекул
1. Просканувати дзеркала тем `sugar`, `shrine-pro`, `story-basic`, `casaio`, `ella`.
2. Вилучити та класифікувати найкращі рішення:
   * Систему організації токенів кольорів і шрифтів.
   * Топ-5 конверсійних блоків (Sticky ATC, Cart Drawer, Bundle Builder, Size Chart, Trust Badges).
3. Сформувати інженерні картки молекул.

### 🔹 Зріз 3: Аудит медіа-рушія та патернів створення соцмережевого контенту
1. Проаналізувати `services/dnk_media/` та скіли `hyperframes*` / `remotion_composition_patterns`.
2. Зафіксувати матрицю motion-токенів:
   * Шкала швидкості анімацій (Fast: 150ms, Base: 250ms, Dramatic: 400ms).
   * Набір із 4 канонічних пружин (`spring-gentle`, `spring-snappy`, `spring-bouncy`, `spring-focal`).
   * Шаблони безпечних зон 9:16 для вертикальних відео.

### 🔹 Зріз 4: Синтез Підсумкового Звіту та Каталогу Рецептів
1. Створити канонічний звіт: `docs/projects/dnk_ecom/audits/AUDIT_DESIGN_SYSTEM_KNOWLEDGE_AND_REPOS.md`.
2. Створити файл рецептів: `docs/projects/dnk_ecom/audits/GENOME_DESIGN_SYSTEM_RECIPES.yaml`.
3. Додати галузевий шаблон дизайн-системи для моди/DTC: `core/design_system/templates/dnk_dtc_social_ecommerce_spec.yaml`.

### 🔹 Зріз 5: Детермінована Верифікація та Закриття Задачі
1. Написати юніт-тести для перевірки валідності нових рецептів та шаблону.
2. Прогнати повний комплекс перевірок `./scripts/verify_all.sh` (всі 4 шлюзи).
3. Отримати `Exit Code 0` та зафіксувати артефакти в звіті.

---

## 🏁 6. Критерії Приймання та Детерміновані Шлюзи (Acceptance Gates)

| Критерій | Метод Перевірки | Очікуваний Результат |
| :--- | :--- | :--- |
| **Повнота аудиту тем** | AST-сканування репо | Задокументовано $\ge 10$ реальних блоків із кодом Liquid |
| **Повнота медіа-аудиту** | Специфікація HyperFrames | Зафіксовано 9:16 safe-zones та 4 пружинні motion-пресети |
| **Машиночитаний каталог** | YAML Schema Gate | Валідний `GENOME_DESIGN_SYSTEM_RECIPES.yaml` |
| **Zero-Hallucination** | Git Path Audit | 100% посилань вказують на реальні існуючі шляхи репо |
| **WCAG 2.2 AA Contrast** | `DesignTokenLinter` | 100% pass rate для всіх нових токенів |
| **Якість коду системи** | `./scripts/verify_all.sh` | **Exit Code 0** (111+ тестів пройдено, 0 помилок) |

---

## 🚀 Команда на запуск (Для Максима або Автономного Рою):

```bash
# Запуск автономного виконання ТЗ через Денчіка:
python3 scripts/system/denchik.sh --task "TASK-DNK-DS-AUDIT-20261117-001" \
  --spec "docs/architecture/specs/18_DESIGN_SYSTEM_KNOWLEDGE_AND_REPO_AUDIT_SPEC.md"
```
