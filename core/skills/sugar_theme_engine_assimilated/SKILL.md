---
name: sugar_theme_engine_assimilated
description: "Assimilated SOTA patterns and architecture from Sugar Theme (Theme Blocks 2.0, 12-column universal canvas, native Web Components event bus, Cart Drawer V2, and Zero-DRM cleanroom standards)."
version: "2.3.16"
category: "shopify-architecture"
assimilated_at: "2026-11-18"
license: "Cleanroom Commercial Derivative"
target_worker: "dnk_shopify"
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/skills/sugar_theme_engine_assimilated/SKILL.md"
purpose: "Architecture blueprint, component contracts, and execution runbook for Sugar Theme Engine."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "2.3.16"
updated_at: "2026-11-18"
author: "DNK-e.com Maksym & Antigravity (Chief Architect)"
--- END DNK-MRH-HEADER -->

# 🍭 Sugar Theme Engine & Architecture Manual

## 📌 Загальний огляд
Sugar Theme є еталонною реалізацією стандарту **Shopify Theme Blocks 2.0**, оптимізованою під максимальну конверсію (CRO) та візуальну свободу кастомізації без сторонніх конструкторів сторінок (Page Builders).

- **Ядро**: Чистий HTML5 / Liquid + Vanilla JS Web Components (0 KB важких фреймворків).
- **Стилі**: 1 172 кастомні CSS-властивості (CSS Custom Properties).
- **Стандарт чистоти**: 100% Zero-DRM Cleanroom (повне вилучення вендорських блокувань та трекерів).

---

## 🏛️ 5 Архітектурних Стовпів Теми

### 1. 12-колонковий Універсальний Канвас (Theme Blocks 2.0)
Ключовий модуль гнучкої верстки: `blocks/custom-columns.liquid` у парі з `blocks/column.liquid`.
- Дозволяє розбивати будь-яку секцію на довільну сітку колонок від 1 до 12.
- **`media-sizes-scope`**: автоматично передає реальну розрахункову ширину колонки у дочірні блоки зображень, забезпечуючи генерацію ідеального тегу `sizes="..."` для `image_tag`, що мінімізує вагу завантажуваних картинок та оптимізує показник LCP.
- **Вкладеність**: підтримує вкладення дочірніх блоків через `{% content_for 'blocks' %}` (глибина до 8 рівнів).

### 2. Нативна Шина Подій (Event Bus) та Web Components
Усі інтерактивні елементи реалізовані як стандартні Web Components без зовнішніх залежностей:
- `<cart-drawer>`: керування висувним кошиком.
- `<variant-picker>`: селектор варіантів товару з оновленням URL через History API без перезавантаження сторінки.
- `<variable-media>`: адаптивна медіа-галерея товару (відео, 3D-моделі, зум).
- `<sticky-header>`: оптимізований липкий хедер з `IntersectionObserver`.
- `<inline-accordion>`: плавний нативний акордеон на базі CSS Grid / transitions.

**Шина подій CustomEvents**:
- `sugar:cart:change` — викликається після додавання/видалення товарів з передачею нового стану `cart`.
- `sugar:cart:error` — спрацьовує при перевищенні залишків на складі або валідаційних помилках.
- `sugar:variant:change` — сповіщає всі блоки PDP про зміну обраного варіанту (оновлює ціни, наявність, бейджі).
- Атрибути стану: `data-sugar-animating` (запобігає спам-клікам під час CSS-переходів), `data-sugar-dropdown-open`.

### 3. Дизайн-Система та Токенізація
- Усі відступи, радіуси, тіні та кольори винесені у CSS змінні:
  - `--sugar-color-*` (фони, текст, акценти).
  - `--sugar-font-*` (типографіка з `clamp()` для плавної адаптивності між мобільними та десктопом).
  - `--sugar-radius-*` (радіуси заокруглення кнопок, карток, бейджів).
- Кожен блок інкапсулює свої стилі, уникаючи глобального конфлікту селекторів.

### 4. Cart Drawer V2 та CRO-Інструменти
- **Транспорт**: оновлення кошика через асинхронні запити до `/cart/add.js`, `/cart/change.js` та Shopify Section Rendering API (`?sections=cart-drawer`).
- **Мотиваційний блок**: шкала безкоштовної доставки та прогресу подарунків (`cart-rewards`).
- **Upsell Carousel**: інтегровані рекомендації безпосередньо всередині дровера.

### 5. Інваріант Чистоти (Zero-DRM Cleanroom Standard)
У робочій версії DNK тема повністю автономна:
- Фізично видалено всі виклики `fetch('https://ipwho.is/...')`.
- Вилучено `if (window.__swOk === false) return;` з усіх 16 JS-файлів.
- Вилучено всі залишкові `<script>window.__swOk=true;</script>`.
- Локалізовано іконний шар на локальні SVG без звернень до сторонніх бакетів.

---

## 🛠️ Рецепти для Агентів (Agent Runbooks)

### 1. Аудит нової версії теми:
1. Виконати диференціальний побайтовий та CRC-32 аналіз:
   ```bash
   python3 -c "import zipfile ... diff CRC-32"
   ```
2. Запустити `drm_telemetry_hunter.py` на пошук нових векторів перевірок ліцензій.
3. Провести `shopify theme check`.

### 2. Графтинг блоку в іншу тему:
1. Скопіювати `blocks/<block-name>.liquid`.
2. Скопіювати відповідний JS (`assets/<block-name>.js`) та CSS (`assets/<block-name>.css`).
3. Замінити префікси `--sugar-*` на цільові токени.
4. Додати локалізаційні ключі до `locales/uk.json` та `locales/uk.schema.json`.
