---
title: "DNK OS Sovereign Store Creation & Social Commerce SOP"
description: "Canonical standard operating procedure for deploying Shopify stores, AI-crawling GEO bundles (/llms.txt), Google Shopping XML feeds, and rich social media assets."
mrh_id: "docs/architecture/specs/19_STORE_CREATION_AND_SOCIAL_COMMERCE_SOP.md"
status: "Active"
version: "1.0.0"
updated: 2026-11-18
type: "architecture"
archetype: "SOP_RUNBOOK"
tags:
  - dnk-os
  - shopify
  - sop
  - social-commerce
  - geo
  - c2pa
domain: "distribution"
author: "DNK-e.com Maksym & Antigravity"
canonical_source: true
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/19_STORE_CREATION_AND_SOCIAL_COMMERCE_SOP.md"
> purpose: "Canonical standard operating procedure for deploying Shopify stores, AI-crawling GEO bundles (/llms.txt), Google Shopping XML feeds, and rich social media assets."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛍️ Регламент створення магазинів та ведення соціальних мереж (SOP-19)

Цей документ фіксує обов'язковий інженерний цикл при розгортанні нового клієнтського магазину та виробництві контенту для соціальних мереж на базі рішень **DEC-159** та **DEC-160**.

---

## 0. Мета та Тригер Запуску (Purpose & Trigger)
- **Мета**: Автоматизоване розгортання та щоденна операційна діяльність суверенного Shopify-магазину під ключ.
- **Тригер**: Запит на підключення нового клієнтського магазину або старт щоденного циклу публікації контенту.

## 0.1. Ролі та Відповідальність (Roles & Responsibilities)
- **Оркестратор (Antigravity)**: Контроль за дотриманням регламенту та детермінованих гейтів якості.
- **Будівельник (Denchik)**: Генерація `llms.txt`, Google Merchant Feed XML та підключення блоків теми `dnk-c2pa-badge.liquid`.
- **Медіа-генератор (dnk_media)**: Синтез відео, сторіз та OpenGraph-карток з C2PA-маніфестами.

## 1. Схема Архітектурного Конвеєра

```
                         КАТАЛОГ ТОВАРІВ (Shopify / DNK OS)
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
      [services/dnk_shopify]   [services/dnk_distribution]  [services/dnk_media]
                 │                       │                       │
      - DNK_Ecom               - /llms.txt (llmstxt.org)    - C2PA 2.0 Signer
      - dnk-c2pa-badge.liquid  - /llms-full.txt (Deep Specs)- 1200x630 OG Cards (SVG)
      - 7-Gate Theme Integrity - google_merchant_feed.xml   - 9:16 Hormozi Reels
                                                            - SERP Dominator @graph
```

---

## 2. Фаза 1: Створення та розгортання магазину (Shopify Store Creation)

При ініціалізації кожного нового магазину агент чи інженер виконує наступні кроки:

1. **Розгортання флагманської теми**:
   - Базова тема — `services/dnk_shopify/DNK_Ecom/` (Флагманська тема DNK Ecom).
   - Тема вже містить вбудований Theme Block 2.0: `blocks/dnk-c2pa-badge.liquid`.
   - У кастомайзері Shopify мерчант активує блок у секції продукту поряд із кнопкою додавання в кошик.

2. **Генерація пакету для AI-пошуковиків та Google Shopping**:
   - Виконати консольну команду:
     ```bash
     just geo-bundle public/
     ```
   - Команда автоматично створює:
     - `public/llms.txt` — короткий опис для ChatGPT Search, Perplexity, Claude.
     - `public/llms-full.txt` — повнотекстовий каталог із матеріалами та характеристиками.
     - `public/google_merchant_feed.xml` — RSS 2.0 XML фід для Google Shopping.

3. **Маршрутизація кореневих шляхів**:
   - **Варіант А (Cloudflare Reverse Proxy)**: Домен підключено через Cloudflare Pages/Worker (DEC-154), який миттєво віддає `/llms.txt` та `/google_merchant_feed.xml` з крайового кешу.
   - **Варіант Б (Shopify Files Redirect)**: Файли завантажуються в Shopify Admin ➔ Settings ➔ Files, а в Online Store ➔ Navigation ➔ URL Redirects прописуються редіректи:
     - `/llms.txt` ➔ CDN URL
     - `/google_merchant_feed.xml` ➔ CDN URL

---

## 3. Фаза 2: Ведення соціальних мереж та месенджерів (Social Commerce)

Для максимізації CTR та віральності в соціальних мережах (Telegram, WhatsApp, Instagram, TikTok, Twitter/X) використовується наступний арсенал:

1. **Криптографічний захист та Alt-текст зображень**:
   - Перед публікацією товару фото підписується через `services/dnk_media`:
     ```bash
     just media-sign "product.png" "DNK-e.com" "Чорне оверсайз худі DNK" "Black oversized DNK hoodie"
     ```
   - Зображення отримує валідний C2PA маніфест та вбудовані двомовні метадані (W3C WCAG 2.2).

2. **Генерація карток для чатів та месенджерів (1200x630)**:
   - Для розсилок у Telegram/WhatsApp та прев'ю посилань:
     ```bash
     just social-card "Оверсайз худі DNK" "2 400" "UAH" "DNK" "Преміальна тринитка 450г/м²" "assets/card.svg"
     ```
   - Картка містить Dark Glassmorphism, статус наявності, підсвітку ціни та C2PA маркування.

3. **Створення вертикальних відео 9:16 (Reels / TikTok / Shorts)**:
   - Використовується рушій `services/dnk_media` (`media_compose_video_9_16`):
     - Авто-вирізання мертвої тиші (Jump-cuts).
     - Динамічне центрирування обличчя в пропорцію 9:16.
     - Кінетичні субтитри в стилі Hormozi (ASS + MP4 mov_text).
     - Автоматичний аудіо-дакінг під фонову музику.

---

## 4. Фаза 3: Домінування в пошуковій видачі Google (SERP Dominance)

У шаблон товару `theme.liquid` підключається єдиний розширений `@graph` об'єкт:
```python
from services.dnk_media.src.service import generate_serp_dominator_graph

graph = generate_serp_dominator_graph(
    product_title="Оверсайз худі DNK Heavyweight",
    price="2400",
    currency="UAH",
    brand="DNK",
    in_stock=True,
    breadcrumbs=[("Головна", "https://dnk-e.com"), ("Худі", "https://dnk-e.com/collections/hoodies")],
    faqs=[
        {"question": "Який термін доставки?", "answer": "1-2 дні Новою Поштою по Україні."},
        {"question": "Як підібрати розмір?", "answer": "Скористайтеся таблицею розмірів на сторінці товару."}
    ]
)
```
*Результат*: Google відображає картку товару, клікабельні хлібні крихти та випадаючий список запитань-відповідей, займаючи весь екран мобільного пристрою.

---

## 5. Контроль якості, Перевірка та Результати (Verification & Sign-off Checklist)

Перед кожним релізом обов'язково запускається верифікація:
```bash
just test-workhorses
```
Усі 54+ тестів повинні завершуватися з `Exit Code 0`.

---

## 6. Аварійний Відкат та Відновлення (Rollback & Recovery)
- У разі виявлення помилок у генерації фідів або маніфестів C2PA: негайне повернення на попередню версію файлу через git worktree.
- При збої публікації в соцмережах: автоматичне призупинення конвеєра та сповіщення оркестратора без перезапису живого каталогу.
