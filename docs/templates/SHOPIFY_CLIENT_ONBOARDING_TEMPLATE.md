---
title: "Shopify Client Onboarding Specification (SSOT Intake)"
description: "Canonical Client Onboarding & Intake Specification Standard for Shopify OS 2.0 Theme Blocks Pipeline."
mrh_id: "docs/templates/SHOPIFY_CLIENT_ONBOARDING_TEMPLATE.md"
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
> mrh_id: "docs/templates/SHOPIFY_CLIENT_ONBOARDING_TEMPLATE.md"
> purpose: "Canonical Client Onboarding & Intake Specification Standard for Shopify OS 2.0 Theme Blocks Pipeline."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🛍️ Shopify Client Onboarding Specification (SSOT Intake)

> **Стандарт вхідного брифу для 6-етапного конвеєра запуску магазину на базі Theme Blocks 2.0 (DEC-010)**  
> Цей документ заповнюється під час онбординг-сесії з клієнтом (Етап 1).  
> Зібрані дані є єдиним джерелом правди (SSOT) для подальшої автоматичної генерації дослідження (`gerych_researcher`), 2 варіантів вайрфреймів (`dnk_shopify`) та фінального складання теми.

---

## 📋 1. Загальні дані клієнта та бізнесу

```yaml
client_meta:
  client_name: "[Назва компанії / Замовника]"
  contact_person: "[Ім'я та контакти особи, що приймає рішення]"
  store_url: "[URL магазину (або бажаний домен)]"
  shopify_plan: "[Basic / Shopify / Advanced / Plus]"
  market_geography: "[Географія продажів: UA, EU, US, Global]"
  primary_language: "[Основна мова магазину: uk, en, pl...]"
  secondary_languages: ["[Додаткові мови]"]
  primary_currency: "[UAH, USD, EUR...]"
  niche: "[Ніша: e.g. Преміальна доглядова косметика, Електроніка, Одяг]"
  business_model: "[DTC, B2B, Dropshipping, Hybrid]"
  target_launch_date: "[РРРР-ММ-ДД]"
```

---

## 🎨 2. Бренд-стиль та дизайн-токени (Brand Tokens)

Ці параметри автоматично транслюються агентом `dnk_shopify` у файл `config/settings_data.json` теми Tinker.

```yaml
brand_identity:
  logo:
    svg_source: "[Посилання на векторний SVG логотип]"
    png_dark_fallback: "[Логотип для темного фону]"
    png_light_fallback: "[Логотип для світлого фону]"
    favicon_url: "[URL фавікона]"
  
  color_tokens:
    primary_accent: "#000000"      # Кнопки дії, активні елементи
    secondary_accent: "#35D5D5"    # Бейджі, акценти, іконки переваг
    background_main: "#FFFFFF"     # Основний фон сторінки
    background_secondary: "#F4F6F8"# Фоновий колір для блоків довіри/альтернативних секцій
    text_primary: "#111827"        # Основний колір заголовків та тексту
    text_muted: "#6B7280"          # Вторинний текст, підписи, хлібні крихти
    success_stock: "#10B981"       # Бейджі наявності товару
    sale_badge: "#EF4444"          # Знижки та таймери

  typography:
    heading_font: "[e.g. Montserrat, Inter, Playfair Display]"
    body_font: "[e.g. Inter, Roboto, Lato]"
    heading_style: "[UPPERCASE / Normal / Bold]"
    base_size_px: 16

  ui_tokens:
    border_radius: "[sharp (0px) | rounded (8px) | pill (999px)]"
    button_style: "[solid | outline | shadow]"
    visual_mood: "[minimalist | luxury_editorial | tech_clean | vibrant_youth]"
```

---

## 📦 3. Продуктовий каталог та структура оферу

```yaml
catalog_structure:
  total_skus: "[Орієнтовна кількість товарів: 1-10, 10-50, 100+]"
  hero_products:
    - title: "[Назва головного флагманського товару 1]"
      price_range: "[Ціна або діапазон]"
      unique_value_prop: "[Головна унікальна перевага товару]"
      media_ready: "[true / false / потрібні мокапи]"
    - title: "[Назва товару 2]"
      price_range: "[Ціна]"
      unique_value_prop: "[Перевага]"
      media_ready: "[true / false]"

  conversion_offers:
    free_shipping_threshold: "[e.g. від 1500 грн / $50 / відсутня]"
    guarantee_terms: "[e.g. 30 днів повернення без питань, 12 міс гарантія]"
    bundle_offers: "[e.g. Купуй 2 — отримай 20% знижки, подарунок до замовлення]"
    trust_elements: ["[Швидка доставка Нова Пошта]", "[Оплата при отриманні]", "[100% оригінал]"]
```

---

## 🔗 4. Референси, бенчмарки та анти-патерни

```yaml
references:
  benchmark_stores:
    - url: "https://example-competitor.com"
      liked_aspects: "[Що конкретно подобається: hero-секція, подача відгуків, sticky cart]"
      notes: "[Коментар клієнта]"
    - url: "https://another-brand.com"
      liked_aspects: "[Анімації, мінімалістичний каталог, вибір варіантів]"
      notes: "[Коментар клієнта]"

  must_have_features:
    - "[e.g. Sticky Add to Cart на мобільних]"
    - "[e.g. Розрахунок термінів доставки в картці товару (Delivery Estimator)]"
    - "[e.g. Слайдер до/після або відео-відгуки покупців]"
    - "[e.g. Модальне вікно підбору розміру або тесту]"

  anti_patterns:
    - "[Чого категорично НЕ повинно бути: e.g. агресивні спливаючі вікна зі знижкою 5%]"
    - "[Перевантажений футер, авто-плей музики, занадто дрібний шрифт]"
```

---

## 🎯 5. Цільова аудиторія (ЦА) та бар'єри покупки

Вхідні тези для кроку **Deep Research** (`gerych_researcher`):

```yaml
target_audience:
  core_personas:
    - segment: "[e.g. Жінки 25-40, цінують якість, купують зі смартфона ввечері]"
      primary_need: "[e.g. Швидкий видимий результат без подразнення шкіри]"
      main_fear_or_doubt: "[e.g. Чи це оригінальна продукція? Що як не підійде?]"
      buying_trigger: "[e.g. Рекомендація дерматолога, відео-доказ, відгуки з фото]"

  social_proof_assets_available:
    customer_reviews: "[Кількість реальних відгуків, наявність скріншотів з Instagram]"
    influencer_mentions: "[Наявність UGC-відео від блогерів]"
    certifications: "[Сертифікати якості, нагороди, лабораторні тести]"
```

---

## ⚙️ 6. Технічний чеклист для передачі в Swarm (Machine Handoff)

Після заповнення цього брифу генерується команда для запуску:

```bash
# Команда запуску Етапу 2 (Deep Research) та Етапу 3 (Синтез 2 вайрфреймів)
python3 scripts/system/zero_waste_runner.py \
  --goal "Synthesize Dual-Variant Wireframes for client [CLIENT_NAME] based on docs/clients/[CLIENT_SLUG]/onboarding_brief.md" \
  --workspace_id ws-shopify-launch
```

- [ ] Бриф заповнено та підтверджено клієнтом.
- [ ] Векторний логотип збережено в `services/dnk_shopify/DNK_Horizon_Tinker/assets/`.
- [ ] Створено директорію клієнта: `docs/clients/[CLIENT_SLUG]/`.
- [ ] Передано агенту `gerych_researcher` для формування `research_dossier.md`.
